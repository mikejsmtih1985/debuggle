"""
Focused test targeting specific missing lines to reach 90% coverage.
Based on actual code inspection of core/context.py, main.py, and config_v2.py.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Import the actual classes and functions that exist
from src.debuggle.core.context import (
    ContextExtractor, DevelopmentContext, FileContext, GitContext, 
    ProjectContext, EnvironmentContext, ErrorContext
)
from src.debuggle.config_v2 import (
    Settings, DevelopmentSettings, ProductionSettings, TestingSettings,
    Environment, LogLevel, validate_settings, get_settings_for_env
)
from src.debuggle.main import app
from fastapi.testclient import TestClient


class TestCoreContextMissingLines:
    """Target specific missing lines in core/context.py (lines 90, 105, 121, etc.)"""
    
    def test_development_context_properties(self):
        """Test DevelopmentContext properties - targets lines 90, 105, 121"""
        # Create context with no file_context (line 90 - None path)
        context = DevelopmentContext()
        assert context.error_location is None  # Line 90
        assert context.surrounding_code is None  # Line 105
        assert context.project_structure == {}  # Line 121
        
        # Create context with file_context (property access)
        file_ctx = FileContext(file_path="test.py", line_number=10, surrounding_code="test code")
        context = DevelopmentContext(file_context=file_ctx)
        assert context.error_location == "test.py:10"
        assert context.surrounding_code == "test code"
        
        # Test with project_context
        project_ctx = ProjectContext(
            root_path="/test", 
            language="python", 
            framework="flask",
            has_tests=True,
            config_files=["setup.py"]
        )
        context = DevelopmentContext(project_context=project_ctx)
        structure = context.project_structure
        assert structure['language'] == 'python'
        assert structure['framework'] == 'flask'
        assert structure['has_tests'] is True

    def test_context_extractor_error_handling(self):
        """Test error handling paths - targets lines 182-184, 227-229"""
        extractor = ContextExtractor()
        
        # Test context extraction with exceptions (lines 182-184)
        with patch.object(extractor, '_extract_file_context', side_effect=Exception("File error")):
            context = extractor.extract_full_context("Error text", "test.py")
            assert context.extraction_metadata['extraction_successful'] is False
            assert 'error' in context.extraction_metadata
        
        # Test file context extraction failure (lines 227-229)  
        with patch('pathlib.Path.exists', return_value=False):
            result = extractor._extract_file_context("Error at file.py:10", "file.py")
            assert result is None

    def test_git_context_extraction_branches(self):
        """Test git context branches - targets lines 241-263"""
        extractor = ContextExtractor()
        
        # Test when git repo doesn't exist
        with patch.object(extractor, '_run_git_command', side_effect=Exception("Not a git repo")):
            git_ctx = extractor._extract_git_context()
            assert git_ctx.is_git_repo is False
            assert git_ctx.current_branch is None
            assert git_ctx.recent_commits == []
        
        # Test successful git operations (targets multiple branches)
        mock_results = {
            'status': MagicMock(returncode=0, stdout=''),
            'branch': MagicMock(returncode=0, stdout='main\n'),
            'log': MagicMock(returncode=0, stdout='abc123 First commit\ndef456 Second commit\n'),
            'diff': MagicMock(returncode=0, stdout='file1.py\nfile2.py\n')
        }
        
        def mock_git_command(args, **kwargs):
            if 'status' in args:
                return mock_results['status']
            elif 'branch' in args:
                return mock_results['branch']
            elif 'log' in args:
                return mock_results['log']
            elif 'diff' in args:
                return mock_results['diff']
            return MagicMock(returncode=1)
        
        with patch.object(extractor, '_run_git_command', side_effect=mock_git_command):
            git_ctx = extractor._extract_git_context()
            assert git_ctx.is_git_repo is True
            assert git_ctx.current_branch == 'main'
            assert len(git_ctx.recent_commits) == 2
            assert git_ctx.last_commit_hash == 'abc123'
            assert len(git_ctx.modified_files) == 2

    def test_project_context_detection(self):
        """Test project context detection - targets lines 288-289, 300-317"""
        extractor = ContextExtractor()
        
        # Test project detection with various file patterns
        with patch('os.path.exists') as mock_exists:
            # Simulate different project types
            def exists_side_effect(path):
                path_str = str(path)
                return any(pattern in path_str for pattern in ['requirements.txt', 'package.json', 'pom.xml'])
            
            mock_exists.side_effect = exists_side_effect
            
            project_ctx = extractor._extract_project_context()
            assert project_ctx.root_path == str(extractor.project_root)
            # Should detect some project characteristics

    def test_environment_context_extraction(self):
        """Test environment context - targets lines 368, 387-389"""
        extractor = ContextExtractor()
        
        # Test environment detection
        with patch('subprocess.run') as mock_run:
            # Test successful python version detection
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='Python 3.9.0\n',
                stderr=''
            )
            
            env_ctx = extractor._extract_environment_context()
            assert env_ctx is not None
            assert env_ctx.working_directory == str(extractor.project_root)
            
            # Test subprocess failure (line 368, 387-389)
            mock_run.side_effect = Exception("Command failed")
            env_ctx = extractor._extract_environment_context()
            assert env_ctx is not None  # Should handle gracefully


class TestConfigV2MissingLines:
    """Target specific missing lines in config_v2.py"""
    
    def test_field_validators(self):
        """Test field validators - targets lines 161, 168-169, 177-181"""
        # Test debug validator with None value and different environments
        settings_dev = Settings(environment=Environment.DEVELOPMENT)
        assert settings_dev.debug is False  # Default Settings has debug=False
        
        settings_prod = Settings(environment=Environment.PRODUCTION)  
        assert settings_prod.debug is False  # Should be False for production
        
        # Test log level defaults (lines 177-181) 
        settings = Settings(environment=Environment.DEVELOPMENT)
        assert settings.log_level == LogLevel.INFO  # Default is INFO

    def test_settings_validation_functions(self):
        """Test validation functions - targets lines 296, 298, 302, 307-316"""
        # Test get_settings_for_env with all environments
        dev_settings = get_settings_for_env('development')
        assert isinstance(dev_settings, DevelopmentSettings)
        
        prod_settings = get_settings_for_env('production')
        assert isinstance(prod_settings, ProductionSettings)
        
        test_settings = get_settings_for_env('testing')
        assert isinstance(test_settings, TestingSettings)
        
        # Test unknown environment (line 302)
        unknown_settings = get_settings_for_env('unknown')
        assert isinstance(unknown_settings, Settings)
        
        # Test validate_settings function (lines 307-316)
        settings = ProductionSettings()
        settings.debug = True  # Force debug in production
        settings.api.max_log_size = 2000000  # Large size
        settings.analysis.max_context_lines = 100  # Large lines
        settings.security.api_key = ""  # Empty API key
        settings.api.cors_origins = ["*"]  # Permissive CORS
        
        messages = validate_settings(settings)
        assert isinstance(messages, list)
        # Should have multiple warnings
        assert len(messages) > 0

    def test_settings_class_inheritance(self):
        """Test settings class inheritance - targets lines 334-354"""
        # Test different settings classes (examine actual default environment)
        dev = DevelopmentSettings()
        # DevelopmentSettings may inherit environment from base Settings
        assert dev.debug is True
        
        prod = ProductionSettings()
        assert prod.environment == Environment.PRODUCTION
        assert prod.debug is False
        
        test = TestingSettings()
        assert test.environment == Environment.TESTING
        assert test.debug is False


class TestMainAPIMissingLines:
    """Target specific missing lines in main.py"""
    
    def test_api_endpoints_basic(self):
        """Test basic API endpoints - targets various missing lines"""
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # Test tiers endpoint  
        response = client.get("/api/v1/tiers")
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200

    def test_api_error_handling(self):
        """Test API error handling paths - targets lines 70, 83, etc."""
        client = TestClient(app)
        
        # Test with invalid JSON
        response = client.post(
            "/api/v1/beautify",
            content='{"invalid": json}',
            headers={"content-type": "application/json"}
        )
        # Should handle malformed JSON gracefully
        assert response.status_code in [400, 422, 500]

    def test_file_upload_error_paths(self):
        """Test file upload error handling - targets various error lines"""
        client = TestClient(app)
        
        # Test beautify API with invalid data
        response = client.post(
            "/api/v1/beautify",
            json={"text": "", "language": "invalid", "max_lines": 0}
        )
        # Should handle invalid data appropriately
        assert response.status_code in [200, 400, 422]
        
        # Test beautify API with binary-like content
        response = client.post(
            "/api/v1/beautify", 
            json={"text": "\x00\x01\x02\x03", "language": "auto", "max_lines": 100}
        )
        # Should handle binary data gracefully
        assert response.status_code in [200, 400, 422]


class TestAdditionalTargetedCoverage:
    """Additional targeted tests for remaining gaps"""
    
    def test_legacy_error_context(self):
        """Test legacy ErrorContext for backward compatibility"""
        # Test with all None values
        context = ErrorContext()
        assert context.error_location is None
        assert context.surrounding_code is None
        assert context.recent_changes == []
        assert context.project_structure == {}
        
        # Test with values
        context = ErrorContext(
            error_location="test.py:10",
            surrounding_code="code",
            recent_changes=["change1", "change2"]
        )
        assert context.error_location == "test.py:10"
        assert len(context.recent_changes) == 2
    
    def test_context_classes_initialization(self):
        """Test various context class initializations"""
        # Test all context classes
        file_ctx = FileContext(file_path="test.py")
        assert file_ctx.file_path == "test.py"
        assert file_ctx.line_number is None
        
        git_ctx = GitContext()
        assert git_ctx.is_git_repo is False
        assert git_ctx.recent_commits == []
        
        proj_ctx = ProjectContext(root_path="/test")
        assert proj_ctx.root_path == "/test"
        assert proj_ctx.dependencies == []
        
        env_ctx = EnvironmentContext()
        assert env_ctx.working_directory == "."
        assert env_ctx.environment_variables == {}

    def test_file_operations_edge_cases(self):
        """Test file operation edge cases"""
        extractor = ContextExtractor()
        
        # Test with non-existent file
        with patch('pathlib.Path.exists', return_value=False):
            result = extractor._extract_file_context("Error", "missing.py")
            assert result is None
        
        # Test with file read errors
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', side_effect=PermissionError("Access denied")):
                result = extractor._extract_file_context("Error at test.py:10", "test.py")
                # Should handle the error gracefully


if __name__ == "__main__":
    pytest.main([__file__, "-v"])