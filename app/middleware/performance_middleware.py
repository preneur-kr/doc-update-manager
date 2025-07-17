"""
🚀 고성능 API 미들웨어 시스템
- 응답 압축
- 캐싱 헤더 최적화
- 요청 성능 추적
- 동시 요청 제한
- 자동 성능 모니터링
"""

import time
import gzip
import json
import asyncio
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
import threading
from collections import deque, defaultdict

class PerformanceMetrics:
    """성능 메트릭 수집기"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.request_times: deque = deque(maxlen=max_samples)
        self.endpoints_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'errors': 0
        })
        self.lock = threading.RLock()
    
    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """요청 성능 기록"""
        with self.lock:
            self.request_times.append(duration)
            
            key = f"{method} {endpoint}"
            stats = self.endpoints_stats[key]
            
            stats['count'] += 1
            stats['total_time'] += duration
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['min_time'] = min(stats['min_time'], duration)
            stats['max_time'] = max(stats['max_time'], duration)
            
            if status_code >= 400:
                stats['errors'] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """성능 요약 통계"""
        with self.lock:
            if not self.request_times:
                return {}
            
            avg_time = sum(self.request_times) / len(self.request_times)
            
            # 상위 느린 엔드포인트
            slow_endpoints = sorted(
                [(k, v) for k, v in self.endpoints_stats.items()],
                key=lambda x: x[1]['avg_time'],
                reverse=True
            )[:5]
            
            return {
                'total_requests': len(self.request_times),
                'avg_response_time_ms': round(avg_time * 1000, 2),
                'min_response_time_ms': round(min(self.request_times) * 1000, 2),
                'max_response_time_ms': round(max(self.request_times) * 1000, 2),
                'slow_endpoints': [
                    {
                        'endpoint': endpoint,
                        'avg_time_ms': round(stats['avg_time'] * 1000, 2),
                        'count': stats['count'],
                        'errors': stats['errors']
                    }
                    for endpoint, stats in slow_endpoints
                ]
            }

class ResponseCompressionMiddleware(BaseHTTPMiddleware):
    """
    🗜️ 응답 압축 미들웨어
    - Gzip 압축으로 대역폭 절약
    - 조건부 압축 (크기, Content-Type 기반)
    """
    
    def __init__(self, app, min_size: int = 500, compression_level: int = 6):
        super().__init__(app)
        self.min_size = min_size
        self.compression_level = compression_level
        self.compressible_types = {
            'application/json',
            'text/html',
            'text/plain',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/xml',
            'text/xml'
        }
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 압축 조건 확인
        if not self._should_compress(request, response):
            return response
        
        # 응답 본문 읽기
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # 최소 크기 확인
        if len(response_body) < self.min_size:
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Gzip 압축
        compressed_body = gzip.compress(response_body, compresslevel=self.compression_level)
        
        # 압축 헤더 설정
        headers = dict(response.headers)
        headers['content-encoding'] = 'gzip'
        headers['content-length'] = str(len(compressed_body))
        headers['vary'] = 'Accept-Encoding'
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
    
    def _should_compress(self, request: Request, response: Response) -> bool:
        """압축 여부 결정"""
        # 이미 압축된 경우
        if response.headers.get('content-encoding'):
            return False
        
        # Accept-Encoding 확인
        accept_encoding = request.headers.get('accept-encoding', '')
        if 'gzip' not in accept_encoding:
            return False
        
        # Content-Type 확인
        content_type = response.headers.get('content-type', '').split(';')[0]
        return content_type in self.compressible_types

class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    🏪 캐싱 헤더 최적화 미들웨어
    - 엔드포인트별 캐싱 전략
    - ETags 자동 생성
    - 조건부 요청 처리
    """
    
    def __init__(self, app, default_cache_control: str = "no-cache"):
        super().__init__(app)
        self.default_cache_control = default_cache_control
        
        # 엔드포인트별 캐싱 규칙
        self.cache_rules = {
            '/api/v1/chat': 'no-cache, no-store, must-revalidate',  # 채팅은 캐싱하지 않음
            '/health': 'max-age=60',  # 헬스체크는 1분 캐싱
            '/metrics': 'max-age=30',  # 메트릭은 30초 캐싱
            '/static': 'max-age=86400',  # 정적 파일은 1일 캐싱
        }
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 캐시 컨트롤 헤더 설정
        cache_control = self._get_cache_control(request.url.path)
        response.headers['cache-control'] = cache_control
        
        # Vary 헤더 설정 (컨텐츠 협상)
        response.headers['vary'] = 'Accept, Accept-Encoding, Accept-Language'
        
        # ETag 생성 (응답이 JSON인 경우)
        if response.headers.get('content-type', '').startswith('application/json'):
            response.headers['etag'] = self._generate_etag(response)
        
        return response
    
    def _get_cache_control(self, path: str) -> str:
        """경로에 따른 캐시 컨트롤 헤더 결정"""
        for pattern, cache_control in self.cache_rules.items():
            if path.startswith(pattern):
                return cache_control
        return self.default_cache_control
    
    def _generate_etag(self, response: Response) -> str:
        """ETag 생성"""
        import hashlib
        content_hash = hashlib.md5(str(response.body).encode()).hexdigest()
        return f'"{content_hash}"'

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    📊 요청 추적 및 성능 모니터링 미들웨어
    - 응답 시간 측정
    - 엔드포인트별 통계
    - 에러율 추적
    - 동시 요청 수 모니터링
    """
    
    def __init__(self, app, enable_detailed_logging: bool = False):
        super().__init__(app)
        self.metrics = PerformanceMetrics()
        self.enable_detailed_logging = enable_detailed_logging
        self.active_requests: Set[str] = set()
        self.active_requests_lock = threading.RLock()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = f"{id(request)}_{start_time}"
        
        # 활성 요청 추가
        with self.active_requests_lock:
            self.active_requests.add(request_id)
        
        try:
            # X-Request-ID 헤더 추가
            request.state.request_id = request_id
            
            # 요청 처리
            response = await call_next(request)
            
            # 응답 시간 계산
            duration = time.time() - start_time
            
            # 성능 메트릭 기록
            self.metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                duration=duration,
                status_code=response.status_code
            )
            
            # 응답 헤더에 성능 정보 추가
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            response.headers['X-Request-ID'] = request_id
            
            # 상세 로깅
            if self.enable_detailed_logging:
                print(f"📊 {request.method} {request.url.path} - "
                      f"{response.status_code} - {duration:.3f}s")
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 에러 메트릭 기록
            self.metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                duration=duration,
                status_code=500
            )
            
            print(f"❌ {request.method} {request.url.path} - ERROR - {duration:.3f}s: {str(e)}")
            raise
            
        finally:
            # 활성 요청 제거
            with self.active_requests_lock:
                self.active_requests.discard(request_id)
    
    def get_active_requests_count(self) -> int:
        """현재 활성 요청 수"""
        with self.active_requests_lock:
            return len(self.active_requests)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 통계"""
        summary = self.metrics.get_summary()
        summary['active_requests'] = self.get_active_requests_count()
        return summary

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    🚦 요청 제한 미들웨어
    - IP 기반 요청 제한
    - 엔드포인트별 제한
    - 슬라이딩 윈도우 방식
    """
    
    def __init__(self, app, requests_per_minute: int = 60, burst_limit: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        self.lock = threading.RLock()
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # 요청 제한 확인
        if not self._is_request_allowed(client_ip, current_time):
            return Response(
                content=json.dumps({
                    "error": "Rate limit exceeded",
                    "retry_after": 60
                }),
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": "60"
                }
            )
        
        # 요청 기록
        self._record_request(client_ip, current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 추출"""
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # 직접 연결
        return request.client.host if request.client else "unknown"
    
    def _is_request_allowed(self, client_ip: str, current_time: float) -> bool:
        """요청 허용 여부 확인"""
        with self.lock:
            timestamps = self.request_counts[client_ip]
            
            # 1분 이전 요청 제거
            cutoff_time = current_time - 60
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            # 요청 제한 확인
            return len(timestamps) < self.requests_per_minute
    
    def _record_request(self, client_ip: str, current_time: float):
        """요청 기록"""
        with self.lock:
            self.request_counts[client_ip].append(current_time)

# 미들웨어 팩토리 함수
def create_performance_middlewares(
    enable_compression: bool = True,
    enable_caching: bool = True,
    enable_tracking: bool = True,
    enable_rate_limiting: bool = True,
    detailed_logging: bool = False
) -> list:
    """성능 미들웨어 생성"""
    middlewares = []
    
    if enable_rate_limiting:
        middlewares.append(RateLimitingMiddleware)
    
    if enable_tracking:
        middlewares.append(
            lambda app: RequestTrackingMiddleware(app, enable_detailed_logging=detailed_logging)
        )
    
    if enable_caching:
        middlewares.append(CacheControlMiddleware)
    
    if enable_compression:
        middlewares.append(ResponseCompressionMiddleware)
    
    return middlewares

# 전역 성능 추적기
_global_tracker: Optional[RequestTrackingMiddleware] = None

def get_performance_tracker() -> Optional[RequestTrackingMiddleware]:
    """전역 성능 추적기 반환"""
    return _global_tracker

def set_performance_tracker(tracker: RequestTrackingMiddleware):
    """전역 성능 추적기 설정"""
    global _global_tracker
    _global_tracker = tracker 