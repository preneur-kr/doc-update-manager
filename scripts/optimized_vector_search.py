"""
🚀 고성능 벡터 검색 최적화 시스템 - 인덱싱, 배치 처리, 병렬 검색
"""

import asyncio
import time
import threading
from typing import List, Dict, Any, Optional, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta
import json

# Pinecone 및 OpenAI 연결
from scripts.connection_manager import connection_manager
from scripts.filtered_vector_search import FilteredVectorSearch

@dataclass
class SearchMetrics:
    """검색 성능 메트릭"""
    total_searches: int = 0
    avg_search_time: float = 0.0
    cache_hits: int = 0
    vector_hits: int = 0
    errors: int = 0
    last_optimization: Optional[datetime] = None

class OptimizedVectorSearchManager:
    """
    🚀 고성능 벡터 검색 관리자
    
    주요 최적화:
    - 배치 검색
    - 결과 캐싱
    - 병렬 처리
    - 인덱스 최적화
    - 지능형 필터링
    """
    
    def __init__(self, 
                 batch_size: int = 10,
                 max_workers: int = 4,
                 cache_ttl_minutes: int = 30):
        
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        
        # 기본 검색기
        self.base_searcher: Optional[FilteredVectorSearch] = None
        
        # 검색 결과 캐시 (메모리 기반)
        self.search_cache: Dict[str, Tuple[List[Tuple[dict, float]], datetime]] = {}
        self.cache_lock = threading.RLock()
        
        # 성능 메트릭
        self.metrics = SearchMetrics()
        
        # 스레드 풀
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 자주 검색되는 패턴 추적
        self.query_patterns: Dict[str, int] = {}
        self.pattern_lock = threading.RLock()
        
        # 최적화 설정
        self.enable_parallel_search = True
        self.enable_smart_filtering = True
        self.enable_result_prefetching = True
    
    def initialize(self):
        """검색 시스템 초기화"""
        try:
            self.base_searcher = connection_manager.vector_searcher
            print("✅ 최적화된 벡터 검색 시스템 초기화 완료")
            return True
        except Exception as e:
            print(f"❌ 벡터 검색 시스템 초기화 실패: {str(e)}")
            return False
    
    def _generate_search_cache_key(self, query: str, category: Optional[str], 
                                  section: Optional[str], k: int, 
                                  score_threshold: float) -> str:
        """검색 캐시 키 생성"""
        key_data = {
            'query': query.lower().strip(),
            'category': category,
            'section': section,
            'k': k,
            'threshold': score_threshold
        }
        return json.dumps(key_data, sort_keys=True)
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """캐시가 유효한지 확인"""
        return datetime.now() - timestamp < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Tuple[dict, float]]]:
        """캐시에서 검색 결과 조회"""
        with self.cache_lock:
            if cache_key in self.search_cache:
                results, timestamp = self.search_cache[cache_key]
                if self._is_cache_valid(timestamp):
                    self.metrics.cache_hits += 1
                    return results
                else:
                    # 만료된 캐시 제거
                    del self.search_cache[cache_key]
        return None
    
    def _store_in_cache(self, cache_key: str, results: List[Tuple[dict, float]]):
        """검색 결과를 캐시에 저장"""
        with self.cache_lock:
            self.search_cache[cache_key] = (results, datetime.now())
            
            # 캐시 크기 제한 (최대 1000개)
            if len(self.search_cache) > 1000:
                # 가장 오래된 항목 제거
                oldest_key = min(self.search_cache.keys(), 
                               key=lambda k: self.search_cache[k][1])
                del self.search_cache[oldest_key]
    
    def _track_query_pattern(self, query: str):
        """자주 검색되는 패턴 추적"""
        with self.pattern_lock:
            # 쿼리를 단순화하여 패턴 추출
            pattern = " ".join(sorted(query.lower().split()))
            self.query_patterns[pattern] = self.query_patterns.get(pattern, 0) + 1
    
    def _apply_smart_filtering(self, query: str, category: Optional[str], 
                             section: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """지능형 필터링 - 쿼리 내용을 분석하여 최적 필터 추천"""
        if not self.enable_smart_filtering:
            return category, section
        
        query_lower = query.lower()
        
        # 카테고리 자동 추론
        if not category:
            if any(word in query_lower for word in ['체크인', '입실', '도착']):
                category = 'checkin'
            elif any(word in query_lower for word in ['체크아웃', '퇴실', '출발']):
                category = 'checkout'
            elif any(word in query_lower for word in ['식당', '레스토랑', '뷔페', '조식']):
                category = 'dining'
            elif any(word in query_lower for word in ['수영장', '헬스장', '스파', '시설']):
                category = 'facilities'
        
        return category, section
    
    async def similarity_search_async(self, 
                                    query: str,
                                    k: int = 3,
                                    category: Optional[str] = None,
                                    section: Optional[str] = None,
                                    score_threshold: float = 0.7) -> List[Tuple[dict, float]]:
        """
        🚀 비동기 최적화된 유사도 검색
        
        Returns:
            List[Tuple[dict, float]]: (메타데이터, 점수) 리스트
        """
        start_time = time.time()
        self.metrics.total_searches += 1
        
        try:
            # 검색 패턴 추적
            self._track_query_pattern(query)
            
            # 지능형 필터링 적용
            category, section = self._apply_smart_filtering(query, category, section)
            
            # 캐시 확인
            cache_key = self._generate_search_cache_key(query, category, section, k, score_threshold)
            cached_results = self._get_from_cache(cache_key)
            if cached_results:
                return cached_results
            
            # 벡터 검색 수행
            if not self.base_searcher:
                self.initialize()
            
            if self.base_searcher:
                results = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self.base_searcher.similarity_search_with_metadata,
                    query, k, category, section, score_threshold
                )
                
                # 결과 캐싱
                self._store_in_cache(cache_key, results)
                self.metrics.vector_hits += 1
                
                return results
            else:
                self.metrics.errors += 1
                return []
                
        except Exception as e:
            print(f"❌ 벡터 검색 오류: {str(e)}")
            self.metrics.errors += 1
            return []
        
        finally:
            # 성능 메트릭 업데이트
            search_time = time.time() - start_time
            self._update_avg_search_time(search_time)
    
    async def batch_search(self, 
                          queries: List[str],
                          k: int = 3,
                          category: Optional[str] = None,
                          section: Optional[str] = None,
                          score_threshold: float = 0.7) -> List[List[Tuple[dict, float]]]:
        """
        🚀 배치 검색 - 여러 쿼리를 병렬로 처리
        
        Args:
            queries: 검색할 쿼리 리스트
            
        Returns:
            List[List[Tuple[dict, float]]]: 각 쿼리별 검색 결과
        """
        if not self.enable_parallel_search or len(queries) == 1:
            # 순차 처리
            results = []
            for query in queries:
                result = await self.similarity_search_async(
                    query, k, category, section, score_threshold
                )
                results.append(result)
            return results
        
        # 병렬 처리
        tasks = [
            self.similarity_search_async(query, k, category, section, score_threshold)
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"⚠️ 배치 검색 중 오류: {str(result)}")
                processed_results.append([])
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def smart_search_with_expansion(self, 
                                        query: str,
                                        k: int = 3,
                                        category: Optional[str] = None,
                                        section: Optional[str] = None,
                                        score_threshold: float = 0.7,
                                        expand_queries: bool = True) -> List[Tuple[dict, float]]:
        """
        🧠 지능형 검색 - 쿼리 확장 및 다양한 검색 전략 적용
        
        Args:
            expand_queries: 쿼리 확장 여부
            
        Returns:
            List[Tuple[dict, float]]: 최적화된 검색 결과
        """
        queries_to_search = [query]
        
        if expand_queries:
            # 쿼리 확장 (동의어, 유사 표현 추가)
            expanded_queries = self._expand_query(query)
            queries_to_search.extend(expanded_queries)
        
        # 배치 검색 수행
        all_results = await self.batch_search(
            queries_to_search, k, category, section, score_threshold
        )
        
        # 결과 통합 및 중복 제거
        combined_results = self._merge_and_deduplicate_results(all_results)
        
        # 상위 k개 결과만 반환
        return combined_results[:k]
    
    def _expand_query(self, query: str) -> List[str]:
        """쿼리 확장 - 동의어 및 유사 표현 생성"""
        expanded = []
        query_lower = query.lower()
        
        # 호텔 관련 동의어 매핑
        synonyms_map = {
            '체크인': ['입실', '도착', '입실시간'],
            '체크아웃': ['퇴실', '출발', '퇴실시간'],
            '조식': ['아침식사', '브랙퍼스트', '모닝부페'],
            '수영장': ['풀', '수영시설'],
            '주차': ['주차장', '파킹'],
            '와이파이': ['wifi', '인터넷', '무선인터넷'],
        }
        
        for original, synonyms in synonyms_map.items():
            if original in query_lower:
                for synonym in synonyms:
                    expanded_query = query_lower.replace(original, synonym)
                    if expanded_query != query_lower:
                        expanded.append(expanded_query)
        
        return expanded[:2]  # 최대 2개 확장 쿼리
    
    def _merge_and_deduplicate_results(self, 
                                     all_results: List[List[Tuple[dict, float]]]) -> List[Tuple[dict, float]]:
        """여러 검색 결과를 통합하고 중복 제거"""
        seen_texts: Set[str] = set()
        merged_results = []
        
        # 모든 결과를 점수 순으로 정렬
        all_items = []
        for results in all_results:
            all_items.extend(results)
        
        all_items.sort(key=lambda x: x[1], reverse=True)
        
        for metadata, score in all_items:
            text = metadata.get('text', '')
            if text and text not in seen_texts:
                seen_texts.add(text)
                merged_results.append((metadata, score))
        
        return merged_results
    
    def _update_avg_search_time(self, search_time: float):
        """평균 검색 시간 업데이트"""
        total = self.metrics.total_searches
        current_avg = self.metrics.avg_search_time
        
        if total == 1:
            self.metrics.avg_search_time = search_time
        else:
            # 지수 이동 평균
            alpha = 2.0 / (total + 1)
            self.metrics.avg_search_time = alpha * search_time + (1 - alpha) * current_avg
    
    async def optimize_cache(self):
        """캐시 최적화 - 만료된 항목 정리 및 성능 조정"""
        with self.cache_lock:
            # 만료된 캐시 항목 제거
            current_time = datetime.now()
            expired_keys = [
                key for key, (_, timestamp) in self.search_cache.items()
                if current_time - timestamp >= self.cache_ttl
            ]
            
            for key in expired_keys:
                del self.search_cache[key]
            
            print(f"🧹 캐시 정리 완료: {len(expired_keys)}개 만료 항목 제거")
        
        self.metrics.last_optimization = datetime.now()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        cache_hit_rate = (
            self.metrics.cache_hits / max(self.metrics.total_searches, 1) * 100
        )
        
        top_patterns = sorted(
            self.query_patterns.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return {
            'total_searches': self.metrics.total_searches,
            'avg_search_time_ms': round(self.metrics.avg_search_time * 1000, 2),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cache_size': len(self.search_cache),
            'vector_hits': self.metrics.vector_hits,
            'errors': self.metrics.errors,
            'top_query_patterns': top_patterns,
            'last_optimization': self.metrics.last_optimization.isoformat() if self.metrics.last_optimization else None,
            'configuration': {
                'batch_size': self.batch_size,
                'max_workers': self.max_workers,
                'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60,
                'parallel_search_enabled': self.enable_parallel_search,
                'smart_filtering_enabled': self.enable_smart_filtering
            }
        }
    
    async def close(self):
        """리소스 정리"""
        if self.executor:
            self.executor.shutdown(wait=True)

# 전역 최적화된 검색 인스턴스
_optimized_searcher: Optional[OptimizedVectorSearchManager] = None
_searcher_lock = threading.Lock()

def get_optimized_searcher() -> OptimizedVectorSearchManager:
    """전역 최적화된 검색 인스턴스 반환"""
    global _optimized_searcher
    
    if _optimized_searcher is None:
        with _searcher_lock:
            if _optimized_searcher is None:
                _optimized_searcher = OptimizedVectorSearchManager()
                _optimized_searcher.initialize()
    
    return _optimized_searcher

# 편의 함수들
async def optimized_search(query: str, 
                         k: int = 3,
                         category: Optional[str] = None,
                         section: Optional[str] = None,
                         score_threshold: float = 0.7) -> List[Tuple[dict, float]]:
    """최적화된 검색 편의 함수"""
    searcher = get_optimized_searcher()
    return await searcher.similarity_search_async(query, k, category, section, score_threshold)

async def smart_search(query: str, 
                      k: int = 3,
                      category: Optional[str] = None,
                      section: Optional[str] = None,
                      score_threshold: float = 0.7) -> List[Tuple[dict, float]]:
    """지능형 검색 편의 함수"""
    searcher = get_optimized_searcher()
    return await searcher.smart_search_with_expansion(query, k, category, section, score_threshold) 