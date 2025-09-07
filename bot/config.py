"""Bot configuration settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class BotSettings(BaseSettings):
    """Bot settings."""
    
    # Bot Configuration
    bot_token: str = Field(env="TELEGRAM_BOT_TOKEN")
    webhook_url: Optional[str] = Field(default=None, env="TELEGRAM_WEBHOOK_URL")
    webhook_port: int = Field(default=8080, env="TELEGRAM_WEBHOOK_PORT")
    
    # Backend API
    api_base_url: str = Field(env="API_BASE_URL")
    api_token: str = Field(env="API_TOKEN")
    
    # Redis
    redis_url: str = Field(env="REDIS_URL")
    
    # Admin Configuration
    admin_telegram_ids: list[int] = Field(default=[], env="ADMIN_TELEGRAM_IDS")
    
    # Bot Settings
    max_bots_per_user: int = Field(default=10, env="MAX_BOTS_PER_USER")
    deployment_timeout: int = Field(default=300, env="DEPLOYMENT_TIMEOUT")
    
    # Payment Settings
    bank_account_number: str = Field(env="BANK_ACCOUNT_NUMBER")
    crypto_wallet_address: str = Field(env="CRYPTO_WALLET_ADDRESS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("admin_telegram_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [int(x) for x in v]
        # Accept single int or comma-separated string
        try:
            return [int(v)]
        except Exception:
            return [int(x.strip()) for x in str(v).split(",") if x.strip()]


# Global settings instance
settings = BotSettings()