from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from typing import List, Optional

from .models import (
    BeautifyRequest, BeautifyResponse, BeautifyMetadata,
    FileUploadResponse, FileUploadMetadata, LanguageEnum,
    HealthResponse, TiersResponse, TierFeature, ErrorResponse
)
from .processor import LogProcessor
from .config import settings

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

# Mount static files (HTML frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

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
            features=["Debuggle logs", "Syntax highlighting", "Error tags", "Smart summaries"]
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


@app.post("/api/v1/beautify", response_model=BeautifyResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def beautify_log(request: Request, beautify_request: BeautifyRequest):
    """
    Debuggle and analyze log entries or stack traces.
    
    Takes raw log input and returns:
    - Debuggled and formatted log with syntax highlighting
    - Human-readable error summary (if recognizable)
    - Error category tags
    - Processing metadata
    """
    try:
        # Validate input size
        if len(beautify_request.log_input) > settings.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Log input too large",
                    details=f"Maximum size is {settings.max_log_size} characters",
                    code="INPUT_TOO_LARGE"
                ).model_dump()
            )
        
        # Validate max_lines parameter
        if beautify_request.options.max_lines > settings.max_lines_limit:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Max lines parameter too large",
                    details=f"Maximum allowed is {settings.max_lines_limit} lines",
                    code="MAX_LINES_EXCEEDED"
                ).model_dump()
            )
        
        # Process the log
        cleaned_log, summary, tags, metadata = processor.process_log(
            log_input=beautify_request.log_input,
            language=beautify_request.language.value,
            highlight=beautify_request.options.highlight,
            summarize=beautify_request.options.summarize and settings.enable_summarization,
            tags=beautify_request.options.tags,
            max_lines=beautify_request.options.max_lines
        )
        
        # Build response
        return BeautifyResponse(
            cleaned_log=cleaned_log,
            summary=summary,
            tags=tags,
            metadata=BeautifyMetadata(**metadata)
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
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
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
    through the same beautification pipeline as the text endpoint.
    """
    try:
        # Validate file size (check content length if available)
        if file.size and file.size > settings.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="File too large",
                    details=f"Maximum file size is {settings.max_log_size} bytes",
                    code="FILE_TOO_LARGE"
                ).model_dump()
            )
        
        # Validate max_lines parameter
        if max_lines > settings.max_lines_limit:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Max lines parameter too large",
                    details=f"Maximum allowed is {settings.max_lines_limit} lines",
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
        
        # Validate content size after reading
        if len(content) > settings.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="File content too large",
                    details=f"Maximum content size is {settings.max_log_size} bytes",
                    code="CONTENT_TOO_LARGE"
                ).model_dump()
            )
        
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


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML frontend."""
    with open("static/index.html", "r") as f:
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
            "beautify": "/api/v1/beautify",
            "upload": "/api/v1/upload-log",
            "tiers": "/api/v1/tiers"
        }
    }


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