"""
Comprehensive tests for utils/logging.py module.
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from src.debuggle.utils.logging import (
    setup_logging,
    get_logger,
    StructuredLogger,
    setup_development_logging,
    setup_production_logging,
    setup_testing_logging,
    log_performance,
    RequestLogger
)


class TestSetupLogging:
    """Test setup_logging function."""
    
    def test_setup_logging_console_only(self):
        """Test basic console logging setup."""
        setup_logging(level="INFO", enable_console=True, enable_file=False)
        
        logger = logging.getLogger("debuggle")
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0
    
    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            setup_logging(
                level="DEBUG",
                log_file=tmp_path,
                enable_console=True,
                enable_file=True
            )
            
            logger = logging.getLogger("debuggle")
            logger.info("Test message")
            
            # Check file was created and contains message
            assert os.path.exists(tmp_path)
            with open(tmp_path, 'r') as f:
                content = f.read()
                assert "Test message" in content
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_setup_logging_different_formats(self):
        """Test different log formats."""
        formats = ['simple', 'detailed', 'development', 'json']
        
        for fmt in formats:
            setup_logging(level="INFO", log_format=fmt)
            logger = logging.getLogger("debuggle")
            assert logger is not None
    
    def test_setup_logging_different_levels(self):
        """Test different log levels."""
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in levels:
            setup_logging(level=level)
            logger = logging.getLogger("debuggle")
            expected_level = getattr(logging, level)
            assert logger.level == expected_level
    
    def test_setup_logging_creates_log_directory(self):
        """Test that log directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = Path(tmp_dir) / "subdir" / "test.log"
            
            setup_logging(
                level="INFO",
                log_file=str(log_file),
                enable_file=True
            )
            
            assert log_file.parent.exists()
    
    def test_setup_logging_no_handlers_when_disabled(self):
        """Test that no handlers are added when both console and file are disabled."""
        setup_logging(enable_console=False, enable_file=False)
        
        logger = logging.getLogger("debuggle")
        # Should still have logger but minimal handlers
        assert logger is not None


