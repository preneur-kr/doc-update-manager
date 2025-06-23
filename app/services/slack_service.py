from typing import Dict, Any
from fastapi import HTTPException
from datetime import datetime
from scripts.sheet_logger import log_to_sheet
from scripts.slack_sender import send_block_message
import json

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
        print(f"DEBUG: Handling Slack event: {event_data}")
        
        # URL 검증 요청 처리
        if event_data.get("type") == "url_verification":
            print("DEBUG: Processing URL verification request")
            return {"challenge": event_data["challenge"]}
            
        # Interactive message 처리
        if event_data.get("type") == "block_actions":
            print("DEBUG: Processing block_actions event")
            actions = event_data.get("actions", [])
            if not actions:
                print("DEBUG: No actions found in block_actions event")
                return {"status": "error", "message": "No actions found"}
                
            action = actions[0]  # 첫 번째 액션 사용
            action_id = action.get("action_id")
            value = action.get("value")  # 문서 경로
            
            # 채널 정보 추출
            channel = event_data.get("channel", {}).get("id")
            if not channel:
                print("DEBUG: Channel ID not found in event data")
                channel = event_data.get("container", {}).get("channel_id")
            
            # 메시지 정보 추출
            message = event_data.get("message", {})
            message_ts = message.get("ts") or event_data.get("message_ts")
            
            # 원본 문서 변경 정보 추출
            original_blocks = message.get("blocks", [])
            print(f"DEBUG: Original message blocks: {json.dumps(original_blocks, indent=2, ensure_ascii=False)}")
            change_info = {}
            for block in original_blocks:
                if block.get("type") == "section":
                    text = block.get("text", {}).get("text", "")
                    if "변경된 키워드" in text:
                        keywords = [k.strip("*") for k in text.split("*")[1:] if k.strip()]
                        change_info["keywords"] = keywords
                    elif "변경 통계" in text:
                        stats = text.split("\n")[1].strip()
                        chunks_info = {}
                        for stat in stats.split("|"):
                            stat = stat.strip()
                            try:
                                if "추가" in stat:
                                    # ➕ 2개 추가 -> 2
                                    num = stat.split("개")[0].strip().split()[-1]
                                    chunks_info["added"] = int(num)
                                elif "삭제" in stat:
                                    # ➖ 1개 삭제 -> 1
                                    num = stat.split("개")[0].strip().split()[-1]
                                    chunks_info["removed"] = int(num)
                                elif "수정" in stat:
                                    # ✏️ 3개 수정 -> 3
                                    num = stat.split("개")[0].strip().split()[-1]
                                    chunks_info["modified"] = int(num)
                            except (ValueError, IndexError) as e:
                                print(f"DEBUG: Error parsing chunk stats: {e}")
                                print(f"DEBUG: Problematic stat: {stat}")
                                # 파싱 실패시 기본값 0 사용
                                if "추가" in stat:
                                    chunks_info["added"] = 0
                                elif "삭제" in stat:
                                    chunks_info["removed"] = 0
                                elif "수정" in stat:
                                    chunks_info["modified"] = 0
                        change_info["chunks"] = chunks_info
            
            # Slack 메시지 URL 생성
            slack_message_url = ""
            if channel and message_ts:
                clean_ts = message_ts.replace(".", "")
                slack_message_url = f"https://slack.com/archives/{channel}/p{clean_ts}"
            
            print(f"DEBUG: Action details - action_id: {action_id}, value: {value}")
            print(f"DEBUG: Message details - ts: {message_ts}, channel: {channel}")
            print(f"DEBUG: Change info: {change_info}")
            
            if action_id == "approve_changes":
                print(f"DEBUG: Processing approve_changes action for file: {value}")
                # 승인 처리
                try:
                    # Google Sheets에 승인 기록
                    log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "document_path": value,
                        "change_type": "approved",
                        "change_keywords": json.dumps(change_info.get("keywords", []), ensure_ascii=False),
                        "chunks_plus": json.dumps([f"+{n}" for n in range(change_info.get("chunks", {}).get("added", 0))], ensure_ascii=False),
                        "chunks_minus": json.dumps([f"-{n}" for n in range(change_info.get("chunks", {}).get("removed", 0))], ensure_ascii=False),
                        "chunks_tilde": json.dumps([f"~{n}" for n in range(change_info.get("chunks", {}).get("modified", 0))], ensure_ascii=False),
                        "approved": True,
                        "comment": "승인됨",
                        "slack_message_url": slack_message_url
                    }
                    
                    print(f"DEBUG: Logging approval to sheet: {log_data}")
                    
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
                    if not send_block_message({"blocks": blocks}, channel=channel):
                        print("DEBUG: Failed to send approval message")
                    
                    return {"status": "ok", "message": "Changes approved"}
                    
                except Exception as e:
                    print(f"DEBUG: Error processing approval: {str(e)}")
                    return {"status": "error", "message": str(e)}
                    
            elif action_id == "request_revision":
                print(f"DEBUG: Processing request_revision action for file: {value}")
                # 수정 요청 처리
                try:
                    # Google Sheets에 수정 요청 기록
                    log_data = {
                        "timestamp": datetime.now().isoformat(),
                        "document_path": value,
                        "change_type": "revision_requested",
                        "change_keywords": json.dumps(change_info.get("keywords", []), ensure_ascii=False),
                        "chunks_plus": json.dumps([f"+{n}" for n in range(change_info.get("chunks", {}).get("added", 0))], ensure_ascii=False),
                        "chunks_minus": json.dumps([f"-{n}" for n in range(change_info.get("chunks", {}).get("removed", 0))], ensure_ascii=False),
                        "chunks_tilde": json.dumps([f"~{n}" for n in range(change_info.get("chunks", {}).get("modified", 0))], ensure_ascii=False),
                        "approved": False,
                        "comment": "수정 요청됨",
                        "slack_message_url": slack_message_url
                    }
                    
                    print(f"DEBUG: Logging revision request to sheet: {log_data}")
                    
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
                    if not send_block_message({"blocks": blocks}, channel=channel):
                        print("DEBUG: Failed to send revision request message")
                    
                    return {"status": "ok", "message": "Revision requested"}
                    
                except Exception as e:
                    print(f"DEBUG: Error processing revision request: {str(e)}")
                    return {"status": "error", "message": str(e)}
        
        print(f"DEBUG: Unhandled event type: {event_data.get('type')}")
        return {"status": "ok", "message": "Event processed"} 