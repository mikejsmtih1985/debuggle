"""
Comprehensive tests for database.py module covering:
- TierLevel and LogSeverity enums
- LogEntry dataclass creation and validation
- LogStats dataclass functionality
- DatabaseManager initialization and database setup
- Log storage and retrieval operations
- Advanced search functionality with multiple filters
- Statistics and analytics generation
- Database maintenance operations (cleanup, vacuum)
- Error handling and edge cases
- Database schema validation
- Concurrent access scenarios
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import json

from src.debuggle.storage.database import (
    TierLevel, LogSeverity, LogEntry, LogStats, DatabaseManager
)


def create_test_log_entry(
    log_id="test-log-123",
    original_log="Test error message",
    severity=LogSeverity.ERROR,
    language="python",
    tags=None,
    project_name="test-project",
    file_path="/path/to/test.py"
):
    """Helper function to create test LogEntry objects"""
    if tags is None:
        tags = ["test", "error"]
    
    return LogEntry(
        log_id=log_id,
        timestamp=datetime.now(),
        original_log=original_log,
        processed_log=f"Processed: {original_log}",
        summary=f"Summary: {original_log}",
        tags=tags,
        severity=severity,
        language=language,
        metadata={"source": "test", "version": "1.0"},
        project_name=project_name,
        file_path=file_path,
        source="test"
    )


class TestEnums:
    """Test TierLevel and LogSeverity enums"""
    
    def test_tier_level_values(self):
        """Test TierLevel enum values"""
        assert TierLevel.FREE == "free"
        assert TierLevel.PRO == "pro"
        assert TierLevel.ENTERPRISE == "enterprise"
        
        # Test all values are present
        tier_values = [e.value for e in TierLevel]
        assert len(tier_values) == 3
        assert "free" in tier_values
        assert "enterprise" in tier_values
    
    def test_log_severity_values(self):
        """Test LogSeverity enum values"""
        assert LogSeverity.TRACE == "trace"
        assert LogSeverity.DEBUG == "debug"
        assert LogSeverity.INFO == "info"
        assert LogSeverity.WARNING == "warning"
        assert LogSeverity.ERROR == "error"
        assert LogSeverity.CRITICAL == "critical"
        
        # Test all values are present
        severity_values = [e.value for e in LogSeverity]
        assert len(severity_values) == 6
        assert "trace" in severity_values
        assert "debug" in severity_values
        assert "critical" in severity_values
    
    def test_enum_string_comparison(self):
        """Test that enums can be compared with strings"""
        assert LogSeverity.ERROR == "error"
        assert TierLevel.PRO == "pro"
        assert LogSeverity.INFO != "error"
        assert TierLevel.FREE != "pro"


class TestLogEntry:
    """Test LogEntry dataclass creation and validation"""
    
    def test_log_entry_creation_minimal(self):
        """Test LogEntry creation with minimal required fields"""
        entry = create_test_log_entry()
        
        assert entry.log_id == "test-log-123"
        assert entry.original_log == "Test error message"
        assert entry.processed_log == "Processed: Test error message"
        assert entry.summary == "Summary: Test error message"
        assert entry.severity == LogSeverity.ERROR
        assert entry.language == "python"
        assert isinstance(entry.timestamp, datetime)
        assert isinstance(entry.tags, list)
        assert entry.tags == ["test", "error"]
        assert entry.project_name == "test-project"
        assert entry.file_path == "/path/to/test.py"
        assert entry.source == "test"
    
    def test_log_entry_creation_full(self):
        """Test LogEntry creation with all fields populated"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        metadata = {"error_type": "ValueError", "line_number": 42, "function": "process_data"}
        
        entry = LogEntry(
            log_id="full-log-456",
            timestamp=timestamp,
            original_log="ValueError: Invalid input data format",
            processed_log="🔴 ValueError: Invalid input data format\n  File: data_processor.py, Line: 42",
            summary="Input validation error in data processor",
            tags=["validation", "input", "data_processing"],
            severity=LogSeverity.CRITICAL,
            language="python",
            metadata=metadata,
            project_name="data-pipeline",
            file_path="/src/data_processor.py",
            source="api_upload"
        )
        
        assert entry.log_id == "full-log-456"
        assert entry.timestamp == timestamp
        assert "ValueError" in entry.original_log
        assert "🔴" in entry.processed_log
        assert entry.summary is not None and "validation error" in entry.summary
        assert entry.tags == ["validation", "input", "data_processing"]
        assert entry.severity == LogSeverity.CRITICAL
        assert entry.language == "python"
        assert entry.metadata == metadata
        assert entry.metadata["line_number"] == 42
        assert entry.project_name == "data-pipeline"
        assert entry.file_path == "/src/data_processor.py"
        assert entry.source == "api_upload"
    
    def test_log_entry_with_none_values(self):
        """Test LogEntry handling of None values"""
        entry = LogEntry(
            log_id="none-test",
            timestamp=datetime.now(),
            original_log="Test message",
            processed_log="Processed test",
            summary=None,  # None summary
            tags=[],  # Empty tags
            severity=LogSeverity.INFO,
            language="unknown",
            metadata={},  # Empty metadata
            project_name=None,  # None project
            file_path=None,  # None file path
            source="test"
        )
        
        assert entry.summary is None
        assert entry.tags == []
        assert entry.metadata == {}
        assert entry.project_name is None
        assert entry.file_path is None
    
    def test_log_entry_serialization(self):
        """Test LogEntry can be converted to dict for JSON serialization"""
        entry = create_test_log_entry()
        
        # Should be able to convert to dict
        entry_dict = {
            'log_id': entry.log_id,
            'timestamp': entry.timestamp.isoformat(),
            'original_log': entry.original_log,
            'processed_log': entry.processed_log,
            'summary': entry.summary,
            'tags': entry.tags,
            'severity': entry.severity.value,
            'language': entry.language,
            'metadata': entry.metadata,
            'project_name': entry.project_name,
            'file_path': entry.file_path,
            'source': entry.source
        }
        
        # Should be serializable to JSON
        json_str = json.dumps(entry_dict)
        assert isinstance(json_str, str)
        assert "test-log-123" in json_str


