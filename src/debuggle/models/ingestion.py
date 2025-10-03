"""
🚀 Hospital Data Ingestion Department - Models for Large-Scale Log Processing

This is the data processing center of our hospital! Just like how a large hospital
has specialized systems for handling high volumes of patient data, lab results, and
medical records, we have sophisticated systems for processing massive amounts of
log data efficiently.

Think of this like the hospital's data processing center:
- BatchIngestionRequest: Setting up bulk processing of patient records
- StreamingIngestionRequest: Real-time monitoring of patient vitals
- IngestionJobResponse: Status report of data processing operations

🏆 HIGH SCHOOL EXPLANATION:
Like a school processing thousands of test papers:
1. Batch processing: Grade all papers together efficiently
2. Streaming: Grade papers as students turn them in
3. Job tracking: Keep track of grading progress and results
4. Statistics: Report on overall grading system performance
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


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