"""
Debuggle FastAPI Web Server - The Heart of Our Error Analysis Service! 🏥💻

Think of this file as the# Step 4: Create our "chief medical officer" - the main error analysis engine
# This is the core brain that actually analyzes errors and generates insights
processor = LogProcessor()  # Our main diagnostic tool

# Step 5: Initialize persistent storage system - Our digital filing cabinet
# This handles long-term storage, search, and retention of all log data
database_manager = DatabaseManager("logs.db")  # SQLite database for local storage
search_manager = SearchManager(database_manager)  # Full-text search engine
retention_manager = RetentionManager(database_manager)  # Data retention policiesain office" of a hospital where:
- Patients (errors) come in for diagnosis 
- Doctors (our analysis functions) examine them
- Reception (API endpoints) manages the flow
- Medical records (logs) are processed and analyzed
- Emergency broadcast system (WebSocket) alerts everyone about critical issues

This is where the magic happens when you visit Debuggle's website or send API requests!

What this "digital hospital" provides:
🔬 REST API endpoints - Like different hospital departments for different needs
📁 File upload functionality - Like bringing in medical records from other hospitals  
🚦 Rate limiting - Like managing patient flow so the hospital doesn't get overwhelmed
🌐 CORS handling - Like allowing ambulances from different cities to bring patients
💓 Health checks - Like the hospital's vital signs monitoring
📊 Service metadata - Like the hospital's information directory

Key difference from CLI:
- entry_point.py runs this when you want the "full hospital" (web server mode)
- debuggle_cli.py is like a "house call doctor" (command-line mode)

This is what makes Debuggle better than ChatGPT - it's a complete, integrated system
that can handle errors from websites, mobile apps, and direct integrations!
"""

# Import all the tools and libraries we need - like getting medical equipment for our hospital

# FastAPI framework - Our main hospital building framework
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware  # Allows websites from different domains to use our service
from fastapi.responses import JSONResponse, HTMLResponse  # Different ways to send responses back to users
from fastapi.staticfiles import StaticFiles  # Serves our website files (HTML, CSS, JavaScript)

# Rate limiting tools - Like controlling how many patients can see a doctor per hour
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address  # Identifies who is making requests
from slowapi.errors import RateLimitExceeded  # What happens when someone makes too many requests

# Python standard library imports - Basic tools that come with Python
import time  # For measuring how long things take and timestamps
import json  # For converting data to/from JSON format (the internet's common language)
import logging  # For recording what happens in our system
from datetime import datetime  # For working with dates and times
from typing import Optional, List, Dict  # Type hints to make our code clearer (Optional = might be None)

logger = logging.getLogger(__name__)

# Import our custom Debuggle components - Like specialized medical equipment
from .models import (
    # Data models - Like medical forms that define what information we need
    AnalyzeRequest, AnalyzeResponse, AnalyzeMetadata,  # For basic error analysis
    FileUploadResponse, FileUploadMetadata, LanguageEnum,  # For file uploads
    HealthResponse, TiersResponse, TierFeature, ErrorResponse,  # For system info and errors
    SearchRequest, SearchResponse, LogStorageRequest, LogStorageResponse,  # For persistent storage
    RetentionPolicyRequest, RetentionPolicyResponse, LogAnalyticsResponse,  # For data management
    AlertRuleRequest, AlertRuleResponse, AlertResponse, AlertAcknowledgeRequest,  # For alert rules and alerts
    AlertStatsResponse, AlertSeverityAPI, AlertChannelAPI,  # For alert statistics and enums
    BatchIngestionRequest, StreamingIngestionRequest, IngestionJobResponse,  # For scalable ingestion
    IngestionStatsResponse, StreamDataRequest, BulkUploadRequest,  # For ingestion system features
    IngestionSourceAPI, ProcessingPriorityAPI, IngestionStatusAPI,  # For ingestion enums
    ChartDataRequest, ChartDataResponse, DashboardRequest, DashboardResponse,  # For dashboard system
    DashboardListResponse, SystemMetricsResponse, ChartTypeAPI, TimeRangeAPI  # For dashboard features
)
from .processor import LogProcessor  # Our main error analysis engine - the "chief medical officer"
from .config_v2 import settings  # Configuration settings - like hospital policies and procedures
from .realtime import connection_manager, error_monitor  # Real-time communication system - like hospital intercom
from .self_monitor import setup_self_monitoring  # System that watches itself for problems - like security cameras
from .storage import DatabaseManager, RetentionManager, SearchManager  # Persistent storage system
from .alerting import AlertManager, AlertRule, Alert, AlertSeverity, AlertChannel  # Proactive alerting system
from .ingestion import initialize_ingestion_engine, get_ingestion_engine, IngestionSource, ProcessingPriority  # Scalable ingestion system
from .dashboard import initialize_dashboard_engine, get_dashboard_engine  # Rich dashboard system

# Step 1: Set up our "hospital security system" - rate limiting
# This prevents any single user from overwhelming our service with too many requests
# Like having a security guard who says "slow down, you can only see the doctor X times per hour"
limiter = Limiter(key_func=get_remote_address)  # Uses visitor's IP address to track requests

# Step 2: Create our main "hospital building" - the FastAPI application
# This is like constructing the main hospital facility with all its departments
app = FastAPI(
    title=settings.app_name,           # Hospital name (from our settings)
    version=settings.app_version,      # Which version of our hospital we're running
    description="🐞 Debuggle Core - Professional log debuggling and error analysis microservice",
    docs_url="/docs",                  # Where visitors can see all available services (like a hospital directory)
    redoc_url="/redoc"                 # Alternative documentation format (like a fancy brochure)
)

# Step 3: Install our "security system" in the hospital
# This actually activates the rate limiting we set up above
app.state.limiter = limiter  # Attach the limiter to our app
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # What to do when someone hits the limit

# Step 4: Set up "international access" - CORS middleware
# CORS = Cross-Origin Resource Sharing (allows websites from different domains to use our API)
# Like allowing ambulances from different cities to bring patients to our hospital
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # "*" means allow from anywhere (like accepting all ambulances)
    allow_credentials=True,       # Allow sending authentication info (like patient ID cards)
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc. - like all types of visits)
    allow_headers=["*"],          # Allow all headers (like all types of medical forms)
)

# Step 3: Set up our "internal monitoring system" - self-monitoring
# This is like having security cameras and health monitors throughout the hospital
# It watches our own system for problems and reports them in real-time
self_monitor = setup_self_monitoring(app, connection_manager)

# Step 4: Set up our "hospital website and brochures" - static file serving
# This serves the HTML, CSS, and JavaScript files that make up our web interface
# Like having a hospital website where patients can learn about services
import os
static_dir = "assets/static"  # Where our website files are stored
if os.path.exists(static_dir):  # Only if the directory actually exists
    # Mount the static files so people can access our website
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Step 5: Create our "chief medical officer" - the main error analysis engine
# This is the core brain that actually analyzes errors and generates insights
processor = LogProcessor()  # Our main diagnostic tool

# Step 6: Initialize persistent storage system - Our digital filing cabinet
# This handles long-term storage, search, and retention of all log data
database_manager = DatabaseManager("logs.db")  # SQLite database for local storage
search_manager = SearchManager(database_manager)  # Full-text search engine
retention_manager = RetentionManager(database_manager)  # Data retention policies

# Step 7: Initialize proactive alerting system - Our emergency notification center
# This monitors for critical issues and sends alerts through multiple channels
alert_manager = AlertManager(error_monitor)  # Alert system connected to real-time monitoring

# Step 8: Initialize scalable ingestion system - Our enterprise processing factory
# This handles large-scale log processing, streaming, and batch operations
ingestion_engine = initialize_ingestion_engine(
    max_concurrent_jobs=10,  # Process up to 10 jobs concurrently
    max_memory_mb=500  # 500MB memory limit for processing
)

