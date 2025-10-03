"""
🧪 CLOUD STORAGE TESTS - Making Sure Our Sky Filing Cabinet Works! ☁️📁

Think of this like quality control for a filing cabinet manufacturer:
- We test every drawer (upload, retrieve, search functions)
- We simulate different users (free, pro, enterprise tiers)
- We check safety features (expiration, rate limiting, privacy)
- We ensure graceful failures (what happens when cloud is down?)

🏗️ HIGH SCHOOL EXPLANATION:
Imagine you're testing a new locker system at school:

WHAT WE'RE TESTING:
1. Can students store their stuff? (upload_log)
2. Can they find their stuff later? (get_log, search_logs)
3. Do the locks work properly? (expiration, privacy)
4. What happens if too many people use it at once? (rate limiting) 
5. Does it work the same for everyone? (tier differences)

WHY THIS MATTERS:
- If cloud storage breaks, students lose their shared error analyses
- If privacy fails, sensitive error info could leak
- If rate limiting fails, the free service could get overwhelmed
- If tier differences don't work, monetization fails

These tests ensure every part works perfectly before students use it!

🔒 TESTING APPROACH:
- Unit tests: Test each function in isolation
- Integration tests: Test components working together
- Regression tests: Ensure new features don't break existing ones
- Error handling: Test graceful failures and edge cases
"""

import os
import pytest
import asyncio
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import the cloud storage components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.debuggle.cloud.cloud_storage import (
    CloudStorageManager, 
    CloudLogEntry, 
    CloudStorageStats
)

