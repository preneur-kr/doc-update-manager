"""
🚀 고성능 분산 캐시 시스템 - Redis 기반 캐싱으로 성능 극대화
"""

import json
import hashlib
import threading
import time
from typing import Optional, Dict, Any, Tuple, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import os
from contextlib import asynccontextmanager

# Redis 연결을 위한 import (선택적)
try:
    import redis.asyncio as redis
    import redis.exceptions as redis_exceptions
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    redis_exceptions = None
    REDIS_AVAILABLE = False

from scripts.response_cache import ThreadSafeResponseCache

@dataclass
class CacheConfig:
    """캐시 설정 클래스"""
    # Redis 설정
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0
    redis_timeout: int = 5
    
    # 캐시 계층 설정
    l1_max_size: int = 100  # 로컬 캐시 크기
    l1_ttl_hours: int = 1   # 로컬 캐시 TTL
    l2_ttl_hours: int = 24  # Redis 캐시 TTL
    
    # 성능 설정
    compression_enabled: bool = True
    batch_size: int = 50
    connection_pool_size: int = 10

class DistributedCacheManager:
    """
    🚀 2단계 분산 캐시 시스템
    
    L1: 로컬 메모리 캐시 (ThreadSafeResponseCache)
    L2: Redis 분산 캐시
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        
        # L1 캐시 (로컬 메모리)
        self.l1_cache = ThreadSafeResponseCache(
            max_size=self.config.l1_max_size,
            ttl_hours=self.config.l1_ttl_hours
        )
        
        # L2 캐시 (Redis) - 비동기 연결
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        self._redis_lock = threading.RLock()
        self._initialized = False
        
        # 성능 통계
        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'errors': 0,
            'total_requests': 0,
            'avg_response_time': 0.0
        }
        
        # Redis 연결 상태
        self.redis_healthy = False
        self.last_health_check = 0
        self.health_check_interval = 30  # 30초마다 헬스 체크
    
    async def initialize(self) -> bool:
        """
        Redis 연결을 초기화합니다.
        
        Returns:
            bool: 초기화 성공 여부
        """
        if not REDIS_AVAILABLE:
            print("⚠️ Redis가 설치되지 않음. 로컬 캐시만 사용합니다.")
            self._initialized = True
            return True
        
        try:
            # Redis 연결 풀 생성
            self.redis_pool = redis.ConnectionPool.from_url(
                self.config.redis_url,
                password=self.config.redis_password,
                db=self.config.redis_db,
                max_connections=self.config.connection_pool_size,
                socket_connect_timeout=self.config.redis_timeout,
                socket_timeout=self.config.redis_timeout,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # 연결 테스트
            await self.redis_client.ping()
            self.redis_healthy = True
            print("✅ Redis 연결 성공")
            
        except Exception as e:
            print(f"❌ Redis 연결 실패: {str(e)}")
            print("⚠️ 로컬 캐시만 사용합니다.")
            self.redis_healthy = False
        
        self._initialized = True
        return True
    
    async def _check_redis_health(self) -> bool:
        """Redis 연결 상태를 확인합니다."""
        current_time = time.time()
        
        # 일정 간격으로만 헬스 체크 수행
        if current_time - self.last_health_check < self.health_check_interval:
            return self.redis_healthy
        
        self.last_health_check = current_time
        
        if not self.redis_client:
            self.redis_healthy = False
            return False
        
        try:
            await asyncio.wait_for(self.redis_client.ping(), timeout=2.0)
            if not self.redis_healthy:
                print("✅ Redis 연결 복구됨")
            self.redis_healthy = True
        except Exception as e:
            if self.redis_healthy:
                print(f"❌ Redis 연결 끊어짐: {str(e)}")
            self.redis_healthy = False
        
        return self.redis_healthy
    
    def _generate_cache_key(self, question: str, category: Optional[str] = None, 
                          section: Optional[str] = None) -> str:
        """캐시 키 생성"""
        key_data = {
            'question': question.lower().strip(),
            'category': category,
            'section': section
        }
        key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        return f"chat_cache:{hashlib.sha256(key_string.encode()).hexdigest()[:16]}"
    
    def _compress_data(self, data: str) -> bytes:
        """데이터 압축 (선택적)"""
        if not self.config.compression_enabled:
            return data.encode('utf-8')
        
        try:
            import zlib
            return zlib.compress(data.encode('utf-8'))
        except ImportError:
            return data.encode('utf-8')
    
    def _decompress_data(self, data: bytes) -> str:
        """데이터 압축 해제"""
        if not self.config.compression_enabled:
            return data.decode('utf-8')
        
        try:
            import zlib
            return zlib.decompress(data).decode('utf-8')
        except:
            # 압축되지 않은 데이터로 간주
            return data.decode('utf-8')
    
    async def get(self, question: str, category: Optional[str] = None, 
                  section: Optional[str] = None) -> Optional[Tuple[str, bool]]:
        """
        캐시에서 응답을 조회합니다.
        
        Returns:
            Optional[Tuple[str, bool]]: (응답, is_fallback) 또는 None
        """
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            # L1 캐시 확인 (로컬 메모리)
            l1_result = self.l1_cache.get(question, category, section)
            if l1_result:
                self.stats['l1_hits'] += 1
                return l1_result
            
            # L2 캐시 확인 (Redis)
            if await self._check_redis_health():
                cache_key = self._generate_cache_key(question, category, section)
                
                try:
                    redis_data = await asyncio.wait_for(
                        self.redis_client.get(cache_key),
                        timeout=2.0
                    )
                    
                    if redis_data:
                        # Redis에서 찾은 데이터를 L1에도 저장
                        decompressed = self._decompress_data(redis_data)
                        cached_data = json.loads(decompressed)
                        
                        answer = cached_data['answer']
                        is_fallback = cached_data['is_fallback']
                        
                        # L1 캐시에 추가 (빠른 접근을 위해)
                        self.l1_cache.set(question, answer, is_fallback, category, section)
                        
                        self.stats['l2_hits'] += 1
                        return (answer, is_fallback)
                
                except asyncio.TimeoutError:
                    print("⚠️ Redis 조회 타임아웃")
                    self.stats['errors'] += 1
                except Exception as e:
                    print(f"⚠️ Redis 조회 오류: {str(e)}")
                    self.stats['errors'] += 1
            
            # 캐시 미스
            self.stats['misses'] += 1
            return None
            
        finally:
            # 응답 시간 통계 업데이트
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)
    
    async def set(self, question: str, answer: str, is_fallback: bool,
                  category: Optional[str] = None, section: Optional[str] = None) -> bool:
        """
        캐시에 응답을 저장합니다.
        
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # L1 캐시에 저장
            self.l1_cache.set(question, answer, is_fallback, category, section)
            
            # L2 캐시에 저장 (Redis)
            if await self._check_redis_health():
                cache_key = self._generate_cache_key(question, category, section)
                cache_data = {
                    'answer': answer,
                    'is_fallback': is_fallback,
                    'timestamp': datetime.now().isoformat(),
                    'category': category,
                    'section': section
                }
                
                try:
                    compressed_data = self._compress_data(json.dumps(cache_data))
                    ttl_seconds = self.config.l2_ttl_hours * 3600
                    
                    await asyncio.wait_for(
                        self.redis_client.setex(cache_key, ttl_seconds, compressed_data),
                        timeout=2.0
                    )
                    return True
                    
                except asyncio.TimeoutError:
                    print("⚠️ Redis 저장 타임아웃")
                    self.stats['errors'] += 1
                except Exception as e:
                    print(f"⚠️ Redis 저장 오류: {str(e)}")
                    self.stats['errors'] += 1
            
            return True  # L1 저장은 성공
            
        except Exception as e:
            print(f"❌ 캐시 저장 실패: {str(e)}")
            return False
    
    async def clear_by_pattern(self, pattern: str) -> int:
        """패턴에 맞는 캐시 키들을 삭제합니다."""
        if not await self._check_redis_health():
            return 0
        
        try:
            keys = await self.redis_client.keys(f"chat_cache:*{pattern}*")
            if keys:
                deleted = await self.redis_client.delete(*keys)
                print(f"🗑️ Redis에서 {deleted}개 키 삭제 (패턴: {pattern})")
                return deleted
        except Exception as e:
            print(f"⚠️ Redis 패턴 삭제 오류: {str(e)}")
        
        return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보를 반환합니다."""
        l1_stats = self.l1_cache.get_stats()
        
        redis_info = {}
        if await self._check_redis_health():
            try:
                redis_info = await self.redis_client.info('memory')
                redis_keys = await self.redis_client.dbsize()
                redis_info['total_keys'] = redis_keys
            except Exception as e:
                redis_info = {'error': str(e)}
        
        return {
            'l1_cache': l1_stats,
            'l2_cache': {
                'healthy': self.redis_healthy,
                'info': redis_info
            },
            'combined_stats': self.stats,
            'config': {
                'l1_max_size': self.config.l1_max_size,
                'l2_ttl_hours': self.config.l2_ttl_hours,
                'compression_enabled': self.config.compression_enabled
            }
        }
    
    def _update_avg_response_time(self, response_time: float):
        """평균 응답 시간 업데이트"""
        current_avg = self.stats['avg_response_time']
        total_requests = self.stats['total_requests']
        
        # 이동 평균 계산
        if total_requests == 1:
            self.stats['avg_response_time'] = response_time
        else:
            alpha = 2.0 / (total_requests + 1)  # 지수 이동 평균
            self.stats['avg_response_time'] = alpha * response_time + (1 - alpha) * current_avg
    
    async def close(self):
        """연결을 정리합니다."""
        if self.redis_client:
            try:
                await self.redis_client.close()
            except:
                pass
        
        if self.redis_pool:
            try:
                await self.redis_pool.disconnect()
            except:
                pass

# 전역 분산 캐시 인스턴스
_distributed_cache: Optional[DistributedCacheManager] = None
_cache_lock = threading.Lock()

async def get_distributed_cache() -> DistributedCacheManager:
    """전역 분산 캐시 인스턴스를 반환합니다."""
    global _distributed_cache
    
    if _distributed_cache is None:
        with _cache_lock:
            if _distributed_cache is None:
                config = CacheConfig(
                    redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
                    redis_password=os.getenv('REDIS_PASSWORD'),
                    redis_db=int(os.getenv('REDIS_DB', '0')),
                    l1_max_size=int(os.getenv('CACHE_L1_SIZE', '100')),
                    l2_ttl_hours=int(os.getenv('CACHE_L2_TTL_HOURS', '24'))
                )
                
                _distributed_cache = DistributedCacheManager(config)
                await _distributed_cache.initialize()
    
    return _distributed_cache

# 편의 함수들
async def get_cached_response(question: str, category: Optional[str] = None, 
                            section: Optional[str] = None) -> Optional[Tuple[str, bool]]:
    """캐시된 응답을 조회하는 편의 함수"""
    cache = await get_distributed_cache()
    return await cache.get(question, category, section)

async def cache_response(question: str, answer: str, is_fallback: bool,
                        category: Optional[str] = None, section: Optional[str] = None) -> bool:
    """응답을 캐시에 저장하는 편의 함수"""
    cache = await get_distributed_cache()
    return await cache.set(question, answer, is_fallback, category, section)

async def invalidate_cache_pattern(pattern: str) -> int:
    """패턴에 맞는 캐시를 무효화하는 편의 함수"""
    cache = await get_distributed_cache()
    return await cache.clear_by_pattern(pattern)

# 컨텍스트 매니저
@asynccontextmanager
async def distributed_cache_context():
    """분산 캐시 컨텍스트 매니저"""
    cache = await get_distributed_cache()
    try:
        yield cache
    finally:
        await cache.close() 