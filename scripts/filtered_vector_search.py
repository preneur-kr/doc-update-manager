import os
from typing import List, Tuple, Optional, TYPE_CHECKING
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

if TYPE_CHECKING:
    from scripts.connection_manager import ConnectionManager

# ✅ 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

class FilteredVectorSearch:
    def __init__(self, connection_manager: Optional['ConnectionManager'] = None):
        """
        초기화: 연결 관리자를 통한 의존성 주입
        
        Args:
            connection_manager: 연결 관리자 인스턴스 (없으면 직접 초기화)
        """
        self.connection_manager = connection_manager
        
        if connection_manager:
            # 연결 관리자를 통한 초기화 (권장)
            self.embedding_model = None  # 지연 초기화
            self.index = None  # 지연 초기화
        else:
            # 직접 초기화 (하위 호환성)
            print("⚠️ 연결 관리자 없이 직접 초기화 - 성능이 저하될 수 있습니다")
            self.embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            pc = Pinecone(api_key=PINECONE_API_KEY)
            self.index = pc.Index(PINECONE_INDEX_NAME)
    
    def _get_embedding_model(self) -> OpenAIEmbeddings:
        """임베딩 모델을 가져옵니다 (지연 초기화)"""
        if self.connection_manager:
            return self.connection_manager.openai_embeddings
        return self.embedding_model
    
    def _get_index(self):
        """Pinecone 인덱스를 가져옵니다 (지연 초기화)"""
        if self.connection_manager:
            pc = self.connection_manager.pinecone_client
            return pc.Index(PINECONE_INDEX_NAME)
        return self.index
    
    def similarity_search_with_metadata(
        self,
        query: str,
        k: int = 3,
        category: Optional[str] = None,
        section: Optional[str] = None,
        score_threshold: float = 0.7
    ) -> List[Tuple[dict, float]]:
        """
        메타데이터 필터링을 적용한 벡터 유사도 검색을 수행합니다.
        
        Args:
            query (str): 검색 쿼리
            k (int): 반환할 결과 수
            category (Optional[str]): 카테고리 필터 (예: "예약", "운영", "시설")
            section (Optional[str]): 섹션 필터 (예: "환불정책", "체크인 안내")
            score_threshold (float): 최소 유사도 점수 (0.0 ~ 1.0)
            
        Returns:
            List[Tuple[dict, float]]: (문서 메타데이터, 유사도 점수) 튜플의 리스트
        """
        try:
            # 1. 쿼리 텍스트를 벡터로 변환
            embedding_model = self._get_embedding_model()
            query_vector = embedding_model.embed_query(query)
            
            # 2. 메타데이터 필터 구성
            filter_dict = {}
            if category:
                filter_dict["category"] = category
            if section:
                filter_dict["section"] = section
            
            # 3. Pinecone에서 유사도 검색 수행
            index = self._get_index()
            search_kwargs = {
                "vector": query_vector,
                "top_k": k * 2,  # 필터링으로 인한 결과 손실을 고려하여 더 많이 검색
                "include_metadata": True
            }
            
            # 필터가 있는 경우에만 추가
            if filter_dict:
                search_kwargs["filter"] = filter_dict
            
            search_results = index.query(**search_kwargs)
            
            # 4. 결과 처리 및 점수 필터링
            filtered_results = []
            for match in search_results.matches:
                score = float(match.score)
                if score >= score_threshold:
                    metadata = match.metadata or {}
                    # 텍스트 내용이 메타데이터에 포함되어 있는지 확인
                    if 'text' not in metadata:
                        metadata['text'] = f"문서 ID: {match.id}"
                    
                    filtered_results.append((metadata, score))
            
            # 5. 상위 k개 결과만 반환
            final_results = filtered_results[:k]
            
            print(f"🔍 벡터 검색 완료: {len(final_results)}개 결과 (임계값: {score_threshold})")
            for i, (metadata, score) in enumerate(final_results):
                text_preview = metadata.get('text', '')[:50] + '...' if len(metadata.get('text', '')) > 50 else metadata.get('text', '')
                print(f"  {i+1}. 점수: {score:.3f} | {text_preview}")
            
            return final_results
            
        except Exception as e:
            print(f"❌ 벡터 검색 중 오류 발생: {str(e)}")
            return []
    
    def get_search_stats(self) -> dict:
        """검색 통계 정보를 반환합니다."""
        try:
            index = self._get_index()
            stats = index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': getattr(stats, 'index_fullness', 'unknown'),
                'namespaces': getattr(stats, 'namespaces', {}),
                'connection_type': 'managed' if self.connection_manager else 'direct'
            }
        except Exception as e:
            return {
                'error': str(e),
                'connection_type': 'managed' if self.connection_manager else 'direct'
            }
    
    def health_check(self) -> dict:
        """검색 시스템의 헬스 체크를 수행합니다."""
        try:
            # 간단한 테스트 쿼리 수행
            test_results = self.similarity_search_with_metadata(
                query="테스트",
                k=1,
                score_threshold=0.0
            )
            
            return {
                'status': 'healthy',
                'test_query_results': len(test_results),
                'embedding_model_available': self._get_embedding_model() is not None,
                'index_available': self._get_index() is not None,
                'connection_type': 'managed' if self.connection_manager else 'direct'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'connection_type': 'managed' if self.connection_manager else 'direct'
            }

def main():
    """예제 실행"""
    # 실제 사용 시에는 ConnectionManager를 통해 인스턴스화
    # 여기서는 임시로 직접 인스턴스화하여 사용
    # from scripts.connection_manager import ConnectionManager
    # conn_manager = ConnectionManager()
    # searcher = FilteredVectorSearch(connection_manager=conn_manager)

    # 임시 인스턴스화 (연결 관리자 없이 직접 사용)
    searcher = FilteredVectorSearch()
    
    # 예제 쿼리들
    example_queries = [
        "환불 정책이 어떻게 되나요?",
        "체크인 시간은 언제인가요?",
        "주차는 어떻게 하나요?"
    ]
    
    # 카테고리별 검색 예제
    print("\n=== 카테고리 '예약' 검색 결과 ===")
    for query in example_queries:
        print(f"\n쿼리: {query}")
        results = searcher.similarity_search_with_metadata(
            query=query,
            category="예약",
            k=2
        )
        for metadata, score in results:
            print(f"점수: {score:.3f}")
            print(f"섹션: {metadata['section']}")
            print(f"카테고리: {metadata['category']}")
            print(f"내용: {metadata['text'][:100]}...")
    
    # 섹션별 검색 예제
    print("\n=== 섹션 '환불정책' 검색 결과 ===")
    for query in example_queries:
        print(f"\n쿼리: {query}")
        results = searcher.similarity_search_with_metadata(
            query=query,
            section="환불정책",
            k=2
        )
        for metadata, score in results:
            print(f"점수: {score:.3f}")
            print(f"섹션: {metadata['section']}")
            print(f"카테고리: {metadata['category']}")
            print(f"내용: {metadata['text'][:100]}...")

if __name__ == "__main__":
    main() 