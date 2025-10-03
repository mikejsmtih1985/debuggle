"""
📊 Hospital Dashboard Department - Models for Medical Statistics & Analytics

This is the analytics and dashboard department of our hospital! Just like how a real 
hospital has dashboards showing patient statistics, bed occupancy, and performance metrics,
we have dashboards showing code error patterns, system health, and usage analytics.

Think of this like the hospital's main control center:
- DashboardStatsRequest: Asking for specific time period statistics
- DashboardStatsResponse: Complete analytics report with charts and trends

🏆 HIGH SCHOOL EXPLANATION:
Like asking for a school report card that shows:
1. How many students are in each grade (error counts by type)
2. Which subjects are most challenging (programming languages with errors)  
3. Attendance patterns over time (error trends)
4. Most popular activities (search terms and usage patterns)
"""

from typing import Optional, Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field
from .common import LogSeverity


class DashboardStatsRequest(BaseModel):
    """
    📊 ANALYTICS REQUEST FORM - What Statistics Do You Want to See?
    
    This is like asking the school principal for a custom report about
    student performance. You can specify the time period and what kinds
    of statistics you're most interested in seeing.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like requesting a custom school report:
    - days_back: "Show me the last 30 days" (time period)
    - include_trends: "Show me if things are getting better or worse" (trend analysis)
    - include_search_stats: "Show me what students are researching" (search analytics)
    """
    
    # 📅 TIME PERIOD - how far back should we look?
    # Like asking "show me this semester's grades" vs "show me this week's grades"
    days_back: int = Field(7, ge=1, le=365, description="Number of days to analyze")
    
    # 📈 TREND ANALYSIS - should we show if things are improving or getting worse?
    # Like asking "are test scores trending up or down?"
    include_trends: bool = Field(True, description="Include trend analysis")
    
    # 🔍 SEARCH INSIGHTS - should we show what people are searching for?
    # Like asking "what topics are students researching most?"
    include_search_stats: bool = Field(True, description="Include search analytics")
    
    # 🎯 DETAILED BREAKDOWNS - should we show detailed category breakdowns?
    # Like asking for detailed subject-by-subject grade reports
    include_detailed_breakdowns: bool = Field(True, description="Include detailed category analysis")


class DashboardStatsResponse(BaseModel):
    """
    📋 COMPLETE ANALYTICS REPORT - Here's Your Hospital Performance Dashboard!
    
    This is like getting a comprehensive hospital performance report that shows
    everything from patient volume to most common diagnoses to system efficiency.
    Perfect for executives who need to understand how the hospital is performing.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like a complete school report card that shows:
    - Overall performance numbers (total logs, success rates)
    - Subject-by-subject breakdown (errors by programming language)
    - Time trends (are things getting better or worse?)
    - Popular activities (what are people searching for?)
    - System performance (how fast are we processing requests?)
    """
    
    # 📊 HEADLINE NUMBERS - the big picture statistics
    # Like the summary at the top of a report card
    total_logs: int = Field(..., description="Total log entries in time period")
    unique_errors: int = Field(..., description="Number of unique error types")
    processed_successfully: int = Field(..., description="Successfully processed logs")
    processing_failures: int = Field(..., description="Failed processing attempts")
    
    # 📈 PERFORMANCE METRICS - how efficient is our system?
    # Like grades showing how well the school is operating
    avg_processing_time_ms: float = Field(..., description="Average processing time")
    search_queries_count: int = Field(..., description="Number of search queries performed")
    avg_search_time_ms: float = Field(..., description="Average search response time")
    
    # 🏆 TOP CATEGORIES - what are the most common issues?
    # Like showing which subjects have the most homework or challenges
    top_languages: Dict[str, int] = Field(..., description="Most common programming languages")
    top_severities: Dict[str, int] = Field(..., description="Most common severity levels")
    
    # 📅 TRENDS - are things getting better or worse over time?
    # Like showing if test scores are improving throughout the semester
    daily_error_counts: List[int] = Field(..., description="Errors per day for last 7 days")
    hourly_patterns: Dict[str, int] = Field(..., description="Busiest hours of the day")
    
    # 🔍 SEARCH ANALYTICS - what are people looking for?
    # Like showing what topics students research most in the library
    popular_search_terms: List[str] = Field(..., description="Most searched terms")
    search_performance: Dict[str, float] = Field(..., description="Search system performance metrics")
    
    # 📊 SYSTEM HEALTH - how is our infrastructure performing?
    # Like showing school facility usage and capacity
    database_size_mb: Optional[float] = Field(None, description="Database size in megabytes")
    oldest_log_date: Optional[str] = Field(None, description="Date of oldest log")
    newest_log_date: Optional[str] = Field(None, description="Date of newest log")


class ChartTypeAPI(str, Enum):
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


class TimeRangeAPI(str, Enum):
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