# Step 9: Initialize rich dashboard system - Our visual analytics command center
# This creates beautiful, interactive dashboards with real-time charts and metrics
dashboard_engine = initialize_dashboard_engine(database_manager)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global Emergency Response System - When Things Go Wrong in Our Hospital! 🚨🏥
    
    This is like having a master emergency protocol that kicks in when ANYTHING
    unexpected happens in our hospital. Instead of letting the whole system crash,
    we catch the problem, document it, and give users a helpful response.
    
    Think of it as the "Code Blue" system in a hospital - when there's an emergency
    anywhere in the building, this system coordinates the response.
    
    What this does:
    1. Catches ANY error that wasn't handled elsewhere (like a safety net)
    2. Reports the error to our self-monitoring system (like calling security)
    3. Gives users a clean, helpful error message (instead of scary technical details)
    4. Keeps the service running for other users (doesn't bring down the whole hospital)
    """
    # Step 1: Report this incident to our internal monitoring system
    # Like filling out an incident report and alerting the hospital administration
    self_monitor.capture_exception(exc, "global_exception_handler", request)
    
    # Step 2: Send a clean, professional response to the user
    # Instead of showing scary error details, we give a helpful message
    return JSONResponse(
        status_code=500,  # HTTP 500 = "Internal Server Error" (something went wrong on our end)
        content=ErrorResponse(
            error="Internal server error",  # User-friendly error title
            # Show technical details only in debug mode (like showing X-rays only to doctors)
            details=str(exc) if settings.debug else "An unexpected error occurred",
            code="INTERNAL_ERROR"  # Unique code for this type of error
        ).model_dump()  # Convert to JSON format for sending over the internet
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Hospital Vital Signs Monitor - "Is Our System Healthy?" 💓🏥
    
    This is like a nurse taking the hospital's vital signs every few minutes.
    Other systems (load balancers, monitoring tools, uptime checkers) can
    call this endpoint to make sure our service is still running properly.
    
    It's the digital equivalent of asking "Are you okay?" and getting back
    "Yes, I'm healthy and ready to help patients!"
    
    Real-world usage:
    - Kubernetes uses this to know if it should restart our service
    - Load balancers use this to know if they should send traffic here
    - Monitoring systems use this to alert if something goes wrong
    - Developers use this to quickly check if the service is up
    
    Simple but CRUCIAL for production systems!
    """
    # Return a simple health status - like a thumbs up from the hospital
    return HealthResponse(
        status="ok",                    # "We're healthy and ready to serve!"
        service=settings.app_name,      # Which service this is (Debuggle Core)
        version=settings.app_version    # Which version we're running
    )


@app.get("/api/v1/tiers", response_model=TiersResponse)
async def get_tiers():
    """Get available service tiers and their features."""
    tiers = [
        TierFeature(
            name="Core",
            icon="🔧",
            features=[
                "✅ Log beautification & syntax highlighting", 
                "✅ Smart error summaries & tags", 
                "✅ File upload support", 
                "✅ Real-time WebSocket monitoring",
                "✅ Persistent storage (1-30 days retention)",
                "✅ Full-text search & advanced filtering",
                "✅ Log analytics dashboard",
                "✅ Automated retention policies"
            ]
        ),
        TierFeature(
            name="Pro",
            icon="⚡",
            features=[
                "✅ All Core features", 
                "🚧 Proactive alerting system", 
                "🚧 Email/Slack notifications", 
                "🚧 Pattern-based alert rules",
                "🚧 Scalable ingestion (GB+ files)"
            ]
        ),
        TierFeature(
            name="Team",
            icon="👥",
            features=[
                "✅ All Pro features", 
                "🚧 Rich dashboard visualizations", 
                "🚧 Custom charts & trend analysis", 
                "🚧 Team collaboration features",
                "🚧 Project-based organization"
            ]
        ),
        TierFeature(
            name="Enterprise",
            icon="🏢",
            features=[
                "✅ All Team features", 
                "🚧 Audit trails & compliance", 
                "🚧 SSO integration", 
                "🚧 Advanced security controls",
                "🚧 API rate limiting per user"
            ]
        ),
        TierFeature(
            name="Scale",
            icon="🚀",
            features=[
                "✅ All Enterprise features", 
                "🚧 AI-powered insights", 
                "🚧 GDPR/SOC2 compliance", 
                "🚧 Priority support",
                "🚧 Custom integrations"
            ]
        )
    ]
    
    return TiersResponse(tiers=tiers)


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
@limiter.limit(f"{settings.api.rate_limit_per_minute}/minute")  # Rate limiting - like appointment scheduling
async def analyze_log(request: Request, analyze_request: AnalyzeRequest):
    """
    🎯 THE MAIN EVENT - Our Core Error Analysis Service! 🔬🏥
    
    This is the "chief diagnostician" of our digital hospital - the main function
    that takes a patient's (error's) symptoms and provides a complete diagnosis.
    
    Think of it like bringing a sick patient to the emergency room:
    1. Patient arrives with symptoms (raw error logs)
    2. Doctors examine and run tests (our analysis algorithms)
    3. Medical report is generated (cleaned logs, summary, diagnosis)
    4. Treatment recommendations provided (error tags and solutions)
    
    What makes this BETTER than ChatGPT:
    ✅ Specialized for programming errors (like a specialist vs. general practitioner)
    ✅ Consistent analysis quality (same diagnosis every time)
    ✅ No data sent to external services (your code stays private)
    ✅ Integrated with development tools (works with your workflow)
    ✅ Fast and always available (no waiting for ChatGPT to respond)
    
    Input: Raw error logs/stack traces (like patient symptoms)
    Output: Complete analysis with insights (like a medical diagnosis report)
    """
    try:
        # Step 1: Pre-examination checks - Like checking if a patient is too sick for outpatient care
        # We need to make sure the error log isn't so massive that it would overwhelm our system
        if len(analyze_request.log_input) > settings.api.max_log_size:
            # This is like saying "this patient needs to go to a specialized trauma center"
            raise HTTPException(
                status_code=400,  # HTTP 400 = "Bad Request" (problem with what user sent)
                detail=ErrorResponse(
                    error="Log input too large",
                    details=f"Maximum size is {settings.api.max_log_size} characters",
                    code="INPUT_TOO_LARGE"  # Specific error code for tracking
                ).model_dump()
            )
        
        # Step 2: Check processing limits - Like making sure we don't overwork our doctors
        # Some users might ask us to process millions of log lines, which would crash our system
        if analyze_request.options.max_lines > settings.api.max_lines_limit:
            # This is like saying "we can only see 1000 patients per day, not 10,000"
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Max lines parameter too large",
                    details=f"Maximum allowed is {settings.api.max_lines_limit} lines",
                    code="MAX_LINES_EXCEEDED"
                ).model_dump()
            )
        
        # Process the log
        try:
            cleaned_log, summary, tags, metadata = processor.process_log(
                log_input=analyze_request.log_input,
                language=analyze_request.language.value,
                highlight=analyze_request.options.highlight,
                summarize=analyze_request.options.summarize and settings.enable_summarization,
                tags=analyze_request.options.tags,
                max_lines=analyze_request.options.max_lines
            )
            
            # Report successful processing to real-time monitoring
            if any(tag in ['Error', 'Critical', 'Exception'] for tag in tags):
                await error_monitor.report_error(
                    error_type="ErrorDetected",
                    message=f"Error detected in log processing: {summary[:100] if summary else 'No summary available'}",
                    source="api_analyze",
                    severity="warning",
                    metadata={
                        "detected_language": metadata.get("detected_language"),
                        "error_tags": tags,
                        "input_size": len(analyze_request.log_input),
                        "processing_time": metadata.get("processing_time")
                    }
                )
        
        except Exception as processing_error:
            # Report processing failure to real-time monitoring
            await error_monitor.report_log_processing_error(
                analyze_request.log_input,
                processing_error,
                {
                    "endpoint": "/api/v1/analyze",
                    "language": analyze_request.language.value,
                    "client_ip": str(request.client.host) if request.client else "unknown"
                }
            )
            raise processing_error
        
        # 💾 STORE LOG FOR HISTORICAL ANALYSIS - Save to permanent collection
        # This is like filing the medical record for future reference and research
        try:
            from .storage.database import LogEntry, LogSeverity
            from datetime import datetime
            
            # Determine severity level based on tags and content
            severity = LogSeverity.INFO  # Default
            if any(tag.lower() in ['critical', 'fatal', 'panic'] for tag in tags):
                severity = LogSeverity.CRITICAL
            elif any(tag.lower() in ['error', 'exception'] for tag in tags):
                severity = LogSeverity.ERROR
            elif any(tag.lower() in ['warning', 'warn'] for tag in tags):
                severity = LogSeverity.WARNING
            elif any(tag.lower() in ['debug'] for tag in tags):
                severity = LogSeverity.DEBUG
            
            # Create log entry for storage
            log_entry = LogEntry(
                log_id=database_manager.create_log_id(analyze_request.log_input, datetime.now()),
                timestamp=datetime.now(),
                original_log=analyze_request.log_input,
                processed_log=cleaned_log,
                summary=summary,
                tags=tags,
                severity=severity,
                language=analyze_request.language.value,
                metadata=metadata,
                source="api"
            )
            
            # Store in database (asynchronously to not slow down response)
            database_manager.store_log(log_entry)
            
            # 🚨 EVALUATE FOR ALERTS - Check if this log should trigger any notifications
            # This is like having the hospital's alert system check if this incident
            # requires immediate notification to emergency personnel
            try:
                import asyncio
                asyncio.create_task(alert_manager.evaluate_log_for_alerts(log_entry))
            except Exception as alert_error:
                # Don't fail the request if alert evaluation fails - just log it
                logger.warning(f"Failed to evaluate log for alerts: {alert_error}")
            
        except Exception as storage_error:
            # Don't fail the request if storage fails - just log it
            logger.warning(f"Failed to store log in database: {storage_error}")
        
        # Build response
        return AnalyzeResponse(
            cleaned_log=cleaned_log,
            summary=summary,
            tags=tags,
            metadata=AnalyzeMetadata(**metadata)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Processing failed",
                details=str(e) if settings.debug else "Failed to process log input",
                code="PROCESSING_ERROR"
            ).model_dump()
        )


