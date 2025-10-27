"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


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

    # YouTube Data API
    YOUTUBE_API_KEY: Optional[str] = None  # For resource recommendations

    # Security
    SECRET_KEY: str = "change-this-in-production"

    # CORS - Can be overridden in .env as comma-separated string
    CORS_ORIGINS_STR: Optional[str] = None

    # File Storage
    PDF_STORAGE_PATH: str = "./data"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from string or return defaults"""
        if self.CORS_ORIGINS_STR:
            return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        return ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = "../.env"  # .env is in parent directory
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
