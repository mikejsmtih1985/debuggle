"""
Enhanced configuration management for Debuggle.

Provides environment-specific settings, validation, and dynamic configuration
updates for different deployment scenarios.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from enum import Enum


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AnalysisSettings(BaseSettings):
    """Settings for error analysis engine."""
    
    # Error pattern matching
    max_patterns_to_check: int = Field(default=100, description="Maximum patterns to check per analysis")
    pattern_match_timeout: int = Field(default=5, description="Timeout for pattern matching (seconds)")
    enable_fuzzy_matching: bool = Field(default=False, description="Enable fuzzy pattern matching")
    
    # Context extraction
    max_context_lines: int = Field(default=10, description="Maximum lines of code context to extract")
    enable_git_context: bool = Field(default=True, description="Enable git context extraction")
    git_command_timeout: int = Field(default=10, description="Timeout for git commands (seconds)")
    
    # Language detection
    enable_language_detection: bool = Field(default=True, description="Enable automatic language detection")
    language_detection_confidence_threshold: float = Field(default=0.7, description="Minimum confidence for language detection")
    
    # Performance
    enable_caching: bool = Field(default=True, description="Enable result caching")
    cache_ttl_seconds: int = Field(default=300, description="Cache TTL in seconds")


class APISettings(BaseSettings):
    """Settings for API behavior."""
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=100, description="Requests per minute per IP")
    rate_limit_per_hour: int = Field(default=1000, description="Requests per hour per IP")
    burst_rate_limit: int = Field(default=10, description="Burst requests allowed")
    
    # Request limits  
    max_log_size: int = Field(default=100000, description="Maximum log size in characters")
    max_lines: int = Field(default=1000, description="Default maximum lines to process")
    max_lines_limit: int = Field(default=5000, description="Hard limit for maximum lines")
    max_file_size: int = Field(default=1048576, description="Maximum file upload size (1MB)")
    
    # Request timeout
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_methods: List[str] = Field(default=["GET", "POST"], description="Allowed CORS methods")


class SecuritySettings(BaseSettings):
    """Security-related settings."""
    
    # API Keys
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    api_key_header: str = Field(default="X-API-Key", description="Header name for API key")
    
    # Input validation
    enable_input_sanitization: bool = Field(default=True, description="Enable input sanitization")
    blocked_patterns: List[str] = Field(
        default=[r"<script", r"javascript:", r"data:"],
        description="Patterns to block in input"
    )
    
    # Privacy
    enable_telemetry: bool = Field(default=False, description="Enable anonymous telemetry")
    log_sensitive_data: bool = Field(default=False, description="Whether to log potentially sensitive data")


class DatabaseSettings(BaseSettings):
    """Database configuration (for future use)."""
    
    # Database connection
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    enable_database: bool = Field(default=False, description="Enable database features")
    
    # Connection pool
    max_connections: int = Field(default=10, description="Maximum database connections")
    connection_timeout: int = Field(default=30, description="Database connection timeout")


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DEBUGGLE_",
        case_sensitive=False
    )
    
    # Application metadata
    app_name: str = Field(default="Debuggle Core", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    app_description: str = Field(
        default="🐞 Professional error analysis that beats copy-pasting into ChatGPT",
        description="Application description"
    )
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload")
    workers: int = Field(default=1, description="Number of worker processes")
    
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    enable_file_logging: bool = Field(default=False, description="Enable file logging")
    log_format: str = Field(default="detailed", description="Log format style")
    
    # Feature flags
    enable_summarization: bool = Field(default=True, description="Enable error summarization")
    enable_context_extraction: bool = Field(default=True, description="Enable context extraction")
    enable_web_interface: bool = Field(default=True, description="Enable web interface")
    enable_metrics: bool = Field(default=False, description="Enable metrics collection")
    
    # Nested settings
    analysis: AnalysisSettings = Field(default_factory=AnalysisSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    
    @field_validator('environment', mode='before')
    @classmethod
    def validate_environment(cls, v):
        """Validate and normalize environment value."""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator('debug', mode='before')
    @classmethod 
    def validate_debug(cls, v, info):
        """Set debug based on environment if not explicitly set."""
        if v is None:
            env = info.data.get('environment', Environment.DEVELOPMENT)
            return env in [Environment.DEVELOPMENT, Environment.TESTING]
        return v

    @field_validator('log_level', mode='before')
    @classmethod
    def validate_log_level(cls, v, info):
        """Set log level based on debug flag if not explicitly set."""
        if v is None:
            debug = info.data.get('debug', False)
            if debug is None:
                env = info.data.get('environment', Environment.DEVELOPMENT)
                debug = env in [Environment.DEVELOPMENT, Environment.TESTING]
            return LogLevel.DEBUG if debug else LogLevel.INFO
        return v.upper() if isinstance(v, str) else v    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary."""
        return {
            'level': self.log_level.value,
            'log_file': self.log_file,
            'enable_console': True,
            'enable_file': self.enable_file_logging,
            'log_format': self.log_format
        }


