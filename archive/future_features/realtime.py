"""
📡 DEBUGGLE LIVE BROADCAST STATION - Real-Time Error Monitoring! 📡

Think of this file as a TV news station that broadcasts breaking news about
errors as they happen! Just like how news stations have reporters, camera crews,
and broadcast equipment, this module has everything needed to capture and
broadcast error "news" in real-time.

🎯 WHAT THIS MODULE DOES:
This is the "live streaming" system for Debuggle. When errors happen anywhere
in the system, this module immediately tells all connected users about it,
like a news alert system for programming problems!

📺 THE NEWS STATION ANALOGY:
- ConnectionManager: Like the broadcast control room that manages all TV channels
- ErrorEvent: Like a news story with headline, details, and timestamp
- RealtimeErrorMonitor: Like the news director who decides what to broadcast
- WebSocket connections: Like individual TV channels going to different homes

🔄 HOW REAL-TIME MONITORING WORKS:
1. Something goes wrong in the system (like a "breaking news" event)
2. We create an ErrorEvent (like writing a news story)
3. The RealtimeErrorMonitor decides if it should be broadcast
4. The ConnectionManager sends it to all connected users (like broadcasting)
5. Users see the error immediately in their browsers (like watching live TV)

Real-world analogy: This is like having a security system that immediately
sends alerts to your phone when something happens at your house - no waiting,
no delays, you know about problems as soon as they occur!
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
    """
    📻 BROADCAST CONTROL ROOM - Managing All Our Live Connections!
    
    Think of this as the control room at a radio or TV station where they
    manage all the different channels and keep track of who's listening.
    This class handles all the "phone lines" (WebSocket connections) between
    our server and users' browsers.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like managing a group video call where you need to:
    - Keep track of who joined the call (active_connections)
    - Remember details about each person (connection_metadata)
    - Send messages to everyone or specific people
    - Handle it gracefully when someone leaves
    
    WebSockets are like having a continuous phone conversation instead of
    sending individual text messages - the connection stays open!
    """
    
    def __init__(self):
        """
        🏗️ SETTING UP THE BROADCAST STUDIO
        
        When we create a new ConnectionManager, it's like setting up a new
        radio station - we need to prepare our equipment and start with
        empty lists of listeners!
        """
        # 📞 ACTIVE PHONE LINES - list of all open WebSocket connections
        # Like keeping a list of everyone currently on a conference call
        self.active_connections: List[WebSocket] = []
        
        # 📋 CONNECTION DETAILS - extra information about each connection
        # Like having a guest book with details about each visitor
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_info: Optional[Dict[str, Any]] = None):
        """
        🤝 WELCOMING A NEW LISTENER - Someone Wants to Join Our Broadcast!
        
        This is like when someone calls into a radio show and the host says
        "You're on the air!" - we're accepting their connection and adding
        them to our list of active listeners.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like when someone joins your Discord voice channel:
        1. They request to join
        2. You accept them into the channel
        3. You add them to the "who's here" list
        4. You remember when they joined and their username
        """
        # 📞 ANSWER THE PHONE - officially accept the WebSocket connection
        # Like picking up when someone calls and saying "Hello!"
        await websocket.accept()
        
        # 📝 ADD TO GUEST LIST - put them on our active connections list
        # Like writing their name on the attendance sheet
        self.active_connections.append(websocket)
        
        # 📋 RECORD THEIR DETAILS - remember info about this connection
        # Like a hotel keeping a guest registry with check-in time and details
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(),      # When they joined (like a timestamp)
            "client_info": client_info or {},    # Any extra info about them
            "message_count": 0                   # How many messages we've sent them
        }
        
        # 📢 ANNOUNCE THE NEW ARRIVAL - log this for our records
        # Like a security guard noting "new visitor arrived at 3:15 PM"
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
        """
        📢 EMERGENCY BROADCAST - Send Breaking News to Everyone!
        
        This is like the Emergency Alert System that can interrupt all TV
        and radio stations with important news. When we have an error event
        that everyone needs to know about, this function tells ALL connected
        users at the same time.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like the principal making an announcement over the school PA system -
        everyone in every classroom hears it at the same time. But if some
        classrooms have broken speakers, we note which ones didn't get the message.
        """
        # 🤷 NO AUDIENCE? NO SHOW! - if nobody's listening, don't bother
        # Like checking if anyone is in the auditorium before starting a presentation
        if not self.active_connections:
            return
        
        # 📻 GOING LIVE - announce that we're about to broadcast
        # Like a radio DJ saying "Now broadcasting to all our listeners"
        logger.info(f"Broadcasting message to {len(self.active_connections)} connections")
        
        # 📝 KEEP TRACK OF BROKEN CONNECTIONS - list of people who can't receive messages
        # Like noting which phones had busy signals when making group calls
        disconnected = []
        
        # 📞 CALL EVERYONE ON THE LIST - send the message to each connection
        # Like calling everyone in your contacts to share important news
        for connection in self.active_connections:
            try:
                # 💬 SEND THE MESSAGE - deliver the news to this person
                await connection.send_text(message)
                
                # 📊 UPDATE THEIR STATS - increment their message counter
                # Like keeping track of how many newsletters you've sent each subscriber
                if connection in self.connection_metadata:
                    self.connection_metadata[connection]["message_count"] += 1
                    
            except Exception as e:
                # 📵 CONNECTION FAILED - this person's "phone line" is broken
                # Like getting a "number disconnected" message when calling
                logger.error(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # 🧹 HOUSEKEEPING - remove the broken connections from our list
        # Like removing dead phone numbers from your contact list
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
    """
    📰 ERROR NEWS STORY - A Complete Report About What Went Wrong!
    
    Think of this as a news article about an error! Just like a newspaper
    story has a headline, timestamp, reporter, and details, this class
    contains all the important information about an error that occurred.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like writing a news report for the school newspaper:
    - id: The article number (like "Story #12345")
    - timestamp: When it happened (like "March 15, 2024 at 2:30 PM")
    - error_type: The headline (like "Fire Drill" or "Network Outage")
    - message: The main story (what actually happened)
    - source: Who reported it (like "Science Lab" or "Library")
    - severity: How serious it is (like "Minor", "Major", "Emergency")
    - metadata: Extra details (like witness statements or photos)
    """
    
    def __init__(self, error_type: str, message: str, source: str = "unknown", 
                 severity: str = "error", metadata: Optional[Dict[str, Any]] = None):
        """
        📝 WRITING A NEW ERROR STORY
        
        When something goes wrong, we create a complete "news report" about it
        with all the important details organized and timestamped.
        """
        # 🏷️ UNIQUE STORY ID - a special number for this error event
        # Like a tracking number for a package - no two errors have the same ID
        self.id = f"error_{int(time.time() * 1000)}"
        
        # 🕒 WHEN IT HAPPENED - exact timestamp of the error
        # Like the time stamp on a news article or security camera footage
        self.timestamp = datetime.now()
        
        # 📊 WHAT KIND OF ERROR - category or type of problem
        # Like the section of the newspaper: "Sports", "Weather", "Breaking News"
        self.error_type = error_type
        
        # 💬 THE MAIN STORY - detailed description of what went wrong
        # Like the main text of a news article explaining what happened
        self.message = message
        
        # 📍 WHERE IT CAME FROM - which part of the system reported this
        # Like the dateline on a news story: "WASHINGTON -" or "LOCAL -"
        self.source = source
        
        # 🌡️ HOW SERIOUS IS IT - severity level of the error
        # Like news categories: "Breaking News", "Weather Alert", "Sports Update"
        self.severity = severity
        
        # 📎 EXTRA DETAILS - any additional information about the error
        # Like photos, witness statements, or related documents attached to a news story
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
    """
    📺 THE NEWS DIRECTOR - Deciding What Gets Broadcast!
    
    Think of this as the news director at a TV station who decides which
    stories are important enough to interrupt regular programming with
    "breaking news" alerts. This class watches for errors and immediately
    broadcasts the important ones to all connected viewers.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the person who manages the school's announcement system:
    - Decides which announcements are important enough to broadcast
    - Keeps a record of all announcements made
    - Can turn the system on/off
    - Provides statistics about what types of announcements happen most
    
    This monitor watches the entire Debuggle system and immediately tells
    users when interesting errors happen!
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        🏗️ SETTING UP THE NEWS ROOM
        
        When we create a new RealtimeErrorMonitor, it's like setting up
        a complete news operation with broadcasting equipment, archive storage,
        and editorial policies.
        """
        # 📡 OUR BROADCASTING EQUIPMENT - the connection manager that sends messages
        # Like having the radio transmitter that actually broadcasts our signal
        self.connection_manager = connection_manager
        
        # 📚 THE NEWS ARCHIVE - list of all error events we've seen
        # Like keeping a complete archive of every news story we've ever published
        self.error_history: List[ErrorEvent] = []
        
        # 📏 ARCHIVE SIZE LIMIT - how many old stories should we keep?
        # Like deciding to keep only the last 1000 newspapers in the library
        self.max_history_size = 1000
        
        # 🔛 BROADCAST SWITCH - is our monitoring system currently active?
        # Like the "ON AIR" light at a radio station
        self.monitoring_enabled = True
    
    async def report_error(self, error_type: str, message: str, source: str = "api",
                          severity: str = "error", metadata: Optional[Dict[str, Any]] = None):
        """
        🚨 BREAKING NEWS ALERT - Something Important Just Happened!
        
        This is like when a news director gets a hot tip about a breaking story
        and immediately decides to interrupt regular programming with a news flash.
        When any part of Debuggle encounters an error, it calls this function
        to broadcast the news to all connected users.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like when something important happens at school and they need to make
        an announcement over the PA system:
        1. Create the announcement (ErrorEvent)
        2. Add it to the record books (error_history)
        3. Broadcast it to everyone (connection_manager.broadcast)
        4. Keep the announcement archive from getting too big
        """
        # 📴 SYSTEM OFF? NO BROADCAST - check if monitoring is enabled
        # Like checking if the "ON AIR" light is on before making an announcement
        if not self.monitoring_enabled:
            return
        
        # 📰 CREATE THE NEWS STORY - package all the error details
        # Like a reporter writing up all the facts about what happened
        error_event = ErrorEvent(error_type, message, source, severity, metadata)
        
        # 📚 ADD TO THE ARCHIVE - save this error in our history
        # Like filing a copy of today's newspaper in the library archive
        self.error_history.append(error_event)
        
        # 🗑️ ARCHIVE MAINTENANCE - keep the archive from getting too big
        # Like throwing away the oldest newspapers when the storage is full
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)  # Remove the oldest error
        
        # 📡 GO LIVE! - broadcast this error to all connected clients
        # Like the news director saying "interrupt all programs, we're going live!"
        await self.connection_manager.broadcast(error_event.to_json())
        
        # 📝 LOG IT FOR OUR RECORDS - write it in the internal log book
        # Like the producer keeping notes about what was broadcast when
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
        """
        📊 NEWSROOM ANALYTICS - What Stories Have We Been Covering?
        
        This is like the analytics department at a news station that tracks
        what types of stories they've been reporting. It analyzes our error
        history to show patterns and trends in what's been going wrong.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like making a summary report of all the school announcements this year:
        - How many total announcements were made?
        - What were the most common types? (fire drills, weather delays, etc.)
        - How many were urgent vs. just informational?
        - Which departments made the most announcements?
        
        This helps us understand if there are patterns in our errors!
        """
        # 📭 EMPTY ARCHIVE? EMPTY REPORT - no history means no stats
        # Like trying to write a summary when no newspapers were published
        if not self.error_history:
            return {
                "total_errors": 0,
                "error_types": {},
                "severity_breakdown": {},
                "sources": {}
            }
        
        # 📊 COUNTING BUCKETS - initialize our counting systems
        # Like setting up different boxes to sort different types of documents
        error_types = {}          # Count by error type (IndexError, TypeError, etc.)
        severity_breakdown = {}   # Count by severity (critical, high, medium, etc.)
        sources = {}             # Count by source (api, database, file_system, etc.)
        
        # 🔍 ANALYZE EACH ERROR - go through our entire history
        # Like reading every newspaper in the archive and making tally marks
        for error in self.error_history:
            
            # 📈 COUNT ERROR TYPES - tally up each type of error
            # Like counting "how many sports stories vs weather stories"
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            
            # 🌡️ COUNT SEVERITY LEVELS - tally up how serious each error was
            # Like counting "emergency alerts vs routine announcements"
            severity_breakdown[error.severity] = severity_breakdown.get(error.severity, 0) + 1
            
            # 📍 COUNT SOURCES - tally up where errors came from
            # Like counting "how many stories from each department"
            sources[error.source] = sources.get(error.source, 0) + 1
        
        # 📋 COMPILE THE FINAL REPORT - package up all our statistics
        # Like creating a comprehensive annual report with all the data
        return {
            "total_errors": len(self.error_history),    # Grand total count
            "error_types": error_types,                 # Breakdown by type
            "severity_breakdown": severity_breakdown,   # Breakdown by severity
            "sources": sources,                         # Breakdown by source
            "monitoring_enabled": self.monitoring_enabled  # Is the system active?
        }
    
    def toggle_monitoring(self, enabled: bool):
        """Enable or disable error monitoring."""
        self.monitoring_enabled = enabled
        logger.info(f"Error monitoring {'enabled' if enabled else 'disabled'}")


# Global instances
connection_manager = ConnectionManager()
error_monitor = RealtimeErrorMonitor(connection_manager)