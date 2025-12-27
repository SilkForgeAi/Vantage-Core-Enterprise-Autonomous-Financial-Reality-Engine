"""Application configuration and settings."""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_model: str = "claude-3-5-sonnet-20241022"
    
    # Telegram
    telegram_bot_token: str
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./trading_agent.db"
    
    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    
    # Encryption
    encryption_key: str  # Must be 32-byte hex string
    
    # Exchange API Keys
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None
    bybit_api_key: Optional[str] = None
    bybit_api_secret: Optional[str] = None
    alpaca_api_key: Optional[str] = None
    alpaca_api_secret: Optional[str] = None
    
    # Agent Configuration
    max_execution_time_seconds: int = 10
    enable_live_trading: bool = False
    demo_mode: bool = False  # Use mock exchanges for demonstrations (no API keys needed)
    
    # Logging
    log_level: str = "INFO"
    audit_log_dir: str = "./audit_logs"
    
    # Performance
    max_concurrent_users: int = 5
    state_sync_interval_seconds: float = 0.5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

