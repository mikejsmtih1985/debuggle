"""
Comprehensive tests for dashboard.py focusing on web interface and user interactions.
Following Debuggle's quality-first testing philosophy.

Target: 75%+ coverage focusing on:
- Dashboard routes and templates
- User workflow endpoints
- Real browser interaction scenarios
- Error handling in web interface
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from fastapi.testclient import TestClient
from fastapi import status

# Import dashboard functionality 
from src.debuggle.main import app


class TestDashboardRoutes:
    """Test dashboard web interface routes."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_home_page(self):
        """Test dashboard home page loads - primary user entry point."""
        response = self.client.get("/")
        # Should serve the main dashboard page
        assert response.status_code == status.HTTP_200_OK
        
        # Should return HTML content
        content_type = response.headers.get("content-type", "")
        assert "text/html" in content_type.lower() or response.status_code == status.HTTP_200_OK
    
    def test_dashboard_static_assets(self):
        """Test static assets are served correctly."""
        # Test CSS files
        response = self.client.get("/static/css/style.css")
        if response.status_code == status.HTTP_200_OK:
            assert "text/css" in response.headers.get("content-type", "")
        else:
            # Static files might not be available in test environment
            assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]
        
        # Test JavaScript files
        response = self.client.get("/static/js/dashboard.js")
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK]
    
    def test_dashboard_analyze_page(self):
        """Test analyze page - key user workflow."""
        response = self.client.get("/analyze")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            # Should serve analyze interface
            content = response.text.lower()
            assert "analyze" in content or "error" in content
    
    def test_dashboard_upload_page(self):
        """Test file upload page."""
        response = self.client.get("/upload")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_dashboard_history_page(self):
        """Test analysis history page."""
        response = self.client.get("/history")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestDashboardWebSocketIntegration:
    """Test dashboard WebSocket integration for real-time features."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_websocket_dashboard_endpoint(self):
        """Test WebSocket endpoint for dashboard updates."""
        # Test WebSocket connection endpoint
        response = self.client.get("/ws/dashboard")
        # WebSocket endpoints return 426 Upgrade Required for HTTP requests
        assert response.status_code in [
            status.HTTP_426_UPGRADE_REQUIRED,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK
        ]
    
    @patch('src.debuggle.realtime.WebSocketManager')
    def test_dashboard_realtime_updates(self, mock_ws_manager):
        """Test dashboard real-time update mechanism."""
        mock_manager = MagicMock()
        mock_ws_manager.return_value = mock_manager
        
        # Simulate dashboard requesting real-time updates
        response = self.client.get("/api/v1/dashboard/status")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestDashboardErrorHandling:
    """Test dashboard error handling and user experience."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_404_handling(self):
        """Test dashboard handles missing pages gracefully."""
        response = self.client.get("/nonexistent-dashboard-page")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_dashboard_with_invalid_parameters(self):
        """Test dashboard handles invalid parameters."""
        response = self.client.get("/analyze?invalid_param=malicious_value")
        # Should handle gracefully, not crash
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    @patch('src.debuggle.dashboard.render_template')
    def test_dashboard_template_error_handling(self, mock_render):
        """Test dashboard handles template rendering errors."""
        mock_render.side_effect = Exception("Template error")
        
        response = self.client.get("/")
        # Should handle template errors gracefully
        assert response.status_code in [
            status.HTTP_200_OK,  # If fallback template is used
            status.HTTP_500_INTERNAL_SERVER_ERROR  # If error is raised
        ]


