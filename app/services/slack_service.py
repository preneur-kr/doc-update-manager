from typing import Dict, Any
from fastapi import HTTPException
from datetime import datetime
from scripts.sheet_logger import log_to_sheet
from scripts.slack_sender import send_block_message

class SlackService:
    @staticmethod
    async def handle_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Slack 이벤트를 처리합니다.
        
        Args:
            event_data (Dict[str, Any]): Slack 이벤트 데이터
            
        Returns:
            Dict[str, Any]: 처리 결과
        """
        # URL 검증 요청 처리
        if event_data.get("type") == "url_verification":
            return {"challenge": event_data["challenge"]}
            
        # Interactive message 처리
        if event_data.get("type") == "block_actions":
            actions = event_data.get("actions", [])
            if not actions:
                return {"status": "error", "message": "No actions found"}
                
            action = actions[0]  # 첫 번째 액션 사용
            action_id = action.get("action_id")
            value = action.get("value")  # 문서 경로
            message_ts = event_data.get("message_ts")
            channel = event_data.get("channel", {}).get("id")
            
            # Slack 메시지 URL 생성
            slack_message_url = f"https://slack.com/archives/{channel}/p{message_ts.replace('.', '')}" if channel and message_ts else ""
            
            if action_id == "approve_changes":
                # 승인 처리
                try:
                    # Google Sheets에 승인 기록
                    log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "document_path": value,
                        "change_type": "approved",
                        "change_keywords": "[]",
                        "chunks_plus": "[]",
                        "chunks_minus": "[]",
                        "chunks_tilde": "[]",
                        "approved": True,
                        "comment": "승인됨",
                        "slack_message_url": slack_message_url
                    }
                    
                    if not log_to_sheet(log_data):
                        raise Exception("Failed to log approval to sheet")
                        
                    # 승인 메시지 전송
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"✅ 문서 변경이 승인되었습니다: `{value}`"
                            }
                        }
                    ]
                    send_block_message({"blocks": blocks})
                    
                    return {"status": "ok", "message": "Changes approved"}
                    
                except Exception as e:
                    return {"status": "error", "message": str(e)}
                    
            elif action_id == "request_revision":
                # 수정 요청 처리
                try:
                    # Google Sheets에 수정 요청 기록
                    log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "document_path": value,
                        "change_type": "revision_requested",
                        "change_keywords": "[]",
                        "chunks_plus": "[]",
                        "chunks_minus": "[]",
                        "chunks_tilde": "[]",
                        "approved": False,
                        "comment": "수정 요청됨",
                        "slack_message_url": slack_message_url
                    }
                    
                    if not log_to_sheet(log_data):
                        raise Exception("Failed to log revision request to sheet")
                        
                    # 수정 요청 메시지 전송
                    blocks = [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"🔄 문서 수정이 요청되었습니다: `{value}`"
                            }
                        }
                    ]
                    send_block_message({"blocks": blocks})
                    
                    return {"status": "ok", "message": "Revision requested"}
                    
                except Exception as e:
                    return {"status": "error", "message": str(e)}
        
        return {"status": "ok", "message": "Event processed"} 