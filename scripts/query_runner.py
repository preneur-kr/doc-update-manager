# scripts/query_runner.py

import os
import json
import readline  # 터미널 입력 개선을 위한 모듈 추가
from datetime import datetime
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from scripts.filtered_vector_search import FilteredVectorSearch
from scripts.answer_guard import is_fallback_response, is_fallback_like_response
from scripts.slack_alert_manager import SlackAlertManager  # SlackAlertManager import 활성화
from scripts.sheet_logger import log_to_sheet
from scripts.fallback_logger import log_fallback_to_sheet

# ✅ 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

# ✅ 상수 정의
FALLBACK_MESSAGE = (
    "죄송합니다. 해당 내용에 대해선 지금 바로 정확한 안내가 어려워,\n"
    "👉 02-1234-5678번으로 연락 주시면 더 빠르게 도와드릴 수 있습니다."
)

# ✅ 기본 프롬프트 템플릿
DEFAULT_PROMPT_TEMPLATE = """
다음은 우리 호텔의 정책 문서입니다. 아래 내용을 참고하여 고객의 질문에 정확히 답변해주세요.

{context}

고객 질문: {question}

※ 반드시 아래 조건을 지켜주세요:
- 문서에 *직접적으로 명시된 내용*만을 바탕으로 답변하세요.
- 문서에 정보가 없거나 불명확한 경우에는 "정확한 안내가 어렵습니다"라고만 답변하세요.
- 추측하거나 일반적인 상식에 기반한 응답을 하지 마세요.
- 특히 시간, 날짜, 금액과 같은 정보는 정확히 전달해야 하며, 문서에 없다면 절대 임의로 생성하지 마세요.
"""

# ✅ 프롬프트 템플릿 로드
def load_prompt_template() -> str:
    """
    프롬프트 템플릿 파일을 로드합니다.
    파일이 없거나 로드 실패 시 기본 템플릿을 반환합니다.
    
    Returns:
        str: 프롬프트 템플릿 문자열
    """
    # 1. prompts 디렉토리 생성
    try:
        os.makedirs("prompts", exist_ok=True)
        print("✅ prompts 디렉토리 확인/생성 완료")
    except Exception as e:
        print(f"❌ prompts 디렉토리 생성 실패: {str(e)}")
        return DEFAULT_PROMPT_TEMPLATE
    
    # 2. 프롬프트 파일 로드
    prompt_path = "prompts/prompt_hotel_policy.txt"
    try:
        if not os.path.exists(prompt_path):
            print(f"⚠️ 프롬프트 파일이 없습니다: {prompt_path}")
            print("기본 프롬프트 템플릿을 사용합니다.")
            return DEFAULT_PROMPT_TEMPLATE
            
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
            if not template.strip():
                print("⚠️ 프롬프트 파일이 비어있습니다.")
                return DEFAULT_PROMPT_TEMPLATE
            print("✅ 프롬프트 템플릿 로드 성공")
            return template
            
    except UnicodeDecodeError:
        print("❌ 프롬프트 파일 인코딩 오류: UTF-8이 아닌 인코딩이 감지됨")
        return DEFAULT_PROMPT_TEMPLATE
    except Exception as e:
        print(f"❌ 프롬프트 템플릿 로드 실패: {str(e)}")
        return DEFAULT_PROMPT_TEMPLATE

# ✅ 프롬프트 템플릿 로드
PROMPT_TEMPLATE = load_prompt_template()

def run_query(
    question: str,
    category: Optional[str] = None,
    section: Optional[str] = None,
    k: int = 3,
    score_threshold: float = 0.7
) -> Tuple[str, List[Tuple[dict, float]], bool]:
    """
    사용자 질문에 대한 답변을 생성합니다.
    
    Args:
        question (str): 사용자 질문
        category (Optional[str]): 카테고리 필터
        section (Optional[str]): 섹션 필터
        k (int): 검색할 문서 수
        score_threshold (float): 최소 유사도 점수
        
    Returns:
        Tuple[str, List[Tuple[dict, float]], bool]: (생성된 답변, 검색된 문서와 점수, fallback 여부)
    """
    # 1. 벡터 검색 수행
    searcher = FilteredVectorSearch()
    search_results = searcher.similarity_search_with_metadata(
        query=question,
        k=k,
        category=category,
        section=section,
        score_threshold=score_threshold
    )
    
    # 2. 검색 결과가 없는 경우
    if not search_results:
        print("\n=== 검색 결과 없음: Fallback 응답 반환 ===")
        return FALLBACK_MESSAGE, [], True
    
    # 3. 컨텍스트 구성
    context = "\n\n".join([
        f"문서 {i+1}:\n{metadata['text']}\n"
        f"섹션: {metadata.get('section', 'N/A')}\n"
        f"카테고리: {metadata.get('category', 'N/A')}"
        for i, (metadata, _) in enumerate(search_results)
    ])
    
    # 4. GPT 답변 생성
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )
    
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    
    response = chain.invoke({
        "context": context,
        "question": question
    })
    
    # 5. GPT 응답이 fallback인지 확인
    is_fallback = is_fallback_response(response.content)
    if is_fallback:
        print("\n=== GPT 응답이 fallback으로 감지됨 ===")
        return FALLBACK_MESSAGE, search_results, True
    
    return response.content, search_results, False

