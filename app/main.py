from fastapi import FastAPI, HTTPException, Request
from app.core.config import settings
from app.utils.google_sheets import append_row
from datetime import datetime
from typing import Dict, Any
import hmac
import hashlib
import json

app = FastAPI(
    title="Hotel Bot API",
    description="Hotel Bot API with Slack integration",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Hotel Bot API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    try:
        # 환경 변수 검증
        required_vars = [
            "GOOGLE_SHEET_ID",
            "GOOGLE_CREDENTIALS_PATH",
            "SLACK_WEBHOOK_URL",
            "SLACK_DOCUPDATE_WEBHOOK_URL"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(settings, var, None)]
        if missing_vars:
            raise HTTPException(
                status_code=500,
                detail=f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "google_sheet_id": settings.GOOGLE_SHEET_ID[:8] + "..." if settings.GOOGLE_SHEET_ID else None,
                "slack_webhook_configured": bool(settings.SLACK_WEBHOOK_URL),
                "slack_docupdate_webhook_configured": bool(settings.SLACK_DOCUPDATE_WEBHOOK_URL)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@app.post("/api/v1/logs/document-update")
async def log_document_update(request: Request):
    """
    문서 업데이트 로그를 Google Sheets에 기록합니다.
    """
    try:
        data = await request.json()
        
        # 필수 필드 검증
        required_fields = ["document_id", "update_type", "updated_by"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # 로그 데이터 준비
        log_data = [
            datetime.now().isoformat(),  # timestamp
            data["document_id"],
            data["update_type"],
            data["updated_by"],
            data.get("description", ""),  # 선택적 필드
            data.get("changes", "")  # 선택적 필드
        ]
        
        # Google Sheets에 로그 추가
        success = append_row(settings.GOOGLE_DOC_LOG_SHEET_NAME, log_data)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to log document update"
            )
        
        return {
            "status": "success",
            "message": "Document update logged successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document update log: {str(e)}"
        )

def verify_slack_request(request_body: bytes, timestamp: str, signature: str) -> bool:
    """
    Slack 요청의 유효성을 검증합니다.
    """
    if not settings.SLACK_SIGNING_SECRET:
        return False
        
    # Slack 요청 검증을 위한 문자열 생성
    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"
    
    # 서명 생성
    my_signature = f"v0={hmac.new(
        settings.SLACK_SIGNING_SECRET.encode('utf-8'),
        sig_basestring.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()}"
    
    return hmac.compare_digest(my_signature, signature)

@app.post("/api/v1/slack/events")
async def handle_slack_events(request: Request):
    """
    Slack 이벤트를 처리합니다.
    """
    try:
        # 요청 헤더 검증
        timestamp = request.headers.get("X-Slack-Request-Timestamp")
        signature = request.headers.get("X-Slack-Signature")
        
        if not timestamp or not signature:
            raise HTTPException(
                status_code=400,
                detail="Missing required Slack headers"
            )
            
        # 요청 본문 읽기
        body = await request.body()
        
        # 요청 검증
        if not verify_slack_request(body, timestamp, signature):
            raise HTTPException(
                status_code=401,
                detail="Invalid Slack request signature"
            )
            
        # 이벤트 데이터 파싱
        event_data = json.loads(body)
        
        # URL 검증 요청 처리
        if event_data.get("type") == "url_verification":
            return {"challenge": event_data["challenge"]}
            
        # 이벤트 타입에 따른 처리
        event_type = event_data.get("event", {}).get("type")
        if event_type == "message":
            # 메시지 이벤트 처리
            message = event_data["event"]
            # 여기에 메시지 처리 로직 추가
            
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Slack event: {str(e)}"
        ) 