@app.post("/api/v1/upload-log", response_model=FileUploadResponse)
@limiter.limit(f"{settings.api.rate_limit_per_minute}/minute")
async def upload_log_file(
    request: Request,
    file: UploadFile = File(..., description="Log file to process"),
    language: str = Form(default="auto", description="Programming language"),
    highlight: bool = Form(default=True, description="Apply syntax highlighting"),
    summarize: bool = Form(default=True, description="Generate error summary"),
    tags: bool = Form(default=True, description="Generate error tags"),
    max_lines: int = Form(default=1000, description="Maximum lines to process")
):
    """
    Upload and process a log file.
    
    Accepts various file formats (.log, .txt, .out, etc.) and processes them
    through the same analysis pipeline as the text endpoint.
    """
    try:
        # Validate file size (check content length if available)
        if file.size and file.size > settings.api.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="File too large",
                    details=f"Maximum file size is {settings.api.max_log_size} bytes",
                    code="FILE_TOO_LARGE"
                ).model_dump()
            )
        
        # Validate max_lines parameter
        if max_lines > settings.api.max_lines_limit:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Max lines parameter too large",
                    details=f"Maximum allowed is {settings.api.max_lines_limit} lines",
                    code="MAX_LINES_EXCEEDED"
                ).model_dump()
            )
        
        # Validate language parameter
        try:
            lang_enum = LanguageEnum(language)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Invalid language",
                    details=f"Supported languages: {', '.join([e.value for e in LanguageEnum])}",
                    code="INVALID_LANGUAGE"
                ).model_dump()
            )
        
        # Read file content
        content = await file.read()
        
        # Decode file content (try UTF-8 first, then other encodings)
        try:
            log_input = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                log_input = content.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail=ErrorResponse(
                        error="File encoding not supported",
                        details="Please upload a UTF-8 or Latin-1 encoded text file",
                        code="ENCODING_ERROR"
                    ).model_dump()
                )
        
        # Validate content size after decoding (check character count)
        if len(log_input) > settings.api.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="File content too large",
                    details=f"Maximum content size is {settings.api.max_log_size} characters",
                    code="CONTENT_TOO_LARGE"
                ).model_dump()
            )
        
        # Validate that file has content
        if not log_input.strip():
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Empty file",
                    details="The uploaded file appears to be empty",
                    code="EMPTY_FILE"
                ).model_dump()
            )
        
        # Process the log using existing processor
        cleaned_log, summary, error_tags, metadata = processor.process_log(
            log_input=log_input,
            language=lang_enum.value,
            highlight=highlight,
            summarize=summarize and settings.enable_summarization,
            tags=tags,
            max_lines=max_lines
        )
        
        # 💾 STORE LOG FOR HISTORICAL ANALYSIS - Save file upload to permanent collection
        # This is like filing uploaded medical records for future reference
        try:
            from .storage.database import LogEntry, LogSeverity
            from datetime import datetime
            
            # Determine severity level based on tags and content
            severity = LogSeverity.INFO  # Default
            if any(tag.lower() in ['critical', 'fatal', 'panic'] for tag in error_tags):
                severity = LogSeverity.CRITICAL
            elif any(tag.lower() in ['error', 'exception'] for tag in error_tags):
                severity = LogSeverity.ERROR
            elif any(tag.lower() in ['warning', 'warn'] for tag in error_tags):
                severity = LogSeverity.WARNING
            elif any(tag.lower() in ['debug'] for tag in error_tags):
                severity = LogSeverity.DEBUG
            
            # Create log entry for storage
            log_entry = LogEntry(
                log_id=database_manager.create_log_id(log_input, datetime.now()),
                timestamp=datetime.now(),
                original_log=log_input,
                processed_log=cleaned_log,
                summary=summary,
                tags=error_tags,
                severity=severity,
                language=lang_enum.value,
                file_path=file.filename,
                metadata=metadata,
                source="file_upload"
            )
            
            # Store in database (asynchronously to not slow down response)
            database_manager.store_log(log_entry)
            
            # 🚨 EVALUATE FOR ALERTS - Check if this uploaded log should trigger any notifications
            try:
                import asyncio
                asyncio.create_task(alert_manager.evaluate_log_for_alerts(log_entry))
            except Exception as alert_error:
                # Don't fail the request if alert evaluation fails - just log it
                logger.warning(f"Failed to evaluate uploaded log for alerts: {alert_error}")
            
        except Exception as storage_error:
            # Don't fail the request if storage fails - just log it
            logger.warning(f"Failed to store uploaded log in database: {storage_error}")
        
        # Build file upload specific metadata
        file_metadata = FileUploadMetadata(
            filename=file.filename or "unknown",
            file_size=len(content),
            **metadata
        )
        
        # Build response
        return FileUploadResponse(
            cleaned_log=cleaned_log,
            summary=summary,
            tags=error_tags,
            metadata=file_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="File processing failed",
                details=str(e) if settings.debug else "Failed to process uploaded file",
                code="FILE_PROCESSING_ERROR"
            ).model_dump()
        )


@app.post("/api/v1/analyze-with-context")
@limiter.limit(f"{settings.api.rate_limit_per_minute}/minute")
async def analyze_with_context(
    request: Request,
    log_input: str = Form(..., description="Raw log or stack trace"),
    project_root: Optional[str] = Form(default=None, description="Project root directory for context"),
    file_path: Optional[str] = Form(default=None, description="Specific file path if known"),
    language: str = Form(default="auto", description="Programming language"),
    highlight: bool = Form(default=True, description="Apply syntax highlighting"),
    summarize: bool = Form(default=True, description="Generate error summary"),
    tags: bool = Form(default=True, description="Generate error tags"),
    max_lines: int = Form(default=1000, description="Maximum lines to process")
):
    """
    🚀 **OUR CHATGPT KILLER FEATURE** 🚀
    
    Analyze errors with FULL CONTEXT that developers never paste into ChatGPT:
    - Surrounding code from the actual error location
    - Recent git changes that might have caused the issue
    - Project structure and dependencies
    - Environment information
    - Development context that ChatGPT never sees
    
    This provides WAY MORE insight than copy/pasting a stack trace!
    """
    try:
        # Validate input size
        if len(log_input) > settings.api.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=f"Log input too large. Maximum size is {settings.api.max_log_size} characters"
            )
        
        # Process with rich context extraction
        processor = LogProcessor()
        cleaned_log, summary, tags_list, metadata, rich_context = processor.process_log_with_context(
            log_input=log_input,
            project_root=project_root,
            file_path=file_path,
            language=language,
            highlight=highlight,
            summarize=summarize,
            tags=tags,
            max_lines=max_lines
        )
        
        return {
            "message": "🎯 Analysis complete with FULL context - something ChatGPT can't do!",
            "basic_analysis": {
                "cleaned_log": cleaned_log,
                "summary": summary,
                "tags": tags_list,
                "metadata": metadata
            },
            "rich_context": rich_context,
            "competitive_advantage": {
                "vs_chatgpt": [
                    "✅ Includes surrounding code context",
                    "✅ Shows recent git changes",  
                    "✅ Analyzes project structure",
                    "✅ Provides environment details",
                    "✅ 100% private - no data sent to external APIs",
                    "✅ Integrated into your development workflow"
                ],
                "why_better": "ChatGPT only sees what you copy/paste. We see your entire development context!"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Context analysis failed: {str(e) if settings.debug else 'Processing error'}"
        )


# 💾 PERSISTENT STORAGE API ENDPOINTS - Advanced Data Management Features
# ========================================================================

@app.post("/api/v1/search", response_model=SearchResponse)
@limiter.limit(f"{settings.api.rate_limit_per_minute}/minute")
async def search_logs(request: Request, search_request: SearchRequest):
    """
    🔍 ADVANCED LOG SEARCH - Find Historical Errors Like a Detective!
    
    This is our advanced search system that can find historical error logs
    using multiple search criteria. Think of it like a sophisticated library
    search system that can find exactly what you're looking for!
    
    🏆 COMPETITIVE ADVANTAGE:
    Unlike ChatGPT which has no memory, we can search through ALL your
    historical errors to find patterns, similar issues, and solutions!
    """
    try:
        from .storage.search import SearchQuery, SortOrder
        from .storage.database import LogSeverity
        from datetime import datetime
        
        # Convert request to internal search query format
        query = SearchQuery(
            text=search_request.text,
            exact_phrase=search_request.exact_phrase,
            start_date=datetime.fromisoformat(search_request.start_date) if search_request.start_date else None,
            end_date=datetime.fromisoformat(search_request.end_date) if search_request.end_date else None,
            last_n_days=search_request.last_n_days,
            severities=[LogSeverity(s) for s in search_request.severities] if search_request.severities else None,
            languages=search_request.languages,
            tags=search_request.tags,
            projects=search_request.projects,
            sort_by=SortOrder(search_request.sort_by) if search_request.sort_by else SortOrder.NEWEST_FIRST,
            limit=search_request.limit,
            offset=search_request.offset
        )
        
        # Execute the search
        result = await search_manager.search(query)
        
        # Convert log entries to dict format for JSON response
        results_dict = []
        for log in result.logs:
            results_dict.append({
                "log_id": log.log_id,
                "timestamp": log.timestamp.isoformat(),
                "original_log": log.original_log,
                "processed_log": log.processed_log,
                "summary": log.summary,
                "tags": log.tags,
                "severity": log.severity.value,
                "language": log.language,
                "project_name": log.project_name,
                "file_path": log.file_path,
                "source": log.source
            })
        
        return SearchResponse(
            results=results_dict,
            total_matches=result.total_matches,
            search_duration_ms=result.search_duration_ms,
            suggested_filters=result.suggested_filters,
            related_tags=result.related_tags,
            query_info=result.query_executed
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Search failed",
                details=str(e) if settings.debug else "Failed to execute search",
                code="SEARCH_ERROR"
            ).model_dump()
        )


