import hmac
import hashlib
from app.core.config import settings

def verify_slack_request(request_body: bytes, timestamp: str, signature: str) -> bool:
    """
    Slack 요청의 유효성을 검증합니다.
    
    Args:
        request_body (bytes): 요청 본문
        timestamp (str): Slack 요청 타임스탬프
        signature (str): Slack 서명
        
    Returns:
        bool: 검증 성공 여부
    """
    if not settings.SLACK_SIGNING_SECRET:
        return False
        
    # Slack 요청 검증을 위한 문자열 생성
    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"
    
    # 서명 생성
    hashed_signature = hmac.new(
        settings.SLACK_SIGNING_SECRET.encode('utf-8'),
        sig_basestring.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    my_signature = f"v0={hashed_signature}"
    
    return hmac.compare_digest(my_signature, signature) 