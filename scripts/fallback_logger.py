from datetime import datetime
import os
from dotenv import load_dotenv
from scripts.google_sheets_utils import get_worksheet

# Load environment variables
load_dotenv()
GOOGLE_FALLBACK_LOG_SHEET_NAME = os.getenv("GOOGLE_FALLBACK_LOG_SHEET_NAME", "fallback_logs")

def log_fallback_to_sheet(
    fallback_type: str,
    similarity_scores: list,
    query: str,
    gpt_response: str,
    displayed_answer: str,
    slack_sent: bool,
    confirmed: bool,
    needs_update: bool,
    notes: str
) -> bool:
    """
    Fallback 응답을 Google Sheets에 기록합니다.
    
    Args:
        fallback_type (str): Fallback 유형
        similarity_scores (list): 유사도 점수 목록
        query (str): 사용자 질문
        gpt_response (str): GPT 원본 응답
        displayed_answer (str): 표시된 답변
        slack_sent (bool): Slack 알림 전송 여부
        confirmed (bool): 관리자 확인 여부
        needs_update (bool): 문서 업데이트 필요 여부
        notes (str): 추가 메모
        
    Returns:
        bool: 기록 성공 여부
    """
    try:
        print("\n=== Fallback 로깅 시작 ===")
        print(f"시트 이름: {GOOGLE_FALLBACK_LOG_SHEET_NAME}")
        print(f"환경 변수 확인:")
        print(f"- GOOGLE_SHEET_ID: {'설정됨' if os.getenv('GOOGLE_SHEET_ID') else '설정되지 않음'}")
        print(f"- GOOGLE_CREDENTIALS_PATH: {'설정됨' if os.getenv('GOOGLE_CREDENTIALS_PATH') else '설정되지 않음'}")
        print(f"- GOOGLE_SERVICE_ACCOUNT_EMAIL: {'설정됨' if os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL') else '설정되지 않음'}")
        
        # 워크시트 가져오기
        sheet = get_worksheet(GOOGLE_FALLBACK_LOG_SHEET_NAME)
        if not sheet:
            print("❌ 워크시트를 가져올 수 없습니다.")
            print("1. GOOGLE_FALLBACK_LOG_SHEET_NAME 환경 변수가 올바르게 설정되어 있는지 확인")
            print("2. Google Sheets 문서에 서비스 계정이 접근 권한이 있는지 확인")
            print("3. 서비스 계정 이메일:", os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL"))
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        scores_str = ", ".join([f"{score:.4f}" for score in similarity_scores])

        row = [
            timestamp,             # Timestamp
            fallback_type,         # Fallback Type
            scores_str,            # Similarity Score(s)
            query,                 # User Query
            gpt_response,          # GPT Response
            displayed_answer,      # Displayed Answer
            str(slack_sent),       # SlackAlertSent
            str(confirmed),        # ConfirmedByAdmin
            str(needs_update),     # NeedsUpdateInDocs
            notes                  # Notes
        ]

        print("📝 데이터 준비 완료, 시트에 기록 시도...")
        print(f"기록할 데이터:")
        print(f"- Timestamp: {timestamp}")
        print(f"- Fallback Type: {fallback_type}")
        print(f"- Query: {query[:50]}...")
        print(f"- GPT Response: {gpt_response[:50]}...")
        print(f"- Displayed Answer: {displayed_answer[:50]}...")
        
        try:
            sheet.append_row(row)
            print("✅ Google Sheet 로그 기록 완료")
            return True
        except Exception as append_error:
            print("\n❗️데이터 추가 중 오류 발생")
            print(f"에러 유형: {type(append_error)}")
            print(f"에러 메시지: {str(append_error)}")
            return False

    except Exception as e:
        print("\n❗️Google Sheet 로깅 중 오류 발생")
        print(f"에러 유형: {type(e)}")
        print(f"에러 메시지: {str(e)}")
        print("\n상세 정보:")
        print(f"- 시트 이름: {GOOGLE_FALLBACK_LOG_SHEET_NAME}")
        print(f"- Fallback 유형: {fallback_type}")
        print(f"- 질문 길이: {len(query)}")
        print(f"- GPT 응답 길이: {len(gpt_response)}")
        print(f"- 표시된 답변 길이: {len(displayed_answer)}")
        
        if "insufficient permission" in str(e).lower():
            print("\n⚠️ 권한 문제가 감지되었습니다.")
            print("1. Google Sheets 문서에 서비스 계정 이메일을 편집자로 추가했는지 확인")
            print("2. 권한 변경 후 몇 분 정도 기다려주세요")
            print("3. 여전히 문제가 있다면 문서를 다시 공유해보세요")
        return False