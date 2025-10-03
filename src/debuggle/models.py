"""
🏗️ DEBUGGLE DATA BLUEPRINTS - The Architectural Plans! 🏗️

Think of this file as the "blueprint library" for a construction company!
Just like architects need detailed plans before building a house, programmers
need detailed "data models" before building software features.

🎯 WHAT THIS MODULE DOES:
This file defines all the "data shapes" that Debuggle uses - like templates
that tell us exactly what information we expect and how it should be organized.

🏠 THE BLUEPRINT ANALOGY:
- LanguageEnum: Like a list of approved building materials ("wood", "brick", "steel")
- AnalyzeRequest: Like a work order form ("I want a house with 3 bedrooms, 2 baths")
- AnalyzeResponse: Like the completion report ("Here's your finished house with details")
- Metadata models: Like the inspector's report ("took 5 days, used 1000 bricks")

🔍 HOW DATA MODELS WORK:
1. Define exactly what data we expect (like a form with required fields)
2. Validate that incoming data matches our expectations (like checking ID at a club)
3. Provide helpful error messages when data doesn't match (like a GPS recalculating)
4. Document what each field means (like labels on a circuit breaker box)

Real-world analogy: This is like having standardized forms at a doctor's office -
everyone fills out the same patient information form so the system works smoothly!
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum

# Define LogSeverity here to avoid circular imports
class LogSeverity(str, Enum):
    """
    🌡️ LOG SEVERITY LEVELS - How Serious Is This Message?
    
    Just like a thermometer shows temperature, these levels show how
    serious a log message is. This helps prioritize which problems
    need immediate attention versus which are just informational.
    """
    TRACE = "trace"      # 🔍 Detailed debugging info
    DEBUG = "debug"      # 🐛 Developer debugging messages  
    INFO = "info"        # ℹ️ General information
    WARNING = "warning"  # ⚠️ Something might be wrong
    ERROR = "error"      # ❌ Something definitely went wrong
    CRITICAL = "critical" # 🚨 System-threatening emergency


class LanguageEnum(str, Enum):
    """
    🗺️ PROGRAMMING LANGUAGE MENU - What Languages Do We Speak?
    
    This is like a restaurant menu that lists all the languages (cuisines) we can handle!
    Just like a restaurant might specialize in Italian, Chinese, and Mexican food,
    Debuggle specializes in different programming languages.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like choosing your foreign language class - you can pick Spanish,
    French, German, etc. Each programming language has its own "grammar rules" and
    common mistakes, just like human languages do.
    
    The "AUTO" option is like having a smart translator who can figure out what
    language you're speaking automatically!
    """
    
    # 🐍 THE SNAKE LANGUAGE - great for beginners, data science, and AI
    PYTHON = "python"
    
    # 🌐 THE WEB LANGUAGE - powers websites and interactive features
    JAVASCRIPT = "javascript"
    
    # ☕ THE ENTERPRISE LANGUAGE - used in big business applications
    JAVA = "java"
    
    # 🏢 THE MICROSOFT LANGUAGE - popular for Windows applications
    CSHARP = "csharp"
    
    # ⚡ THE SPEED DEMON - when you need maximum performance
    CPP = "cpp"
    
    # 🚀 THE GOOGLE LANGUAGE - simple and efficient for servers
    GO = "go"
    
    # 🦀 THE SAFE LANGUAGE - prevents many common programming mistakes
    RUST = "rust"
    
    # 🤖 THE SMART DETECTIVE - "figure it out yourself!" option
    AUTO = "auto"


class AnalyzeOptions(BaseModel):
    """
    🎛️ INVESTIGATION CONTROL PANEL - How Deep Should We Dig?
    
    This is like the control panel on a detective's dashboard - it lets you decide
    how thorough you want the investigation to be. Think of it like ordering at
    a restaurant where you can customize your meal!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like choosing options when ordering a pizza:
    - highlight: "Make it colorful and easy to read" (like adding visual toppings)
    - summarize: "Give me the TL;DR version" (like asking for a quick explanation)
    - tags: "Categorize it for me" (like organizing your music by genre)
    - max_lines: "Don't make it too long" (like setting a page limit on an essay)
    """
    
    # 🌈 MAKE IT PRETTY - should we add colors and formatting?
    # Like asking "do you want syntax highlighting in your code editor?"
    highlight: bool = Field(default=True, description="Apply syntax highlighting")
    
    # 📝 EXECUTIVE SUMMARY - should we write a human readable explanation?
    # Like asking "do you want the CliffsNotes version?"
    summarize: bool = Field(default=True, description="Generate error summary")
    
    # 🏷️ FILING LABELS - should we add category stickers?
    # Like asking "do you want us to organize this with labels?"
    tags: bool = Field(default=True, description="Generate error tags")
    
    # 📏 LENGTH LIMIT - how much text should we process?
    # Like saying "I only have time to read the first 1000 lines"
    # We set reasonable limits: minimum 1 line, maximum 5000 lines
    max_lines: int = Field(default=1000, ge=1, le=5000, description="Maximum lines to process")


class AnalyzeRequest(BaseModel):
    """
    📋 CRIME REPORT INTAKE FORM - Everything We Need to Start Investigating
    
    This is like the form you fill out when reporting a crime to the police!
    It captures all the essential information our detective agency needs to
    start working on your case.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like a doctor's patient intake form:
    - log_input: "What are your symptoms?" (the error message)
    - language: "What language do you speak?" (programming language)
    - options: "How detailed should the examination be?" (analysis preferences)
    
    The form has built-in validation to make sure we get useful information!
    """
    
    # 📄 THE EVIDENCE - the actual error message or log file content
    # This is the "crime scene photo" - we need at least 1 character,
    # but won't process more than 50,000 characters (that's about 20 pages)
    log_input: str = Field(..., min_length=1, max_length=50000, description="Raw log or stack trace")
    
    # 🗣️ LANGUAGE HINT - what programming language is this from?
    # Defaults to AUTO ("figure it out yourself!") if not specified
    language: LanguageEnum = Field(default=LanguageEnum.AUTO, description="Programming language")
    
    # ⚙️ INVESTIGATION PREFERENCES - how thorough should we be?
    # Uses sensible defaults if you don't specify (like a "standard package")
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions, description="Processing options")
    
    @field_validator('log_input')
    @classmethod
    def validate_log_input(cls, v):
        """
        🔍 EVIDENCE QUALITY CHECK - Make Sure We Got Something Useful
        
        This is like a receptionist checking that you actually wrote something
        on the form before passing it to the detective. We can't investigate
        an empty crime report!
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like a teacher checking that you didn't turn in a blank homework paper -
        we need actual content to work with, not just empty spaces!
        """
        if not v.strip():  # If it's just whitespace or empty
            raise ValueError('log_input cannot be empty or whitespace only')
        return v


class AnalyzeMetadata(BaseModel):
    """
    📊 INVESTIGATION STATISTICS - Behind-the-Scenes Details
    
    This is like the "investigation report footnotes" that tell you interesting
    details about how the analysis was performed. Think of it like the nutrition
    facts label on food - technical details for those who want to know!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the stats at the end of a video game level:
    - lines: "You processed 247 lines of code!" (like enemies defeated)
    - language_detected: "This was Python code!" (like the level theme)
    - processing_time_ms: "Analysis took 150 milliseconds!" (like completion time)
    - truncated: "Had to cut off some text due to size" (like reaching time limit)
    """
    
    # 📏 HOW MUCH TEXT - how many lines did we actually look at?
    # Like counting pages in a book you just read
    lines: int = Field(..., description="Number of lines processed")
    
    # 🔍 LANGUAGE DETECTION RESULT - what programming language was this?
    # Like a detective saying "after investigation, this is definitely Spanish"
    language_detected: str = Field(..., description="Detected or specified language")
    
    # ⏱️ SPEED MEASUREMENT - how fast was our analysis?
    # Measured in milliseconds (1000 milliseconds = 1 second)
    # Like timing how long it takes to solve a math problem
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    
    # ✂️ DID WE HAVE TO CUT IT SHORT? - was the input too long?
    # Like having to summarize a 500-page book because you only had time for 100 pages
    truncated: bool = Field(default=False, description="Whether input was truncated")


class AnalyzeResponse(BaseModel):
    """
    📋 COMPLETE INVESTIGATION REPORT - Here's What We Found!
    
    This is like the final police report that gets delivered to you after the
    investigation is complete. It contains everything: the cleaned-up evidence,
    a summary of what happened, category labels, and technical details.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like getting your graded essay back from the teacher:
    - cleaned_log: Your essay with corrections and highlighting (the improved version)
    - summary: Teacher's comment at the top ("Good work on thesis, watch grammar")
    - tags: Categories like "A+ Work", "Needs Grammar Help", "Creative Writing"
    - metadata: Details like "Graded in 10 minutes, 3 pages, marked as English essay"
    """
    
    # 🎨 THE MASTERPIECE - your error message, but cleaned up and prettified
    # Like getting your photo back from a professional photo editor
    cleaned_log: str = Field(..., description="Analyzed and formatted log")
    
    # 📖 PLAIN ENGLISH EXPLANATION - what happened in human terms?
    # Like having a translator explain a foreign movie to you
    # This might be None if we couldn't figure out what the error was
    summary: Optional[str] = Field(None, description="Plain English error explanation")
    
    # 🏷️ CATEGORY STICKERS - quick labels to organize this error
    # Like hashtags on social media posts: #PythonError #Beginner #FixableInMinutes
    tags: List[str] = Field(default_factory=list, description="Error category tags")
    
    # 📊 THE TECHNICAL DETAILS - stats about how the analysis was performed
    # Like the "behind the scenes" extras on a DVD
    metadata: AnalyzeMetadata = Field(..., description="Processing metadata")


class HealthResponse(BaseModel):
    """
    🏥 SYSTEM HEALTH CHECKUP - Is Everything Working OK?
    
    This is like a quick health checkup for our service - a simple way to ask
    "Are you alive and working properly?" It's like taking your pulse or
    checking if a website is online.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like asking a friend "How are you doing?" and getting back:
    - status: "I'm doing great!" or "I'm feeling sick"
    - service: "This is John speaking" (who is responding)
    - version: "I'm John v2.5" (which version of the system is running)
    """
    
    # 💚 HEALTH STATUS - are we healthy, sick, or somewhere in between?
    # Like "OK", "WARNING", or "ERROR" traffic light colors
    status: str = Field(..., description="Service status")
    
    # 🏷️ WHO'S TALKING - which service is responding to this health check?
    # Like caller ID showing you who's calling
    service: str = Field(..., description="Service name")
    
    # 🔢 VERSION NUMBER - what version of the software is running?
    # Like asking "What iOS version are you running?" on your phone
    version: str = Field(..., description="Service version")


class TierFeature(BaseModel):
    """
    🏆 SERVICE LEVEL DESCRIPTION - What Do You Get at Each Level?
    
    This describes one "tier" or level of service we offer. Think of it like
    different membership levels at a gym: Basic, Premium, and VIP each come
    with different features and benefits.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like describing different Netflix subscription plans:
    - name: "Premium Plan" (what it's called)
    - icon: "👑" (a visual symbol for this tier)
    - features: ["4K Video", "Multiple Screens", "Downloads"] (what you get)
    """
    
    # 🎭 TIER NAME - what do we call this service level?
    # Like "Basic", "Pro", "Enterprise", or "Student Plan"
    name: str = Field(..., description="Tier name")
    
    # 🎨 VISUAL SYMBOL - what icon represents this tier?
    # Like emoji or symbols to make it visually recognizable
    icon: str = Field(..., description="Tier icon")
    
    # 📋 WHAT YOU GET - list of features included at this level
    # Like a bullet-point list of benefits
    features: List[str] = Field(..., description="Available features")


class TiersResponse(BaseModel):
    """
    📊 COMPLETE PRICING MENU - All Available Service Levels
    
    This is like a complete menu at a restaurant showing all the different
    meal deals available. Each tier is like a different combo meal with
    different features and prices.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a phone plan comparison chart that shows Basic, Standard, and Premium
    plans side by side, so you can pick which one fits your needs and budget.
    """
    
    # 📋 ALL THE OPTIONS - complete list of available service tiers
    # Like an array of different membership levels you can choose from
    tiers: List[TierFeature] = Field(..., description="Available service tiers")


class FileUploadMetadata(BaseModel):
    """
    📁 FILE PROCESSING RECEIPT - Details About Your Uploaded File
    
    This is like a receipt you get when dropping off film for development
    at a photo lab. It tells you exactly what file you submitted and how
    the processing went.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like the details you see when uploading a video to YouTube:
    - filename: "my_vacation_video.mp4" (what you called your file)
    - file_size: "25.3 MB" (how big the file was)
    - lines: "1,247 lines processed" (how much content we analyzed)
    - language_detected: "Python" (what type of content it was)
    - processing_time_ms: "1,500ms" (how long it took to process)
    - truncated: "Had to cut it short due to size" (if we couldn't process it all)
    """
    
    # 🏷️ ORIGINAL NAME - what did you call this file?
    # Like the original title of a document you uploaded
    filename: str = Field(..., description="Original filename")
    
    # 📏 FILE SIZE - how big was your file?
    # Measured in bytes (1,024 bytes = 1 KB, 1,024 KB = 1 MB)
    file_size: int = Field(..., description="File size in bytes")
    
    # 📊 CONTENT VOLUME - how many lines of text did we process?
    # Like counting pages in a book you submitted for review
    lines: int = Field(..., description="Number of lines processed")
    
    # 🔍 CONTENT TYPE - what programming language was this?
    # Like identifying a document as "English essay" vs "Spanish poem"
    language_detected: str = Field(..., description="Detected or specified language")
    
    # ⏱️ PROCESSING TIME - how long did it take to analyze?
    # In milliseconds (1000ms = 1 second)
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    
    # ✂️ WAS IT TOO BIG? - did we have to cut off part of the file?
    # Like when you have to summarize a book because it's too long to read fully
    truncated: bool = Field(default=False, description="Whether input was truncated")


class FileUploadResponse(BaseModel):
    """
    📦 FILE ANALYSIS DELIVERY - Your Processed File is Ready!
    
    This is like getting your developed photos back from the photo lab,
    but instead of photos, you're getting back your analyzed and cleaned-up
    error logs with explanations and insights.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like getting your graded project back from the teacher,
    complete with corrections, feedback, category grades, and processing notes.
    """
    
    # 🎨 YOUR FILE, BUT BETTER - cleaned up and formatted nicely
    # Like getting your essay back with proper formatting and highlighting
    cleaned_log: str = Field(..., description="Analyzed and formatted log")
    
    # 📖 TEACHER'S EXPLANATION - what the errors mean in plain English
    # Might be None if the errors were too complex to explain simply
    summary: Optional[str] = Field(None, description="Plain English error explanation")
    
    # 🏷️ CATEGORY LABELS - quick tags to classify your file's contents
    # Like subject tags: "Math", "Science", "Easy Fix", "Needs Attention"
    tags: List[str] = Field(default_factory=list, description="Error category tags")
    
    # 📊 PROCESSING RECEIPT - technical details about how we handled your file
    # Like the metadata about when and how your file was processed
    metadata: FileUploadMetadata = Field(..., description="File processing metadata")


class ErrorResponse(BaseModel):
    """
    🚨 OOPS REPORT - When Something Goes Wrong With Our Service
    
    This is like an error message you see when a website crashes or when
    your phone app stops working. It tells you what went wrong and
    (hopefully) how to fix it.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like getting an error message when your computer won't start:
    - error: "Could not connect to internet" (main problem description)
    - details: "WiFi password might be wrong, or router is offline" (more info)
    - code: "ERROR_WIFI_001" (technical error code for support)
    """
    
    # 🚨 MAIN PROBLEM - what went wrong in simple terms?
    # Like the headline of a news article - the key issue in one sentence
    error: str = Field(..., description="Error message")
    
    # 📝 MORE DETAILS - additional explanation if available
    # Like the article body that explains the headline in more depth
    # This might be None if we don't have extra details
    details: Optional[str] = Field(None, description="Detailed error information")
    
    # 🔢 TECHNICAL CODE - error code for debugging and support
    # Like error codes on blue screens or appliance displays
    # This might be None if we don't have a specific code
    code: Optional[str] = Field(None, description="Error code")


# 📊 STORAGE AND SEARCH MODELS - New Persistent Storage Features
# ============================================================

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
    
    # 🎯 WHAT TO DO WHEN TIME IS UP
    action: str = Field(..., description="Action: delete, archive, export, or mark_archived")
    
    # 🎛️ FILTERING - which logs does this policy apply to?
    severity_filter: Optional[List[str]] = Field(None, description="Apply only to these severities")
    language_filter: Optional[List[str]] = Field(None, description="Apply only to these languages")
    tag_filter: Optional[List[str]] = Field(None, description="Apply only to logs with these tags")
    project_filter: Optional[List[str]] = Field(None, description="Apply only to these projects")
    
    # ⚙️ POLICY SETTINGS
    enabled: bool = Field(True, description="Is this policy active?")
    archive_path: Optional[str] = Field(None, description="Path for archived/exported files")


class RetentionPolicyResponse(BaseModel):
    """
    📋 RETENTION POLICY CONFIRMATION - Policy Created Successfully!
    
    This confirms that your data retention policy was set up correctly
    and provides details about how it will work.
    """
    
    # ✅ CONFIRMATION
    message: str = Field(..., description="Policy creation confirmation")
    
    # 📋 POLICY DETAILS
    policy_info: Dict[str, Any] = Field(..., description="Details about the created policy")
    
    # 📊 CURRENT STATUS
    total_policies: int = Field(..., description="Total number of active retention policies")


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


# ===================================================================================
# 🚨 ALERT SYSTEM MODELS - Proactive Notification Blueprints! 🚨
# ===================================================================================

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


# ===================================================================================
# 🚀 SCALABLE INGESTION MODELS - Enterprise Processing Blueprints! 🚀
# ===================================================================================

class IngestionSourceAPI(str, Enum):
    """
    📡 DATA SOURCE TYPES - Where Are These Logs Coming From?
    
    Different sources need different handling approaches, like how
    a hospital has different intake procedures for different types
    of patient arrivals.
    """
    FILE_UPLOAD = "file_upload"         # 📁 Traditional file uploads
    STREAMING = "streaming"             # 🌊 Real-time log streams
    BATCH_UPLOAD = "batch_upload"       # 📦 Large file processing
    WEBHOOK = "webhook"                 # 🔗 External system pushes
    API_DIRECT = "api_direct"           # 💻 Direct API calls
    WEBSOCKET = "websocket"             # ⚡ WebSocket connections


class ProcessingPriorityAPI(str, Enum):
    """
    🚨 PROCESSING URGENCY LEVELS - Hospital Triage System!
    
    Just like a hospital emergency room, we prioritize processing
    based on urgency. Critical system errors get immediate attention
    while routine logs can wait in the regular queue.
    """
    CRITICAL = "critical"       # 🔴 Emergency - process immediately
    HIGH = "high"              # 🟠 Urgent - high priority queue
    NORMAL = "normal"          # 🟡 Standard - regular processing
    LOW = "low"                # 🟢 Background - when system is idle
    BATCH = "batch"            # 📦 Bulk - special batch processing


class IngestionStatusAPI(str, Enum):
    """
    📊 PROCESSING STATUS TRACKING - Where Is My Request?
    
    Like a package tracking system, this shows exactly where
    your log processing request is in the pipeline.
    """
    QUEUED = "queued"               # ⏳ Waiting in line for processing
    PROCESSING = "processing"       # ⚙️ Currently being processed
    COMPLETED = "completed"         # ✅ Successfully processed
    FAILED = "failed"              # ❌ Processing failed
    PARTIALLY_FAILED = "partial"    # ⚠️ Some parts failed
    CANCELLED = "cancelled"         # 🚫 Request was cancelled


class BatchIngestionRequest(BaseModel):
    """
    📦 BATCH PROCESSING REQUEST - Submit Large File for Processing
    
    This is like submitting a large batch order to a factory.
    Instead of processing one item at a time, the system will
    efficiently handle the entire batch using specialized processing.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like submitting a bulk order at a printing shop:
    - You give them a huge file with thousands of pages
    - They use special equipment designed for bulk processing
    - They process it efficiently in the background
    - You get updates on progress until it's complete
    """
    
    # 📝 PROCESSING CONFIGURATION
    priority: ProcessingPriorityAPI = Field(ProcessingPriorityAPI.BATCH, description="Processing priority level")
    language: Optional[str] = Field(None, description="Programming language hint for processing")
    project_name: Optional[str] = Field(None, description="Project name for organization")
    
    # 🏷️ METADATA
    description: Optional[str] = Field(None, description="Human-readable description of this batch")
    tags: List[str] = Field(default_factory=list, description="Tags to apply to all logs in batch")
    
    # ⚙️ PROCESSING OPTIONS
    chunk_size: int = Field(1000, description="Number of log entries to process per chunk")
    enable_streaming_updates: bool = Field(True, description="Send progress updates via WebSocket")
    notification_webhook: Optional[str] = Field(None, description="Webhook URL for completion notification")


class StreamingIngestionRequest(BaseModel):
    """
    🌊 STREAMING PROCESSING REQUEST - Set Up Real-Time Log Processing
    
    This sets up a continuous stream for processing logs as they arrive.
    Like setting up a conveyor belt that processes items as they're
    placed on it, rather than waiting for a complete batch.
    """
    
    # 🎯 STREAM CONFIGURATION
    stream_id: str = Field(..., description="Unique identifier for this stream")
    priority: ProcessingPriorityAPI = Field(ProcessingPriorityAPI.NORMAL, description="Processing priority")
    
    # 📊 BUFFER SETTINGS
    buffer_size_lines: int = Field(1000, description="Lines to buffer before processing")
    buffer_size_bytes: int = Field(64 * 1024, description="Bytes to buffer before processing")
    flush_interval_seconds: float = Field(5.0, description="Max seconds before auto-flush")
    
    # 🏷️ METADATA
    project_name: Optional[str] = Field(None, description="Project name for organization")
    language: Optional[str] = Field(None, description="Programming language hint")
    
    # 🔗 INTEGRATION OPTIONS
    webhook_url: Optional[str] = Field(None, description="Webhook for processed log notifications")
    enable_alerts: bool = Field(True, description="Enable alert evaluation for streamed logs")


class IngestionJobResponse(BaseModel):
    """
    📋 PROCESSING JOB STATUS - Complete Job Information
    
    This provides complete information about a processing job,
    including its current status, progress, and results. Like
    a detailed order status report from a factory.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like tracking a pizza delivery order:
    - job_id: "Order #12345" (tracking number)
    - status: "In oven" vs "Out for delivery" (current stage)
    - progress_percent: "75% complete" (how far along)
    - created_at: "Ordered at 7:30 PM" (when you placed the order)
    - processing_time: "15 minutes so far" (how long it's taking)
    """
    
    # 🏷️ JOB IDENTIFICATION
    job_id: str = Field(..., description="Unique job identifier")
    source: IngestionSourceAPI = Field(..., description="Where this job came from")
    priority: ProcessingPriorityAPI = Field(..., description="Processing priority level")
    
    # 📊 STATUS AND PROGRESS
    status: IngestionStatusAPI = Field(..., description="Current processing status")
    progress_percent: float = Field(..., description="Completion percentage (0-100)")
    created_at: str = Field(..., description="When job was created")
    started_at: Optional[str] = Field(None, description="When processing started")
    completed_at: Optional[str] = Field(None, description="When processing finished")
    
    # 📈 PROCESSING METRICS
    bytes_processed: int = Field(..., description="Total bytes processed")
    lines_processed: int = Field(..., description="Total lines processed")
    processing_time_seconds: float = Field(..., description="Time taken to process")
    
    # 📝 RESULTS AND ERRORS
    processed_logs: List[str] = Field(..., description="Successfully processed log IDs")
    failed_logs: List[str] = Field(..., description="Failed log processing attempts")
    error_messages: List[str] = Field(..., description="Any error messages")
    
    # 📊 ADDITIONAL METADATA
    metadata: Dict[str, Any] = Field(..., description="Additional job information")


class IngestionStatsResponse(BaseModel):
    """
    📊 INGESTION SYSTEM STATISTICS - Performance Dashboard
    
    This provides comprehensive statistics about the ingestion system's
    performance and current status. Like a factory's production
    dashboard showing all the key performance metrics.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a restaurant's daily performance report:
    - jobs_completed: "Served 150 customers today"
    - average_processing_time: "Average order time: 12 minutes"
    - active_jobs: "Currently preparing 8 orders"
    - memory_usage: "Kitchen using 75% of capacity"
    - queue_sizes: "5 orders waiting in each priority level"
    """
    
    # 📊 JOB STATISTICS
    jobs_created: int = Field(..., description="Total jobs created")
    jobs_completed: int = Field(..., description="Total jobs completed successfully")
    jobs_failed: int = Field(..., description="Total jobs that failed")
    active_jobs: int = Field(..., description="Currently processing jobs")
    queued_jobs: int = Field(..., description="Jobs waiting to be processed")
    total_jobs: int = Field(..., description="Total jobs in system")
    
    # 📈 PERFORMANCE METRICS
    bytes_processed: int = Field(..., description="Total bytes processed")
    lines_processed: int = Field(..., description="Total lines processed")
    average_processing_time: float = Field(..., description="Average job processing time in seconds")
    
    # 💾 SYSTEM RESOURCES
    memory_usage_mb: float = Field(..., description="Current memory usage in megabytes")
    active_connections: int = Field(..., description="Active WebSocket connections")
    
    # 📋 QUEUE STATUS
    queue_sizes: Dict[str, int] = Field(..., description="Number of jobs in each priority queue")


class StreamDataRequest(BaseModel):
    """
    🌊 STREAMING DATA SUBMISSION - Send Data to Active Stream
    
    This is used to send log data to an active streaming processing
    session. Like adding items to a conveyor belt that's already running.
    """
    
    stream_id: str = Field(..., description="ID of the target stream")
    log_data: str = Field(..., description="Log data to process")
    timestamp: Optional[str] = Field(None, description="Timestamp of the log data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BulkUploadRequest(BaseModel):
    """
    📦 BULK FILE UPLOAD REQUEST - Enterprise-Scale File Processing
    
    This handles very large file uploads that need special processing
    to avoid memory issues and provide efficient handling. Like having
    a specialized loading dock for huge deliveries.
    """
    
    # 📁 FILE INFORMATION
    expected_size_bytes: Optional[int] = Field(None, description="Expected file size for progress tracking")
    content_type: Optional[str] = Field(None, description="MIME type of the uploaded content")
    
    # ⚙️ PROCESSING CONFIGURATION
    priority: ProcessingPriorityAPI = Field(ProcessingPriorityAPI.BATCH, description="Processing priority")
    chunk_size: int = Field(64 * 1024, description="Chunk size for processing (bytes)")
    enable_progress_updates: bool = Field(True, description="Send real-time progress updates")
    
    # 🏷️ METADATA
    project_name: Optional[str] = Field(None, description="Project name for organization")
    language: Optional[str] = Field(None, description="Programming language hint")
    description: Optional[str] = Field(None, description="Description of the uploaded content")
    tags: List[str] = Field(default_factory=list, description="Tags to apply to processed logs")


# ===================================================================================
# 📊 RICH DASHBOARD MODELS - Visual Analytics Blueprints! 📊
# ===================================================================================

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
    
    # 🌡️ SEVERITY BREAKDOWN
    critical_errors: int = Field(..., description="Number of critical errors")
    error_errors: int = Field(..., description="Number of error-level messages")
    warning_errors: int = Field(..., description="Number of warnings")
    info_messages: int = Field(..., description="Number of info messages")
    
    # 💻 LANGUAGE DISTRIBUTION
    top_languages: List[Dict[str, Any]] = Field(..., description="Most common programming languages")
    
    # 🔝 TOP ERROR TYPES
    top_error_types: List[Dict[str, Any]] = Field(..., description="Most frequent error types")
    
    # 📈 TRENDS
    hourly_trend: List[int] = Field(..., description="Error counts for last 24 hours")
    daily_trend: List[int] = Field(..., description="Error counts for last 7 days")
    
    # 💾 SYSTEM HEALTH
    database_size_mb: float = Field(..., description="Database size in megabytes")
    total_log_entries: int = Field(..., description="Total log entries stored")
    oldest_log_date: Optional[str] = Field(None, description="Date of oldest log")
    newest_log_date: Optional[str] = Field(None, description="Date of newest log")
    
    # ⏰ METADATA
    last_updated: str = Field(..., description="When metrics were last calculated")