"""
📤 Hospital File Upload Department - Medical File Processing Routes

This is the file upload department of our hospital! Just like how a real hospital
processes different types of medical documents (lab reports, X-rays, patient files),
this module handles uploading and processing different types of log files.

Think of this like the hospital's medical records intake:
- /upload-log: Upload log files for analysis (like bringing medical records from another hospital)

🏆 HIGH SCHOOL EXPLANATION:
Like a school's document submission center where students can:
1. Upload their programming assignment files that have errors
2. System processes the files and finds the problems
3. Students get back detailed feedback on what went wrong
4. Files are kept on record for progress tracking

NOTE: This is the modular route structure. The route implementations will be
moved here from main.py during the refactoring process.
"""

from fastapi import APIRouter

# Create router for this department
router = APIRouter(prefix="/api/v1", tags=["upload"])


from fastapi import HTTPException, Request, File, UploadFile, Form
from datetime import datetime

from ...models import FileUploadResponse, FileUploadMetadata, ErrorResponse, LanguageEnum
from ...config_v2 import settings
from ...processor import LogProcessor

# Initialize the log processor
processor = LogProcessor()


@router.post("/upload-log", response_model=FileUploadResponse)
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
    📤 Upload and Process Log File - Like Submitting Medical Records! 📤
    
    This endpoint accepts log files and processes them through the same
    analysis pipeline as the text-based analyze endpoint. It's like
    submitting medical records to the hospital for analysis.
    
    Supported file formats: .log, .txt, .out, .err, and more
    """
    try:
        # Validate file size
        if file.size and file.size > settings.api.max_log_size:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    status="error",
                    message="File too large",
                    details=f"Maximum file size is {settings.api.max_log_size} bytes",
                    code="FILE_TOO_LARGE",
                    type="validation_error",
                    timestamp=datetime.now().timestamp(),
                    incident_id=None
                ).model_dump()
            )
        
        # Validate max_lines parameter
        if max_lines > settings.api.max_lines_limit:
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
        
        # Read file content
        try:
            content = await file.read()
            log_input = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            try:
                log_input = content.decode('latin1')
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail=ErrorResponse(
                        status="error",
                        message="File encoding not supported",
                        details="Could not decode file content. Please ensure file is text-based.",
                        code="ENCODING_ERROR",
                        type="validation_error",
                        timestamp=datetime.now().timestamp(),
                        incident_id=None
                    ).model_dump()
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    status="error",
                    message="Failed to read file",
                    details=str(e) if settings.debug else "Could not read uploaded file",
                    code="FILE_READ_ERROR",
                    type="server_error",
                    timestamp=datetime.now().timestamp(),
                    incident_id=None
                ).model_dump()
            )
        
        # Validate content isn't empty
        if not log_input.strip():
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    status="error",
                    message="Empty file",
                    details="Uploaded file appears to be empty",
                    code="EMPTY_FILE",
                    type="validation_error",
                    timestamp=datetime.now().timestamp(),
                    incident_id=None
                ).model_dump()
            )
        
        # Validate language parameter
        if language != "auto" and language not in [lang.value for lang in LanguageEnum]:
            language = "auto"  # Default to auto-detection
        
        # Process the log content using the same processor as analyze endpoint
        try:
            cleaned_log, summary, error_tags, metadata = processor.process_log(
                log_input=log_input,
                language=language,
                highlight=highlight,
                summarize=summarize,
                tags=tags,
                max_lines=max_lines
            )
        except Exception as processing_error:
            raise HTTPException(
                status_code=500,
                detail=ErrorResponse(
                    status="error",
                    message="Processing failed",
                    details=str(processing_error) if settings.debug else "Failed to process uploaded file",
                    code="PROCESSING_ERROR",
                    type="server_error",
                    timestamp=datetime.now().timestamp(),
                    incident_id=None
                ).model_dump()
            )
        
        # Build response
        return FileUploadResponse(
            cleaned_log=cleaned_log,
            summary=summary,
            tags=error_tags,
            metadata=FileUploadMetadata(
                filename=file.filename or "unknown",
                file_size=len(log_input),
                lines=len(log_input.split('\n')),
                language_detected=metadata.get("detected_language", language),
                processing_time_ms=int(metadata.get("processing_time", 0.0) * 1000),
                truncated=metadata.get("truncated", False)
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status="error",
                message="Upload processing failed",
                details=str(e) if settings.debug else "Failed to process file upload",
                code="UPLOAD_PROCESSING_ERROR",
                type="server_error",
                timestamp=datetime.now().timestamp(),
                incident_id=None
            ).model_dump()
        )