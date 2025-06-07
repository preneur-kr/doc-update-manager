import os
import json
import hashlib
from typing import List, Tuple, Dict, Set
from datetime import datetime
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocChangeDetector:
    """문서 변경 감지 및 키워드 추출 클래스"""
    
    def __init__(self, doc_path: str):
        """
        초기화
        
        Args:
            doc_path (str): 문서 경로
        """
        self.doc_path = doc_path
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self.keywords = self._load_keywords()
    
    def _load_keywords(self) -> List[str]:
        """
        키워드 설정 파일을 로드합니다.
        
        Returns:
            List[str]: 키워드 목록
        """
        try:
            # config/keywords.json 파일 로드
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "keywords.json")
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("keywords", [])
        except Exception as e:
            print(f"⚠️ 키워드 설정 파일 로드 실패: {str(e)}")
            return []
    
    def _load_and_split_doc(self, doc_path: str) -> List[str]:
        """
        문서를 로드하고 청크로 분할합니다.
        
        Args:
            doc_path (str): 문서 경로
            
        Returns:
            List[str]: 청크 목록
        """
        loader = TextLoader(doc_path, encoding="utf-8")
        documents = loader.load()
        chunks = self.splitter.split_documents(documents)
        return [doc.page_content for doc in chunks]
    
    def _get_chunk_hash(self, chunk: str) -> str:
        """
        청크의 해시값을 계산합니다.
        
        Args:
            chunk (str): 청크 텍스트
            
        Returns:
            str: SHA256 해시값
        """
        return hashlib.sha256(chunk.encode()).hexdigest()
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """
        텍스트에서 주요 키워드를 추출합니다.
        
        Args:
            text (str): 텍스트
            
        Returns:
            Set[str]: 추출된 키워드 집합
        """
        text = text.lower()
        return {keyword for keyword in self.keywords if keyword in text}
    
    def _get_chunk_diff(self, old_chunk: str, new_chunk: str) -> str:
        """
        청크의 변경 사항을 diff 형식으로 반환합니다.
        
        Args:
            old_chunk (str): 이전 청크
            new_chunk (str): 새로운 청크
            
        Returns:
            str: diff 형식의 변경 사항
        """
        # TODO: 실제 diff 구현
        return f"```diff\n- {old_chunk}\n+ {new_chunk}\n```"
    
    def detect_changes(self) -> Tuple[List[str], int, int, int, Dict[str, List[str]]]:
        """
        문서 변경을 감지하고 변경 통계를 반환합니다.
        
        Returns:
            Tuple[List[str], int, int, int, Dict[str, List[str]]]: 
                (변경된 키워드 목록, 추가된 청크 수, 삭제된 청크 수, 수정된 청크 수, 변경 상세 정보)
        """
        # 이전 청크 로드
        try:
            with open(f"{self.doc_path}.chunks", "r", encoding="utf-8") as f:
                old_chunks = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            old_chunks = []
        
        # 현재 청크 로드
        current_chunks = self._load_and_split_doc(self.doc_path)
        
        # 청크 해시 계산
        old_hashes = {self._get_chunk_hash(chunk): chunk for chunk in old_chunks}
        current_hashes = {self._get_chunk_hash(chunk): chunk for chunk in current_chunks}
        
        # 변경 감지
        added_chunks = [chunk for chunk in current_chunks if self._get_chunk_hash(chunk) not in old_hashes]
        removed_chunks = [chunk for chunk in old_chunks if self._get_chunk_hash(chunk) not in current_hashes]
        modified_chunks = [
            chunk for chunk in current_chunks
            if self._get_chunk_hash(chunk) in old_hashes and chunk != old_hashes[self._get_chunk_hash(chunk)]
        ]
        
        # 변경된 청크에서 키워드 추출
        changed_keywords = set()
        for chunk in added_chunks + modified_chunks:
            changed_keywords.update(self._extract_keywords(chunk))
        
        # 변경 상세 정보 수집
        change_details = {
            "added": added_chunks,
            "removed": removed_chunks,
            "modified": [
                self._get_chunk_diff(
                    old_hashes[self._get_chunk_hash(chunk)],
                    chunk
                ) for chunk in modified_chunks
            ]
        }
        
        # 현재 청크 저장
        with open(f"{self.doc_path}.chunks", "w", encoding="utf-8") as f:
            f.write("\n".join(current_chunks))
        
        return (
            sorted(list(changed_keywords)),
            len(added_chunks),
            len(removed_chunks),
            len(modified_chunks),
            change_details
        ) 