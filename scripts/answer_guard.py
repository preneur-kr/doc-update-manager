"""
Fallback-like 응답을 감지하는 모듈입니다.
GPT의 응답이 문서에 없는 정보를 포함하거나 불명확한 경우를 감지합니다.
"""

from typing import List

# Fallback 감지 키워드 목록
FALLBACK_INDICATORS = [
    "정확한 안내가 어렵습니다",
    "자세한 정보는 없습니다",
    "명확하지 않습니다",
    "해당 정보는 제공되지 않습니다",
    "명시되어 있지 않습니다",
    "문서에서 확인할 수 없습니다",
    "문서에 해당 정보가 없습니다",
    "정책에 명시된 내용이 없습니다",
    "시간이 정확히 명시되어 있지 않습니다",
    "문서에 명확한 시간 정보가 없습니다",
    "정확한 시간을 확인할 수 없습니다"
]

def is_fallback_like_response(answer: str) -> bool:
    """
    GPT의 응답이 fallback-like 응답인지 확인합니다.
    
    Args:
        answer (str): GPT가 생성한 응답 텍스트
        
    Returns:
        bool: fallback-like 응답이면 True, 아니면 False
    """
    return any(indicator in answer for indicator in FALLBACK_INDICATORS)

def is_fallback_response(response: str) -> bool:
    """
    응답이 fallback 응답인지 확인합니다.
    
    Args:
        response (str): 확인할 응답
        
    Returns:
        bool: fallback 응답 여부
    """
    fallback_keywords = [
        "정확한 안내가 어렵습니다",
        "문서에서 찾을 수 없습니다",
        "확인할 수 없습니다",
        "알 수 없습니다",
        "제공할 수 없습니다",
        "02-1234-5678번으로 연락 주시면"  # FALLBACK_MESSAGE의 핵심 문구
    ]
    
    return any(keyword in response for keyword in fallback_keywords) 