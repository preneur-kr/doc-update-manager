from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import document, slack
from datetime import datetime

app = FastAPI(
    title="Hotel Bot API",
    description="Hotel Bot API with Slack integration",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://api.slack.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "X-Slack-Request-Timestamp", "X-Slack-Signature", "Content-Type"],
    expose_headers=["*"]
)

# 라우터 등록
app.include_router(document.router, prefix="/api/v1", tags=["document"])
app.include_router(slack.router, prefix="/api/v1/slack", tags=["slack"])

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
        # 필수 환경 변수 검증
        required_vars = {
            "GOOGLE_SHEET_ID": settings.GOOGLE_SHEET_ID,
            "GOOGLE_CREDENTIALS_PATH": settings.GOOGLE_CREDENTIALS_PATH,
            "SLACK_WEBHOOK_URL": settings.SLACK_WEBHOOK_URL,
            "SLACK_DOCUPDATE_WEBHOOK_URL": settings.SLACK_DOCUPDATE_WEBHOOK_URL
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise HTTPException(
                status_code=500,
                detail=f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "google_sheet_id": settings.GOOGLE_SHEET_ID[:8] + "..." if settings.GOOGLE_SHEET_ID else None,
                "slack_webhook_configured": bool(settings.SLACK_WEBHOOK_URL),
                "slack_docupdate_webhook_configured": bool(settings.SLACK_DOCUPDATE_WEBHOOK_URL)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 