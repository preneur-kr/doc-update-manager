from typing import Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv
from scripts.google_sheets_utils import get_worksheet

# Load environment variables
load_dotenv()
GOOGLE_CHAT_LOG_SHEET_NAME = os.getenv("GOOGLE_CHAT_LOG_SHEET_NAME", "chat_logs")
GOOGLE_DOC_LOG_SHEET_NAME = os.getenv("GOOGLE_DOC_LOG_SHEET_NAME", "doc_update_logs")

def log_to_sheet(data: Dict[str, Any], sheet_name: str = None) -> bool:
    """
    Google Sheets에 로그를 기록합니다.
    
    Args:
        data (Dict[str, Any]): 기록할 데이터
        sheet_name (str, optional): 시트 이름. 기본값은 GOOGLE_DOC_LOG_SHEET_NAME
        
    Returns:
        bool: 기록 성공 여부
    """
    try:
        # 문서 업데이트 로그인 경우
        if "document_path" in data:
            sheet = get_worksheet(sheet_name or GOOGLE_DOC_LOG_SHEET_NAME)
            if not sheet:
                return False
            
            # 데이터 행 구성
            row = [
                data.get("timestamp", datetime.now().isoformat()),
                data.get("document_path", ""),
                data.get("change_type", ""),
                data.get("change_keywords", "[]"),
                data.get("chunks_plus", "[]"),
                data.get("chunks_minus", "[]"),
                data.get("chunks_tilde", "[]"),
                data.get("approved", False),
                data.get("comment", ""),
                data.get("slack_message_url", "")
            ]
        # 채팅 로그인 경우
        else:
            sheet = get_worksheet(GOOGLE_CHAT_LOG_SHEET_NAME)
            if not sheet:
                return False
            
            # 데이터 행 구성
            row = [
                data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                data.get("question", ""),
                data.get("answer", ""),
                str(data.get("is_fallback", False)),
                data.get("search_results", "[]")
            ]
        
        # 시트에 데이터 추가
        sheet.append_row(row)
        return True
        
    except Exception as e:
        print(f"❌ Google Sheet 로깅 중 오류 발생: {str(e)}")
        return False 