from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import document, slack
from app.api.endpoints.chat import router as chat_router
from datetime import datetime

# Hotel Bot API with Chat functionality
app = FastAPI(
    title="Hotel Bot API",
    description="Hotel Bot API with Slack integration",
    version="1.0.0"
)

# CORS 설정
# 개발 환경과 프로덕션 환경 모두 지원
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 개발 서버
        "http://localhost:3000",  # 일반적인 React 개발 서버
        "https://api.slack.com",  # Slack API
        "*"  # 기타 모든 출처 (개발 환경용)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
    expose_headers=["*"]  # 모든 헤더 노출
)

# 라우터 등록
app.include_router(document.router, prefix="/api/v1", tags=["document"])
app.include_router(slack.router, prefix="/api/v1/slack", tags=["slack"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])

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