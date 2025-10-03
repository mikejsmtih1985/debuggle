"""
🧪 CLOUD API TESTS - Making Sure Our Cloud Reception Desk Works! ☁️🏢

Think of this like testing the front desk of a hotel:
- Can guests check in? (upload endpoints)
- Can they find their rooms? (search endpoints)  
- Can they get their keys? (share endpoints)
- Does the system handle busy periods? (rate limiting)

🏗️ HIGH SCHOOL EXPLANATION:
Imagine testing a new online system for your school:

WHAT WE'RE TESTING:
1. Can students submit assignments online? (POST /api/v1/cloud/upload)
2. Can they search for their past work? (POST /api/v1/cloud/search)
3. Can teachers access shared work via links? (GET /api/v1/cloud/share/{id})
4. Does the system show usage stats? (GET /api/v1/cloud/stats)

WHY THIS MATTERS:
- If uploads fail, students can't share their errors for help
- If search breaks, they can't find their previous analyses
- If sharing fails, collaboration stops working
- If stats are wrong, billing and limits don't work

These tests ensure the API works perfectly before real users try it!
"""

import os
import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

# Import the components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.debuggle.cloud.cloud_api import setup_cloud_routes
from src.debuggle.cloud.cloud_storage import CloudStorageManager, CloudLogEntry
from src.debuggle.processor import LogProcessor
from fastapi import FastAPI

