"""
🚨 Hospital Alert System Department - Models for Emergency Notifications

This is the emergency alert system of our hospital! Just like how a real hospital
has different levels of emergency alerts (Code Blue, Code Red, etc.) and various 
ways to notify staff (PA system, pagers, mobile alerts), we have a sophisticated
alert system for code emergencies.

Think of this like the hospital's emergency response system:
- AlertRuleRequest: Setting up new emergency protocols
- AlertResponse: Details of an actual emergency incident
- AlertStatsResponse: Performance report of the alert system

🏆 HIGH SCHOOL EXPLANATION:
Like a school's emergency alert system:
1. Set up rules for different emergencies (fire, tornado, lockdown)
2. Choose how to notify people (PA, text, email)
3. Track when alerts happen and how people respond
4. Review system performance to improve response times
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

from .common import LogSeverity


class AlertSeverityAPI(str, Enum):
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


class AlertChannelAPI(str, Enum):
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


class AlertRuleRequest(BaseModel):
    """
    📋 CREATE ALERT RULE REQUEST - Blueprint for New Alert Rule
    
    This is like filling out a form to set up a new security alarm system.
    You specify what conditions should trigger the alarm and how you want
    to be notified when it goes off.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like programming a home security system:
    - name: "Front Door Alert" (what to call this alarm)
    - conditions: "Motion detected after 10 PM" (when to trigger)
    - notifications: "Send text to mom and dad" (who to contact)
    - enabled: "Yes, this alarm is active" (is it turned on)
    """
    
    # 🏷️ RULE IDENTIFICATION
    name: str = Field(..., description="Human-readable name for the alert rule")
    description: str = Field(..., description="Description of what this rule does")
    
    # 🎯 TRIGGER CONDITIONS - When should this alert fire?
    severity_filter: Optional[List[LogSeverity]] = Field(None, description="Filter by log severity levels")
    language_filter: Optional[List[str]] = Field(None, description="Filter by programming languages")
    tag_filter: Optional[List[str]] = Field(None, description="Filter by log tags")
    project_filter: Optional[List[str]] = Field(None, description="Filter by project names")
    
    # 🔍 ADVANCED PATTERN MATCHING
    content_regex: Optional[str] = Field(None, description="Regex pattern to match in log content")
    error_count_threshold: Optional[int] = Field(None, description="Alert if more than N errors in time window")
    time_window_minutes: int = Field(5, description="Time window for counting errors")
    
    # 📅 TIME-BASED CONTROLS
    business_hours_only: bool = Field(False, description="Only alert during business hours")
    business_start_hour: int = Field(9, description="Business hours start (24-hour format)")
    business_end_hour: int = Field(17, description="Business hours end (24-hour format)")
    weekdays_only: bool = Field(False, description="Only alert Monday-Friday")
    
    # 🚨 ALERT CONFIGURATION
    alert_severity: AlertSeverityAPI = Field(AlertSeverityAPI.MEDIUM, description="Alert urgency level")
    channels: List[AlertChannelAPI] = Field(default_factory=list, description="Notification channels to use")
    
    # 📬 NOTIFICATION TARGETS
    email_recipients: List[str] = Field(default_factory=list, description="Email addresses to notify")
    slack_channels: List[str] = Field(default_factory=list, description="Slack channels to notify")
    webhook_urls: List[str] = Field(default_factory=list, description="Webhook URLs to call")
    
    # ⚙️ RULE MANAGEMENT
    enabled: bool = Field(True, description="Whether this rule is active")
    cooldown_minutes: int = Field(15, description="Minutes to wait between duplicate alerts")
    escalation_minutes: Optional[int] = Field(None, description="Minutes before escalating unacknowledged alerts")
    custom_message_template: Optional[str] = Field(None, description="Custom alert message template")


class AlertRuleResponse(BaseModel):
    """
    📋 ALERT RULE DETAILS - Complete Information About an Alert Rule
    
    This is like getting a complete summary of a security system's configuration.
    It shows you exactly how the alarm is set up, when it was installed,
    and how many times it has been triggered.
    """
    
    # 🏷️ RULE IDENTIFICATION
    rule_id: str = Field(..., description="Unique identifier for this rule")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What this rule does")
    enabled: bool = Field(..., description="Whether this rule is currently active")
    
    # 📊 RULE STATISTICS
    created_at: str = Field(..., description="When this rule was created")
    last_triggered: Optional[str] = Field(None, description="When this rule last fired an alert")
    trigger_count: int = Field(..., description="How many times this rule has fired")
    
    # 🎯 ALL THE CONFIGURATION DETAILS (same as request model)
    severity_filter: Optional[List[LogSeverity]] = Field(None, description="Severity level filters")
    language_filter: Optional[List[str]] = Field(None, description="Programming language filters")
    tag_filter: Optional[List[str]] = Field(None, description="Tag filters")
    project_filter: Optional[List[str]] = Field(None, description="Project name filters")
    content_regex: Optional[str] = Field(None, description="Content pattern matching")
    error_count_threshold: Optional[int] = Field(None, description="Error count threshold")
    time_window_minutes: int = Field(..., description="Time window for error counting")
    business_hours_only: bool = Field(..., description="Business hours restriction")
    business_start_hour: int = Field(..., description="Business hours start")
    business_end_hour: int = Field(..., description="Business hours end")
    weekdays_only: bool = Field(..., description="Weekdays only restriction")
    alert_severity: AlertSeverityAPI = Field(..., description="Alert urgency level")
    channels: List[AlertChannelAPI] = Field(..., description="Notification channels")
    email_recipients: List[str] = Field(..., description="Email notification targets")
    slack_channels: List[str] = Field(..., description="Slack notification targets")
    webhook_urls: List[str] = Field(..., description="Webhook notification targets")
    cooldown_minutes: int = Field(..., description="Cooldown period between alerts")
    escalation_minutes: Optional[int] = Field(None, description="Escalation timeout")
    custom_message_template: Optional[str] = Field(None, description="Custom message template")


class AlertResponse(BaseModel):
    """
    🚨 INDIVIDUAL ALERT DETAILS - Complete Information About One Alert
    
    This is like an incident report that gets filed when an alarm goes off.
    It contains all the details about what happened, when it happened,
    who was notified, and what actions were taken.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a school incident report:
    - alert_id: "Incident #12345" (tracking number)
    - rule_name: "Fire Alarm System" (which alarm went off)
    - timestamp: "March 15, 2024 at 2:30 AM" (when it happened)
    - message: "Smoke detected in Building A" (what happened)
    - status: "RESOLVED" (current state of the incident)
    """
    
    # 🏷️ ALERT IDENTIFICATION
    alert_id: str = Field(..., description="Unique identifier for this alert")
    rule_id: str = Field(..., description="ID of the rule that triggered this alert")
    rule_name: str = Field(..., description="Name of the rule that triggered this alert")
    
    # ⏰ TIMING INFORMATION
    timestamp: str = Field(..., description="When this alert was triggered")
    
    # 📝 ALERT CONTENT
    message: str = Field(..., description="Main alert message")
    details: Dict[str, Any] = Field(..., description="Additional structured data")
    severity: AlertSeverityAPI = Field(..., description="Alert urgency level")
    
    # 🎯 SOURCE INFORMATION
    triggered_by_log: Optional[str] = Field(None, description="Log ID that triggered this alert")
    source_project: Optional[str] = Field(None, description="Project where error occurred")
    source_language: Optional[str] = Field(None, description="Programming language")
    error_tags: List[str] = Field(default_factory=list, description="Error category tags")
    
    # 📊 ALERT STATUS TRACKING
    status: str = Field(..., description="Current status: ACTIVE, ACKNOWLEDGED, RESOLVED, EXPIRED")
    acknowledged_at: Optional[str] = Field(None, description="When someone acknowledged this alert")
    acknowledged_by: Optional[str] = Field(None, description="Who acknowledged this alert")
    resolved_at: Optional[str] = Field(None, description="When this alert was resolved")
    
    # 📬 DELIVERY TRACKING
    channels_notified: List[str] = Field(default_factory=list, description="Which channels received notifications")
    delivery_failures: List[str] = Field(default_factory=list, description="Any notification delivery errors")
    
    # 🔄 ESCALATION TRACKING
    escalated: bool = Field(False, description="Has this alert been escalated")
    escalated_at: Optional[str] = Field(None, description="When was it escalated")
    escalation_level: int = Field(0, description="Current escalation level")


class AlertAcknowledgeRequest(BaseModel):
    """
    ✅ ACKNOWLEDGE ALERT REQUEST - "I Got The Message!"
    
    This is like signing a form to confirm you received an emergency
    notification and are taking action. It lets the system know that
    someone is handling the situation.
    """
    acknowledged_by: str = Field(..., description="Name or ID of person acknowledging the alert")


class AlertStatsResponse(BaseModel):
    """
    📊 ALERT SYSTEM STATISTICS - Performance Dashboard
    
    This is like a monthly report on how the emergency response system
    is performing. It shows how many alerts were sent, which types are
    most common, and how quickly issues are being resolved.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a school safety report that shows:
    - How many fire drills happened this month
    - Which buildings had the most alarms
    - How quickly students evacuated on average
    - Which safety systems are working best
    """
    
    # 📊 CURRENT STATUS
    active_alerts: int = Field(..., description="Number of unresolved alerts")
    total_rules: int = Field(..., description="Total number of alert rules configured")
    enabled_rules: int = Field(..., description="Number of currently active rules")
    alert_history_size: int = Field(..., description="Number of alerts in history")
    
    # 📈 DETAILED STATISTICS
    statistics: Dict[str, Any] = Field(..., description="Comprehensive alert system metrics")
    
    # 🕒 RECENT ACTIVITY
    recent_alerts: List[Dict[str, Any]] = Field(..., description="Summary of recent alerts")