"""
💾 COMPREHENSIVE DATABASE STORAGE TESTS

Following Debuggle's educational philosophy: Think of the database layer as 
the "digital filing cabinet" of your debugging process - it needs to reliably
store, organize, and retrieve all your debugging information.

Like a library system that:
- 📚 Stores books (saves log entries)  
- 🔍 Finds books quickly (fast search and retrieval)
- 📊 Tracks usage (analytics and metrics)
- 🛡️ Protects data (backup and recovery)

TARGET: Boost storage/database.py from 0% → 75% coverage
FOCUS: Real database operations that ensure data integrity and performance
"""

import pytest
import tempfile
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

from src.debuggle.storage.database import (
    DatabaseManager,
    LogEntry,
    LogStats,
    LogSeverity,
    TierLevel
)


class TestDatabaseManagerInitialization:
    """Test database manager setup and initialization"""
    
    def test_database_manager_creates_successfully(self):
        """Test basic database manager creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(database_path=str(db_path))
            
            assert db_manager is not None
            assert db_manager.database_path == Path(str(db_path))
            assert hasattr(db_manager, 'store_log')
            assert hasattr(db_manager, 'get_log')
    
    def test_database_creates_tables_on_init(self):
        """Test that database tables are created during initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(database_path=str(db_path))
            
            # Verify database file exists
            assert Path(db_path).exists()
            
            # Verify tables were created
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for expected tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['logs']
            for table in expected_tables:
                assert table in tables
            
            conn.close()
    
    def test_database_with_default_path(self):
        """Test database with default path"""
        db_manager = DatabaseManager()
        
        # Should use default path
        assert db_manager.database_path == Path("logs.db")