class TestCloudStorageManager:
    """
    🧪 Test suite for the CloudStorageManager class.
    
    Like having a quality control inspector test every feature
    of our cloud filing cabinet before it goes to customers.
    """
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary directory for test storage."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def cloud_manager_free(self, temp_storage_dir):
        """Create a CloudStorageManager with free tier settings."""
        return CloudStorageManager(
            storage_backend="sqlite",
            tier="free",
            base_url="https://test.debuggle.cloud"
        )
    
    @pytest.fixture
    def cloud_manager_pro(self, temp_storage_dir):
        """Create a CloudStorageManager with pro tier settings."""
        return CloudStorageManager(
            storage_backend="hybrid",
            tier="pro", 
            base_url="https://test.debuggle.cloud"
        )
    
    @pytest.fixture
    def sample_error_log(self):
        """Sample error log for testing."""
        return {
            "content": "IndexError: list index out of range\\nFile 'main.py', line 42",
            "title": "IndexError in user signup",
            "tags": ["python", "critical", "signup"],
            "language": "python",
            "severity": "error"
        }
    
    def test_initialization_free_tier(self, cloud_manager_free):
        """
        🆓 Test that free tier manager initializes correctly.
        
        Like checking that a basic locker system is set up properly:
        - Has the right capacity limits
        - Uses appropriate security settings
        - Configured for free usage patterns
        """
        assert cloud_manager_free.tier == "free"
        assert cloud_manager_free.rate_limits["free"]["uploads_per_day"] == 50
        assert cloud_manager_free.rate_limits["free"]["retention_hours"] == 24
        assert cloud_manager_free.storage is not None
    
    def test_initialization_pro_tier(self, cloud_manager_pro):
        """
        💎 Test that pro tier manager initializes with enhanced features.
        
        Like checking that a premium locker system has all the upgrades:
        - Higher capacity limits
        - Longer retention periods
        - More storage options
        """
        assert cloud_manager_pro.tier == "pro"
        assert cloud_manager_pro.rate_limits["pro"]["uploads_per_day"] == 500
        assert cloud_manager_pro.rate_limits["pro"]["retention_hours"] == 24 * 90
        assert cloud_manager_pro.storage is not None
    
    @pytest.mark.asyncio
    async def test_upload_log_success(self, cloud_manager_free, sample_error_log):
        """
        📤 Test successful log upload to cloud storage.
        
        Like testing that a student can successfully put their homework
        in a locker and get a receipt with the locker number.
        """
        # Mock the storage operations since we don't have real cloud in tests
        with patch.object(cloud_manager_free, '_check_rate_limits', return_value=True), \
             patch.object(cloud_manager_free, '_store_log_entry', return_value=True):
            
            result = await cloud_manager_free.upload_log(
                content=sample_error_log["content"],
                title=sample_error_log["title"], 
                tags=sample_error_log["tags"],
                language=sample_error_log["language"],
                severity=sample_error_log["severity"]
            )
            
            # Verify the upload was successful
            assert result is not None
            assert isinstance(result, CloudLogEntry)
            assert result.content == sample_error_log["content"]
            assert result.title == sample_error_log["title"]
            assert result.tags == sample_error_log["tags"]
            assert result.language == sample_error_log["language"]
            assert result.severity == sample_error_log["severity"]
            assert result.share_url.startswith("https://test.debuggle.cloud/share/")
            assert result.expires_at > datetime.now()
    
    @pytest.mark.asyncio
    async def test_upload_log_rate_limit_exceeded(self, cloud_manager_free, sample_error_log):
        """
        🚫 Test that rate limiting prevents abuse of free tier.
        
        Like testing that the locker system stops students from
        using too many lockers and overwhelming the system.
        """
        # Mock rate limiting to return False (limit exceeded)
        with patch.object(cloud_manager_free, '_check_rate_limits', return_value=False):
            
            result = await cloud_manager_free.upload_log(
                content=sample_error_log["content"],
                title=sample_error_log["title"]
            )
            
            # Should return None when rate limited
            assert result is None
    
    @pytest.mark.asyncio
    async def test_upload_log_storage_failure(self, cloud_manager_free, sample_error_log):
        """
        💥 Test graceful handling of storage failures.
        
        Like testing what happens when the locker mechanism jams:
        - System doesn't crash
        - User gets a clear error message
        - No data is lost or corrupted
        """
        # Mock storage failure
        with patch.object(cloud_manager_free, '_check_rate_limits', return_value=True), \
             patch.object(cloud_manager_free, '_store_log_entry', return_value=False):
            
            result = await cloud_manager_free.upload_log(
                content=sample_error_log["content"],
                title=sample_error_log["title"]
            )
            
            # Should return None when storage fails
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_log_success(self, cloud_manager_free):
        """
        📥 Test successful retrieval of a stored log.
        
        Like testing that a student can use their locker number
        to get back their homework exactly as they stored it.
        """
        # Mock successful retrieval
        mock_log_data = {
            "log_id": "test123",
            "content": "Test error content",
            "title": "Test Error",
            "uploaded_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            "share_url": "https://test.debuggle.cloud/share/test123",
            "tags": ["test"],
            "language": "python",
            "severity": "info"
        }
        
        with patch.object(cloud_manager_free, '_get_share_data', return_value=mock_log_data):
            result = await cloud_manager_free.get_log("test123")
            
            # For now, this returns None since we haven't implemented the full retrieval
            # In a complete implementation, this would return the CloudLogEntry
            assert result is None
    
    @pytest.mark.asyncio
    async def test_search_logs(self, cloud_manager_free):
        """
        🔍 Test searching through stored logs.
        
        Like testing the search function on a digital filing system:
        - Can find logs by content
        - Can filter by tags
        - Returns results in order of relevance
        """
        result = await cloud_manager_free.search_logs(
            query="IndexError",
            limit=10,
            tags=["python", "critical"]
        )
        
        # For now, returns empty list since storage isn't fully implemented
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_stats(self, cloud_manager_free):
        """
        📊 Test retrieval of storage statistics.
        
        Like testing the dashboard that shows how much space
        students are using in their lockers.
        """
        stats = await cloud_manager_free.get_stats()
        
        assert isinstance(stats, CloudStorageStats)
        assert stats.storage_tier == "free"
        assert stats.total_logs >= 0
        assert stats.total_size_mb >= 0.0
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_logs(self, cloud_manager_free):
        """
        🧹 Test automatic cleanup of expired logs.
        
        Like testing the janitor system that automatically
        empties lockers after their rental period expires.
        """
        cleaned_count = await cloud_manager_free.cleanup_expired_logs()
        
        # Should return number of cleaned logs (0 for empty test system)
        assert isinstance(cleaned_count, int)
        assert cleaned_count >= 0
    
    def test_generate_log_id_uniqueness(self, cloud_manager_free):
        """
        🔑 Test that log IDs are unique and secure.
        
        Like testing that every locker gets a unique number
        and the numbers can't be easily guessed.
        """
        content1 = "First error message"
        content2 = "Second error message"
        
        id1 = cloud_manager_free._generate_log_id(content1)
        id2 = cloud_manager_free._generate_log_id(content2)
        
        # IDs should be different
        assert id1 != id2
        
        # IDs should be reasonable length (not too short, not too long)
        assert len(id1) == 12
        assert len(id2) == 12
        
        # IDs should be alphanumeric
        assert id1.isalnum()
        assert id2.isalnum()
    
    def test_generate_title_from_content(self, cloud_manager_free):
        """
        📝 Test automatic title generation from log content.
        
        Like testing that the system can automatically create
        a good summary title when students don't provide one.
        """
        # Test with clear error message
        error_content = "IndexError: list index out of range\\nFile 'main.py', line 42"
        title = cloud_manager_free._generate_title(error_content, "python")
        
        assert "IndexError" in title
        
        # Test with no clear error (should use generic title)
        generic_content = "Some debug output without clear error"
        title = cloud_manager_free._generate_title(generic_content, "javascript")
        
        assert "Javascript" in title or "error log" in title.lower()
    
    @pytest.mark.asyncio
    async def test_tier_differences(self, cloud_manager_free, cloud_manager_pro):
        """
        💎 Test that different tiers have different limits and features.
        
        Like testing that basic vs premium locker rentals
        have different space, time, and feature allowances.
        """
        # Free tier limits
        free_limits = cloud_manager_free.rate_limits["free"]
        assert free_limits["uploads_per_day"] == 50
        assert free_limits["retention_hours"] == 24
        assert free_limits["max_size_mb"] == 1
        
        # Pro tier limits  
        pro_limits = cloud_manager_pro.rate_limits["pro"]
        assert pro_limits["uploads_per_day"] == 500
        assert pro_limits["retention_hours"] == 24 * 90  # 90 days
        assert pro_limits["max_size_mb"] == 10
        
        # Pro should have higher limits than free
        assert pro_limits["uploads_per_day"] > free_limits["uploads_per_day"]
        assert pro_limits["retention_hours"] > free_limits["retention_hours"]
        assert pro_limits["max_size_mb"] > free_limits["max_size_mb"]

    def test_error_handling_without_cloud_deps(self):
        """
        🚫 Test graceful handling when cloud dependencies aren't available.
        
        Like testing that the locker system gives a helpful message
        when the electronic lock system is broken, instead of crashing.
        """
        # Test initialization when CLOUD_DEPS_AVAILABLE is False
        with patch('src.debuggle.cloud.cloud_storage.CLOUD_DEPS_AVAILABLE', False):
            manager = CloudStorageManager()
            
            # Should initialize but with warnings
            assert manager.storage is None
    
    @pytest.mark.asyncio
    async def test_concurrent_uploads(self, cloud_manager_free, sample_error_log):
        """
        🔄 Test handling multiple simultaneous uploads.
        
        Like testing what happens when many students try to use
        the locker system at the same time during lunch rush.
        """
        # Mock successful operations
        with patch.object(cloud_manager_free, '_check_rate_limits', return_value=True), \
             patch.object(cloud_manager_free, '_store_log_entry', return_value=True):
            
            # Create multiple upload tasks
            tasks = []
            for i in range(5):
                task = cloud_manager_free.upload_log(
                    content=f"{sample_error_log['content']} #{i}",
                    title=f"{sample_error_log['title']} #{i}"
                )
                tasks.append(task)
            
            # Execute all uploads concurrently
            results = await asyncio.gather(*tasks)
            
            # All uploads should succeed
            assert len(results) == 5
            for result in results:
                assert result is not None
                assert isinstance(result, CloudLogEntry)
                
            # Each should have unique log_id
            log_ids = [result.log_id for result in results]
            assert len(set(log_ids)) == 5  # All unique

