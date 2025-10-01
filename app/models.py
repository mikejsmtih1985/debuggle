from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class LanguageEnum(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    AUTO = "auto"


class BeautifyOptions(BaseModel):
    """Options for log beautification."""
    highlight: bool = Field(default=True, description="Apply syntax highlighting")
    summarize: bool = Field(default=True, description="Generate error summary")
    tags: bool = Field(default=True, description="Generate error tags")
    max_lines: int = Field(default=1000, ge=1, le=5000, description="Maximum lines to process")


class BeautifyRequest(BaseModel):
    """Request model for log beautification."""
    log_input: str = Field(..., min_length=1, max_length=50000, description="Raw log or stack trace")
    language: LanguageEnum = Field(default=LanguageEnum.AUTO, description="Programming language")
    options: BeautifyOptions = Field(default_factory=BeautifyOptions, description="Processing options")
    
    @validator('log_input')
    def validate_log_input(cls, v):
        if not v.strip():
            raise ValueError('log_input cannot be empty or whitespace only')
        return v


class BeautifyMetadata(BaseModel):
    """Metadata about the processing."""
    lines: int = Field(..., description="Number of lines processed")
    language_detected: str = Field(..., description="Detected or specified language")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    truncated: bool = Field(default=False, description="Whether input was truncated")


class BeautifyResponse(BaseModel):
    """Response model for log beautification."""
    cleaned_log: str = Field(..., description="Beautified and formatted log")
    summary: Optional[str] = Field(None, description="Plain English error explanation")
    tags: List[str] = Field(default_factory=list, description="Error category tags")
    metadata: BeautifyMetadata = Field(..., description="Processing metadata")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class TierFeature(BaseModel):
    """Individual tier feature."""
    name: str = Field(..., description="Tier name")
    icon: str = Field(..., description="Tier icon")
    features: List[str] = Field(..., description="Available features")


class TiersResponse(BaseModel):
    """Available tiers response."""
    tiers: List[TierFeature] = Field(..., description="Available service tiers")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")