class ChartDataRequest(BaseModel):
    """
    📊 CHART DATA REQUEST - Ask for Specific Chart Data
    
    This is used to request data for a specific chart type and configuration.
    Like asking a data analyst to create a specific type of graph with
    certain parameters and time ranges.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like asking the school statistician:
    "Can you make me a bar chart showing test scores by subject
    for the last semester, broken down by grade level?"
    
    This request specifies exactly what kind of chart you want
    and what data should be included.
    """
    
    # 📊 CHART CONFIGURATION
    chart_type: ChartTypeAPI = Field(..., description="Type of chart to create")
    title: str = Field(..., description="Chart title")
    description: Optional[str] = Field(None, description="Chart description")
    
    # 📅 TIME AND FILTERING
    time_range: TimeRangeAPI = Field(TimeRangeAPI.LAST_DAY, description="Time period to analyze")
    start_date: Optional[str] = Field(None, description="Custom start date (ISO format)")
    end_date: Optional[str] = Field(None, description="Custom end date (ISO format)")
    
    # 🎯 DATA FILTERS
    severity_filter: Optional[List[LogSeverity]] = Field(None, description="Filter by severity levels")
    language_filter: Optional[List[str]] = Field(None, description="Filter by programming languages")
    project_filter: Optional[List[str]] = Field(None, description="Filter by project names")
    tag_filter: Optional[List[str]] = Field(None, description="Filter by tags")
    
    # 🎨 VISUAL CUSTOMIZATION
    color_palette: Optional[str] = Field("default", description="Color palette to use")
    height: Optional[int] = Field(None, description="Chart height in pixels")
    width: Optional[int] = Field(None, description="Chart width in pixels")
    
    # ⚙️ CHART OPTIONS
    max_data_points: int = Field(100, description="Maximum number of data points to include")
    group_small_values: bool = Field(True, description="Group small values into 'Others' category")
    show_percentages: bool = Field(False, description="Show percentages instead of raw counts")


class ChartDataResponse(BaseModel):
    """
    📊 CHART DATA RESPONSE - Complete Chart Information
    
    This contains all the data and configuration needed to render
    a chart on the frontend. Like a complete chart specification
    that includes the data, colors, labels, and display options.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like getting a complete art kit for a specific project:
    - chart_type: "Make a bar chart" (what kind of visual)
    - data: [85, 92, 78, 95] (the actual numbers)
    - labels: ["Math", "Science", "English", "History"] (what each bar represents)
    - colors: ["red", "blue", "green", "yellow"] (how to color each bar)
    - title: "Test Scores by Subject" (what to write at the top)
    """
    
    # 📊 CHART IDENTIFICATION
    chart_id: str = Field(..., description="Unique chart identifier")
    chart_type: ChartTypeAPI = Field(..., description="Type of chart")
    title: str = Field(..., description="Chart title")
    description: Optional[str] = Field(None, description="Chart description")
    
    # 📈 CHART DATA
    data: List[Any] = Field(..., description="Chart data points")
    labels: List[str] = Field(..., description="Data point labels")
    datasets: List[Dict[str, Any]] = Field(default_factory=list, description="Multiple data series")
    
    # 🎨 VISUAL STYLING
    colors: List[str] = Field(default_factory=list, description="Colors for data points")
    background_colors: List[str] = Field(default_factory=list, description="Background colors")
    border_colors: List[str] = Field(default_factory=list, description="Border colors")
    
    # ⚙️ CHART OPTIONS
    options: Dict[str, Any] = Field(default_factory=dict, description="Chart rendering options")
    height: Optional[int] = Field(None, description="Chart height in pixels")
    width: Optional[int] = Field(None, description="Chart width in pixels")
    
    # 📅 METADATA
    time_range: Optional[TimeRangeAPI] = Field(None, description="Time period covered")
    last_updated: str = Field(..., description="When data was last updated")
    data_points_count: int = Field(..., description="Number of data points")
    
    # 🔄 REFRESH SETTINGS
    auto_refresh: bool = Field(True, description="Should this chart auto-update")
    refresh_interval_seconds: int = Field(30, description="Refresh interval in seconds")


class DashboardRequest(BaseModel):
    """
    📋 DASHBOARD CREATION REQUEST - Build a New Dashboard
    
    This is used to create a new custom dashboard with specific
    configuration and layout. Like submitting architectural plans
    for a new building that specifies the layout and features.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like designing a custom bulletin board for your classroom:
    - title: "Science Fair Results" (what to call the board)
    - description: "Display winners and statistics" (what it's for)
    - layout: "Put charts on left, winner photos on right" (how to arrange content)
    - theme: "Use school colors" (visual styling)
    - auto_refresh: "Update every hour" (how often to change content)
    """
    
    # 📋 DASHBOARD IDENTIFICATION
    title: str = Field(..., description="Dashboard display title")
    description: Optional[str] = Field(None, description="Dashboard description")
    
    # 🎨 VISUAL CONFIGURATION
    theme: str = Field("light", description="Color theme (light/dark)")
    layout: Dict[str, Any] = Field(default_factory=dict, description="Grid layout configuration")
    custom_css: Optional[str] = Field(None, description="Custom CSS styling")
    
    # 👤 ACCESS CONTROL
    is_public: bool = Field(True, description="Whether dashboard is publicly viewable")
    allowed_users: List[str] = Field(default_factory=list, description="Specific users who can view")
    
    # 🔄 AUTO-REFRESH SETTINGS
    auto_refresh_enabled: bool = Field(True, description="Enable automatic data refresh")
    refresh_interval_seconds: int = Field(60, description="Refresh interval in seconds")
    
    # 📊 INITIAL CHARTS
    include_default_charts: bool = Field(True, description="Include standard system charts")
    custom_charts: List[ChartDataRequest] = Field(default_factory=list, description="Custom charts to add")


