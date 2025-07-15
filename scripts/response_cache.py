"""
응답 캐싱 시스템 - 자주 묻는 질문에 대한 응답을 캐싱하여 성능을 개선합니다.
"""

import hashlib
import json
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

class ResponseCache:
    """응답 캐싱을 관리하는 클래스"""
    
    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        """
        초기화
        
        Args:
            max_size (int): 최대 캐시 크기
            ttl_hours (int): 캐시 유효 시간 (시간)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_hours * 3600
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
    
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
    
    def _is_expired(self, cache_key: str) -> bool:
        """
        캐시 항목이 만료되었는지 확인합니다.
        
        Args:
            cache_key (str): 캐시 키
            
        Returns:
            bool: 만료 여부
        """
        if cache_key not in self.cache:
            return True
        
        cached_time = self.cache[cache_key].get("timestamp", 0)
        return time.time() - cached_time > self.ttl_seconds
    
    def _cleanup_expired(self):
        """만료된 캐시 항목들을 정리합니다."""
        expired_keys = [key for key in self.cache.keys() if self._is_expired(key)]
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def _evict_lru(self):
        """LRU 정책에 따라 캐시 항목을 제거합니다."""
        if len(self.cache) <= self.max_size:
            return
        
        # 가장 오래된 접근 시간을 가진 항목 찾기
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
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
        cache_key = self._generate_cache_key(question, category, section)
        
        # 만료된 캐시 정리
        self._cleanup_expired()
        
        if cache_key in self.cache and not self._is_expired(cache_key):
            # 접근 시간 업데이트
            self.access_times[cache_key] = time.time()
            
            cached_data = self.cache[cache_key]
            print(f"🎯 캐시 히트: {question[:50]}...")
            return cached_data["answer"], cached_data["is_fallback"]
        
        return None
    
    def set(self, question: str, answer: str, is_fallback: bool, category: Optional[str] = None, section: Optional[str] = None):
        """
        응답을 캐시에 저장합니다.
        
        Args:
            question (str): 사용자 질문
            answer (str): 생성된 응답
            is_fallback (bool): fallback 여부
            category (Optional[str]): 카테고리 필터
            section (Optional[str]): 섹션 필터
        """
        cache_key = self._generate_cache_key(question, category, section)
        
        # 만료된 캐시 정리
        self._cleanup_expired()
        
        # LRU 정책에 따른 캐시 제거
        self._evict_lru()
        
        # 새 항목 추가
        self.cache[cache_key] = {
            "answer": answer,
            "is_fallback": is_fallback,
            "timestamp": time.time(),
            "question": question  # 디버깅용
        }
        self.access_times[cache_key] = time.time()
        
        print(f"💾 캐시 저장: {question[:50]}...")
    
    def clear(self):
        """모든 캐시를 삭제합니다."""
        self.cache.clear()
        self.access_times.clear()
        print("🧹 캐시 전체 삭제 완료")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계를 반환합니다."""
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "ttl_hours": self.ttl_seconds // 3600,
            "oldest_entry": min(self.access_times.values()) if self.access_times else None,
            "newest_entry": max(self.access_times.values()) if self.access_times else None
        }

# 전역 캐시 인스턴스
response_cache = ResponseCache(max_size=50, ttl_hours=12) 