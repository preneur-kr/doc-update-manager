import os
import json
from typing import Optional
from google.oauth2.service_account import Credentials
from google.auth.exceptions import DefaultCredentialsError
import gspread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
            return Credentials.from_service_account_info(credentials_info)
        
        # 2. 파일 경로에서 credentials 가져오기 (로컬 개발용)
        credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        if credentials_path and os.path.exists(credentials_path):
            print(f"✅ Google credentials를 파일에서 로드: {credentials_path}")
            return Credentials.from_service_account_file(credentials_path)
        
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
        # Google credentials 가져오기
        credentials = get_google_credentials()
        if not credentials:
            return None
        
        # Google Sheets 클라이언트 생성
        client = gspread.authorize(credentials)
        
        # 시트 ID 가져오기
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            print("❌ GOOGLE_SHEET_ID 환경 변수가 설정되지 않았습니다.")
            return None
        
        # 스프레드시트 열기
        spreadsheet = client.open_by_key(sheet_id)
        
        # 워크시트 가져오기 (없으면 생성)
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"✅ 워크시트 '{sheet_name}' 로드 성공")
        except gspread.WorksheetNotFound:
            print(f"⚠️ 워크시트 '{sheet_name}'이 없어서 생성합니다.")
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            print(f"✅ 워크시트 '{sheet_name}' 생성 완료")
        
        return worksheet
        
    except Exception as e:
        print(f"❌ Google Sheets 연결 오류: {e}")
        return None 