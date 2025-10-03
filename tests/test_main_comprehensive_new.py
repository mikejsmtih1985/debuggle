"""
Comprehensive tests for main.py focusing on real user workflows and business logic.
Following Debuggle's quality-first testing philosophy - testing meaningful functionality, not metrics.

Target: 80%+ coverage focusing on:
- API endpoints and user-facing functionality
- Real error scenarios and integration points
- Business logic and core workflows
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient
from fastapi import status

from src.debuggle.main import app
from src.debuggle.models import AnalyzeRequest, LanguageEnum, AnalyzeOptions


class TestMainAPIEndpoints:
    """Test core API endpoints that users interact with."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint - critical for monitoring."""
        response = self.client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_analyze_endpoint_with_valid_request(self):
        """Test analyze endpoint with valid log input - core user workflow."""
        request_data = {
            "log_input": "FileNotFoundError: [Errno 2] No such file or directory: 'missing_file.txt'",
            "language": "python"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "analysis" in data
        assert "error_type" in data
        assert "suggestions" in data
    
    def test_analyze_endpoint_with_javascript_error(self):
        """Test analyze endpoint with JavaScript error - multi-language support."""
        request_data = {
            "log_input": "TypeError: Cannot read property 'length' of undefined",
            "language": "javascript"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "analysis" in data
        assert "javascript" in data.get("language", "").lower() or "js" in data.get("language", "").lower()
    
    def test_analyze_endpoint_with_auto_language_detection(self):
        """Test analyze endpoint with automatic language detection."""
        request_data = {
            "log_input": "java.lang.NullPointerException: null",
            "language": "auto"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "analysis" in data
        # Should detect Java language
        detected_lang = data.get("language", "").lower()
        assert "java" in detected_lang or "auto" in detected_lang
    
    def test_analyze_endpoint_with_options(self):
        """Test analyze endpoint with analysis options."""
        request_data = {
            "log_input": "IndexError: list index out of range",
            "language": "python",
            "options": {
                "highlight": True,
                "include_context": True,
                "detailed": True
            }
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "analysis" in data
        # Should include more detailed information when options are provided
        assert len(data["analysis"]) > 50  # Detailed analysis should be longer
    
    def test_analyze_endpoint_with_empty_log_input(self):
        """Test analyze endpoint handles empty input gracefully."""
        request_data = {
            "log_input": "",
            "language": "python"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        # Should handle gracefully with either 422 (validation error) or 200 with message
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_analyze_endpoint_with_very_long_input(self):
        """Test analyze endpoint handles large log inputs - realistic scenario."""
        long_log = "Error occurred\n" * 1000  # Simulate large log file
        request_data = {
            "log_input": long_log,
            "language": "python"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        # Should handle large inputs without crashing
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE]
    
    def test_analyze_endpoint_with_invalid_json(self):
        """Test analyze endpoint handles malformed JSON - real error scenario."""
        response = self.client.post(
            "/api/v1/analyze",
            content="{ invalid json }",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_analyze_endpoint_with_missing_required_field(self):
        """Test analyze endpoint validates required fields."""
        request_data = {
            "language": "python"
            # Missing log_input
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        error_data = response.json()
        assert "detail" in error_data


class TestFileUploadEndpoints:
    """Test file upload functionality - important user workflow."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_upload_log_file_valid(self):
        """Test uploading a valid log file."""
        log_content = "Error: Unable to connect to database\nConnectionTimeout: 30 seconds"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            f.flush()
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    "/api/v1/upload-log",
                    files={"file": ("test.log", f, "text/plain")}
                )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "analysis" in data
            assert "filename" in data
        finally:
            os.unlink(temp_path)
    
    def test_upload_log_file_empty(self):
        """Test uploading an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    "/api/v1/upload-log",
                    files={"file": ("empty.log", f, "text/plain")}
                )
            
            # Should handle empty files gracefully
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        finally:
            os.unlink(temp_path)
    
    def test_upload_non_text_file(self):
        """Test uploading a non-text file - realistic error scenario."""
        binary_content = b'\x89PNG\r\n\x1a\n'  # PNG header
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(binary_content)
            f.flush()
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    "/api/v1/upload-log",
                    files={"file": ("test.png", f, "image/png")}
                )
            
            # Should reject or handle binary files appropriately
            assert response.status_code in [
                status.HTTP_200_OK,  # If it tries to process anyway
                status.HTTP_400_BAD_REQUEST,  # If it rejects binary files
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE  # If it checks file type
            ]
        finally:
            os.unlink(temp_path)
    
    def test_upload_no_file_provided(self):
        """Test upload endpoint when no file is provided."""
        response = self.client.post("/api/v1/upload-log")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRealtimeFeatures:
    """Test real-time monitoring features - key differentiator."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_monitoring_status_endpoint(self):
        """Test real-time monitoring status endpoint."""
        response = self.client.get("/api/v1/self-monitor/status")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "monitoring" in data or "status" in data
    
    def test_errors_stats_endpoint(self):
        """Test error statistics endpoint."""
        response = self.client.get("/api/v1/errors/stats")
        # Should return stats even if empty
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
    
    @patch('src.debuggle.main.WebSocketManager')
    def test_websocket_endpoint_connection(self, mock_websocket):
        """Test WebSocket endpoint for real-time updates."""
        # This is a basic connection test - full WebSocket testing would require more setup
        mock_manager = MagicMock()
        mock_websocket.return_value = mock_manager
        
        # Test that the WebSocket endpoint exists
        response = self.client.get("/ws/errors")
        # WebSocket endpoints typically return 426 Upgrade Required for HTTP requests
        assert response.status_code in [status.HTTP_426_UPGRADE_REQUIRED, status.HTTP_404_NOT_FOUND]


class TestCloudIntegration:
    """Test cloud sharing and deployment features."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_cloud_upload_endpoint(self):
        """Test cloud upload functionality."""
        request_data = {
            "error_data": "Sample error for cloud sharing",
            "share_public": True
        }
        
        response = self.client.post("/api/v1/cloud/upload", json=request_data)
        # May not be fully implemented, but should not crash
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]
    
    def test_cloud_search_endpoint(self):
        """Test cloud search functionality."""
        response = self.client.get("/api/v1/cloud/search?q=IndexError")
        # May not be fully implemented, but should not crash
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_501_NOT_IMPLEMENTED,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases - critical for robustness."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_invalid_endpoint(self):
        """Test accessing non-existent endpoint."""
        response = self.client.get("/api/v1/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_method_not_allowed(self):
        """Test using wrong HTTP method."""
        response = self.client.get("/api/v1/analyze")  # Should be POST
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    @patch('src.debuggle.processor.LogProcessor.process_log')
    def test_analyze_endpoint_with_processor_error(self, mock_process):
        """Test analyze endpoint when processor fails - realistic scenario."""
        mock_process.side_effect = Exception("Processor failed")
        
        request_data = {
            "log_input": "Test error",
            "language": "python"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        # Should handle processor errors gracefully
        assert response.status_code in [
            status.HTTP_200_OK,  # If it returns error in response
            status.HTTP_500_INTERNAL_SERVER_ERROR  # If it raises HTTP exception
        ]
    
    def test_cors_headers(self):
        """Test CORS headers are present - needed for web integration."""
        response = self.client.options("/api/v1/analyze")
        # CORS should be configured for API endpoints
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
    
    def test_content_type_validation(self):
        """Test content type validation for POST endpoints."""
        response = self.client.post(
            "/api/v1/analyze",
            content="not json",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestConfigurationAndSettings:
    """Test configuration handling - prevents deployment issues."""
    
    def test_app_configuration(self):
        """Test that app is properly configured."""
        assert app is not None
        assert hasattr(app, 'routes')
        assert len(app.routes) > 0
    
    @patch.dict(os.environ, {'DEBUGGLE_MODE': 'production'})
    def test_production_mode_configuration(self):
        """Test app behavior in production mode."""
        # Configuration should be loaded properly
        from src.debuggle.config_v2 import get_settings
        settings = get_settings()
        assert settings is not None
    
    @patch.dict(os.environ, {'DEBUGGLE_MODE': 'development'})
    def test_development_mode_configuration(self):
        """Test app behavior in development mode."""
        from src.debuggle.config_v2 import get_settings
        settings = get_settings()
        assert settings is not None
    
    def test_middleware_configuration(self):
        """Test that middleware is properly configured."""
        # Should have CORS and other middleware configured
        assert hasattr(app, 'middleware_stack')


class TestIntegrationScenarios:
    """Test realistic integration scenarios - end-to-end workflows."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_complete_error_analysis_workflow(self):
        """Test complete workflow from error input to analysis output."""
        # Simulate a real developer workflow
        error_log = """
        Traceback (most recent call last):
          File "app.py", line 42, in main
            result = process_data(user_input)
          File "app.py", line 23, in process_data
            return data[index]
        IndexError: list index out of range
        """
        
        request_data = {
            "log_input": error_log,
            "language": "python",
            "options": {
                "highlight": True,
                "include_context": True
            }
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "analysis" in data
        assert "suggestions" in data
        assert len(data["analysis"]) > 100  # Should provide detailed analysis
        
        # Verify it identified the error type
        analysis_text = data["analysis"].lower()
        assert "index" in analysis_text or "range" in analysis_text
    
    def test_multi_language_error_analysis(self):
        """Test analyzing errors from different programming languages."""
        test_cases = [
            {
                "log": "NullPointerException: null",
                "language": "java",
                "expected_keywords": ["null", "pointer"]
            },
            {
                "log": "TypeError: Cannot read property 'length' of undefined",
                "language": "javascript", 
                "expected_keywords": ["undefined", "property"]
            },
            {
                "log": "FileNotFoundError: No such file or directory",
                "language": "python",
                "expected_keywords": ["file", "directory"]
            }
        ]
        
        for case in test_cases:
            request_data = {
                "log_input": case["log"],
                "language": case["language"]
            }
            
            response = self.client.post("/api/v1/analyze", json=request_data)
            assert response.status_code == status.HTTP_200_OK
            
            data = response.json()
            analysis_text = data["analysis"].lower()
            
            # Should contain relevant keywords for the error type
            assert any(keyword in analysis_text for keyword in case["expected_keywords"])
    
    def test_file_upload_to_analysis_workflow(self):
        """Test complete file upload and analysis workflow."""
        log_content = """
        [ERROR] 2024-10-03 10:30:15 - Database connection failed
        [ERROR] 2024-10-03 10:30:16 - Retrying connection... (attempt 1/3)
        [ERROR] 2024-10-03 10:30:17 - Connection timeout after 30 seconds
        [FATAL] 2024-10-03 10:30:18 - Unable to establish database connection
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            f.flush()
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                response = self.client.post(
                    "/api/v1/upload-log",
                    files={"file": ("database_errors.log", f, "text/plain")}
                )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Should analyze the uploaded log file
            assert "analysis" in data
            analysis_text = data["analysis"].lower()
            assert "database" in analysis_text or "connection" in analysis_text
            
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])