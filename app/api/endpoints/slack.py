from fastapi import APIRouter, Request, HTTPException
from app.core.security import verify_slack_request
from app.services.slack_service import SlackService
import json
import os
from datetime import datetime

router = APIRouter()

@router.post("/events")
async def handle_slack_events(request: Request):
    """
    Slack 이벤트를 처리합니다.
    """
    try:
        print("DEBUG: Received Slack event request")
        # 요청 헤더 검증
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        signature = request.headers.get("X-Slack-Signature")
        
        print(f"DEBUG: Headers - timestamp: {timestamp}, signature: {signature}")
        
        if not timestamp or not signature:
            print("DEBUG: Missing required Slack headers")
            raise HTTPException(
                status_code=400,
                detail="Missing required Slack headers"
            )
            
        # 요청 본문 읽기
        body = await request.body()
        print(f"DEBUG: Request body: {body.decode()}")
        
        # 요청 검증
        if not verify_slack_request(body, timestamp, signature):
            print("DEBUG: Invalid Slack request signature")
            raise HTTPException(
                status_code=401,
                detail="Invalid Slack request signature"
            )
            
        # 이벤트 데이터 파싱
        event_data = json.loads(body)
        print(f"DEBUG: Parsed event data: {event_data}")
        
        # Slack 서비스를 통해 이벤트 처리
        return await SlackService.handle_event(event_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Error processing Slack event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Slack event: {str(e)}"
        )

@router.post("/test-event")
async def test_slack_event():
    """
    개발 환경에서 Slack 이벤트를 테스트합니다.
    """
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in development environment"
        )
    
    # 테스트용 이벤트 데이터
    test_event = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "text": "Test message",
            "user": "U1234567890",
            "ts": datetime.now().timestamp(),
            "channel": "C1234567890"
        }
    }
    
    # Slack 서비스를 통해 이벤트 처리
    return await SlackService.handle_event(test_event)

@router.options("/events")
async def handle_slack_events_options():
    """
    Slack 이벤트 OPTIONS 요청을 처리합니다.
    """
    return {"status": "ok"} 