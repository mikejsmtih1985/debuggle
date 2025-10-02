from pydantic_settings import BaseSettings, SettingsConfigDict  
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DEBUGGLE_"
    )
    
    # Application metadata
    app_name: str = "Debuggle Core"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Processing limits
    max_log_size: int = 50000
    max_lines: int = 1000
    max_lines_limit: int = 5000
    
    # Feature flags
    enable_summarization: bool = True
    enable_language_detection: bool = True
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    
    # Optional API key for future monetization
    api_key: Optional[str] = None


# Global settings instance
settings = Settings()