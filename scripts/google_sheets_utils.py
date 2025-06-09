import os
import json
from typing import Optional
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials path from environment (이제는 JSON 내용이 들어있음)
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def get_google_sheets_client() -> Optional[gspread.Client]:
    """
    Google Sheets API 클라이언트를 초기화하고 반환합니다.
    
    Returns:
        Optional[gspread.Client]: 초기화된 Google Sheets 클라이언트
    """
    try:
        if not GOOGLE_CREDENTIALS_PATH:
            raise ValueError("GOOGLE_CREDENTIALS_PATH environment variable (JSON content) is not set")
            
        if not GOOGLE_SHEET_ID:
            raise ValueError("GOOGLE_SHEET_ID environment variable is not set")
            
        print("\n=== Google Sheets 클라이언트 초기화 ===")
        # print(f"Credentials 경로: {GOOGLE_CREDENTIALS_PATH}") # 더 이상 경로가 아님
        
        # Google Sheets API 인증 (JSON 내용에서 직접 로드)
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # 환경 변수에서 JSON 문자열을 파싱
        credentials_info = json.loads(GOOGLE_CREDENTIALS_PATH)
        
        credentials = Credentials.from_service_account_info(
            credentials_info, # 파일 경로 대신 파싱된 JSON 정보 사용
            scopes=scopes
        )
        
        # 서비스 계정 이메일 출력
        print(f"서비스 계정 이메일: {credentials.service_account_email}")
        
        # Google Sheets 클라이언트 초기화
        client = gspread.authorize(credentials)
        print("✅ 클라이언트 초기화 성공")
        return client
        
    except json.JSONDecodeError as e:
        print(f"❌ GOOGLE_CREDENTIALS_PATH 환경 변수 파싱 오류: 유효한 JSON 형식이 아닙니다. {str(e)}")
        return None
    except Exception as e:
        print(f"\n❌ Google Sheets 클라이언트 초기화 실패")
        print(f"에러 유형: {type(e)}")
        print(f"에러 메시지: {str(e)}")
        if "insufficient permission" in str(e).lower():
            print("\n⚠️ 권한 문제가 감지되었습니다.")
            print("1. Google Sheets 문서에 서비스 계정 이메일을 편집자로 추가했는지 확인")
            print("2. 권한 변경 후 몇 분 정도 기다려주세요")
            print("3. 여전히 문제가 있다면 문서를 다시 공유해보세요")
        return None

def get_worksheet(sheet_name: str) -> Optional[gspread.Worksheet]:
    """
    지정된 이름의 워크시트를 가져옵니다.
    
    Args:
        sheet_name (str): 워크시트 이름
        
    Returns:
        Optional[gspread.Worksheet]: 워크시트 객체
    """
    try:
        print(f"\n=== 워크시트 가져오기 시도 ===")
        print(f"시트 이름: {sheet_name}")
        
        client = get_google_sheets_client()
        if not client:
            print("❌ Google Sheets 클라이언트 초기화 실패")
            return None
            
        # 스프레드시트 열기
        print(f"스프레드시트 ID: {GOOGLE_SHEET_ID}")
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        print(f"✅ 스프레드시트 열기 성공: {spreadsheet.title}")
        
        # 워크시트 가져오기 (없으면 생성)
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"✅ 기존 워크시트 찾음: {worksheet.title}")
        except gspread.exceptions.WorksheetNotFound:
            print(f"⚠️ 워크시트를 찾을 수 없음. 새로 생성합니다: {sheet_name}")
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            print(f"✅ 새 워크시트 생성 완료: {worksheet.title}")
            
        return worksheet
        
    except Exception as e:
        print(f"❌ 워크시트 가져오기 실패: {str(e)}")
        print(f"에러 유형: {type(e)}")
        return None 