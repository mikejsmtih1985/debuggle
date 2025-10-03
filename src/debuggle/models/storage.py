"""
💾 Hospital Medical Records Department - Models for Log Storage & Search

This is the medical records and search department of our hospital! Just like how a 
real hospital maintains comprehensive patient records, search systems, and data retention
policies, we maintain sophisticated storage and search capabilities for code diagnostics.

Think of this like the hospital's medical records system:
- SearchRequest: Looking up patient records with specific criteria
- LogStorageRequest: Filing new medical reports in permanent records
- RetentionPolicyRequest: Setting policies for how long to keep different types of records

🏆 HIGH SCHOOL EXPLANATION:
Like a school's student records system:
1. Search: Find student files matching specific criteria (grades, subjects, dates)
2. Storage: File new test results and reports in permanent records
3. Retention: Decide how long to keep different types of student records
4. Organization: Keep everything organized so it can be found quickly later
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """
    🔍 ADVANCED SEARCH FORM - Find Exactly What You're Looking For!
    
    This is like a sophisticated library search form that lets you combine
    multiple search criteria to find exactly the logs you need. Think of it
    like an advanced Google search where you can specify dates, file types,
    exact phrases, etc.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like using the advanced search on a school's online library:
    - text: "Find books containing these words"
    - date_range: "Published between 2020-2023"
    - categories: "Only science books"
    - exact_phrase: "Must contain this exact quote"
    - sort_by: "Show newest first"
    """
    
    # 🔍 MAIN SEARCH TEXT - what are you looking for?
    text: Optional[str] = Field(None, description="Search text (searches content, summary, tags)")
    
    # 📝 EXACT PHRASE - must contain this exact phrase
    exact_phrase: Optional[str] = Field(None, description="Exact phrase that must appear")
    
    # 📅 TIME FILTERS
    start_date: Optional[str] = Field(None, description="Earliest date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Latest date (YYYY-MM-DD)")
    last_n_days: Optional[int] = Field(None, ge=1, le=365, description="Only last N days")
    
    # 🏷️ CATEGORY FILTERS
    severities: Optional[List[str]] = Field(None, description="Filter by error severity")
    languages: Optional[List[str]] = Field(None, description="Filter by programming language")
    tags: Optional[List[str]] = Field(None, description="Filter by error tags")
    projects: Optional[List[str]] = Field(None, description="Filter by project name")
    
    # 📊 RESULT CONTROL
    sort_by: Optional[str] = Field("newest_first", description="Sort order")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Results to skip (for pagination)")


class SearchResponse(BaseModel):
    """
    📋 SEARCH RESULTS PACKAGE - Here's What We Found!
    
    This is like getting back a research report from a librarian who found
    exactly what you were looking for, along with helpful context and
    suggestions for related searches.
    """
    
    # 📚 THE ACTUAL RESULTS - logs that matched your search
    results: List[Dict[str, Any]] = Field(..., description="Found log entries")
    
    # 📊 SEARCH STATISTICS
    total_matches: int = Field(..., description="Total number of matching logs")
    search_duration_ms: int = Field(..., description="Search execution time")
    
    # 💡 HELPFUL SUGGESTIONS
    suggested_filters: Optional[Dict[str, List[str]]] = Field(None, description="Suggested filter refinements")
    related_tags: Optional[List[str]] = Field(None, description="Related error tags found")
    
    # 🎯 SEARCH QUALITY INFO
    query_info: Optional[str] = Field(None, description="Information about the executed query")


class LogStorageRequest(BaseModel):
    """
    💾 STORAGE REQUEST - Save This Log for Later!
    
    This is like asking a librarian to file a document in the permanent
    collection so you can find it again later. We store the original
    analysis plus additional metadata.
    """
    
    # 📄 ORIGINAL LOG DATA
    log_input: str = Field(..., description="Original log content")
    processed_log: str = Field(..., description="Cleaned/formatted log")
    summary: Optional[str] = Field(None, description="Error summary")
    tags: List[str] = Field(default_factory=list, description="Error tags")
    
    # 🏷️ CLASSIFICATION DATA
    severity: str = Field(..., description="Log severity level")
    language: str = Field(..., description="Programming language")
    
    # 📁 CONTEXT DATA
    project_name: Optional[str] = Field(None, description="Project name")
    file_path: Optional[str] = Field(None, description="File path where error occurred")
    source: str = Field("api", description="How this log entered the system")
    
    # 📊 TECHNICAL METADATA
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LogStorageResponse(BaseModel):
    """
    📦 STORAGE CONFIRMATION - Your Log Has Been Saved!
    
    This confirms that your log was successfully stored and provides
    the information you need to find it again later.
    """
    
    # 🏷️ UNIQUE IDENTIFIER - your "library card number" for this log
    log_id: str = Field(..., description="Unique identifier for the stored log")
    
    # ✅ CONFIRMATION MESSAGE
    message: str = Field(..., description="Storage confirmation message")
    
    # ⏰ WHEN IT WAS STORED
    stored_at: str = Field(..., description="Timestamp when log was stored")
    
    # 📊 STORAGE STATS
    storage_info: Optional[Dict[str, Any]] = Field(None, description="Storage statistics")


class RetentionPolicyRequest(BaseModel):
    """
    📅 RETENTION POLICY SETUP - How Long Should We Keep Logs?
    
    This is like setting up filing policies for a office - how long to keep
    different types of documents before archiving or disposing of them.
    """
    
    # 🏷️ POLICY IDENTIFICATION
    policy_name: str = Field(..., description="Name for this retention policy")
    description: str = Field(..., description="Description of what this policy does")
    
    # ⏰ TIME SETTINGS
    days_to_keep: int = Field(..., ge=1, le=3650, description="Days to keep logs (1-3650)")
    
    # 🎯 WHAT LOGS DOES THIS APPLY TO?
    severity_filter: Optional[List[str]] = Field(None, description="Apply to specific severity levels")
    language_filter: Optional[List[str]] = Field(None, description="Apply to specific programming languages")
    project_filter: Optional[List[str]] = Field(None, description="Apply to specific projects")
    tag_filter: Optional[List[str]] = Field(None, description="Apply to logs with specific tags")
    
    # ⚙️ POLICY SETTINGS 
    enabled: bool = Field(True, description="Whether this policy is active")
    priority: int = Field(0, description="Policy priority (higher numbers take precedence)")


class RetentionPolicyResponse(BaseModel):
    """
    📋 RETENTION POLICY DETAILS - Complete Policy Information
    
    This provides complete information about a data retention policy,
    including when it was created, how many logs it affects, and
    its current status.
    """
    
    # 🏷️ POLICY IDENTIFICATION
    policy_id: str = Field(..., description="Unique policy identifier")
    policy_name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    enabled: bool = Field(..., description="Whether policy is active")
    
    # ⏰ TIME SETTINGS
    days_to_keep: int = Field(..., description="Days to retain matching logs")
    created_at: str = Field(..., description="When policy was created")
    last_applied: Optional[str] = Field(None, description="When policy was last applied")
    
    # 🎯 FILTER SETTINGS
    severity_filter: Optional[List[str]] = Field(None, description="Severity level filters")
    language_filter: Optional[List[str]] = Field(None, description="Programming language filters")
    project_filter: Optional[List[str]] = Field(None, description="Project name filters")
    tag_filter: Optional[List[str]] = Field(None, description="Tag filters")
    
    # 📊 POLICY STATISTICS
    affected_logs_count: int = Field(..., description="Number of logs this policy applies to")
    priority: int = Field(..., description="Policy priority level")
    
    # 🔄 EXECUTION HISTORY
    execution_history: List[Dict[str, Any]] = Field(default_factory=list, description="Recent policy executions")


class LogAnalyticsResponse(BaseModel):
    """
    📊 LOG ANALYTICS DASHBOARD - The Big Picture View!
    
    This is like a monthly report from a library showing usage patterns,
    popular books, busiest times, and trends over time. But instead of
    books, we're analyzing error log patterns.
    """
    
    # 📈 BASIC STATISTICS
    total_logs: int = Field(..., description="Total logs in database")
    logs_today: int = Field(..., description="Logs processed today")
    logs_this_week: int = Field(..., description="Logs processed this week")
    logs_this_month: int = Field(..., description="Logs processed this month")
    
    # 🏆 TOP CATEGORIES
    top_error_types: Dict[str, int] = Field(..., description="Most common error types")
    top_languages: Dict[str, int] = Field(..., description="Most common programming languages")
    top_severities: Dict[str, int] = Field(..., description="Most common severity levels")
    
    # 📅 TRENDS
    daily_error_counts: List[int] = Field(..., description="Errors per day for last 7 days")
    hourly_patterns: Dict[str, int] = Field(..., description="Busiest hours of the day")
    
    # 🔍 SEARCH ANALYTICS
    popular_search_terms: List[str] = Field(..., description="Most searched terms")
    search_performance: Dict[str, float] = Field(..., description="Search system performance metrics")
    
    # 📊 SYSTEM HEALTH
    database_size_mb: Optional[float] = Field(None, description="Database size in megabytes")
    oldest_log_date: Optional[str] = Field(None, description="Date of oldest log")
    newest_log_date: Optional[str] = Field(None, description="Date of newest log")