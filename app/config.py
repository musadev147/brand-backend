"""
Brand Bridge (CreatorHub AI) — App Configuration
Loads settings from .env file using pydantic-settings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "BrandBridge"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./brand_bridge.db"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # OTP
    OTP_EXPIRE_MINUTES: int = 10

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Email (Resend)
    RESEND_API_KEY: str = "re_abzMSrT5..." # Provide a default but it will be loaded from .env
    FROM_EMAIL: str = "onboarding@resend.dev"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — loads .env once."""
    return Settings()
