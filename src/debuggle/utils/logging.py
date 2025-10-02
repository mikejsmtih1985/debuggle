"""
Comprehensive logging configuration for Debuggle.

This module provides structured logging with different levels for development
and production environments.
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = False,
    log_format: str = "detailed"
) -> None:
    """
    Setup comprehensive logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if file logging enabled)
        enable_console: Whether to log to console
        enable_file: Whether to log to file
        log_format: Format style ('simple', 'detailed', 'json')
    """
    
    # Define log formats
    formats = {
        'simple': '%(levelname)s: %(message)s',
        'detailed': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        'development': '%(asctime)s | %(name)s:%(lineno)d | %(levelname)s | %(message)s',
        'json': {
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        }
    }
    
    # Choose format
    if log_format == 'json':
        log_formatter = formats['json']['format']
        formatter_class = formats['json'].get('class', 'logging.Formatter')
    else:
        log_formatter = formats.get(log_format, formats['detailed'])
        formatter_class = 'logging.Formatter'
    
    # Build logging configuration
    config: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': log_formatter,
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {},
        'loggers': {
            'debuggle': {
                'level': level,
                'handlers': [],
                'propagate': False
            },
            'app': {
                'level': level,
                'handlers': [],
                'propagate': False
            }
        },
        'root': {
            'level': level,
            'handlers': []
        }
    }
    
    # Add console handler
    if enable_console:
        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'level': level,
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        }
        config['loggers']['debuggle']['handlers'].append('console')
        config['loggers']['app']['handlers'].append('console')
        config['root']['handlers'].append('console')
    
    # Add file handler
    if enable_file and log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': level,
            'formatter': 'standard',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
        config['loggers']['debuggle']['handlers'].append('file')
        config['loggers']['app']['handlers'].append('file')
        config['root']['handlers'].append('file')
    
    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """
    Structured logger with context support for better debugging.
    """
    
    def __init__(self, name: str):
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def add_context(self, **kwargs) -> 'StructuredLogger':
        """Add context to all log messages."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        new_logger.logger = self.logger
        return new_logger
    
    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        full_message = self._format_message(message)
        self.logger.debug(full_message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        full_message = self._format_message(message)
        self.logger.info(full_message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        full_message = self._format_message(message)
        self.logger.warning(full_message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        full_message = self._format_message(message)
        self.logger.error(full_message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        full_message = self._format_message(message)
        self.logger.critical(full_message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with context."""
        full_message = self._format_message(message)
        self.logger.exception(full_message, **kwargs)


def setup_development_logging():
    """Setup logging optimized for development."""
    setup_logging(
        level="DEBUG",
        enable_console=True,
        enable_file=False,
        log_format="development"
    )


def setup_production_logging(log_file: str = "logs/debuggle.log"):
    """Setup logging optimized for production."""
    setup_logging(
        level="INFO",
        log_file=log_file,
        enable_console=True,
        enable_file=True,
        log_format="detailed"
    )


def setup_testing_logging():
    """Setup logging for testing (minimal output)."""
    setup_logging(
        level="ERROR",
        enable_console=False,
        enable_file=False
    )


# Performance logging decorator
def log_performance(logger: logging.Logger):
    """Decorator to log function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"{func.__name__} completed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
                raise
        
        return wrapper
    return decorator


# Request logging utilities for FastAPI
class RequestLogger:
    """Utility for logging HTTP requests."""
    
    def __init__(self, logger_name: str = "debuggle.requests"):
        self.logger = get_logger(logger_name)
    
    def log_request(self, method: str, path: str, status_code: int, duration: float, **context):
        """Log HTTP request with context."""
        message = f"{method} {path} - {status_code} - {duration:.4f}s"
        
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            message = f"{message} | {context_str}"
        
        if status_code >= 500:
            self.logger.error(message)
        elif status_code >= 400:
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def log_error(self, method: str, path: str, error: Exception, **context):
        """Log request error."""
        message = f"{method} {path} - ERROR: {error}"
        
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            message = f"{message} | {context_str}"
        
        self.logger.error(message, exc_info=True)