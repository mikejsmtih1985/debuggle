"""
Real-time error monitoring and WebSocket broadcasting service.

This module provides:
- WebSocket endpoint for real-time error streaming
- Error event broadcasting to connected clients
- Error monitoring service for live updates
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time error broadcasting."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Optional[Dict[str, Any]] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(),
            "client_info": client_info or {},
            "message_count": 0
        }
        logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(message)
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]["message_count"] += 1
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        logger.info(f"Broadcasting message to {len(self.active_connections)} connections")
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                if connection in self.connection_metadata:
                    self.connection_metadata[connection]["message_count"] += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections."""
        return {
            "total_connections": len(self.active_connections),
            "connections": [
                {
                    "connected_at": metadata["connected_at"].isoformat(),
                    "message_count": metadata["message_count"],
                    "client_info": metadata["client_info"]
                }
                for metadata in self.connection_metadata.values()
            ]
        }


class ErrorEvent:
    """Represents a real-time error event."""
    
    def __init__(self, error_type: str, message: str, source: str = "unknown", 
                 severity: str = "error", metadata: Optional[Dict[str, Any]] = None):
        self.id = f"error_{int(time.time() * 1000)}"
        self.timestamp = datetime.now()
        self.error_type = error_type
        self.message = message
        self.source = source
        self.severity = severity
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error event to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "error_type": self.error_type,
            "message": self.message,
            "source": self.source,
            "severity": self.severity,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert error event to JSON string."""
        return json.dumps(self.to_dict())


class RealtimeErrorMonitor:
    """Service for monitoring and broadcasting errors in real-time."""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.error_history: List[ErrorEvent] = []
        self.max_history_size = 1000
        self.monitoring_enabled = True
    
    async def report_error(self, error_type: str, message: str, source: str = "api",
                          severity: str = "error", metadata: Optional[Dict[str, Any]] = None):
        """Report a new error and broadcast it to connected clients."""
        if not self.monitoring_enabled:
            return
        
        error_event = ErrorEvent(error_type, message, source, severity, metadata)
        
        # Add to history
        self.error_history.append(error_event)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
        
        # Broadcast to connected clients
        await self.connection_manager.broadcast(error_event.to_json())
        
        logger.info(f"Reported error: {error_type} - {message}")
    
    async def report_log_processing_error(self, log_content: str, error: Exception, 
                                        processing_metadata: Optional[Dict[str, Any]] = None):
        """Report an error that occurred during log processing."""
        metadata = processing_metadata or {}
        metadata.update({
            "log_content_preview": log_content[:200] + "..." if len(log_content) > 200 else log_content,
            "exception_type": type(error).__name__,
            "exception_details": str(error)
        })
        
        await self.report_error(
            error_type="LogProcessingError",
            message=f"Failed to process log: {str(error)}",
            source="log_processor",
            severity="error",
            metadata=metadata
        )
    
    async def report_system_event(self, event_type: str, message: str, 
                                 metadata: Optional[Dict[str, Any]] = None):
        """Report a system event (not necessarily an error)."""
        await self.report_error(
            error_type=event_type,
            message=message,
            source="system",
            severity="info",
            metadata=metadata
        )
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent error events."""
        recent_errors = self.error_history[-limit:] if limit > 0 else self.error_history
        return [error.to_dict() for error in recent_errors]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self.error_history:
            return {
                "total_errors": 0,
                "error_types": {},
                "severity_breakdown": {},
                "sources": {}
            }
        
        error_types = {}
        severity_breakdown = {}
        sources = {}
        
        for error in self.error_history:
            # Count error types
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            
            # Count severity levels
            severity_breakdown[error.severity] = severity_breakdown.get(error.severity, 0) + 1
            
            # Count sources
            sources[error.source] = sources.get(error.source, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "severity_breakdown": severity_breakdown,
            "sources": sources,
            "monitoring_enabled": self.monitoring_enabled
        }
    
    def toggle_monitoring(self, enabled: bool):
        """Enable or disable error monitoring."""
        self.monitoring_enabled = enabled
        logger.info(f"Error monitoring {'enabled' if enabled else 'disabled'}")


# Global instances
connection_manager = ConnectionManager()
error_monitor = RealtimeErrorMonitor(connection_manager)