# backend/app/config/settings.py

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (and optionally a .env file).
    """

    CURRENT_TERM: str = "1404-1"

    # General app settings
    APP_NAME: str = "Course Registration System API"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # JWT / auth settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()