class TestLogStats:
    """Test LogStats dataclass functionality"""
    
    def test_log_stats_creation(self):
        """Test LogStats creation with various metrics"""
        stats = LogStats(
            total_logs=1500,
            logs_today=50,
            logs_this_week=350,
            logs_this_month=1200,
            top_error_types={
                "connection": 300,
                "validation": 250,
                "authentication": 200
            },
            top_languages={
                "python": 800,
                "javascript": 400,
                "java": 200,
                "golang": 100
            },
            top_severity_levels={
                "error": 600,
                "warning": 500,
                "info": 300,
                "critical": 80,
                "debug": 20
            },
            errors_per_day_last_week=[45, 52, 38, 67, 43, 39, 41],
            severity_trends={
                "error": [50, 55, 48, 62, 59],
                "warning": [30, 35, 28, 40, 37]
            },
            busiest_hours={9: 150, 10: 180, 14: 160, 15: 175},
            busiest_days={"Monday": 220, "Tuesday": 195, "Wednesday": 210},
            oldest_log_date=datetime(2024, 1, 1),
            newest_log_date=datetime(2024, 1, 15),
            last_updated=datetime(2024, 1, 15, 12, 0, 0)
        )
        
        assert stats.total_logs == 1500
        assert stats.logs_today == 50
        assert stats.logs_this_week == 350
        assert stats.top_error_types["connection"] == 300
        assert stats.top_languages["python"] == 800
        assert stats.top_severity_levels["error"] == 600
        assert len(stats.errors_per_day_last_week) == 7
        assert stats.busiest_hours[10] == 180
        assert stats.busiest_days["Monday"] == 220
        assert isinstance(stats.oldest_log_date, datetime)
        assert isinstance(stats.newest_log_date, datetime)
        assert isinstance(stats.last_updated, datetime)
    
    def test_log_stats_empty(self):
        """Test LogStats with empty/zero values"""
        stats = LogStats(
            total_logs=0,
            logs_today=0,
            logs_this_week=0,
            logs_this_month=0,
            top_error_types={},
            top_languages={},
            top_severity_levels={},
            errors_per_day_last_week=[0, 0, 0, 0, 0, 0, 0],
            severity_trends={},
            busiest_hours={},
            busiest_days={},
            oldest_log_date=None,
            newest_log_date=None,
            last_updated=datetime.now()
        )
        
        assert stats.total_logs == 0
        assert stats.logs_today == 0
        assert stats.logs_this_week == 0
        assert stats.top_error_types == {}
        assert stats.top_languages == {}
        assert stats.top_severity_levels == {}
        assert len(stats.errors_per_day_last_week) == 7
        assert stats.oldest_log_date is None
        assert stats.newest_log_date is None


