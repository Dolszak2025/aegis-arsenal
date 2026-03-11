"""Application configuration management"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables"""

    # Application
    APP_NAME: str = "Aegis Arsenal"
    APP_VERSION: str = "1.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Server
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    # Database
    DATABASE_URL: Optional[str] = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/aegis_arsenal"
    )
    DATABASE_ECHO: bool = DEBUG  # Log SQL queries in debug mode
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))

    # API Configuration
    CORS_ALLOWED_ORIGINS: list = ["*"]  # Configure via environment
    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"

    # Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Monitoring & Observability
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Features
    ENABLE_SWAGGER: bool = os.getenv("ENABLE_SWAGGER", "True").lower() == "true"
    ENABLE_SPEED_INSIGHTS: bool = os.getenv("ENABLE_SPEED_INSIGHTS", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
