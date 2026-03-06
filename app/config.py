"""
Configuration management using environment variables.
Copy .env.example to .env and fill in your values.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "GenAI Pulse Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./genai_pulse.db"

    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Scrapers
    ARXIV_MAX_RESULTS: int = 20
    HUGGINGFACE_MAX_RESULTS: int = 20
    REDDIT_MAX_RESULTS: int = 25
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "GenAIPulseBot/1.0"

    # Notifiers
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHANNEL_ID: Optional[str] = None

    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_CHANNEL: str = "#genai-updates"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "GenAI Pulse Bot <noreply@genai-pulse.bot>"

    # Schedule (cron expressions)
    FETCH_SCHEDULE: str = "0 */6 * * *"     # every 6 hours
    DIGEST_SCHEDULE: str = "0 9 * * *"       # daily at 9am UTC

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
