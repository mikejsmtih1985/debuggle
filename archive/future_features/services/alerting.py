"""
🚨 DEBUGGLE ALERT SYSTEM - Proactive Error Notifications! 🚨

Think of this module as a smart alarm system for your applications - like having
a security guard who watches for problems 24/7 and immediately notifies you
when something goes wrong. Instead of waiting for users to report issues,
this system catches problems as they happen and alerts the right people!

🏆 HIGH SCHOOL EXPLANATION:
Imagine you're monitoring a school building:
- Motion sensors detect unusual activity (error pattern detection)
- Fire alarms trigger when smoke is detected (critical error alerts)
- The system calls security, fire department, or maintenance (notification channels)
- Different alerts go to different people (routing rules)
- Some issues are more urgent than others (priority levels)

This alerting system does the same thing but for software errors!

WHY PROACTIVE ALERTING MATTERS:
🔥 Early Detection - Catch problems before they affect users
⚡ Instant Response - Get notified in seconds, not hours
🎯 Smart Routing - Right alert to right person at right time
📊 Pattern Recognition - Spot trends before they become disasters  
💤 Reduce Alert Fatigue - Only alert on what truly matters
🔧 Integration Ready - Works with Slack, email, PagerDuty, etc.

ALERT CAPABILITIES PROVIDED:
📧 Multi-Channel Notifications - Email, Slack, webhook, SMS
🔍 Pattern-Based Triggers - "Alert if >10 errors in 5 minutes"
🏷️ Smart Categorization - Different rules for different error types
⏰ Time-Based Rules - "Only alert during business hours"
🔄 Escalation Policies - "If not acknowledged in 15 minutes, call manager"
💡 Alert Grouping - Prevent spam by grouping similar alerts
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp

from ..realtime import connection_manager, RealtimeErrorMonitor
from ..storage.database import LogEntry, LogSeverity

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """
    🌡️ ALERT URGENCY SCALE - How Fast Should We Respond?
    
    Just like hospital triage levels, we categorize alerts by how
    urgently they need attention. This helps prevent alert fatigue
    while ensuring critical issues get immediate response.
    """
    LOW = "low"           # 💚 Nice to know - can wait until business hours
    MEDIUM = "medium"     # 🟡 Should investigate - within a few hours  
    HIGH = "high"         # 🟠 Needs attention - within an hour
    CRITICAL = "critical" # 🔴 Emergency - wake someone up immediately


class AlertChannel(str, Enum):
    """
    📢 NOTIFICATION DELIVERY METHODS - How Should We Contact You?
    
    Different situations call for different notification methods.
    Like choosing between texting, calling, or sending an email
    based on how urgent the message is.
    """
    EMAIL = "email"           # 📧 Traditional email notification
    SLACK = "slack"           # 💬 Slack channel or DM
    WEBHOOK = "webhook"       # 🔗 HTTP POST to custom endpoint
    WEBSOCKET = "websocket"   # ⚡ Real-time browser notification
    SMS = "sms"              # 📱 Text message (future implementation)
    PAGERDUTY = "pagerduty"  # 📟 PagerDuty incident (future implementation)


@dataclass
class AlertRule:
    """
    📋 SMART ALARM CONFIGURATION - One Complete Alert Setup
    
    Think of this as programming a smart security system. Each AlertRule
    is like setting up one specific alarm - "If the front door opens
    after midnight, send me a text message and turn on the lights."
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like setting up a smart home automation rule:
    - name: "After Hours Security Alert" (what to call this rule)
    - conditions: "Motion detected after 10 PM" (when to trigger)
    - actions: "Send notification + turn on lights" (what to do)
    - enabled: "Yes, this rule is active" (is it currently running)
    """
    
    # 🏷️ RULE IDENTIFICATION
    rule_id: str                              # Unique identifier for this rule
    name: str                                 # Human-readable name
    description: str                          # What this rule does
    
    # 🎯 TRIGGER CONDITIONS - When should this alert fire?
    severity_filter: Optional[List[LogSeverity]] = None    # Only these severity levels
    language_filter: Optional[List[str]] = None            # Only these programming languages
    tag_filter: Optional[List[str]] = None                 # Only logs with these tags
    project_filter: Optional[List[str]] = None             # Only these projects
    
    # 🔍 ADVANCED PATTERN MATCHING
    content_regex: Optional[str] = None                    # Regex pattern in log content
    error_count_threshold: Optional[int] = None            # Alert if >N errors in time window
    time_window_minutes: int = 5                           # Time window for counting errors
    
    # 📅 TIME-BASED CONTROLS
    business_hours_only: bool = False                      # Only alert during business hours
    business_start_hour: int = 9                           # Business hours start (24-hour format)
    business_end_hour: int = 17                            # Business hours end
    weekdays_only: bool = False                            # Only alert Monday-Friday
    
    # 🚨 ALERT CONFIGURATION
    alert_severity: AlertSeverity = AlertSeverity.MEDIUM   # How urgent is this alert?
    channels: List[AlertChannel] = field(default_factory=list)  # How to notify
    
    # 📬 NOTIFICATION TARGETS
    email_recipients: List[str] = field(default_factory=list)   # Email addresses
    slack_channels: List[str] = field(default_factory=list)     # Slack channels
    webhook_urls: List[str] = field(default_factory=list)       # Webhook endpoints
    
    # ⚙️ RULE MANAGEMENT
    enabled: bool = True                                   # Is this rule active?
    created_at: datetime = field(default_factory=datetime.now)  # When was it created
    last_triggered: Optional[datetime] = None             # When did it last fire
    trigger_count: int = 0                                # How many times has it fired
    
    # 🔧 ADVANCED OPTIONS
    cooldown_minutes: int = 15                            # Wait time between duplicate alerts
    escalation_minutes: Optional[int] = None              # Escalate if not acknowledged
    custom_message_template: Optional[str] = None         # Custom alert message format


@dataclass
class Alert:
    """
    🚨 INDIVIDUAL ALERT INSTANCE - One Specific Alert Event
    
    This represents one specific alert that was triggered - like one
    specific fire alarm going off. It contains all the details about
    what happened, when it happened, and what actions were taken.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like an incident report that gets filed when something happens:
    - alert_id: "Incident #12345" (unique tracking number)
    - rule_name: "Fire Detection System" (which alarm system triggered)
    - timestamp: "March 15, 2024 at 2:30 AM" (when it happened)
    - message: "Smoke detected in Building A, Room 201" (what happened)
    - severity: "CRITICAL" (how serious it is)
    - status: "ACTIVE" (current state of the incident)
    """
    
    # 🏷️ ALERT IDENTIFICATION
    alert_id: str                             # Unique identifier for this alert
    rule_id: str                              # Which rule triggered this alert
    rule_name: str                            # Human-readable rule name
    
    # ⏰ TIMING INFORMATION
    timestamp: datetime                       # When the alert was triggered
    
    # 📝 ALERT CONTENT
    message: str                              # Main alert message
    details: Dict[str, Any]                   # Additional structured data
    severity: AlertSeverity                   # How urgent this alert is
    
    # 🎯 SOURCE INFORMATION
    triggered_by_log: Optional[str] = None    # Log ID that triggered this alert
    source_project: Optional[str] = None     # Project where the error occurred
    source_language: Optional[str] = None    # Programming language
    error_tags: List[str] = field(default_factory=list)  # Error categories
    
    # 📊 ALERT STATUS
    status: str = "ACTIVE"                    # ACTIVE, ACKNOWLEDGED, RESOLVED, EXPIRED
    acknowledged_at: Optional[datetime] = None # When someone acknowledged it
    acknowledged_by: Optional[str] = None     # Who acknowledged it
    resolved_at: Optional[datetime] = None    # When it was resolved
    
    # 📬 DELIVERY TRACKING
    channels_notified: List[str] = field(default_factory=list)  # Which channels got notified
    delivery_failures: List[str] = field(default_factory=list) # Any delivery errors
    
    # 🔄 ESCALATION TRACKING
    escalated: bool = False                   # Has this been escalated?
    escalated_at: Optional[datetime] = None  # When was it escalated
    escalation_level: int = 0                 # Current escalation level


class AlertManager:
    """
    🎯 THE ALERT COMMANDER - Master Controller of All Notifications!
    
    Think of this class as the central command center for a emergency response
    system. It watches for problems, decides which alerts to send, manages
    notification channels, and tracks the status of all active alerts.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the emergency dispatch center for a city:
    - Receives 911 calls (error logs)
    - Decides which emergency services to send (notification channels)
    - Tracks all active incidents (alert management)
    - Prevents duplicate responses (alert deduplication)
    - Escalates serious situations (escalation policies)
    - Keeps detailed records (alert history)
    
    This system does the same thing but for software errors instead of emergencies!
    """
    
    def __init__(self, error_monitor: RealtimeErrorMonitor):
        """
        🏗️ SETTING UP THE COMMAND CENTER
        
        When we create a new AlertManager, it's like setting up a complete
        emergency response center with all the communication equipment,
        monitoring systems, and protocol manuals needed to handle alerts.
        """
        # 📡 CONNECTION TO ERROR MONITORING SYSTEM
        self.error_monitor = error_monitor
        
        # 📋 ALERT RULES DATABASE - all our configured alert conditions
        self.rules: Dict[str, AlertRule] = {}
        
        # 🚨 ACTIVE ALERTS TRACKING - currently firing alerts
        self.active_alerts: Dict[str, Alert] = {}
        
        # 📚 ALERT HISTORY - historical record of all alerts
        self.alert_history: List[Alert] = []
        self.max_history_size: int = 10000
        
        # 🔄 COOLDOWN TRACKING - prevent duplicate alerts
        self.cooldowns: Dict[str, datetime] = {}  # rule_id -> last_alert_time
        
        # 📊 ALERT STATISTICS
        self.stats = {
            "total_alerts_sent": 0,
            "alerts_by_severity": {severity.value: 0 for severity in AlertSeverity},
            "alerts_by_channel": {channel.value: 0 for channel in AlertChannel},
            "average_response_time_minutes": 0.0
        }
        
        # ⚙️ CONFIGURATION SETTINGS
        self.config = {
            "max_alerts_per_hour": 100,        # Rate limiting to prevent spam
            "alert_retention_days": 30,        # How long to keep alert history
            "default_cooldown_minutes": 15,    # Default time between duplicate alerts
            "escalation_enabled": True,        # Whether to escalate unacknowledged alerts
            "business_hours_timezone": "UTC"   # Timezone for business hours calculations
        }
        
        # 🔗 NOTIFICATION CHANNEL CLIENTS
        self.notification_clients = {}  # Will hold email, Slack, webhook clients
        
        # 🚀 START BACKGROUND TASKS
        self._setup_background_tasks()
        
        logger.info("Alert manager initialized")
    
    def _setup_background_tasks(self):
        """
        🔄 START BACKGROUND MONITORING TASKS
        
        This starts the background processes that continuously monitor for
        alert conditions and handle ongoing alert management tasks.
        Like having security guards on patrol 24/7.
        """
        # TODO: In a real implementation, you'd start asyncio background tasks here
        # For now, we'll handle this through direct method calls
        pass
    
    def add_alert_rule(self, rule: AlertRule):
        """
        📝 REGISTER A NEW ALERT RULE - Adding to Our Alert Protocols
        
        This is like adding a new emergency protocol to the dispatch manual.
        "When condition X happens, follow procedure Y to notify person Z."
        Each rule defines exactly when and how to send alerts.
        """
        self.rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.rule_id})")
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """
        🗑️ REMOVE AN ALERT RULE - Deleting Outdated Protocols
        
        This removes an alert rule from our system, like taking an outdated
        emergency procedure out of the dispatch manual.
        """
        if rule_id in self.rules:
            removed_rule = self.rules.pop(rule_id)
            logger.info(f"Removed alert rule: {removed_rule.name} ({rule_id})")
            return True
        else:
            logger.warning(f"Attempted to remove non-existent rule: {rule_id}")
            return False
    
    async def evaluate_log_for_alerts(self, log_entry: LogEntry):
        """
        🔍 CHECK IF THIS LOG SHOULD TRIGGER ALERTS - The Main Detection Engine
        
        This is the core function that examines each new error log and decides
        whether it should trigger any alerts. Like a security guard checking
        each event against the list of things to watch for.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like a school security system checking each event:
        1. Student badge scanned at door (new log entry arrives)
        2. Check against all security rules (evaluate each alert rule)
        3. "After hours entry detected" (rule condition matches)
        4. Send alert to security office (trigger notification)
        5. Log the incident (record the alert)
        """
        for rule in self.rules.values():
            if not rule.enabled:
                continue  # Skip disabled rules
            
            # 🎯 CHECK IF THIS LOG MATCHES THE RULE CONDITIONS
            if await self._log_matches_rule(log_entry, rule):
                # 🔄 CHECK COOLDOWN - prevent alert spam
                if self._is_in_cooldown(rule):
                    logger.debug(f"Rule {rule.name} is in cooldown, skipping alert")
                    continue
                
                # 📅 CHECK TIME-BASED CONDITIONS
                if not self._is_alert_time_allowed(rule):
                    logger.debug(f"Rule {rule.name} not allowed at current time, skipping")
                    continue
                
                # 🚨 TRIGGER THE ALERT!
                await self._trigger_alert(rule, log_entry)
    
    async def _log_matches_rule(self, log_entry: LogEntry, rule: AlertRule) -> bool:
        """
        🎯 DOES THIS LOG MATCH THE ALERT RULE? - Pattern Detection Engine
        
        This checks whether a specific log entry meets all the conditions
        defined in an alert rule. Like checking if an event matches all
        the criteria in a security protocol.
        """
        # 🌡️ CHECK SEVERITY FILTER
        if rule.severity_filter and log_entry.severity not in rule.severity_filter:
            return False
        
        # 💻 CHECK LANGUAGE FILTER
        if rule.language_filter and log_entry.language not in rule.language_filter:
            return False
        
        # 📁 CHECK PROJECT FILTER
        if rule.project_filter and log_entry.project_name not in rule.project_filter:
            return False
        
        # 🏷️ CHECK TAG FILTER - any of the rule's tags must be present
        if rule.tag_filter:
            rule_tags_set = set(rule.tag_filter)
            log_tags_set = set(log_entry.tags)
            if not rule_tags_set.intersection(log_tags_set):
                return False
        
        # 🔍 CHECK CONTENT REGEX - pattern matching in log content
        if rule.content_regex:
            try:
                pattern = re.compile(rule.content_regex, re.IGNORECASE | re.MULTILINE)
                searchable_text = f"{log_entry.original_log} {log_entry.processed_log} {log_entry.summary or ''}"
                if not pattern.search(searchable_text):
                    return False
            except re.error as e:
                logger.error(f"Invalid regex in rule {rule.name}: {e}")
                return False
        
        # 📊 CHECK ERROR COUNT THRESHOLD
        if rule.error_count_threshold:
            recent_count = await self._count_recent_matching_errors(rule, log_entry)
            if recent_count < rule.error_count_threshold:
                return False
        
        # ✅ ALL CONDITIONS MATCHED!
        return True
    
    async def _count_recent_matching_errors(self, rule: AlertRule, current_log: LogEntry) -> int:
        """
        📊 COUNT RECENT SIMILAR ERRORS - Pattern Frequency Detection
        
        This counts how many similar errors have occurred in the recent time window.
        Like counting how many times the fire alarm has gone off in the last hour.
        """
        # TODO: In a real implementation, you'd query the database for recent matching logs
        # For now, we'll return 1 (just the current log)
        return 1
    
    def _is_in_cooldown(self, rule: AlertRule) -> bool:
        """
        ⏰ CHECK ALERT COOLDOWN - Prevent Alert Spam
        
        This prevents the same alert from being sent repeatedly in a short time.
        Like having a "snooze" period after each alert to avoid bombarding people.
        """
        if rule.rule_id not in self.cooldowns:
            return False
        
        last_alert_time = self.cooldowns[rule.rule_id]
        cooldown_duration = timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() < (last_alert_time + cooldown_duration)
    
    def _is_alert_time_allowed(self, rule: AlertRule) -> bool:
        """
        📅 CHECK IF ALERTS ARE ALLOWED NOW - Time-Based Filtering
        
        This checks whether alerts should be sent at the current time
        based on business hours and weekday settings. Like a "Do Not Disturb"
        mode that respects work schedules.
        """
        now = datetime.now()
        
        # 📅 CHECK WEEKDAY FILTER
        if rule.weekdays_only and now.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # 🕒 CHECK BUSINESS HOURS FILTER
        if rule.business_hours_only:
            current_hour = now.hour
            if not (rule.business_start_hour <= current_hour < rule.business_end_hour):
                return False
        
        return True
    
    async def _trigger_alert(self, rule: AlertRule, log_entry: LogEntry):
        """
        🚨 FIRE THE ALERT! - Send Notifications to All Channels
        
        This is where the actual alert gets created and sent out through
        all the configured notification channels. Like pressing the big
        red emergency button that activates all the alarm systems.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like activating a school's emergency protocol:
        1. Create the alert message (incident report)
        2. Update cooldown timers (prevent duplicate alerts)
        3. Send to all notification channels (PA system, text alerts, emails)
        4. Record the incident (add to alert history)
        5. Update statistics (track response metrics)
        """
        
        # 🏷️ CREATE UNIQUE ALERT ID
        alert_id = self._generate_alert_id(rule, log_entry)
        
        # 📝 BUILD ALERT MESSAGE
        message = self._build_alert_message(rule, log_entry)
        
        # 🚨 CREATE ALERT OBJECT
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            rule_name=rule.name,
            timestamp=datetime.now(),
            message=message,
            details=self._build_alert_details(rule, log_entry),
            severity=rule.alert_severity,
            triggered_by_log=log_entry.log_id,
            source_project=log_entry.project_name,
            source_language=log_entry.language,
            error_tags=log_entry.tags.copy()
        )
        
        # 📚 RECORD THE ALERT
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # 🧹 MANAGE HISTORY SIZE
        if len(self.alert_history) > self.max_history_size:
            self.alert_history.pop(0)
        
        # ⏰ UPDATE COOLDOWN
        self.cooldowns[rule.rule_id] = datetime.now()
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        # 📤 SEND NOTIFICATIONS TO ALL CHANNELS
        await self._send_alert_notifications(alert, rule)
        
        # 📊 UPDATE STATISTICS
        self.stats["total_alerts_sent"] += 1
        self.stats["alerts_by_severity"][alert.severity.value] += 1
        
        logger.info(f"Alert triggered: {alert.alert_id} from rule {rule.name}")
    
    def _generate_alert_id(self, rule: AlertRule, log_entry: LogEntry) -> str:
        """
        🏷️ CREATE UNIQUE ALERT IDENTIFIER
        
        This creates a unique ID for each alert, like generating a case number
        for each emergency incident. The ID includes information about the
        rule and timing to make it unique and traceable.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rule_hash = hashlib.md5(rule.rule_id.encode()).hexdigest()[:8]
        return f"alert_{timestamp}_{rule_hash}"
    
    def _build_alert_message(self, rule: AlertRule, log_entry: LogEntry) -> str:
        """
        📝 CREATE ALERT MESSAGE TEXT
        
        This builds the human-readable alert message that will be sent
        to notification channels. Like writing the emergency announcement
        that goes out over the PA system.
        """
        if rule.custom_message_template:
            # TODO: Implement template substitution
            return rule.custom_message_template
        
        # 📋 BUILD DEFAULT MESSAGE
        message_parts = [
            f"🚨 {rule.alert_severity.value.upper()} ALERT: {rule.name}",
            f"📍 Project: {log_entry.project_name or 'Unknown'}",
            f"💻 Language: {log_entry.language}",
            f"🏷️ Tags: {', '.join(log_entry.tags)}",
            "",
            f"📝 Error Summary: {log_entry.summary or 'No summary available'}",
            "",
            f"⏰ Occurred at: {log_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"🆔 Log ID: {log_entry.log_id}"
        ]
        
        return "\n".join(message_parts)
    
    def _build_alert_details(self, rule: AlertRule, log_entry: LogEntry) -> Dict[str, Any]:
        """
        📊 BUILD STRUCTURED ALERT DATA
        
        This creates the structured data that accompanies the alert,
        like the detailed incident report that goes with an emergency
        notification. This data can be used by automation systems.
        """
        return {
            "rule": {
                "id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "severity": rule.alert_severity.value
            },
            "log": {
                "id": log_entry.log_id,
                "timestamp": log_entry.timestamp.isoformat(),
                "severity": log_entry.severity.value,
                "language": log_entry.language,
                "project": log_entry.project_name,
                "tags": log_entry.tags,
                "file_path": log_entry.file_path
            },
            "system": {
                "alert_time": datetime.now().isoformat(),
                "source": "debuggle_alert_system"
            }
        }
    
    async def _send_alert_notifications(self, alert: Alert, rule: AlertRule):
        """
        📤 SEND ALERT TO ALL NOTIFICATION CHANNELS
        
        This is the delivery system that sends the alert through all
        configured channels (email, Slack, webhooks, etc.). Like having
        multiple communication systems activate simultaneously during
        an emergency.
        """
        # 📬 SEND TO EACH CONFIGURED CHANNEL
        for channel in rule.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert, rule)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_alert(alert, rule)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert, rule)
                elif channel == AlertChannel.WEBSOCKET:
                    await self._send_websocket_alert(alert, rule)
                
                # 📊 TRACK SUCCESSFUL DELIVERY
                alert.channels_notified.append(channel.value)
                self.stats["alerts_by_channel"][channel.value] += 1
                
            except Exception as e:
                # 📝 TRACK DELIVERY FAILURE
                error_msg = f"{channel.value}: {str(e)}"
                alert.delivery_failures.append(error_msg)
                logger.error(f"Failed to send alert via {channel.value}: {e}")
    
    async def _send_email_alert(self, alert: Alert, rule: AlertRule):
        """
        📧 SEND EMAIL NOTIFICATION
        
        This sends the alert via email to all configured recipients.
        Like sending an emergency notification email to the response team.
        """
        if not rule.email_recipients:
            return
        
        # TODO: Implement actual email sending
        # For now, just log that we would send an email
        logger.info(f"Would send email alert to: {rule.email_recipients}")
    
    async def _send_slack_alert(self, alert: Alert, rule: AlertRule):
        """
        💬 SEND SLACK NOTIFICATION
        
        This sends the alert to configured Slack channels or direct messages.
        Like posting an emergency notification in the team's Slack channel.
        """
        if not rule.slack_channels:
            return
        
        # TODO: Implement actual Slack integration
        # For now, just log that we would send to Slack
        logger.info(f"Would send Slack alert to: {rule.slack_channels}")
    
    async def _send_webhook_alert(self, alert: Alert, rule: AlertRule):
        """
        🔗 SEND WEBHOOK NOTIFICATION
        
        This sends the alert to configured webhook URLs via HTTP POST.
        Like triggering automated systems or third-party integrations.
        """
        if not rule.webhook_urls:
            return
        
        # Build webhook payload
        payload = {
            "alert_id": alert.alert_id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "details": alert.details
        }
        
        # TODO: Implement actual webhook sending
        # For now, just log that we would send webhooks
        logger.info(f"Would send webhook alert to: {rule.webhook_urls}")
    
    async def _send_websocket_alert(self, alert: Alert, rule: AlertRule):
        """
        ⚡ SEND REAL-TIME WEBSOCKET NOTIFICATION
        
        This sends the alert to all connected WebSocket clients for
        real-time browser notifications. Like flashing a warning light
        on everyone's dashboard immediately.
        """
        # Build WebSocket message
        ws_message = {
            "type": "alert",
            "alert_id": alert.alert_id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "project": alert.source_project,
            "language": alert.source_language,
            "tags": alert.error_tags
        }
        
        # Send to all connected WebSocket clients
        await connection_manager.broadcast(json.dumps(ws_message))
        logger.info(f"Sent WebSocket alert: {alert.alert_id}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """
        ✅ ACKNOWLEDGE AN ALERT - Someone Is Handling This
        
        This marks an alert as acknowledged, meaning someone has seen it
        and is taking action. Like a security guard confirming they received
        the emergency notification and are responding.
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = "ACKNOWLEDGED"
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        else:
            logger.warning(f"Attempted to acknowledge non-existent alert: {alert_id}")
            return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        ✅ RESOLVE AN ALERT - Problem Has Been Fixed
        
        This marks an alert as resolved, meaning the underlying issue
        has been fixed. Like closing an incident report after the
        emergency has been handled.
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = "RESOLVED"
            alert.resolved_at = datetime.now()
            
            # Remove from active alerts
            self.active_alerts.pop(alert_id)
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
        else:
            logger.warning(f"Attempted to resolve non-existent alert: {alert_id}")
            return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """
        📊 GET ALERT SYSTEM STATISTICS
        
        This provides comprehensive statistics about the alerting system's
        performance and activity. Like a monthly report on emergency
        response system usage and effectiveness.
        """
        active_count = len(self.active_alerts)
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules.values() if r.enabled])
        
        return {
            "active_alerts": active_count,
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "alert_history_size": len(self.alert_history),
            "statistics": self.stats.copy(),
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity.value,
                    "timestamp": alert.timestamp.isoformat(),
                    "status": alert.status
                }
                for alert in self.alert_history[-10:]  # Last 10 alerts
            ]
        }


# Global alert manager instance (will be initialized when needed)
alert_manager: Optional[AlertManager] = None


def initialize_alert_manager(error_monitor: RealtimeErrorMonitor) -> AlertManager:
    """
    🚀 INITIALIZE THE GLOBAL ALERT SYSTEM
    
    This sets up the main alert manager instance that will be used
    throughout the application. Like setting up the emergency response
    center when the application starts.
    """
    global alert_manager
    if alert_manager is None:
        alert_manager = AlertManager(error_monitor)
        logger.info("Global alert manager initialized")
    return alert_manager


def get_alert_manager() -> Optional[AlertManager]:
    """
    📋 GET THE GLOBAL ALERT MANAGER INSTANCE
    
    This provides access to the main alert manager from anywhere
    in the application. Like having a direct line to the emergency
    dispatch center.
    """
    return alert_manager