class TestDatabaseManager:
    """Test DatabaseManager initialization and core functionality"""
    
    def setup_method(self):
        """Set up test fixtures with temporary database"""
        # Create temporary database file for each test
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Initialize database manager with temp database
        self.db_manager = DatabaseManager(database_path=self.db_path)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        # Close any open connections and remove temp database
        if hasattr(self, 'db_manager'):
            del self.db_manager
        
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization creates database and tables"""
        assert os.path.exists(self.db_path)
        assert Path(self.db_path).is_file()
        
        # Test that database has correct schema
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check that logs table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'logs'
            
            # Check table structure
            cursor.execute("PRAGMA table_info(logs)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            expected_columns = [
                'log_id', 'timestamp', 'original_log', 'processed_log',
                'summary', 'tags', 'severity', 'language', 'metadata',
                'project_name', 'file_path', 'source'
            ]
            
            for expected_col in expected_columns:
                assert expected_col in column_names
    
    def test_database_initialization_with_custom_path(self):
        """Test DatabaseManager with custom database path"""
        custom_path = tempfile.mktemp(suffix='.db')
        
        try:
            custom_db = DatabaseManager(database_path=custom_path)
            
            assert os.path.exists(custom_path)
            assert Path(custom_path).is_file()
            
            # Cleanup
            del custom_db
        finally:
            if os.path.exists(custom_path):
                os.unlink(custom_path)
    
    def test_store_log_success(self):
        """Test successful log storage"""
        log_entry = create_test_log_entry(
            log_id="store-test-1",
            original_log="Test storage operation",
            severity=LogSeverity.INFO
        )
        
        result = self.db_manager.store_log(log_entry)
        
        assert result is True
        
        # Verify log was stored by retrieving it
        retrieved_log = self.db_manager.get_log("store-test-1")
        assert retrieved_log is not None
        assert retrieved_log.log_id == "store-test-1"
        assert retrieved_log.original_log == "Test storage operation"
        assert retrieved_log.severity == LogSeverity.INFO
    
    def test_store_log_duplicate_id(self):
        """Test storing log with duplicate ID - should replace existing log"""
        log_entry1 = create_test_log_entry(
            log_id="duplicate-id",
            original_log="First log entry"
        )
        
        log_entry2 = create_test_log_entry(
            log_id="duplicate-id",
            original_log="Second log entry"
        )
        
        # First storage should succeed
        result1 = self.db_manager.store_log(log_entry1)
        assert result1 is True
        
        # Second storage with same ID should also succeed (INSERT OR REPLACE behavior)
        result2 = self.db_manager.store_log(log_entry2)
        assert result2 is True
        
        # Verify second log replaced the first
        retrieved_log = self.db_manager.get_log("duplicate-id")
        assert retrieved_log is not None
        assert retrieved_log.original_log == "Second log entry"
    
    def test_get_log_existing(self):
        """Test retrieving existing log"""
        log_entry = create_test_log_entry(
            log_id="get-test-1",
            original_log="Retrieve me later",
            severity=LogSeverity.WARNING,
            language="javascript",
            tags=["frontend", "ui"],
            project_name="web-app"
        )
        
        # Store the log
        self.db_manager.store_log(log_entry)
        
        # Retrieve the log
        retrieved_log = self.db_manager.get_log("get-test-1")
        
        assert retrieved_log is not None
        assert retrieved_log.log_id == "get-test-1"
        assert retrieved_log.original_log == "Retrieve me later"
        assert retrieved_log.severity == LogSeverity.WARNING
        assert retrieved_log.language == "javascript"
        assert retrieved_log.tags == ["frontend", "ui"]
        assert retrieved_log.project_name == "web-app"
        assert isinstance(retrieved_log.timestamp, datetime)
    
    def test_get_log_nonexistent(self):
        """Test retrieving non-existent log"""
        retrieved_log = self.db_manager.get_log("nonexistent-log-id")
        
        assert retrieved_log is None
    
    def test_get_log_with_complex_data(self):
        """Test retrieving log with complex metadata and tags"""
        complex_metadata = {
            "error_code": 500,
            "stack_trace": ["function1()", "function2()", "function3()"],
            "request_data": {"user_id": 123, "action": "login"},
            "server_info": {"hostname": "web-01", "version": "2.1.0"}
        }
        
        log_entry = create_test_log_entry(
            log_id="complex-data-test",
            original_log="Complex error with detailed context",
            tags=["authentication", "server_error", "high_priority"],
            language="python"
        )
        log_entry.metadata = complex_metadata
        
        # Store and retrieve
        self.db_manager.store_log(log_entry)
        retrieved_log = self.db_manager.get_log("complex-data-test")
        
        assert retrieved_log is not None
        assert retrieved_log.metadata == complex_metadata
        assert retrieved_log.metadata["error_code"] == 500
        assert "function1()" in retrieved_log.metadata["stack_trace"]
        assert retrieved_log.tags == ["authentication", "server_error", "high_priority"]
    
    def test_search_logs_no_filters(self):
        """Test searching logs without any filters"""
        # Store multiple test logs
        for i in range(5):
            log_entry = create_test_log_entry(
                log_id=f"search-test-{i}",
                original_log=f"Test log entry {i}",
                severity=LogSeverity.INFO
            )
            self.db_manager.store_log(log_entry)
        
        # Search without filters
        results = self.db_manager.search_logs()
        
        assert len(results) == 5
        assert all(isinstance(log, LogEntry) for log in results)
        assert any(log.log_id == "search-test-0" for log in results)
        assert any(log.log_id == "search-test-4" for log in results)
    
    def test_search_logs_by_severity(self):
        """Test searching logs by severity filter"""
        # Store logs with different severities
        severities = [LogSeverity.DEBUG, LogSeverity.INFO, LogSeverity.WARNING, LogSeverity.ERROR, LogSeverity.CRITICAL]
        
        for i, severity in enumerate(severities):
            log_entry = create_test_log_entry(
                log_id=f"severity-test-{i}",
                original_log=f"Log with {severity.value} severity",
                severity=severity
            )
            self.db_manager.store_log(log_entry)
        
        # Search for only ERROR logs
        error_results = self.db_manager.search_logs(severity=LogSeverity.ERROR)
        assert len(error_results) == 1
        assert error_results[0].severity == LogSeverity.ERROR
        assert "ERROR" in error_results[0].original_log.upper()
        
        # Search for only CRITICAL logs
        critical_results = self.db_manager.search_logs(severity=LogSeverity.CRITICAL)
        assert len(critical_results) == 1
        assert critical_results[0].severity == LogSeverity.CRITICAL
    
    def test_search_logs_by_date_range(self):
        """Test searching logs by date range"""
        base_time = datetime(2024, 1, 15, 10, 0, 0)
        
        # Store logs with different timestamps
        for i in range(5):
            timestamp = base_time + timedelta(days=i)
            log_entry = create_test_log_entry(
                log_id=f"date-test-{i}",
                original_log=f"Log from day {i}"
            )
            log_entry.timestamp = timestamp
            self.db_manager.store_log(log_entry)
        
        # Search for logs in middle date range
        start_date = base_time + timedelta(days=1)
        end_date = base_time + timedelta(days=3)
        
        date_results = self.db_manager.search_logs(start_date=start_date, end_date=end_date)
        
        assert len(date_results) == 3  # Days 1, 2, 3
        for log in date_results:
            assert start_date <= log.timestamp <= end_date
    
    def test_search_logs_by_language(self):
        """Test searching logs by programming language"""
        languages = ["python", "javascript", "java", "golang", "python"]
        
        for i, language in enumerate(languages):
            log_entry = create_test_log_entry(
                log_id=f"lang-test-{i}",
                original_log=f"{language} error occurred",
                language=language
            )
            self.db_manager.store_log(log_entry)
        
        # Search for Python logs
        python_results = self.db_manager.search_logs(language="python")
        assert len(python_results) == 2  # Two python logs
        assert all(log.language == "python" for log in python_results)
        
        # Search for JavaScript logs
        js_results = self.db_manager.search_logs(language="javascript")
        assert len(js_results) == 1
        assert js_results[0].language == "javascript"
    
    def test_search_logs_by_tags(self):
        """Test searching logs by tags"""
        test_logs = [
            ("tag-test-1", ["database", "connection"], "Database connection error"),
            ("tag-test-2", ["authentication", "security"], "Auth failure"),
            ("tag-test-3", ["database", "query"], "SQL query timeout"),
            ("tag-test-4", ["frontend", "ui"], "UI rendering issue"),
            ("tag-test-5", ["database", "migration"], "Schema migration failed")
        ]
        
        for log_id, tags, original_log in test_logs:
            log_entry = create_test_log_entry(
                log_id=log_id,
                original_log=original_log,
                tags=tags
            )
            self.db_manager.store_log(log_entry)
        
        # Search for logs with "database" tag
        database_results = self.db_manager.search_logs(tags=["database"])
        assert len(database_results) == 3  # 3 logs have database tag
        
        for log in database_results:
            assert "database" in log.tags
        
        # Search for logs with "authentication" tag
        auth_results = self.db_manager.search_logs(tags=["authentication"])
        assert len(auth_results) == 1
        assert "authentication" in auth_results[0].tags
    
    def test_search_logs_by_project(self):
        """Test searching logs by project name"""
        projects = ["web-api", "data-pipeline", "frontend", "web-api", "mobile-app"]
        
        for i, project in enumerate(projects):
            log_entry = create_test_log_entry(
                log_id=f"project-test-{i}",
                original_log=f"Error in {project}",
                project_name=project
            )
            self.db_manager.store_log(log_entry)
        
        # Search for web-api logs
        api_results = self.db_manager.search_logs(project_name="web-api")
        assert len(api_results) == 2  # Two web-api logs
        assert all(log.project_name == "web-api" for log in api_results)
        
        # Search for mobile-app logs
        mobile_results = self.db_manager.search_logs(project_name="mobile-app")
        assert len(mobile_results) == 1
        assert mobile_results[0].project_name == "mobile-app"
    
    def test_search_logs_text_search(self):
        """Test searching logs by text content"""
        test_logs = [
            ("text-test-1", "ValueError: Invalid input format"),
            ("text-test-2", "ConnectionError: Unable to connect to database"),
            ("text-test-3", "TypeError: Expected string, got integer"),
            ("text-test-4", "FileNotFoundError: Missing configuration file"),
            ("text-test-5", "Authentication failed for user session")
        ]
        
        for log_id, original_log in test_logs:
            log_entry = create_test_log_entry(
                log_id=log_id,
                original_log=original_log
            )
            self.db_manager.store_log(log_entry)
        
        # Search for logs containing "Error"
        error_results = self.db_manager.search_logs(text_search="Error")
        assert len(error_results) >= 3  # At least ValueError, ConnectionError, etc.
        
        for log in error_results:
            assert "Error" in log.original_log or "error" in log.original_log.lower()
        
        # Search for specific terms
        auth_results = self.db_manager.search_logs(text_search="Authentication")
        assert len(auth_results) == 1
        assert "Authentication" in auth_results[0].original_log
    
    def test_search_logs_with_limit_and_offset(self):
        """Test searching logs with pagination (limit and offset)"""
        # Store 20 test logs
        for i in range(20):
            log_entry = create_test_log_entry(
                log_id=f"pagination-test-{i:02d}",
                original_log=f"Test log number {i}"
            )
            self.db_manager.store_log(log_entry)
        
        # Test limit
        limited_results = self.db_manager.search_logs(limit=5)
        assert len(limited_results) == 5
        
        # Test offset
        offset_results = self.db_manager.search_logs(limit=5, offset=10)
        assert len(offset_results) == 5
        
        # Verify different results due to offset
        first_batch = self.db_manager.search_logs(limit=5, offset=0)
        second_batch = self.db_manager.search_logs(limit=5, offset=5)
        
        first_ids = {log.log_id for log in first_batch}
        second_ids = {log.log_id for log in second_batch}
        
        # Should be different sets of log IDs
        assert first_ids.isdisjoint(second_ids)
    
    def test_search_logs_combined_filters(self):
        """Test searching logs with multiple filters combined"""
        # Create logs with various combinations of attributes
        test_data = [
            ("combo-1", LogSeverity.ERROR, "python", ["database"], "web-api", "Database connection failed"),
            ("combo-2", LogSeverity.WARNING, "python", ["database"], "data-pipeline", "Slow query detected"),
            ("combo-3", LogSeverity.ERROR, "javascript", ["ui"], "frontend", "UI component crashed"),
            ("combo-4", LogSeverity.CRITICAL, "python", ["security"], "web-api", "Security breach detected"),
            ("combo-5", LogSeverity.ERROR, "python", ["validation"], "web-api", "Input validation failed")
        ]
        
        for log_id, severity, language, tags, project, original_log in test_data:
            log_entry = create_test_log_entry(
                log_id=log_id,
                original_log=original_log,
                severity=severity,
                language=language,
                tags=tags,
                project_name=project
            )
            self.db_manager.store_log(log_entry)
        
        # Search with multiple filters: ERROR severity + python + web-api project
        combined_results = self.db_manager.search_logs(
            severity=LogSeverity.ERROR,
            language="python",
            project_name="web-api"
        )
        
        assert len(combined_results) == 2  # combo-1 and combo-5
        for log in combined_results:
            assert log.severity == LogSeverity.ERROR
            assert log.language == "python"
            assert log.project_name == "web-api"
    
    def test_delete_logs_older_than(self):
        """Test deleting old logs based on age"""
        base_time = datetime.now()
        
        # Create logs with different ages
        test_logs = [
            ("old-1", base_time - timedelta(days=10)),  # 10 days old
            ("old-2", base_time - timedelta(days=8)),   # 8 days old
            ("recent-1", base_time - timedelta(days=3)), # 3 days old
            ("recent-2", base_time - timedelta(days=1)), # 1 day old
            ("new-1", base_time)                        # Current
        ]
        
        for log_id, timestamp in test_logs:
            log_entry = create_test_log_entry(
                log_id=log_id,
                original_log=f"Log from {timestamp.date()}"
            )
            log_entry.timestamp = timestamp
            self.db_manager.store_log(log_entry)
        
        # Delete logs older than 5 days
        deleted_count = self.db_manager.delete_logs_older_than(5)
        
        assert deleted_count == 2  # old-1 and old-2 should be deleted
        
        # Verify remaining logs
        remaining_logs = self.db_manager.search_logs()
        remaining_ids = {log.log_id for log in remaining_logs}
        
        assert "old-1" not in remaining_ids
        assert "old-2" not in remaining_ids
        assert "recent-1" in remaining_ids
        assert "recent-2" in remaining_ids
        assert "new-1" in remaining_ids
    
    def test_get_statistics_empty_database(self):
        """Test getting statistics from empty database"""
        stats = self.db_manager.get_statistics()
        
        assert isinstance(stats, LogStats)
        assert stats.total_logs == 0
        assert stats.logs_today == 0
        assert stats.logs_this_week == 0
        assert stats.logs_this_month == 0
        assert isinstance(stats.top_error_types, dict)
        assert isinstance(stats.top_languages, dict)
        assert isinstance(stats.top_severity_levels, dict)
        assert isinstance(stats.errors_per_day_last_week, list)
        assert len(stats.errors_per_day_last_week) == 7
        assert isinstance(stats.severity_trends, dict)
        assert isinstance(stats.busiest_hours, dict)
        assert isinstance(stats.busiest_days, dict)
        assert stats.oldest_log_date is None
        assert stats.newest_log_date is None
        assert isinstance(stats.last_updated, datetime)
    
    def test_get_statistics_with_data(self):
        """Test getting statistics from database with data"""
        # Create test data with known distribution
        test_data = [
            (LogSeverity.ERROR, "python", "web-api"),
            (LogSeverity.ERROR, "python", "web-api"),
            (LogSeverity.WARNING, "javascript", "frontend"),
            (LogSeverity.CRITICAL, "python", "data-pipeline"),
            (LogSeverity.INFO, "java", "web-api"),
            (LogSeverity.ERROR, "golang", "microservice")
        ]
        
        oldest_time = datetime.now() - timedelta(days=7)
        newest_time = datetime.now()
        
        for i, (severity, language, project) in enumerate(test_data):
            # Spread timestamps across time range
            timestamp = oldest_time + timedelta(days=i)
            
            log_entry = create_test_log_entry(
                log_id=f"stats-test-{i}",
                original_log=f"Test log {i}",
                severity=severity,
                language=language,
                project_name=project
            )
            log_entry.timestamp = timestamp
            self.db_manager.store_log(log_entry)
        
        stats = self.db_manager.get_statistics()
        
        assert stats.total_logs == 6
        assert stats.logs_today >= 0
        assert stats.logs_this_week >= 0
        assert stats.logs_this_month >= 0
        
        # Check that statistics contain expected data types
        assert isinstance(stats.top_error_types, dict)
        assert isinstance(stats.top_languages, dict)
        assert isinstance(stats.top_severity_levels, dict)
        
        # Check top languages contains our test languages
        assert "python" in stats.top_languages
        assert "javascript" in stats.top_languages
        assert "java" in stats.top_languages
        assert "golang" in stats.top_languages
        
        # Check severity levels
        assert "error" in stats.top_severity_levels
        assert "warning" in stats.top_severity_levels
        assert "critical" in stats.top_severity_levels
        assert "info" in stats.top_severity_levels
        
        # Check trends and timing data
        assert isinstance(stats.errors_per_day_last_week, list)
        assert len(stats.errors_per_day_last_week) == 7
        assert isinstance(stats.severity_trends, dict)
        assert isinstance(stats.busiest_hours, dict)
        assert isinstance(stats.busiest_days, dict)
        
        # Check date range
        assert stats.oldest_log_date is not None
        assert stats.newest_log_date is not None
        assert stats.oldest_log_date <= stats.newest_log_date
        assert isinstance(stats.last_updated, datetime)
    
    def test_create_log_id_deterministic(self):
        """Test that create_log_id produces deterministic results"""
        content = "Test error message"
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        # Generate ID multiple times with same inputs
        id1 = self.db_manager.create_log_id(content, timestamp)
        id2 = self.db_manager.create_log_id(content, timestamp)
        id3 = self.db_manager.create_log_id(content, timestamp)
        
        # Should be identical
        assert id1 == id2 == id3
        assert isinstance(id1, str)
        assert len(id1) > 0
    
    def test_create_log_id_unique_for_different_inputs(self):
        """Test that create_log_id produces different IDs for different inputs"""
        timestamp = datetime(2024, 1, 15, 10, 30, 0)
        
        id1 = self.db_manager.create_log_id("First message", timestamp)
        id2 = self.db_manager.create_log_id("Second message", timestamp)
        id3 = self.db_manager.create_log_id("First message", timestamp + timedelta(seconds=1))
        
        # Should all be different
        assert id1 != id2
        assert id1 != id3
        assert id2 != id3
    
    def test_vacuum_database(self):
        """Test database vacuum operation"""
        # Add and delete some data to create fragmentation
        for i in range(10):
            log_entry = create_test_log_entry(
                log_id=f"vacuum-test-{i}",
                original_log=f"Test log {i}"
            )
            self.db_manager.store_log(log_entry)
        
        # Delete half the logs
        self.db_manager.delete_logs_older_than(0)  # Delete all logs
        
        # Vacuum should complete without error
        self.db_manager.vacuum_database()
        
        # Database should still be functional
        test_log = create_test_log_entry(log_id="post-vacuum-test")
        result = self.db_manager.store_log(test_log)
        assert result is True
        
        retrieved = self.db_manager.get_log("post-vacuum-test")
        assert retrieved is not None


class TestDatabaseErrorHandling:
    """Test error handling and edge cases"""
    
    def test_database_manager_with_invalid_path(self):
        """Test DatabaseManager with invalid database path"""
        # Try to create database in non-existent directory
        invalid_path = "/non/existent/directory/test.db"
        
        # Should handle gracefully or create necessary directories
        try:
            db_manager = DatabaseManager(database_path=invalid_path)
            # If it succeeds, cleanup
            if os.path.exists(invalid_path):
                os.unlink(invalid_path)
        except Exception as e:
            # Should be a reasonable error
            assert isinstance(e, (OSError, sqlite3.Error))
    
    def test_store_log_with_malformed_data(self):
        """Test storing log with malformed/problematic data"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            db_manager = DatabaseManager(database_path=temp_db.name)
            
            # Create log with very long content
            huge_content = "A" * 100000  # 100KB of text
            log_entry = create_test_log_entry(
                log_id="huge-content-test",
                original_log=huge_content
            )
            
            # Should handle large content
            result = db_manager.store_log(log_entry)
            assert result is True
            
            retrieved = db_manager.get_log("huge-content-test")
            assert retrieved is not None
            assert len(retrieved.original_log) == 100000
            
        finally:
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)
    
    def test_concurrent_database_access(self):
        """Test concurrent database access scenarios"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            # Create two database managers pointing to same file
            db_manager1 = DatabaseManager(database_path=temp_db.name)
            db_manager2 = DatabaseManager(database_path=temp_db.name)
            
            # Both should be able to store logs
            log1 = create_test_log_entry(log_id="concurrent-1", original_log="From manager 1")
            log2 = create_test_log_entry(log_id="concurrent-2", original_log="From manager 2")
            
            result1 = db_manager1.store_log(log1)
            result2 = db_manager2.store_log(log2)
            
            assert result1 is True
            assert result2 is True
            
            # Both should be able to read each other's logs
            retrieved1_by_2 = db_manager2.get_log("concurrent-1")
            retrieved2_by_1 = db_manager1.get_log("concurrent-2")
            
            assert retrieved1_by_2 is not None
            assert retrieved2_by_1 is not None
            
        finally:
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)
    
    def test_search_logs_with_invalid_parameters(self):
        """Test search_logs with invalid or edge case parameters"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            db_manager = DatabaseManager(database_path=temp_db.name)
            
            # Store a test log
            log_entry = create_test_log_entry()
            db_manager.store_log(log_entry)
            
            # Test with invalid date range (end before start)
            future_date = datetime.now() + timedelta(days=1)
            past_date = datetime.now() - timedelta(days=1)
            
            results = db_manager.search_logs(start_date=future_date, end_date=past_date)
            assert len(results) == 0  # Should return empty results
            
            # Test with negative limit (should handle gracefully)
            results = db_manager.search_logs(limit=-1)
            assert isinstance(results, list)
            
            # Test with huge offset
            results = db_manager.search_logs(offset=999999)
            assert len(results) == 0
            
        finally:
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)
    
    def test_database_corruption_recovery(self):
        """Test behavior with corrupted database file"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        
        try:
            # Write invalid data to simulate corruption
            temp_db.write(b"This is not a valid SQLite database file")
            temp_db.close()
            
            # Try to initialize DatabaseManager with corrupted file
            # Should either handle gracefully or raise appropriate error
            try:
                db_manager = DatabaseManager(database_path=temp_db.name)
                # If it handles corruption by recreating, test functionality
                test_log = create_test_log_entry()
                result = db_manager.store_log(test_log)
                # Should work if database was recreated
                assert isinstance(result, bool)
            except sqlite3.DatabaseError:
                # Acceptable to raise database error for corrupted file
                pass
            
        finally:
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)