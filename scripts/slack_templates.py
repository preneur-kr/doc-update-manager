import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from datetime import datetime
from scripts.sheet_logger import GOOGLE_DOC_LOG_SHEET_NAME

# Load environment variables
load_dotenv()
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def format_similarity_score(score: float) -> str:
    """유사도 점수를 퍼센트로 포맷팅합니다."""
    return f"{score * 100:.1f}%"

def get_sheet_url(sheet_name: str) -> str:
    """Google Sheets 문서 URL을 생성합니다."""
    return f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit#gid=0&range={sheet_name}"

def build_fallback_alert(
    question: str,
    gpt_response: str,
    displayed_answer: str,
    fallback_type: str,
    top_result: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fallback 알림을 위한 Block Kit 메시지를 구성합니다.
    
    Args:
        question (str): 사용자 질문
        gpt_response (str): GPT 원본 응답
        displayed_answer (str): 최종 표시된 응답
        fallback_type (str): fallback 유형 ("fallback" 또는 "fallback-like")
        top_result (Optional[Dict[str, Any]]): 최상위 검색 결과
        timestamp (Optional[str]): 타임스탬프 (기본값: 현재 시간)
        
    Returns:
        Dict[str, Any]: Block Kit 메시지 payload
    """
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 {fallback_type.upper()} 응답 감지",
                "emoji": True
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🙋 고객 질문:*\n{question}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🤖 GPT 원본 응답:*\n```\n{gpt_response}\n```"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📝 최종 표시 응답:*\n```\n{displayed_answer}\n```"
            }
        }
    ]

    if top_result:
        blocks.extend([
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🔍 최상위 검색 결과*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*섹션:*\n{top_result.get('section', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*카테고리:*\n{top_result.get('category', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*유사도:*\n{format_similarity_score(top_result.get('score', 0))}"
                    }
                ]
            }
        ])

    blocks.extend([
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📊 로그 확인:*\n<{get_sheet_url('fallback_logs')}|Google Sheets 로그 보기>"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"⏰ {timestamp}"
                }
            ]
        }
    ])

    return {
        "text": f"{fallback_type.upper()} 응답이 감지되었습니다",
        "blocks": blocks
    }

def build_doc_update_alert(
    file_path: str,
    updated_at: str,
    updated_keywords: List[str],
    added_chunks: int,
    removed_chunks: int,
    modified_chunks: int,
    change_details: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    문서 업데이트 알림을 위한 Block Kit 메시지를 구성합니다.
    
    Args:
        file_path (str): 업데이트된 문서 경로
        updated_at (str): 업데이트 시간
        updated_keywords (List[str]): 변경된 주요 키워드 목록
        added_chunks (int): 신규 청크 수
        removed_chunks (int): 삭제된 청크 수
        modified_chunks (int): 수정된 청크 수
        change_details (Dict[str, List[str]]): 변경 상세 정보
        
    Returns:
        Dict[str, Any]: Block Kit 메시지 payload
    """
    # 변경 상세 정보를 doc_update_logs 시트의 URL로 변경
    change_doc_url = get_sheet_url(GOOGLE_DOC_LOG_SHEET_NAME)
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📄 문서 변경 감지됨",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*🗂 문서:*\n`{file_path}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*🕒 업데이트:*\n`{updated_at}`"
                }
            ]
        }
    ]

    # 변경된 키워드가 있는 경우에만 표시
    if updated_keywords:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*📌 변경된 키워드:*\n{', '.join([f'*{keyword}*' for keyword in updated_keywords])}"
            }
        })

    # 청크 변경 통계를 한 줄로 표시
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*📊 변경 통계:*\n➕ {added_chunks}개 추가 | ➖ {removed_chunks}개 삭제 | ✏️ {modified_chunks}개 수정"
        }
    })

    # 변경 상세 정보 링크
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*📋 변경 상세 정보:*\n<{change_doc_url}|Google Sheets에서 확인하기>"
        }
    })

    # 승인/수정 요청 버튼 추가
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "✅ 변경 승인",
                    "emoji": True
                },
                "style": "primary",
                "action_id": "approve_changes",
                "value": file_path
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "🔄 수정 요청",
                    "emoji": True
                },
                "style": "danger",
                "action_id": "request_revision",
                "value": file_path
            }
        ]
    })

    return {
        "text": f"문서 변경이 감지되었습니다: {file_path}",
        "blocks": blocks
    } 