class TestLogEntryStorage:
    """Test storing and retrieving log entries"""
    
    @pytest.fixture
    def db_manager(self):
        """Create database manager for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(database_path=str(db_path))
            yield manager
    
    def test_store_log_entry(self, db_manager):
        """Test storing log entry to database"""
        log_entry = LogEntry(
            log_id="test_log_1",
            timestamp=datetime.now(),
            original_log="IndexError: list index out of range",
            processed_log="Array index error: tried to access index 5 in array of length 3",
            summary="Array access violation",
            tags=["IndexError", "array", "bounds"],
            severity=LogSeverity.ERROR,
            language="python",
            metadata={"function": "process_data", "line": 42},
            project_name="test_project",
            file_path="/app/main.py",
            source="api"
        )
        
        # Store log entry
        result = db_manager.store_log(log_entry)
        
        assert result is True
    
    def test_retrieve_log_entry(self, db_manager):
        """Test retrieving saved log entry"""
        # First store a log entry
        log_entry = LogEntry(
            log_id="test_retrieve_1",
            timestamp=datetime.now(),
            original_log="ValueError: invalid literal for int()",
            processed_log="Cannot convert 'hello' to integer",
            summary="Type conversion error",
            tags=["ValueError", "conversion"],
            severity=LogSeverity.WARNING,
            language="python",
            metadata={"context": "user_input"},
            project_name="parser_app",
            file_path="/app/parser.py"
        )
        
        db_manager.store_log(log_entry)
        
        # Retrieve the log entry
        retrieved = db_manager.get_log("test_retrieve_1")
        
        assert retrieved is not None
        assert retrieved.log_id == "test_retrieve_1"
        assert retrieved.original_log == "ValueError: invalid literal for int()"
        assert retrieved.processed_log == "Cannot convert 'hello' to integer"
        assert retrieved.severity == LogSeverity.WARNING
        assert retrieved.language == "python"
        assert retrieved.tags == ["ValueError", "conversion"]
    
    def test_store_log_with_minimal_data(self, db_manager):
        """Test storing log with only required fields"""
        log_entry = LogEntry(
            log_id="minimal_log",
            timestamp=datetime.now(),
            original_log="Simple error message",
            processed_log="Simple error message",
            summary=None,
            tags=[],
            severity=LogSeverity.INFO,
            language="unknown",
            metadata={}
        )
        
        result = db_manager.store_log(log_entry)
        assert result is True
        
        # Should be able to retrieve it
        retrieved = db_manager.get_log("minimal_log")
        assert retrieved is not None
        assert retrieved.log_id == "minimal_log"
    
    def test_replace_existing_log(self, db_manager):
        """Test replacing existing log entry with same ID"""
        log_id = "replaceable_log"
        
        # Store first version
        log_v1 = LogEntry(
            log_id=log_id,
            timestamp=datetime.now(),
            original_log="Original error",
            processed_log="Original processed",
            summary="Original summary",
            tags=["original"],
            severity=LogSeverity.INFO,
            language="python",
            metadata={}
        )
        db_manager.store_log(log_v1)
        
        # Store updated version with same ID
        log_v2 = LogEntry(
            log_id=log_id,
            timestamp=datetime.now(),
            original_log="Updated error",
            processed_log="Updated processed",
            summary="Updated summary",
            tags=["updated"],
            severity=LogSeverity.ERROR,
            language="python",
            metadata={}
        )
        db_manager.store_log(log_v2)
        
        # Should retrieve the updated version
        retrieved = db_manager.get_log(log_id)
        assert retrieved.original_log == "Updated error"
        assert retrieved.summary == "Updated summary"
        assert retrieved.tags == ["updated"]
        assert retrieved.severity == LogSeverity.ERROR


class TestLogSearching:
    """Test searching and filtering log entries"""
    
    @pytest.fixture
    def db_manager_with_data(self):
        """Create database manager with sample data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(database_path=str(db_path))
            
            # Add sample log entries
            base_time = datetime.now()
            sample_logs = [
                LogEntry(
                    log_id="log_1",
                    timestamp=base_time - timedelta(hours=1),
                    original_log="IndexError in Python",
                    processed_log="Array index error",
                    summary="Index out of bounds",
                    tags=["IndexError", "python"],
                    severity=LogSeverity.ERROR,
                    language="python",
                    metadata={},
                    project_name="web_app"
                ),
                LogEntry(
                    log_id="log_2", 
                    timestamp=base_time - timedelta(hours=2),
                    original_log="NullPointerException in Java",
                    processed_log="Null reference error",
                    summary="Accessing null object",
                    tags=["NullPointer", "java"],
                    severity=LogSeverity.CRITICAL,
                    language="java",
                    metadata={},
                    project_name="backend_api"
                ),
                LogEntry(
                    log_id="log_3",
                    timestamp=base_time - timedelta(hours=3),
                    original_log="TypeError in Python",
                    processed_log="Type mismatch error",
                    summary="Wrong data type",
                    tags=["TypeError", "python"],
                    severity=LogSeverity.WARNING,
                    language="python",
                    metadata={},
                    project_name="web_app"
                )
            ]
            
            for log in sample_logs:
                manager.store_log(log)
            
            yield manager
    
    def test_search_by_date_range(self, db_manager_with_data):
        """Test searching logs by date range"""
        now = datetime.now()
        start_date = now - timedelta(hours=2.5)
        end_date = now
        
        results = db_manager_with_data.search_logs(
            start_date=start_date,
            end_date=end_date
        )
        
        # Should find logs from last 2.5 hours (log_1 and log_2)
        assert len(results) == 2
        log_ids = [log.log_id for log in results]
        assert "log_1" in log_ids
        assert "log_2" in log_ids
    
    def test_search_by_severity(self, db_manager_with_data):
        """Test searching logs by severity level"""
        results = db_manager_with_data.search_logs(severity=LogSeverity.ERROR)
        
        # Should find only ERROR level logs
        assert len(results) == 1
        assert results[0].log_id == "log_1"
        assert results[0].severity == LogSeverity.ERROR
    
    def test_search_by_language(self, db_manager_with_data):
        """Test searching logs by programming language"""
        results = db_manager_with_data.search_logs(language="python")
        
        # Should find all Python logs (log_1 and log_3)
        assert len(results) == 2
        log_ids = [log.log_id for log in results]
        assert "log_1" in log_ids
        assert "log_3" in log_ids
    
    def test_search_by_project(self, db_manager_with_data):
        """Test searching logs by project name"""
        results = db_manager_with_data.search_logs(project_name="web_app")
        
        # Should find logs from web_app project
        assert len(results) == 2
        for log in results:
            assert log.project_name == "web_app"
    
    def test_search_by_tags(self, db_manager_with_data):
        """Test searching logs by tags"""
        results = db_manager_with_data.search_logs(tags=["python"])
        
        # Should find logs tagged with python
        assert len(results) == 2
        for log in results:
            assert "python" in log.tags
    
    def test_search_by_text(self, db_manager_with_data):
        """Test text search across log content"""
        results = db_manager_with_data.search_logs(text_search="index")
        
        # Should find logs containing "index" in any text field
        assert len(results) >= 1
        # Verify that found logs contain the search term
        found_text = False
        for log in results:
            if ("index" in log.original_log.lower() or 
                "index" in log.processed_log.lower() or
                (log.summary and "index" in log.summary.lower())):
                found_text = True
                break
        assert found_text
    
    def test_search_with_limit_offset(self, db_manager_with_data):
        """Test search pagination with limit and offset"""
        # Get first page (limit 2)
        page1 = db_manager_with_data.search_logs(limit=2, offset=0)
        assert len(page1) == 2
        
        # Get second page (limit 2, offset 2)
        page2 = db_manager_with_data.search_logs(limit=2, offset=2)
        assert len(page2) == 1  # Only 3 total logs, so 1 on second page
        
        # Verify different results
        page1_ids = {log.log_id for log in page1}
        page2_ids = {log.log_id for log in page2}
        assert page1_ids != page2_ids
    
    def test_search_with_multiple_filters(self, db_manager_with_data):
        """Test combining multiple search filters"""
        results = db_manager_with_data.search_logs(
            language="python",
            severity=LogSeverity.ERROR,
            project_name="web_app"
        )
        
        # Should find logs matching ALL criteria
        assert len(results) == 1
        log = results[0]
        assert log.language == "python"
        assert log.severity == LogSeverity.ERROR
        assert log.project_name == "web_app"
    
    def test_search_returns_empty_for_no_matches(self, db_manager_with_data):
        """Test search returns empty list when no matches found"""
        results = db_manager_with_data.search_logs(
            language="nonexistent",
            text_search="impossible_string_xyz"
        )
        
        assert len(results) == 0
        assert isinstance(results, list)


