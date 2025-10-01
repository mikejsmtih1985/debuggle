import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check_success(self):
        """Test health check returns correct response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "Debuggle Trace Level"
        assert data["version"] == "1.0.0"


class TestTiersEndpoint:
    def test_get_tiers_success(self):
        """Test tiers endpoint returns all available tiers."""
        response = client.get("/api/v1/tiers")
        assert response.status_code == 200
        
        data = response.json()
        assert "tiers" in data
        assert len(data["tiers"]) == 5
        
        # Check first tier (Trace Level)
        trace_tier = data["tiers"][0]
        assert trace_tier["name"] == "Trace Level"
        assert trace_tier["icon"] == "🐜"
        assert "Beautify logs" in trace_tier["features"]


class TestBeautifyEndpoint:
    def test_beautify_python_error_success(self):
        """Test beautifying a Python IndexError."""
        payload = {
            "log_input": 'Traceback (most recent call last):\n  File "app.py", line 14, in <module>\n    main()\nIndexError: list index out of range',
            "language": "python",
            "options": {
                "highlight": True,
                "summarize": True,
                "tags": True
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "cleaned_log" in data
        assert "summary" in data
        assert "tags" in data
        assert "metadata" in data
        
        # Check summary was generated
        assert data["summary"] is not None
        assert "list index out of range" in data["summary"].lower()
        
        # Check tags include IndexError and Python
        assert "IndexError" in data["tags"]
        assert "Python" in data["tags"]
        
        # Check metadata
        assert data["metadata"]["language_detected"] == "python"
        assert data["metadata"]["lines"] > 0
    
    def test_beautify_auto_language_detection(self):
        """Test automatic language detection."""
        payload = {
            "log_input": 'Traceback (most recent call last):\n  File "test.py", line 1\n    print "hello"\n          ^\nSyntaxError: Missing parentheses',
            "language": "auto"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metadata"]["language_detected"] == "python"
    
    def test_beautify_with_options_disabled(self):
        """Test beautification with all options disabled."""
        payload = {
            "log_input": "Simple error message",
            "options": {
                "highlight": False,
                "summarize": False,
                "tags": False
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["summary"] is None
        assert len(data["tags"]) == 0
    
    def test_beautify_empty_input_error(self):
        """Test error handling for empty input."""
        payload = {
            "log_input": "",
            "language": "python"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_beautify_max_lines_limit(self):
        """Test max_lines parameter enforcement."""
        # Create a large log input
        large_log = "\n".join([f"Line {i}: Some error message" for i in range(100)])
        
        payload = {
            "log_input": large_log,
            "options": {
                "max_lines": 50
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["metadata"]["lines"] == 50
        assert data["metadata"]["truncated"] == True
    
    def test_beautify_max_lines_too_large_error(self):
        """Test error when max_lines exceeds limit."""
        payload = {
            "log_input": "test error",
            "options": {
                "max_lines": 10000  # Exceeds limit of 5000
            }
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 400
        
        data = response.json()
        assert "Max lines parameter too large" in data["detail"]["error"]


class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Debuggle Trace Level"
        assert data["status"] == "running"
        assert "/docs" in data["docs"]


class TestErrorHandling:
    def test_invalid_json_error(self):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/v1/beautify",
            data="invalid json",  # Not JSON
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_field_error(self):
        """Test handling of missing required fields."""
        payload = {
            # Missing log_input
            "language": "python"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 422
    
    def test_invalid_language_enum_error(self):
        """Test handling of invalid language enum."""
        payload = {
            "log_input": "test error",
            "language": "invalid_language"
        }
        
        response = client.post("/api/v1/beautify", json=payload)
        assert response.status_code == 422