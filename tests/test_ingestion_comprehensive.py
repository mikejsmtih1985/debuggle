"""
🎯 COMPREHENSIVE INGESTION ENGINE COVERAGE TESTS

This test suite is designed to boost ingestion.py coverage from 20% to 70%+ by testing:
- All enum classes and their behavior  
- IngestionJob creation, progress tracking, and state management
- StreamBuffer functionality including buffering, flushing, and overflow handling
- IngestionEngine initialization, job processing, and concurrent operations
- All processing methods (standard, batch, streaming)
- Background services (metrics collection, job cleanup)
- Error handling and edge cases throughout the system
- Resource management and memory limits

These tests cover the previously untested branches and critical error paths.
"""

import pytest
import asyncio
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
from collections import deque

from src.debuggle.services.ingestion import (
    IngestionSource, ProcessingPriority, IngestionStatus,
    IngestionJob, StreamBuffer, IngestionEngine
)
from src.debuggle.processor import LogProcessor


class TestEnumClasses:
    """Test all enum classes for completeness and behavior"""
    
    def test_ingestion_source_enum_values(self):
        """Test IngestionSource enum has all expected values"""
        expected_sources = [
            "api_upload", "web_interface", "streaming_websocket",
            "batch_file", "real_time_stream", "external_api",
            "log_aggregator", "monitoring_system"
        ]
        
        sources = [source.value for source in IngestionSource]
        for expected in expected_sources:
            assert expected in sources
    
    def test_processing_priority_enum_values(self):
        """Test ProcessingPriority enum has all expected values"""
        expected_priorities = [
            "critical", "high", "normal", "low", "background"
        ]
        
        priorities = [priority.value for priority in ProcessingPriority]
        for expected in expected_priorities:
            assert expected in priorities
    
    def test_ingestion_status_enum_values(self):
        """Test IngestionStatus enum has all expected values"""
        expected_statuses = [
            "queued", "processing", "completed", "failed",
            "cancelled", "retrying", "paused"
        ]
        
        statuses = [status.value for status in IngestionStatus]
        for expected in expected_statuses:
            assert expected in statuses
    
    def test_enum_string_conversion(self):
        """Test enum string conversion and equality"""
        assert str(IngestionSource.API_UPLOAD) == "api_upload"
        assert ProcessingPriority.HIGH == "high"
        assert IngestionStatus.PROCESSING == "processing"


class TestIngestionJob:
    """Test IngestionJob class functionality"""
    
    def test_ingestion_job_creation_minimal(self):
        """Test creating IngestionJob with minimal parameters"""
        job = IngestionJob(
            job_id="test_job",
            source=IngestionSource.API_UPLOAD,
            data="Test log data"
        )
        
        assert job.job_id == "test_job"
        assert job.source == IngestionSource.API_UPLOAD
        assert job.data == "Test log data"
        assert job.priority == ProcessingPriority.NORMAL  # default
        assert job.status == IngestionStatus.QUEUED  # default
        assert job.metadata == {}  # default
        assert job.progress_percent == 0.0  # default
        assert job.progress_message == ""  # default
        assert job.error_message is None  # default
        assert job.retry_count == 0  # default
        assert job.max_retries == 3  # default
        assert isinstance(job.created_at, datetime)
        assert job.started_at is None
        assert job.completed_at is None
    
    def test_ingestion_job_creation_full(self):
        """Test creating IngestionJob with all parameters"""
        test_metadata = {"language": "python", "size": 1024}
        
        job = IngestionJob(
            job_id="full_job",
            source=IngestionSource.BATCH_FILE,
            data="Full test data",
            priority=ProcessingPriority.HIGH,
            metadata=test_metadata,
            progress_percent=25.0,
            progress_message="Starting processing",
            max_retries=5
        )
        
        assert job.job_id == "full_job"
        assert job.source == IngestionSource.BATCH_FILE
        assert job.data == "Full test data"
        assert job.priority == ProcessingPriority.HIGH
        assert job.metadata == test_metadata
        assert job.progress_percent == 25.0
        assert job.progress_message == "Starting processing"
        assert job.max_retries == 5
    
    def test_ingestion_job_update_progress(self):
        """Test updating job progress"""
        job = IngestionJob("progress_test", IngestionSource.API_UPLOAD, "data")
        
        job.update_progress(50.0, "Half way done")
        
        assert job.progress_percent == 50.0
        assert job.progress_message == "Half way done"
        assert job.last_updated is not None
    
    def test_ingestion_job_update_progress_only_percent(self):
        """Test updating only progress percent"""
        job = IngestionJob("progress_test", IngestionSource.API_UPLOAD, "data")
        original_message = job.progress_message
        
        job.update_progress(75.0)
        
        assert job.progress_percent == 75.0
        assert job.progress_message == original_message  # unchanged
    
    def test_ingestion_job_timestamps(self):
        """Test that timestamps are set correctly"""
        before_creation = datetime.now()
        job = IngestionJob("time_test", IngestionSource.API_UPLOAD, "data")
        after_creation = datetime.now()
        
        assert before_creation <= job.created_at <= after_creation
        assert job.last_updated == job.created_at
        
        # Update progress and check last_updated changes
        old_updated = job.last_updated
        job.update_progress(10.0)
        
        assert job.last_updated > old_updated


