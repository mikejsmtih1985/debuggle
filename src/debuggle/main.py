"""
Debuggle FastAPI Web Server - The Heart of Our Error Analysis Service! 🏥💻

Think of this file as the "main office" of a hospital where:
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
from typing import Optional  # Type hints to make our code clearer (Optional = might be None)

# Import our custom Debuggle components - Like specialized medical equipment
from .models import (
    # Data models - Like medical forms that define what information we need
    AnalyzeRequest, AnalyzeResponse, AnalyzeMetadata,  # For basic error analysis
    FileUploadResponse, FileUploadMetadata, LanguageEnum,  # For file uploads
    HealthResponse, TiersResponse, TierFeature, ErrorResponse  # For system info and errors
)
from .processor import LogProcessor  # Our main error analysis engine - the "chief medical officer"
from .config_v2 import settings  # Configuration settings - like hospital policies and procedures
from .realtime import connection_manager, error_monitor  # Real-time communication system - like hospital intercom
from .self_monitor import setup_self_monitoring  # System that watches itself for problems - like security cameras

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
            features=["Debuggle logs", "Syntax highlighting", "Error tags", "Smart summaries", "File upload", "Web interface", "Enhanced stack trace analysis"]
        ),
        TierFeature(
            name="Pro",
            icon="⚡",
            features=["All Core features", "Log grouping", "Pattern detection", "Basic storage"]
        ),
        TierFeature(
            name="Team",
            icon="👥",
            features=["All Pro features", "Persistent storage", "Dashboard UI", "Search & filter"]
        ),
        TierFeature(
            name="Enterprise",
            icon="🏢",
            features=["All Team features", "Proactive alerts", "Integrations", "Team collaboration"]
        ),
        TierFeature(
            name="Scale",
            icon="🚀",
            features=["All Enterprise features", "AI insights", "SSO", "Compliance", "Priority support"]
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