class DashboardResponse(BaseModel):
    """
    📋 DASHBOARD INFORMATION - Complete Dashboard Details
    
    This provides complete information about a dashboard, including
    all its charts, configuration, and metadata. Like a detailed
    report about a bulletin board that lists everything on it.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a detailed inventory of a classroom bulletin board:
    - dashboard_id: "Science_Fair_Board_2024" (unique name)
    - title: "Science Fair Results" (what's written at the top)
    - charts: [winners_chart, scores_chart] (all the displays on the board)
    - created_at: "March 1, 2024" (when it was set up)
    - view_count: "Viewed 150 times" (how popular it is)
    """
    
    # 📋 DASHBOARD IDENTIFICATION
    dashboard_id: str = Field(..., description="Unique dashboard identifier")
    title: str = Field(..., description="Dashboard display title")
    description: Optional[str] = Field(None, description="Dashboard description")
    
    # 📊 DASHBOARD CONTENT
    charts: List[ChartDataResponse] = Field(..., description="All charts in the dashboard")
    widgets: List[Dict[str, Any]] = Field(default_factory=list, description="Non-chart widgets")
    
    # 🎨 VISUAL CONFIGURATION
    layout: Dict[str, Any] = Field(..., description="Grid layout configuration")
    theme: str = Field(..., description="Color theme")
    custom_css: Optional[str] = Field(None, description="Custom CSS styling")
    
    # 👤 ACCESS AND PERMISSIONS
    owner: Optional[str] = Field(None, description="Dashboard owner")
    is_public: bool = Field(..., description="Whether dashboard is publicly viewable")
    allowed_users: List[str] = Field(..., description="Users with access")
    
    # ⏰ METADATA
    created_at: str = Field(..., description="When dashboard was created")
    updated_at: str = Field(..., description="When dashboard was last modified")
    view_count: int = Field(..., description="Number of times viewed")
    
    # 🔄 AUTO-REFRESH SETTINGS
    auto_refresh_enabled: bool = Field(..., description="Whether auto-refresh is enabled")
    refresh_interval_seconds: int = Field(..., description="Refresh interval in seconds")


class DashboardListResponse(BaseModel):
    """
    📋 DASHBOARD LIST - Summary of All Available Dashboards
    
    This provides a list of all available dashboards with summary
    information. Like a directory of all bulletin boards in a school
    that shows what each one is about.
    """
    
    dashboards: List[Dict[str, Any]] = Field(..., description="List of available dashboards")
    total_count: int = Field(..., description="Total number of dashboards")
    public_count: int = Field(..., description="Number of public dashboards")
    private_count: int = Field(..., description="Number of private dashboards")


class SystemMetricsResponse(BaseModel):
    """
    📊 SYSTEM METRICS SUMMARY - Key Performance Indicators
    
    This provides the key metrics and statistics about system
    performance and health. Like a school's report card that
    shows how well everything is performing.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a school's daily performance summary:
    - total_errors: "25 incidents today" (problems that happened)
    - error_rate: "2.3 errors per hour" (how often problems occur)
    - top_error_types: "Most common: login issues" (what goes wrong most)
    - system_health: "95% uptime" (how well everything is working)
    """
    
    # 📊 ERROR STATISTICS
    total_errors: int = Field(..., description="Total errors in system")
    errors_last_24h: int = Field(..., description="Errors in last 24 hours")
    errors_last_hour: int = Field(..., description="Errors in last hour")
    error_rate_per_hour: float = Field(..., description="Average errors per hour")
    
    # 🎯 TOP CATEGORIES
    top_error_types: Dict[str, int] = Field(..., description="Most common error types")
    top_languages: Dict[str, int] = Field(..., description="Most common programming languages")
    top_severities: Dict[str, int] = Field(..., description="Most common severity levels")
    
    # 📈 TRENDS
    daily_error_counts: List[int] = Field(..., description="Errors per day for last 7 days")
    hourly_patterns: Dict[str, int] = Field(..., description="Busiest hours of the day")
    
    # 💾 STORAGE AND PERFORMANCE
    database_size_mb: Optional[float] = Field(None, description="Database size in megabytes")
    processing_queue_size: int = Field(..., description="Number of items in processing queue")
    avg_processing_time_ms: float = Field(..., description="Average processing time")
    
    # 🔍 SEARCH SYSTEM HEALTH
    search_queries_count: int = Field(..., description="Number of search queries performed")
    avg_search_time_ms: float = Field(..., description="Average search response time")
    search_cache_hit_rate: float = Field(..., description="Search cache efficiency percentage")