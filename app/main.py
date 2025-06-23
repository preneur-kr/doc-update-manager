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
# 🚨 배포 시 주의사항:
# - ngrok을 사용하는 경우: allow_origins=["*", "https://api.slack.com"]
# - Render 배포 시: allow_origins=["https://api.slack.com"]로 변경 권장
# - Slack Request URL을 Render 주소로 업데이트 필요
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

@app.get("/ping")
async def ping():
    """Simple health check endpoint for load balancers"""
    return {"status": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    try:
        # 필수 환경 변수 검증
        required_vars = {
            "GOOGLE_SHEET_ID": settings.GOOGLE_SHEET_ID,
            "SLACK_BOT_TOKEN": settings.SLACK_BOT_TOKEN,
            "SLACK_SIGNING_SECRET": settings.SLACK_SIGNING_SECRET
        }
        
        # Google Credentials 검증 (둘 중 하나만 있으면 됨)
        if not settings.GOOGLE_CREDENTIALS_PATH and not settings.GOOGLE_CREDENTIALS_JSON:
            raise HTTPException(
                status_code=500,
                detail="Missing Google credentials. Set either GOOGLE_CREDENTIALS_PATH or GOOGLE_CREDENTIALS_JSON."
            )
        
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
                "slack_bot_token_configured": bool(settings.SLACK_BOT_TOKEN),
                "slack_signing_secret_configured": bool(settings.SLACK_SIGNING_SECRET),
                "google_credentials_configured": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 