from pydantic_settings import BaseSettings
from pydantic import validator
from typing import Optional
import os

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_timeout: int = 30
    openai_max_retries: int = 3

    # Slack Configuration
    slack_bot_token: Optional[str] = None
    slack_signing_secret: Optional[str] = None
    slack_app_token: Optional[str] = None

    # Application Settings
    log_level: str = "INFO"
    debug: bool = False
    max_concurrent_requests: int = 5
    cache_ttl: int = 3600

    # Database
    database_url: str = "sqlite:///./slack_bot.db"

    @validator('openai_api_key')
    def validate_openai_key(cls, v):
        if not v or not v.startswith('sk-'):
            raise ValueError('Invalid OpenAI API key format')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
