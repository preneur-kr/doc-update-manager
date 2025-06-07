import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_DOCUPDATE_WEBHOOK_URL = os.getenv("SLACK_DOCUPDATE_WEBHOOK_URL")

def send_block_message(payload: Dict[str, Any], webhook_url: Optional[str] = None) -> bool:
    """
    Block Kit 메시지를 Slack으로 전송합니다.
    
    Args:
        payload (Dict[str, Any]): Block Kit 메시지 payload
        webhook_url (Optional[str]): 사용할 webhook URL (기본값: SLACK_WEBHOOK_URL)
        
    Returns:
        bool: 전송 성공 여부
    """
    if not webhook_url:
        webhook_url = SLACK_WEBHOOK_URL
        
    if not webhook_url:
        print("❌ Slack Webhook URL이 설정되지 않았습니다.")
        return False
        
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"❌ Slack 알림 전송 실패: {response.text}")
            return False
            
        print("✅ Slack 알림 전송 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Slack 알림 전송 중 오류 발생: {str(e)}")
        return False

def send_doc_update_message(payload: Dict[str, Any]) -> bool:
    """
    문서 업데이트 알림을 전송합니다.
    
    Args:
        payload (Dict[str, Any]): Block Kit 메시지 payload
        
    Returns:
        bool: 전송 성공 여부
    """
    if not SLACK_DOCUPDATE_WEBHOOK_URL:
        print("⚠️ SLACK_DOCUPDATE_WEBHOOK_URL이 설정되지 않았습니다.")
        return False
        
    return send_block_message(payload, SLACK_DOCUPDATE_WEBHOOK_URL) 