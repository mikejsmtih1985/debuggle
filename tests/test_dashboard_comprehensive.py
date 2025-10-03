"""
🎯 COMPREHENSIVE DASHBOARD SYSTEM COVERAGE TESTS

This test suite is designed to boost dashboard.py coverage from 34% to 70%+ by testing:
- All enum classes and their behavior
- ChartData creation, manipulation, and serialization
- Dashboard creation, chart management, and operations
- DashboardEngine initialization and background services
- All chart update methods and data refresh logic
- Error handling and edge cases throughout the system
- Real-time update mechanisms and async operations

These tests cover the previously untested branches and critical error paths.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import asdict

from src.debuggle.dashboard import (
    ChartType, TimeRange, MetricType, ChartData, Dashboard, DashboardEngine
)
from src.debuggle.storage.database import DatabaseManager, LogEntry, LogSeverity


class TestEnumClasses:
    """Test all enum classes for completeness and behavior"""
    
    def test_chart_type_enum_values(self):
        """Test ChartType enum has all expected values"""
        expected_types = [
            "line", "bar", "pie", "heatmap", "gauge", 
            "timeline", "geographic", "scatter", "area"
        ]
        
        chart_types = [chart_type.value for chart_type in ChartType]
        for expected in expected_types:
            assert expected in chart_types
    
    def test_time_range_enum_values(self):
        """Test TimeRange enum has all expected values"""
        expected_ranges = [
            "last_hour", "last_24h", "last_7d", "last_30d", 
            "last_90d", "last_year", "custom"
        ]
        
        time_ranges = [time_range.value for time_range in TimeRange]
        for expected in expected_ranges:
            assert expected in time_ranges
    
    def test_metric_type_enum_values(self):
        """Test MetricType enum has all expected values"""
        expected_metrics = [
            "error_count", "severity_distribution", "language_breakdown",
            "timeline", "top_errors", "response_time", "geographic_distribution",
            "hourly_patterns", "daily_trends", "error_rate", "resolution_time",
            "user_impact", "system_health", "performance_metrics"
        ]
        
        metric_types = [metric.value for metric in MetricType]
        for expected in expected_metrics:
            assert expected in metric_types
    
    def test_enum_string_conversion(self):
        """Test enum string conversion and equality"""
        assert str(ChartType.LINE) == "line"
        assert ChartType.BAR == "bar"
        assert TimeRange.LAST_24H == "last_24h"
        assert MetricType.ERROR_COUNT == "error_count"


class TestChartData:
    """Test ChartData class functionality"""
    
    def test_chart_data_creation_minimal(self):
        """Test creating ChartData with minimal parameters"""
        chart = ChartData(
            chart_id="test_chart",
            title="Test Chart",
            chart_type=ChartType.LINE,
            metric_type=MetricType.ERROR_COUNT
        )
        
        assert chart.chart_id == "test_chart"
        assert chart.title == "Test Chart"
        assert chart.chart_type == ChartType.LINE
        assert chart.metric_type == MetricType.ERROR_COUNT
        assert chart.time_range == TimeRange.LAST_24H  # default
        assert chart.data == []  # default
        assert chart.metadata == {}  # default
    
    def test_chart_data_creation_full(self):
        """Test creating ChartData with all parameters"""
        test_data = [{"x": 1, "y": 2}, {"x": 2, "y": 4}]
        test_metadata = {"color": "blue", "label": "Errors"}
        
        chart = ChartData(
            chart_id="full_chart",
            title="Full Chart",
            chart_type=ChartType.BAR,
            metric_type=MetricType.SEVERITY_DISTRIBUTION,
            time_range=TimeRange.LAST_7D,
            data=test_data,
            metadata=test_metadata,
            refresh_interval=30
        )
        
        assert chart.chart_id == "full_chart"
        assert chart.title == "Full Chart"
        assert chart.chart_type == ChartType.BAR
        assert chart.metric_type == MetricType.SEVERITY_DISTRIBUTION
        assert chart.time_range == TimeRange.LAST_7D
        assert chart.data == test_data
        assert chart.metadata == test_metadata
        assert chart.refresh_interval == 30
    
    def test_chart_data_to_dict(self):
        """Test ChartData serialization to dictionary"""
        chart = ChartData(
            chart_id="serialize_test",
            title="Serialize Test",
            chart_type=ChartType.PIE,
            metric_type=MetricType.LANGUAGE_BREAKDOWN,
            data=[{"language": "Python", "count": 10}],
            metadata={"theme": "dark"}
        )
        
        chart_dict = chart.to_dict()
        
        assert chart_dict["chart_id"] == "serialize_test"
        assert chart_dict["title"] == "Serialize Test"
        assert chart_dict["chart_type"] == "pie"
        assert chart_dict["metric_type"] == "language_breakdown"
        assert chart_dict["time_range"] == "last_24h"
        assert chart_dict["data"] == [{"language": "Python", "count": 10}]
        assert chart_dict["metadata"] == {"theme": "dark"}
        assert "last_updated" in chart_dict
        assert "refresh_interval" in chart_dict
    
    def test_chart_data_last_updated_automatic(self):
        """Test that last_updated is set automatically"""
        before_creation = datetime.now()
        chart = ChartData(
            chart_id="time_test",
            title="Time Test",
            chart_type=ChartType.LINE,
            metric_type=MetricType.ERROR_COUNT
        )
        after_creation = datetime.now()
        
        assert before_creation <= chart.last_updated <= after_creation
    
    def test_chart_data_default_values(self):
        """Test that default values are properly set"""
        chart = ChartData(
            chart_id="defaults",
            title="Defaults",
            chart_type=ChartType.GAUGE,
            metric_type=MetricType.SYSTEM_HEALTH
        )
        
        assert chart.time_range == TimeRange.LAST_24H
        assert chart.data == []
        assert chart.metadata == {}
        assert chart.refresh_interval == 60
        assert isinstance(chart.last_updated, datetime)


class TestDashboard:
    """Test Dashboard class functionality"""
    
    def test_dashboard_creation_minimal(self):
        """Test creating Dashboard with minimal parameters"""
        dashboard = Dashboard(
            dashboard_id="test_dash",
            title="Test Dashboard"
        )
        
        assert dashboard.dashboard_id == "test_dash"
        assert dashboard.title == "Test Dashboard"
        assert dashboard.description == ""  # default
        assert dashboard.charts == []  # default
        assert dashboard.layout == {}  # default
        assert dashboard.metadata == {}  # default
        assert dashboard.is_active is True  # default
    
    def test_dashboard_creation_full(self):
        """Test creating Dashboard with all parameters"""
        test_charts = [
            ChartData("chart1", "Chart 1", ChartType.LINE, MetricType.ERROR_COUNT),
            ChartData("chart2", "Chart 2", ChartType.BAR, MetricType.SEVERITY_DISTRIBUTION)
        ]
        test_layout = {"grid": "2x2", "responsive": True}
        test_metadata = {"theme": "dark", "auto_refresh": True}
        
        dashboard = Dashboard(
            dashboard_id="full_dash",
            title="Full Dashboard",
            description="Complete dashboard test",
            charts=test_charts,
            layout=test_layout,
            metadata=test_metadata,
            is_active=False
        )
        
        assert dashboard.dashboard_id == "full_dash"
        assert dashboard.title == "Full Dashboard"
        assert dashboard.description == "Complete dashboard test"
        assert len(dashboard.charts) == 2
        assert dashboard.layout == test_layout
        assert dashboard.metadata == test_metadata
        assert dashboard.is_active is False
    
    def test_dashboard_add_chart(self):
        """Test adding charts to dashboard"""
        dashboard = Dashboard("test", "Test")
        
        chart1 = ChartData("chart1", "Chart 1", ChartType.LINE, MetricType.ERROR_COUNT)
        chart2 = ChartData("chart2", "Chart 2", ChartType.PIE, MetricType.LANGUAGE_BREAKDOWN)
        
        dashboard.add_chart(chart1)
        assert len(dashboard.charts) == 1
        assert dashboard.charts[0].chart_id == "chart1"
        
        dashboard.add_chart(chart2)
        assert len(dashboard.charts) == 2
        assert dashboard.charts[1].chart_id == "chart2"
    
    def test_dashboard_remove_chart_success(self):
        """Test successfully removing a chart from dashboard"""
        chart = ChartData("remove_me", "Remove Me", ChartType.BAR, MetricType.ERROR_COUNT)
        dashboard = Dashboard("test", "Test", charts=[chart])
        
        assert len(dashboard.charts) == 1
        result = dashboard.remove_chart("remove_me")
        
        assert result is True
        assert len(dashboard.charts) == 0
    
    def test_dashboard_remove_chart_not_found(self):
        """Test removing a chart that doesn't exist"""
        chart = ChartData("existing", "Existing", ChartType.LINE, MetricType.ERROR_COUNT)
        dashboard = Dashboard("test", "Test", charts=[chart])
        
        result = dashboard.remove_chart("nonexistent")
        
        assert result is False
        assert len(dashboard.charts) == 1  # Original chart still there
    
    def test_dashboard_to_dict(self):
        """Test Dashboard serialization to dictionary"""
        chart = ChartData("chart1", "Chart 1", ChartType.LINE, MetricType.ERROR_COUNT)
        dashboard = Dashboard(
            dashboard_id="serialize_dash",
            title="Serialize Dashboard",
            description="Test serialization",
            charts=[chart],
            layout={"columns": 2},
            metadata={"version": "1.0"},
            is_active=True
        )
        
        dash_dict = dashboard.to_dict()
        
        assert dash_dict["dashboard_id"] == "serialize_dash"
        assert dash_dict["title"] == "Serialize Dashboard"
        assert dash_dict["description"] == "Test serialization"
        assert len(dash_dict["charts"]) == 1
        assert dash_dict["charts"][0]["chart_id"] == "chart1"
        assert dash_dict["layout"] == {"columns": 2}
        assert dash_dict["metadata"] == {"version": "1.0"}
        assert dash_dict["is_active"] is True
        assert "created_at" in dash_dict
        assert "last_updated" in dash_dict
    
    def test_dashboard_created_at_automatic(self):
        """Test that created_at is set automatically"""
        before_creation = datetime.now()
        dashboard = Dashboard("time_test", "Time Test")
        after_creation = datetime.now()
        
        assert before_creation <= dashboard.created_at <= after_creation
        assert before_creation <= dashboard.last_updated <= after_creation