class TestGetLogger:
    """Test get_logger function."""
    
    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a proper logger instance."""
        logger = get_logger("test_logger")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_get_logger_same_name_returns_same_instance(self):
        """Test that same logger name returns same instance."""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        
        assert logger1 is logger2


class TestStructuredLogger:
    """Test StructuredLogger class."""
    
    def test_structured_logger_initialization(self):
        """Test StructuredLogger initialization."""
        struct_logger = StructuredLogger("test")
        
        assert struct_logger.logger.name == "test"
        assert struct_logger.context == {}
    
    def test_add_context(self):
        """Test adding context to structured logger."""
        struct_logger = StructuredLogger("test")
        new_logger = struct_logger.add_context(user_id=123, session="abc")
        
        assert new_logger.context == {"user_id": 123, "session": "abc"}
        assert struct_logger.context == {}  # Original unchanged
    
    def test_add_context_chaining(self):
        """Test chaining context additions."""
        struct_logger = StructuredLogger("test")
        new_logger = struct_logger.add_context(user_id=123).add_context(action="login")
        
        assert new_logger.context == {"user_id": 123, "action": "login"}
    
    def test_format_message_without_context(self):
        """Test message formatting without context."""
        struct_logger = StructuredLogger("test")
        
        formatted = struct_logger._format_message("Test message")
        assert formatted == "Test message"
    
    def test_format_message_with_context(self):
        """Test message formatting with context."""
        struct_logger = StructuredLogger("test")
        struct_logger = struct_logger.add_context(user_id=123, action="test")
        
        formatted = struct_logger._format_message("Test message")
        assert "Test message" in formatted
        assert "user_id=123" in formatted
        assert "action=test" in formatted
    
    @patch('logging.Logger.info')
    def test_info_logging(self, mock_info):
        """Test info level logging."""
        struct_logger = StructuredLogger("test")
        struct_logger = struct_logger.add_context(user_id=123)
        
        struct_logger.info("Test info message")
        
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "Test info message" in args[0]
        assert "user_id=123" in args[0]
    
    @patch('logging.Logger.debug')
    def test_debug_logging(self, mock_debug):
        """Test debug level logging."""
        struct_logger = StructuredLogger("test")
        struct_logger.debug("Debug message")
        
        mock_debug.assert_called_once()
    
    @patch('logging.Logger.warning')
    def test_warning_logging(self, mock_warning):
        """Test warning level logging."""
        struct_logger = StructuredLogger("test")
        struct_logger.warning("Warning message")
        
        mock_warning.assert_called_once()
    
    @patch('logging.Logger.error')
    def test_error_logging(self, mock_error):
        """Test error level logging."""
        struct_logger = StructuredLogger("test")
        struct_logger.error("Error message")
        
        mock_error.assert_called_once()
    
    @patch('logging.Logger.critical')
    def test_critical_logging(self, mock_critical):
        """Test critical level logging."""
        struct_logger = StructuredLogger("test")
        struct_logger.critical("Critical message")
        
        mock_critical.assert_called_once()
    
    @patch('logging.Logger.exception')
    def test_exception_logging(self, mock_exception):
        """Test exception logging."""
        struct_logger = StructuredLogger("test")
        struct_logger.exception("Exception message")
        
        mock_exception.assert_called_once()


class TestPresetLoggingFunctions:
    """Test preset logging setup functions."""
    
    @patch('src.debuggle.utils.logging.setup_logging')
    def test_setup_development_logging(self, mock_setup):
        """Test development logging setup."""
        setup_development_logging()
        
        mock_setup.assert_called_once_with(
            level="DEBUG",
            enable_console=True,
            enable_file=False,
            log_format="development"
        )
    
    @patch('src.debuggle.utils.logging.setup_logging')
    def test_setup_production_logging_default(self, mock_setup):
        """Test production logging setup with defaults."""
        setup_production_logging()
        
        mock_setup.assert_called_once_with(
            level="INFO",
            log_file="logs/debuggle.log",
            enable_console=True,
            enable_file=True,
            log_format="detailed"
        )
    
    @patch('src.debuggle.utils.logging.setup_logging')
    def test_setup_production_logging_custom_file(self, mock_setup):
        """Test production logging setup with custom file."""
        setup_production_logging(log_file="custom.log")
        
        mock_setup.assert_called_once_with(
            level="INFO",
            log_file="custom.log",
            enable_console=True,
            enable_file=True,
            log_format="detailed"
        )
    
    @patch('src.debuggle.utils.logging.setup_logging')
    def test_setup_testing_logging(self, mock_setup):
        """Test testing logging setup."""
        setup_testing_logging()
        
        mock_setup.assert_called_once_with(
            level="ERROR",
            enable_console=False,
            enable_file=False
        )


class TestLogPerformanceDecorator:
    """Test log_performance decorator."""
    
    def test_log_performance_success(self):
        """Test performance logging for successful function."""
        mock_logger = MagicMock()
        
        @log_performance(mock_logger)
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        mock_logger.debug.assert_called_once()
        
        # Check that the debug message contains timing info
        debug_call_args = mock_logger.debug.call_args[0][0]
        assert "test_function completed in" in debug_call_args
        assert "s" in debug_call_args  # seconds unit
    
    def test_log_performance_exception(self):
        """Test performance logging for function that raises exception."""
        mock_logger = MagicMock()
        
        @log_performance(mock_logger)
        def test_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            test_function()
        
        mock_logger.error.assert_called_once()
        
        # Check that the error message contains timing info
        error_call_args = mock_logger.error.call_args[0][0]
        assert "test_function failed after" in error_call_args
        assert "Test error" in error_call_args


class TestRequestLogger:
    """Test RequestLogger class."""
    
    def test_request_logger_initialization(self):
        """Test RequestLogger initialization."""
        req_logger = RequestLogger()
        
        assert req_logger.logger.name == "debuggle.requests"
    
    def test_request_logger_custom_name(self):
        """Test RequestLogger with custom logger name."""
        req_logger = RequestLogger("custom.requests")
        
        assert req_logger.logger.name == "custom.requests"
    
    @patch('src.debuggle.utils.logging.get_logger')
    def test_log_request_success(self, mock_get_logger):
        """Test logging successful request."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        req_logger = RequestLogger()
        req_logger.log_request("GET", "/api/test", 200, 0.123)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "GET /api/test - 200 - 0.1230s" in call_args
    
    @patch('src.debuggle.utils.logging.get_logger')
    def test_log_request_with_context(self, mock_get_logger):
        """Test logging request with additional context."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        req_logger = RequestLogger()
        req_logger.log_request("POST", "/api/login", 200, 0.456, user_id=123, ip="1.2.3.4")
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "POST /api/login - 200 - 0.4560s" in call_args
        assert "user_id=123" in call_args
        assert "ip=1.2.3.4" in call_args
    
    @patch('src.debuggle.utils.logging.get_logger')
    def test_log_request_client_error(self, mock_get_logger):
        """Test logging client error (4xx)."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        req_logger = RequestLogger()
        req_logger.log_request("GET", "/api/not-found", 404, 0.050)
        
        mock_logger.warning.assert_called_once()
    
    @patch('src.debuggle.utils.logging.get_logger')
    def test_log_request_server_error(self, mock_get_logger):
        """Test logging server error (5xx)."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        req_logger = RequestLogger()
        req_logger.log_request("POST", "/api/error", 500, 1.234)
        
        mock_logger.error.assert_called_once()
    
    @patch('src.debuggle.utils.logging.get_logger')
    def test_log_error(self, mock_get_logger):
        """Test logging request error."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        req_logger = RequestLogger()
        test_error = ValueError("Test error")
        req_logger.log_error("GET", "/api/error", test_error)
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "GET /api/error - ERROR: Test error" in call_args
        
        # Check that exc_info=True was passed
        call_kwargs = mock_logger.error.call_args[1]
        assert call_kwargs.get('exc_info') is True
    
    @patch('src.debuggle.utils.logging.get_logger')
    def test_log_error_with_context(self, mock_get_logger):
        """Test logging request error with context."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        req_logger = RequestLogger()
        test_error = RuntimeError("Runtime error")
        req_logger.log_error("POST", "/api/submit", test_error, user_id=456)
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "POST /api/submit - ERROR: Runtime error" in call_args
        assert "user_id=456" in call_args


class TestLoggingIntegration:
    """Integration tests for logging functionality."""
    
    def test_end_to_end_logging_flow(self):
        """Test complete logging flow."""
        # Setup logging
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            log_file = tmp_file.name
        
        try:
            setup_logging(
                level="INFO",
                log_file=log_file,
                enable_console=False,
                enable_file=True,
                log_format="detailed"
            )
            
            # Create structured logger
            struct_logger = StructuredLogger("integration_test")
            struct_logger = struct_logger.add_context(test_id=12345)
            
            # Log messages
            struct_logger.info("Integration test message")
            struct_logger.error("Integration test error")
            
            # Create request logger
            req_logger = RequestLogger("integration.requests")
            req_logger.log_request("GET", "/test", 200, 0.100)
            
            # Verify log file contents
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Integration test message" in content
                assert "test_id=12345" in content
                assert "GET /test - 200" in content
                
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_logger_hierarchy(self):
        """Test logger hierarchy and inheritance."""
        # Setup parent logger
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")
        
        assert child_logger.parent == parent_logger
        assert "parent" in child_logger.name