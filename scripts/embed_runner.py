import os
import hashlib
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient

# ✅ 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# ✅ 메타데이터 추론을 위한 키워드 매핑
SECTION_KEYWORDS = {
    "환불": ("환불정책", "예약"),
    "취소": ("환불정책", "예약"),
    "예약": ("예약정책", "예약"),
    "체크인": ("체크인 안내", "예약"),
    "입실": ("체크인 안내", "예약"),
    "체크아웃": ("체크아웃 안내", "예약"),
    "퇴실": ("체크아웃 안내", "예약"),
    "조식": ("식사 안내", "운영"),
    "중식": ("식사 안내", "운영"),
    "석식": ("식사 안내", "운영"),
    "흡연": ("흡연 정책", "운영"),
    "금연": ("흡연 정책", "운영"),
    "주차": ("주차 안내", "시설"),
    "CCTV": ("보안 정책", "운영"),
    "반려동물": ("반려동물 정책", "운영"),
    "청소": ("청소 정책", "운영"),
    "파손": ("시설 이용", "시설"),
    "오염": ("시설 이용", "시설"),
    "추가요금": ("요금 정책", "예약"),
    "인원": ("인원 정책", "예약")
}

def get_section_category(text: str) -> tuple[str, str]:
    """
    텍스트 내용을 기반으로 section과 category를 추론합니다.
    
    Args:
        text (str): 청크 텍스트 내용
        
    Returns:
        tuple[str, str]: (section, category) 튜플
    """
    text = text.lower()
    for keyword, (section, category) in SECTION_KEYWORDS.items():
        if keyword in text:
            return section, category
    return "기타", "기타"

# ✅ 문서 임베딩 및 업로드 함수
def run_embedding(doc_path: str = "docs/hotel_policy.txt"):
    print("📥 문서 임베딩 및 업로드 시작...")

    # 1. 문서 불러오기
    loader = TextLoader(doc_path, encoding="utf-8")
    documents = loader.load()
    print(f"📄 문서 로드 완료: {doc_path}")

    # 2. 문서 분할
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"🔪 문서 분할 완료: {len(chunks)}개 청크")

    # 3. Embedding 모델 준비
    embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # 4. Pinecone 초기화 및 인덱스 선택
    pc = PineconeClient(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    print(f"🧠 Pinecone 인덱스 선택됨: {PINECONE_INDEX_NAME}")
    print(f"✅ 사용 가능한 인덱스 목록: {pc.list_indexes().names()}")

    # 5. 기존 벡터 삭제
    print("🧹 기존 벡터 삭제 중...")
    index.delete(delete_all=True)
    print("✅ 기존 벡터 삭제 완료")

    # 6. 벡터 변환 및 업로드
    embeddings = embedding_model.embed_documents([doc.page_content for doc in chunks])
    
    vectors_to_upsert = []
    for doc, embedding in zip(chunks, embeddings):
        # 문서 내용의 해시값을 ID로 사용
        doc_hash = hashlib.sha256(doc.page_content.encode()).hexdigest()[:16]
        
        # 메타데이터 추론
        section, category = get_section_category(doc.page_content)
        origin = os.path.basename(doc_path)
        
        vectors_to_upsert.append({
            'id': doc_hash,
            'values': embedding,
            'metadata': {
                'text': doc.page_content,
                'source': doc.metadata.get('source', ''),
                'origin': origin,
                'section': section,
                'category': category
            }
        })

    # 벡터 일괄 업로드
    index.upsert(vectors=vectors_to_upsert)
    print("✅ 벡터 업로드 완료!")

# ✅ 단독 실행 시 테스트
if __name__ == "__main__":
    run_embedding()