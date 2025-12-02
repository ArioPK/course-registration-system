# backend/app/config/settings.py

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict # type: ignore


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (and optionally a .env file).

    All attributes here can be configured via environment variables.
    """

    # General app settings
    APP_NAME: str = "Course Registration System API"
    DEBUG: bool = True  # You can set DEBUG=false in production

    # Database
    DATABASE_URL: str  # e.g. mysql+pymysql://user:password@localhost:3306/course_registration_db

    # JWT / auth settings
    JWT_SECRET_KEY: str  # e.g. a long random string
    JWT_ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",             # Load variables from .env in development
        env_file_encoding="utf-8",
        extra="ignore",              # Ignore unknown env vars instead of raising
    )


# Singleton-style settings object used throughout the app
settings = Settings()
