from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    app_name: str = "Debuggle Trace Level"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Processing limits
    max_log_size: int = 50000  # 50KB max log size
    max_lines: int = 1000      # Default max lines to process
    max_lines_limit: int = 5000 # Hard limit for max_lines parameter
    
    # Features
    enable_summarization: bool = True
    enable_language_detection: bool = True
    
    # Rate limiting (requests per minute)
    rate_limit_per_minute: int = 100
    
    # Optional API key for future monetization
    api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_prefix = "DEBUGGLE_"


# Global settings instance
settings = Settings()