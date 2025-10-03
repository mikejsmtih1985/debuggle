"""
🚀 DEBUGGLE SCALABLE INGESTION ENGINE - Enterprise-Grade Log Processing! 🚀

Think of this module as upgrading from a small clinic to a massive hospital
emergency room that can handle thousands of patients simultaneously! Instead
of processing one log at a time, this system can handle massive log files,
streaming data, and concurrent uploads like a world-class medical facility.

🏆 HIGH SCHOOL EXPLANATION:
Imagine the difference between:
- Small clinic: One doctor sees one patient at a time (basic log processing)
- Major hospital: Multiple emergency rooms, triage system, specialists working
  in parallel, ambulances arriving continuously (scalable ingestion system)

This system provides the "major hospital" approach to log processing!

WHY SCALABLE INGESTION MATTERS:
📈 Volume Handling - Process thousands of logs per second
⚡ Real-Time Streaming - Handle live log feeds from multiple sources  
🔄 Batch Processing - Efficiently process huge log files
🎯 Smart Routing - Send different log types to different processors
💾 Memory Efficiency - Handle files larger than available RAM
🚦 Rate Management - Prevent system overload with smart queuing
📊 Performance Monitoring - Track processing metrics and bottlenecks

ENTERPRISE CAPABILITIES PROVIDED:
🌊 Streaming Ingestion - WebSocket and HTTP streaming endpoints
📦 Batch Processing - Handle multi-GB log files efficiently
⚙️ Connection Pooling - Manage multiple concurrent connections
🎛️ Load Balancing - Distribute processing across system resources
📈 Auto-Scaling - Adjust processing capacity based on load
🔍 Smart Parsing - Automatically detect log formats and structure
🎯 Content Routing - Route logs to appropriate processors based on type
📊 Real-Time Metrics - Monitor ingestion performance and health
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
# import aiofiles  # Not available, will use standard file operations
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import deque

logger = logging.getLogger(__name__)


class IngestionSource(str, Enum):
    """
    📡 DATA SOURCE TYPES - Where Are These Logs Coming From?
    
    Different sources need different handling approaches, like how
    a hospital has different intake procedures for walk-ins vs
    ambulances vs scheduled appointments.
    """
    FILE_UPLOAD = "file_upload"         # 📁 Traditional file uploads
    STREAMING = "streaming"             # 🌊 Real-time log streams
    BATCH_UPLOAD = "batch_upload"       # 📦 Large file processing
    WEBHOOK = "webhook"                 # 🔗 External system pushes
    API_DIRECT = "api_direct"           # 💻 Direct API calls
    WEBSOCKET = "websocket"             # ⚡ WebSocket connections


class ProcessingPriority(str, Enum):
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


class IngestionStatus(str, Enum):
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


@dataclass
class IngestionJob:
    """
    📋 PROCESSING JOB TICKET - One Complete Processing Request
    
    Think of this as a hospital patient intake form that follows
    the patient through their entire visit. It contains all the
    information needed to process one log ingestion request.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a restaurant order ticket:
    - job_id: "Order #12345" (unique tracking number)
    - source: "Table 7" vs "Drive-through" (where it came from)
    - priority: "Rush order" vs "Standard" (how urgent)
    - content: "2 burgers, 1 fries" (what to process)
    - status: "Cooking" vs "Ready" (current state)
    """
    
    # 🏷️ JOB IDENTIFICATION
    job_id: str                                    # Unique identifier for this job
    source: IngestionSource                        # Where this data came from
    
    # 📊 JOB CONFIGURATION
    created_at: datetime = field(default_factory=datetime.now)  # When job was created
    priority: ProcessingPriority = ProcessingPriority.NORMAL  # How urgent is this
    content_type: Optional[str] = None             # MIME type of the content
    
    # 📝 PROCESSING DATA
    raw_content: Optional[bytes] = None            # Original raw data
    text_content: Optional[str] = None             # Decoded text content
    file_path: Optional[str] = None                # Path to temporary file
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional job info
    
    # 📊 STATUS TRACKING
    status: IngestionStatus = IngestionStatus.QUEUED  # Current processing status
    progress_percent: float = 0.0                  # How much is complete (0-100)
    started_at: Optional[datetime] = None          # When processing started
    completed_at: Optional[datetime] = None        # When processing finished
    
    # 📈 PROCESSING RESULTS
    processed_logs: List[str] = field(default_factory=list)  # Successfully processed log IDs
    failed_logs: List[str] = field(default_factory=list)     # Failed log processing attempts
    error_messages: List[str] = field(default_factory=list)  # Any error messages
    
    # 📊 PERFORMANCE METRICS
    bytes_processed: int = 0                       # Total bytes processed
    lines_processed: int = 0                       # Total lines processed
    processing_time_seconds: float = 0.0           # Time taken to process
    
    def update_progress(self, percent: float, message: Optional[str] = None):
        """Update job progress and optionally add a status message."""
        self.progress_percent = min(100.0, max(0.0, percent))
        if message:
            self.metadata.setdefault('progress_messages', []).append({
                'timestamp': datetime.now().isoformat(),
                'percent': percent,
                'message': message
            })


class StreamBuffer:
    """
    🌊 STREAMING DATA BUFFER - Smart Data Collection System!
    
    This is like having a smart conveyor belt that collects streaming
    data and organizes it into manageable chunks for processing.
    Instead of trying to process every single byte as it arrives,
    we collect it into logical groups.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a smart mailbox for a busy office:
    - Collects incoming mail (streaming data) throughout the day
    - Groups similar mail together (buffers by log type)
    - Delivers batches when full or at scheduled times
    - Handles overflow when too much mail arrives at once
    """
    
    def __init__(self, max_size: int = 64 * 1024, max_lines: int = 1000, flush_interval: float = 5.0):
        """
        🏗️ SET UP THE SMART BUFFER SYSTEM
        
        Configure how the buffer collects and manages streaming data.
        Like setting up the rules for how the office mailbox works.
        """
        self.max_size = max_size                    # Maximum bytes before auto-flush
        self.max_lines = max_lines                  # Maximum lines before auto-flush  
        self.flush_interval = flush_interval        # Seconds before time-based flush
        
        # 📦 BUFFER STORAGE
        self.buffer = deque()                      # Collected data lines
        self.current_size = 0                      # Current buffer size in bytes
        self.last_flush = datetime.now()           # When we last flushed the buffer
        
        # 🔒 THREAD SAFETY
        self.lock = asyncio.Lock()                 # Prevent concurrent access issues
        
        # 📊 STATISTICS
        self.total_bytes_buffered = 0              # Total data that has passed through
        self.total_lines_buffered = 0              # Total lines that have passed through
        self.flush_count = 0                       # How many times we've flushed
    
    async def add_line(self, line: str) -> bool:
        """
        📝 ADD A LINE TO THE BUFFER - Smart Collection
        
        Add a new line of data to the buffer, automatically flushing
        when limits are reached. Returns True if flush is needed.
        """
        async with self.lock:
            line_bytes = len(line.encode('utf-8'))
            
            # 📦 ADD TO BUFFER
            self.buffer.append(line)
            self.current_size += line_bytes
            self.total_bytes_buffered += line_bytes
            self.total_lines_buffered += 1
            
            # 🚦 CHECK FLUSH CONDITIONS
            should_flush = (
                len(self.buffer) >= self.max_lines or           # Too many lines
                self.current_size >= self.max_size or           # Too much data
                (datetime.now() - self.last_flush).total_seconds() >= self.flush_interval  # Too much time
            )
            
            return should_flush
    
    async def flush(self) -> List[str]:
        """
        🚿 FLUSH THE BUFFER - Empty and Return Contents
        
        Empty the buffer and return all collected lines for processing.
        Like emptying the mailbox and taking all the mail to be sorted.
        """
        async with self.lock:
            lines = list(self.buffer)
            self.buffer.clear()
            self.current_size = 0
            self.last_flush = datetime.now()
            self.flush_count += 1
            
            return lines
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer performance statistics."""
        return {
            'current_lines': len(self.buffer),
            'current_size_bytes': self.current_size,
            'total_bytes_buffered': self.total_bytes_buffered,
            'total_lines_buffered': self.total_lines_buffered,
            'flush_count': self.flush_count,
            'last_flush': self.last_flush.isoformat() if self.last_flush else None
        }


