from typing import Dict, Any, Optional, List
from datetime import datetime
from scripts.slack_templates import build_fallback_alert, build_doc_update_alert
from scripts.slack_sender import send_block_message, send_doc_update_message

class SlackAlertManager:
    """Slack 알림을 중앙에서 관리하는 클래스"""
    
    @staticmethod
    def send_fallback_alert(
        question: str,
        gpt_response: str,
        displayed_answer: str,
        fallback_type: str,
        top_result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Fallback 응답 알림을 전송합니다.
        
        Args:
            question (str): 사용자 질문
            gpt_response (str): GPT 원본 응답
            displayed_answer (str): 최종 표시된 응답
            fallback_type (str): fallback 유형 ("fallback" 또는 "fallback-like")
            top_result (Optional[Dict[str, Any]]): 최상위 검색 결과
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # Block Kit 메시지 구성
            payload = build_fallback_alert(
                question=question,
                gpt_response=gpt_response,
                displayed_answer=displayed_answer,
                fallback_type=fallback_type,
                top_result=top_result,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # 메시지 전송 (전용 채널 지정)
            return send_block_message(payload, channel="fallback-alerts")
            
        except Exception as e:
            print(f"❌ Fallback 알림 전송 중 오류 발생: {str(e)}")
            return False
    
    @staticmethod
    def send_doc_update_alert(
        file_path: str,
        updated_at: str,
        updated_keywords: List[str],
        added_chunks: int,
        removed_chunks: int,
        modified_chunks: int,
        change_details: Dict[str, List[str]]
    ) -> bool:
        """
        문서 업데이트 알림을 전송합니다.
        
        Args:
            file_path (str): 업데이트된 문서 경로
            updated_at (str): 업데이트 시간
            updated_keywords (List[str]): 변경된 주요 키워드 목록
            added_chunks (int): 신규 청크 수
            removed_chunks (int): 삭제된 청크 수
            modified_chunks (int): 수정된 청크 수
            change_details (Dict[str, List[str]]): 변경 상세 정보
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # Block Kit 메시지 구성
            payload = build_doc_update_alert(
                file_path=file_path,
                updated_at=updated_at,
                updated_keywords=updated_keywords,
                added_chunks=added_chunks,
                removed_chunks=removed_chunks,
                modified_chunks=modified_chunks,
                change_details=change_details
            )
            
            # 메시지 전송
            return send_doc_update_message(payload)
            
        except Exception as e:
            print(f"❌ 문서 업데이트 알림 전송 중 오류 발생: {str(e)}")
            return False
    
    @staticmethod
    def handle_button_action(action_id: str, value: str, file_path: str) -> bool:
        """
        버튼 액션을 처리합니다.
        
        Args:
            action_id (str): 액션 ID ("approve_changes" 또는 "request_revision")
            value (str): 액션 값
            file_path (str): 문서 경로
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            if action_id == "approve_changes":
                # 변경 승인 처리
                print(f"✅ 변경 승인됨: {file_path}")
                # TODO: 승인 처리 로직 구현
                return True
                
            elif action_id == "request_revision":
                # 수정 요청 처리
                print(f"🔄 수정 요청됨: {file_path}")
                # TODO: 수정 요청 처리 로직 구현
                return True
                
            else:
                print(f"⚠️ 알 수 없는 액션: {action_id}")
                return False
                
        except Exception as e:
            print(f"❌ 버튼 액션 처리 중 오류 발생: {str(e)}")
            return False 