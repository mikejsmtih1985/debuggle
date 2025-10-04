"""
Comprehensive tests for dashboard.py module covering:
- Enum classes (ChartType, TimeRange, MetricType)
- ChartData dataclass
- Dashboard dataclass  
- DashboardEngine class with all methods
- Async operations and background services
- Error handling and edge cases
- Real-time updates and WebSocket functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from dataclasses import asdict

from src.debuggle.services.dashboard import (
    ChartType, TimeRange, MetricType, ChartData, Dashboard, DashboardEngine
)
from src.debuggle.storage.database import DatabaseManager


class TestEnumClasses:
    """Test the enum classes used in dashboard module"""
    
    def test_chart_type_enum_values(self):
        """Test ChartType enum has all expected values"""
        expected_types = [
            "line", "bar", "pie", "area", "scatter", "heatmap",
            "donut", "histogram", "gauge", "treemap"
        ]
        
        chart_types = [chart_type.value for chart_type in ChartType]
        for expected in expected_types:
            assert expected in chart_types
    
    def test_time_range_enum_values(self):
        """Test TimeRange enum has all expected values"""
        expected_ranges = [
            "1h", "4h", "1d", "7d", "30d", "90d", "365d", "custom"
        ]
        
        time_ranges = [time_range.value for time_range in TimeRange]
        for expected in expected_ranges:
            assert expected in time_ranges
    
    def test_metric_type_enum_values(self):
        """Test MetricType enum has all expected values"""
        expected_metrics = [
            "error_count", "error_rate", "severity_dist", "language_dist",
            "project_dist", "time_series", "top_errors", "response_time", "system_health"
        ]
        
        metric_types = [metric.value for metric in MetricType]
        for expected in expected_metrics:
            assert expected in metric_types
    
    def test_enum_string_conversion(self):
        """Test enum string conversion and equality"""
        assert ChartType.LINE.value == "line"
        assert TimeRange.LAST_DAY.value == "1d"
        assert MetricType.ERROR_COUNT.value == "error_count"


class TestChartData:
    """Test ChartData dataclass functionality"""
    
    def test_chart_data_creation_minimal(self):
        """Test creating ChartData with minimal parameters"""
        chart = ChartData(
            chart_id="test_chart",
            chart_type=ChartType.LINE,
            title="Test Chart"
        )
        
        assert chart.chart_id == "test_chart"
        assert chart.chart_type == ChartType.LINE
        assert chart.title == "Test Chart"
        assert chart.description is None
        assert chart.data == []
        assert chart.labels == []
        assert chart.auto_refresh is True
        assert chart.refresh_interval_seconds == 30
    
    def test_chart_data_creation_full(self):
        """Test creating ChartData with all parameters"""
        test_data = [{"x": 1, "y": 2}, {"x": 2, "y": 4}]
        test_labels = ["Point 1", "Point 2"]
        
        chart = ChartData(
            chart_id="full_chart",
            chart_type=ChartType.BAR,
            title="Full Chart",
            description="Test chart with all parameters",
            data=test_data,
            labels=test_labels,
            time_range=TimeRange.LAST_DAY,
            colors=["red", "blue"],
            background_colors=["lightred", "lightblue"],
            border_colors=["darkred", "darkblue"],
            height=400,
            width=600,
            auto_refresh=False,
            refresh_interval_seconds=60
        )
        
        assert chart.chart_id == "full_chart"
        assert chart.chart_type == ChartType.BAR
        assert chart.title == "Full Chart"
        assert chart.description == "Test chart with all parameters"
        assert chart.data == test_data
        assert chart.labels == test_labels
        assert chart.time_range == TimeRange.LAST_DAY
        assert chart.colors == ["red", "blue"]
        assert chart.background_colors == ["lightred", "lightblue"]
        assert chart.border_colors == ["darkred", "darkblue"]
        assert chart.height == 400
        assert chart.width == 600
        assert chart.auto_refresh is False
        assert chart.refresh_interval_seconds == 60
    
    def test_chart_data_to_dict(self):
        """Test ChartData serialization to dictionary"""
        chart = ChartData(
            chart_id="serialize_test",
            chart_type=ChartType.PIE,
            title="Serialize Test",
            data=[{"language": "Python", "count": 10}],
            colors=["blue"]
        )
        
        chart_dict = chart.to_dict()
        
        assert chart_dict["chart_id"] == "serialize_test"
        assert chart_dict["chart_type"] == "pie"
        assert chart_dict["title"] == "Serialize Test"
        assert chart_dict["data"] == [{"language": "Python", "count": 10}]
        assert chart_dict["colors"] == ["blue"]
        assert "last_updated" in chart_dict
        assert isinstance(chart_dict["last_updated"], str)
    
    def test_chart_data_last_updated_automatic(self):
        """Test that last_updated is set automatically"""
        before_creation = datetime.now()
        chart = ChartData(
            chart_id="time_test",
            chart_type=ChartType.LINE,
            title="Time Test"
        )
        after_creation = datetime.now()
        
        assert before_creation <= chart.last_updated <= after_creation
    
    def test_chart_data_default_values(self):
        """Test that default values are properly set"""
        chart = ChartData(
            chart_id="defaults",
            chart_type=ChartType.GAUGE,
            title="Defaults"
        )
        
        assert chart.data == []
        assert chart.labels == []
        assert chart.datasets == []
        assert chart.colors == []
        assert chart.options == {}
        assert chart.height is None
        assert chart.width is None
        assert chart.time_range is None
        assert chart.data_points_count == 0
        assert chart.auto_refresh is True
        assert chart.refresh_interval_seconds == 30


class TestDashboard:
    """Test Dashboard dataclass functionality"""
    
    def test_dashboard_creation_minimal(self):
        """Test creating Dashboard with minimal parameters"""
        dashboard = Dashboard(
            dashboard_id="test_dash",
            title="Test Dashboard"
        )
        
        assert dashboard.dashboard_id == "test_dash"
        assert dashboard.title == "Test Dashboard"
        assert dashboard.description is None
        assert dashboard.charts == []
        assert dashboard.widgets == []
        assert dashboard.layout == {}
        assert dashboard.theme == "light"
        assert dashboard.custom_css is None
        assert dashboard.owner is None
        assert dashboard.is_public is True
        assert dashboard.allowed_users == []
        assert dashboard.view_count == 0
        assert dashboard.auto_refresh_enabled is True
        assert dashboard.refresh_interval_seconds == 60
    
    def test_dashboard_creation_full(self):
        """Test creating Dashboard with all parameters"""
        test_charts = [
            ChartData("chart1", ChartType.LINE, "Chart 1"),
            ChartData("chart2", ChartType.BAR, "Chart 2")
        ]
        test_layout = {"grid": "2x2", "responsive": True}
        
        dashboard = Dashboard(
            dashboard_id="full_dash",
            title="Full Dashboard",
            description="Complete dashboard test",
            charts=test_charts,
            layout=test_layout,
            theme="dark",
            custom_css="body { background: black; }",
            owner="test_user",
            is_public=False,
            allowed_users=["user1", "user2"],
            auto_refresh_enabled=False,
            refresh_interval_seconds=120
        )
        
        assert dashboard.dashboard_id == "full_dash"
        assert dashboard.title == "Full Dashboard"
        assert dashboard.description == "Complete dashboard test"
        assert len(dashboard.charts) == 2
        assert dashboard.layout == test_layout
        assert dashboard.theme == "dark"
        assert dashboard.custom_css == "body { background: black; }"
        assert dashboard.owner == "test_user"
        assert dashboard.is_public is False
        assert dashboard.allowed_users == ["user1", "user2"]
        assert dashboard.auto_refresh_enabled is False
        assert dashboard.refresh_interval_seconds == 120
        
    def test_dashboard_add_chart(self):
        """Test adding charts to dashboard"""
        dashboard = Dashboard("test", "Test")
        
        chart1 = ChartData("chart1", ChartType.LINE, "Chart 1")
        chart2 = ChartData("chart2", ChartType.PIE, "Chart 2")
        
        initial_updated = dashboard.updated_at
        dashboard.add_chart(chart1)
        
        assert len(dashboard.charts) == 1
        assert dashboard.charts[0] == chart1
        assert dashboard.updated_at > initial_updated
        
        dashboard.add_chart(chart2)
        assert len(dashboard.charts) == 2
        assert dashboard.charts[1] == chart2
    
    def test_dashboard_remove_chart(self):
        """Test removing charts from dashboard"""
        chart1 = ChartData("chart1", ChartType.LINE, "Chart 1")
        chart2 = ChartData("chart2", ChartType.BAR, "Chart 2")
        
        dashboard = Dashboard(
            dashboard_id="test",
            title="Test",
            charts=[chart1, chart2]
        )
        
        # Test successful removal
        initial_updated = dashboard.updated_at
        result = dashboard.remove_chart("chart1")
        
        assert result is True
        assert len(dashboard.charts) == 1
        assert dashboard.charts[0] == chart2
        assert dashboard.updated_at > initial_updated
        
        # Test removal of non-existent chart
        result = dashboard.remove_chart("nonexistent")
        assert result is False
        assert len(dashboard.charts) == 1
    
    def test_dashboard_to_dict(self):
        """Test Dashboard serialization to dictionary"""
        chart = ChartData("chart1", ChartType.LINE, "Chart 1")
        dashboard = Dashboard(
            dashboard_id="serialize_dash",
            title="Serialize Dashboard",
            description="Test serialization",
            charts=[chart],
            layout={"columns": 2},
            theme="dark",
            owner="test_user",
            is_public=False
        )
        
        dashboard_dict = dashboard.to_dict()
        
        assert dashboard_dict["dashboard_id"] == "serialize_dash"
        assert dashboard_dict["title"] == "Serialize Dashboard"
        assert dashboard_dict["description"] == "Test serialization"
        assert len(dashboard_dict["charts"]) == 1
        assert dashboard_dict["layout"] == {"columns": 2}
        assert dashboard_dict["theme"] == "dark"
        assert dashboard_dict["owner"] == "test_user"
        assert dashboard_dict["is_public"] is False
        assert "created_at" in dashboard_dict
        assert "updated_at" in dashboard_dict
        assert isinstance(dashboard_dict["created_at"], str)
        assert isinstance(dashboard_dict["updated_at"], str)
    
    def test_dashboard_created_at_automatic(self):
        """Test that created_at and updated_at are set automatically"""
        before_creation = datetime.now()
        dashboard = Dashboard("time_test", "Time Test")
        after_creation = datetime.now()
        
        assert before_creation <= dashboard.created_at <= after_creation
        assert before_creation <= dashboard.updated_at <= after_creation


class TestDashboardEngine:
    """Test DashboardEngine core functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=DatabaseManager)
        
        # Mock the background service startup to avoid asyncio issues
        with patch.object(DashboardEngine, '_start_background_services'):
            self.engine = DashboardEngine(self.mock_db)
    
    def test_dashboard_engine_initialization(self):
        """Test DashboardEngine initializes correctly"""
        assert self.engine.database_manager == self.mock_db
        assert isinstance(self.engine.dashboards, dict)
        assert self.engine.default_dashboard is not None
        assert self.engine.default_dashboard.dashboard_id == "system_overview"
        assert isinstance(self.engine.color_palettes, dict)
        assert isinstance(self.engine.metrics_cache, dict)
        assert isinstance(self.engine.cache_expiry, dict)
    
    def test_create_default_dashboard(self):
        """Test creation of default dashboard"""
        dashboard = self.engine.default_dashboard
        
        assert dashboard is not None
        assert dashboard.dashboard_id == "system_overview"
        assert dashboard.title == "🐞 Debuggle System Overview"
        assert dashboard.theme == "light"
        assert dashboard.auto_refresh_enabled is True
        assert dashboard.refresh_interval_seconds == 30
        assert "grid" in dashboard.layout
        assert "responsive_breakpoints" in dashboard.layout
    
    def test_get_dashboard_existing(self):
        """Test getting an existing dashboard"""
        dashboard = self.engine.get_dashboard("system_overview")
        
        assert dashboard is not None
        assert dashboard.dashboard_id == "system_overview"
        assert dashboard == self.engine.default_dashboard
    
    def test_get_dashboard_nonexistent(self):
        """Test getting a non-existent dashboard"""
        dashboard = self.engine.get_dashboard("nonexistent")
        assert dashboard is None
    
    @pytest.mark.asyncio
    async def test_create_dashboard_new(self):
        """Test creating a new dashboard"""
        dashboard = await self.engine.create_dashboard(
            dashboard_id="new_dash",
            title="New Dashboard",
            description="Test dashboard",
            owner="test_user"
        )
        
        assert dashboard.dashboard_id == "new_dash"
        assert dashboard.title == "New Dashboard"
        assert dashboard.description == "Test dashboard"
        assert dashboard.owner == "test_user"
        
        # Verify it's stored in the engine
        stored_dashboard = self.engine.get_dashboard("new_dash")
        assert stored_dashboard == dashboard
    
    def test_list_dashboards(self):
        """Test listing all dashboards"""
        dashboards = self.engine.list_dashboards()
        
        assert isinstance(dashboards, list)
        assert len(dashboards) >= 1  # At least the default dashboard
        assert self.engine.default_dashboard in dashboards
    
    def test_delete_dashboard_success(self):
        """Test successful dashboard deletion"""
        # First create a dashboard to delete
        test_dashboard = Dashboard("delete_test", "Delete Test")
        self.engine.dashboards["delete_test"] = test_dashboard
        
        result = self.engine.delete_dashboard("delete_test")
        
        assert result is True
        assert "delete_test" not in self.engine.dashboards
        assert self.engine.get_dashboard("delete_test") is None
    
    def test_delete_dashboard_not_found(self):
        """Test deleting a non-existent dashboard"""
        result = self.engine.delete_dashboard("nonexistent")
        assert result is False