class TestDashboardEngine:
    """Test DashboardEngine class functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=DatabaseManager)
        self.engine = DashboardEngine(self.mock_db)
    
    def test_dashboard_engine_initialization(self):
        """Test DashboardEngine initialization"""
        assert self.engine.db == self.mock_db
        assert len(self.engine.dashboards) == 1  # default dashboard created
        assert "default" in self.engine.dashboards
        assert self.engine.is_running is False
        assert self.engine.refresh_task is None
    
    def test_create_default_dashboard(self):
        """Test creation of default dashboard"""
        default_dash = self.engine.dashboards["default"]
        
        assert default_dash.dashboard_id == "default"
        assert default_dash.title == "Default Dashboard"
        assert len(default_dash.charts) > 0  # Should have some default charts
        assert default_dash.is_active is True
        
        # Check that default charts are created
        chart_ids = [chart.chart_id for chart in default_dash.charts]
        expected_charts = [
            "error_count_timeline",
            "severity_distribution", 
            "language_breakdown",
            "top_errors"
        ]
        for expected in expected_charts:
            assert expected in chart_ids
    
    def test_get_dashboard_existing(self):
        """Test getting an existing dashboard"""
        dashboard = self.engine.get_dashboard("default")
        
        assert dashboard is not None
        assert dashboard.dashboard_id == "default"
        assert dashboard.title == "Default Dashboard"
    
    def test_get_dashboard_nonexistent(self):
        """Test getting a non-existent dashboard"""
        dashboard = self.engine.get_dashboard("nonexistent")
        
        assert dashboard is None
    
    def test_create_dashboard_new(self):
        """Test creating a new dashboard"""
        new_dashboard = self.engine.create_dashboard(
            "custom",
            "Custom Dashboard", 
            "Custom description"
        )
        
        assert new_dashboard is not None
        assert new_dashboard.dashboard_id == "custom"
        assert new_dashboard.title == "Custom Dashboard"
        assert new_dashboard.description == "Custom description"
        assert "custom" in self.engine.dashboards
    
    def test_create_dashboard_duplicate_id(self):
        """Test creating dashboard with duplicate ID"""
        # Try to create dashboard with existing ID
        duplicate = self.engine.create_dashboard("default", "Duplicate")
        
        assert duplicate is None  # Should return None for duplicate ID
        assert len(self.engine.dashboards) == 1  # No new dashboard added
    
    def test_delete_dashboard_success(self):
        """Test successfully deleting a dashboard"""
        # Create a dashboard to delete
        self.engine.create_dashboard("delete_me", "Delete Me")
        assert "delete_me" in self.engine.dashboards
        
        result = self.engine.delete_dashboard("delete_me")
        
        assert result is True
        assert "delete_me" not in self.engine.dashboards
    
    def test_delete_dashboard_not_found(self):
        """Test deleting a non-existent dashboard"""
        result = self.engine.delete_dashboard("nonexistent")
        
        assert result is False
    
    def test_delete_default_dashboard_protected(self):
        """Test that default dashboard cannot be deleted"""
        result = self.engine.delete_dashboard("default")
        
        assert result is False
        assert "default" in self.engine.dashboards
    
    def test_list_dashboards(self):
        """Test listing all dashboards"""
        # Add a custom dashboard
        self.engine.create_dashboard("custom", "Custom")
        
        dashboards = self.engine.list_dashboards()
        
        assert len(dashboards) >= 2
        dashboard_ids = [d.dashboard_id for d in dashboards]
        assert "default" in dashboard_ids
        assert "custom" in dashboard_ids
    
    def test_list_dashboards_active_only(self):
        """Test listing only active dashboards"""
        # Create inactive dashboard
        custom = self.engine.create_dashboard("inactive", "Inactive")
        custom.is_active = False
        
        active_dashboards = self.engine.list_dashboards(active_only=True)
        
        dashboard_ids = [d.dashboard_id for d in active_dashboards]
        assert "default" in dashboard_ids
        assert "inactive" not in dashboard_ids


class TestDashboardEngineAsyncOperations:
    """Test DashboardEngine async operations and background services"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=DatabaseManager)
        self.engine = DashboardEngine(self.mock_db)
    
    @pytest.mark.asyncio
    async def test_start_engine(self):
        """Test starting the dashboard engine"""
        with patch.object(self.engine, '_start_background_services') as mock_start:
            await self.engine.start()
            
            assert self.engine.is_running is True
            mock_start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_engine_already_running(self):
        """Test starting engine when already running"""
        self.engine.is_running = True
        
        with patch.object(self.engine, '_start_background_services') as mock_start:
            await self.engine.start()
            
            # Should not start background services again
            mock_start.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_stop_engine(self):
        """Test stopping the dashboard engine"""
        # Set up running state
        self.engine.is_running = True
        mock_task = AsyncMock()
        self.engine.refresh_task = mock_task
        
        await self.engine.stop()
        
        assert self.engine.is_running is False
        mock_task.cancel.assert_called_once()
        assert self.engine.refresh_task is None
    
    @pytest.mark.asyncio
    async def test_stop_engine_not_running(self):
        """Test stopping engine when not running"""
        self.engine.is_running = False
        self.engine.refresh_task = None
        
        # Should not raise exception
        await self.engine.stop()
        
        assert self.engine.is_running is False
    
    @pytest.mark.asyncio
    async def test_refresh_all_dashboards(self):
        """Test refreshing all dashboards"""
        with patch.object(self.engine, '_refresh_dashboard_data') as mock_refresh:
            await self.engine.refresh_all_dashboards()
            
            # Should call refresh for default dashboard
            assert mock_refresh.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_refresh_dashboard_data(self):
        """Test refreshing data for a specific dashboard"""
        dashboard = self.engine.get_dashboard("default")
        
        with patch.object(self.engine, '_update_chart_data', new_callable=AsyncMock) as mock_update:
            await self.engine._refresh_dashboard_data(dashboard)
            
            # Should call update for each chart in dashboard
            assert mock_update.call_count == len(dashboard.charts)
    
    @pytest.mark.asyncio
    async def test_update_chart_data_error_count(self):
        """Test updating error count chart data"""
        chart = ChartData(
            "test_error_count",
            "Error Count",
            ChartType.LINE,
            MetricType.ERROR_COUNT
        )
        
        # Mock database response
        self.mock_db.get_logs_by_time_range.return_value = [
            Mock(timestamp=datetime.now(), severity=LogSeverity.ERROR),
            Mock(timestamp=datetime.now(), severity=LogSeverity.WARNING)
        ]
        
        with patch.object(self.engine, '_update_error_count_chart', new_callable=AsyncMock) as mock_update:
            await self.engine._update_chart_data(chart)
            
            mock_update.assert_called_once_with(chart)
    
    @pytest.mark.asyncio
    async def test_update_chart_data_severity_distribution(self):
        """Test updating severity distribution chart data"""
        chart = ChartData(
            "test_severity",
            "Severity Distribution",
            ChartType.PIE,
            MetricType.SEVERITY_DISTRIBUTION
        )
        
        with patch.object(self.engine, '_update_severity_chart', new_callable=AsyncMock) as mock_update:
            await self.engine._update_chart_data(chart)
            
            mock_update.assert_called_once_with(chart)
    
    @pytest.mark.asyncio
    async def test_update_chart_data_language_breakdown(self):
        """Test updating language breakdown chart data"""
        chart = ChartData(
            "test_language",
            "Language Breakdown",
            ChartType.BAR,
            MetricType.LANGUAGE_BREAKDOWN
        )
        
        with patch.object(self.engine, '_update_language_chart', new_callable=AsyncMock) as mock_update:
            await self.engine._update_chart_data(chart)
            
            mock_update.assert_called_once_with(chart)
    
    @pytest.mark.asyncio
    async def test_update_chart_data_unknown_metric(self):
        """Test updating chart with unknown metric type"""
        chart = ChartData(
            "test_unknown",
            "Unknown Metric",
            ChartType.LINE,
            "unknown_metric"  # Not a valid MetricType
        )
        
        # Should not raise exception, just skip unknown metric
        await self.engine._update_chart_data(chart)
        
        # Chart data should remain empty for unknown metric
        assert chart.data == []