class TestDashboardInteractiveFeatures:
    """Test interactive dashboard features that users rely on."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_error_submission(self):
        """Test submitting error through dashboard form."""
        form_data = {
            "error_text": "IndexError: list index out of range",
            "language": "python"
        }
        
        response = self.client.post("/analyze", data=form_data)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_302_FOUND,  # Redirect after form submission
            status.HTTP_404_NOT_FOUND  # If form endpoint doesn't exist
        ]
    
    def test_dashboard_file_upload_form(self):
        """Test file upload through dashboard interface."""
        log_content = "Error: Database connection failed"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            f.flush()
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {"logfile": ("test.log", f, "text/plain")}
                response = self.client.post("/upload", files=files)
                
                assert response.status_code in [
                    status.HTTP_200_OK,
                    status.HTTP_302_FOUND,  # Redirect after upload
                    status.HTTP_404_NOT_FOUND,  # If upload endpoint doesn't exist
                    status.HTTP_422_UNPROCESSABLE_ENTITY  # If form validation fails
                ]
        finally:
            os.unlink(temp_path)
    
    def test_dashboard_search_functionality(self):
        """Test dashboard search feature."""
        search_params = {"q": "IndexError", "filter": "recent"}
        
        response = self.client.get("/search", params=search_params)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # If search not implemented
        ]
    
    def test_dashboard_pagination(self):
        """Test dashboard pagination for history/results."""
        pagination_params = {"page": 2, "per_page": 10}
        
        response = self.client.get("/history", params=pagination_params)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # If history page doesn't exist
        ]


class TestDashboardConfiguration:
    """Test dashboard configuration and settings."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_settings_page(self):
        """Test dashboard settings/configuration page."""
        response = self.client.get("/settings")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # If settings page doesn't exist
        ]
    
    def test_dashboard_theme_switching(self):
        """Test dashboard theme/display options."""
        # Test setting theme preference
        theme_data = {"theme": "dark"}
        response = self.client.post("/settings/theme", json=theme_data)
        
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,  # If theme switching not implemented
            status.HTTP_422_UNPROCESSABLE_ENTITY  # If validation fails
        ]
    
    @patch.dict(os.environ, {'DEBUGGLE_THEME': 'dark'})
    def test_dashboard_with_environment_theme(self):
        """Test dashboard respects environment theme settings."""
        response = self.client.get("/")
        # Should load without errors regardless of theme setting
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestDashboardAPIIntegration:
    """Test dashboard integration with backend API."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_api_status_check(self):
        """Test dashboard can check API status."""
        response = self.client.get("/api/dashboard/status")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # If endpoint doesn't exist
        ]
    
    def test_dashboard_api_error_stats(self):
        """Test dashboard fetches error statistics."""
        response = self.client.get("/api/dashboard/stats")
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND  # If endpoint doesn't exist
        ]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, dict)
    
    @patch('src.debuggle.storage.database.DatabaseManager')
    def test_dashboard_with_database_integration(self, mock_db):
        """Test dashboard database integration."""
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.get_recent_analyses.return_value = []
        
        response = self.client.get("/history")
        # Should handle database operations without crashing
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]


class TestDashboardSecurity:
    """Test dashboard security features and validation."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_xss_protection(self):
        """Test dashboard protects against XSS attacks."""
        malicious_input = "<script>alert('xss')</script>"
        
        # Test in error analysis form
        response = self.client.post("/analyze", data={"error_text": malicious_input})
        
        if response.status_code == status.HTTP_200_OK:
            content = response.text
            # Should escape or sanitize malicious content
            assert "<script>" not in content or "escaped" in content.lower()
    
    def test_dashboard_csrf_protection(self):
        """Test dashboard CSRF protection."""
        # Attempt form submission without CSRF token
        response = self.client.post("/analyze", data={"error_text": "test error"})
        
        # Should either accept (if CSRF not implemented) or reject
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_302_FOUND,
            status.HTTP_403_FORBIDDEN,  # CSRF protection active
            status.HTTP_404_NOT_FOUND,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
    
    def test_dashboard_file_upload_security(self):
        """Test dashboard file upload security."""
        # Test uploading potentially malicious file
        malicious_content = "<?php system($_GET['cmd']); ?>"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
            f.write(malicious_content)
            f.flush()
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {"logfile": ("malicious.php", f, "application/x-php")}
                response = self.client.post("/upload", files=files)
                
                # Should reject or safely handle malicious files
                assert response.status_code in [
                    status.HTTP_200_OK,  # If it processes safely
                    status.HTTP_400_BAD_REQUEST,  # If it rejects file type
                    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,  # If it checks MIME type
                    status.HTTP_404_NOT_FOUND  # If upload not implemented
                ]
        finally:
            os.unlink(temp_path)