@app.get("/api/v1/analytics", response_model=LogAnalyticsResponse)
@limiter.limit(f"{settings.api.rate_limit_per_minute}/minute")
async def get_log_analytics(request: Request):
    """
    📊 LOG ANALYTICS DASHBOARD - Historical Error Insights!
    
    This provides comprehensive analytics about your error patterns over time.
    Think of it like a "year in review" report that shows trends, patterns,
    and insights from all your historical error data.
    
    🏆 COMPETITIVE ADVANTAGE:
    ChatGPT can't provide historical analysis of YOUR specific errors.
    We can show you patterns like "JavaScript errors spike on Fridays"
    or "IndexErrors are your most common Python issue."
    """
    try:
        # Get comprehensive statistics from database
        stats = database_manager.get_statistics()
        
        # Get search analytics
        search_analytics = search_manager.get_search_analytics()
        
        # Calculate database size (rough estimate)
        import os
        db_size_mb = None
        try:
            if os.path.exists(database_manager.database_path):
                db_size_bytes = os.path.getsize(database_manager.database_path)
                db_size_mb = db_size_bytes / (1024 * 1024)  # Convert to MB
        except:
            pass
        
        return LogAnalyticsResponse(
            total_logs=stats.total_logs,
            logs_today=stats.logs_today,
            logs_this_week=stats.logs_this_week,
            logs_this_month=stats.logs_this_month,
            top_error_types=stats.top_error_types,
            top_languages=stats.top_languages,
            top_severities=stats.top_severity_levels,
            daily_error_counts=stats.errors_per_day_last_week,
            hourly_patterns={str(hour): count for hour, count in stats.busiest_hours.items()},
            popular_search_terms=search_analytics.get("popular_search_terms", []),
            search_performance={
                "avg_search_time_ms": search_analytics.get("average_search_time_ms", 0),
                "total_searches": search_analytics.get("total_searches", 0)
            },
            database_size_mb=db_size_mb,
            oldest_log_date=stats.oldest_log_date.isoformat() if stats.oldest_log_date else None,
            newest_log_date=stats.newest_log_date.isoformat() if stats.newest_log_date else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Analytics failed",
                details=str(e) if settings.debug else "Failed to generate analytics",
                code="ANALYTICS_ERROR"
            ).model_dump()
        )


@app.post("/api/v1/retention/policy", response_model=RetentionPolicyResponse)
@limiter.limit(f"{settings.api.rate_limit_per_minute}/minute")
async def create_retention_policy(request: Request, policy_request: RetentionPolicyRequest):
    """
    📅 CREATE DATA RETENTION POLICY - Automated Log Cleanup!
    
    This creates automatic policies for cleaning up old log data.
    Think of it like setting up automatic file cleanup rules on your
    computer - "delete debug logs after 7 days, archive errors after 30 days."
    
    🏆 COMPETITIVE ADVANTAGE:
    Unlike cloud solutions that charge you for storage forever, our local
    retention policies give you complete control over your data lifecycle!
    """
    try:
        from .storage.retention import RetentionRule, RetentionAction
        from .storage.database import LogSeverity
        
        # Convert request to internal retention rule format
        rule = RetentionRule(
            name=policy_request.policy_name,
            description=policy_request.description,
            days_to_keep=policy_request.days_to_keep,
            action=RetentionAction(policy_request.action),
            severity_filter=[LogSeverity(s) for s in policy_request.severity_filter] if policy_request.severity_filter else None,
            language_filter=policy_request.language_filter,
            tag_filter=policy_request.tag_filter,
            project_filter=policy_request.project_filter,
            enabled=policy_request.enabled,
            archive_path=policy_request.archive_path
        )
        
        # Add the rule to retention manager
        retention_manager.add_rule(rule)
        
        # Get current policy status
        status = retention_manager.get_retention_status()
        
        return RetentionPolicyResponse(
            message=f"Retention policy '{policy_request.policy_name}' created successfully",
            policy_info={
                "name": rule.name,
                "description": rule.description,
                "days_to_keep": rule.days_to_keep,
                "action": rule.action.value,
                "enabled": rule.enabled,
                "filters": {
                    "severities": [s.value for s in rule.severity_filter] if rule.severity_filter else None,
                    "languages": rule.language_filter,
                    "tags": rule.tag_filter,
                    "projects": rule.project_filter
                }
            },
            total_policies=status["total_rules"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Policy creation failed",
                details=str(e) if settings.debug else "Failed to create retention policy",
                code="RETENTION_POLICY_ERROR"
            ).model_dump()
        )


@app.post("/api/v1/retention/execute")
@limiter.limit("5/hour")  # Limited to 5 times per hour to prevent abuse
async def execute_retention_policies(request: Request):
    """
    🧹 EXECUTE RETENTION CLEANUP - Run Data Cleanup Now!
    
    This manually triggers the data retention cleanup process.
    Normally this runs automatically, but you can trigger it manually
    if needed. Like running a "disk cleanup" tool on your computer.
    
    ⚠️ LIMITED USE: Only 5 times per hour to prevent system overload.
    """
    try:
        # Execute retention policies
        report = await retention_manager.execute_retention_policies()
        
        return {
            "message": "Retention policies executed successfully",
            "execution_report": {
                "total_logs_processed": report.total_logs_processed,
                "actions_taken": {action.value: count for action, count in report.actions_taken.items()},
                "rules_executed": report.rules_executed,
                "duration_seconds": report.duration_seconds,
                "errors": report.errors
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Retention execution failed",
                details=str(e) if settings.debug else "Failed to execute retention policies",
                code="RETENTION_EXECUTION_ERROR"
            ).model_dump()
        )


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML frontend."""
    with open("assets/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/v1", response_class=JSONResponse)
async def api_info():
    """API information endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "upload": "/api/v1/upload-log",
            "tiers": "/api/v1/tiers",
            "realtime": "/ws/errors",
            "error_stats": "/api/v1/errors/stats"
        }
    }