class TestStreamBuffer:
    """Test StreamBuffer class functionality"""
    
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
        assert self.buffer.lines_added == 0
        assert self.buffer.last_flush is not None
    
    @pytest.mark.asyncio
    async def test_stream_buffer_add_line_normal(self):
        """Test adding lines to buffer normally"""
        line1 = "First log line"
        line2 = "Second log line"
        
        result1 = await self.buffer.add_line(line1)
        assert result1 is True
        assert len(self.buffer.buffer) == 1
        assert self.buffer.current_size == len(line1) + 1  # +1 for newline
        assert self.buffer.lines_added == 1
        
        result2 = await self.buffer.add_line(line2)
        assert result2 is True
        assert len(self.buffer.buffer) == 2
        assert self.buffer.lines_added == 2
    
    @pytest.mark.asyncio
    async def test_stream_buffer_auto_flush_on_max_lines(self):
        """Test buffer auto-flushes when reaching max lines"""
        # Add exactly max_lines (10) lines
        for i in range(10):
            result = await self.buffer.add_line(f"Line {i}")
            assert result is True
        
        assert len(self.buffer.buffer) == 10
        
        # Adding one more should trigger flush and return the lines
        with patch.object(self.buffer, 'flush', new_callable=AsyncMock) as mock_flush:
            mock_flush.return_value = []  # Simulate empty after flush
            result = await self.buffer.add_line("Line 10")
            
            assert result is True
            mock_flush.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_buffer_auto_flush_on_max_size(self):
        """Test buffer auto-flushes when reaching max size"""
        # Create a line that will exceed max_size when added
        large_line = "X" * 1000  # Larger than our 1024 max_size
        
        with patch.object(self.buffer, 'flush', new_callable=AsyncMock) as mock_flush:
            mock_flush.return_value = []
            result = await self.buffer.add_line(large_line)
            
            assert result is True
            mock_flush.assert_called_once()
    
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
        assert self.buffer.lines_added == 0
    
    @pytest.mark.asyncio
    async def test_stream_buffer_flush_empty(self):
        """Test flushing empty buffer"""
        flushed_lines = await self.buffer.flush()
        
        assert flushed_lines == []
        assert len(self.buffer.buffer) == 0
    
    def test_stream_buffer_get_stats(self):
        """Test getting buffer statistics"""
        # Add some data
        asyncio.run(self.buffer.add_line("Test line"))
        
        stats = self.buffer.get_stats()
        
        assert "current_lines" in stats
        assert "current_size" in stats
        assert "total_lines_processed" in stats
        assert "last_flush" in stats
        assert "max_size" in stats
        assert "max_lines" in stats
        
        assert stats["current_lines"] == 1
        assert stats["current_size"] > 0
        assert stats["total_lines_processed"] == 1
    
    def test_stream_buffer_custom_parameters(self):
        """Test StreamBuffer with custom parameters"""
        custom_buffer = StreamBuffer(
            max_size=2048,
            max_lines=50,
            flush_interval=10.0
        )
        
        assert custom_buffer.max_size == 2048
        assert custom_buffer.max_lines == 50
        assert custom_buffer.flush_interval == 10.0


