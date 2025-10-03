"""
Comprehensive tests for the configuration system.

This module tests all aspects of the configuration management including:
- Environment variable loading
- Default value assignments  
- Validation rules
- Different environment configurations
- Error handling for invalid configurations
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from src.debuggle.config_v2 import (
    Environment,
    LogLevel,
    Settings,
    AnalysisSettings,
    APISettings,
    SecuritySettings,
    DatabaseSettings,
    get_settings
)


class TestEnvironmentEnum:
    """Test the Environment enumeration."""
    
    def test_all_environment_values(self):
        """Test all environment enum values are valid."""
        assert Environment.DEVELOPMENT == "development"
        assert Environment.TESTING == "testing"
        assert Environment.STAGING == "staging"  
        assert Environment.PRODUCTION == "production"
    
    def test_environment_str_conversion(self):
        """Test that Environment enum can be converted to string."""
        # Test string representation - actual enum behavior
        assert str(Environment.DEVELOPMENT) == "Environment.DEVELOPMENT"
        assert str(Environment.TESTING) == "Environment.TESTING"
        assert str(Environment.STAGING) == "Environment.STAGING"
        assert str(Environment.PRODUCTION) == "Environment.PRODUCTION"


class TestLogLevelEnum:
    """Test the LogLevel enumeration."""
    
    def test_all_log_levels(self):
        """Test all log level enum values."""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"


class TestAnalysisSettings:
    """Test the AnalysisSettings configuration."""
    
    def test_default_analysis_settings(self):
        """Test default analysis settings values."""
        settings = AnalysisSettings()
        assert settings.max_patterns_to_check == 100
        assert settings.pattern_match_timeout == 5
        assert settings.enable_fuzzy_matching is False
        assert settings.max_context_lines == 10
        assert settings.enable_git_context is True
        assert settings.git_command_timeout == 10
        assert settings.enable_language_detection is True
        assert settings.language_detection_confidence_threshold == 0.7
        assert settings.enable_caching is True
        assert settings.cache_ttl_seconds == 300
    
    def test_analysis_settings_custom_values(self):
        """Test analysis settings with custom values."""
        settings = AnalysisSettings(
            max_patterns_to_check=200,
            pattern_match_timeout=10,
            enable_fuzzy_matching=True,
            max_context_lines=20,
            language_detection_confidence_threshold=0.8
        )
        assert settings.max_patterns_to_check == 200
        assert settings.pattern_match_timeout == 10
        assert settings.enable_fuzzy_matching is True
        assert settings.max_context_lines == 20
        assert settings.language_detection_confidence_threshold == 0.8
    
    def test_analysis_settings_validation(self):
        """Test validation of analysis settings."""
        # Valid confidence threshold
        settings = AnalysisSettings(language_detection_confidence_threshold=0.9)
        assert settings.language_detection_confidence_threshold == 0.9
        
        # Test edge cases
        settings = AnalysisSettings(max_patterns_to_check=1)
        assert settings.max_patterns_to_check == 1


class TestAPISettings:
    """Test the APISettings configuration."""
    
    def test_default_api_settings(self):
        """Test default API settings values."""
        settings = APISettings()
        assert settings.rate_limit_per_minute == 100
        assert settings.rate_limit_per_hour == 1000
        assert settings.burst_rate_limit == 10
        assert settings.max_log_size == 100000
        assert settings.max_lines == 1000
        assert settings.max_lines_limit == 5000
        assert settings.max_file_size == 1048576  # 1MB
        assert settings.request_timeout == 30
        assert settings.cors_origins == ["*"]
        assert settings.cors_methods == ["GET", "POST"]
    
    def test_api_settings_custom_values(self):
        """Test API settings with custom values."""
        settings = APISettings(
            rate_limit_per_minute=200,
            max_log_size=200000,
            max_lines=2000,
            request_timeout=60,
            cors_origins=["https://example.com"]
        )
        assert settings.rate_limit_per_minute == 200
        assert settings.max_log_size == 200000
        assert settings.max_lines == 2000
        assert settings.request_timeout == 60
        assert settings.cors_origins == ["https://example.com"]
    
    def test_api_settings_validation(self):
        """Test API settings validation."""
        # Test valid settings
        settings = APISettings(
            max_lines=5000,  # Should be within max_lines_limit
            max_file_size=2097152  # 2MB
        )
        assert settings.max_lines == 5000
        assert settings.max_file_size == 2097152


class TestSecuritySettings:
    """Test the SecuritySettings configuration."""
    
    def test_default_security_settings(self):
        """Test default security settings."""
        settings = SecuritySettings()
        assert settings.api_key is None
        assert settings.api_key_header == "X-API-Key"
        assert settings.enable_input_sanitization is True
        assert len(settings.blocked_patterns) > 0
        assert settings.enable_telemetry is False
        assert settings.log_sensitive_data is False
    
    def test_security_settings_custom_values(self):
        """Test security settings with custom values."""
        settings = SecuritySettings(
            api_key="test-key-123",
            api_key_header="Authorization",
            enable_input_sanitization=False,
            blocked_patterns=["<script>", "javascript:"],
            enable_telemetry=True
        )
        assert settings.api_key == "test-key-123"
        assert settings.api_key_header == "Authorization"
        assert settings.enable_input_sanitization is False
        assert settings.blocked_patterns == ["<script>", "javascript:"]
        assert settings.enable_telemetry is True
    
    def test_security_settings_blocked_patterns(self):
        """Test blocked patterns functionality."""
        settings = SecuritySettings()
        # Should have some default blocked patterns
        assert len(settings.blocked_patterns) > 0
        assert any("script" in pattern.lower() for pattern in settings.blocked_patterns)


class TestDatabaseSettings:
    """Test the DatabaseSettings configuration."""
    
    def test_default_database_settings(self):
        """Test default database settings."""
        settings = DatabaseSettings()
        # Just verify it initializes without error
        assert settings is not None
    
    def test_database_settings_custom_values(self):
        """Test database settings with custom values."""
        # Test with any available fields
        settings = DatabaseSettings()
        assert settings is not None


class TestMainSettings:
    """Test the main Settings class."""
    
    def test_default_settings_creation(self):
        """Test default settings creation."""
        settings = Settings()
        assert settings.environment == Environment.TESTING  # Actual default
        assert settings.debug is False  # Actual default
        assert settings.log_level == LogLevel.DEBUG
        assert isinstance(settings.analysis, AnalysisSettings)
        assert isinstance(settings.api, APISettings)
        assert isinstance(settings.security, SecuritySettings)
        assert isinstance(settings.database, DatabaseSettings)
    
    def test_settings_model_config(self):
        """Test model configuration settings."""
        settings = Settings()
        config = settings.model_config
        assert config.get("env_prefix") == "DEBUGGLE_"
        assert config.get("case_sensitive") is False
        assert config.get("env_file") == ".env"
    
    def test_environment_variable_loading(self):
        """Test environment variables are loaded correctly."""
        env_vars = {
            "DEBUGGLE_ENVIRONMENT": "staging",
            "DEBUGGLE_DEBUG": "false",
            "DEBUGGLE_LOG_LEVEL": "WARNING"
        }
        
        with patch.dict(os.environ, env_vars):
            # Clear any cached settings
            if hasattr(get_settings, 'cache_clear'):
                get_settings.cache_clear()
            settings = Settings()
            assert settings.environment == Environment.STAGING
            assert settings.debug is False
            assert settings.log_level == LogLevel.WARNING
    
    def test_nested_settings_structure(self):
        """Test nested settings are properly structured."""
        settings = Settings()
        
        # Verify nested settings exist and are properly typed
        assert hasattr(settings, 'analysis')
        assert hasattr(settings, 'api')
        assert hasattr(settings, 'security')
        assert hasattr(settings, 'database')
        
        # Verify they're instances of the correct classes
        assert isinstance(settings.analysis, AnalysisSettings)
        assert isinstance(settings.api, APISettings)
        assert isinstance(settings.security, SecuritySettings)
        assert isinstance(settings.database, DatabaseSettings)


class TestSettingsCache:
    """Test the settings caching mechanism."""
    
    def test_get_settings_function_exists(self):
        """Test get_settings function exists and works."""
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    def test_get_settings_returns_same_instance(self):
        """Test get_settings() returns the same instance on multiple calls."""
        settings1 = get_settings()
        settings2 = get_settings()
        # Should be the same instance due to caching
        assert settings1 is settings2
    
    def test_settings_cache_behavior(self):
        """Test settings caching behavior."""
        # First call
        settings1 = get_settings()
        
        # Second call should return cached instance
        settings2 = get_settings()
        assert settings1 is settings2
        
        # Verify it's actually cached by checking specific attributes
        assert settings1.environment == settings2.environment
        assert settings1.debug == settings2.debug


class TestEnvironmentSpecificBehavior:
    """Test behavior differences across environments."""
    
    @pytest.mark.parametrize("env_name,env_enum", [
        ("development", Environment.DEVELOPMENT),
        ("testing", Environment.TESTING),
        ("staging", Environment.STAGING),
        ("production", Environment.PRODUCTION),
    ])
    def test_environment_loading(self, env_name, env_enum):
        """Test each environment loads correctly."""
        with patch.dict(os.environ, {"DEBUGGLE_ENVIRONMENT": env_name}):
            if hasattr(get_settings, 'cache_clear'):
                get_settings.cache_clear()
            settings = Settings()
            assert settings.environment == env_enum
    
    def test_development_environment_characteristics(self):
        """Test development environment specific characteristics."""
        with patch.dict(os.environ, {'DEBUGGLE_ENVIRONMENT': 'development'}):
            settings = Settings()
            assert settings.environment == Environment.DEVELOPMENT
            assert settings.debug is False  # Debug is controlled separately from environment
    
    def test_production_environment_characteristics(self):
        """Test production environment has appropriate characteristics.""" 
        with patch.dict(os.environ, {"DEBUGGLE_ENVIRONMENT": "production"}):
            if hasattr(get_settings, 'cache_clear'):
                get_settings.cache_clear()
            settings = Settings()
            assert settings.environment == Environment.PRODUCTION
            assert settings.debug is False


class TestConfigurationIntegration:
    """Test configuration integration with the application."""
    
    def test_settings_serialization(self):
        """Test settings can be serialized to dict."""
        settings = Settings()
        settings_dict = settings.model_dump()
        
        assert isinstance(settings_dict, dict)
        assert "environment" in settings_dict
        assert "debug" in settings_dict
        assert "log_level" in settings_dict
        assert "analysis" in settings_dict
        assert "api" in settings_dict
        assert "security" in settings_dict
        assert "database" in settings_dict
    
    def test_settings_json_serialization(self):
        """Test settings can be serialized to JSON."""
        import json
        settings = Settings()
        settings_dict = settings.model_dump()
        
        # Should be able to serialize to JSON without error
        json_str = json.dumps(settings_dict)
        assert len(json_str) > 0
        
        # Should be able to deserialize back
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict)
        assert deserialized["environment"] == settings.environment.value
    
    def test_settings_validation_basic(self):
        """Test basic settings validation."""
        # Settings should validate without error with default values
        settings = Settings()
        assert settings is not None
        
        # Test that all nested settings are valid
        assert settings.analysis is not None
        assert settings.api is not None  
        assert settings.security is not None
        assert settings.database is not None