import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_DEFAULT_CHANNEL = os.getenv("SLACK_DEFAULT_CHANNEL", "general")

def send_block_message(payload: Dict[str, Any], channel: Optional[str] = None) -> bool:
    """
    Block Kit 메시지를 Slack으로 전송합니다.
    
    Args:
        payload (Dict[str, Any]): Block Kit 메시지 payload
        channel (Optional[str]): 메시지를 보낼 채널 (기본값: SLACK_DEFAULT_CHANNEL)
        
    Returns:
        bool: 전송 성공 여부
    """
    if not SLACK_BOT_TOKEN:
        print("❌ Slack Bot Token이 설정되지 않았습니다.")
        return False
        
    if not channel:
        channel = SLACK_DEFAULT_CHANNEL
        
    try:
        # ---  debugging ---
        print("\n--- 📦 SLACK API 요청 정보 ---")
        print(f"  - 전송 채널: #{channel}")
        print(f"  - 페이로드 (일부): {str(payload)[:500]}...")
        # --- debugging ---

        # chat.postMessage API 사용
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "channel": channel,
                **payload
            }
        )
        
        if not response.ok:
            print(f"❌ Slack API 요청 실패: {response.status_code}")
            return False
            
        result = response.json()
        if not result.get("ok"):
            print(f"❌ Slack 메시지 전송 실패: {result.get('error')}")
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
    # 문서 업데이트 알림은 항상 #docupdate-alerts 채널로 전송
    return send_block_message(payload, "docupdate-alerts")

def send_fallback_alert_message(payload: Dict[str, Any]) -> bool:
    """
    Fallback 알림을 전송합니다.
    
    Args:
        payload (Dict[str, Any]): Block Kit 메시지 payload
        
    Returns:
        bool: 전송 성공 여부
    """
    # Fallback 알림은 항상 #fallback-alerts 채널로 전송
    return send_block_message(payload, "fallback-alerts") 