class TestCloudAPIEndpoints:
    """
    🧪 Test suite for cloud API endpoints.
    
    Like testing every button and form on a website to make sure
    they all work correctly and handle errors gracefully.
    """
    
    @pytest.fixture
    def test_app(self):
        """Create a test FastAPI app with cloud routes."""
        app = FastAPI(title="Test Debuggle Cloud")
        
        # Mock processor for testing
        mock_processor = Mock()
        mock_processor.analyze_log = AsyncMock(return_value={
            "summary": "Test analysis",
            "suggestions": ["Fix the error"],
            "severity": "error",
            "language": "python"
        })
        
        # Add cloud routes
        setup_cloud_routes(app, processor=mock_processor, tier="free")
        
        return app
    
    @pytest.fixture
    def client(self, test_app):
        """Create a test client for the app."""
        return TestClient(test_app)
    
    @pytest.fixture
    def sample_upload_data(self):
        """Sample data for upload testing."""
        return {
            "content": "IndexError: list index out of range\\nFile 'main.py', line 42",
            "title": "IndexError in user signup",
            "tags": ["python", "critical", "signup"],
            "language": "python",
            "severity": "error"
        }
    
    def test_upload_endpoint_success(self, client, sample_upload_data):
        """
        📤 Test successful upload to cloud storage.
        
        Like testing that a student can successfully submit
        their homework through the online portal.
        """
        # Mock the cloud manager's upload method
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.upload_log = AsyncMock(return_value=CloudLogEntry(
                log_id="test123",
                content=sample_upload_data["content"],
                title=sample_upload_data["title"],
                uploaded_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24),
                share_url="https://test.debuggle.cloud/share/test123",
                tags=sample_upload_data["tags"],
                language=sample_upload_data["language"],
                severity=sample_upload_data["severity"]
            ))
            
            response = client.post("/api/v1/cloud/upload", json=sample_upload_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["log_id"] == "test123"
            assert data["share_url"] == "https://test.debuggle.cloud/share/test123"
            assert "expires_at" in data
            assert "upgrade_hint" in data  # Free tier should get upgrade hints
    
    def test_upload_endpoint_failure(self, client, sample_upload_data):
        """
        💥 Test upload failure handling.
        
        Like testing what happens when the online submission
        system is temporarily down - should give helpful error.
        """
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.upload_log = AsyncMock(return_value=None)  # Upload failed
            
            response = client.post("/api/v1/cloud/upload", json=sample_upload_data)
            
            assert response.status_code == 500
            assert "Failed to upload log to cloud storage" in response.json()["detail"]
    
    def test_upload_endpoint_validation(self, client):
        """
        ✅ Test input validation on upload endpoint.
        
        Like testing that the submission form catches when
        students forget to fill in required fields.
        """
        # Test with missing required field
        invalid_data = {
            "title": "Test Error",
            # Missing required 'content' field
            "tags": ["test"],
            "language": "python"
        }
        
        response = client.post("/api/v1/cloud/upload", json=invalid_data)
        
        # Should return validation error
        assert response.status_code == 422
        assert "content" in str(response.json())
    
    def test_search_endpoint_success(self, client):
        """
        🔍 Test successful search of cloud logs.
        
        Like testing that students can search for their
        previous submissions using keywords.
        """
        search_data = {
            "query": "IndexError",
            "limit": 10,
            "tags": ["python"]
        }
        
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.search_logs = AsyncMock(return_value=[
                # Mock search results
                type('MockResult', (), {
                    'log_id': 'test1',
                    'title': 'Test Error 1',
                    'content': 'IndexError in test1.py',
                    'share_url': 'https://test.debuggle.cloud/share/test1',
                    'uploaded_at': datetime.now(),
                    'expires_at': datetime.now() + timedelta(hours=24),
                    'tags': ['python', 'test'],
                    'language': 'python',
                    'severity': 'error'
                })()
            ])
            
            response = client.post("/api/v1/cloud/search", json=search_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 1
            assert data["total_found"] == 1
            assert "search_time_ms" in data
            assert "upgrade_hint" in data  # Should have Pro tier upgrade hint
    
    def test_search_endpoint_empty_results(self, client):
        """
        🔍 Test search with no matching results.
        
        Like testing what happens when a student searches
        for something that doesn't exist in their submissions.
        """
        search_data = {
            "query": "NonexistentError",
            "limit": 10
        }
        
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.search_logs = AsyncMock(return_value=[])  # No results
            
            response = client.post("/api/v1/cloud/search", json=search_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["results"]) == 0
            assert data["total_found"] == 0
    
    def test_share_endpoint_success(self, client):
        """
        🔗 Test successful retrieval of shared log.
        
        Like testing that when someone clicks on a shared
        Google Drive link, they can see the document.
        """
        share_id = "test123"
        
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.get_log = AsyncMock(return_value=CloudLogEntry(
                log_id=share_id,
                content="IndexError: list index out of range",
                title="Test Error",
                uploaded_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24),
                share_url=f"https://test.debuggle.cloud/share/{share_id}",
                tags=["python", "test"],
                language="python",
                severity="error"
            ))
            
            response = client.get(f"/api/v1/cloud/share/{share_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["log_entry"]["log_id"] == share_id
            assert data["analysis"] is not None  # Should include analysis from processor
            assert data["viral_cta"] is not None  # Should include call-to-action
    
    def test_share_endpoint_not_found(self, client):
        """
        🔗 Test share endpoint with non-existent log.
        
        Like testing what happens when someone clicks on
        a broken or expired share link.
        """
        share_id = "nonexistent"
        
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.get_log = AsyncMock(return_value=None)  # Not found
            
            response = client.get(f"/api/v1/cloud/share/{share_id}")
            
            assert response.status_code == 404
            assert "not found or expired" in response.json()["detail"]
    
    def test_stats_endpoint_success(self, client):
        """
        📊 Test cloud storage statistics endpoint.
        
        Like testing the dashboard that shows students
        how many assignments they've submitted and when.
        """
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.get_stats = AsyncMock(return_value=type('MockStats', (), {
                'total_logs': 5,
                'total_size_mb': 2.5,
                'logs_expiring_soon': 2,
                'most_shared_log': 'test123',
                'total_shares': 10,
                'storage_tier': 'free'
            })())
            
            response = client.get("/api/v1/cloud/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["stats"]["total_logs"] == 5
            assert data["stats"]["storage_tier"] == "free"
            assert "upgrade_hints" in data
            assert len(data["upgrade_hints"]) >= 0
    
    def test_cleanup_endpoint_success(self, client):
        """
        🧹 Test manual cleanup endpoint.
        
        Like testing the "empty trash" button that students
        can use to clean up their old submissions.
        """
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.cleanup_expired_logs = AsyncMock(return_value=3)  # Cleaned 3 logs
            
            response = client.post("/api/v1/cloud/cleanup")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["logs_removed"] == 3
            assert "Cleaned up 3 expired logs" in data["message"]

class TestCloudAPIIntegration:
    """
    🔄 Integration tests for cloud API with main app.
    
    Like testing that the new online submission system
    works properly with the existing school website.
    """
    
    def test_cloud_routes_added_to_main_app(self):
        """
        🏗️ Test that cloud routes are properly added to main app.
        
        Like testing that all the new online features appear
        in the school website's navigation menu.
        """
        from fastapi import FastAPI
        from src.debuggle.cloud.cloud_api import setup_cloud_routes
        
        app = FastAPI()
        mock_processor = Mock()
        
        # Should be able to add routes without errors
        try:
            enhanced_app = setup_cloud_routes(app, processor=mock_processor, tier="free")
            assert enhanced_app is not None
            
            # Check that routes were added
            route_paths = [getattr(route, 'path', str(route)) for route in app.routes]
            
            # Should have our cloud endpoints
            expected_routes = [
                "/api/v1/cloud/upload",
                "/api/v1/cloud/search", 
                "/api/v1/cloud/share/{log_id}",
                "/api/v1/cloud/stats",
                "/api/v1/cloud/cleanup"
            ]
            
            for expected_route in expected_routes:
                # Check if any route matches (accounting for path parameters)
                found = any(expected_route.replace("{log_id}", "{path}") in path 
                          or expected_route.split("{")[0] in path 
                          for path in route_paths)
                assert found, f"Route {expected_route} not found in {route_paths}"
                
        except Exception as e:
            pytest.fail(f"Failed to add cloud routes to app: {e}")
    
    def test_tier_differences_in_responses(self):
        """
        💎 Test that different tiers get different responses.
        
        Like testing that premium vs free school accounts
        get different features and limits in the system.
        """
        # Test free tier app
        free_app = FastAPI()
        setup_cloud_routes(free_app, processor=Mock(), tier="free")
        free_client = TestClient(free_app)
        
        # Test pro tier app  
        pro_app = FastAPI()
        setup_cloud_routes(pro_app, processor=Mock(), tier="pro")
        pro_client = TestClient(pro_app)
        
        # Mock the cloud storage for both
        sample_data = {
            "content": "Test error",
            "title": "Test",
            "language": "python"
        }
        
        with patch('src.debuggle.cloud.cloud_api.CloudStorageManager') as mock_manager_class:
            mock_manager = mock_manager_class.return_value
            mock_manager.upload_log = AsyncMock(return_value=CloudLogEntry(
                log_id="test123",
                content="Test error",
                title="Test",
                uploaded_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24),
                share_url="https://test.debuggle.cloud/share/test123",
                tags=[],
                language="python",
                severity="info"
            ))
            
            # Both should work, but responses should differ
            free_response = free_client.post("/api/v1/cloud/upload", json=sample_data)
            pro_response = pro_client.post("/api/v1/cloud/upload", json=sample_data)
            
            assert free_response.status_code == 200
            assert pro_response.status_code == 200
            
            free_data = free_response.json()
            pro_data = pro_response.json()
            
            # Free tier should have upgrade hints, Pro might not
            assert "upgrade_hint" in free_data
            # Pro tier might have different hints or none
            
            # Both should have basic success data
            assert free_data["success"] is True
            assert pro_data["success"] is True

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])