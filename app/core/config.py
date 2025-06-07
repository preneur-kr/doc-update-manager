from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Google Sheets
    GOOGLE_SHEET_ID: str
    GOOGLE_CREDENTIALS_PATH: str
    GOOGLE_DOC_LOG_SHEET_NAME: str = "doc_update_logs"
    GOOGLE_CHAT_LOG_SHEET_NAME: str = "chat_logs"
    GOOGLE_FALLBACK_LOG_SHEET_NAME: str = "fallback_logs"
    
    # Slack
    SLACK_WEBHOOK_URL: str
    SLACK_DOCUPDATE_WEBHOOK_URL: str
    SLACK_SIGNING_SECRET: str  # Slack App의 Signing Secret
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX_NAME: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 