class TestLogDeletion:
    """Test log deletion and cleanup operations"""
    
    @pytest.fixture
    def db_manager(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(database_path=str(db_path))
            yield manager
    
    def test_delete_old_logs(self, db_manager):
        """Test deletion of logs older than specified days"""
        base_time = datetime.now()
        
        # Add logs with different ages
        old_logs = []
        recent_logs = []
        
        for i in range(10):
            days_old = i * 5  # 0, 5, 10, 15, ... days old
            log_entry = LogEntry(
                log_id=f"log_{i}",
                timestamp=base_time - timedelta(days=days_old),
                original_log=f"Error message {i}",
                processed_log=f"Processed error {i}",
                summary=f"Summary {i}",
                tags=[f"tag{i}"],
                severity=LogSeverity.INFO,
                language="python",
                metadata={}
            )
            
            db_manager.store_log(log_entry)
            
            if days_old >= 30:  # Include 30 days as old since delete_logs_older_than(30) includes 30
                old_logs.append(log_entry.log_id)
            else:
                recent_logs.append(log_entry.log_id)
        
        # Delete logs older than 30 days
        deleted_count = db_manager.delete_logs_older_than(30)
        
        # Should have deleted old logs (at least the ones we expect)
        assert deleted_count >= len(old_logs)  # Allow for boundary conditions
        
        # Verify old logs are gone
        for log_id in old_logs:
            assert db_manager.get_log(log_id) is None
        
        # Verify recent logs still exist
        for log_id in recent_logs:
            assert db_manager.get_log(log_id) is not None


class TestDatabaseStatistics:
    """Test database analytics and statistics generation"""
    
    @pytest.fixture
    def db_manager_with_stats_data(self):
        """Create database with data for statistics testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(database_path=str(db_path))
            
            # Add diverse log entries for statistics
            base_time = datetime.now()
            
            # Different severities
            severities = [LogSeverity.ERROR, LogSeverity.WARNING, LogSeverity.ERROR, 
                         LogSeverity.CRITICAL, LogSeverity.INFO, LogSeverity.ERROR]
            
            # Different languages
            languages = ["python", "java", "python", "javascript", "python", "java"]
            
            # Different error types (tags)
            error_types = [["IndexError"], ["Warning"], ["ValueError"], 
                          ["TypeError"], ["Info"], ["NullPointer"]]
            
            for i, (severity, language, tags) in enumerate(zip(severities, languages, error_types)):
                # Distribute logs across different days
                days_ago = i % 7  # Spread across last week
                hours_ago = i % 24  # Spread across different hours
                
                log_entry = LogEntry(
                    log_id=f"stats_log_{i}",
                    timestamp=base_time - timedelta(days=days_ago, hours=hours_ago),
                    original_log=f"Error message {i}",
                    processed_log=f"Processed error {i}",
                    summary=f"Summary {i}",
                    tags=tags,
                    severity=severity,
                    language=language,
                    metadata={},
                    project_name=f"project_{i % 3}"  # 3 different projects
                )
                manager.store_log(log_entry)
            
            yield manager
    
    def test_get_basic_statistics(self, db_manager_with_stats_data):
        """Test basic count statistics"""
        stats = db_manager_with_stats_data.get_statistics()
        
        assert isinstance(stats, LogStats)
        assert stats.total_logs == 6  # We added 6 logs
        assert stats.logs_today >= 0
        assert stats.logs_this_week >= 0
        assert stats.logs_this_month >= 0
        assert stats.last_updated is not None
        
        # Verify we have data for different time periods
        # (exact numbers depend on when test runs, but should be reasonable)
        assert stats.logs_this_month >= stats.logs_this_week
        assert stats.logs_this_week >= stats.logs_today
    
    def test_get_top_categories_statistics(self, db_manager_with_stats_data):
        """Test top categories in statistics"""
        stats = db_manager_with_stats_data.get_statistics()
        
        # Should have top severity levels
        assert isinstance(stats.top_severity_levels, dict)
        assert len(stats.top_severity_levels) > 0
        
        # Should have top languages
        assert isinstance(stats.top_languages, dict)
        assert len(stats.top_languages) > 0
        assert "python" in stats.top_languages  # We added several Python logs
        
        # Should have top error types
        assert isinstance(stats.top_error_types, dict)
        assert len(stats.top_error_types) > 0
    
    def test_get_trend_statistics(self, db_manager_with_stats_data):
        """Test trend analysis in statistics"""
        stats = db_manager_with_stats_data.get_statistics()
        
        # Should have daily error counts for last week
        assert isinstance(stats.errors_per_day_last_week, list) 
        assert len(stats.errors_per_day_last_week) == 7  # 7 days
        
        # Should have severity trends
        assert isinstance(stats.severity_trends, dict)
        for severity_name, daily_counts in stats.severity_trends.items():
            assert isinstance(daily_counts, list)
            assert len(daily_counts) == 7  # 7 days of data
    
    def test_get_timing_statistics(self, db_manager_with_stats_data):
        """Test timing pattern statistics"""
        stats = db_manager_with_stats_data.get_statistics()
        
        # Should have busiest hours data
        assert isinstance(stats.busiest_hours, dict)
        # Hours should be 0-23
        for hour in stats.busiest_hours.keys():
            assert 0 <= hour <= 23
        
        # Should have busiest days data  
        assert isinstance(stats.busiest_days, dict)
        expected_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday',
                        'Thursday', 'Friday', 'Saturday']
        for day in stats.busiest_days.keys():
            assert day in expected_days
    
    def test_get_data_freshness_statistics(self, db_manager_with_stats_data):
        """Test data freshness information in statistics"""
        stats = db_manager_with_stats_data.get_statistics()
        
        # Should have oldest and newest log dates
        assert stats.oldest_log_date is not None
        assert stats.newest_log_date is not None
        assert isinstance(stats.oldest_log_date, datetime)
        assert isinstance(stats.newest_log_date, datetime)
        
        # Newest should be more recent than oldest
        assert stats.newest_log_date >= stats.oldest_log_date


class TestLogIdGeneration:
    """Test unique log ID generation"""
    
    @pytest.fixture
    def db_manager(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(database_path=str(db_path))
            yield manager
    
    def test_create_unique_log_ids(self, db_manager):
        """Test that log IDs are unique for different content"""
        timestamp = datetime.now()
        
        # Create IDs for different content
        id1 = db_manager.create_log_id("Error message 1", timestamp)
        id2 = db_manager.create_log_id("Error message 2", timestamp)
        
        assert id1 != id2
        assert id1.startswith("log_")
        assert id2.startswith("log_")
        assert len(id1) > 4  # Should be more than just "log_"
        assert len(id2) > 4
    
    def test_create_same_log_id_for_identical_content(self, db_manager):
        """Test that identical content produces same log ID"""
        timestamp = datetime.now()
        content = "Identical error message"
        
        id1 = db_manager.create_log_id(content, timestamp)
        id2 = db_manager.create_log_id(content, timestamp)
        
        assert id1 == id2  # Same content + timestamp = same ID
    
    def test_create_different_log_ids_for_different_timestamps(self, db_manager):
        """Test that same content with different timestamps produces different IDs"""
        content = "Same error message"
        timestamp1 = datetime.now()
        timestamp2 = timestamp1 + timedelta(seconds=1)
        
        id1 = db_manager.create_log_id(content, timestamp1)
        id2 = db_manager.create_log_id(content, timestamp2)
        
        assert id1 != id2  # Different timestamps = different IDs


class TestDatabaseMaintenance:
    """Test database maintenance operations"""
    
    @pytest.fixture
    def db_manager(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            manager = DatabaseManager(database_path=str(db_path))
            yield manager
    
    def test_vacuum_database(self, db_manager):
        """Test database vacuum operation"""
        # Add some data first
        for i in range(10):
            log_entry = LogEntry(
                log_id=f"vacuum_test_{i}",
                timestamp=datetime.now(),
                original_log=f"Test error {i}",
                processed_log=f"Processed test error {i}",
                summary=f"Test summary {i}",
                tags=[f"test{i}"],
                severity=LogSeverity.INFO,
                language="python",
                metadata={}
            )
            db_manager.store_log(log_entry)
        
        # Vacuum should complete without error
        db_manager.vacuum_database()
        
        # Database should still be functional after vacuum
        test_log = db_manager.get_log("vacuum_test_0")
        assert test_log is not None
        assert test_log.log_id == "vacuum_test_0"


class TestDatabaseErrorHandling:
    """Test database error handling and edge cases"""
    
    def test_handles_missing_log_gracefully(self):
        """Test handling of requests for non-existent logs"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(database_path=str(db_path))
            
            # Should return None for non-existent log
            result = db_manager.get_log("nonexistent_log_id")
            assert result is None
    
    def test_handles_empty_search_results_gracefully(self):
        """Test handling when search finds no results"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(database_path=str(db_path))
            
            # Search with parameters that won't match anything
            far_future = datetime.now() + timedelta(days=365)
            results = db_manager.search_logs(
                start_date=far_future,  # No logs from the future
                language="nonexistent_language"  # Language that doesn't exist
            )
            assert isinstance(results, list)
            assert len(results) == 0
    
    def test_handles_storage_errors_gracefully(self):
        """Test handling of storage errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            db_manager = DatabaseManager(database_path=str(db_path))
            
            # Try to store invalid log entry (should handle gracefully)
            invalid_log = LogEntry(
                log_id="",  # Empty log ID might cause issues
                timestamp=datetime.now(),
                original_log="",  # Empty content
                processed_log="",
                summary=None,
                tags=[],
                severity=LogSeverity.INFO,
                language="",
                metadata={}
            )
            
            # Should not crash, might return False or handle gracefully
            result = db_manager.store_log(invalid_log)
            # We don't assert a specific result, just that it doesn't crash
            assert isinstance(result, bool)


def test_database_integration_with_debuggle():
    """Test database integration with other Debuggle components"""
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "integration.db"
        db_manager = DatabaseManager(database_path=str(db_path))
        
        # Test creating log entry from real error analysis
        log_entry = LogEntry(
            log_id="integration_test",
            timestamp=datetime.now(),
            original_log="Traceback (most recent call):\n  File 'test.py', line 5, in <module>\n    print(arr[10])\nIndexError: list index out of range",
            processed_log="Array index error: Attempted to access index 10 in array of length 5",
            summary="Index out of bounds error in test.py line 5",
            tags=["IndexError", "array", "bounds_check"],
            severity=LogSeverity.ERROR,
            language="python",
            metadata={
                "function": "<module>",
                "line_number": 5,
                "file_path": "test.py",
                "context": "print(arr[10])"
            },
            project_name="debuggle_test",
            file_path="test.py",
            source="analyzer"
        )
        
        # Should be able to store and retrieve
        result = db_manager.store_log(log_entry)
        assert result is True
        
        retrieved = db_manager.get_log("integration_test")
        assert retrieved is not None
        assert retrieved.log_id == "integration_test"
        assert retrieved.severity == LogSeverity.ERROR
        assert "IndexError" in retrieved.tags