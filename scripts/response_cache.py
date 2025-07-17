"""
응답 캐싱 시스템 - 자주 묻는 질문에 대한 응답을 캐싱하여 성능을 개선합니다.
"""

import hashlib
import json
import threading
import time
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime, timedelta
from collections import OrderedDict

class ThreadSafeResponseCache:
    """스레드 안전한 응답 캐싱을 관리하는 클래스"""
    
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        """
        초기화
        
        Args:
            max_size (int): 최대 캐시 크기
            ttl_hours (int): 캐시 유효 시간 (시간)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_hours * 3600
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.access_times: Dict[str, float] = {}
        self.lock = threading.RLock()  # 재귀적 잠금 허용
        
        # 통계 정보
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_removals': 0,
            'total_requests': 0
        }
    
    def _generate_cache_key(self, question: str, category: Optional[str] = None, section: Optional[str] = None) -> str:
        """
        질문과 필터를 기반으로 캐시 키를 생성합니다.
        
        Args:
            question (str): 사용자 질문
            category (Optional[str]): 카테고리 필터
            section (Optional[str]): 섹션 필터
            
        Returns:
            str: 캐시 키
        """
        # 질문을 정규화 (소문자, 공백 정리)
        normalized_question = question.lower().strip()
        
        # 캐시 키 생성을 위한 데이터
        cache_data = {
            "question": normalized_question,
            "category": category,
            "section": section
        }
        
        # JSON 문자열로 변환 후 해시 생성
        cache_string = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """
        캐시 항목이 만료되었는지 확인합니다.
        
        Args:
            cache_entry (Dict[str, Any]): 캐시 항목
            
        Returns:
            bool: 만료 여부
        """
        created_time = cache_entry.get('created_at', 0)
        return time.time() - created_time > self.ttl_seconds
    
    def _evict_expired(self) -> int:
        """
        만료된 캐시 항목들을 제거합니다.
        
        Returns:
            int: 제거된 항목 수
        """
        expired_keys = []
        current_time = time.time()
        
        for key, entry in self.cache.items():
            if current_time - entry.get('created_at', 0) > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)
        
        if expired_keys:
            self.stats['expired_removals'] += len(expired_keys)
            print(f"🗑️ 만료된 캐시 {len(expired_keys)}개 항목 제거")
        
        return len(expired_keys)
    
    def _evict_lru(self, count: int = 1) -> int:
        """
        LRU(Least Recently Used) 정책에 따라 캐시 항목을 제거합니다.
        
        Args:
            count (int): 제거할 항목 수
            
        Returns:
            int: 실제 제거된 항목 수
        """
        removed_count = 0
        
        # 접근 시간 기준으로 정렬하여 가장 오래된 항목부터 제거
        sorted_keys = sorted(
            self.access_times.items(),
            key=lambda x: x[1]
        )
        
        for key, _ in sorted_keys[:count]:
            if key in self.cache:
                self.cache.pop(key, None)
                self.access_times.pop(key, None)
                removed_count += 1
        
        if removed_count > 0:
            self.stats['evictions'] += removed_count
            print(f"📤 LRU 정책에 따라 캐시 {removed_count}개 항목 제거")
        
        return removed_count
    
    def get(self, question: str, category: Optional[str] = None, section: Optional[str] = None) -> Optional[Tuple[str, bool]]:
        """
        캐시에서 응답을 가져옵니다.
        
        Args:
            question (str): 사용자 질문
            category (Optional[str]): 카테고리 필터
            section (Optional[str]): 섹션 필터
            
        Returns:
            Optional[Tuple[str, bool]]: (응답, fallback 여부) 또는 None
        """
        with self.lock:
            self.stats['total_requests'] += 1
            
            cache_key = self._generate_cache_key(question, category, section)
            
            if cache_key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            cache_entry = self.cache[cache_key]
            
            # 만료 확인
            if self._is_expired(cache_entry):
                self.cache.pop(cache_key, None)
                self.access_times.pop(cache_key, None)
                self.stats['misses'] += 1
                self.stats['expired_removals'] += 1
                return None
            
            # 접근 시간 업데이트 (LRU를 위해)
            self.access_times[cache_key] = time.time()
            
            # 캐시 순서 업데이트 (OrderedDict의 move_to_end 사용)
            self.cache.move_to_end(cache_key)
            
            self.stats['hits'] += 1
            return (cache_entry['answer'], cache_entry['is_fallback'])
    
    def set(self, question: str, answer: str, is_fallback: bool, category: Optional[str] = None, section: Optional[str] = None) -> None:
        """
        응답을 캐시에 저장합니다.
        
        Args:
            question (str): 사용자 질문
            answer (str): 응답
            is_fallback (bool): fallback 응답 여부
            category (Optional[str]): 카테고리 필터
            section (Optional[str]): 섹션 필터
        """
        with self.lock:
            cache_key = self._generate_cache_key(question, category, section)
            current_time = time.time()
            
            # 만료된 항목들 먼저 정리
            self._evict_expired()
            
            # 캐시 크기 제한 확인
            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                # 새 항목을 위한 공간 확보
                self._evict_lru(1)
            
            # 캐시에 저장
            cache_entry = {
                'answer': answer,
                'is_fallback': is_fallback,
                'created_at': current_time,
                'question': question,
                'category': category,
                'section': section,
                'access_count': 1
            }
            
            if cache_key in self.cache:
                # 기존 항목 업데이트
                cache_entry['access_count'] = self.cache[cache_key].get('access_count', 0) + 1
            
            self.cache[cache_key] = cache_entry
            self.access_times[cache_key] = current_time
    
    def clear(self) -> None:
        """캐시를 모두 지웁니다."""
        with self.lock:
            cleared_count = len(self.cache)
            self.cache.clear()
            self.access_times.clear()
            print(f"🧹 캐시 전체 정리: {cleared_count}개 항목 제거")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보를 반환합니다."""
        with self.lock:
            hit_rate = (self.stats['hits'] / max(self.stats['total_requests'], 1)) * 100
            
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': round(hit_rate, 2),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'total_requests': self.stats['total_requests'],
                'evictions': self.stats['evictions'],
                'expired_removals': self.stats['expired_removals'],
                'ttl_hours': self.ttl_seconds / 3600,
                'memory_usage_estimate': len(self.cache) * 500  # 대략적인 메모리 사용량 (바이트)
            }
    
    def get_cache_items(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        캐시 항목들을 반환합니다 (디버깅용).
        
        Args:
            limit (int): 반환할 최대 항목 수
            
        Returns:
            List[Dict[str, Any]]: 캐시 항목 리스트
        """
        with self.lock:
            items = []
            for i, (key, entry) in enumerate(self.cache.items()):
                if i >= limit:
                    break
                
                items.append({
                    'key': key[:8] + '...',  # 키 일부만 표시
                    'question': entry.get('question', '')[:50] + '...' if len(entry.get('question', '')) > 50 else entry.get('question', ''),
                    'answer_preview': entry.get('answer', '')[:50] + '...' if len(entry.get('answer', '')) > 50 else entry.get('answer', ''),
                    'is_fallback': entry.get('is_fallback', False),
                    'created_at': datetime.fromtimestamp(entry.get('created_at', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'access_count': entry.get('access_count', 0),
                    'category': entry.get('category'),
                    'section': entry.get('section')
                })
            
            return items
    
    def cleanup(self) -> Dict[str, int]:
        """
        만료된 항목들을 정리하고 통계를 반환합니다.
        
        Returns:
            Dict[str, int]: 정리 결과 통계
        """
        with self.lock:
            initial_size = len(self.cache)
            expired_removed = self._evict_expired()
            
            # 캐시 크기가 최대 크기의 80%를 초과하면 추가 정리
            if len(self.cache) > self.max_size * 0.8:
                lru_removed = self._evict_lru(int(self.max_size * 0.2))
            else:
                lru_removed = 0
            
            final_size = len(self.cache)
            
            return {
                'initial_size': initial_size,
                'final_size': final_size,
                'expired_removed': expired_removed,
                'lru_removed': lru_removed,
                'total_removed': expired_removed + lru_removed
            }

# 글로벌 캐시 인스턴스
response_cache = ThreadSafeResponseCache(max_size=100, ttl_hours=24)

# 하위 호환성을 위한 별칭
ResponseCache = ThreadSafeResponseCache 