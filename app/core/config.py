from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hotel Bot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Slack settings
    SLACK_SIGNING_SECRET: str
    SLACK_BOT_TOKEN: str
    SLACK_DEFAULT_CHANNEL: str = "general"
    
    # Google Sheets settings (scripts에서 사용)
    GOOGLE_SHEET_ID: str
    GOOGLE_CREDENTIALS_PATH: Optional[str] = None  # 선택적 필드로 변경
    GOOGLE_CREDENTIALS_JSON: Optional[str] = None  # 새로운 필드 추가
    GOOGLE_DOC_LOG_SHEET_NAME: str = "doc_update_logs"
    GOOGLE_CHAT_LOG_SHEET_NAME: str
    GOOGLE_FALLBACK_LOG_SHEET_NAME: str
    
    # OpenAI settings
    OPENAI_API_KEY: str
    
    # Pinecone settings
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX_NAME: str
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # 추가 필드 허용
    }

@lru_cache()
def get_settings():
    _settings = Settings()
    print(f"DEBUG: SLACK_SIGNING_SECRET loaded: {bool(_settings.SLACK_SIGNING_SECRET)}")
    print(f"DEBUG: SLACK_BOT_TOKEN loaded: {bool(_settings.SLACK_BOT_TOKEN)}")
    print(f"DEBUG: GOOGLE_SHEET_ID loaded: {bool(_settings.GOOGLE_SHEET_ID)}")
    print(f"DEBUG: GOOGLE_CREDENTIALS_PATH loaded: {bool(_settings.GOOGLE_CREDENTIALS_PATH)}")
    print(f"DEBUG: GOOGLE_CREDENTIALS_JSON loaded: {bool(_settings.GOOGLE_CREDENTIALS_JSON)}")
    return _settings

settings = get_settings() 