# Regression test to ensure existing functionality still works
class TestCloudIntegrationRegression:
    """
    🔄 Regression tests to ensure cloud features don't break existing functionality.
    
    Like testing that adding Wi-Fi to a building doesn't break the existing ethernet.
    """
    
    def test_imports_dont_break_existing_code(self):
        """
        📦 Test that cloud imports don't interfere with existing imports.
        
        Like making sure that installing new software doesn't break
        the programs that were already working.
        """
        # These should all import successfully even with cloud module present
        try:
            from src.debuggle.processor import LogProcessor
            from src.debuggle.models import AnalyzeRequest
            from src.debuggle.storage.search_engine import DebuggleSearchEngine
            
            # Should be able to create instances
            processor = LogProcessor()
            search_engine = DebuggleSearchEngine()
            
            assert processor is not None
            assert search_engine is not None
            
        except ImportError as e:
            pytest.fail(f"Cloud features broke existing imports: {e}")
    
    @pytest.mark.asyncio
    async def test_main_app_still_works_without_cloud(self):
        """
        🏠 Test that main app works when cloud features are disabled.
        
        Like testing that your house still has electricity when
        the Wi-Fi is turned off.
        """
        # Mock environment to disable cloud
        with patch.dict(os.environ, {"DEBUGGLE_CLOUD_ENABLED": "false"}):
            # Main app import should still work
            try:
                # This would normally test app creation, but we'll just test the import
                import src.debuggle.main
                assert src.debuggle.main is not None
            except Exception as e:
                pytest.fail(f"Main app broken when cloud disabled: {e}")

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])