# WebSocket endpoints for real-time error reporting
@app.websocket("/ws/errors")
async def websocket_errors(websocket: WebSocket):
    """WebSocket endpoint for real-time error updates."""
    try:
        await connection_manager.connect(websocket, {
            "endpoint": "/ws/errors",
            "purpose": "real-time error monitoring"
        })
        
        # Send welcome message with current stats
        welcome_message = {
            "type": "welcome",
            "message": "Connected to real-time error monitoring",
            "stats": error_monitor.get_error_stats(),
            "recent_errors": error_monitor.get_recent_errors(10)
        }
        await connection_manager.send_personal_message(json.dumps(welcome_message), websocket)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (like ping/pong or config changes)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await connection_manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": time.time()}), 
                        websocket
                    )
                elif message.get("type") == "get_stats":
                    stats = {
                        "type": "stats_update",
                        "error_stats": error_monitor.get_error_stats(),
                        "connection_stats": connection_manager.get_connection_stats()
                    }
                    await connection_manager.send_personal_message(json.dumps(stats), websocket)
                elif message.get("type") == "get_recent_errors":
                    limit = message.get("limit", 20)
                    recent = {
                        "type": "recent_errors",
                        "errors": error_monitor.get_recent_errors(limit)
                    }
                    await connection_manager.send_personal_message(json.dumps(recent), websocket)
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection_manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}), 
                    websocket
                )
            except Exception as e:
                await connection_manager.send_personal_message(
                    json.dumps({"type": "error", "message": f"Server error: {str(e)}"}), 
                    websocket
                )
                
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(websocket)


@app.get("/api/v1/errors/stats")
async def get_error_stats():
    """Get current error monitoring statistics."""
    return {
        "error_stats": error_monitor.get_error_stats(),
        "connection_stats": connection_manager.get_connection_stats(),
        "monitoring_enabled": error_monitor.monitoring_enabled
    }


@app.post("/api/v1/errors/toggle-monitoring")
async def toggle_error_monitoring(enabled: bool = True):
    """Enable or disable real-time error monitoring."""
    error_monitor.toggle_monitoring(enabled)
    
    # Broadcast the monitoring status change
    status_message = {
        "type": "monitoring_status",
        "enabled": enabled,
        "message": f"Error monitoring {'enabled' if enabled else 'disabled'}"
    }
    await connection_manager.broadcast(json.dumps(status_message))
    
    return {"message": f"Error monitoring {'enabled' if enabled else 'disabled'}", "enabled": enabled}


# ===================================================================================
# 🚨 ALERT SYSTEM ROUTES - Proactive Notification Management! 🚨
# ===================================================================================

@app.post("/api/v1/alerts/rules", response_model=AlertRuleResponse)
async def create_alert_rule(request: AlertRuleRequest):
    """
    📝 CREATE NEW ALERT RULE - Set Up a New Alarm System!
    
    This endpoint creates a new alert rule that will monitor your logs
    and send notifications when certain conditions are met. It's like
    setting up a new smoke detector in your house that will call the
    fire department automatically when it detects danger.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like programming a security system at school:
    1. Tell it what to watch for ("motion after 10 PM")
    2. Tell it who to notify ("call security guard")
    3. Give it a name ("After Hours Motion Alert")
    4. The system will automatically watch and alert!
    """
    try:
        # Generate unique rule ID
        import uuid
        rule_id = str(uuid.uuid4())
        
        # Create AlertRule object from request
        # Convert models.LogSeverity to storage.database.LogSeverity for compatibility
        from .storage.database import LogSeverity as StorageLogSeverity
        severity_filter = None
        if request.severity_filter:
            severity_filter = [StorageLogSeverity(sev.value) for sev in request.severity_filter]
        
        alert_rule = AlertRule(
            rule_id=rule_id,
            name=request.name,
            description=request.description,
            severity_filter=severity_filter,
            language_filter=request.language_filter,
            tag_filter=request.tag_filter,
            project_filter=request.project_filter,
            content_regex=request.content_regex,
            error_count_threshold=request.error_count_threshold,
            time_window_minutes=request.time_window_minutes,
            business_hours_only=request.business_hours_only,
            business_start_hour=request.business_start_hour,
            business_end_hour=request.business_end_hour,
            weekdays_only=request.weekdays_only,
            alert_severity=AlertSeverity(request.alert_severity.value),
            channels=[AlertChannel(ch.value) for ch in request.channels],
            email_recipients=request.email_recipients,
            slack_channels=request.slack_channels,
            webhook_urls=request.webhook_urls,
            enabled=request.enabled,
            cooldown_minutes=request.cooldown_minutes,
            escalation_minutes=request.escalation_minutes,
            custom_message_template=request.custom_message_template
        )
        
        # Add rule to alert manager
        alert_manager.add_alert_rule(alert_rule)
        
        # Return response - convert back to models.LogSeverity
        from .models import LogSeverity as ModelsLogSeverity
        response_severity_filter = None
        if alert_rule.severity_filter:
            response_severity_filter = [ModelsLogSeverity(sev.value) for sev in alert_rule.severity_filter]
        
        return AlertRuleResponse(
            rule_id=alert_rule.rule_id,
            name=alert_rule.name,
            description=alert_rule.description,
            enabled=alert_rule.enabled,
            created_at=alert_rule.created_at.isoformat(),
            last_triggered=alert_rule.last_triggered.isoformat() if alert_rule.last_triggered else None,
            trigger_count=alert_rule.trigger_count,
            severity_filter=response_severity_filter,
            language_filter=alert_rule.language_filter,
            tag_filter=alert_rule.tag_filter,
            project_filter=alert_rule.project_filter,
            content_regex=alert_rule.content_regex,
            error_count_threshold=alert_rule.error_count_threshold,
            time_window_minutes=alert_rule.time_window_minutes,
            business_hours_only=alert_rule.business_hours_only,
            business_start_hour=alert_rule.business_start_hour,
            business_end_hour=alert_rule.business_end_hour,
            weekdays_only=alert_rule.weekdays_only,
            alert_severity=AlertSeverityAPI(alert_rule.alert_severity.value),
            channels=[AlertChannelAPI(ch.value) for ch in alert_rule.channels],
            email_recipients=alert_rule.email_recipients,
            slack_channels=alert_rule.slack_channels,
            webhook_urls=alert_rule.webhook_urls,
            cooldown_minutes=alert_rule.cooldown_minutes,
            escalation_minutes=alert_rule.escalation_minutes,
            custom_message_template=alert_rule.custom_message_template
        )
        
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert rule: {str(e)}")


