"""
Self-monitoring system for Debuggle.
Captures and broadcasts Debuggle's own errors for meta-debugging during development.
"""

import logging
import traceback
import sys
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json

from .realtime import ConnectionManager


class DebugglerSelfMonitor:
    """Self-monitoring system for Debuggle's own errors."""
    
    def __init__(self, connection_manager: ConnectionManager, max_errors: int = 100):
        self.connection_manager = connection_manager
        self.max_errors = max_errors
        self.internal_errors: List[Dict[str, Any]] = []
        self.is_enabled = False
        
        # Set up logging capture
        self.setup_logging_capture()
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable or disable self-monitoring."""
        self.is_enabled = enabled
        
    def setup_logging_capture(self):
        """Set up logging to capture Debuggle's own errors."""
        # Create custom handler that captures logs
        class SelfMonitorHandler(logging.Handler):
            def __init__(self, monitor):
                super().__init__()
                self.monitor = monitor
            
            def emit(self, record):
                if record.levelno >= logging.ERROR and self.monitor.is_enabled:
                    self.monitor.capture_log_error(record)
        
        # Add handler to debuggle logger
        debuggle_logger = logging.getLogger('debuggle')
        self.log_handler = SelfMonitorHandler(self)
        debuggle_logger.addHandler(self.log_handler)
        
        # Also capture uvicorn errors
        uvicorn_logger = logging.getLogger('uvicorn.error')
        uvicorn_logger.addHandler(self.log_handler)
    
    def capture_log_error(self, record: logging.LogRecord):
        """Capture a logging error."""
        error_data = {
            'id': f'log_{datetime.now().timestamp()}',
            'timestamp': datetime.now().isoformat(),
            'source': 'logging',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'error_type': 'LogError'
        }
        
        if record.exc_info:
            error_data['traceback'] = ''.join(traceback.format_exception(*record.exc_info))
        
        self.add_internal_error(error_data)
    
    def capture_exception(self, exc: Exception, context: str = "unknown", request: Optional[Request] = None):
        """Capture an exception with context."""
        if not self.is_enabled:
            return
            
        error_data = {
            'id': f'exc_{datetime.now().timestamp()}',
            'timestamp': datetime.now().isoformat(),
            'source': 'exception',
            'context': context,
            'error_type': exc.__class__.__name__,
            'message': str(exc),
            'traceback': ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        }
        
        if request:
            error_data['method'] = request.method
            error_data['url'] = str(request.url)
            error_data['headers'] = str(dict(request.headers))
            error_data['client'] = request.client.host if request.client else "unknown"
        
        self.add_internal_error(error_data)
    
    def capture_api_error(self, endpoint: str, error: Exception, request_data: Any = None):
        """Capture API-specific errors."""
        if not self.is_enabled:
            return
            
        error_data = {
            'id': f'api_{datetime.now().timestamp()}',
            'timestamp': datetime.now().isoformat(),
            'source': 'api',
            'endpoint': endpoint,
            'error_type': error.__class__.__name__,
            'message': str(error),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        }
        
        if request_data:
            # Sanitize request data (remove sensitive info)
            sanitized_data = self.sanitize_data(request_data)
            error_data['request_data'] = sanitized_data
        
        self.add_internal_error(error_data)
    
    def sanitize_data(self, data: Any) -> Any:
        """Sanitize data to remove sensitive information."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in ['password', 'token', 'secret', 'key']):
                    sanitized[key] = '[REDACTED]'
                else:
                    sanitized[key] = self.sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str) and len(data) > 1000:
            return data[:1000] + "... [TRUNCATED]"
        else:
            return data
    
    def add_internal_error(self, error_data: Dict[str, Any]):
        """Add an internal error to the collection."""
        self.internal_errors.append(error_data)
        
        # Keep only the most recent errors
        if len(self.internal_errors) > self.max_errors:
            self.internal_errors = self.internal_errors[-self.max_errors:]
        
        # Broadcast to connected clients
        asyncio.create_task(self.broadcast_error(error_data))
    
    async def broadcast_error(self, error_data: Dict[str, Any]):
        """Broadcast error to WebSocket clients."""
        message = {
            'type': 'self_monitoring_error',
            'error': error_data,
            'meta': {
                'total_internal_errors': len(self.internal_errors),
                'monitoring_enabled': self.is_enabled
            }
        }
        
        await self.connection_manager.broadcast(json.dumps(message))
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of internal errors."""
        if not self.internal_errors:
            return {
                'total_errors': 0,
                'recent_errors': [],
                'error_types': {},
                'sources': {}
            }
        
        # Count error types
        error_types = {}
        sources = {}
        
        for error in self.internal_errors:
            error_type = error.get('error_type', 'Unknown')
            source = error.get('source', 'unknown')
            
            error_types[error_type] = error_types.get(error_type, 0) + 1
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_errors': len(self.internal_errors),
            'recent_errors': self.internal_errors[-10:],  # Last 10 errors
            'error_types': error_types,
            'sources': sources,
            'monitoring_enabled': self.is_enabled
        }
    
    def clear_errors(self):
        """Clear all internal errors."""
        self.internal_errors.clear()


class SelfMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to capture HTTP errors and exceptions."""
    
    def __init__(self, app, monitor: DebugglerSelfMonitor):
        super().__init__(app)
        self.monitor = monitor
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            
            # Log slow requests (> 2 seconds)
            if hasattr(request.state, 'start_time'):
                duration = datetime.now().timestamp() - request.state.start_time
                if duration > 2.0 and self.monitor.is_enabled:
                    self.monitor.add_internal_error({
                        'id': f'slow_{datetime.now().timestamp()}',
                        'timestamp': datetime.now().isoformat(),
                        'source': 'performance',
                        'error_type': 'SlowRequest',
                        'message': f'Slow request: {duration:.2f}s',
                        'method': request.method,
                        'url': str(request.url),
                        'duration': duration
                    })
            
            return response
            
        except Exception as exc:
            # Capture the exception
            self.monitor.capture_exception(exc, "middleware", request)
            
            # Re-raise to let FastAPI handle it
            raise
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add start time for performance monitoring
            scope["state"] = {"start_time": datetime.now().timestamp()}
        
        await super().__call__(scope, receive, send)


def setup_self_monitoring(app, connection_manager: ConnectionManager) -> DebugglerSelfMonitor:
    """Set up self-monitoring for the Debuggle application."""
    monitor = DebugglerSelfMonitor(connection_manager)
    
    # Add middleware
    app.add_middleware(SelfMonitoringMiddleware, monitor=monitor)
    
    # Add API endpoints for self-monitoring
    @app.get("/api/v1/self-monitor/status")
    async def get_self_monitor_status():
        """Get self-monitoring status and error summary."""
        return monitor.get_error_summary()
    
    @app.post("/api/v1/self-monitor/toggle")
    async def toggle_self_monitoring(request: dict):
        """Enable or disable self-monitoring."""
        enabled = request.get("enabled", True)
        monitor.enable_monitoring(enabled)
        
        return {
            "message": f"Self-monitoring {'enabled' if enabled else 'disabled'}",
            "enabled": enabled
        }
    
    @app.post("/api/v1/self-monitor/clear")
    async def clear_self_monitor_errors():
        """Clear all self-monitoring errors."""
        monitor.clear_errors()
        return {"message": "Self-monitoring errors cleared"}
    
    @app.post("/api/v1/self-monitor/test-error")
    async def test_self_monitoring():
        """Generate a test error for self-monitoring validation."""
        if monitor.is_enabled:
            try:
                # Intentionally cause an error
                raise ValueError("Test error for self-monitoring validation")
            except Exception as e:
                monitor.capture_exception(e, "test-endpoint")
                return {"message": "Test error generated and captured"}
        else:
            return {"message": "Self-monitoring is disabled"}
    
    return monitor