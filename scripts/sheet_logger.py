from typing import Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv
from scripts.google_sheets_utils import get_worksheet

# Load environment variables
load_dotenv()
GOOGLE_CHAT_LOG_SHEET_NAME = os.getenv("GOOGLE_CHAT_LOG_SHEET_NAME", "chat_logs")

def log_to_sheet(data: Dict[str, Any]) -> bool:
    """
    Google Sheets에 로그를 기록합니다.
    
    Args:
        data (Dict[str, Any]): 기록할 데이터
        
    Returns:
        bool: 기록 성공 여부
    """
    try:
        # 워크시트 가져오기
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
        print(f"Google Sheets 로깅 실패: {str(e)}")
        return False 