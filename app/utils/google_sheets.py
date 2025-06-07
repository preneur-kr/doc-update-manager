import os
from typing import Optional, List, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from app.core.config import settings

def get_google_sheets_client() -> Optional[gspread.Client]:
    """
    Google Sheets API 클라이언트를 초기화하고 반환합니다.
    
    Returns:
        Optional[gspread.Client]: 초기화된 Google Sheets 클라이언트
    """
    try:
        if not settings.GOOGLE_CREDENTIALS_PATH:
            raise ValueError("GOOGLE_CREDENTIALS_PATH environment variable is not set")
            
        if not settings.GOOGLE_SHEET_ID:
            raise ValueError("GOOGLE_SHEET_ID environment variable is not set")
            
        # Google Sheets API 인증
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            settings.GOOGLE_CREDENTIALS_PATH,
            scopes=scopes
        )
        
        # Google Sheets 클라이언트 초기화
        client = gspread.authorize(credentials)
        return client
        
    except Exception as e:
        print(f"Google Sheets 클라이언트 초기화 실패: {str(e)}")
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
        client = get_google_sheets_client()
        if not client:
            return None
            
        # 스프레드시트 열기
        spreadsheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
        
        # 워크시트 가져오기 (없으면 생성)
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            
        return worksheet
        
    except Exception as e:
        print(f"워크시트 가져오기 실패: {str(e)}")
        return None

def append_row(sheet_name: str, data: List[Any]) -> bool:
    """
    워크시트에 새로운 행을 추가합니다.
    
    Args:
        sheet_name (str): 워크시트 이름
        data (List[Any]): 추가할 데이터 리스트
        
    Returns:
        bool: 성공 여부
    """
    try:
        worksheet = get_worksheet(sheet_name)
        if not worksheet:
            return False
            
        worksheet.append_row(data)
        return True
        
    except Exception as e:
        print(f"행 추가 실패: {str(e)}")
        return False

def get_all_records(sheet_name: str) -> List[Dict[str, Any]]:
    """
    워크시트의 모든 레코드를 가져옵니다.
    
    Args:
        sheet_name (str): 워크시트 이름
        
    Returns:
        List[Dict[str, Any]]: 레코드 리스트
    """
    try:
        worksheet = get_worksheet(sheet_name)
        if not worksheet:
            return []
            
        return worksheet.get_all_records()
        
    except Exception as e:
        print(f"레코드 가져오기 실패: {str(e)}")
        return [] 