class TestIngestionEngine:
    """Test IngestionEngine class functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_processor = Mock(spec=LogProcessor)
        self.engine = IngestionEngine(max_concurrent_jobs=5, max_memory_mb=100)
        # Inject mock processor
        self.engine.processor = self.mock_processor
    
    def test_ingestion_engine_initialization(self):
        """Test IngestionEngine initialization"""
        assert self.engine.max_concurrent_jobs == 5
        assert self.engine.max_memory_mb == 100
        assert len(self.engine.active_jobs) == 0
        assert len(self.engine.completed_jobs) == 0
        assert len(self.engine.job_queue) == 0
        assert self.engine.is_running is False
        assert self.engine.job_processor_task is None
        assert self.engine.metrics_task is None
        assert self.engine.cleanup_task is None
        assert isinstance(self.engine.executor, ThreadPoolExecutor)
    
    @pytest.mark.asyncio
    async def test_ingestion_engine_start_stop(self):
        """Test starting and stopping the ingestion engine"""
        # Start engine
        await self.engine.start()
        
        assert self.engine.is_running is True
        assert self.engine.job_processor_task is not None
        assert self.engine.metrics_task is not None
        assert self.engine.cleanup_task is not None
        
        # Stop engine
        await self.engine.stop()
        
        assert self.engine.is_running is False
        # Tasks should be cancelled and set to None
        assert self.engine.job_processor_task is None
        assert self.engine.metrics_task is None
        assert self.engine.cleanup_task is None
    
    def test_submit_job_success(self):
        """Test submitting a job successfully"""
        job_id = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data="Test log data",
            priority=ProcessingPriority.HIGH,
            metadata={"language": "python"}
        )
        
        assert job_id is not None
        assert isinstance(job_id, str)
        assert len(job_id) > 0
        
        # Job should be in queue
        assert len(self.engine.job_queue) == 1
        
        # Job should exist in active_jobs
        assert job_id in self.engine.active_jobs
        
        job = self.engine.active_jobs[job_id]
        assert job.source == IngestionSource.API_UPLOAD
        assert job.data == "Test log data"
        assert job.priority == ProcessingPriority.HIGH
        assert job.metadata == {"language": "python"}
    
    def test_submit_job_with_custom_id(self):
        """Test submitting job with custom job ID"""
        custom_id = "custom_job_123"
        
        job_id = self.engine.submit_job(
            source=IngestionSource.BATCH_FILE,
            data="Custom job data",
            job_id=custom_id
        )
        
        assert job_id == custom_id
        assert custom_id in self.engine.active_jobs
    
    def test_submit_job_duplicate_id(self):
        """Test submitting job with duplicate ID"""
        job_id = "duplicate_test"
        
        # Submit first job
        result1 = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data="First job",
            job_id=job_id
        )
        assert result1 == job_id
        
        # Submit second job with same ID
        result2 = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data="Second job",
            job_id=job_id
        )
        assert result2 is None  # Should return None for duplicate
    
    def test_get_job_status_existing(self):
        """Test getting status of existing job"""
        job_id = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data="Status test"
        )
        
        status = self.engine.get_job_status(job_id)
        
        assert status is not None
        assert status["job_id"] == job_id
        assert status["status"] == IngestionStatus.QUEUED
        assert "progress_percent" in status
        assert "created_at" in status
    
    def test_get_job_status_nonexistent(self):
        """Test getting status of non-existent job"""
        status = self.engine.get_job_status("nonexistent_job")
        
        assert status is None
    
    def test_cancel_job_success(self):
        """Test successfully cancelling a queued job"""
        job_id = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data="Cancel test"
        )
        
        result = self.engine.cancel_job(job_id)
        
        assert result is True
        
        # Job should be marked as cancelled
        job = self.engine.active_jobs[job_id]
        assert job.status == IngestionStatus.CANCELLED
    
    def test_cancel_job_nonexistent(self):
        """Test cancelling non-existent job"""
        result = self.engine.cancel_job("nonexistent_job")
        
        assert result is False
    
    def test_cancel_job_already_completed(self):
        """Test cancelling already completed job"""
        job_id = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data="Completed test"
        )
        
        # Mark job as completed
        job = self.engine.active_jobs[job_id]
        job.status = IngestionStatus.COMPLETED
        
        result = self.engine.cancel_job(job_id)
        
        assert result is False  # Cannot cancel completed job
    
    def test_list_jobs_all(self):
        """Test listing all jobs"""
        # Submit multiple jobs
        job1 = self.engine.submit_job(IngestionSource.API_UPLOAD, "Job 1")
        job2 = self.engine.submit_job(IngestionSource.BATCH_FILE, "Job 2")
        
        jobs = self.engine.list_jobs()
        
        assert len(jobs) == 2
        job_ids = [job["job_id"] for job in jobs]
        assert job1 in job_ids
        assert job2 in job_ids
    
    def test_list_jobs_by_status(self):
        """Test listing jobs filtered by status"""
        # Submit jobs and change their status
        job1 = self.engine.submit_job(IngestionSource.API_UPLOAD, "Job 1")
        job2 = self.engine.submit_job(IngestionSource.API_UPLOAD, "Job 2")
        
        # Mark one as processing
        self.engine.active_jobs[job1].status = IngestionStatus.PROCESSING
        
        queued_jobs = self.engine.list_jobs(status=IngestionStatus.QUEUED)
        processing_jobs = self.engine.list_jobs(status=IngestionStatus.PROCESSING)
        
        assert len(queued_jobs) == 1
        assert queued_jobs[0]["job_id"] == job2
        
        assert len(processing_jobs) == 1
        assert processing_jobs[0]["job_id"] == job1
    
    def test_get_engine_stats(self):
        """Test getting engine statistics"""
        # Submit some jobs
        self.engine.submit_job(IngestionSource.API_UPLOAD, "Job 1")
        self.engine.submit_job(IngestionSource.BATCH_FILE, "Job 2")
        
        stats = self.engine.get_stats()
        
        assert "total_jobs" in stats
        assert "active_jobs" in stats
        assert "completed_jobs" in stats
        assert "queued_jobs" in stats
        assert "processing_jobs" in stats
        assert "failed_jobs" in stats
        assert "memory_usage_mb" in stats
        assert "is_running" in stats
        assert "uptime_seconds" in stats
        
        assert stats["total_jobs"] == 2
        assert stats["active_jobs"] == 2
        assert stats["is_running"] is False  # Not started yet


class TestIngestionEngineJobProcessing:
    """Test IngestionEngine job processing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_processor = Mock(spec=LogProcessor)
        self.mock_processor.process_log.return_value = (
            "cleaned_log", "summary", ["tag1", "tag2"], {"language": "python"}
        )
        self.engine = IngestionEngine(max_concurrent_jobs=2)
        self.engine.processor = self.mock_processor
    
    @pytest.mark.asyncio
    async def test_process_standard_job(self):
        """Test processing a standard job"""
        job = IngestionJob(
            job_id="standard_test",
            source=IngestionSource.API_UPLOAD,
            data="Standard log data for processing"
        )
        
        await self.engine._process_standard_job(job)
        
        # Job should be completed
        assert job.status == IngestionStatus.COMPLETED
        assert job.progress_percent == 100.0
        assert job.completed_at is not None
        
        # Processor should have been called
        self.mock_processor.process_log.assert_called_once_with("Standard log data for processing")
    
    @pytest.mark.asyncio
    async def test_process_standard_job_with_error(self):
        """Test processing standard job with error"""
        self.mock_processor.process_log.side_effect = Exception("Processing failed")
        
        job = IngestionJob(
            job_id="error_test",
            source=IngestionSource.API_UPLOAD,
            data="Error prone data"
        )
        
        await self.engine._process_standard_job(job)
        
        # Job should be failed
        assert job.status == IngestionStatus.FAILED
        assert "Processing failed" in job.error_message
        assert job.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_process_batch_job(self):
        """Test processing a batch job"""
        # Create temporary file for batch processing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as temp_file:
            temp_file.write("Line 1: Error occurred\n")
            temp_file.write("Line 2: Warning message\n") 
            temp_file.write("Line 3: Info message\n")
            temp_file_path = temp_file.name
        
        try:
            job = IngestionJob(
                job_id="batch_test",
                source=IngestionSource.BATCH_FILE,
                data=temp_file_path,
                metadata={"file_path": temp_file_path}
            )
            
            await self.engine._process_batch_job(job)
            
            # Job should be completed
            assert job.status == IngestionStatus.COMPLETED
            assert job.progress_percent == 100.0
            
            # Processor should have been called for each line
            assert self.mock_processor.process_log.call_count == 3
        
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_process_batch_job_file_not_found(self):
        """Test batch job with non-existent file"""
        job = IngestionJob(
            job_id="file_not_found",
            source=IngestionSource.BATCH_FILE,
            data="/nonexistent/file.log"
        )
        
        await self.engine._process_batch_job(job)
        
        # Job should be failed
        assert job.status == IngestionStatus.FAILED
        assert "not found" in job.error_message.lower() or "no such file" in job.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_process_streaming_job(self):
        """Test processing a streaming job"""
        # Create a StreamBuffer with data
        buffer = StreamBuffer()
        await buffer.add_line("Stream line 1")
        await buffer.add_line("Stream line 2")
        
        job = IngestionJob(
            job_id="streaming_test",
            source=IngestionSource.STREAMING_WEBSOCKET,
            data=buffer
        )
        
        # Mock buffer.flush to return lines and then empty
        with patch.object(buffer, 'flush', new_callable=AsyncMock) as mock_flush:
            mock_flush.side_effect = [
                ["Stream line 1", "Stream line 2"],  # First flush returns data
                []  # Second flush returns empty (stream ended)
            ]
            
            await self.engine._process_streaming_job(job)
        
        # Job should be completed
        assert job.status == IngestionStatus.COMPLETED
        
        # Processor should have been called for each line
        assert self.mock_processor.process_log.call_count == 2
    
    @pytest.mark.asyncio
    async def test_job_processor_loop(self):
        """Test the main job processor loop"""
        # Submit a job
        job_id = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data="Loop test data"
        )
        
        # Start the engine temporarily
        self.engine.is_running = True
        
        # Mock _process_job to avoid actual processing
        with patch.object(self.engine, '_process_job', new_callable=AsyncMock) as mock_process:
            # Run one iteration of the job processor
            # We'll simulate stopping after one job
            original_is_running = self.engine.is_running
            
            async def stop_after_first_job(*args):
                self.engine.is_running = False
                return None
            
            mock_process.side_effect = stop_after_first_job
            
            await self.engine._job_processor()
            
            # Process job should have been called
            mock_process.assert_called_once_with(job_id)
    
    @pytest.mark.asyncio
    async def test_metrics_collector(self):
        """Test metrics collection background task"""
        # Add some jobs for metrics
        self.engine.submit_job(IngestionSource.API_UPLOAD, "Metrics test 1")
        self.engine.submit_job(IngestionSource.BATCH_FILE, "Metrics test 2")
        
        # Mock the update of metrics
        original_stats = self.engine.total_jobs_processed
        
        # Run one iteration of metrics collector
        self.engine.is_running = True
        
        # Create a task that will stop after one iteration
        async def run_one_iteration():
            await asyncio.sleep(0.1)  # Small delay to simulate real operation
            self.engine.is_running = False
        
        # Run metrics collector for a short time
        metrics_task = asyncio.create_task(self.engine._metrics_collector())
        stop_task = asyncio.create_task(run_one_iteration())
        
        await asyncio.gather(metrics_task, stop_task, return_exceptions=True)
        
        # Should have collected some metrics
        assert isinstance(self.engine.total_jobs_processed, int)
    
    @pytest.mark.asyncio
    async def test_cleanup_completed_jobs(self):
        """Test cleanup of completed jobs"""
        # Create some completed jobs
        old_job = IngestionJob("old_job", IngestionSource.API_UPLOAD, "old data")
        old_job.status = IngestionStatus.COMPLETED
        old_job.completed_at = datetime.now() - timedelta(hours=25)  # Older than 24h
        
        recent_job = IngestionJob("recent_job", IngestionSource.API_UPLOAD, "recent data")
        recent_job.status = IngestionStatus.COMPLETED
        recent_job.completed_at = datetime.now() - timedelta(hours=1)  # Recent
        
        self.engine.completed_jobs["old_job"] = old_job
        self.engine.completed_jobs["recent_job"] = recent_job
        
        await self.engine._cleanup_completed_jobs()
        
        # Old job should be removed, recent job should remain
        assert "old_job" not in self.engine.completed_jobs
        assert "recent_job" in self.engine.completed_jobs


