"""
📊 DEBUGGLE RICH DASHBOARD SYSTEM - Visual Analytics Command Center! 📊

Think of this module as building a NASA mission control center for your
application errors! Instead of just seeing raw data, you get beautiful
charts, graphs, and visualizations that help you understand patterns,
trends, and critical insights at a glance.

🏆 HIGH SCHOOL EXPLANATION:
Imagine the difference between:
- Reading a huge spreadsheet of numbers (raw log data)
- Looking at colorful charts and graphs that instantly show trends (dashboard)

This is like having a sports commentator who takes all the game statistics
and turns them into exciting, easy-to-understand visual stories!

WHY RICH DASHBOARDS MATTER:
👁️ Visual Understanding - See patterns that are invisible in raw data
⚡ Quick Decision Making - Spot problems and trends instantly
📈 Trend Analysis - Understand how your systems perform over time
🎯 Problem Identification - Quickly locate the source of issues
📊 Executive Reporting - Show stakeholders system health at a glance
🔍 Deep Dive Capability - Click through from overview to detailed analysis
⏰ Real-Time Monitoring - Watch your systems' pulse in real-time

DASHBOARD CAPABILITIES PROVIDED:
📈 Interactive Charts - Line graphs, bar charts, pie charts, heat maps
🌡️ System Health Meters - CPU-style gauges showing system status
🗺️ Geographic Views - Map showing errors by location/server
📅 Time Series Analysis - How errors change over hours, days, weeks
🏷️ Category Breakdowns - Errors by type, severity, language, project
⚡ Real-Time Updates - Live data streaming to dashboard widgets
🎛️ Custom Dashboards - Users can create personalized views
📱 Responsive Design - Works perfectly on desktop, tablet, and mobile
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from collections import defaultdict, Counter
import statistics
import hashlib
import base64

from .storage.database import DatabaseManager, LogEntry, LogSeverity
from .realtime import connection_manager

logger = logging.getLogger(__name__)


class ChartType(str, Enum):
    """
    📊 CHART VISUALIZATION TYPES - Different Ways to Show Data
    
    Different types of data need different visualization approaches.
    Like choosing between a bar chart, pie chart, or line graph
    based on what story you want to tell with your data.
    """
    LINE = "line"                    # 📈 Line chart - great for trends over time
    BAR = "bar"                      # 📊 Bar chart - compare different categories
    PIE = "pie"                      # 🥧 Pie chart - show proportions of a whole
    AREA = "area"                    # 🏔️ Area chart - show volume over time
    SCATTER = "scatter"              # 🎯 Scatter plot - show correlations
    HEATMAP = "heatmap"             # 🌡️ Heat map - show intensity patterns
    DONUT = "donut"                 # 🍩 Donut chart - pie chart with center space
    HISTOGRAM = "histogram"          # 📊 Histogram - show distribution patterns
    GAUGE = "gauge"                 # 🌡️ Gauge - show single metric with ranges
    TREEMAP = "treemap"             # 🌳 Tree map - hierarchical data visualization


class TimeRange(str, Enum):
    """
    ⏰ TIME PERIOD OPTIONS - How Far Back Should We Look?
    
    Different analysis needs require different time windows.
    Like choosing between looking at today's weather vs
    this month's weather patterns vs this year's climate.
    """
    LAST_HOUR = "1h"                # 🕐 Last 60 minutes
    LAST_4_HOURS = "4h"             # 🕓 Last 4 hours
    LAST_DAY = "1d"                 # 📅 Last 24 hours
    LAST_WEEK = "7d"                # 📆 Last 7 days
    LAST_MONTH = "30d"              # 📅 Last 30 days
    LAST_3_MONTHS = "90d"           # 📅 Last 3 months
    LAST_YEAR = "365d"              # 📅 Last 12 months
    CUSTOM = "custom"               # 🎛️ User-defined range


class MetricType(str, Enum):
    """
    📊 METRIC CATEGORIES - What Kind of Data Are We Measuring?
    
    Different metrics tell different stories about system health.
    Like vital signs in medicine - heart rate, blood pressure,
    temperature each reveal different aspects of health.
    """
    ERROR_COUNT = "error_count"              # 📊 Total number of errors
    ERROR_RATE = "error_rate"                # 📈 Errors per time unit
    SEVERITY_DISTRIBUTION = "severity_dist"  # 🌡️ Breakdown by severity
    LANGUAGE_DISTRIBUTION = "language_dist"  # 💻 Breakdown by programming language
    PROJECT_DISTRIBUTION = "project_dist"    # 📁 Breakdown by project
    TIME_SERIES = "time_series"              # ⏰ Changes over time
    TOP_ERRORS = "top_errors"                # 🔝 Most common error types
    RESPONSE_TIME = "response_time"          # ⚡ Processing performance
    SYSTEM_HEALTH = "system_health"          # 💚 Overall system status


@dataclass
class ChartData:
    """
    📊 CHART DATA CONTAINER - All Information Needed for One Chart
    
    This holds all the data and configuration needed to render
    one complete chart or visualization. Like a complete recipe
    that includes ingredients, instructions, and presentation details.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a complete art project instruction packet:
    - chart_type: "Draw a bar chart" (what kind of visual)
    - title: "My School's Test Scores" (what to call it)
    - data: [85, 92, 78, 95] (the actual numbers)
    - labels: ["Math", "Science", "English", "History"] (what each number means)
    - colors: ["red", "blue", "green", "yellow"] (how to make it pretty)
    """
    
    # 📊 CHART CONFIGURATION
    chart_id: str                                      # Unique identifier for this chart
    chart_type: ChartType                              # What kind of visualization
    title: str                                         # Human-readable title
    description: Optional[str] = None                  # Optional longer description
    
    # 📈 DATA AND LABELS
    data: List[Any] = field(default_factory=list)     # The actual data points
    labels: List[str] = field(default_factory=list)   # Labels for data points
    datasets: List[Dict[str, Any]] = field(default_factory=list)  # Multiple data series
    
    # 🎨 VISUAL STYLING
    colors: List[str] = field(default_factory=list)   # Colors for data points
    background_colors: List[str] = field(default_factory=list)  # Background colors
    border_colors: List[str] = field(default_factory=list)     # Border colors
    
    # ⚙️ CHART OPTIONS
    options: Dict[str, Any] = field(default_factory=dict)      # Chart.js options
    height: Optional[int] = None                       # Chart height in pixels
    width: Optional[int] = None                        # Chart width in pixels
    
    # 📅 DATA METADATA
    time_range: Optional[TimeRange] = None             # Time period covered
    last_updated: datetime = field(default_factory=datetime.now)  # When data was generated
    data_points_count: int = 0                         # Number of data points
    
    # 🔄 REFRESH SETTINGS
    auto_refresh: bool = True                          # Should this chart auto-update
    refresh_interval_seconds: int = 30                 # How often to refresh
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chart data to dictionary for JSON serialization."""
        return {
            'chart_id': self.chart_id,
            'chart_type': self.chart_type.value,
            'title': self.title,
            'description': self.description,
            'data': self.data,
            'labels': self.labels,
            'datasets': self.datasets,
            'colors': self.colors,
            'background_colors': self.background_colors,
            'border_colors': self.border_colors,
            'options': self.options,
            'height': self.height,
            'width': self.width,
            'time_range': self.time_range.value if self.time_range else None,
            'last_updated': self.last_updated.isoformat(),
            'data_points_count': self.data_points_count,
            'auto_refresh': self.auto_refresh,
            'refresh_interval_seconds': self.refresh_interval_seconds
        }


