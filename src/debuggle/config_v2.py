"""
⚙️ DEBUGGLE CONTROL CENTER - The Master Settings Dashboard! ⚙️

Think of this file as the "control room" of a spaceship or the settings menu
of your favorite video game! This is where we define ALL the knobs, switches,
and dials that control how Debuggle behaves in different situations.

🎯 WHAT THIS MODULE DOES:
This is the "brain" that remembers how Debuggle should behave. Just like how
you can adjust your phone's brightness, volume, and notifications, this file
lets us adjust Debuggle's behavior for different environments.

🏠 THE CONTROL ROOM ANALOGY:
- Environment: Like choosing "Home", "Work", or "Do Not Disturb" mode on your phone
- LogLevel: Like adjusting how much detail you want in notifications
- AnalysisSettings: Like tuning how thorough your spell-checker should be
- APISettings: Like setting speed limits and traffic rules for requests
- SecuritySettings: Like configuring your home security system

🔍 HOW CONFIGURATION WORKS:
1. We define what settings are available (like creating a settings menu)
2. We set sensible defaults (like factory settings on a new device)
3. We allow environment variables to override defaults (like user preferences)
4. We validate settings to prevent dangerous configurations (like safety checks)
5. We provide different "profiles" for different situations (dev, test, production)

Real-world analogy: This is like having different profiles on Netflix - 
"Kids Profile" has different rules than "Adult Profile", and "Travel Profile"
might have different download settings than "Home Profile"!
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
    """
    🌍 OPERATING ENVIRONMENTS - Where Is Debuggle Running?
    
    Think of these like different "locations" where Debuggle might be running.
    Just like you behave differently at home vs. at school vs. at work,
    Debuggle behaves differently in different environments!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like different "modes" on your phone:
    - DEVELOPMENT: "Do Not Disturb Off" - everything is loud and detailed for debugging
    - TESTING: "Focus Mode" - quiet and fast, only show important stuff
    - STAGING: "Work Mode" - practice for the real thing, but still safe to experiment
    - PRODUCTION: "Professional Mode" - quiet, secure, and reliable for real users
    """
    
    # 🏠 HOME BASE - where developers work and experiment
    # Like your bedroom where you can be messy and try new things
    DEVELOPMENT = "development"
    
    # 🧪 THE LAB - where we run automated tests
    # Like a science lab where we test theories before presenting them
    TESTING = "testing"
    
    # 🎭 DRESS REHEARSAL - practice run that's almost like the real thing
    # Like a rehearsal before the actual performance
    STAGING = "staging"
    
    # 🌟 THE BIG STAGE - where real users interact with Debuggle
    # Like performing on stage in front of a real audience
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """
    📢 VOLUME CONTROL - How Much Information Should We Show?
    
    Think of this like the volume setting on your phone or the detail level
    in a news app. Sometimes you want ALL the details, sometimes just the
    important stuff!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like choosing how much detail you want in notifications:
    - DEBUG: "Tell me EVERYTHING!" (even tiny details)
    - INFO: "Keep me informed" (general updates)
    - WARNING: "Only important stuff" (things I should know about)
    - ERROR: "Only problems" (things that went wrong)
    - CRITICAL: "EMERGENCY ONLY!" (system is broken)
    """
    
    # 🔍 MICROSCOPE MODE - show every tiny detail
    # Like having subtitles, commentary, and behind-the-scenes all on
    DEBUG = "DEBUG"
    
    # 📰 NEWSPAPER MODE - general information and updates
    # Like reading the main headlines and stories
    INFO = "INFO"
    
    # ⚠️ HEADS UP MODE - things you should probably know about
    # Like getting a "low battery" warning on your phone
    WARNING = "WARNING"
    
    # 🚨 PROBLEM ALERT - something went wrong
    # Like getting a "payment failed" notification
    ERROR = "ERROR"
    
    # 🆘 EMERGENCY BROADCAST - system is in serious trouble
    # Like a "system failure" message that needs immediate attention
    CRITICAL = "CRITICAL"


class AnalysisSettings(BaseSettings):
    """
    🔬 DETECTIVE LABORATORY SETTINGS - How Thorough Should Our Investigation Be?
    
    This controls how our error analysis "detective" works. Think of it like
    adjusting the settings on a high-tech crime lab - you can make it faster
    or more thorough, depending on what you need!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like adjusting the settings on your phone's camera:
    - Some settings make it faster but less detailed
    - Some settings make it slower but more accurate
    - Some settings help with storage and memory
    """
    
    # 🎯 ERROR PATTERN MATCHING - how many "suspects" should we check?
    # Like deciding how many people to interview in an investigation
    max_patterns_to_check: int = Field(default=100, description="Maximum patterns to check per analysis")
    
    # ⏰ INVESTIGATION TIME LIMIT - how long should we spend on pattern matching?
    # Like setting a timer for how long to spend on each case
    pattern_match_timeout: int = Field(default=5, description="Timeout for pattern matching (seconds)")
    
    # 🔍 FUZZY MATCHING - should we look for "close enough" matches?
    # Like asking "is this person similar to our suspect?" vs. "is this exactly our suspect?"
    enable_fuzzy_matching: bool = Field(default=False, description="Enable fuzzy pattern matching")
    
    # 📄 CONTEXT EXTRACTION - how much surrounding code should we look at?
    # Like deciding how much of the "crime scene" to photograph
    max_context_lines: int = Field(default=10, description="Maximum lines of code context to extract")
    
    # 📚 GIT HISTORY - should we check the version control history?
    # Like asking "what happened before this incident?" by checking security cameras
    enable_git_context: bool = Field(default=True, description="Enable git context extraction")
    
    # ⏱️ GIT TIMEOUT - how long to spend checking version history?
    # Like setting a time limit for reviewing security footage
    git_command_timeout: int = Field(default=10, description="Timeout for git commands (seconds)")
    
    # 🗣️ LANGUAGE DETECTION - should we try to figure out the programming language automatically?
    # Like having a translator who can identify what language someone is speaking
    enable_language_detection: bool = Field(default=True, description="Enable automatic language detection")
    
    # 🎯 CONFIDENCE THRESHOLD - how sure should we be before guessing the language?
    # Like saying "I'm 70% sure this is Spanish" (0.7 = 70% confidence)
    language_detection_confidence_threshold: float = Field(default=0.7, description="Minimum confidence for language detection")
    
    # 💾 RESULT CACHING - should we remember previous analysis results?
    # Like keeping a filing cabinet of previous cases to avoid re-doing work
    enable_caching: bool = Field(default=True, description="Enable result caching")
    
    # 🗓️ CACHE EXPIRATION - how long should we remember previous results?
    # Like deciding how long to keep old case files before archiving them
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
    """
    🎛️ MASTER CONTROL PANEL - The Main Dashboard for Everything!
    
    This is the "main settings screen" that contains all the primary controls
    for Debuggle. Think of it like the main settings app on your phone that
    has sections for WiFi, Bluetooth, Display, etc.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the main control panel in a car that has:
    - Basic info (speedometer, fuel gauge)
    - Environment controls (heat, AC, radio)
    - Safety settings (lights, wipers)
    - Advanced features (GPS, phone integration)
    
    This class is organized the same way - basic app info, environment settings,
    server configuration, and specialized sub-systems!
    """
    
    # 📋 CONFIGURATION INSTRUCTIONS - tells the system how to load settings
    # This is like telling your phone "look for settings in these places"
    model_config = SettingsConfigDict(
        env_file=".env",           # Look for a .env file with settings
        env_prefix="DEBUGGLE_",    # Environment variables should start with "DEBUGGLE_"
        case_sensitive=False       # Don't worry about uppercase vs lowercase
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
    🏪 THE SETTINGS FACTORY - Smart Settings Based on Where We're Running!
    
    This is like a smart function that automatically gives you the right
    settings for your situation. Think of it like a GPS that automatically
    switches between "walking", "driving", and "public transit" modes
    based on what you're doing.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a smart thermostat that automatically knows:
    - "Home mode" when you're at home (comfortable settings)
    - "Away mode" when you're gone (energy saving)
    - "Sleep mode" at night (quiet and dim)
    - "Party mode" when guests are over (optimal for groups)
    
    The @lru_cache() decorator means "remember the result so you don't
    have to figure it out again" - like remembering your favorite coffee order!
    
    Settings are determined by the DEBUGGLE_ENVIRONMENT variable:
    - development: DevelopmentSettings (loose and flexible for coding)
    - production: ProductionSettings (secure and stable for real users)
    - testing: TestingSettings (fast and quiet for automated tests)
    - default: Settings (basic settings if nothing else is specified)
    """
    # 🔍 CHECK THE ENVIRONMENT - what mode should we be in?
    # Like checking if you're at home, work, or school to adjust behavior
    env = os.getenv('DEBUGGLE_ENVIRONMENT', 'development').lower()
    
    # 🏠 DEVELOPMENT MODE - comfortable settings for programmers
    if env == 'development':
        return DevelopmentSettings()
    # 🌟 PRODUCTION MODE - secure settings for real users
    elif env == 'production':
        return ProductionSettings()
    # 🧪 TESTING MODE - fast settings for automated tests
    elif env == 'testing':
        return TestingSettings()
    # 🤷 DEFAULT MODE - fallback to development if we're not sure
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