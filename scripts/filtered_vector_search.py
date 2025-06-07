import os
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

# ✅ 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

class FilteredVectorSearch:
    def __init__(self):
        """초기화: Embedding 모델과 Pinecone 인덱스 설정"""
        self.embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)
    
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
        # 1. 쿼리 텍스트를 벡터로 변환
        query_vector = self.embedding_model.embed_query(query)
        
        # 2. 메타데이터 필터 구성
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        if section:
            filter_dict["section"] = section
        
        # 3. Pinecone 검색 실행
        search_results = self.index.query(
            vector=query_vector,
            top_k=k,
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )
        
        # 4. 결과 처리 및 필터링
        results = []
        for match in search_results.matches:
            score = match.score
            if score >= score_threshold:
                results.append((match.metadata, score))
        
        return results

def main():
    """예제 실행"""
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