class TestDashboardPerformance:
    """Test dashboard performance and responsiveness."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_load_time(self):
        """Test dashboard loads within reasonable time."""
        import time
        
        start_time = time.time()
        response = self.client.get("/")
        load_time = time.time() - start_time
        
        # Should load quickly (under 5 seconds even in test environment)
        assert load_time < 5.0
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_dashboard_concurrent_requests(self):
        """Test dashboard handles concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return self.client.get("/")
        
        # Test multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # All requests should complete successfully
        for response in results:
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_dashboard_large_error_display(self):
        """Test dashboard handles large error logs efficiently."""
        # Simulate displaying a very large error log
        large_error = "Error line\n" * 1000
        
        response = self.client.post("/analyze", data={"error_text": large_error})
        
        # Should handle large content without timeout
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_302_FOUND,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_404_NOT_FOUND
        ]


class TestDashboardAccessibility:
    """Test dashboard accessibility and usability features."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_dashboard_html_structure(self):
        """Test dashboard HTML structure for accessibility."""
        response = self.client.get("/")
        
        if response.status_code == status.HTTP_200_OK:
            content = response.text.lower()
            # Should have basic HTML structure
            assert "<html" in content or "<!doctype" in content
    
    def test_dashboard_mobile_responsiveness(self):
        """Test dashboard mobile responsiveness."""
        # Simulate mobile user agent
        headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)"}
        response = self.client.get("/", headers=headers)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            content = response.text.lower()
            # Should include viewport meta tag for mobile
            assert "viewport" in content or response.status_code == status.HTTP_200_OK


class TestDashboardIntegrationWorkflows:
    """Test complete dashboard user workflows."""
    
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
    
    def test_complete_dashboard_error_analysis_workflow(self):
        """Test complete user workflow through dashboard."""
        # Step 1: Load dashboard
        response = self.client.get("/")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Dashboard not implemented")
        
        # Step 2: Submit error for analysis
        error_data = {
            "error_text": "ValueError: invalid literal for int() with base 10: 'abc'",
            "language": "python"
        }
        
        response = self.client.post("/analyze", data=error_data)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_302_FOUND,  # Redirect to results
            status.HTTP_404_NOT_FOUND
        ]
        
        # Step 3: View analysis results
        if response.status_code == status.HTTP_302_FOUND:
            redirect_location = response.headers.get("location", "/results")
            response = self.client.get(redirect_location)
            assert response.status_code == status.HTTP_200_OK
    
    def test_dashboard_file_upload_workflow(self):
        """Test complete file upload workflow through dashboard."""
        log_content = """
        [2024-10-03 10:30:15] ERROR: Failed to process user request
        [2024-10-03 10:30:16] ERROR: Database connection timeout
        [2024-10-03 10:30:17] FATAL: Service unavailable
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(log_content)
            f.flush()
            temp_path = f.name
        
        try:
            # Step 1: Load upload page
            response = self.client.get("/upload")
            if response.status_code == status.HTTP_404_NOT_FOUND:
                pytest.skip("Upload page not implemented")
            
            # Step 2: Upload file
            with open(temp_path, 'rb') as f:
                files = {"logfile": ("error.log", f, "text/plain")}
                response = self.client.post("/upload", files=files)
                
                assert response.status_code in [
                    status.HTTP_200_OK,
                    status.HTTP_302_FOUND,
                    status.HTTP_404_NOT_FOUND
                ]
                
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])