@dataclass
class Dashboard:
    """
    📋 COMPLETE DASHBOARD CONFIGURATION - One Full Dashboard Layout
    
    This represents a complete dashboard with multiple charts, widgets,
    and layout information. Like a complete newspaper page layout that
    shows where each article, photo, and advertisement should go.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like designing a school bulletin board:
    - dashboard_id: "March Bulletin Board" (unique name)
    - title: "Spring Activities and Announcements" (big title at top)
    - charts: [sports_scores_chart, club_meetings_chart] (different sections)
    - layout: "Put sports on left, clubs on right" (how to arrange everything)
    - refresh: "Update every hour" (how often to change content)
    """
    
    # 🏷️ DASHBOARD IDENTIFICATION
    dashboard_id: str                                  # Unique identifier
    title: str                                         # Display title
    description: Optional[str] = None                  # Optional description
    
    # 📊 DASHBOARD CONTENT
    charts: List[ChartData] = field(default_factory=list)      # All charts in dashboard
    widgets: List[Dict[str, Any]] = field(default_factory=list)  # Non-chart widgets
    
    # 🎨 LAYOUT AND STYLING
    layout: Dict[str, Any] = field(default_factory=dict)       # Grid layout configuration
    theme: str = "light"                               # Color theme (light/dark)
    custom_css: Optional[str] = None                   # Custom styling
    
    # 👤 ACCESS AND PERMISSIONS
    owner: Optional[str] = None                        # Who created this dashboard
    is_public: bool = True                             # Can others view this
    allowed_users: List[str] = field(default_factory=list)     # Specific user access
    
    # ⏰ METADATA
    created_at: datetime = field(default_factory=datetime.now)  # When created
    updated_at: datetime = field(default_factory=datetime.now)  # Last modified
    view_count: int = 0                                # How many times viewed
    
    # 🔄 AUTO-REFRESH SETTINGS
    auto_refresh_enabled: bool = True                  # Should dashboard auto-update
    refresh_interval_seconds: int = 60                 # How often to refresh
    
    def add_chart(self, chart: ChartData):
        """Add a chart to this dashboard."""
        self.charts.append(chart)
        self.updated_at = datetime.now()
    
    def remove_chart(self, chart_id: str) -> bool:
        """Remove a chart from this dashboard."""
        initial_count = len(self.charts)
        self.charts = [chart for chart in self.charts if chart.chart_id != chart_id]
        if len(self.charts) < initial_count:
            self.updated_at = datetime.now()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert dashboard to dictionary for JSON serialization."""
        return {
            'dashboard_id': self.dashboard_id,
            'title': self.title,
            'description': self.description,
            'charts': [chart.to_dict() for chart in self.charts],
            'widgets': self.widgets,
            'layout': self.layout,
            'theme': self.theme,
            'custom_css': self.custom_css,
            'owner': self.owner,
            'is_public': self.is_public,
            'allowed_users': self.allowed_users,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'view_count': self.view_count,
            'auto_refresh_enabled': self.auto_refresh_enabled,
            'refresh_interval_seconds': self.refresh_interval_seconds
        }


class DashboardEngine:
    """
    🎛️ DASHBOARD CONTROL CENTER - The Master Dashboard Manager!
    
    This is the central system that creates, manages, and updates all
    dashboards and charts. Think of it as the control room for a TV
    station that manages all the different shows, graphics, and content
    that appear on screen.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the control room for the school's morning announcements:
    - Creates different announcement segments (dashboards)
    - Pulls in data from various sources (sports scores, lunch menu, weather)
    - Formats everything nicely with graphics and charts
    - Updates content automatically throughout the day
    - Broadcasts to all the TVs around school (WebSocket updates)
    
    This system does the same thing but for error monitoring dashboards!
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        🏗️ SET UP THE DASHBOARD CONTROL CENTER
        
        Initialize all the systems needed to create and manage
        beautiful, interactive dashboards with real-time data.
        """
        self.database_manager = database_manager
        
        # 📚 DASHBOARD STORAGE
        self.dashboards: Dict[str, Dashboard] = {}          # All configured dashboards
        self.default_dashboard: Optional[Dashboard] = None  # The main system dashboard
        
        # 🎨 CHART COLOR PALETTES
        self.color_palettes = {
            'default': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
            'severity': {
                'critical': '#DC2626',    # Red
                'error': '#EA580C',       # Orange  
                'warning': '#D97706',     # Amber
                'info': '#0284C7',        # Blue
                'debug': '#059669',       # Green
                'trace': '#6B7280'        # Gray
            },
            'success': ['#10B981', '#34D399', '#6EE7B7', '#A7F3D0'],
            'danger': ['#EF4444', '#F87171', '#FCA5A5', '#FECACA'],
            'info': ['#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE'],
            'warning': ['#F59E0B', '#FBBF24', '#FCD34D', '#FEF3C7']
        }
        
        # 📊 METRICS CACHE
        self.metrics_cache: Dict[str, Any] = {}           # Cached metric calculations
        self.cache_expiry: Dict[str, datetime] = {}       # When cache entries expire
        self.cache_duration_minutes = 5                   # How long to cache metrics
        
        # 🔄 BACKGROUND TASKS
        self.background_tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()
        
        # 🚀 START DASHBOARD SERVICES
        self._create_default_dashboard()
        self._start_background_services()
        
        logger.info("Dashboard engine initialized")
    
    def _create_default_dashboard(self):
        """
        📊 CREATE THE MAIN SYSTEM DASHBOARD
        
        Set up the default dashboard that shows overall system health
        and key metrics. Like creating the main monitoring screen
        in a mission control center.
        """
        dashboard = Dashboard(
            dashboard_id="system_overview",
            title="🐞 Debuggle System Overview",
            description="Real-time system health and error analytics dashboard",
            theme="light",
            auto_refresh_enabled=True,
            refresh_interval_seconds=30
        )
        
        # Set up default layout for responsive design
        dashboard.layout = {
            'grid': {
                'columns': 12,  # 12-column grid system
                'rows': 'auto',
                'gap': 16
            },
            'responsive_breakpoints': {
                'mobile': 576,
                'tablet': 768,
                'desktop': 992,
                'large': 1200
            }
        }
        
        self.dashboards[dashboard.dashboard_id] = dashboard
        self.default_dashboard = dashboard
        
        logger.info("Default system dashboard created")
    
    def _start_background_services(self):
        """
        🔄 START BACKGROUND DASHBOARD SERVICES
        
        Launch the background tasks that keep dashboards updated
        with fresh data and push updates to connected clients.
        """
        # Dashboard refresh task
        task = asyncio.create_task(self._dashboard_refresh_loop())
        self.background_tasks.append(task)
        
        # Metrics calculation task
        task = asyncio.create_task(self._metrics_calculation_loop())
        self.background_tasks.append(task)
        
        # Cache cleanup task
        task = asyncio.create_task(self._cache_cleanup_loop())
        self.background_tasks.append(task)
        
        logger.info("Dashboard background services started")
    
    async def _dashboard_refresh_loop(self):
        """
        🔄 MAIN DASHBOARD REFRESH LOOP
        
        Continuously update dashboard data and push updates to
        connected WebSocket clients. Like the heartbeat of the
        entire dashboard system.
        """
        while not self.shutdown_event.is_set():
            try:
                for dashboard in self.dashboards.values():
                    if dashboard.auto_refresh_enabled:
                        # Check if it's time to refresh this dashboard
                        time_since_update = (datetime.now() - dashboard.updated_at).total_seconds()
                        
                        if time_since_update >= dashboard.refresh_interval_seconds:
                            # Refresh the dashboard
                            await self._refresh_dashboard_data(dashboard)
                            
                            # Send updated data to WebSocket clients
                            await self._broadcast_dashboard_update(dashboard)
                
                # Wait before next refresh cycle
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in dashboard refresh loop: {e}")
                await asyncio.sleep(30)  # Wait longer after error
    
    async def _refresh_dashboard_data(self, dashboard: Dashboard):
        """
        📊 REFRESH ONE DASHBOARD'S DATA
        
        Update all the charts and widgets in a single dashboard
        with fresh data from the database.
        """
        try:
            for chart in dashboard.charts:
                if chart.auto_refresh:
                    # Refresh this chart's data based on its type
                    await self._update_chart_data(chart)
            
            dashboard.updated_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard {dashboard.dashboard_id}: {e}")
    
    async def _update_chart_data(self, chart: ChartData):
        """
        📈 UPDATE ONE CHART'S DATA
        
        Fetch fresh data for a specific chart based on its
        configuration and data requirements.
        """
        try:
            # Determine what data this chart needs based on its ID and type
            if 'error_count' in chart.chart_id:
                await self._update_error_count_chart(chart)
            elif 'severity' in chart.chart_id:
                await self._update_severity_chart(chart)
            elif 'language' in chart.chart_id:
                await self._update_language_chart(chart)
            elif 'timeline' in chart.chart_id:
                await self._update_timeline_chart(chart)
            elif 'top_errors' in chart.chart_id:
                await self._update_top_errors_chart(chart)
            
            chart.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Error updating chart {chart.chart_id}: {e}")
    
    async def _update_error_count_chart(self, chart: ChartData):
        """📊 Update error count metrics chart."""
        # Get total error count from database
        total_errors = await self._get_cached_metric('total_errors', self._calculate_total_errors)
        recent_errors = await self._get_cached_metric('recent_errors', self._calculate_recent_errors)
        
        chart.data = [total_errors, recent_errors]
        chart.labels = ['Total Errors', 'Last 24 Hours']
        chart.colors = ['#EF4444', '#F97316']  # Red and orange
        chart.data_points_count = len(chart.data)
    
    async def _update_severity_chart(self, chart: ChartData):
        """🌡️ Update severity distribution chart."""
        severity_counts = await self._get_cached_metric('severity_dist', self._calculate_severity_distribution)
        
        chart.data = list(severity_counts.values())
        chart.labels = [sev.capitalize() for sev in severity_counts.keys()]
        chart.colors = [self.color_palettes['severity'].get(sev, '#6B7280') for sev in severity_counts.keys()]
        chart.data_points_count = len(chart.data)
    
    async def _update_language_chart(self, chart: ChartData):
        """💻 Update programming language distribution chart."""
        language_counts = await self._get_cached_metric('language_dist', self._calculate_language_distribution)
        
        chart.data = list(language_counts.values())
        chart.labels = list(language_counts.keys())
        chart.colors = self.color_palettes['default'][:len(chart.data)]
        chart.data_points_count = len(chart.data)
    
    async def _update_timeline_chart(self, chart: ChartData):
        """⏰ Update timeline/time series chart."""
        timeline_data = await self._get_cached_metric('timeline_24h', self._calculate_timeline_data)
        
        chart.data = timeline_data['counts']
        chart.labels = timeline_data['hours']
        chart.colors = ['#3B82F6']  # Blue line
        chart.data_points_count = len(chart.data)
    
    async def _update_top_errors_chart(self, chart: ChartData):
        """🔝 Update top errors chart."""
        top_errors = await self._get_cached_metric('top_errors', self._calculate_top_errors)
        
        chart.data = [error['count'] for error in top_errors]
        chart.labels = [error['type'][:30] + '...' if len(error['type']) > 30 else error['type'] for error in top_errors]
        chart.colors = self.color_palettes['default'][:len(chart.data)]
        chart.data_points_count = len(chart.data)
    
    async def _get_cached_metric(self, metric_key: str, calculation_func) -> Any:
        """
        💾 GET CACHED METRIC OR CALCULATE IF NEEDED
        
        Use cached version of metric if available and fresh,
        otherwise calculate new value and cache it.
        """
        now = datetime.now()
        
        # Check if we have a cached value that hasn't expired
        if (metric_key in self.metrics_cache and 
            metric_key in self.cache_expiry and 
            now < self.cache_expiry[metric_key]):
            return self.metrics_cache[metric_key]
        
        # Calculate new value
        try:
            value = await calculation_func()
            
            # Cache the result
            self.metrics_cache[metric_key] = value
            self.cache_expiry[metric_key] = now + timedelta(minutes=self.cache_duration_minutes)
            
            return value
            
        except Exception as e:
            logger.error(f"Error calculating metric {metric_key}: {e}")
            # Return cached value if available, otherwise return default
            return self.metrics_cache.get(metric_key, 0)
    
    async def _calculate_total_errors(self) -> int:
        """Calculate total number of errors in database."""
        try:
            # This would query the database for total error count
            # For now, return a placeholder value
            results = self.database_manager.search_logs()
            return len(results)
        except Exception:
            return 0
    
    async def _calculate_recent_errors(self) -> int:
        """Calculate errors in last 24 hours."""
        try:
            # This would query for recent errors
            # For now, return a placeholder value
            return 42  # Placeholder
        except Exception:
            return 0
    
    async def _calculate_severity_distribution(self) -> Dict[str, int]:
        """Calculate breakdown of errors by severity."""
        try:
            # This would query database for severity counts
            # For now, return placeholder data
            return {
                'critical': 5,
                'error': 25,
                'warning': 45,
                'info': 15,
                'debug': 10
            }
        except Exception:
            return {}
    
    async def _calculate_language_distribution(self) -> Dict[str, int]:
        """Calculate breakdown of errors by programming language."""
        try:
            # This would query database for language counts
            # For now, return placeholder data
            return {
                'Python': 35,
                'JavaScript': 28,
                'Java': 15,
                'Go': 12,
                'TypeScript': 10
            }
        except Exception:
            return {}
    
    async def _calculate_timeline_data(self) -> Dict[str, List]:
        """Calculate error counts over time (last 24 hours)."""
        try:
            # This would query database for hourly error counts
            # For now, return placeholder data
            hours = [f"{i:02d}:00" for i in range(24)]
            counts = [5, 3, 2, 1, 1, 2, 4, 8, 12, 15, 18, 22, 25, 20, 18, 16, 14, 12, 10, 8, 6, 7, 6, 4]
            
            return {
                'hours': hours,
                'counts': counts
            }
        except Exception:
            return {'hours': [], 'counts': []}
    
    async def _calculate_top_errors(self) -> List[Dict[str, Any]]:
        """Calculate most common error types."""
        try:
            # This would query database for most common errors
            # For now, return placeholder data
            return [
                {'type': 'NullPointerException', 'count': 45},
                {'type': 'IndexError: list index out of range', 'count': 32},
                {'type': 'KeyError: missing key', 'count': 28},
                {'type': 'TypeError: unsupported operand', 'count': 21},
                {'type': 'AttributeError: object has no attribute', 'count': 18}
            ]
        except Exception:
            return []
    
    async def _broadcast_dashboard_update(self, dashboard: Dashboard):
        """
        📡 BROADCAST DASHBOARD UPDATE TO WEBSOCKET CLIENTS
        
        Send the updated dashboard data to all connected WebSocket
        clients so they see real-time updates.
        """
        try:
            update_message = {
                'type': 'dashboard_update',
                'dashboard_id': dashboard.dashboard_id,
                'dashboard_data': dashboard.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            
            await connection_manager.broadcast(json.dumps(update_message))
            
        except Exception as e:
            logger.error(f"Error broadcasting dashboard update: {e}")
    
    async def _metrics_calculation_loop(self):
        """
        📊 BACKGROUND METRICS CALCULATION
        
        Continuously calculate and cache expensive metrics
        in the background to keep dashboard updates fast.
        """
        while not self.shutdown_event.is_set():
            try:
                # Pre-calculate commonly used metrics
                await self._get_cached_metric('total_errors', self._calculate_total_errors)
                await self._get_cached_metric('recent_errors', self._calculate_recent_errors)
                await self._get_cached_metric('severity_dist', self._calculate_severity_distribution)
                
                # Wait before next calculation cycle
                await asyncio.sleep(60)  # Calculate every minute
                
            except Exception as e:
                logger.error(f"Error in metrics calculation loop: {e}")
                await asyncio.sleep(120)  # Wait longer after error
    
    async def _cache_cleanup_loop(self):
        """
        🧹 CLEAN UP EXPIRED CACHE ENTRIES
        
        Remove old cached metrics to prevent memory leaks.
        """
        while not self.shutdown_event.is_set():
            try:
                now = datetime.now()
                expired_keys = [
                    key for key, expiry in self.cache_expiry.items()
                    if now >= expiry
                ]
                
                for key in expired_keys:
                    self.metrics_cache.pop(key, None)
                    self.cache_expiry.pop(key, None)
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")
                await asyncio.sleep(600)  # Wait longer after error
    
    async def create_dashboard(self, dashboard_id: str, title: str, description: Optional[str] = None,
                             owner: Optional[str] = None) -> Dashboard:
        """
        🎨 CREATE A NEW CUSTOM DASHBOARD
        
        Create a new dashboard with the specified configuration.
        Like creating a new bulletin board with a specific theme.
        """
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            title=title,
            description=description,
            owner=owner
        )
        
        self.dashboards[dashboard_id] = dashboard
        logger.info(f"Created new dashboard: {dashboard_id}")
        
        return dashboard
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """📋 Get a dashboard by ID."""
        return self.dashboards.get(dashboard_id)
    
    def list_dashboards(self) -> List[Dashboard]:
        """📋 Get all available dashboards."""
        return list(self.dashboards.values())
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """🗑️ Delete a dashboard."""
        if dashboard_id in self.dashboards:
            dashboard = self.dashboards.pop(dashboard_id)
            logger.info(f"Deleted dashboard: {dashboard_id}")
            return True
        return False
    
    async def create_default_charts(self, dashboard: Dashboard):
        """
        📊 CREATE DEFAULT CHARTS FOR A DASHBOARD
        
        Add a standard set of useful charts to a dashboard.
        Like setting up a standard monitoring station with
        all the essential displays.
        """
        # Error Count Gauge
        error_count_chart = ChartData(
            chart_id=f"{dashboard.dashboard_id}_error_count",
            chart_type=ChartType.GAUGE,
            title="Total Error Count",
            description="Total number of errors in the system"
        )
        await self._update_error_count_chart(error_count_chart)
        dashboard.add_chart(error_count_chart)
        
        # Severity Distribution Pie Chart
        severity_chart = ChartData(
            chart_id=f"{dashboard.dashboard_id}_severity_dist",
            chart_type=ChartType.PIE,
            title="Errors by Severity",
            description="Breakdown of errors by severity level"
        )
        await self._update_severity_chart(severity_chart)
        dashboard.add_chart(severity_chart)
        
        # Language Distribution Bar Chart
        language_chart = ChartData(
            chart_id=f"{dashboard.dashboard_id}_language_dist",
            chart_type=ChartType.BAR,
            title="Errors by Programming Language",
            description="Distribution of errors across programming languages"
        )
        await self._update_language_chart(language_chart)
        dashboard.add_chart(language_chart)
        
        # 24-Hour Timeline
        timeline_chart = ChartData(
            chart_id=f"{dashboard.dashboard_id}_timeline_24h",
            chart_type=ChartType.LINE,
            title="Error Timeline (24 Hours)",
            description="Error count over the last 24 hours"
        )
        await self._update_timeline_chart(timeline_chart)
        dashboard.add_chart(timeline_chart)
        
        logger.info(f"Added {len(dashboard.charts)} default charts to dashboard {dashboard.dashboard_id}")
    
    async def shutdown(self):
        """
        🔒 SHUTDOWN DASHBOARD SYSTEM
        
        Gracefully shut down all background processes.
        """
        logger.info("Starting dashboard engine shutdown...")
        
        self.shutdown_event.set()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("Dashboard engine shutdown complete")


# Global dashboard engine instance
dashboard_engine: Optional[DashboardEngine] = None


def get_dashboard_engine() -> Optional[DashboardEngine]:
    """
    📊 GET THE GLOBAL DASHBOARD ENGINE
    
    Get access to the main dashboard engine from anywhere in the application.
    """
    return dashboard_engine


def initialize_dashboard_engine(database_manager: DatabaseManager) -> DashboardEngine:
    """
    📊 INITIALIZE THE GLOBAL DASHBOARD SYSTEM
    
    Set up the main dashboard engine that will manage all
    visual analytics and reporting throughout the application.
    """
    global dashboard_engine
    if dashboard_engine is None:
        dashboard_engine = DashboardEngine(database_manager)
        logger.info("Global dashboard engine initialized")
    return dashboard_engine