class TestErrorHandling:
    """Test error handling throughout ingestion system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = IngestionEngine()
        self.engine.processor = Mock(spec=LogProcessor)
    
    def test_submit_job_with_invalid_data(self):
        """Test submitting job with invalid data"""
        # Submit job with None data
        job_id = self.engine.submit_job(
            source=IngestionSource.API_UPLOAD,
            data=None
        )
        
        # Should still create job but may fail during processing
        assert job_id is not None
        assert job_id in self.engine.active_jobs
    
    @pytest.mark.asyncio
    async def test_stream_buffer_with_very_long_line(self):
        """Test stream buffer handling extremely long lines"""
        buffer = StreamBuffer(max_size=100, max_lines=10)  # Small buffer
        
        # Add a line longer than max_size
        very_long_line = "X" * 200
        
        # Should handle gracefully (might flush or truncate)
        result = await buffer.add_line(very_long_line)
        
        # Should return boolean without crashing
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_engine_shutdown_with_active_jobs(self):
        """Test engine shutdown while jobs are active"""
        # Submit jobs
        job1 = self.engine.submit_job(IngestionSource.API_UPLOAD, "Job 1")
        job2 = self.engine.submit_job(IngestionSource.API_UPLOAD, "Job 2")
        
        # Mark as processing
        self.engine.active_jobs[job1].status = IngestionStatus.PROCESSING
        self.engine.active_jobs[job2].status = IngestionStatus.PROCESSING
        
        # Start and then stop engine
        await self.engine.start()
        await self.engine.stop()
        
        # Should shutdown gracefully without crashing
        assert self.engine.is_running is False
    
    def test_get_stats_with_empty_engine(self):
        """Test getting stats from empty engine"""
        stats = self.engine.get_stats()
        
        # Should return valid stats even when empty
        assert isinstance(stats, dict)
        assert stats["total_jobs"] == 0
        assert stats["active_jobs"] == 0
        assert stats["completed_jobs"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])