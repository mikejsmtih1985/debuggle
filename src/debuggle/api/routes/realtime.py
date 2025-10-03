"""
📡 Hospital Real-Time Communication Department - WebSocket Routes

This is the real-time communication department of our hospital! Just like how a real 
hospital has intercoms, paging systems, and emergency broadcast networks for instant 
communication, this module handles all WebSocket connections for live updates.

Think of this like the hospital's communication center:
- /ws/errors: Live error monitoring channel
- Real-time notifications and updates
- Connection management and heartbeat monitoring

🏆 HIGH SCHOOL EXPLANATION:
Like a school's intercom system that can:
1. Broadcast emergency announcements to all classrooms (error alerts)
2. Allow two-way communication between office and classrooms (WebSocket chat)
3. Monitor which rooms are connected and responding (connection management)
4. Send regular updates about school events (real-time stats)
"""

import json
import time
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...realtime import ConnectionManager, RealtimeErrorMonitor

# Create router for this department
router = APIRouter(tags=["realtime"])

# Initialize real-time components
connection_manager = ConnectionManager()
error_monitor = RealtimeErrorMonitor(connection_manager)


@router.websocket("/ws/errors")
async def websocket_errors(websocket: WebSocket):
    """
    📡 REAL-TIME ERROR MONITORING CHANNEL
    
    This WebSocket endpoint provides live error monitoring, like having
    a direct communication line to the hospital's emergency response center.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like being on a group video call with the IT department where:
    - You get notified instantly when something breaks
    - You can ask for current system status
    - You get live updates about what's happening
    - Connection stays open for continuous communication
    """
    try:
        # Connect to the real-time monitoring system
        await connection_manager.connect(websocket, {
            "endpoint": "/ws/errors",
            "purpose": "real-time error monitoring"
        })
        
        # Send welcome message with current stats
        welcome_message = {
            "type": "welcome",
            "message": "Connected to real-time error monitoring",
            "stats": error_monitor.get_error_stats(),
            "recent_errors": error_monitor.get_recent_errors(10)
        }
        await connection_manager.send_personal_message(json.dumps(welcome_message), websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (like ping/pong or config changes)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await connection_manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": time.time()}), 
                        websocket
                    )
                elif message.get("type") == "get_stats":
                    stats = {
                        "type": "stats_update",
                        "error_stats": error_monitor.get_error_stats(),
                        "connection_stats": connection_manager.get_connection_stats()
                    }
                    await connection_manager.send_personal_message(json.dumps(stats), websocket)
                elif message.get("type") == "get_recent_errors":
                    limit = message.get("limit", 20)
                    recent = {
                        "type": "recent_errors",
                        "errors": error_monitor.get_recent_errors(limit)
                    }
                    await connection_manager.send_personal_message(json.dumps(recent), websocket)
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}), 
                    websocket
                )
            except Exception as e:
                await connection_manager.send_personal_message(
                    json.dumps({"type": "error", "message": f"Processing error: {str(e)}"}), 
                    websocket
                )
                
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        # Clean up connection
        connection_manager.disconnect(websocket)