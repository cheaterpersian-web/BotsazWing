"""Application configuration settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Telegram Bot SaaS Platform"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database
    database_url: str = Field(env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis
    redis_url: str = Field(env="REDIS_URL")
    
    # Security
    secret_key: str = Field(env="SECRET_KEY")
    encryption_key: str = Field(env="ENCRYPTION_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = "HS256"
    
    # CORS
    allowed_origins: list[str] = Field(default=["http://localhost:3000"], env="ALLOWED_ORIGINS")
    
    # File Storage
    minio_endpoint: str = Field(env="MINIO_ENDPOINT")
    minio_access_key: str = Field(env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(env="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(default="telegram-bot-saas", env="MINIO_BUCKET_NAME")
    minio_secure: bool = Field(default=True, env="MINIO_SECURE")
    
    # Telegram Bot
    telegram_bot_token: str = Field(env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(default=None, env="TELEGRAM_WEBHOOK_URL")
    
    # Docker
    docker_host: str = Field(default="unix:///var/run/docker.sock", env="DOCKER_HOST")
    docker_network: str = Field(default="telegram-bot-saas", env="DOCKER_NETWORK")
    
    # Payment Settings
    bank_account_number: str = Field(env="BANK_ACCOUNT_NUMBER")
    crypto_wallet_address: str = Field(env="CRYPTO_WALLET_ADDRESS")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()