"""
🔬 Hospital Analysis Department - Error Diagnostic Routes

This is the analysis department of our hospital! Just like how a real hospital's
diagnostic department handles lab tests, X-rays, and medical analysis, this module
handles all error analysis and diagnostic endpoints.

Think of this like the hospital's diagnostic center:
- /analyze: Basic error analysis (like a routine blood test)
- /analyze-with-context: Advanced analysis with additional context (like a full MRI scan)

🏆 HIGH SCHOOL EXPLANATION:
Like a school's tutoring center where students bring their homework problems:
1. Student submits their coding problem (error log)
2. Tutor analyzes the problem and explains what's wrong
3. Student gets back explained solution with helpful hints
4. System keeps track of common problems to help future students
"""

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from ...models import AnalyzeRequest, AnalyzeResponse, AnalyzeMetadata, ErrorResponse
from ...config_v2 import settings
from ...processor import LogProcessor

# Create router for this department
router = APIRouter(prefix="/api/v1", tags=["analysis"])

# Initialize the log processor
processor = LogProcessor()


@router.post("/analyze", response_model=AnalyzeResponse)
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
    """
    try:
        # Step 1: Pre-examination checks - Like checking if a patient is too sick for outpatient care
        if len(analyze_request.log_input) > settings.api.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    status="error",
                    message="Log input too large",
                    details=f"Maximum size is {settings.api.max_log_size} characters",
                    code="INPUT_TOO_LARGE",
                    type="validation_error",
                    timestamp=datetime.now().timestamp(),
                    incident_id=None
                ).model_dump()
            )
        
        # Step 2: Check processing limits
        if analyze_request.options.max_lines > settings.api.max_lines_limit:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    status="error",
                    message="Max lines parameter too large",
                    details=f"Maximum allowed is {settings.api.max_lines_limit} lines",
                    code="MAX_LINES_EXCEEDED",
                    type="validation_error",
                    timestamp=datetime.now().timestamp(),
                    incident_id=None
                ).model_dump()
            )
        
        # Process the log
        try:
            cleaned_log, summary, tags, metadata = processor.process_log(
                log_input=analyze_request.log_input,
                language=analyze_request.language.value,
                highlight=analyze_request.options.highlight,
                summarize=analyze_request.options.summarize,
                tags=analyze_request.options.tags,
                max_lines=analyze_request.options.max_lines
            )
        except Exception as processing_error:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    status="error",
                    message="Processing failed", 
                    details=str(processing_error) if settings.debug else "Failed to process log input",
                    code="PROCESSING_ERROR",
                    type="server_error",
                    timestamp=datetime.now().timestamp(),
                    incident_id=None
                ).model_dump()
            )
        
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
                status="error",
                message="Processing failed",
                details=str(e) if settings.debug else "Failed to process log input",
                code="PROCESSING_ERROR",
                type="server_error",
                timestamp=datetime.now().timestamp(),
                incident_id=None
            ).model_dump()
        )


@router.post("/analyze-with-context")
async def analyze_with_context(request: Request, analyze_request: AnalyzeRequest):
    """
    🔬 Advanced Contextual Analysis - Like a Full Medical Workup!
    
    This is like going to a specialist who not only looks at your symptoms
    but also examines your medical history, family history, lifestyle, etc.
    for a more comprehensive diagnosis.
    """
    # For now, redirect to the main analyze endpoint
    # This can be enhanced later with additional context processing
    return await analyze_log(request, analyze_request)