@app.get("/api/v1/alerts/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules():
    """
    📋 LIST ALL ALERT RULES - See All Your Alarm Systems!
    
    This endpoint returns a list of all configured alert rules,
    showing you what alarms you have set up and their current status.
    Like getting a report of all the security systems in your building.
    """
    try:
        from .models import LogSeverity as ModelsLogSeverity
        rules = []
        for rule in alert_manager.rules.values():
            # Convert storage.LogSeverity back to models.LogSeverity
            response_severity_filter = None
            if rule.severity_filter:
                response_severity_filter = [ModelsLogSeverity(sev.value) for sev in rule.severity_filter]
            
            rules.append(AlertRuleResponse(
                rule_id=rule.rule_id,
                name=rule.name,
                description=rule.description,
                enabled=rule.enabled,
                created_at=rule.created_at.isoformat(),
                last_triggered=rule.last_triggered.isoformat() if rule.last_triggered else None,
                trigger_count=rule.trigger_count,
                severity_filter=response_severity_filter,
                language_filter=rule.language_filter,
                tag_filter=rule.tag_filter,
                project_filter=rule.project_filter,
                content_regex=rule.content_regex,
                error_count_threshold=rule.error_count_threshold,
                time_window_minutes=rule.time_window_minutes,
                business_hours_only=rule.business_hours_only,
                business_start_hour=rule.business_start_hour,
                business_end_hour=rule.business_end_hour,
                weekdays_only=rule.weekdays_only,
                alert_severity=AlertSeverityAPI(rule.alert_severity.value),
                channels=[AlertChannelAPI(ch.value) for ch in rule.channels],
                email_recipients=rule.email_recipients,
                slack_channels=rule.slack_channels,
                webhook_urls=rule.webhook_urls,
                cooldown_minutes=rule.cooldown_minutes,
                escalation_minutes=rule.escalation_minutes,
                custom_message_template=rule.custom_message_template
            ))
        
        return rules
        
    except Exception as e:
        logger.error(f"Error listing alert rules: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list alert rules: {str(e)}")


@app.delete("/api/v1/alerts/rules/{rule_id}")
async def delete_alert_rule(rule_id: str):
    """
    🗑️ DELETE ALERT RULE - Remove an Alarm System!
    
    This endpoint removes an alert rule, effectively turning off
    that particular alarm system. Like uninstalling a smoke detector
    that you no longer need.
    """
    try:
        success = alert_manager.remove_alert_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        return {"message": f"Alert rule {rule_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert rule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete alert rule: {str(e)}")


@app.get("/api/v1/alerts", response_model=List[AlertResponse])
async def list_active_alerts():
    """
    🚨 LIST ACTIVE ALERTS - See What Alarms Are Currently Going Off!
    
    This endpoint returns all currently active (unresolved) alerts.
    Like checking a security panel to see which alarms are currently
    flashing red and need attention.
    """
    try:
        alerts = []
        for alert in alert_manager.active_alerts.values():
            alerts.append(AlertResponse(
                alert_id=alert.alert_id,
                rule_id=alert.rule_id,
                rule_name=alert.rule_name,
                timestamp=alert.timestamp.isoformat(),
                message=alert.message,
                details=alert.details,
                severity=AlertSeverityAPI(alert.severity.value),
                triggered_by_log=alert.triggered_by_log,
                source_project=alert.source_project,
                source_language=alert.source_language,
                error_tags=alert.error_tags,
                status=alert.status,
                acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                acknowledged_by=alert.acknowledged_by,
                resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
                channels_notified=alert.channels_notified,
                delivery_failures=alert.delivery_failures,
                escalated=alert.escalated,
                escalated_at=alert.escalated_at.isoformat() if alert.escalated_at else None,
                escalation_level=alert.escalation_level
            ))
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error listing active alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list active alerts: {str(e)}")


@app.post("/api/v1/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, request: AlertAcknowledgeRequest):
    """
    ✅ ACKNOWLEDGE ALERT - "I Got The Message!"
    
    This endpoint marks an alert as acknowledged, meaning someone
    has seen it and is taking action. Like pressing the button
    on a fire alarm to confirm you heard it and are evacuating.
    """
    try:
        success = alert_manager.acknowledge_alert(alert_id, request.acknowledged_by)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": f"Alert {alert_id} acknowledged by {request.acknowledged_by}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@app.post("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """
    ✅ RESOLVE ALERT - "Problem Fixed!"
    
    This endpoint marks an alert as resolved, meaning the underlying
    issue has been fixed. Like turning off a fire alarm after
    confirming the fire has been extinguished.
    """
    try:
        success = alert_manager.resolve_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": f"Alert {alert_id} resolved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@app.get("/api/v1/alerts/stats", response_model=AlertStatsResponse)
async def get_alert_statistics():
    """
    📊 ALERT SYSTEM STATISTICS - Performance Dashboard!
    
    This endpoint provides comprehensive statistics about your
    alerting system's performance and activity. Like getting
    a monthly report on how your security system is performing.
    """
    try:
        stats = alert_manager.get_alert_statistics()
        return AlertStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alert statistics: {str(e)}")


# ===================================================================================
# 🚀 SCALABLE INGESTION ROUTES - Enterprise Processing Endpoints! 🚀
# ===================================================================================

@app.post("/api/v1/ingestion/batch", response_model=IngestionJobResponse)
async def submit_batch_job(
    request: BatchIngestionRequest,
    file: UploadFile = File(..., description="Large file to process in batch mode")
):
    """
    📦 SUBMIT BATCH PROCESSING JOB - Enterprise-Scale File Handling!
    
    This endpoint handles very large files by processing them efficiently
    in the background using specialized batch processing techniques. Perfect
    for multi-gigabyte log files that would overwhelm regular processing.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like submitting a huge printing job to a copy center:
    1. You upload your massive file (thousands of pages)
    2. They give you a tracking number for your job
    3. They process it using industrial equipment in the background
    4. You can check progress and get the results when done
    
    Instead of trying to process everything at once and crashing,
    the system handles it professionally with proper resource management!
    """
    try:
        # 📁 SAVE UPLOADED FILE TO TEMPORARY LOCATION
        import tempfile
        
        # Read uploaded content
        content = await file.read()
        
        # Create temporary file for processing
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        temp_file.write(content)
        temp_file_path = temp_file.name
        temp_file.close()
        
        # 📊 PREPARE JOB METADATA
        metadata = {
            'filename': file.filename or 'unknown',
            'file_size': len(content),
            'content_type': file.content_type,
            'description': request.description,
            'project_name': request.project_name,
            'language': request.language,
            'tags': request.tags,
            'chunk_size': request.chunk_size,
            'enable_streaming_updates': request.enable_streaming_updates,
            'notification_webhook': request.notification_webhook
        }
        
        # 🚀 SUBMIT TO INGESTION ENGINE
        from .models import ProcessingPriorityAPI
        priority_map = {
            ProcessingPriorityAPI.CRITICAL: ProcessingPriority.CRITICAL,
            ProcessingPriorityAPI.HIGH: ProcessingPriority.HIGH,
            ProcessingPriorityAPI.NORMAL: ProcessingPriority.NORMAL,
            ProcessingPriorityAPI.LOW: ProcessingPriority.LOW,
            ProcessingPriorityAPI.BATCH: ProcessingPriority.BATCH
        }
        
        job_id = await ingestion_engine.submit_job(
            source=IngestionSource.BATCH_UPLOAD,
            priority=priority_map[request.priority],
            file_path=temp_file_path,
            metadata=metadata
        )
        
        # 📋 GET JOB STATUS TO RETURN
        job = ingestion_engine.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create batch job")
        
        # 🔄 CONVERT TO API RESPONSE FORMAT
        from .models import IngestionSourceAPI, ProcessingPriorityAPI, IngestionStatusAPI
        source_map = {v: k for k, v in {
            IngestionSourceAPI.BATCH_UPLOAD: IngestionSource.BATCH_UPLOAD
        }.items()}
        
        status_map = {
            'queued': IngestionStatusAPI.QUEUED,
            'processing': IngestionStatusAPI.PROCESSING,
            'completed': IngestionStatusAPI.COMPLETED,
            'failed': IngestionStatusAPI.FAILED,
            'partial': IngestionStatusAPI.PARTIALLY_FAILED,
            'cancelled': IngestionStatusAPI.CANCELLED
        }
        
        return IngestionJobResponse(
            job_id=job.job_id,
            source=IngestionSourceAPI.BATCH_UPLOAD,
            priority=request.priority,
            status=status_map.get(job.status.value, IngestionStatusAPI.QUEUED),
            progress_percent=job.progress_percent,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            bytes_processed=job.bytes_processed,
            lines_processed=job.lines_processed,
            processing_time_seconds=job.processing_time_seconds,
            processed_logs=job.processed_logs,
            failed_logs=job.failed_logs,
            error_messages=job.error_messages,
            metadata=job.metadata
        )
        
    except Exception as e:
        logger.error(f"Error submitting batch job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit batch job: {str(e)}")


@app.get("/api/v1/ingestion/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_job_status(job_id: str):
    """
    📊 CHECK JOB STATUS - Track Your Processing Order!
    
    This endpoint lets you check the status and progress of any
    ingestion job using its tracking ID. Like checking the status
    of a package delivery or restaurant order.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like checking your pizza delivery status:
    - "Your order is being prepared" (processing)
    - "Out for delivery" (in progress with 75% complete)
    - "Delivered!" (completed successfully)
    - Or "Sorry, there was a problem" (failed with error details)
    """
    try:
        job = ingestion_engine.get_job_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # 🔄 CONVERT TO API RESPONSE FORMAT
        from .models import IngestionSourceAPI, ProcessingPriorityAPI, IngestionStatusAPI
        
        # Map internal enums to API enums
        source_map = {
            IngestionSource.FILE_UPLOAD: IngestionSourceAPI.FILE_UPLOAD,
            IngestionSource.STREAMING: IngestionSourceAPI.STREAMING,
            IngestionSource.BATCH_UPLOAD: IngestionSourceAPI.BATCH_UPLOAD,
            IngestionSource.WEBHOOK: IngestionSourceAPI.WEBHOOK,
            IngestionSource.API_DIRECT: IngestionSourceAPI.API_DIRECT,
            IngestionSource.WEBSOCKET: IngestionSourceAPI.WEBSOCKET
        }
        
        priority_map = {
            ProcessingPriority.CRITICAL: ProcessingPriorityAPI.CRITICAL,
            ProcessingPriority.HIGH: ProcessingPriorityAPI.HIGH,
            ProcessingPriority.NORMAL: ProcessingPriorityAPI.NORMAL,
            ProcessingPriority.LOW: ProcessingPriorityAPI.LOW,
            ProcessingPriority.BATCH: ProcessingPriorityAPI.BATCH
        }
        
        status_map = {
            'queued': IngestionStatusAPI.QUEUED,
            'processing': IngestionStatusAPI.PROCESSING,
            'completed': IngestionStatusAPI.COMPLETED,
            'failed': IngestionStatusAPI.FAILED,
            'partial': IngestionStatusAPI.PARTIALLY_FAILED,
            'cancelled': IngestionStatusAPI.CANCELLED
        }
        
        return IngestionJobResponse(
            job_id=job.job_id,
            source=source_map.get(job.source, IngestionSourceAPI.FILE_UPLOAD),
            priority=priority_map.get(job.priority, ProcessingPriorityAPI.NORMAL),
            status=status_map.get(job.status.value, IngestionStatusAPI.QUEUED),
            progress_percent=job.progress_percent,
            created_at=job.created_at.isoformat(),
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            bytes_processed=job.bytes_processed,
            lines_processed=job.lines_processed,
            processing_time_seconds=job.processing_time_seconds,
            processed_logs=job.processed_logs,
            failed_logs=job.failed_logs,
            error_messages=job.error_messages,
            metadata=job.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@app.get("/api/v1/ingestion/stats", response_model=IngestionStatsResponse)
async def get_ingestion_statistics():
    """
    📈 GET INGESTION SYSTEM STATISTICS - Factory Performance Dashboard!
    
    This endpoint provides comprehensive statistics about the ingestion
    system's performance, capacity utilization, and processing metrics.
    Like getting a real-time dashboard of a factory's production status.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a restaurant's end-of-day report:
    - "We served 200 customers today" (jobs completed)
    - "Average order time was 15 minutes" (processing performance)
    - "Kitchen is currently at 80% capacity" (system utilization)
    - "We have 5 orders waiting" (queued jobs)
    
    This helps you understand how busy the system is and how well it's performing!
    """
    try:
        stats = ingestion_engine.get_system_stats()
        
        return IngestionStatsResponse(
            jobs_created=stats['jobs_created'],
            jobs_completed=stats['jobs_completed'],
            jobs_failed=stats['jobs_failed'],
            active_jobs=stats['active_jobs'],
            queued_jobs=stats['queued_jobs'],
            total_jobs=stats['total_jobs'],
            bytes_processed=stats['bytes_processed'],
            lines_processed=stats['lines_processed'],
            average_processing_time=stats['average_processing_time'],
            memory_usage_mb=stats['memory_usage_mb'],
            active_connections=stats['active_connections'],
            queue_sizes=stats['queue_sizes']
        )
        
    except Exception as e:
        logger.error(f"Error getting ingestion statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion statistics: {str(e)}")


@app.post("/api/v1/ingestion/stream/start", response_model=Dict[str, str])
async def start_streaming_session(request: StreamingIngestionRequest):
    """
    🌊 START STREAMING SESSION - Set Up Real-Time Log Processing!
    
    This endpoint starts a new streaming session that can accept
    continuous log data. Like setting up a conveyor belt that
    processes items as they're placed on it.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like starting a live video stream:
    1. You configure the stream settings (quality, resolution, etc.)
    2. The system gives you a stream URL/ID
    3. You can then send video data continuously
    4. Viewers see the content in real-time as it's processed
    
    But instead of video, we're streaming and processing log data!
    """
    try:
        # For now, we'll create a simple streaming job
        # In a full implementation, this would set up WebSocket connections
        # and streaming buffers
        
        metadata = {
            'stream_id': request.stream_id,
            'project_name': request.project_name,
            'language': request.language,
            'buffer_size_lines': request.buffer_size_lines,
            'buffer_size_bytes': request.buffer_size_bytes,
            'flush_interval_seconds': request.flush_interval_seconds,
            'webhook_url': request.webhook_url,
            'enable_alerts': request.enable_alerts
        }
        
        # Map API priority to internal priority
        priority_map = {
            ProcessingPriorityAPI.CRITICAL: ProcessingPriority.CRITICAL,
            ProcessingPriorityAPI.HIGH: ProcessingPriority.HIGH,
            ProcessingPriorityAPI.NORMAL: ProcessingPriority.NORMAL,
            ProcessingPriorityAPI.LOW: ProcessingPriority.LOW,
            ProcessingPriorityAPI.BATCH: ProcessingPriority.BATCH
        }
        
        # Submit streaming job setup
        job_id = await ingestion_engine.submit_job(
            source=IngestionSource.STREAMING,
            priority=priority_map[request.priority],
            metadata=metadata
        )
        
        return {
            "stream_id": request.stream_id,
            "job_id": job_id,
            "status": "streaming_session_started",
            "websocket_url": f"/ws/stream/{request.stream_id}",
            "message": f"Streaming session {request.stream_id} is ready to receive data"
        }
        
    except Exception as e:
        logger.error(f"Error starting streaming session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start streaming session: {str(e)}")


@app.post("/api/v1/ingestion/stream/{stream_id}/data")
async def send_stream_data(stream_id: str, request: StreamDataRequest):
    """
    📤 SEND DATA TO STREAM - Add Items to the Conveyor Belt!
    
    This endpoint sends log data to an active streaming session.
    The data will be buffered and processed according to the
    stream's configuration settings.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like adding items to a moving conveyor belt at a factory:
    - The belt is already running (streaming session is active)
    - You place items on it (send log data)
    - The factory processes them as they move along
    - You can keep adding more items continuously
    """
    try:
        if stream_id != request.stream_id:
            raise HTTPException(status_code=400, detail="Stream ID mismatch")
        
        # Submit the stream data as a processing job
        metadata = {
            'stream_id': stream_id,
            'timestamp': request.timestamp,
            'is_stream_data': True,
            **request.metadata
        }
        
        job_id = await ingestion_engine.submit_job(
            source=IngestionSource.STREAMING,
            priority=ProcessingPriority.NORMAL,
            content=request.log_data,
            metadata=metadata
        )
        
        return {
            "stream_id": stream_id,
            "job_id": job_id,
            "status": "data_received",
            "message": f"Log data added to stream {stream_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending stream data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send stream data: {str(e)}")


# ===================================================================================
# 📊 RICH DASHBOARD ROUTES - Visual Analytics Endpoints! 📊
# ===================================================================================

@app.get("/api/v1/dashboards", response_model=DashboardListResponse)
async def list_dashboards():
    """
    📋 LIST ALL DASHBOARDS - Browse Available Dashboards!
    
    This endpoint returns a list of all available dashboards with
    summary information. Like browsing a directory of all the
    information displays available in a building.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like looking at a school directory that shows:
    - "Math Department Board" - displays test scores and assignments
    - "Sports Results Board" - shows game scores and team standings  
    - "Student Activities Board" - lists clubs and upcoming events
    - "Administrative Board" - shows announcements and policies
    
    Each dashboard serves a different purpose and audience!
    """
    try:
        dashboards = dashboard_engine.list_dashboards()
        
        # Build summary information for each dashboard
        dashboard_summaries = []
        for dashboard in dashboards:
            dashboard_summaries.append({
                'dashboard_id': dashboard.dashboard_id,
                'title': dashboard.title,
                'description': dashboard.description,
                'chart_count': len(dashboard.charts),
                'is_public': dashboard.is_public,
                'owner': dashboard.owner,
                'created_at': dashboard.created_at.isoformat(),
                'updated_at': dashboard.updated_at.isoformat(),
                'view_count': dashboard.view_count,
                'auto_refresh_enabled': dashboard.auto_refresh_enabled
            })
        
        # Calculate counts
        total_count = len(dashboards)
        public_count = len([d for d in dashboards if d.is_public])
        private_count = total_count - public_count
        
        return DashboardListResponse(
            dashboards=dashboard_summaries,
            total_count=total_count,
            public_count=public_count,
            private_count=private_count
        )
        
    except Exception as e:
        logger.error(f"Error listing dashboards: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list dashboards: {str(e)}")


@app.get("/api/v1/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: str):
    """
    📊 GET DASHBOARD DETAILS - View Complete Dashboard!
    
    This endpoint returns complete information about a specific dashboard,
    including all its charts, data, and configuration. Like getting a
    detailed view of one specific information display.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like walking up to the "Sports Results Board" and seeing:
    - The title "Winter Sports Championships"
    - A bar chart showing wins/losses by team
    - A pie chart showing budget allocation
    - A timeline showing game schedules
    - All the colors, styling, and layout details
    
    You get everything needed to fully understand and display the dashboard!
    """
    try:
        dashboard = dashboard_engine.get_dashboard(dashboard_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        # Increment view count
        dashboard.view_count += 1
        
        # Convert charts to response format
        chart_responses = []
        for chart in dashboard.charts:
            chart_responses.append(ChartDataResponse(
                chart_id=chart.chart_id,
                chart_type=ChartTypeAPI(chart.chart_type.value),
                title=chart.title,
                description=chart.description,
                data=chart.data,
                labels=chart.labels,
                datasets=chart.datasets,
                colors=chart.colors,
                background_colors=chart.background_colors,
                border_colors=chart.border_colors,
                options=chart.options,
                height=chart.height,
                width=chart.width,
                time_range=TimeRangeAPI(chart.time_range.value) if chart.time_range else None,
                last_updated=chart.last_updated.isoformat(),
                data_points_count=chart.data_points_count,
                auto_refresh=chart.auto_refresh,
                refresh_interval_seconds=chart.refresh_interval_seconds
            ))
        
        return DashboardResponse(
            dashboard_id=dashboard.dashboard_id,
            title=dashboard.title,
            description=dashboard.description,
            charts=chart_responses,
            widgets=dashboard.widgets,
            layout=dashboard.layout,
            theme=dashboard.theme,
            custom_css=dashboard.custom_css,
            owner=dashboard.owner,
            is_public=dashboard.is_public,
            allowed_users=dashboard.allowed_users,
            created_at=dashboard.created_at.isoformat(),
            updated_at=dashboard.updated_at.isoformat(),
            view_count=dashboard.view_count,
            auto_refresh_enabled=dashboard.auto_refresh_enabled,
            refresh_interval_seconds=dashboard.refresh_interval_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


@app.post("/api/v1/dashboards", response_model=DashboardResponse)
async def create_dashboard(request: DashboardRequest):
    """
    🎨 CREATE NEW DASHBOARD - Build Your Custom Analytics View!
    
    This endpoint creates a new custom dashboard with the specified
    configuration and charts. Like setting up a new information
    display board with exactly the content and layout you want.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like designing a custom bulletin board for your club:
    1. Choose a title: "Chess Club Achievements"
    2. Pick a theme: "Use school colors and clean layout"
    3. Add charts: "Show tournament results and member progress"
    4. Set refresh: "Update every week with new results"
    5. Choose access: "Members only" or "Public display"
    
    The system creates exactly what you specified!
    """
    try:
        # Generate unique dashboard ID
        import uuid
        dashboard_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        # Create dashboard
        dashboard = await dashboard_engine.create_dashboard(
            dashboard_id=dashboard_id,
            title=request.title,
            description=request.description,
            owner="api_user"  # Could be extracted from authentication
        )
        
        # Apply configuration
        dashboard.theme = request.theme
        dashboard.layout = request.layout
        dashboard.custom_css = request.custom_css
        dashboard.is_public = request.is_public
        dashboard.allowed_users = request.allowed_users
        dashboard.auto_refresh_enabled = request.auto_refresh_enabled
        dashboard.refresh_interval_seconds = request.refresh_interval_seconds
        
        # Add default charts if requested
        if request.include_default_charts:
            await dashboard_engine.create_default_charts(dashboard)
        
        # Add custom charts
        for chart_request in request.custom_charts:
            # This would create custom charts based on the requests
            # For now, we'll skip custom chart creation
            pass
        
        # Return the created dashboard
        return await get_dashboard(dashboard_id)
        
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create dashboard: {str(e)}")


@app.delete("/api/v1/dashboards/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """
    🗑️ DELETE DASHBOARD - Remove a Dashboard!
    
    This endpoint deletes a dashboard permanently. Like taking down
    an old bulletin board that's no longer needed.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like removing the "Fall Dance Committee" bulletin board
    after the dance is over - it cleans up space and removes
    outdated information that's no longer relevant.
    """
    try:
        success = dashboard_engine.delete_dashboard(dashboard_id)
        if not success:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        return {"message": f"Dashboard {dashboard_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete dashboard: {str(e)}")


@app.post("/api/v1/dashboards/{dashboard_id}/charts", response_model=ChartDataResponse)
async def create_chart(dashboard_id: str, request: ChartDataRequest):
    """
    📊 ADD CHART TO DASHBOARD - Create a New Visualization!
    
    This endpoint adds a new chart to an existing dashboard based
    on the specified configuration and data requirements. Like
    adding a new graph or display to an existing bulletin board.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like adding a new section to the "Student Government" board:
    - You specify: "Add a pie chart showing budget allocation"
    - The system: Pulls the budget data, creates the pie chart,
      applies nice colors, and adds it to the board
    - Result: The board now has your new chart alongside existing content
    """
    try:
        dashboard = dashboard_engine.get_dashboard(dashboard_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
        
        # Generate unique chart ID
        import uuid
        chart_id = f"chart_{uuid.uuid4().hex[:8]}"
        
        # Create chart based on request
        # This is a simplified implementation - in a real system,
        # you'd have more sophisticated chart creation logic
        from .dashboard import ChartData, ChartType
        
        chart = ChartData(
            chart_id=chart_id,
            chart_type=ChartType(request.chart_type.value),
            title=request.title,
            description=request.description,
            height=request.height,
            width=request.width
        )
        
        # Update chart with actual data based on request
        await dashboard_engine._update_chart_data(chart)
        
        # Add to dashboard
        dashboard.add_chart(chart)
        
        # Return chart response
        return ChartDataResponse(
            chart_id=chart.chart_id,
            chart_type=ChartTypeAPI(chart.chart_type.value),
            title=chart.title,
            description=chart.description,
            data=chart.data,
            labels=chart.labels,
            datasets=chart.datasets,
            colors=chart.colors,
            background_colors=chart.background_colors,
            border_colors=chart.border_colors,
            options=chart.options,
            height=chart.height,
            width=chart.width,
            time_range=TimeRangeAPI(chart.time_range.value) if chart.time_range else None,
            last_updated=chart.last_updated.isoformat(),
            data_points_count=chart.data_points_count,
            auto_refresh=chart.auto_refresh,
            refresh_interval_seconds=chart.refresh_interval_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create chart: {str(e)}")


@app.get("/api/v1/metrics/system", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """
    📊 GET SYSTEM METRICS - Key Performance Indicators!
    
    This endpoint provides comprehensive system metrics and statistics
    that are commonly needed for dashboards and monitoring. Like getting
    a complete health report for your entire system.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like getting the school's daily performance report:
    - "25 incidents handled today" (total errors)
    - "2.3 incidents per hour average" (error rate)
    - "Most issues: login problems" (top error types)
    - "Math department had most issues" (breakdown by area)
    - "Peak problems at 3 PM" (timeline patterns)
    
    This gives you all the key numbers for understanding system health!
    """
    try:
        # Get metrics from dashboard engine cache
        engine = dashboard_engine
        
        # Calculate key metrics
        total_errors = await engine._get_cached_metric('total_errors', engine._calculate_total_errors)
        recent_errors = await engine._get_cached_metric('recent_errors', engine._calculate_recent_errors)
        severity_dist = await engine._get_cached_metric('severity_dist', engine._calculate_severity_distribution)
        language_dist = await engine._get_cached_metric('language_dist', engine._calculate_language_distribution)
        timeline_data = await engine._get_cached_metric('timeline_24h', engine._calculate_timeline_data)
        top_errors = await engine._get_cached_metric('top_errors', engine._calculate_top_errors)
        
        # Calculate error rate (errors per hour)
        error_rate = recent_errors / 24.0 if recent_errors > 0 else 0.0
        
        # Build top languages list
        top_languages = [
            {'language': lang, 'count': count, 'percentage': round(count/sum(language_dist.values())*100, 1)}
            for lang, count in sorted(language_dist.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Calculate daily trend (last 7 days - placeholder data)
        daily_trend = [45, 38, 52, 41, 39, 47, recent_errors]
        
        return SystemMetricsResponse(
            total_errors=total_errors,
            errors_last_24h=recent_errors,
            errors_last_hour=max(1, recent_errors // 24),  # Rough estimate
            error_rate_per_hour=error_rate,
            critical_errors=severity_dist.get('critical', 0),
            error_errors=severity_dist.get('error', 0),
            warning_errors=severity_dist.get('warning', 0),
            info_messages=severity_dist.get('info', 0),
            top_languages=top_languages,
            top_error_types=top_errors,
            hourly_trend=timeline_data['counts'],
            daily_trend=daily_trend,
            database_size_mb=5.2,  # Placeholder
            total_log_entries=total_errors,
            oldest_log_date="2024-01-01T00:00:00Z",  # Placeholder
            newest_log_date=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@app.get("/api/v1/dashboards/default", response_model=DashboardResponse)
async def get_default_dashboard():
    """
    📊 GET DEFAULT SYSTEM DASHBOARD - Main Monitoring View!
    
    This endpoint returns the main system dashboard that provides
    an overview of system health and key metrics. Like the main
    information display in a building lobby.
    """
    try:
        if not dashboard_engine.default_dashboard:
            raise HTTPException(status_code=404, detail="Default dashboard not found")
        
        # Ensure default dashboard has charts
        if not dashboard_engine.default_dashboard.charts:
            await dashboard_engine.create_default_charts(dashboard_engine.default_dashboard)
        
        return await get_dashboard(dashboard_engine.default_dashboard.dashboard_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting default dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get default dashboard: {str(e)}")


# Additional middleware for request logging (optional)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log requests for monitoring purposes."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # In production, you might want to use proper logging here
    if settings.debug:
        print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )