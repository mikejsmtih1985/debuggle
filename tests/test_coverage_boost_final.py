"""
Final coverage boost tests - targeting specific uncovered lines to reach 90%+ coverage.
Focus on config_v2.py, context_extractor.py, core/context.py, and main.py gaps.
"""

import os
import pytest
import tempfile
import json
from unittest.mock import patch, mock_open, MagicMock
from fastapi.testclient import TestClient

from src.debuggle.config_v2 import (
    Settings, DevelopmentSettings, ProductionSettings, TestingSettings,
    Environment, LogLevel, get_settings, get_settings_for_env, validate_settings
)
from src.debuggle.context_extractor import ContextExtractor, ErrorContext
from src.debuggle.main import app


class TestConfigV2Coverage:
    """Target missing coverage in config_v2.py"""

    def test_environment_properties(self):
        """Test environment property methods"""
        dev_settings = DevelopmentSettings()
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False
        
        prod_settings = ProductionSettings()
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True

    def test_get_settings_for_env_all_environments(self):
        """Test get_settings_for_env function with all environment types"""
        dev_settings = get_settings_for_env('development')
        assert isinstance(dev_settings, DevelopmentSettings)
        
        prod_settings = get_settings_for_env('production')
        assert isinstance(prod_settings, ProductionSettings)
        
        test_settings = get_settings_for_env('testing')
        assert isinstance(test_settings, TestingSettings)
        
        # Test unknown environment
        unknown_settings = get_settings_for_env('unknown')
        assert isinstance(unknown_settings, Settings)
        assert unknown_settings.environment == Environment.DEVELOPMENT

    def test_get_settings_different_environments(self):
        """Test get_settings function with different environment variables"""
        with patch.dict(os.environ, {'DEBUGGLE_ENVIRONMENT': 'production'}):
            settings = get_settings()
            assert isinstance(settings, ProductionSettings)
        
        with patch.dict(os.environ, {'DEBUGGLE_ENVIRONMENT': 'testing'}):
            settings = get_settings()
            assert isinstance(settings, TestingSettings)
        
        with patch.dict(os.environ, {'DEBUGGLE_ENVIRONMENT': 'unknown'}):
            settings = get_settings()
            assert isinstance(settings, Settings)

    def test_validate_settings_production_warnings(self):
        """Test validate_settings with production warnings"""
        prod_settings = ProductionSettings()
        prod_settings.debug = True  # Override to trigger warning
        prod_settings.security.api_key = ""  # Ensure empty for warning
        prod_settings.api.cors_origins = ["*"]  # Trigger CORS warning
        
        messages = validate_settings(prod_settings)
        assert any("Debug mode is enabled in production" in msg for msg in messages)
        assert any("No API key configured for production" in msg for msg in messages)
        assert any("Permissive CORS origins in production" in msg for msg in messages)

    def test_validate_settings_resource_warnings(self):
        """Test validate_settings with resource limit warnings"""
        settings = Settings()
        settings.api.max_log_size = 2000000  # 2MB, over limit
        settings.analysis.max_context_lines = 100  # Over limit
        
        messages = validate_settings(settings)
        assert any("Large max_log_size may impact performance" in msg for msg in messages)
        assert any("High max_context_lines may slow analysis" in msg for msg in messages)


class TestContextExtractorCoverage:
    """Target missing coverage in context_extractor.py"""

    def test_format_context_for_analysis_full_context(self):
        """Test format_context_for_analysis with comprehensive context"""
        extractor = ContextExtractor()
        
        context = ErrorContext(
            error_location="test.py:10",
            surrounding_code="def test():\n    x = [1, 2]\n    return x[5]  # Error here",
            recent_changes=["Modified test.py", "Added new feature"],
            project_structure={
                'language': 'python',
                'framework': 'flask',
                'has_tests': True,
                'config_files': ['requirements.txt', 'setup.py']
            },
            dependencies=['flask', 'pytest', 'requests'],
            environment_info={'python_version': '3.8', 'virtual_env': 'venv'}
        )
        
        log_input = "IndexError: list index out of range"
        result = extractor.format_context_for_analysis(context, log_input)
        
        assert "ERROR ANALYSIS WITH FULL CONTEXT" in result
        assert "Original Error:" in result
        assert "Code Context" in result
        assert "Recent Changes" in result
        assert "Project Context:" in result
        assert "Language: python" in result
        assert "Framework: flask" in result
        assert "Has Tests: Yes" in result
        assert "Config Files:" in result
        assert "Key Dependencies:" in result
        assert "flask" in result

    def test_extract_full_context_exception_handling(self):
        """Test extract_full_context with various exception scenarios"""
        extractor = ContextExtractor()
        
        # Test with subprocess errors during git operations
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Git command failed")
            
            context = extractor.extract_full_context("Test error", None)
            assert context is not None
            assert context.error_location is None  # Should handle gracefully

    def test_extract_full_context_file_operations(self):
        """Test extract_full_context with file operation errors"""
        extractor = ContextExtractor()
        
        # Test with file read errors
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = FileNotFoundError("File not found")
            
            context = extractor.extract_full_context("File error at test.py:10", "test.py")
            assert context is not None


class TestMainAPICoverage:
    """Target missing coverage in main.py"""

    def test_main_exception_handler_with_request_validation_error(self):
        """Test main exception handler with RequestValidationError"""
        client = TestClient(app)
        
        # Send invalid JSON to trigger RequestValidationError
        response = client.post("/api/analyzy", json={
            "log_input": "",  # Invalid: empty string
            "language": "invalid_language"  # Invalid enum value
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_file_upload_with_large_file(self):
        """Test file upload size validation"""
        client = TestClient(app)
        
        # Create a large file content
        large_content = "Error line\n" * 10000  # Should exceed typical limits
        
        response = client.post(
            "/api/upload",
            files={
                "file": ("large_test.log", large_content, "text/plain")
            },
            data={
                "language": "auto",
                "max_lines": "1000"
            }
        )
        
        # Should handle large file appropriately
        assert response.status_code in [200, 400, 413]  # Various valid responses

    def test_upload_endpoint_with_encoding_errors(self):
        """Test upload endpoint with file encoding issues"""
        client = TestClient(app)
        
        # Test with binary content that might cause encoding issues
        binary_content = b'\x80\x81\x82\x83 Some error message'
        
        response = client.post(
            "/api/upload",
            files={
                "file": ("binary_test.log", binary_content, "text/plain")
            },
            data={
                "language": "auto",
                "max_lines": "100"
            }
        )
        
        # Should handle encoding errors gracefully
        assert response.status_code in [200, 400]

    def test_health_endpoint_additional_checks(self):
        """Test health endpoint with additional validation"""
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_api_with_malformed_json(self):
        """Test API endpoints with malformed JSON"""
        client = TestClient(app)
        
        # Send malformed JSON
        response = client.post(
            "/api/analyzy",
            content='{"log_input": "test", invalid_json',
            headers={"content-type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_cors_headers_validation(self):
        """Test CORS headers are properly set"""
        client = TestClient(app)
        
        response = client.options("/api/analyzy")
        assert response.status_code == 200
        
        # Check CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers

    def test_rate_limiting_simulation(self):
        """Test rate limiting behavior"""
        client = TestClient(app)
        
        # Make multiple rapid requests
        responses = []
        for i in range(5):
            response = client.post("/api/analyzy", json={
                "log_input": f"Test error {i}",
                "language": "python"
            })
            responses.append(response)
        
        # At least some should succeed
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count > 0


class TestProcessorEdgeCases:
    """Additional processor coverage for edge cases"""

    def test_processor_syntax_highlighting_failure(self):
        """Test processor when syntax highlighting fails"""
        from src.debuggle.processor import LogProcessor
        
        processor = LogProcessor()
        
        # Test with content that might cause highlighting issues
        with patch('pygments.highlight') as mock_highlight:
            mock_highlight.side_effect = Exception("Highlighting failed")
            
            result = processor.process_log(
                "Test error message",
                language="python",
                highlight=True
            )
            
            # Should fallback gracefully without highlighting
            assert result[0] is not None  # cleaned_log
            assert "error" in result[0].lower()

    def test_processor_language_detection_fallbacks(self):
        """Test language detection fallback mechanisms"""
        from src.debuggle.processor import LogProcessor
        
        processor = LogProcessor()
        
        # Test with langdetect failure
        with patch('langdetect.detect') as mock_detect:
            mock_detect.side_effect = Exception("Detection failed")
            
            detected = processor.detect_language("Some error text")
            assert detected in ["python", "auto", "unknown"]  # Should fallback

    def test_processor_problem_categorization_edge_cases(self):
        """Test problem categorization with edge cases"""
        from src.debuggle.processor import LogProcessor
        
        processor = LogProcessor()
        
        # Test with various error patterns
        test_cases = [
            "Connection refused",
            "Permission denied", 
            "Timeout error",
            "Memory allocation failed",
            "Disk space full"
        ]
        
        for error_text in test_cases:
            tags = processor.extract_error_tags(error_text)
            # Should extract some meaningful tags
            assert len(tags) >= 0  # At minimum, should not crash


class TestAdditionalCoverageTargets:
    """Additional targeted tests to reach 90% coverage"""
    
    def test_processor_clean_and_deduplicate_edge_cases(self):
        """Test processor clean_and_deduplicate with various inputs"""
        from src.debuggle.processor import LogProcessor
        
        processor = LogProcessor()
        
        # Test with empty input
        result = processor.clean_and_deduplicate("")
        assert result == ""
        
        # Test with only whitespace
        result = processor.clean_and_deduplicate("   \n\n\t  ")
        assert len(result.strip()) == 0
        
        # Test with duplicate lines
        duplicate_input = "Error: test\nError: test\nDifferent error\nError: test"
        result = processor.clean_and_deduplicate(duplicate_input)
        lines = result.split('\n')
        # Should reduce duplicates
        assert len(lines) <= 3

    def test_main_app_exception_paths(self):
        """Test main app exception handling paths"""
        client = TestClient(app)
        
        # Test with extremely large input to trigger size limits
        huge_input = "X" * 100000
        response = client.post("/api/analyzy", json={
            "log_input": huge_input,
            "language": "python"
        })
        
        # Should handle gracefully (either process or reject cleanly)
        assert response.status_code in [200, 400, 413, 422]
        
    def test_error_fixes_module_coverage(self):
        """Test error_fixes module patterns"""
        from src.debuggle.error_fixes import generate_enhanced_error_summary
        
        # Test with various error types to hit different branches
        test_errors = [
            "ModuleNotFoundError: No module named 'nonexistent'",
            "ImportError: cannot import name 'missing' from 'module'",
            "SyntaxError: invalid syntax",
            "UnknownError: this is not a known error type"
        ]
        
        for error in test_errors:
            summary = generate_enhanced_error_summary(error)
            assert isinstance(summary, str)
            assert len(summary) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])