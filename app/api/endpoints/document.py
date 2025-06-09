from fastapi import APIRouter, HTTPException
from scripts.sheet_logger import log_to_sheet
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import json

router = APIRouter()

# 요청 모델 정의
class DocumentUpdate(BaseModel):
    document_path: str
    change_type: str
    change_keywords: List[str]
    chunks_plus: Optional[List[str]] = []
    chunks_minus: Optional[List[str]] = []
    chunks_tilde: Optional[List[str]] = []
    approved: Optional[bool] = False
    comment: Optional[str] = ""
    slack_message_url: Optional[str] = ""

@router.post("/logs/document-update")
async def log_document_update(request: DocumentUpdate):
    """
    문서 업데이트를 로깅합니다.
    """
    try:
        print(f"Received request: {request.dict()}")
        
        # 로그 데이터 준비
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "document_path": request.document_path,
            "change_type": request.change_type,
            "change_keywords": json.dumps(request.change_keywords, ensure_ascii=False),
            "chunks_plus": json.dumps(request.chunks_plus, ensure_ascii=False),
            "chunks_minus": json.dumps(request.chunks_minus, ensure_ascii=False),
            "chunks_tilde": json.dumps(request.chunks_tilde, ensure_ascii=False),
            "approved": request.approved,
            "comment": request.comment,
            "slack_message_url": request.slack_message_url
        }
        
        # scripts/sheet_logger.py의 log_to_sheet 사용
        if not log_to_sheet(log_data):
            raise HTTPException(status_code=500, detail="Failed to log to sheet")
        
        return {
            "status": "success",
            "message": "Document update logged successfully",
            "logged_data": {
                "document_path": request.document_path,
                "change_type": request.change_type,
                "timestamp": log_data["timestamp"]
            }
        }
        
    except Exception as e:
        print(f"Error in log_document_update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 