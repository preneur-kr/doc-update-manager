"""
연결 관리자 - 외부 API 연결을 재사용하여 성능을 개선합니다.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pinecone import Pinecone
from scripts.filtered_vector_search import FilteredVectorSearch

# 환경 변수 로드
load_dotenv()

class ConnectionManager:
    """외부 API 연결을 관리하는 싱글톤 클래스"""
    
    _instance: Optional['ConnectionManager'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._openai_llm: Optional[ChatOpenAI] = None
            self._openai_embeddings: Optional[OpenAIEmbeddings] = None
            self._pinecone_client: Optional[Pinecone] = None
            self._vector_searcher: Optional[FilteredVectorSearch] = None
            ConnectionManager._initialized = True
    
    @property
    def openai_llm(self) -> ChatOpenAI:
        """OpenAI ChatGPT 모델 인스턴스를 반환 (재사용)"""
        if self._openai_llm is None:
            print("🔄 OpenAI ChatGPT 모델 초기화 중...")
            self._openai_llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                request_timeout=30,  # 타임아웃 설정
                max_retries=2        # 재시도 설정
            )
            print("✅ OpenAI ChatGPT 모델 초기화 완료")
        return self._openai_llm
    
    @property
    def openai_embeddings(self) -> OpenAIEmbeddings:
        """OpenAI Embeddings 모델 인스턴스를 반환 (재사용)"""
        if self._openai_embeddings is None:
            print("🔄 OpenAI Embeddings 모델 초기화 중...")
            self._openai_embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                request_timeout=30,  # 타임아웃 설정
                max_retries=2        # 재시도 설정
            )
            print("✅ OpenAI Embeddings 모델 초기화 완료")
        return self._openai_embeddings
    
    @property
    def pinecone_client(self) -> Pinecone:
        """Pinecone 클라이언트 인스턴스를 반환 (재사용)"""
        if self._pinecone_client is None:
            print("🔄 Pinecone 클라이언트 초기화 중...")
            self._pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            print("✅ Pinecone 클라이언트 초기화 완료")
        return self._pinecone_client
    
    @property
    def vector_searcher(self) -> FilteredVectorSearch:
        """벡터 검색기 인스턴스를 반환 (재사용)"""
        if self._vector_searcher is None:
            print("🔄 벡터 검색기 초기화 중...")
            # FilteredVectorSearch를 연결 관리자와 함께 사용하도록 수정 필요
            self._vector_searcher = FilteredVectorSearch()
            print("✅ 벡터 검색기 초기화 완료")
        return self._vector_searcher
    
    def warm_up(self):
        """모든 연결을 미리 초기화 (워밍업)"""
        print("🔥 연결 관리자 워밍업 시작...")
        try:
            # 핵심 연결부터 순차적으로 초기화
            print("🔄 OpenAI LLM 초기화...")
            _ = self.openai_llm
            
            print("🔄 OpenAI Embeddings 초기화...")
            _ = self.openai_embeddings
            
            print("🔄 Pinecone 클라이언트 초기화...")
            _ = self.pinecone_client
            
            print("🔄 벡터 검색기 초기화...")
            _ = self.vector_searcher
            
            # 캐시 통계 출력
            try:
                from scripts.response_cache import response_cache
                stats = response_cache.get_stats()
                print(f"💾 응답 캐시 상태: {stats['cache_size']}/{stats['max_size']} 항목")
            except Exception:
                pass
            
            print("✅ 연결 관리자 워밍업 완료")
        except Exception as e:
            print(f"❌ 연결 관리자 워밍업 실패: {str(e)}")
            raise
    
    def reset_connections(self):
        """모든 연결을 리셋 (문제 발생 시 사용)"""
        print("🔄 모든 연결 리셋 중...")
        self._openai_llm = None
        self._openai_embeddings = None
        self._pinecone_client = None
        self._vector_searcher = None
        print("✅ 모든 연결 리셋 완료")

# 전역 인스턴스
connection_manager = ConnectionManager() 