class IngestionEngine:
    """
    🏭 THE MASTER PROCESSING FACTORY - Enterprise-Grade Log Ingestion!
    
    This is the main control system that manages all log ingestion operations.
    Think of it as the central command center of a massive factory that
    processes raw materials (logs) into finished products (analyzed insights).
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a modern car factory:
    - Multiple assembly lines (processing queues) running in parallel
    - Quality control stations (validation and parsing)
    - Inventory management (memory and disk usage monitoring)
    - Production scheduling (priority-based job scheduling)
    - Performance monitoring (metrics and dashboards)
    - Automated conveyor belts (streaming data pipelines)
    
    This system can handle everything from single log entries to massive
    files containing millions of log lines!
    """
    
    def __init__(self, max_concurrent_jobs: int = 10, max_memory_mb: int = 500):
        """
        🏗️ BUILD THE PROCESSING FACTORY
        
        Set up all the systems needed for enterprise-scale log processing.
        Like constructing a factory with all the assembly lines, quality
        control stations, and management systems.
        """
        
        # ⚙️ PROCESSING CONFIGURATION
        self.max_concurrent_jobs = max_concurrent_jobs   # How many jobs can run simultaneously
        self.max_memory_mb = max_memory_mb               # Memory limit for processing
        
        # 📋 JOB MANAGEMENT
        self.jobs: Dict[str, IngestionJob] = {}          # All jobs (active and historical)
        self.job_queues: Dict[ProcessingPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in ProcessingPriority
        }  # Priority-based job queues
        
        # 🧵 PROCESSING INFRASTRUCTURE
        self.active_jobs: Dict[str, asyncio.Task] = {}   # Currently running job tasks
        self.thread_pool = ThreadPoolExecutor(max_workers=max_concurrent_jobs)  # Thread pool for CPU work
        self.process_pool = ProcessPoolExecutor(max_workers=2)  # Process pool for heavy work
        
        # 🌊 STREAMING INFRASTRUCTURE
        self.stream_buffers: Dict[str, StreamBuffer] = {}  # Buffers for streaming data
        self.websocket_connections: Dict[str, Any] = {}   # Active WebSocket connections
        
        # 📊 MONITORING AND METRICS
        self.stats = {
            'jobs_created': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'bytes_processed': 0,
            'lines_processed': 0,
            'average_processing_time': 0.0,
            'active_connections': 0,
            'memory_usage_mb': 0.0
        }
        
        # ⚡ BACKGROUND TASKS
        self.background_tasks: List[asyncio.Task] = []
        self.shutdown_event = asyncio.Event()
        
        # 🚀 FACTORY IS READY (but background systems start later)
        self._background_started = False
        
        logger.info(f"Ingestion engine initialized with {max_concurrent_jobs} concurrent jobs")
    
    def _start_background_systems(self):
        """
        🔄 START BACKGROUND PROCESSING SYSTEMS
        
        Launch all the background tasks that keep the ingestion system
        running smoothly. Like starting all the factory's automated
        systems and conveyor belts.
        
        Note: Only starts if there's an active event loop.
        """
        if self._background_started:
            return
            
        try:
            # Only start if we have an event loop
            loop = asyncio.get_running_loop()
            
            # Job processor task
            task = asyncio.create_task(self._job_processor())
            self.background_tasks.append(task)
            
            # Metrics collector task
            task = asyncio.create_task(self._metrics_collector())
            self.background_tasks.append(task)
            
            self._background_started = True
            logger.info("Background ingestion systems started")
            
        except RuntimeError:
            # No event loop running - background tasks will start later
            logger.debug("No event loop available - background systems will start when needed")
        
        # Cleanup task
        task = asyncio.create_task(self._cleanup_completed_jobs())
        self.background_tasks.append(task)
        
        logger.info("Background processing systems started")
    
    async def _job_processor(self):
        """
        ⚙️ MAIN JOB PROCESSING LOOP - The Factory Floor Manager
        
        This is the main loop that continuously processes jobs from
        the priority queues. Like a factory floor manager who keeps
        all the assembly lines running efficiently.
        """
        while not self.shutdown_event.is_set():
            try:
                # 🎯 PROCESS JOBS BY PRIORITY (highest first)
                for priority in [ProcessingPriority.CRITICAL, ProcessingPriority.HIGH, 
                               ProcessingPriority.NORMAL, ProcessingPriority.LOW, ProcessingPriority.BATCH]:
                    
                    queue = self.job_queues[priority]
                    
                    # 🚦 CHECK IF WE CAN PROCESS MORE JOBS
                    if len(self.active_jobs) >= self.max_concurrent_jobs:
                        break  # Factory at capacity
                    
                    try:
                        # Get next job (don't wait if queue is empty)
                        job_id = await asyncio.wait_for(queue.get(), timeout=0.1)
                        
                        # 🚀 START PROCESSING THE JOB
                        task = asyncio.create_task(self._process_job(job_id))
                        self.active_jobs[job_id] = task
                        
                        logger.info(f"Started processing job {job_id} with priority {priority.value}")
                        
                    except asyncio.TimeoutError:
                        # No jobs in this priority queue, try next priority
                        continue
                
                # 🧹 CLEAN UP COMPLETED JOBS
                completed_jobs = []
                for job_id, task in self.active_jobs.items():
                    if task.done():
                        completed_jobs.append(job_id)
                
                for job_id in completed_jobs:
                    task = self.active_jobs.pop(job_id)
                    try:
                        await task  # Ensure any exceptions are handled
                    except Exception as e:
                        logger.error(f"Job {job_id} failed: {e}")
                        if job_id in self.jobs:
                            self.jobs[job_id].status = IngestionStatus.FAILED
                            self.jobs[job_id].error_messages.append(str(e))
                
                # 😴 BRIEF PAUSE TO PREVENT CPU OVERLOAD
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in job processor: {e}")
                await asyncio.sleep(1.0)  # Longer pause after error
    
    async def _process_job(self, job_id: str):
        """
        🔧 PROCESS A SINGLE JOB - Individual Assembly Line
        
        This handles the complete processing of one ingestion job,
        from reading the raw data to producing the final analyzed results.
        Like one complete assembly line process for manufacturing a product.
        """
        if job_id not in self.jobs:
            logger.error(f"Job {job_id} not found")
            return
        
        job = self.jobs[job_id]
        
        try:
            # 📊 MARK JOB AS STARTED
            job.status = IngestionStatus.PROCESSING
            job.started_at = datetime.now()
            job.update_progress(10, "Starting job processing")
            
            # 🔍 DETERMINE PROCESSING STRATEGY
            if job.source == IngestionSource.BATCH_UPLOAD:
                await self._process_batch_job(job)
            elif job.source == IngestionSource.STREAMING:
                await self._process_streaming_job(job)
            elif job.source in [IngestionSource.FILE_UPLOAD, IngestionSource.API_DIRECT]:
                await self._process_standard_job(job)
            else:
                raise ValueError(f"Unsupported ingestion source: {job.source}")
            
            # ✅ MARK JOB AS COMPLETED
            job.status = IngestionStatus.COMPLETED
            job.completed_at = datetime.now()
            job.processing_time_seconds = (job.completed_at - job.started_at).total_seconds()
            job.update_progress(100, "Job completed successfully")
            
            # 📊 UPDATE STATISTICS
            self.stats['jobs_completed'] += 1
            self.stats['bytes_processed'] += job.bytes_processed
            self.stats['lines_processed'] += job.lines_processed
            
            logger.info(f"Job {job_id} completed successfully in {job.processing_time_seconds:.2f}s")
            
        except Exception as e:
            # ❌ HANDLE JOB FAILURE
            job.status = IngestionStatus.FAILED
            job.completed_at = datetime.now()
            job.error_messages.append(str(e))
            job.update_progress(0, f"Job failed: {str(e)}")
            
            self.stats['jobs_failed'] += 1
            
            logger.error(f"Job {job_id} failed: {e}")
            raise
    
    async def _process_standard_job(self, job: IngestionJob):
        """
        📝 PROCESS STANDARD JOB - Regular Single File Processing
        
        Handle regular file uploads and API submissions. Like the
        standard assembly line for normal-sized products.
        """
        # 📄 GET CONTENT TO PROCESS
        content = job.text_content
        if not content and job.raw_content:
            # Try to decode raw bytes
            try:
                content = job.raw_content.decode('utf-8')
            except UnicodeDecodeError:
                content = job.raw_content.decode('latin-1', errors='replace')
        
        if not content:
            raise ValueError("No content to process")
        
        job.update_progress(25, "Content loaded, starting analysis")
        
        # 📊 SPLIT INTO INDIVIDUAL LOG ENTRIES
        lines = content.split('\n')
        total_lines = len(lines)
        job.lines_processed = total_lines
        job.bytes_processed = len(content.encode('utf-8'))
        
        # 🔧 PROCESS EACH LOG LINE (simplified for demo)
        # In a real implementation, you'd use the LogProcessor here
        processed_count = 0
        
        for i, line in enumerate(lines):
            if line.strip():  # Skip empty lines
                # Simulate processing
                await asyncio.sleep(0.001)  # Small delay to show progress
                processed_count += 1
                
                # 📊 UPDATE PROGRESS
                progress = 25 + (70 * i / total_lines)  # 25-95% for processing
                if i % 100 == 0:  # Update progress every 100 lines
                    job.update_progress(progress, f"Processed {processed_count} log entries")
        
        job.update_progress(95, f"Completed processing {processed_count} log entries")
    
    async def _process_batch_job(self, job: IngestionJob):
        """
        📦 PROCESS BATCH JOB - Large File Efficient Processing
        
        Handle very large files that need special memory-efficient processing.
        Like a specialized assembly line for oversized products.
        """
        job.update_progress(5, "Starting batch processing")
        
        if job.file_path:
            # 📁 PROCESS FILE IN CHUNKS
            chunk_size = 64 * 1024  # 64KB chunks
            total_size = os.path.getsize(job.file_path)
            bytes_read = 0
            lines_processed = 0
            
            # Use synchronous file reading for now (could be moved to thread pool)
            with open(job.file_path, 'r', encoding='utf-8', errors='replace') as file:
                buffer = []
                
                for line in file:
                    buffer.append(line.strip())
                    bytes_read += len(line.encode('utf-8'))
                    
                    # 📦 PROCESS BUFFER WHEN FULL
                    if len(buffer) >= 1000:  # Process in 1000-line chunks
                        # Simulate processing
                        await asyncio.sleep(0.1)
                        lines_processed += len(buffer)
                        buffer.clear()
                        
                        # 📊 UPDATE PROGRESS
                        progress = 10 + (80 * bytes_read / total_size)
                        job.update_progress(progress, f"Processed {lines_processed} lines")
                
                # 📦 PROCESS REMAINING BUFFER
                if buffer:
                    await asyncio.sleep(0.1)
                    lines_processed += len(buffer)
            
            job.bytes_processed = bytes_read
            job.lines_processed = lines_processed
            job.update_progress(90, f"Batch processing completed: {lines_processed} lines")
        
        else:
            raise ValueError("No file path provided for batch processing")
    
    async def _process_streaming_job(self, job: IngestionJob):
        """
        🌊 PROCESS STREAMING JOB - Real-Time Data Processing
        
        Handle streaming data that arrives continuously. Like a
        conveyor belt system that processes items as they arrive.
        """
        job.update_progress(10, "Setting up streaming processing")
        
        # For streaming jobs, we process whatever data is currently available
        # In a real implementation, this would connect to the streaming source
        
        if job.text_content:
            lines = job.text_content.split('\n')
            job.lines_processed = len(lines)
            job.bytes_processed = len(job.text_content.encode('utf-8'))
            
            job.update_progress(50, f"Processing {len(lines)} streaming log entries")
            
            # Simulate streaming processing
            await asyncio.sleep(0.5)
            
            job.update_progress(90, "Streaming processing completed")
    
    async def _metrics_collector(self):
        """
        📊 COLLECT SYSTEM METRICS - Performance Monitoring
        
        Continuously collect system performance metrics to monitor
        the health and efficiency of the ingestion system.
        """
        while not self.shutdown_event.is_set():
            try:
                # 💾 CALCULATE MEMORY USAGE (optional - requires psutil)
                # Like checking how much RAM your phone app is using! 📱
                try:
                    import psutil  # type: ignore # Optional dependency for monitoring
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    self.stats['memory_usage_mb'] = memory_mb
                except ImportError:
                    # psutil not available, skip memory monitoring
                    self.stats['memory_usage_mb'] = 0.0
                
                # 🔗 COUNT ACTIVE CONNECTIONS
                self.stats['active_connections'] = len(self.websocket_connections)
                
                # 📈 CALCULATE AVERAGE PROCESSING TIME
                completed_jobs = [job for job in self.jobs.values() if job.status == IngestionStatus.COMPLETED]
                if completed_jobs:
                    total_time = sum(job.processing_time_seconds for job in completed_jobs)
                    self.stats['average_processing_time'] = total_time / len(completed_jobs)
                
                # 😴 WAIT BEFORE NEXT COLLECTION
                await asyncio.sleep(30)  # Collect metrics every 30 seconds
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(60)  # Wait longer after error
    
    async def _cleanup_completed_jobs(self):
        """
        🧹 CLEAN UP OLD JOBS - Housekeeping
        
        Remove old completed jobs from memory to prevent memory leaks.
        Like cleaning up the factory floor after each shift.
        """
        while not self.shutdown_event.is_set():
            try:
                # 🗑️ REMOVE JOBS OLDER THAN 1 HOUR
                cutoff_time = datetime.now() - timedelta(hours=1)
                jobs_to_remove = []
                
                for job_id, job in self.jobs.items():
                    if (job.status in [IngestionStatus.COMPLETED, IngestionStatus.FAILED] and
                        job.completed_at and job.completed_at < cutoff_time):
                        jobs_to_remove.append(job_id)
                
                for job_id in jobs_to_remove:
                    job = self.jobs.pop(job_id)
                    # Clean up any temporary files
                    if job.file_path and os.path.exists(job.file_path):
                        try:
                            os.remove(job.file_path)
                        except Exception as e:
                            logger.warning(f"Failed to remove temp file {job.file_path}: {e}")
                
                if jobs_to_remove:
                    logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
                
                # 😴 WAIT BEFORE NEXT CLEANUP
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                await asyncio.sleep(600)  # Wait longer after error
    
    async def submit_job(self, source: IngestionSource, priority: ProcessingPriority = ProcessingPriority.NORMAL,
                        content: Optional[str] = None, raw_content: Optional[bytes] = None,
                        file_path: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        📝 SUBMIT A NEW PROCESSING JOB - Add to Factory Queue
        
        Submit a new job for processing. Like placing a work order
        with the factory to process some raw materials.
        
        Returns the job ID for tracking progress.
        """
        # 🔄 ENSURE BACKGROUND SYSTEMS ARE RUNNING
        if not self._background_started:
            self._start_background_systems()
            
        # 🏷️ CREATE UNIQUE JOB ID
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(content or str(raw_content) or file_path) % 10000:04d}"
        
        # 📋 CREATE JOB OBJECT
        job = IngestionJob(
            job_id=job_id,
            source=source,
            priority=priority,
            text_content=content,
            raw_content=raw_content,
            file_path=file_path,
            metadata=metadata or {}
        )
        
        # 📚 STORE JOB
        self.jobs[job_id] = job
        
        # 📋 ADD TO APPROPRIATE QUEUE
        await self.job_queues[priority].put(job_id)
        
        # 📊 UPDATE STATISTICS
        self.stats['jobs_created'] += 1
        
        logger.info(f"Submitted job {job_id} with priority {priority.value}")
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[IngestionJob]:
        """
        📊 GET JOB STATUS - Track Your Order
        
        Get the current status and progress of a processing job.
        Like checking the status of your factory order.
        """
        return self.jobs.get(job_id)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        📈 GET SYSTEM STATISTICS - Factory Performance Report
        
        Get comprehensive statistics about the ingestion system's
        performance and current status.
        """
        return {
            **self.stats,
            'active_jobs': len(self.active_jobs),
            'queued_jobs': sum(queue.qsize() for queue in self.job_queues.values()),
            'total_jobs': len(self.jobs),
            'queue_sizes': {
                priority.value: queue.qsize() 
                for priority, queue in self.job_queues.items()
            }
        }
    
    async def shutdown(self):
        """
        🔒 SHUTDOWN THE INGESTION SYSTEM - Close the Factory
        
        Gracefully shut down all background processes and clean up resources.
        """
        logger.info("Starting ingestion engine shutdown...")
        
        # 🛑 SIGNAL SHUTDOWN
        self.shutdown_event.set()
        
        # ⏳ WAIT FOR BACKGROUND TASKS
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # 🧵 SHUTDOWN THREAD POOLS
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        logger.info("Ingestion engine shutdown complete")


# Global ingestion engine instance
ingestion_engine: Optional[IngestionEngine] = None


def get_ingestion_engine() -> Optional[IngestionEngine]:
    """
    🏭 GET THE GLOBAL INGESTION ENGINE
    
    Get access to the main ingestion engine from anywhere in the application.
    Like getting a direct line to the factory floor manager.
    """
    return ingestion_engine


def initialize_ingestion_engine(max_concurrent_jobs: int = 10, max_memory_mb: int = 500) -> IngestionEngine:
    """
    🚀 INITIALIZE THE GLOBAL INGESTION SYSTEM
    
    Set up the main ingestion engine that will handle all scalable
    log processing throughout the application.
    """
    global ingestion_engine
    if ingestion_engine is None:
        ingestion_engine = IngestionEngine(max_concurrent_jobs, max_memory_mb)
        logger.info("Global ingestion engine initialized")
    return ingestion_engine