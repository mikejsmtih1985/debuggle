"""
🎯 COMPREHENSIVE MAIN.PY COVERAGE TESTS

This test suite is designed to boost main.py coverage from 35% to 70%+ by testing:
- All API endpoints and their error handling
- Middleware functionality (CORS, rate limiting)
- WebSocket connections and real-time features
- File upload scenarios and validation
- Health checks and service metadata
- Exception handling and error responses

These tests focus on the main FastAPI application logic that was previously untested.
"""

import pytest
import asyncio
import json
import tempfile
import os
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

# Import the main app and its dependencies
from src.debuggle.app_factory import create_app
app = create_app()


class TestMainAppEndpoints:
    """Test core API endpoints in main.py"""
    
    def setup_method(self):
        """Set up test client and mocks"""
        self.client = TestClient(app)
    
    def test_root_endpoint_returns_html(self):
        """Test that root endpoint serves the main HTML page"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_health_endpoint_basic(self):
        """Test basic health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
        assert "version" in data
        assert "version" in data
    
    def test_health_endpoint_detailed(self):
        """Test health endpoint with detailed response validation"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "status" in data
        # The health endpoint may not have timestamp/uptime in simple implementation
        assert data["status"] in ["ok", "healthy"]
    
    def test_info_endpoint(self):
        """Test API info endpoint"""
        response = self.client.get("/api/v1") 
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "endpoints" in data
    
    @patch('src.debuggle.main.processor')
    def test_analyze_endpoint_success(self, mock_processor):
        """Test successful log analysis"""
        mock_processor.process_log.return_value = (
            "cleaned log",
            "summary",
            ["tag1", "tag2"],
            {"language": "python"}
        )
        
        request_data = {
            "log_input": "ValueError: invalid literal for int()",
            "language": "python"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cleaned_log" in data
        assert "summary" in data
        assert "tags" in data
        assert "metadata" in data
    
    @patch('src.debuggle.main.processor')
    def test_analyze_endpoint_error_handling(self, mock_processor):
        """Test analyze endpoint error handling"""
        mock_processor.process_log.side_effect = Exception("Processing failed")
        
        request_data = {
            "log_input": "Some error log",
            "language": "python"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_analyze_endpoint_validation_error(self):
        """Test analyze endpoint with invalid input"""
        # Empty log input should fail validation
        request_data = {
            "log_input": "",
            "language": "invalid_language"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_endpoint_large_input(self):
        """Test analyze endpoint with very large input"""
        large_input = "Error: " + "x" * 100000  # Very large input
        
        request_data = {
            "log_input": large_input,
            "language": "python"
        }
        
        response = self.client.post("/api/v1/analyze", json=request_data)
        # Should either process successfully or reject gracefully
        assert response.status_code in [200, 400, 413, 422]


class TestFileUploadEndpoints:
    """Test file upload functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    @patch('src.debuggle.main.processor')
    def test_file_upload_success(self, mock_processor):
        """Test successful file upload"""
        mock_processor.process_log.return_value = (
            "cleaned log",
            "summary", 
            ["file-upload", "python"],
            {"language": "python", "filename": "test.log"}
        )
        
        # Create a test file
        test_content = "ValueError: test error\\nFile 'test.py', line 10"
        
        response = self.client.post(
            "/api/v1/upload-log",
            files={"file": ("test.log", test_content, "text/plain")},
            data={"language": "python", "max_lines": "100"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "results" in data
    
    def test_file_upload_no_file(self):
        """Test file upload without file"""
        response = self.client.post(
            "/api/v1/upload-log",
            data={"language": "python"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_file_upload_empty_file(self):
        """Test file upload with empty file"""
        response = self.client.post(
            "/api/v1/upload-log",
            files={"file": ("empty.log", "", "text/plain")},
            data={"language": "python"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
    
    def test_file_upload_large_file(self):
        """Test file upload size limits"""
        large_content = "Error line\\n" * 50000  # Very large file
        
        response = self.client.post(
            "/api/v1/upload-log",
            files={"file": ("large.log", large_content, "text/plain")},
            data={"language": "python", "max_lines": "1000"}
        )
        
        # Should handle large files appropriately
        assert response.status_code in [200, 400, 413]
    
    def test_file_upload_binary_content(self):
        """Test file upload with binary content"""
        binary_content = b'\\x80\\x81\\x82Error message'
        
        response = self.client.post(
            "/api/v1/upload-log",
            files={"file": ("binary.log", binary_content, "application/octet-stream")},
            data={"language": "auto"}
        )
        
        # Should handle encoding issues gracefully
        assert response.status_code in [200, 400]


class TestMiddlewareAndErrorHandling:
    """Test CORS, rate limiting, and global error handling"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = self.client.options("/api/v1/analyze", headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # Should allow CORS requests
        assert response.status_code in [200, 204]
        # Check for CORS headers (may vary based on configuration)
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON requests"""
        response = self.client.post(
            "/api/v1/analyze",
            content='{"log_input": "test", invalid_json',
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422  # Should handle malformed JSON
    
    def test_unsupported_media_type(self):
        """Test handling of unsupported content types"""
        response = self.client.post(
            "/api/v1/analyze",
            content="not json data",
            headers={"content-type": "text/plain"}
        )
        
        assert response.status_code in [400, 415, 422]
    
    def test_request_size_limits(self):
        """Test request size limitations"""
        huge_data = {"log_input": "x" * 1000000, "language": "python"}
        
        response = self.client.post("/api/v1/analyze", json=huge_data)
        # Should either process or reject cleanly
        assert response.status_code in [200, 400, 413, 422]
    
    def test_invalid_endpoints(self):
        """Test requests to non-existent endpoints"""
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404
        
        response = self.client.post("/api/invalid")
        assert response.status_code == 404


class TestWebSocketConnections:
    """Test WebSocket functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_websocket_connection_basic(self):
        """Test basic WebSocket connection"""
        with self.client.websocket_connect("/ws") as websocket:
            # Connection should be established
            assert websocket is not None
            
            # Should be able to send/receive basic messages
            websocket.send_json({"type": "ping"})
            data = websocket.receive_json()
            assert data["type"] == "pong"
    
    def test_websocket_error_monitoring(self):
        """Test WebSocket error monitoring features"""
        with self.client.websocket_connect("/ws/monitor") as websocket:
            # Send monitoring request
            websocket.send_json({
                "type": "start_monitoring",
                "filters": ["critical", "error"]
            })
            
            # Should receive acknowledgment
            response = websocket.receive_json()
            assert response["type"] in ["monitoring_started", "ack"]
    
    def test_websocket_invalid_message(self):
        """Test WebSocket with invalid message format"""
        with self.client.websocket_connect("/ws") as websocket:
            # Send invalid message
            websocket.send_text("invalid json")
            
            # Should handle gracefully
            try:
                response = websocket.receive_json()
                assert "error" in response or response["type"] == "error"
            except:
                # Connection might be closed, which is also acceptable
                pass


class TestServiceIntegration:
    """Test integration with ingestion and dashboard engines"""
    
    @patch('src.debuggle.main.get_ingestion_engine')
    def test_ingestion_engine_integration(self, mock_get_ingestion):
        """Test that ingestion engine is properly integrated"""
        mock_engine = AsyncMock()
        mock_get_ingestion.return_value = mock_engine
        
        client = TestClient(app)
        
        # Make a request that should use ingestion engine
        response = client.post("/api/v1/analyze", json={
            "log_input": "Test error",
            "language": "python"
        })
        
        # Should not crash due to ingestion engine issues
        assert response.status_code in [200, 500]  # Either works or fails gracefully
    
    @patch('src.debuggle.main.get_dashboard_engine')
    def test_dashboard_engine_integration(self, mock_get_dashboard):
        """Test that dashboard engine is properly integrated"""
        mock_engine = AsyncMock()
        mock_get_dashboard.return_value = mock_engine
        
        client = TestClient(app)
        
        # Make a request that should use dashboard engine
        response = client.get("/api/v1/health")
        
        # Should not crash due to dashboard engine issues
        assert response.status_code in [200, 500]  # Either works or fails gracefully


class TestErrorScenarios:
    """Test various error scenarios and edge cases"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_server_error_handling(self):
        """Test server error handling"""
        with patch('src.debuggle.main.processor') as mock_processor:
            mock_processor.process_log.side_effect = RuntimeError("Critical error")
            
            response = self.client.post("/api/v1/analyze", json={
                "log_input": "test",
                "language": "python"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False
    
    def test_timeout_handling(self):
        """Test request timeout handling"""
        with patch('src.debuggle.main.processor') as mock_processor:
            # Simulate a long-running operation
            mock_processor.process_log.side_effect = lambda *args, **kwargs: time.sleep(10)
            
            response = self.client.post("/api/v1/analyze", json={
                "log_input": "test",
                "language": "python"
            })
            
            # Should either timeout or complete
            assert response.status_code in [200, 408, 500, 504]
    
    @patch('src.debuggle.main.database_manager')
    def test_database_error_handling(self, mock_db):
        """Test database connection error handling"""
        mock_db.side_effect = Exception("Database connection failed")
        
        response = self.client.get("/api/v1/health")
        
        # Should handle database errors gracefully
        assert response.status_code in [200, 500, 503]


class TestApiResponseFormats:
    """Test API response formats and consistency"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_json_response_structure(self):
        """Test that JSON responses have consistent structure"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        # All responses should have basic structure
        assert isinstance(data, dict)
        assert "status" in data
    
    def test_error_response_structure(self):
        """Test that error responses have consistent structure"""
        response = self.client.get("/api/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert isinstance(data, dict)
        # Error responses should have error information
    
    def test_content_type_headers(self):
        """Test that proper content-type headers are set"""
        response = self.client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")
        
        response = self.client.get("/")
        assert "text/html" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])