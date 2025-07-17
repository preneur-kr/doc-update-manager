"""
연결 관리자 - 외부 API 연결을 재사용하여 성능을 개선합니다.
"""

import os
import threading
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone
from scripts.filtered_vector_search import FilteredVectorSearch

# 환경 변수 로드
load_dotenv()

class ConnectionManager:
    """외부 API 연결을 관리하는 스레드 안전한 싱글톤 클래스"""
    
    _instance: Optional['ConnectionManager'] = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._openai_llm: Optional[ChatOpenAI] = None
                    self._openai_embeddings: Optional[OpenAIEmbeddings] = None
                    self._pinecone_client: Optional[Pinecone] = None
                    self._vector_searcher: Optional[FilteredVectorSearch] = None
                    
                    # 연결 상태 추적
                    self._connection_status: Dict[str, Dict[str, Any]] = {}
                    self._last_health_check: Dict[str, datetime] = {}
                    self._health_check_interval = timedelta(minutes=5)
                    
                    ConnectionManager._initialized = True
    
    def _update_connection_status(self, service: str, status: str, error: Optional[str] = None) -> None:
        """연결 상태를 업데이트합니다."""
        self._connection_status[service] = {
            'status': status,
            'last_updated': datetime.now(),
            'error': error
        }
    
    def _should_check_health(self, service: str) -> bool:
        """헬스 체크가 필요한지 확인합니다."""
        last_check = self._last_health_check.get(service)
        if not last_check:
            return True
        return datetime.now() - last_check > self._health_check_interval
    
    @property
    def openai_llm(self) -> ChatOpenAI:
        """OpenAI ChatGPT 모델 인스턴스를 반환 (재사용)"""
        if self._openai_llm is None:
            with self._lock:
                if self._openai_llm is None:
                    try:
                        print("🔄 OpenAI ChatGPT 모델 초기화 중...")
                        self._openai_llm = ChatOpenAI(
                            model_name="gpt-3.5-turbo",
                            temperature=0.7,
                            openai_api_key=os.getenv("OPENAI_API_KEY"),
                            request_timeout=30,
                            max_retries=2
                        )
                        self._update_connection_status("openai_llm", "connected")
                        print("✅ OpenAI ChatGPT 모델 초기화 완료")
                    except Exception as e:
                        error_msg = f"OpenAI ChatGPT 모델 초기화 실패: {str(e)}"
                        print(f"❌ {error_msg}")
                        self._update_connection_status("openai_llm", "error", error_msg)
                        raise
        return self._openai_llm
    
    @property
    def openai_embeddings(self) -> OpenAIEmbeddings:
        """OpenAI Embeddings 모델 인스턴스를 반환 (재사용)"""
        if self._openai_embeddings is None:
            with self._lock:
                if self._openai_embeddings is None:
                    try:
                        print("🔄 OpenAI Embeddings 모델 초기화 중...")
                        self._openai_embeddings = OpenAIEmbeddings(
                            openai_api_key=os.getenv("OPENAI_API_KEY"),
                            request_timeout=30,
                            max_retries=2
                        )
                        self._update_connection_status("openai_embeddings", "connected")
                        print("✅ OpenAI Embeddings 모델 초기화 완료")
                    except Exception as e:
                        error_msg = f"OpenAI Embeddings 모델 초기화 실패: {str(e)}"
                        print(f"❌ {error_msg}")
                        self._update_connection_status("openai_embeddings", "error", error_msg)
                        raise
        return self._openai_embeddings
    
    @property
    def pinecone_client(self) -> Pinecone:
        """Pinecone 클라이언트 인스턴스를 반환 (재사용)"""
        if self._pinecone_client is None:
            with self._lock:
                if self._pinecone_client is None:
                    try:
                        print("🔄 Pinecone 클라이언트 초기화 중...")
                        self._pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                        self._update_connection_status("pinecone_client", "connected")
                        print("✅ Pinecone 클라이언트 초기화 완료")
                    except Exception as e:
                        error_msg = f"Pinecone 클라이언트 초기화 실패: {str(e)}"
                        print(f"❌ {error_msg}")
                        self._update_connection_status("pinecone_client", "error", error_msg)
                        raise
        return self._pinecone_client
    
    @property
    def vector_searcher(self) -> FilteredVectorSearch:
        """벡터 검색기 인스턴스를 반환 (재사용)"""
        if self._vector_searcher is None:
            with self._lock:
                if self._vector_searcher is None:
                    try:
                        print("🔄 벡터 검색기 초기화 중...")
                        # 의존성 주입을 통해 연결 관리자를 전달
                        self._vector_searcher = FilteredVectorSearch(connection_manager=self)
                        self._update_connection_status("vector_searcher", "connected")
                        print("✅ 벡터 검색기 초기화 완료")
                    except Exception as e:
                        error_msg = f"벡터 검색기 초기화 실패: {str(e)}"
                        print(f"❌ {error_msg}")
                        self._update_connection_status("vector_searcher", "error", error_msg)
                        raise
        return self._vector_searcher
    
    def warm_up(self) -> Dict[str, bool]:
        """모든 연결을 워밍업합니다."""
        results = {}
        services = ['openai_llm', 'openai_embeddings', 'pinecone_client', 'vector_searcher']
        
        for service in services:
            try:
                print(f"🔥 {service} 워밍업 중...")
                getattr(self, service)  # property를 호출하여 초기화
                results[service] = True
                print(f"✅ {service} 워밍업 완료")
            except Exception as e:
                print(f"❌ {service} 워밍업 실패: {str(e)}")
                results[service] = False
        
        return results
    
    def health_check(self) -> Dict[str, Dict[str, Any]]:
        """모든 연결의 헬스 체크를 수행합니다."""
        health_status = {}
        
        for service_name in ['openai_llm', 'openai_embeddings', 'pinecone_client', 'vector_searcher']:
            try:
                if self._should_check_health(service_name):
                    # 기본적인 연결 상태 확인
                    service = getattr(self, f"_{service_name}")
                    if service is not None:
                        status = "healthy"
                    else:
                        status = "not_initialized"
                    
                    self._last_health_check[service_name] = datetime.now()
                else:
                    # 캐시된 상태 사용
                    status = self._connection_status.get(service_name, {}).get('status', 'unknown')
                
                health_status[service_name] = {
                    'status': status,
                    'last_check': self._last_health_check.get(service_name),
                    'cached_status': self._connection_status.get(service_name, {})
                }
            except Exception as e:
                health_status[service_name] = {
                    'status': 'error',
                    'error': str(e),
                    'last_check': datetime.now()
                }
        
        return health_status
    
    def reset_connection(self, service: str) -> bool:
        """특정 서비스의 연결을 재설정합니다."""
        try:
            with self._lock:
                if hasattr(self, f"_{service}"):
                    setattr(self, f"_{service}", None)
                    print(f"🔄 {service} 연결 재설정 완료")
                    return True
                else:
                    print(f"⚠️ 알 수 없는 서비스: {service}")
                    return False
        except Exception as e:
            print(f"❌ {service} 연결 재설정 실패: {str(e)}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """연결 정보를 반환합니다."""
        return {
            'initialized_services': [
                service for service in ['openai_llm', 'openai_embeddings', 'pinecone_client', 'vector_searcher']
                if getattr(self, f"_{service}") is not None
            ],
            'connection_status': self._connection_status,
            'health_check_interval': str(self._health_check_interval),
            'instance_id': id(self)
        }

# 글로벌 인스턴스
connection_manager = ConnectionManager() 