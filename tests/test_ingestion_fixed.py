"""
Comprehensive tests for ingestion.py module covering:
- Enum classes (IngestionSource, ProcessingPriority, IngestionStatus)
- IngestionJob dataclass
- StreamBuffer class
- IngestionEngine class with all methods
- Async operations and background services
- Job processing and queuing
- Error handling and edge cases
- Performance monitoring and metrics
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from dataclasses import asdict
import tempfile
import os

from src.debuggle.services.ingestion import (
    IngestionSource, ProcessingPriority, IngestionStatus,
    IngestionJob, StreamBuffer, IngestionEngine
)


class TestEnumClasses:
    """Test the enum classes used in ingestion module"""
    
    def test_ingestion_source_enum_values(self):
        """Test IngestionSource enum has all expected values"""
        expected_sources = [
            "file_upload", "streaming", "batch_upload", 
            "webhook", "api_direct", "websocket"
        ]
        
        sources = [source.value for source in IngestionSource]
        for expected in expected_sources:
            assert expected in sources
    
    def test_processing_priority_enum_values(self):
        """Test ProcessingPriority enum has all expected values"""
        expected_priorities = [
            "critical", "high", "normal", "low", "batch"
        ]
        
        priorities = [priority.value for priority in ProcessingPriority]
        for expected in expected_priorities:
            assert expected in priorities
    
    def test_ingestion_status_enum_values(self):
        """Test IngestionStatus enum has all expected values"""
        expected_statuses = [
            "queued", "processing", "completed", "failed", 
            "partial", "cancelled"
        ]
        
        statuses = [status.value for status in IngestionStatus]
        for expected in expected_statuses:
            assert expected in statuses
    
    def test_enum_string_conversion(self):
        """Test enum string conversion and equality"""
        assert IngestionSource.FILE_UPLOAD.value == "file_upload"
        assert ProcessingPriority.HIGH.value == "high"
        assert IngestionStatus.COMPLETED.value == "completed"


class TestIngestionJob:
    """Test IngestionJob dataclass functionality"""
    
    def test_ingestion_job_creation_minimal(self):
        """Test creating IngestionJob with minimal parameters"""
        job = IngestionJob(
            job_id="test_job",
            source=IngestionSource.FILE_UPLOAD
        )
        
        assert job.job_id == "test_job"
        assert job.source == IngestionSource.FILE_UPLOAD
        assert job.priority == ProcessingPriority.NORMAL
        assert job.status == IngestionStatus.QUEUED
        assert job.progress_percent == 0.0
        assert job.raw_content is None
        assert job.text_content is None
        assert job.file_path is None
        assert job.metadata == {}
        assert job.processed_logs == []
        assert job.failed_logs == []
        assert job.error_messages == []
        assert job.bytes_processed == 0
        assert job.lines_processed == 0
        assert job.processing_time_seconds == 0.0
        assert job.started_at is None
        assert job.completed_at is None
    
    def test_ingestion_job_creation_full(self):
        """Test creating IngestionJob with all parameters"""
        test_metadata = {"language": "python", "size": 1024}
        test_raw_content = b"Test log data"
        
        job = IngestionJob(
            job_id="full_job",
            source=IngestionSource.BATCH_UPLOAD,
            priority=ProcessingPriority.HIGH,
            text_content="Full test data",
            raw_content=test_raw_content,
            file_path="/tmp/test.log",
            metadata=test_metadata,
            progress_percent=25.0
        )
        
        assert job.job_id == "full_job"
        assert job.source == IngestionSource.BATCH_UPLOAD
        assert job.priority == ProcessingPriority.HIGH
        assert job.text_content == "Full test data"
        assert job.raw_content == test_raw_content
        assert job.file_path == "/tmp/test.log"
        assert job.metadata == test_metadata
        assert job.progress_percent == 25.0
    
    def test_ingestion_job_update_progress(self):
        """Test updating job progress"""
        job = IngestionJob("progress_test", IngestionSource.FILE_UPLOAD)
        
        initial_progress = job.progress_percent
        assert initial_progress == 0.0
        
        job.update_progress(50.0, "Half way done")
        
        assert job.progress_percent == 50.0
        assert "progress_messages" in job.metadata
        assert len(job.metadata["progress_messages"]) == 1
        
        message = job.metadata["progress_messages"][0]
        assert message["percent"] == 50.0
        assert message["message"] == "Half way done"
        assert "timestamp" in message
    
    def test_ingestion_job_update_progress_only_percent(self):
        """Test updating only progress percent"""
        job = IngestionJob("progress_test", IngestionSource.FILE_UPLOAD)
        
        job.update_progress(75.0)
        
        assert job.progress_percent == 75.0
        # When no message is provided, no progress_messages are added
        assert "progress_messages" not in job.metadata
    
    def test_ingestion_job_progress_bounds(self):
        """Test progress percent is bounded between 0 and 100"""
        job = IngestionJob("bounds_test", IngestionSource.FILE_UPLOAD)
        
        # Test upper bound
        job.update_progress(150.0)
        assert job.progress_percent == 100.0
        
        # Test lower bound
        job.update_progress(-25.0)
        assert job.progress_percent == 0.0
    
    def test_ingestion_job_timestamps(self):
        """Test that timestamps are set correctly"""
        before_creation = datetime.now()
        job = IngestionJob("time_test", IngestionSource.FILE_UPLOAD)
        after_creation = datetime.now()
        
        assert before_creation <= job.created_at <= after_creation
        assert job.started_at is None
        assert job.completed_at is None


class TestStreamBuffer:
    """Test StreamBuffer functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.buffer = StreamBuffer(max_size=1024, max_lines=10, flush_interval=1.0)
    
    def test_stream_buffer_initialization(self):
        """Test StreamBuffer initialization"""
        assert self.buffer.max_size == 1024
        assert self.buffer.max_lines == 10
        assert self.buffer.flush_interval == 1.0
        assert len(self.buffer.buffer) == 0
        assert self.buffer.current_size == 0
        assert self.buffer.total_bytes_buffered == 0
        assert self.buffer.total_lines_buffered == 0
        assert self.buffer.flush_count == 0
    
    @pytest.mark.asyncio
    async def test_stream_buffer_add_line_normal(self):
        """Test adding lines to buffer normally"""
        line1 = "First log line"
        line2 = "Second log line"
        
        result1 = await self.buffer.add_line(line1)
        assert result1 is False  # Should not need flush yet
        
        result2 = await self.buffer.add_line(line2)
        assert result2 is False  # Should not need flush yet
        
        assert len(self.buffer.buffer) == 2
        assert self.buffer.total_lines_buffered == 2
        assert self.buffer.current_size > 0
        assert self.buffer.total_bytes_buffered > 0
    
    @pytest.mark.asyncio
    async def test_stream_buffer_auto_flush_on_max_lines(self):
        """Test buffer auto-flushes when reaching max lines"""
        # Add exactly max_lines (10) lines
        for i in range(9):
            result = await self.buffer.add_line(f"Line {i}")
            assert result is False
        
        # The 10th line should trigger flush need
        result = await self.buffer.add_line("Line 9")
        assert result is True  # Should need flush now
        
        assert len(self.buffer.buffer) == 10
    
    @pytest.mark.asyncio
    async def test_stream_buffer_auto_flush_on_max_size(self):
        """Test buffer auto-flushes when reaching max size"""
        # Create a line that will exceed max_size when added multiple times
        large_line = "X" * 200  # 200 bytes per line
        
        # Add lines until we approach the limit
        for i in range(5):  # 5 * 200 = 1000 bytes, close to 1024 limit
            result = await self.buffer.add_line(large_line)
            if i < 4:
                assert result is False
        
        # This should exceed the size limit
        result = await self.buffer.add_line(large_line)
        assert result is True  # Should need flush now
    
    @pytest.mark.asyncio
    async def test_stream_buffer_flush_manual(self):
        """Test manual flush operation"""
        # Add some data
        await self.buffer.add_line("Line 1")
        await self.buffer.add_line("Line 2")
        await self.buffer.add_line("Line 3")
        
        assert len(self.buffer.buffer) == 3
        
        # Manual flush
        flushed_lines = await self.buffer.flush()
        
        assert len(flushed_lines) == 3
        assert "Line 1" in flushed_lines
        assert "Line 2" in flushed_lines
        assert "Line 3" in flushed_lines
        
        # Buffer should be empty after flush
        assert len(self.buffer.buffer) == 0
        assert self.buffer.current_size == 0
        assert self.buffer.flush_count == 1
    
    @pytest.mark.asyncio
    async def test_stream_buffer_flush_empty(self):
        """Test flushing an empty buffer"""
        flushed_lines = await self.buffer.flush()
        
        assert flushed_lines == []
        assert self.buffer.flush_count == 1
    
    def test_stream_buffer_get_stats(self):
        """Test getting buffer statistics"""
        # Add some data
        asyncio.run(self.buffer.add_line("Test line"))
        
        stats = self.buffer.get_stats()
        
        assert "current_lines" in stats
        assert "current_size_bytes" in stats
        assert "total_bytes_buffered" in stats
        assert "total_lines_buffered" in stats
        assert "flush_count" in stats
        assert "last_flush" in stats
        
        assert stats["current_lines"] == 1
        assert stats["current_size_bytes"] > 0
        assert stats["total_bytes_buffered"] > 0
        assert stats["total_lines_buffered"] == 1
        assert stats["flush_count"] == 0
    
    def test_stream_buffer_custom_parameters(self):
        """Test creating buffer with custom parameters"""
        custom_buffer = StreamBuffer(max_size=2048, max_lines=20, flush_interval=3.0)
        
        assert custom_buffer.max_size == 2048
        assert custom_buffer.max_lines == 20
        assert custom_buffer.flush_interval == 3.0