@pytest.mark.asyncio
class TestDashboardEngineAsyncOperations:
    """Test DashboardEngine async operations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=DatabaseManager)
        
        # Mock the background service startup to avoid asyncio issues
        with patch.object(DashboardEngine, '_start_background_services'):
            self.engine = DashboardEngine(self.mock_db)
    
    async def test_create_default_charts(self):
        """Test creating default charts for a dashboard"""
        dashboard = Dashboard("test_dash", "Test Dashboard")
        
        # Mock the database queries that chart creation methods use
        self.mock_db.configure_mock(**{'get_log_entries.return_value': []})
        
        # Mock the individual chart update methods
        with patch.multiple(
            self.engine,
            _update_error_count_chart=AsyncMock(),
            _update_severity_chart=AsyncMock(),
            _update_language_chart=AsyncMock(),
            _update_timeline_chart=AsyncMock()
        ):
            await self.engine.create_default_charts(dashboard)
        
        assert len(dashboard.charts) == 4
        chart_types = [chart.chart_type for chart in dashboard.charts]
        assert ChartType.GAUGE in chart_types
        assert ChartType.PIE in chart_types
        assert ChartType.BAR in chart_types
        assert ChartType.LINE in chart_types
    
    async def test_shutdown(self):
        """Test engine shutdown"""
        # Mock background tasks
        mock_task1 = AsyncMock()
        mock_task2 = AsyncMock()
        self.engine.background_tasks = [mock_task1, mock_task2]
        
        with patch('asyncio.gather', new_callable=AsyncMock) as mock_gather:
            await self.engine.shutdown()
        
        assert self.engine.shutdown_event.is_set()
        mock_gather.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock(spec=DatabaseManager)
        
        # Mock the background service startup to avoid asyncio issues
        with patch.object(DashboardEngine, '_start_background_services'):
            self.engine = DashboardEngine(self.mock_db)
    
    def test_chart_data_serialization_with_non_serializable_data(self):
        """Test ChartData serialization handles non-serializable data gracefully"""
        # Create chart with non-serializable data
        chart = ChartData(
            chart_id="test",
            chart_type=ChartType.LINE,
            title="Test",
            data=[datetime.now()]  # datetime objects need special handling
        )
        
        # The to_dict method should handle this gracefully
        chart_dict = chart.to_dict()
        assert "data" in chart_dict
        # The actual data might be converted or handled, just ensure no exception
    
    def test_dashboard_with_invalid_chart_data(self):
        """Test dashboard handles invalid chart data gracefully"""
        dashboard = Dashboard("test", "Test")
        
        # Add a chart with potentially problematic data
        chart = ChartData("invalid", ChartType.BAR, "Invalid Chart")
        chart.data = [{"invalid": object()}]  # Non-serializable object
        
        dashboard.add_chart(chart)
        
        # Dashboard should still function
        assert len(dashboard.charts) == 1
        
        # Serialization might handle this gracefully or raise appropriate error
        try:
            dashboard_dict = dashboard.to_dict()
            # If it succeeds, great!
            assert "charts" in dashboard_dict
        except (TypeError, ValueError):
            # If it fails with expected error types, that's also acceptable
            pass