from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from typing import List

from .models import (
    BeautifyRequest, BeautifyResponse, BeautifyMetadata,
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
    description="🐞 Debuggle Trace Level - Log beautification and error analysis microservice",
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
        ).dict()
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
            name="Trace Level",
            icon="🐜",
            features=["Beautify logs", "Syntax highlighting", "Error tags", "Smart summaries"]
        ),
        TierFeature(
            name="Swarm Level",
            icon="🐝",
            features=["All Trace features", "Log grouping", "Pattern detection", "Basic storage"]
        ),
        TierFeature(
            name="Beetle Level",
            icon="🪲",
            features=["All Swarm features", "Persistent storage", "Dashboard UI", "Search & filter"]
        ),
        TierFeature(
            name="Spider Level",
            icon="🕷️",
            features=["All Beetle features", "Proactive alerts", "Integrations", "Team collaboration"]
        ),
        TierFeature(
            name="Butterfly Level",
            icon="🦋",
            features=["All Spider features", "AI insights", "SSO", "Compliance", "Enterprise support"]
        )
    ]
    
    return TiersResponse(tiers=tiers)


@app.post("/api/v1/beautify", response_model=BeautifyResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def beautify_log(request: Request, beautify_request: BeautifyRequest):
    """
    Beautify and analyze log entries or stack traces.
    
    Takes raw log input and returns:
    - Cleaned and formatted log with syntax highlighting
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
                ).dict()
            )
        
        # Validate max_lines parameter
        if beautify_request.options.max_lines > settings.max_lines_limit:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    error="Max lines parameter too large",
                    details=f"Maximum allowed is {settings.max_lines_limit} lines",
                    code="MAX_LINES_EXCEEDED"
                ).dict()
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
            ).dict()
        )


@app.get("/")
async def root():
    """Root endpoint with basic service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
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