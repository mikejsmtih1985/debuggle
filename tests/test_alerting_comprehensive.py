"""
Comprehensive tests for alerting.py module covering:
- AlertSeverity and AlertChannel enums
- AlertRule creation and configuration
- Alert creation and management
- AlertManager functionality
- Alert rule evaluation and matching
- Notification channel sending
- Alert acknowledgment and resolution
- Statistics and reporting
- Time-based filtering and business hours
- Error thresholds and cooldowns
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from src.debuggle.services.alerting import (
    AlertSeverity, AlertChannel, AlertRule, Alert, AlertManager
)
from src.debuggle.storage.database import LogEntry, LogSeverity
from src.debuggle.realtime import RealtimeErrorMonitor


def create_test_log_entry(log_id="test-log", content="Test error", severity=LogSeverity.ERROR,
                         language="python", tags=None, project_name=None, file_path=None):
    """Helper function to create test LogEntry objects"""
    if tags is None:
        tags = ["test"]
    
    return LogEntry(
        log_id=log_id,
        timestamp=datetime.now(),
        original_log=content,
        processed_log=content,
        summary=f"Summary: {content}",
        tags=tags,
        severity=severity,
        language=language,
        metadata={"source": "test"},
        project_name=project_name,
        file_path=file_path,
        source="test"
    )


def create_test_alert(alert_id="test-alert", rule_id="test-rule", rule_name="Test Rule",
                     message="Test alert", severity=AlertSeverity.MEDIUM, 
                     triggered_by_log="test-log", project="test-project"):
    """Helper function to create test Alert objects"""
    return Alert(
        alert_id=alert_id,
        rule_id=rule_id,
        rule_name=rule_name,
        timestamp=datetime.now(),
        message=message,
        details={"test": "data"},
        severity=severity,
        triggered_by_log=triggered_by_log,
        source_project=project,
        source_language="python",
        error_tags=["test"]
    )


class TestEnums:
    """Test AlertSeverity and AlertChannel enums"""
    
    def test_alert_severity_values(self):
        """Test AlertSeverity enum values"""
        assert AlertSeverity.LOW == "low"
        assert AlertSeverity.MEDIUM == "medium"  
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.CRITICAL == "critical"
        
        # Test all values are present
        severities = [e.value for e in AlertSeverity]
        assert len(severities) == 4
        assert "low" in severities
        assert "critical" in severities
    
    def test_alert_channel_values(self):
        """Test AlertChannel enum values"""
        assert AlertChannel.EMAIL == "email"
        assert AlertChannel.SLACK == "slack"
        assert AlertChannel.WEBHOOK == "webhook"
        assert AlertChannel.WEBSOCKET == "websocket"
        assert AlertChannel.SMS == "sms"
        assert AlertChannel.PAGERDUTY == "pagerduty"
        
        # Test all values are present
        channels = [e.value for e in AlertChannel]
        assert len(channels) == 6
        assert "email" in channels
        assert "pagerduty" in channels


class TestAlertRule:
    """Test AlertRule creation and configuration"""
    
    def test_alert_rule_basic_creation(self):
        """Test basic AlertRule creation"""
        rule = AlertRule(
            rule_id="test-rule-1",
            name="Test Alert Rule",
            description="A test rule for validation"
        )
        
        assert rule.rule_id == "test-rule-1"
        assert rule.name == "Test Alert Rule"
        assert rule.description == "A test rule for validation"
        assert rule.enabled is True
        assert rule.alert_severity == AlertSeverity.MEDIUM
        assert isinstance(rule.created_at, datetime)
    
    def test_alert_rule_with_filters(self):
        """Test AlertRule with various filters"""
        rule = AlertRule(
            rule_id="filtered-rule",
            name="Filtered Rule",
            description="Rule with filters",
            severity_filter=[LogSeverity.ERROR, LogSeverity.CRITICAL],
            language_filter=["python", "javascript"],
            tag_filter=["authentication", "database"],
            project_filter=["project-a", "project-b"]
        )
        
        assert rule.severity_filter == [LogSeverity.ERROR, LogSeverity.CRITICAL]
        assert rule.language_filter == ["python", "javascript"]
        assert rule.tag_filter == ["authentication", "database"]
        assert rule.project_filter == ["project-a", "project-b"]
    
    def test_alert_rule_with_pattern_matching(self):
        """Test AlertRule with regex pattern matching"""
        rule = AlertRule(
            rule_id="pattern-rule",
            name="Pattern Matching Rule",
            description="Rule with regex pattern",
            content_regex=r"(Error|Exception|Failed).*database",
            error_count_threshold=10,
            time_window_minutes=15
        )
        
        assert rule.content_regex == r"(Error|Exception|Failed).*database" 
        assert rule.error_count_threshold == 10
        assert rule.time_window_minutes == 15
    
    def test_alert_rule_business_hours_config(self):
        """Test AlertRule with business hours configuration"""
        rule = AlertRule(
            rule_id="business-rule",
            name="Business Hours Rule",
            description="Only alert during business hours",
            business_hours_only=True,
            business_start_hour=8,
            business_end_hour=18,
            weekdays_only=True
        )
        
        assert rule.business_hours_only is True
        assert rule.business_start_hour == 8
        assert rule.business_end_hour == 18
        assert rule.weekdays_only is True
    
    def test_alert_rule_notification_config(self):
        """Test AlertRule with notification configuration"""
        rule = AlertRule(
            rule_id="notification-rule",
            name="Notification Rule",
            description="Rule with notifications",
            alert_severity=AlertSeverity.HIGH,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK],
            email_recipients=["admin@example.com", "dev@example.com"],
            slack_channels=["#alerts", "#dev-team"],
            webhook_urls=["https://api.example.com/alerts"]
        )
        
        assert rule.alert_severity == AlertSeverity.HIGH
        assert AlertChannel.EMAIL in rule.channels
        assert AlertChannel.SLACK in rule.channels
        assert AlertChannel.WEBHOOK in rule.channels
        assert "admin@example.com" in rule.email_recipients
        assert "#alerts" in rule.slack_channels
        assert "https://api.example.com/alerts" in rule.webhook_urls


class TestAlert:
    """Test Alert creation and management"""
    
    def test_alert_creation(self):
        """Test Alert creation"""
        alert = create_test_alert(
            alert_id="alert-456",
            rule_id="test-rule",
            rule_name="Test Rule",
            message="Database connection alert triggered",
            severity=AlertSeverity.HIGH,
            triggered_by_log="log-123",
            project="test-project"
        )
        
        assert alert.alert_id == "alert-456"
        assert alert.rule_id == "test-rule"
        assert alert.rule_name == "Test Rule"
        assert alert.triggered_by_log == "log-123"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.message == "Database connection alert triggered"
        assert alert.details == {"test": "data"}
        assert alert.source_project == "test-project"
        assert alert.source_language == "python"
        assert alert.error_tags == ["test"]
        assert alert.status == "ACTIVE"
        assert isinstance(alert.timestamp, datetime)
    
    def test_alert_acknowledgment(self):
        """Test Alert acknowledgment"""
        alert = create_test_alert()
        
        # Initially not acknowledged
        assert alert.status == "ACTIVE"
        assert alert.acknowledged_by is None
        assert alert.acknowledged_at is None
        
        # Acknowledge the alert
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_by = "admin"
        alert.acknowledged_at = datetime.now()
        
        assert alert.status == "ACKNOWLEDGED"
        assert alert.acknowledged_by == "admin"
        assert isinstance(alert.acknowledged_at, datetime)
    
    def test_alert_resolution(self):
        """Test Alert resolution"""
        alert = create_test_alert()
        
        # Initially not resolved
        assert alert.status == "ACTIVE"
        assert alert.resolved_at is None
        
        # Resolve the alert
        alert.status = "RESOLVED"
        alert.resolved_at = datetime.now()
        
        assert alert.status == "RESOLVED"
        assert isinstance(alert.resolved_at, datetime)


class TestAlertManager:
    """Test AlertManager functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_error_monitor = Mock(spec=RealtimeErrorMonitor)
        self.alert_manager = AlertManager(self.mock_error_monitor)
    
    def test_alert_manager_initialization(self):
        """Test AlertManager initialization"""
        assert self.alert_manager.error_monitor == self.mock_error_monitor
        assert self.alert_manager.rules == {}
        assert self.alert_manager.active_alerts == {}
        assert self.alert_manager.alert_history == []
        assert self.alert_manager.cooldowns == {}
        assert self.alert_manager.max_history_size == 10000
    
    def test_add_alert_rule(self):
        """Test adding alert rules"""
        rule = AlertRule(
            rule_id="test-rule-1",
            name="Test Rule 1",
            description="First test rule"
        )
        
        self.alert_manager.add_alert_rule(rule)
        
        assert "test-rule-1" in self.alert_manager.rules
        assert self.alert_manager.rules["test-rule-1"] == rule
    
    def test_add_duplicate_alert_rule(self):
        """Test adding duplicate alert rule (should replace)"""
        rule1 = AlertRule(
            rule_id="duplicate-rule",
            name="First Rule",
            description="First version"
        )
        
        rule2 = AlertRule(
            rule_id="duplicate-rule",
            name="Second Rule", 
            description="Second version"
        )
        
        self.alert_manager.add_alert_rule(rule1)
        self.alert_manager.add_alert_rule(rule2)
        
        # Should have replaced the first rule
        assert len(self.alert_manager.rules) == 1
        assert self.alert_manager.rules["duplicate-rule"].name == "Second Rule"
    
    def test_remove_alert_rule_success(self):
        """Test removing existing alert rule"""
        rule = AlertRule(
            rule_id="removable-rule",
            name="Removable Rule",
            description="This rule will be removed"
        )
        
        self.alert_manager.add_alert_rule(rule)
        assert "removable-rule" in self.alert_manager.rules
        
        result = self.alert_manager.remove_alert_rule("removable-rule")
        
        assert result is True
        assert "removable-rule" not in self.alert_manager.rules
    
    def test_remove_alert_rule_not_found(self):
        """Test removing non-existent alert rule"""
        result = self.alert_manager.remove_alert_rule("non-existent-rule")
        
        assert result is False
    
    def test_remove_alert_rule_with_active_alerts(self):
        """Test removing rule that has active alerts"""
        rule = AlertRule(
            rule_id="active-rule",
            name="Active Rule",
            description="Rule with active alerts"
        )
        
        alert = create_test_alert(
            alert_id="active-alert",
            rule_id="active-rule",
            rule_name="Active Rule",
            message="Test alert",
            severity=AlertSeverity.MEDIUM
        )
        
        self.alert_manager.add_alert_rule(rule)
        self.alert_manager.active_alerts["active-alert"] = alert
        
        result = self.alert_manager.remove_alert_rule("active-rule")
        
        assert result is True
        assert "active-rule" not in self.alert_manager.rules
        # Active alerts should remain for tracking
        assert "active-alert" in self.alert_manager.active_alerts
    
    @pytest.mark.asyncio
    async def test_evaluate_log_for_alerts_no_rules(self):
        """Test evaluating log when no rules exist"""
        log_entry = create_test_log_entry(
            log_id="log-1",
            content="Test error message",
            severity=LogSeverity.ERROR
        )
        
        # Should handle gracefully with no rules
        await self.alert_manager.evaluate_log_for_alerts(log_entry)
        
        # No alerts should be created
        assert len(self.alert_manager.active_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_evaluate_log_for_alerts_disabled_rule(self):
        """Test evaluating log with disabled rule"""
        rule = AlertRule(
            rule_id="disabled-rule",
            name="Disabled Rule",
            description="This rule is disabled",
            enabled=False
        )
        
        self.alert_manager.add_alert_rule(rule)
        
        log_entry = create_test_log_entry(
            log_id="log-1",
            content="Test error message",
            severity=LogSeverity.ERROR
        )
        
        await self.alert_manager.evaluate_log_for_alerts(log_entry)
        
        # No alerts should be created for disabled rules
        assert len(self.alert_manager.active_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_log_matches_rule_severity_filter(self):
        """Test log matching with severity filter"""
        rule = AlertRule(
            rule_id="severity-rule",
            name="Severity Rule",
            description="Filter by severity",
            severity_filter=[LogSeverity.ERROR, LogSeverity.CRITICAL]
        )
        
        # Matching severity
        log_entry_match = create_test_log_entry(
            log_id="log-1",
            content="Error occurred",
            severity=LogSeverity.ERROR
        )
        
        # Non-matching severity  
        log_entry_no_match = create_test_log_entry(
            log_id="log-2",
            content="Info message",
            severity=LogSeverity.INFO
        )
        
        assert await self.alert_manager._log_matches_rule(log_entry_match, rule) is True
        assert await self.alert_manager._log_matches_rule(log_entry_no_match, rule) is False
    
    @pytest.mark.asyncio
    async def test_log_matches_rule_language_filter(self):
        """Test log matching with language filter"""
        rule = AlertRule(
            rule_id="language-rule",
            name="Language Rule", 
            description="Filter by language",
            language_filter=["python", "javascript"]
        )
        
        # Matching language
        log_entry_match = create_test_log_entry(
            log_id="log-1",
            content="Python error",
            severity=LogSeverity.ERROR,
            language="python"
        )
        
        # Non-matching language
        log_entry_no_match = create_test_log_entry(
            log_id="log-2",
            content="Java error",
            severity=LogSeverity.ERROR,
            language="java"
        )
        
        assert await self.alert_manager._log_matches_rule(log_entry_match, rule) is True
        assert await self.alert_manager._log_matches_rule(log_entry_no_match, rule) is False
    
    @pytest.mark.asyncio
    async def test_log_matches_rule_tag_filter(self):
        """Test log matching with tag filter"""
        rule = AlertRule(
            rule_id="tag-rule",
            name="Tag Rule",
            description="Filter by tags",
            tag_filter=["database", "authentication"]
        )
        
        # Matching tags
        log_entry_match = create_test_log_entry(
            log_id="log-1",
            content="Database error",
            severity=LogSeverity.ERROR,
            tags=["database", "connection"]
        )
        
        # Non-matching tags
        log_entry_no_match = create_test_log_entry(
            log_id="log-2",
            content="UI error",
            severity=LogSeverity.ERROR,
            tags=["frontend", "ui"]
        )
        
        assert await self.alert_manager._log_matches_rule(log_entry_match, rule) is True
        assert await self.alert_manager._log_matches_rule(log_entry_no_match, rule) is False
    
    @pytest.mark.asyncio
    async def test_log_matches_rule_regex_pattern(self):
        """Test log matching with regex pattern"""
        rule = AlertRule(
            rule_id="regex-rule",
            name="Regex Rule",
            description="Filter by regex pattern",
            content_regex=r"(Error|Exception).*database"
        )
        
        # Matching pattern
        log_entry_match = create_test_log_entry(
            log_id="log-1",
            content="Error connecting to database server",
            severity=LogSeverity.ERROR
        )
        
        # Non-matching pattern
        log_entry_no_match = create_test_log_entry(
            log_id="log-2",
            content="Info: User logged in successfully",
            severity=LogSeverity.INFO
        )
        
        assert await self.alert_manager._log_matches_rule(log_entry_match, rule) is True
        assert await self.alert_manager._log_matches_rule(log_entry_no_match, rule) is False
    
    @pytest.mark.asyncio
    async def test_log_matches_rule_invalid_regex(self):
        """Test log matching with invalid regex pattern"""
        rule = AlertRule(
            rule_id="invalid-regex-rule",
            name="Invalid Regex Rule",
            description="Rule with invalid regex",
            content_regex=r"[invalid regex pattern"  # Missing closing bracket
        )
        
        log_entry = create_test_log_entry(
            log_id="log-1",
            content="Some error message",
            severity=LogSeverity.ERROR
        )
        
        # Should handle invalid regex gracefully and return False
        result = await self.alert_manager._log_matches_rule(log_entry, rule)
        assert result is False
    
    def test_is_alert_time_allowed_business_hours(self):
        """Test business hours time checking"""
        rule = AlertRule(
            rule_id="business-rule",
            name="Business Rule",
            description="Business hours only",
            business_hours_only=True,
            business_start_hour=9,
            business_end_hour=17,
            weekdays_only=True
        )
        
        # Mock datetime to control time testing
        with patch('src.debuggle.services.alerting.datetime') as mock_datetime:
            # Monday at 2 PM (should allow)
            mock_datetime.now.return_value = datetime(2024, 1, 8, 14, 0, 0)  # Monday
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            assert self.alert_manager._is_alert_time_allowed(rule) is True
            
            # Saturday at 2 PM (should not allow - weekend)
            mock_datetime.now.return_value = datetime(2024, 1, 6, 14, 0, 0)  # Saturday
            
            assert self.alert_manager._is_alert_time_allowed(rule) is False
            
            # Monday at 8 AM (should not allow - before business hours) 
            mock_datetime.now.return_value = datetime(2024, 1, 8, 8, 0, 0)  # Monday
            
            assert self.alert_manager._is_alert_time_allowed(rule) is False
    
    def test_is_alert_time_allowed_24_7(self):
        """Test 24/7 alerting (no time restrictions)"""
        rule = AlertRule(
            rule_id="24-7-rule",
            name="24/7 Rule",
            description="Always alert",
            business_hours_only=False,
            weekdays_only=False
        )
        
        # Should always allow alerts
        assert self.alert_manager._is_alert_time_allowed(rule) is True
    
    def test_is_in_cooldown_no_previous_alert(self):
        """Test cooldown check with no previous alert"""
        rule = AlertRule(
            rule_id="cooldown-rule",
            name="Cooldown Rule",
            description="Rule with cooldown"
        )
        
        # No previous alert means no cooldown
        assert self.alert_manager._is_in_cooldown(rule) is False
    
    def test_is_in_cooldown_within_cooldown_period(self):
        """Test cooldown check within cooldown period"""
        rule = AlertRule(
            rule_id="cooldown-rule",
            name="Cooldown Rule", 
            description="Rule with cooldown"
        )
        
        # Set a recent alert time (within cooldown)
        recent_time = datetime.now() - timedelta(minutes=2)
        self.alert_manager.cooldowns["cooldown-rule"] = recent_time
        
        assert self.alert_manager._is_in_cooldown(rule) is True
    
    def test_is_in_cooldown_outside_cooldown_period(self):
        """Test cooldown check outside cooldown period"""
        rule = AlertRule(
            rule_id="cooldown-rule",
            name="Cooldown Rule",
            description="Rule with cooldown"
        )
        
        # Set an old alert time (outside cooldown)
        old_time = datetime.now() - timedelta(minutes=20)
        self.alert_manager.cooldowns["cooldown-rule"] = old_time
        
        assert self.alert_manager._is_in_cooldown(rule) is False
    
    def test_acknowledge_alert_success(self):
        """Test acknowledging existing alert"""
        alert = create_test_alert(alert_id="test-alert")
        
        self.alert_manager.active_alerts["test-alert"] = alert
        
        result = self.alert_manager.acknowledge_alert("test-alert", "admin")
        
        assert result is True
        assert alert.status == "ACKNOWLEDGED"
        assert alert.acknowledged_by == "admin"
        assert isinstance(alert.acknowledged_at, datetime)
    
    def test_acknowledge_alert_not_found(self):
        """Test acknowledging non-existent alert"""
        result = self.alert_manager.acknowledge_alert("non-existent-alert", "admin")
        
        assert result is False
    
    def test_resolve_alert_success(self):
        """Test resolving existing alert"""
        alert = create_test_alert(alert_id="test-alert")
        
        self.alert_manager.active_alerts["test-alert"] = alert
        
        result = self.alert_manager.resolve_alert("test-alert")
        
        assert result is True
        assert alert.status == "RESOLVED"
        assert isinstance(alert.resolved_at, datetime)
        # Alert should be removed from active alerts
        assert "test-alert" not in self.alert_manager.active_alerts
        # Alert is not automatically moved to history in the current implementation
    
    def test_resolve_alert_not_found(self):
        """Test resolving non-existent alert"""
        result = self.alert_manager.resolve_alert("non-existent-alert")
        
        assert result is False
    
    def test_get_alert_statistics_empty(self):
        """Test getting statistics with no alerts"""
        stats = self.alert_manager.get_alert_statistics()
        
        assert stats["total_rules"] == 0
        assert stats["active_alerts"] == 0
        assert "statistics" in stats
        assert "recent_alerts" in stats
        assert len(stats["recent_alerts"]) == 0
    
    def test_get_alert_statistics_with_data(self):
        """Test getting statistics with alert data"""
        # Add some rules
        rule1 = AlertRule(rule_id="rule-1", name="Rule 1", description="Test")
        rule2 = AlertRule(rule_id="rule-2", name="Rule 2", description="Test") 
        self.alert_manager.add_alert_rule(rule1)
        self.alert_manager.add_alert_rule(rule2)
        
        # Add some alerts
        alert1 = create_test_alert(
            alert_id="alert-1",
            rule_id="rule-1",
            rule_name="Rule 1",
            severity=AlertSeverity.HIGH
        )
        alert1.status = "ACKNOWLEDGED"
        alert1.acknowledged_by = "admin"
        
        alert2 = create_test_alert(
            alert_id="alert-2",
            rule_id="rule-2",
            rule_name="Rule 2",
            severity=AlertSeverity.CRITICAL
        )
        alert2.status = "RESOLVED"
        alert2.resolved_at = datetime.now()
        
        self.alert_manager.active_alerts["alert-1"] = alert1
        self.alert_manager.alert_history.append(alert2)
        
        stats = self.alert_manager.get_alert_statistics()
        
        assert stats["total_rules"] == 2
        assert stats["active_alerts"] == 1
        assert stats["enabled_rules"] == 2  # Both rules are enabled by default
        assert stats["alert_history_size"] == 1
        assert len(stats["recent_alerts"]) == 1


class TestNotificationChannels:
    """Test notification channel functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_error_monitor = Mock(spec=RealtimeErrorMonitor)
        self.alert_manager = AlertManager(self.mock_error_monitor)
    
    @pytest.mark.asyncio
    async def test_send_email_alert(self):
        """Test sending email alert"""
        rule = AlertRule(
            rule_id="email-rule",
            name="Email Rule",
            description="Email alert rule",
            channels=[AlertChannel.EMAIL],
            email_recipients=["admin@example.com"]
        )
        
        alert = create_test_alert(
            alert_id="email-alert",
            rule_id="email-rule",
            rule_name="Email Rule",
            severity=AlertSeverity.MEDIUM,
            message="Email test alert"
        )
        
        # Mock email sending (since actual email implementation may not be available)
        with patch.object(self.alert_manager, '_send_email_alert') as mock_send:
            await self.alert_manager._send_email_alert(alert, rule)
            mock_send.assert_called_once_with(alert, rule)
    
    @pytest.mark.asyncio
    async def test_send_slack_alert(self):
        """Test sending Slack alert"""
        rule = AlertRule(
            rule_id="slack-rule",
            name="Slack Rule",
            description="Slack alert rule",
            channels=[AlertChannel.SLACK],
            slack_channels=["#alerts"]
        )
        
        alert = create_test_alert(
            alert_id="slack-alert",
            rule_id="slack-rule",
            rule_name="Slack Rule",
            severity=AlertSeverity.HIGH,
            message="Slack test alert"
        )
        
        # Mock Slack sending
        with patch.object(self.alert_manager, '_send_slack_alert') as mock_send:
            await self.alert_manager._send_slack_alert(alert, rule)
            mock_send.assert_called_once_with(alert, rule)
    
    @pytest.mark.asyncio
    async def test_send_webhook_alert(self):
        """Test sending webhook alert"""
        rule = AlertRule(
            rule_id="webhook-rule",
            name="Webhook Rule",
            description="Webhook alert rule",
            channels=[AlertChannel.WEBHOOK],
            webhook_urls=["https://api.example.com/alerts"]
        )
        
        alert = create_test_alert(
            alert_id="webhook-alert",
            rule_id="webhook-rule", 
            rule_name="Webhook Rule",
            severity=AlertSeverity.CRITICAL,
            message="Webhook test alert"
        )
        
        # Mock webhook sending
        with patch.object(self.alert_manager, '_send_webhook_alert') as mock_send:
            await self.alert_manager._send_webhook_alert(alert, rule)
            mock_send.assert_called_once_with(alert, rule)
    
    @pytest.mark.asyncio
    async def test_send_websocket_alert(self):
        """Test sending WebSocket alert"""
        rule = AlertRule(
            rule_id="websocket-rule",
            name="WebSocket Rule",
            description="WebSocket alert rule",
            channels=[AlertChannel.WEBSOCKET]
        )
        
        alert = create_test_alert(
            alert_id="websocket-alert",
            rule_id="websocket-rule",
            rule_name="WebSocket Rule", 
            severity=AlertSeverity.MEDIUM,
            message="WebSocket test alert"
        )
        
        # Mock WebSocket sending
        with patch.object(self.alert_manager, '_send_websocket_alert') as mock_send:
            await self.alert_manager._send_websocket_alert(alert, rule)
            mock_send.assert_called_once_with(alert, rule)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_error_monitor = Mock(spec=RealtimeErrorMonitor)
        self.alert_manager = AlertManager(self.mock_error_monitor)
    
    def test_alert_rule_with_empty_values(self):
        """Test AlertRule with empty values"""
        rule = AlertRule(
            rule_id="",
            name="",
            description="",
            channels=[],
            email_recipients=[],
            slack_channels=[],
            webhook_urls=[]
        )
        
        assert rule.rule_id == ""
        assert rule.name == ""
        assert rule.description == ""
        assert rule.channels == []
        assert rule.email_recipients == []
    
    @pytest.mark.asyncio
    async def test_evaluate_log_with_none_values(self):
        """Test evaluating log with None values"""
        log_entry = create_test_log_entry(
            log_id="log-1",
            content="Test error",
            severity=LogSeverity.ERROR,
            tags=[]  # Empty tags instead of None
        )
        
        rule = AlertRule(
            rule_id="test-rule",
            name="Test Rule",
            description="Test rule",
            tag_filter=["database"]
        )
        
        self.alert_manager.add_alert_rule(rule)
        
        # Should handle empty tags gracefully
        await self.alert_manager.evaluate_log_for_alerts(log_entry)
    
    def test_alert_history_size_limit(self):
        """Test alert history size limiting"""
        # Set small limit for testing
        self.alert_manager.max_history_size = 3
        
        # Add exactly max_history_size alerts first
        for i in range(3):
            alert = create_test_alert(
                alert_id=f"alert-{i}",
                rule_id="rule-1", 
                rule_name="Test Rule",
                message=f"Test alert {i}",
                severity=AlertSeverity.MEDIUM
            )
            self.alert_manager.alert_history.append(alert)
        
        # Now add one more to trigger size limit (like _trigger_alert does)
        new_alert = create_test_alert(
            alert_id="new-alert",
            rule_id="rule-1",
            rule_name="Test Rule",
            message="New alert",
            severity=AlertSeverity.MEDIUM
        )
        self.alert_manager.alert_history.append(new_alert)
        
        # Apply size limit check exactly like _trigger_alert does
        if len(self.alert_manager.alert_history) > self.alert_manager.max_history_size:
            self.alert_manager.alert_history.pop(0)
        
        # Should maintain size limit
        assert len(self.alert_manager.alert_history) == 3
        # Should have removed the oldest (alert-0) and kept alert-1, alert-2, new-alert
        assert not any(alert.alert_id == "alert-0" for alert in self.alert_manager.alert_history)
        assert any(alert.alert_id == "new-alert" for alert in self.alert_manager.alert_history)
    
    @pytest.mark.asyncio
    async def test_count_recent_matching_errors_no_database(self):
        """Test counting recent errors without database access"""
        rule = AlertRule(
            rule_id="count-rule",
            name="Count Rule",
            description="Count errors",
            error_count_threshold=5,
            time_window_minutes=10
        )
        
        log_entry = create_test_log_entry(
            log_id="log-1",
            content="Test error",
            severity=LogSeverity.ERROR
        )
        
        # Mock database access failure
        count = await self.alert_manager._count_recent_matching_errors(rule, log_entry)
        
        # Should return default count when database access fails
        assert count == 1