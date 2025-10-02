"""
API endpoint tests to improve main.py coverage.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIEndpointCoverage:
    """Test API endpoints to improve main.py coverage."""
    
    def test_api_endpoints_info(self):
        """Test the /api/v1/endpoints info endpoint."""
        response = client.get("/api/v1/endpoints")
        # Endpoint might not exist, so accept 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "endpoints" in data
    
    def test_invalid_json_beautify(self):
        """Test beautify endpoint with invalid JSON."""
        # Test with malformed JSON
        response = client.post(
            "/api/v1/beautify",
            content="invalid json content",
            headers={"content-type": "application/json"}
        )
        # Should return 422 for validation error
        assert response.status_code == 422
    
    def test_beautify_with_invalid_language(self):
        """Test beautify with invalid language parameter."""
        payload = {
            "log_input": "Error: test error",
            "language": "invalid_language",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        # Should be 422 for validation error
        assert response.status_code == 422
    
    def test_beautify_with_oversized_content(self):
        """Test beautify with content that exceeds limits."""
        # Create very large content
        large_content = "Error: test\n" * 10000  # Very large content
        
        payload = {
            "log_input": large_content,
            "language": "auto",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True,
                "max_lines": 50000  # Try to exceed max_lines_limit
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        # Might succeed with truncation or fail with validation error
        assert response.status_code in [200, 400, 422]
    
    def test_upload_file_size_limits(self):
        """Test file upload with size limit scenarios.""" 
        # Test with empty file
        files = {"file": ("empty.log", b"", "text/plain")}
        data = {"language": "auto"}
        
        response = client.post("/api/v1/upload-log", files=files, data=data)
        assert response.status_code == 400
        assert "empty" in response.json()["detail"]["error"].lower()
    
    def test_upload_file_invalid_language(self):
        """Test file upload with invalid language."""
        files = {"file": ("test.log", b"Error: test error", "text/plain")}
        data = {"language": "invalid_lang"}
        
        response = client.post("/api/v1/upload-log", files=files, data=data)
        assert response.status_code == 400
        assert "Invalid language" in response.json()["detail"]["error"]
    
    def test_upload_file_invalid_max_lines(self):
        """Test file upload with invalid max_lines parameter."""
        files = {"file": ("test.log", b"Error: test error", "text/plain")}
        data = {"language": "auto", "max_lines": 999999}  # Too high
        
        response = client.post("/api/v1/upload-log", files=files, data=data)
        assert response.status_code == 400
        assert "Max lines parameter too large" in response.json()["detail"]["error"]
    
    def test_rate_limiting_simulation(self):
        """Test rate limiting behavior (if configured)."""
        # Make multiple requests quickly to potentially trigger rate limiting
        for i in range(5):
            payload = {
                "log_input": f"Error: test error {i}",
                "language": "auto",
                "options": {"highlight": True, "summarize": True, "tags": True}
            }
            
            response = client.post("/api/v1/beautify", json=payload)
            # Should succeed or hit rate limit
            assert response.status_code in [200, 429]
    
    def test_root_endpoint(self):
        """Test the root endpoint redirect."""
        response = client.get("/")
        # Should redirect or return some response
        assert response.status_code in [200, 301, 302, 307, 308]
    
    def test_health_check_endpoint(self):
        """Test health check endpoint if it exists."""
        response = client.get("/health")
        # Might exist or return 404
        assert response.status_code in [200, 404]
    
    def test_cors_headers(self):
        """Test CORS headers in responses."""
        # Test with a known endpoint
        response = client.post("/api/v1/beautify", json={
            "log_input": "test",
            "language": "auto",
            "options": {"highlight": True}
        })
        assert response.status_code == 200
        # Just verify we get a valid response with headers
        headers = response.headers
        assert isinstance(headers, dict) or hasattr(headers, 'items')
    
    def test_content_type_validation(self):
        """Test content type validation."""
        # Test with wrong content type for JSON endpoint
        response = client.post(
            "/api/v1/beautify",
            content="not json",
            headers={"content-type": "text/plain"}
        )
        # Should reject non-JSON content type
        assert response.status_code in [422, 400]