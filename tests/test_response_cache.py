import pytest
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import patch

# 테스트용 시스템 경로 설정
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.response_cache import ThreadSafeResponseCache


class TestResponseCache:
    """ThreadSafeResponseCache 클래스 테스트"""

    @pytest.fixture
    def cache(self):
        """테스트용 캐시 인스턴스"""
        return ThreadSafeResponseCache(max_size=5, ttl_hours=1)

    @pytest.fixture
    def small_cache(self):
        """작은 크기 캐시 (LRU 테스트용)"""
        return ThreadSafeResponseCache(max_size=2, ttl_hours=1)

    def test_basic_set_get(self, cache):
        """기본적인 저장 및 조회 테스트"""
        cache.set("테스트 질문", "테스트 답변", False)
        
        result = cache.get("테스트 질문")
        assert result is not None
        assert result[0] == "테스트 답변"
        assert result[1] is False

    def test_cache_miss(self, cache):
        """캐시 미스 테스트"""
        result = cache.get("존재하지 않는 질문")
        assert result is None

    def test_category_and_section_filtering(self, cache):
        """카테고리와 섹션 필터링 테스트"""
        # 같은 질문, 다른 카테고리/섹션
        cache.set("질문", "답변1", False, "카테고리1", "섹션1")
        cache.set("질문", "답변2", False, "카테고리2", "섹션2")
        cache.set("질문", "답변3", False, None, None)
        
        # 각각 다른 결과 반환
        result1 = cache.get("질문", "카테고리1", "섹션1")
        result2 = cache.get("질문", "카테고리2", "섹션2")
        result3 = cache.get("질문", None, None)
        
        assert result1[0] == "답변1"
        assert result2[0] == "답변2"
        assert result3[0] == "답변3"

    def test_case_insensitive_question(self, cache):
        """대소문자 구분 없는 질문 처리"""
        cache.set("Test Question", "답변", False)
        
        result1 = cache.get("test question")
        result2 = cache.get("TEST QUESTION")
        result3 = cache.get("Test Question")
        
        assert all(result is not None for result in [result1, result2, result3])
        assert all(result[0] == "답변" for result in [result1, result2, result3])

    def test_whitespace_normalization(self, cache):
        """공백 정규화 테스트"""
        cache.set("  질문  ", "답변", False)
        
        result = cache.get("질문")
        assert result is not None
        assert result[0] == "답변"

    def test_ttl_expiration(self):
        """TTL 만료 테스트"""
        # 매우 짧은 TTL 설정 (0.1초)
        cache = ThreadSafeResponseCache(max_size=5, ttl_hours=0.1/3600)
        
        cache.set("질문", "답변", False)
        
        # 즉시 조회 시 존재
        result = cache.get("질문")
        assert result is not None
        
        # TTL 만료 후 조회 시 None
        time.sleep(0.15)
        result = cache.get("질문")
        assert result is None

    def test_lru_eviction(self, small_cache):
        """LRU 제거 정책 테스트"""
        # 캐시 크기(2)를 초과하여 저장
        small_cache.set("질문1", "답변1", False)
        small_cache.set("질문2", "답변2", False)
        small_cache.set("질문3", "답변3", False)  # 질문1이 제거되어야 함
        
        result1 = small_cache.get("질문1")  # None이어야 함
        result2 = small_cache.get("질문2")  # 존재해야 함
        result3 = small_cache.get("질문3")  # 존재해야 함
        
        assert result1 is None
        assert result2 is not None
        assert result3 is not None

    def test_access_order_lru(self, small_cache):
        """접근 순서 기반 LRU 테스트"""
        small_cache.set("질문1", "답변1", False)
        small_cache.set("질문2", "답변2", False)
        
        # 질문1 접근으로 최근 사용됨 표시
        small_cache.get("질문1")
        
        # 새 항목 추가 (질문2가 제거되어야 함)
        small_cache.set("질문3", "답변3", False)
        
        result1 = small_cache.get("질문1")  # 존재해야 함
        result2 = small_cache.get("질문2")  # None이어야 함
        result3 = small_cache.get("질문3")  # 존재해야 함
        
        assert result1 is not None
        assert result2 is None
        assert result3 is not None

    def test_update_existing_entry(self, cache):
        """기존 항목 업데이트 테스트"""
        cache.set("질문", "답변1", False)
        cache.set("질문", "답변2", True)  # 같은 키로 업데이트
        
        result = cache.get("질문")
        assert result is not None
        assert result[0] == "답변2"
        assert result[1] is True

    def test_access_count_tracking(self, cache):
        """접근 횟수 추적 테스트"""
        cache.set("질문", "답변", False)
        
        # 여러 번 접근
        cache.get("질문")
        cache.get("질문")
        cache.get("질문")
        
        # 캐시 항목 직접 확인 (내부 구조 테스트)
        cache_key = cache._generate_cache_key("질문")
        entry = cache.cache[cache_key]
        assert entry['access_count'] >= 3

    def test_statistics(self, cache):
        """통계 정보 테스트"""
        # 초기 상태
        stats = cache.get_stats()
        assert stats['cache_size'] == 0
        assert stats['hit_rate'] == 0.0
        assert stats['hits'] == 0
        assert stats['misses'] == 0
        
        # 데이터 추가 및 접근
        cache.set("질문1", "답변1", False)
        cache.set("질문2", "답변2", False)
        
        cache.get("질문1")  # hit
        cache.get("질문1")  # hit
        cache.get("존재하지않는질문")  # miss
        
        stats = cache.get_stats()
        assert stats['cache_size'] == 2
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 66.67  # 2/3 * 100

    def test_thread_safety(self, cache):
        """스레드 안전성 테스트"""
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(100):
                    question = f"질문{thread_id}_{i}"
                    answer = f"답변{thread_id}_{i}"
                    
                    cache.set(question, answer, False)
                    result = cache.get(question)
                    
                    if result:
                        results.append(result)
                    else:
                        errors.append(f"Missing: {question}")
            except Exception as e:
                errors.append(str(e))
        
        # 10개 스레드 동시 실행
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 오류가 없어야 함
        assert len(errors) == 0
        # 결과가 있어야 함 (정확한 개수는 LRU로 인해 다를 수 있음)
        assert len(results) > 0

    def test_concurrent_lru_eviction(self, small_cache):
        """동시 LRU 제거 테스트"""
        def worker(thread_id):
            for i in range(10):
                question = f"질문{thread_id}_{i}"
                small_cache.set(question, f"답변{thread_id}_{i}", False)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 캐시 크기가 최대 크기를 초과하지 않아야 함
        stats = small_cache.get_stats()
        assert stats['cache_size'] <= small_cache.max_size

    def test_cache_items_retrieval(self, cache):
        """캐시 항목 조회 테스트 (디버깅용)"""
        cache.set("질문1", "답변1", False, "카테고리1", "섹션1")
        cache.set("질문2", "답변2", True, "카테고리2", "섹션2")
        
        items = cache.get_cache_items(limit=10)
        
        assert len(items) == 2
        assert all('question' in item for item in items)
        assert all('answer_preview' in item for item in items)
        assert all('is_fallback' in item for item in items)
        assert all('created_at' in item for item in items)

    def test_cleanup_functionality(self, cache):
        """정리 기능 테스트"""
        # 캐시에 항목 추가
        for i in range(cache.max_size):
            cache.set(f"질문{i}", f"답변{i}", False)
        
        initial_stats = cache.get_stats()
        
        # 정리 실행
        cleanup_result = cache.cleanup()
        
        assert 'initial_size' in cleanup_result
        assert 'final_size' in cleanup_result
        assert 'expired_removed' in cleanup_result
        assert 'lru_removed' in cleanup_result
        assert cleanup_result['initial_size'] == initial_stats['cache_size']

    def test_clear_all(self, cache):
        """전체 캐시 삭제 테스트"""
        cache.set("질문1", "답변1", False)
        cache.set("질문2", "답변2", False)
        
        assert cache.get_stats()['cache_size'] == 2
        
        cache.clear()
        
        assert cache.get_stats()['cache_size'] == 0
        assert cache.get("질문1") is None
        assert cache.get("질문2") is None

    def test_memory_usage_estimation(self, cache):
        """메모리 사용량 추정 테스트"""
        cache.set("질문1", "답변1", False)
        cache.set("질문2", "답변2", False)
        
        stats = cache.get_stats()
        
        assert 'memory_usage_estimate' in stats
        assert stats['memory_usage_estimate'] > 0
        assert stats['memory_usage_estimate'] == stats['cache_size'] * 500

    def test_expired_items_cleanup(self):
        """만료된 항목 자동 정리 테스트"""
        cache = ThreadSafeResponseCache(max_size=5, ttl_hours=0.1/3600)
        
        cache.set("질문1", "답변1", False)
        cache.set("질문2", "답변2", False)
        
        # 만료 대기
        time.sleep(0.15)
        
        # 새 항목 추가 시 만료된 항목 자동 정리
        cache.set("질문3", "답변3", False)
        
        stats = cache.get_stats()
        assert stats['expired_removals'] > 0

    def test_edge_case_empty_question(self, cache):
        """엣지 케이스: 빈 질문"""
        cache.set("", "빈 질문 답변", False)
        result = cache.get("")
        
        assert result is not None
        assert result[0] == "빈 질문 답변"

    def test_edge_case_very_long_question(self, cache):
        """엣지 케이스: 매우 긴 질문"""
        long_question = "질문" * 1000
        cache.set(long_question, "긴 질문 답변", False)
        
        result = cache.get(long_question)
        assert result is not None
        assert result[0] == "긴 질문 답변"

    def test_unicode_handling(self, cache):
        """유니코드 처리 테스트"""
        unicode_question = "한글 질문 🤔 特殊文字 🎉"
        unicode_answer = "유니코드 답변 ✅ 正解 🌟"
        
        cache.set(unicode_question, unicode_answer, False)
        result = cache.get(unicode_question)
        
        assert result is not None
        assert result[0] == unicode_answer

    def test_json_serialization_safety(self, cache):
        """JSON 직렬화 안전성 테스트"""
        # JSON에서 문제가 될 수 있는 문자들
        problematic_chars = '{"}\n\t\\'
        
        cache.set(problematic_chars, "특수 문자 답변", False)
        result = cache.get(problematic_chars)
        
        assert result is not None
        assert result[0] == "특수 문자 답변"

    @pytest.mark.parametrize("max_size,ttl_hours", [
        (1, 0.1),
        (100, 24),
        (1000, 48),
    ])
    def test_various_configurations(self, max_size, ttl_hours):
        """다양한 설정값 테스트"""
        cache = ThreadSafeResponseCache(max_size=max_size, ttl_hours=ttl_hours)
        
        cache.set("테스트 질문", "테스트 답변", False)
        result = cache.get("테스트 질문")
        
        assert result is not None
        assert cache.max_size == max_size
        assert cache.ttl_seconds == ttl_hours * 3600 