class TestIngestionEngine:
    """Test IngestionEngine core functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = IngestionEngine(max_concurrent_jobs=5, max_memory_mb=100)
    
    def test_ingestion_engine_initialization(self):
        """Test IngestionEngine initializes correctly"""
        assert self.engine.max_concurrent_jobs == 5
        assert self.engine.max_memory_mb == 100
        assert len(self.engine.jobs) == 0
        assert len(self.engine.active_jobs) == 0
        assert isinstance(self.engine.job_queues, dict)
        assert len(self.engine.job_queues) == len(ProcessingPriority)
        
        # Check all priority queues exist
        for priority in ProcessingPriority:
            assert priority in self.engine.job_queues
            assert isinstance(self.engine.job_queues[priority], asyncio.Queue)
    
    @pytest.mark.asyncio
    async def test_submit_job_success(self):
        """Test submitting a job successfully"""
        job_id = await self.engine.submit_job(
            source=IngestionSource.FILE_UPLOAD,
            content="Test log data",
            priority=ProcessingPriority.HIGH,
            metadata={"language": "python"}
        )
        
        assert job_id is not None
        assert job_id.startswith("job_")
        assert job_id in self.engine.jobs
        
        job = self.engine.jobs[job_id]
        assert job.source == IngestionSource.FILE_UPLOAD
        assert job.text_content == "Test log data"
        assert job.priority == ProcessingPriority.HIGH
        assert job.metadata["language"] == "python"
        assert job.status == IngestionStatus.QUEUED
    
    @pytest.mark.asyncio
    async def test_submit_job_with_raw_content(self):
        """Test submitting job with raw bytes content"""
        raw_data = b"Binary log data content"
        
        job_id = await self.engine.submit_job(
            source=IngestionSource.BATCH_UPLOAD,
            raw_content=raw_data
        )
        
        assert job_id in self.engine.jobs
        job = self.engine.jobs[job_id]
        assert job.raw_content == raw_data
        assert job.text_content is None
    
    @pytest.mark.asyncio
    async def test_submit_job_with_file_path(self):
        """Test submitting job with file path"""
        test_file_path = "/tmp/test_log.txt"
        
        job_id = await self.engine.submit_job(
            source=IngestionSource.BATCH_UPLOAD,
            file_path=test_file_path
        )
        
        assert job_id in self.engine.jobs
        job = self.engine.jobs[job_id]
        assert job.file_path == test_file_path
    
    def test_get_job_status_existing(self):
        """Test getting status of existing job"""
        # Create a job directly
        job = IngestionJob("test_job", IngestionSource.FILE_UPLOAD)
        self.engine.jobs["test_job"] = job
        
        retrieved_job = self.engine.get_job_status("test_job")
        
        assert retrieved_job is not None
        assert retrieved_job.job_id == "test_job"
        assert retrieved_job == job
    
    def test_get_job_status_nonexistent(self):
        """Test getting status of non-existent job"""
        job = self.engine.get_job_status("nonexistent_job")
        assert job is None
    
    def test_get_system_stats(self):
        """Test getting system statistics"""
        stats = self.engine.get_system_stats()
        
        assert isinstance(stats, dict)
        assert "active_jobs" in stats
        assert "queued_jobs" in stats
        assert "total_jobs" in stats
        assert "queue_sizes" in stats
        
        assert stats["active_jobs"] == 0
        assert stats["queued_jobs"] == 0
        assert stats["total_jobs"] == 0
        assert isinstance(stats["queue_sizes"], dict)
        
        # Check all priority queues are represented
        for priority in ProcessingPriority:
            assert priority.value in stats["queue_sizes"]
            assert stats["queue_sizes"][priority.value] == 0
    
    @pytest.mark.asyncio
    async def test_system_stats_after_job_submission(self):
        """Test system stats after submitting jobs"""
        # Submit a few jobs
        await self.engine.submit_job(IngestionSource.FILE_UPLOAD, content="Job 1")
        await self.engine.submit_job(IngestionSource.STREAMING, content="Job 2", priority=ProcessingPriority.HIGH)
        
        stats = self.engine.get_system_stats()
        
        assert stats["total_jobs"] == 2
        assert stats["queued_jobs"] == 2
        assert stats["queue_sizes"][ProcessingPriority.NORMAL.value] == 1
        assert stats["queue_sizes"][ProcessingPriority.HIGH.value] == 1
    
    @pytest.mark.asyncio
    async def test_shutdown(self):
        """Test engine shutdown"""
        # Mock background tasks and thread pools
        mock_task1 = AsyncMock()
        mock_task2 = AsyncMock()
        self.engine.background_tasks = [mock_task1, mock_task2]
        
        with patch('asyncio.gather', new_callable=AsyncMock) as mock_gather:
            with patch.object(self.engine.thread_pool, 'shutdown') as mock_thread_shutdown:
                with patch.object(self.engine.process_pool, 'shutdown') as mock_process_shutdown:
                    await self.engine.shutdown()
        
        assert self.engine.shutdown_event.is_set()
        mock_gather.assert_called_once()
        mock_thread_shutdown.assert_called_once_with(wait=True)
        mock_process_shutdown.assert_called_once_with(wait=True)


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = IngestionEngine()
    
    @pytest.mark.asyncio
    async def test_submit_job_with_no_content(self):
        """Test submitting job with no content"""
        job_id = await self.engine.submit_job(
            source=IngestionSource.FILE_UPLOAD
        )
        
        # Should still create job even with no content
        assert job_id in self.engine.jobs
        job = self.engine.jobs[job_id]
        assert job.text_content is None
        assert job.raw_content is None
        assert job.file_path is None
    
    def test_stream_buffer_with_very_long_line(self):
        """Test stream buffer handles very long lines gracefully"""
        buffer = StreamBuffer(max_size=1024, max_lines=10)
        very_long_line = "X" * 2000  # Larger than max_size
        
        # Should handle gracefully without crashing
        result = asyncio.run(buffer.add_line(very_long_line))
        assert isinstance(result, bool)
        assert len(buffer.buffer) == 1
        assert buffer.current_size >= 2000
    
    @pytest.mark.asyncio
    async def test_multiple_job_submissions(self):
        """Test submitting multiple jobs quickly"""
        job_ids = []
        
        # Submit multiple jobs in quick succession
        for i in range(10):
            job_id = await self.engine.submit_job(
                source=IngestionSource.FILE_UPLOAD,
                content=f"Test job {i}",
                priority=ProcessingPriority.NORMAL if i % 2 == 0 else ProcessingPriority.HIGH
            )
            job_ids.append(job_id)
        
        # All jobs should be unique and stored
        assert len(set(job_ids)) == 10  # All unique
        assert len(self.engine.jobs) == 10
        
        # Check queue distribution
        stats = self.engine.get_system_stats()
        assert stats["total_jobs"] == 10
        assert stats["queued_jobs"] == 10
        assert stats["queue_sizes"][ProcessingPriority.NORMAL.value] == 5
        assert stats["queue_sizes"][ProcessingPriority.HIGH.value] == 5
    
    def test_get_stats_with_empty_engine(self):
        """Test getting stats from empty engine"""
        stats = self.engine.get_system_stats()
        
        assert stats["active_jobs"] == 0
        assert stats["queued_jobs"] == 0
        assert stats["total_jobs"] == 0
        
        for priority in ProcessingPriority:
            assert stats["queue_sizes"][priority.value] == 0


class TestIngestionIntegration:
    """Test integration scenarios and workflows"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = IngestionEngine(max_concurrent_jobs=3, max_memory_mb=50)
    
    @pytest.mark.asyncio
    async def test_complete_job_workflow(self):
        """Test a complete job submission and tracking workflow"""
        # Submit job
        job_id = await self.engine.submit_job(
            source=IngestionSource.FILE_UPLOAD,
            content="Complete workflow test data",
            priority=ProcessingPriority.HIGH,
            metadata={"test_type": "integration", "expected_lines": 1}
        )
        
        # Check initial status
        job = self.engine.get_job_status(job_id)
        assert job is not None
        assert job.status == IngestionStatus.QUEUED
        assert job.progress_percent == 0.0
        
        # Update progress
        job.update_progress(50.0, "Processing started")
        assert job.progress_percent == 50.0
        
        # Update status manually (simulating processing)
        job.status = IngestionStatus.PROCESSING
        job.started_at = datetime.now()
        
        # Complete processing
        job.status = IngestionStatus.COMPLETED
        job.completed_at = datetime.now()
        job.progress_percent = 100.0
        job.lines_processed = 1
        job.bytes_processed = len("Complete workflow test data")
        
        # Verify final state
        final_job = self.engine.get_job_status(job_id)
        assert final_job.status == IngestionStatus.COMPLETED
        assert final_job.progress_percent == 100.0
        assert final_job.lines_processed == 1
        assert final_job.started_at is not None
        assert final_job.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_buffer_integration_with_engine(self):
        """Test StreamBuffer integration with IngestionEngine"""
        buffer = StreamBuffer(max_size=512, max_lines=5)
        
        # Add data to buffer
        lines = [
            "Error: Database connection failed",
            "Warning: High memory usage detected", 
            "Info: Processing user request",
            "Error: Authentication failed",
            "Debug: Cache miss for key 'user_123'"
        ]
        
        for line in lines:
            result = await buffer.add_line(line)
            
        # Buffer should be full now
        assert len(buffer.buffer) == 5
        
        # Flush buffer and submit to engine
        buffered_lines = await buffer.flush()
        content = "\n".join(buffered_lines)
        
        job_id = await self.engine.submit_job(
            source=IngestionSource.STREAMING,
            content=content,
            priority=ProcessingPriority.NORMAL,
            metadata={"buffer_flush": True, "line_count": len(buffered_lines)}
        )
        
        # Verify job was created with buffered content
        job = self.engine.get_job_status(job_id)
        assert job is not None
        assert job.text_content == content
        assert job.metadata["buffer_flush"] is True
        assert job.metadata["line_count"] == 5
        
        # Verify buffer was cleared
        assert len(buffer.buffer) == 0
        assert buffer.current_size == 0