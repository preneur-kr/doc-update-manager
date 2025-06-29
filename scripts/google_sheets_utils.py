import os
import json
from typing import Optional
from google.oauth2.service_account import Credentials
from google.auth.exceptions import DefaultCredentialsError
import gspread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# gspread가 요구하는 기본 스코프
DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_credentials() -> Optional[Credentials]:
    """
    Google Service Account credentials를 가져옵니다.
    환경 변수 GOOGLE_CREDENTIALS_JSON이 있으면 그것을 사용하고,
    없으면 GOOGLE_CREDENTIALS_PATH 파일을 읽습니다.
    """
    try:
        # 1. 환경 변수에서 JSON 문자열로 credentials 가져오기 (Render 배포용)
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if credentials_json:
            print("✅ Google credentials를 환경 변수에서 로드")
            credentials_info = json.loads(credentials_json)
            return Credentials.from_service_account_info(
                credentials_info, scopes=DEFAULT_SCOPES
            )
        
        # 2. 파일 경로에서 credentials 가져오기 (로컬 개발용)
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        if credentials_path and os.path.exists(credentials_path):
            print(f"✅ Google credentials를 파일에서 로드: {credentials_path}")
            return Credentials.from_service_account_file(
                credentials_path, scopes=DEFAULT_SCOPES
            )
        
        print("❌ Google credentials를 찾을 수 없습니다.")
        print("환경 변수 GOOGLE_CREDENTIALS_JSON 또는 GOOGLE_CREDENTIALS_PATH를 설정해주세요.")
        return None
        
    except json.JSONDecodeError as e:
        print(f"❌ Google credentials JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ Google credentials 로드 오류: {e}")
        return None

def get_worksheet(sheet_name: str):
    """
    Google Sheets 워크시트를 가져옵니다.
    
    Args:
        sheet_name (str): 시트 이름
        
    Returns:
        gspread.Worksheet: 워크시트 객체 또는 None
    """
    try:
        print(f"🔍 DEBUG: get_worksheet 시작 - sheet_name: {sheet_name}")
        
        # Google credentials 가져오기
        print("🔍 DEBUG: Google credentials 가져오기 시작...")
        credentials = get_google_credentials()
        if not credentials:
            print("❌ DEBUG: get_google_credentials에서 None 반환됨")
            return None
        
        print("✅ DEBUG: Google credentials 가져오기 성공")
        
        # Google Sheets 클라이언트 생성
        print("🔍 DEBUG: gspread 클라이언트 생성 시작...")
        client = gspread.authorize(credentials)
        print("✅ DEBUG: gspread 클라이언트 생성 성공")
        
        # 시트 ID 가져오기
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            print("❌ DEBUG: GOOGLE_SHEET_ID 환경 변수가 설정되지 않음")
            return None
        
        print(f"🔍 DEBUG: 시트 ID: {sheet_id[:8]}...")
        
        # 스프레드시트 열기
        print("🔍 DEBUG: 스프레드시트 열기 시작...")
        spreadsheet = client.open_by_key(sheet_id)
        print("✅ DEBUG: 스프레드시트 열기 성공")
        
        # 워크시트 가져오기 (없으면 생성)
        try:
            print(f"🔍 DEBUG: 워크시트 '{sheet_name}' 가져오기 시도...")
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"✅ DEBUG: 워크시트 '{sheet_name}' 로드 성공")
        except gspread.WorksheetNotFound:
            print(f"⚠️ DEBUG: 워크시트 '{sheet_name}'이 없어서 생성합니다.")
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            print(f"✅ DEBUG: 워크시트 '{sheet_name}' 생성 완료")
        
        return worksheet
        
    except Exception as e:
        print(f"❌ DEBUG: Google Sheets 연결 오류")
        print(f"❌ DEBUG: 에러 타입: {type(e)}")
        print(f"❌ DEBUG: 에러 메시지: {str(e)}")
        print(f"❌ DEBUG: 에러 상세: {repr(e)}")
        import traceback
        print(f"❌ DEBUG: 스택 트레이스:")
        traceback.print_exc()
        return None 