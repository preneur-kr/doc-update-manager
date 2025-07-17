from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import document, slack
from app.api.endpoints.chat import router as chat_router
from app.middleware.performance_middleware import (
    create_performance_middlewares,
    set_performance_tracker,
    get_performance_tracker,
    RequestTrackingMiddleware
)
from datetime import datetime
import asyncio
import threading
import os

# Hotel Bot API with Chat functionality
app = FastAPI(
    title="Hotel Bot API",
    description="Hotel Bot API with Slack integration",
    version="1.0.0"
)

# 🚀 성능 최적화 미들웨어 적용
is_production = os.getenv('ENVIRONMENT', 'development') == 'production'
performance_middlewares = create_performance_middlewares(
    enable_compression=True,
    enable_caching=True,
    enable_tracking=True,
    enable_rate_limiting=is_production,  # 프로덕션에서만 레이트 리미팅
    detailed_logging=not is_production  # 개발 환경에서만 상세 로깅
)

# 성능 미들웨어 추가
tracker_middleware = None
for middleware in performance_middlewares:
    middleware_instance = middleware(app)
    app.add_middleware(type(middleware_instance), **middleware_instance.__dict__)
    
    # 추적 미들웨어 저장
    if isinstance(middleware_instance, RequestTrackingMiddleware):
        tracker_middleware = middleware_instance
        set_performance_tracker(middleware_instance)

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

# 🚀 성능 모니터링 엔드포인트
@app.get("/metrics", tags=["monitoring"])
async def get_performance_metrics():
    """실시간 성능 메트릭 조회"""
    tracker = get_performance_tracker()
    if not tracker:
        return {"error": "Performance tracking not enabled"}
    
    performance_stats = tracker.get_performance_summary()
    
    # 캐시 통계 추가
    try:
        from scripts.distributed_cache import get_distributed_cache
        cache = await get_distributed_cache()
        cache_stats = await cache.get_cache_stats()
        performance_stats['cache_stats'] = cache_stats
    except Exception as e:
        performance_stats['cache_stats'] = {"error": str(e)}
    
    # 벡터 검색 통계 추가
    try:
        from scripts.optimized_vector_search import get_optimized_searcher
        searcher = get_optimized_searcher()
        search_stats = searcher.get_performance_stats()
        performance_stats['search_stats'] = search_stats
    except Exception as e:
        performance_stats['search_stats'] = {"error": str(e)}
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "performance": performance_stats
    }

@app.get("/health", tags=["monitoring"])
async def health_check():
    """🏥 고도화된 헬스 체크"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "environment": os.getenv('ENVIRONMENT', 'development')
    }
    
    # 연결 상태 확인
    try:
        from scripts.connection_manager import connection_manager
        connection_info = connection_manager.get_connection_info()
        health_status['connections'] = connection_info
    except Exception as e:
        health_status['connections'] = {"error": str(e)}
        health_status['status'] = "degraded"
    
    # 활성 요청 수
    tracker = get_performance_tracker()
    if tracker:
        health_status['active_requests'] = tracker.get_active_requests_count()
    
    return health_status

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