class DevelopmentSettings(Settings):
    """Development-specific settings."""
    
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: LogLevel = LogLevel.DEBUG
    reload: bool = True
    
    # More permissive limits for development
    api: APISettings = APISettings(
        rate_limit_per_minute=1000,
        max_log_size=500000,  # 500KB
        max_lines_limit=10000
    )
    
    # Enable all features for development
    enable_summarization: bool = True
    enable_context_extraction: bool = True
    enable_web_interface: bool = True
    enable_metrics: bool = True


class ProductionSettings(Settings):
    """Production-specific settings."""
    
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    reload: bool = False
    workers: int = Field(default=4, description="Number of worker processes for production")
    
    # Conservative limits for production
    api: APISettings = APISettings(
        rate_limit_per_minute=100,
        rate_limit_per_hour=1000,
        max_log_size=100000,  # 100KB
        max_lines_limit=5000,
        cors_origins=[]  # Restrictive CORS in production
    )
    
    # Security settings for production
    security: SecuritySettings = SecuritySettings(
        enable_input_sanitization=True,
        enable_telemetry=False,
        log_sensitive_data=False
    )
    
    # Enable file logging in production
    enable_file_logging: bool = True
    log_file: str = "logs/debuggle.log"


class TestingSettings(Settings):
    """Testing-specific settings."""
    
    environment: Environment = Environment.TESTING
    debug: bool = False
    log_level: LogLevel = LogLevel.ERROR
    
    # Fast settings for testing
    api: APISettings = APISettings(
        rate_limit_per_minute=10000,  # No rate limiting in tests
        request_timeout=5,
        max_log_size=100000,  # 100KB for testing
        max_lines_limit=5000  # 5000 lines for testing
    )
    
    analysis: AnalysisSettings = AnalysisSettings(
        pattern_match_timeout=1,
        git_command_timeout=2,
        enable_caching=False  # Disable caching in tests
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    Settings are determined by the DEBUGGLE_ENVIRONMENT variable:
    - development: DevelopmentSettings
    - production: ProductionSettings  
    - testing: TestingSettings
    - default: Settings
    """
    env = os.getenv('DEBUGGLE_ENVIRONMENT', 'development').lower()
    
    if env == 'development':
        return DevelopmentSettings()
    elif env == 'production':
        return ProductionSettings()
    elif env == 'testing':
        return TestingSettings()
    else:
        return Settings(environment=Environment.DEVELOPMENT)


def get_settings_for_env(environment: str) -> Settings:
    """Get settings for a specific environment."""
    env = environment.lower()
    
    if env == 'development':
        return DevelopmentSettings()
    elif env == 'production':
        return ProductionSettings()
    elif env == 'testing':
        return TestingSettings()
    else:
        return Settings(environment=Environment.DEVELOPMENT)


# Global settings instance
settings = get_settings()


# Configuration validation
def validate_settings(settings_instance: Settings) -> List[str]:
    """
    Validate settings and return list of warnings/errors.
    
    Args:
        settings_instance: Settings instance to validate
        
    Returns:
        List of validation messages
    """
    messages = []
    
    # Check for common misconfigurations
    if settings_instance.is_production:
        if settings_instance.debug:
            messages.append("WARNING: Debug mode is enabled in production")
        
        if not settings_instance.security.api_key:
            messages.append("WARNING: No API key configured for production")
        
        if "*" in settings_instance.api.cors_origins:
            messages.append("WARNING: Permissive CORS origins in production")
    
    # Check resource limits
    if settings_instance.api.max_log_size > 1000000:  # 1MB
        messages.append("WARNING: Large max_log_size may impact performance")
    
    if settings_instance.analysis.max_context_lines > 50:
        messages.append("WARNING: High max_context_lines may slow analysis")
    
    return messages