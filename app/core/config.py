from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Hotel Bot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Slack settings
    SLACK_WEBHOOK_URL: str
    SLACK_DOCUPDATE_WEBHOOK_URL: str
    SLACK_SIGNING_SECRET: str
    SLACK_BOT_TOKEN: str
    
    # Google Sheets settings (scripts에서 사용)
    GOOGLE_SHEET_ID: str
    GOOGLE_CREDENTIALS_PATH: str
    GOOGLE_DOC_LOG_SHEET_NAME: str = "doc_update_logs"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    _settings = Settings()
    print(f"DEBUG: SLACK_SIGNING_SECRET loaded: {bool(_settings.SLACK_SIGNING_SECRET)}")
    print(f"DEBUG: SLACK_BOT_TOKEN loaded: {bool(_settings.SLACK_BOT_TOKEN)}")
    print(f"DEBUG: GOOGLE_SHEET_ID loaded: {bool(_settings.GOOGLE_SHEET_ID)}")
    print(f"DEBUG: GOOGLE_CREDENTIALS_PATH loaded: {bool(_settings.GOOGLE_CREDENTIALS_PATH)}")
    return _settings

settings = get_settings() 