def process_query(question: str, category: Optional[str] = None, section: Optional[str] = None) -> None:
    """
    사용자 질문을 처리하고 결과를 로깅합니다.
    
    Args:
        question (str): 사용자 질문
        category (Optional[str]): 카테고리 필터
        section (Optional[str]): 섹션 필터
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. 질문 처리
    original_answer, search_results, is_fallback = run_query(
        question=question,
        category=category,
        section=section
    )
    
    # 2. fallback-like 응답 감지
    is_fallback_like = is_fallback_like_response(original_answer)
    
    # 3. 최종 표시할 응답 결정
    displayed_answer = FALLBACK_MESSAGE if is_fallback else original_answer
    
    # 4. 결과 출력
    print("\n=== 응답 결과 ===")
    print(f"질문: {question}")
    print(f"답변: {displayed_answer}")
    print(f"Fallback 여부: {'예' if is_fallback else '아니오'}")
    print(f"Fallback-like 여부: {'예' if is_fallback_like else '아니오'}")
    
    # 5. 로깅 및 알림
    if is_fallback:
        print("\n=== Fallback 응답 로깅 시작 ===")
        print(f"Fallback 감지 이유: {'검색 결과 없음' if not search_results else 'GPT 응답이 fallback 키워드 포함'}")

        # 5.1 Slack 알림 전송 (SlackAlertManager 사용)
        print("\n--- 📣 Slack 알림 전송 ---")
        top_result = search_results[0][0] if search_results else None
        slack_success = SlackAlertManager.send_fallback_alert(
            question=question,
            gpt_response=original_answer,
            displayed_answer=displayed_answer,
            fallback_type="fallback",
            top_result=top_result
        )
        
        if slack_success:
            print("✅ Slack 알림 전송 성공!")
        else:
            print("❌ Slack 알림 전송 실패")

        # 5.2 Fallback 로깅
        print("\n--- 📊 Fallback 시트 로깅 시작 ---")
        success = log_fallback_to_sheet(
            fallback_type="LOW_SIMILARITY",
            similarity_scores=[score for _, score in search_results] if search_results else [0.0],
            query=question,
            gpt_response=original_answer,
            displayed_answer=displayed_answer,
            slack_sent=slack_success,
            confirmed=False,
            needs_update=True,
            notes="자동 감지된 fallback 응답"
        )
        if not success:
            print("❌ Fallback 로깅 실패")
        return  # 여기서 함수를 종료하여 일반 로깅이 실행되지 않도록 함
    
    # 5.3 Fallback-like 응답 처리
    elif is_fallback_like:
        print("\n=== Fallback-like 응답 로깅 시작 ===")
        print(f"Fallback-like 감지 이유: GPT 응답이 fallback-like 키워드 포함")

        # 5.4 Slack 알림 전송 (SlackAlertManager 사용)
        print("\n--- 📣 Fallback-like Slack 알림 전송 ---")
        top_result = search_results[0][0] if search_results else None
        slack_success = SlackAlertManager.send_fallback_alert(
            question=question,
            gpt_response=original_answer,
            displayed_answer=displayed_answer,
            fallback_type="fallback-like",
            top_result=top_result
        )
        
        if slack_success:
            print("✅ Fallback-like Slack 알림 전송 성공!")
        else:
            print("❌ Fallback-like Slack 알림 전송 실패")

        # 5.5 Fallback-like 로깅
        print("\n--- 📊 Fallback-like 시트 로깅 시작 ---")
        success = log_fallback_to_sheet(
            fallback_type="FALLBACK_LIKE",
            similarity_scores=[score for _, score in search_results] if search_results else [0.0],
            query=question,
            gpt_response=original_answer,
            displayed_answer=displayed_answer,
            slack_sent=slack_success,
            confirmed=False,
            needs_update=True,
            notes="자동 감지된 fallback-like 응답"
        )
        if not success:
            print("❌ Fallback-like 로깅 실패")
        return  # 여기서 함수를 종료하여 일반 로깅이 실행되지 않도록 함
    
    # 5.6 일반 로깅 (fallback이나 fallback-like가 아닌 경우에만 실행)
    print("\n=== 일반 응답 로깅 시작 ===")
    log_data = {
        "timestamp": timestamp,
        "question": question,
        "answer": displayed_answer,
        "is_fallback": False,  # fallback이 아닌 경우에만 False
        "search_results": json.dumps([
            {
                "text": metadata.get("text", ""),
                "section": metadata.get("section", "N/A"),
                "category": metadata.get("category", "N/A"),
                "score": score
            }
            for metadata, score in search_results
        ], ensure_ascii=False)
    }
    success = log_to_sheet(data=log_data)
    if not success:
        print("❌ 일반 로깅 실패")

def main():
    """메인 실행 함수"""
    # readline 설정
    readline.parse_and_bind('bind ^I rl_complete')
    
    while True:
        try:
            question = input("\n질문을 입력하세요 (종료: q): ")
            if question.lower() == 'q':
                break
                
            process_query(question)
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()