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
        print(f"🔍 DEBUG: log_to_sheet 시작 - sheet_name: {sheet_name}")
        print(f"🔍 DEBUG: data keys: {list(data.keys())}")
        print(f"🔍 DEBUG: document_path in data: {'document_path' in data}")
        
        # 문서 업데이트 로그인 경우
        if "document_path" in data:
            print(f"🔍 DEBUG: 문서 업데이트 로그 처리 시작")
            print(f"🔍 DEBUG: 사용할 시트 이름: {sheet_name or GOOGLE_DOC_LOG_SHEET_NAME}")
            print(f"🔍 DEBUG: GOOGLE_DOC_LOG_SHEET_NAME 환경변수: {GOOGLE_DOC_LOG_SHEET_NAME}")
            
            sheet = get_worksheet(sheet_name or GOOGLE_DOC_LOG_SHEET_NAME)
            if not sheet:
                print("❌ DEBUG: get_worksheet에서 None 반환됨")
                return False
            
            print("✅ DEBUG: 워크시트 가져오기 성공")
            
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
            
            print(f"🔍 DEBUG: 구성된 row 데이터:")
            for i, value in enumerate(row):
                print(f"  [{i}] {type(value)}: {str(value)[:100]}...")
                
        # 채팅 로그인 경우
        else:
            print(f"🔍 DEBUG: 채팅 로그 처리 시작")
            print(f"🔍 DEBUG: 사용할 시트 이름: {GOOGLE_CHAT_LOG_SHEET_NAME}")
            
            sheet = get_worksheet(GOOGLE_CHAT_LOG_SHEET_NAME)
            if not sheet:
                print("❌ DEBUG: get_worksheet에서 None 반환됨")
                return False
            
            print("✅ DEBUG: 워크시트 가져오기 성공")
            
            # 데이터 행 구성
            row = [
                data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                data.get("question", ""),
                data.get("answer", ""),
                str(data.get("is_fallback", False)),
                data.get("search_results", "[]")
            ]
        
            print(f"🔍 DEBUG: 구성된 row 데이터:")
            for i, value in enumerate(row):
                print(f"  [{i}] {type(value)}: {str(value)[:100]}...")
        
        print("🔍 DEBUG: sheet.append_row() 호출 시작...")
        # 시트에 데이터 추가
        sheet.append_row(row)
        print("✅ DEBUG: sheet.append_row() 성공")
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: Google Sheet 로깅 중 오류 발생")
        print(f"❌ DEBUG: 에러 타입: {type(e)}")
        print(f"❌ DEBUG: 에러 메시지: {str(e)}")
        print(f"❌ DEBUG: 에러 상세: {repr(e)}")
        import traceback
        print(f"❌ DEBUG: 스택 트레이스:")
        traceback.print_exc()
        return False 