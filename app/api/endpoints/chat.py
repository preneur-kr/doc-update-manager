from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from scripts.query_runner import run_query
from scripts.sheet_logger import log_to_sheet
from scripts.slack_alert_manager import SlackAlertManager
from scripts.fallback_logger import log_fallback_to_sheet
from scripts.answer_guard import is_fallback_like_response
from datetime import datetime
import json

router = APIRouter()

# 요청 모델 정의
class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None
    section: Optional[str] = None

# 응답 모델 정의
class ChatResponse(BaseModel):
    answer: str
    is_fallback: bool
    timestamp: str
    search_results: Optional[list] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    호텔 정책에 대한 질문을 처리하고 답변을 반환합니다.
    """
    try:
        print(f"📝 채팅 요청 받음: {request.message}")
        
        # 1. 질문 처리
        original_answer, search_results, is_fallback = run_query(
            question=request.message,
            category=request.category,
            section=request.section
        )
        
        # 2. fallback-like 응답 감지
        is_fallback_like = is_fallback_like_response(original_answer)
        
        # 3. 최종 표시할 응답 결정
        if is_fallback:
            displayed_answer = (
                "죄송합니다. 해당 내용에 대해선 지금 바로 정확한 안내가 어려워,\n"
                "👉 02-1234-5678번으로 연락 주시면 더 빠르게 도와드릴 수 있습니다."
            )
        else:
            displayed_answer = original_answer
        
        # 4. 로깅 및 알림 처리
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if is_fallback:
            # Fallback 로깅
            top_result = search_results[0][0] if search_results else None
            slack_success = SlackAlertManager.send_fallback_alert(
                question=request.message,
                gpt_response=original_answer,
                displayed_answer=displayed_answer,
                fallback_type="fallback",
                top_result=top_result
            )
            
            log_fallback_to_sheet(
                fallback_type="LOW_SIMILARITY",
                similarity_scores=[score for _, score in search_results] if search_results else [0.0],
                query=request.message,
                gpt_response=original_answer,
                displayed_answer=displayed_answer,
                slack_sent=slack_success,
                confirmed=False,
                needs_update=True,
                notes="API를 통한 fallback 응답"
            )
            
        elif is_fallback_like:
            # Fallback-like 로깅
            top_result = search_results[0][0] if search_results else None
            slack_success = SlackAlertManager.send_fallback_alert(
                question=request.message,
                gpt_response=original_answer,
                displayed_answer=displayed_answer,
                fallback_type="fallback-like",
                top_result=top_result
            )
            
            log_fallback_to_sheet(
                fallback_type="FALLBACK_LIKE",
                similarity_scores=[score for _, score in search_results] if search_results else [0.0],
                query=request.message,
                gpt_response=original_answer,
                displayed_answer=displayed_answer,
                slack_sent=slack_success,
                confirmed=False,
                needs_update=True,
                notes="API를 통한 fallback-like 응답"
            )
            
        else:
            # 일반 로깅
            log_data = {
                "timestamp": timestamp,
                "question": request.message,
                "answer": displayed_answer,
                "is_fallback": False,
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
            log_to_sheet(data=log_data)
        
        # 5. 응답 구성
        response_data = {
            "answer": displayed_answer,
            "is_fallback": is_fallback,
            "timestamp": timestamp,
            "search_results": [
                {
                    "text": metadata.get("text", ""),
                    "section": metadata.get("section", "N/A"),
                    "category": metadata.get("category", "N/A"),
                    "score": score
                }
                for metadata, score in search_results
            ] if search_results else None
        }
        
        print(f"✅ 채팅 응답 완료: {len(displayed_answer)}자")
        return ChatResponse(**response_data)
        
    except Exception as e:
        print(f"❌ 채팅 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/health")
async def chat_health_check():
    """
    챗봇 API 상태 확인
    """
    return {
        "status": "healthy",
        "service": "chat-api",
        "timestamp": datetime.now().isoformat()
    } 