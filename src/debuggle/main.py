"""
Debuggle FastAPI Application - Core web service

This module contains the FastAPI web application that provides:
- REST API endpoints for log analysis
- File upload functionality
- Rate limiting and CORS handling
- Health checks and service metadata

This is imported by entry_point.py when running in server mode.
For direct CLI usage, use the debuggle_cli.py module instead.
"""

from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import json
from typing import Optional

from .models import (
    AnalyzeRequest, AnalyzeResponse, AnalyzeMetadata,
    FileUploadResponse, FileUploadMetadata, LanguageEnum,
    HealthResponse, TiersResponse, TierFeature, ErrorResponse
)
from .processor import LogProcessor
from .config_v2 import settings
from .realtime import connection_manager, error_monitor

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="🐞 Debuggle Core - Professional log debuggling and error analysis microservice",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (HTML frontend) - only if directory exists
import os
static_dir = "assets/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize log processor
processor = LogProcessor()


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            details=str(exc) if settings.debug else "An unexpected error occurred",
            code="INTERNAL_ERROR"
        ).model_dump()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version
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
@limiter.limit(f"{settings.api.rate_limit_per_minute}/minute")
async def analyze_log(request: Request, analyze_request: AnalyzeRequest):
    """
    Analyze and process log entries or stack traces.
    
    Takes raw log input and returns:
    - Analyzed and formatted log with syntax highlighting
    - Human-readable error summary (if recognizable)
    - Error category tags
    - Processing metadata
    """
    try:
        # Validate input size
        if len(analyze_request.log_input) > settings.api.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Log input too large",
                    details=f"Maximum size is {settings.api.max_log_size} characters",
                    code="INPUT_TOO_LARGE"
                ).model_dump()
            )
        
        # Validate max_lines parameter
        if analyze_request.options.max_lines > settings.api.max_lines_limit:
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
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )