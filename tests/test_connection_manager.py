import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# 테스트용 시스템 경로 설정
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.connection_manager import ConnectionManager


class TestConnectionManager:
    """ConnectionManager 클래스 테스트"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        # 싱글톤 인스턴스 리셋
        ConnectionManager._instance = None
        ConnectionManager._initialized = False

    @pytest.fixture
    def mock_dependencies(self):
        """외부 의존성 모킹"""
        with patch('scripts.connection_manager.ChatOpenAI') as mock_openai, \
             patch('scripts.connection_manager.OpenAIEmbeddings') as mock_embeddings, \
             patch('scripts.connection_manager.Pinecone') as mock_pinecone, \
             patch('scripts.connection_manager.FilteredVectorSearch') as mock_search:
            
            yield {
                'openai': mock_openai,
                'embeddings': mock_embeddings,
                'pinecone': mock_pinecone,
                'search': mock_search
            }

    def test_singleton_pattern(self):
        """싱글톤 패턴이 올바르게 작동하는지 테스트"""
        manager1 = ConnectionManager()
        manager2 = ConnectionManager()
        
        assert manager1 is manager2
        assert id(manager1) == id(manager2)

    def test_thread_safety(self):
        """스레드 안전성 테스트"""
        instances = []
        
        def create_instance():
            instance = ConnectionManager()
            instances.append(instance)
        
        # 여러 스레드에서 동시에 인스턴스 생성
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        # 모든 인스턴스가 동일한지 확인
        assert len(instances) == 10
        assert all(instance is instances[0] for instance in instances)

    def test_openai_llm_initialization(self, mock_dependencies):
        """OpenAI LLM 초기화 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            llm = manager.openai_llm
            
            assert mock_dependencies['openai'].called
            assert llm is not None
            
            # 재호출 시 동일한 인스턴스 반환 확인
            llm2 = manager.openai_llm
            assert llm is llm2

    def test_openai_llm_initialization_error(self, mock_dependencies):
        """OpenAI LLM 초기화 실패 테스트"""
        manager = ConnectionManager()
        mock_dependencies['openai'].side_effect = Exception("API key error")
        
        with pytest.raises(Exception, match="API key error"):
            manager.openai_llm

    def test_openai_embeddings_initialization(self, mock_dependencies):
        """OpenAI Embeddings 초기화 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            embeddings = manager.openai_embeddings
            
            assert mock_dependencies['embeddings'].called
            assert embeddings is not None

    def test_pinecone_client_initialization(self, mock_dependencies):
        """Pinecone 클라이언트 초기화 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'PINECONE_API_KEY': 'test-key'}):
            client = manager.pinecone_client
            
            assert mock_dependencies['pinecone'].called
            assert client is not None

    def test_vector_searcher_initialization(self, mock_dependencies):
        """벡터 검색기 초기화 테스트"""
        manager = ConnectionManager()
        
        searcher = manager.vector_searcher
        
        assert mock_dependencies['search'].called
        assert searcher is not None
        
        # 연결 관리자가 의존성 주입으로 전달되는지 확인
        mock_dependencies['search'].assert_called_with(connection_manager=manager)

    def test_warm_up_success(self, mock_dependencies):
        """워밍업 성공 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'PINECONE_API_KEY': 'test-key'
        }):
            results = manager.warm_up()
            
            expected_services = ['openai_llm', 'openai_embeddings', 'pinecone_client', 'vector_searcher']
            
            assert all(service in results for service in expected_services)
            assert all(results[service] for service in expected_services)

    def test_warm_up_partial_failure(self, mock_dependencies):
        """워밍업 부분 실패 테스트"""
        manager = ConnectionManager()
        
        # OpenAI LLM 초기화 실패 시뮬레이션
        mock_dependencies['openai'].side_effect = Exception("API error")
        
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'PINECONE_API_KEY': 'test-key'
        }):
            results = manager.warm_up()
            
            assert results['openai_llm'] is False
            assert results['openai_embeddings'] is True
            assert results['pinecone_client'] is True
            assert results['vector_searcher'] is True

    def test_health_check_not_initialized(self):
        """서비스가 초기화되지 않은 상태의 헬스 체크"""
        manager = ConnectionManager()
        
        health_status = manager.health_check()
        
        for service in ['openai_llm', 'openai_embeddings', 'pinecone_client', 'vector_searcher']:
            assert health_status[service]['status'] == 'not_initialized'

    def test_health_check_initialized(self, mock_dependencies):
        """서비스가 초기화된 상태의 헬스 체크"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            # 서비스 초기화
            _ = manager.openai_llm
            
            health_status = manager.health_check()
            
            assert health_status['openai_llm']['status'] == 'healthy'

    def test_health_check_caching(self, mock_dependencies):
        """헬스 체크 캐싱 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            # 첫 번째 헬스 체크
            health1 = manager.health_check()
            
            # 즉시 두 번째 헬스 체크 (캐시된 결과 사용)
            health2 = manager.health_check()
            
            # 캐시가 사용되었는지 확인 (실제 서비스 호출 없이)
            assert health1 == health2

    def test_reset_connection_success(self, mock_dependencies):
        """연결 재설정 성공 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            # 서비스 초기화
            _ = manager.openai_llm
            assert manager._openai_llm is not None
            
            # 연결 재설정
            result = manager.reset_connection('openai_llm')
            
            assert result is True
            assert manager._openai_llm is None

    def test_reset_connection_invalid_service(self):
        """잘못된 서비스명으로 연결 재설정 시도"""
        manager = ConnectionManager()
        
        result = manager.reset_connection('invalid_service')
        
        assert result is False

    def test_connection_status_tracking(self, mock_dependencies):
        """연결 상태 추적 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            # 서비스 초기화
            _ = manager.openai_llm
            
            # 연결 상태 확인
            assert 'openai_llm' in manager._connection_status
            assert manager._connection_status['openai_llm']['status'] == 'connected'
            assert 'last_updated' in manager._connection_status['openai_llm']

    def test_connection_status_error_tracking(self, mock_dependencies):
        """연결 오류 상태 추적 테스트"""
        manager = ConnectionManager()
        
        mock_dependencies['openai'].side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            manager.openai_llm
        
        # 오류 상태가 기록되었는지 확인
        assert 'openai_llm' in manager._connection_status
        assert manager._connection_status['openai_llm']['status'] == 'error'
        assert 'Connection failed' in manager._connection_status['openai_llm']['error']

    def test_get_connection_info(self, mock_dependencies):
        """연결 정보 조회 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            # 일부 서비스 초기화
            _ = manager.openai_llm
            _ = manager.pinecone_client
            
            info = manager.get_connection_info()
            
            assert 'initialized_services' in info
            assert 'openai_llm' in info['initialized_services']
            assert 'pinecone_client' in info['initialized_services']
            assert 'connection_status' in info
            assert 'health_check_interval' in info
            assert 'instance_id' in info

    def test_concurrent_initialization(self, mock_dependencies):
        """동시 초기화 테스트"""
        manager = ConnectionManager()
        results = []
        errors = []
        
        def initialize_service():
            try:
                with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
                    llm = manager.openai_llm
                    results.append(llm)
            except Exception as e:
                errors.append(e)
        
        # 여러 스레드에서 동시 초기화
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=initialize_service)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 오류 없이 모든 스레드가 완료되었는지 확인
        assert len(errors) == 0
        assert len(results) == 5
        
        # 모든 결과가 동일한 인스턴스인지 확인
        assert all(result is results[0] for result in results)

    def test_memory_cleanup_on_reset(self, mock_dependencies):
        """재설정 시 메모리 정리 테스트"""
        manager = ConnectionManager()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            # 여러 서비스 초기화
            _ = manager.openai_llm
            _ = manager.openai_embeddings
            
            initial_status_count = len(manager._connection_status)
            
            # 특정 서비스 재설정
            manager.reset_connection('openai_llm')
            
            # 상태 정보는 유지되어야 함 (이력 추적용)
            assert len(manager._connection_status) == initial_status_count
            assert manager._openai_llm is None
            assert manager._openai_embeddings is not None

    @pytest.mark.parametrize("service_name,property_name", [
        ("openai_llm", "_openai_llm"),
        ("openai_embeddings", "_openai_embeddings"),
        ("pinecone_client", "_pinecone_client"),
        ("vector_searcher", "_vector_searcher"),
    ])
    def test_lazy_initialization(self, mock_dependencies, service_name, property_name):
        """지연 초기화 테스트"""
        manager = ConnectionManager()
        
        # 초기 상태에서는 None이어야 함
        assert getattr(manager, property_name) is None
        
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'PINECONE_API_KEY': 'test-key'
        }):
            # 프로퍼티 접근 시 초기화
            service = getattr(manager, service_name)
            
            assert service is not None
            assert getattr(manager, property_name) is not None

    def test_error_resilience(self, mock_dependencies):
        """오류 복원력 테스트"""
        manager = ConnectionManager()
        
        # 첫 번째 시도에서 실패
        mock_dependencies['openai'].side_effect = Exception("Temporary failure")
        
        with pytest.raises(Exception):
            manager.openai_llm
        
        # 오류 해결 후 재시도
        mock_dependencies['openai'].side_effect = None
        mock_dependencies['openai'].return_value = Mock()
        
        # 연결 재설정 후 다시 시도
        manager.reset_connection('openai_llm')
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            llm = manager.openai_llm
            assert llm is not None 