from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import document, slack
from app.api.endpoints.chat import router as chat_router
from datetime import datetime
import asyncio
import threading

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
        "http://localhost:5173",  # Vite 개발 서버 (기본)
        "http://localhost:5174",  # Vite 개발 서버 (설정된 포트)
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

# 연결 워밍업 실행
def warm_up_connections():
    """연결을 워밍업합니다."""
    try:
        print("🔥 연결 워밍업 시작...")
        from scripts.connection_manager import connection_manager
        connection_manager.warm_up()
        print("✅ 연결 워밍업 완료")
        return True
    except Exception as e:
        print(f"❌ 연결 워밍업 실패: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    print("🚀 Hotel Bot API 시작 중...")
    
    # 우선 백그라운드에서 연결 워밍업 시작
    loop = asyncio.get_event_loop()
    warmup_task = loop.run_in_executor(None, warm_up_connections)
    
    # 중요한 연결은 즉시 초기화
    try:
        from scripts.connection_manager import connection_manager
        # OpenAI 연결만 먼저 초기화 (가장 중요)
        _ = connection_manager.openai_llm
        print("✅ 핵심 연결 즉시 초기화 완료")
    except Exception as e:
        print(f"⚠️ 핵심 연결 즉시 초기화 실패: {str(e)}")
    
    print("✅ Hotel Bot API 시작 완료")

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

@app.get("/ready")
async def ready_check():
    """Fast readiness check for frontend connections"""
    try:
        # 빠른 연결 상태 확인 (타임아웃 없이)
        from scripts.connection_manager import connection_manager
        is_ready = connection_manager._openai_llm is not None
        
        return {
            "status": "ready" if is_ready else "warming_up",
            "timestamp": datetime.now().isoformat(),
            "ready": is_ready
        }
    except Exception:
        return {
            "status": "warming_up",
            "timestamp": datetime.now().isoformat(),
            "ready": False
        }

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
        
        # 연결 상태 확인 (선택적)
        connection_status = "unknown"
        try:
            from scripts.connection_manager import connection_manager
            # 연결이 초기화되어 있는지 확인
            if connection_manager._openai_llm is not None:
                connection_status = "warmed_up"
            else:
                connection_status = "cold"
        except Exception:
            connection_status = "error"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "connection_status": connection_status,
            "config": {
                "google_sheet_id": settings.GOOGLE_SHEET_ID[:8] + "..." if settings.GOOGLE_SHEET_ID else None,
                "slack_bot_token_configured": bool(settings.SLACK_BOT_TOKEN),
                "slack_signing_secret_configured": bool(settings.SLACK_SIGNING_SECRET),
                "google_credentials_configured": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 