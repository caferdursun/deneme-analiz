"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # App Info
    APP_NAME: str = "Deneme Analiz"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = "sqlite:///./deneme_analiz.db"

    # Claude API
    ANTHROPIC_API_KEY: str = ""  # Will be required when PDF analysis is used

    # Security
    SECRET_KEY: str = "change-this-in-production"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # File Storage
    PDF_STORAGE_PATH: str = "./data"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