class TestChartUpdateMethods:
    """Test specific chart update methods"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=DatabaseManager)
        self.engine = DashboardEngine(self.mock_db)
    
    @pytest.mark.asyncio
    async def test_update_error_count_chart(self):
        """Test updating error count chart with real data"""
        chart = ChartData(
            "error_count_test",
            "Error Count Test",
            ChartType.LINE,
            MetricType.ERROR_COUNT
        )
        
        # Mock database to return sample log entries
        mock_logs = [
            Mock(timestamp=datetime.now() - timedelta(hours=2), severity=LogSeverity.ERROR),
            Mock(timestamp=datetime.now() - timedelta(hours=1), severity=LogSeverity.ERROR),
            Mock(timestamp=datetime.now(), severity=LogSeverity.WARNING)
        ]
        self.mock_db.get_logs_by_time_range.return_value = mock_logs
        
        await self.engine._update_error_count_chart(chart)
        
        # Should have updated chart data
        assert len(chart.data) > 0
        assert chart.last_updated is not None
    
    @pytest.mark.asyncio 
    async def test_update_severity_chart(self):
        """Test updating severity distribution chart"""
        chart = ChartData(
            "severity_test",
            "Severity Test",
            ChartType.PIE,
            MetricType.SEVERITY_DISTRIBUTION
        )
        
        # Mock database response with mixed severities
        mock_logs = [
            Mock(severity=LogSeverity.ERROR),
            Mock(severity=LogSeverity.ERROR),
            Mock(severity=LogSeverity.WARNING),
            Mock(severity=LogSeverity.INFO)
        ]
        self.mock_db.get_logs_by_time_range.return_value = mock_logs
        
        await self.engine._update_severity_chart(chart)
        
        # Should have data for different severity levels
        assert len(chart.data) > 0
        assert any("ERROR" in str(item) for item in chart.data)
    
    @pytest.mark.asyncio
    async def test_update_language_chart(self):
        """Test updating language breakdown chart"""
        chart = ChartData(
            "language_test",
            "Language Test", 
            ChartType.BAR,
            MetricType.LANGUAGE_BREAKDOWN
        )
        
        # Mock database response with different languages
        mock_logs = [
            Mock(metadata={"language": "python"}),
            Mock(metadata={"language": "javascript"}),
            Mock(metadata={"language": "python"}),
            Mock(metadata={})  # No language metadata
        ]
        self.mock_db.get_logs_by_time_range.return_value = mock_logs
        
        await self.engine._update_language_chart(chart)
        
        # Should have language breakdown data
        assert len(chart.data) > 0
    
    @pytest.mark.asyncio
    async def test_update_timeline_chart(self):
        """Test updating timeline chart"""
        chart = ChartData(
            "timeline_test",
            "Timeline Test",
            ChartType.LINE,
            MetricType.TIMELINE
        )
        
        # Mock database response with timestamps
        now = datetime.now()
        mock_logs = [
            Mock(timestamp=now - timedelta(hours=3)),
            Mock(timestamp=now - timedelta(hours=2)),
            Mock(timestamp=now - timedelta(hours=1)),
            Mock(timestamp=now)
        ]
        self.mock_db.get_logs_by_time_range.return_value = mock_logs
        
        await self.engine._update_timeline_chart(chart)
        
        # Should have timeline data points
        assert len(chart.data) > 0
    
    @pytest.mark.asyncio
    async def test_update_top_errors_chart(self):
        """Test updating top errors chart"""
        chart = ChartData(
            "top_errors_test",
            "Top Errors Test",
            ChartType.BAR,
            MetricType.TOP_ERRORS
        )
        
        # Mock database response with repeated error messages
        mock_logs = [
            Mock(cleaned_log="ValueError: invalid input"),
            Mock(cleaned_log="KeyError: missing key"),
            Mock(cleaned_log="ValueError: invalid input"),
            Mock(cleaned_log="TypeError: wrong type"),
            Mock(cleaned_log="ValueError: invalid input")
        ]
        self.mock_db.get_logs_by_time_range.return_value = mock_logs
        
        await self.engine._update_top_errors_chart(chart)
        
        # Should have top errors data
        assert len(chart.data) > 0


class TestErrorHandling:
    """Test error handling throughout dashboard system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=DatabaseManager)
        self.engine = DashboardEngine(self.mock_db)
    
    @pytest.mark.asyncio
    async def test_chart_update_database_error(self):
        """Test handling database errors during chart updates"""
        chart = ChartData(
            "error_test",
            "Error Test",
            ChartType.LINE,
            MetricType.ERROR_COUNT
        )
        
        # Mock database to raise exception
        self.mock_db.get_logs_by_time_range.side_effect = Exception("Database error")
        
        # Should not raise exception, should handle gracefully
        await self.engine._update_chart_data(chart)
        
        # Chart should remain unchanged
        assert chart.data == []
    
    def test_dashboard_with_invalid_chart_data(self):
        """Test dashboard handling invalid chart data"""
        dashboard = Dashboard("test", "Test")
        
        # Try to add invalid chart (None)
        dashboard.add_chart(None)
        
        # Should handle gracefully (might add None or skip)
        # The exact behavior depends on implementation
        # This test ensures no exception is raised
    
    def test_chart_serialization_with_non_serializable_data(self):
        """Test chart serialization with non-JSON-serializable data"""
        chart = ChartData(
            "serialize_error",
            "Serialize Error",
            ChartType.LINE,
            MetricType.ERROR_COUNT,
            data=[{"timestamp": datetime.now()}]  # datetime not JSON serializable
        )
        
        # Should handle serialization gracefully
        # This might convert datetime to string or handle the error
        chart_dict = chart.to_dict()
        
        # Should return a dictionary even with problematic data
        assert isinstance(chart_dict, dict)
        assert "data" in chart_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])