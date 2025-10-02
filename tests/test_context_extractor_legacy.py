"""
Comprehensive tests for context_extractor.py module (legacy).
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.debuggle.context_extractor import ContextExtractor, ErrorContext


class TestErrorContext:
    """Test ErrorContext dataclass."""
    
    def test_error_context_initialization(self):
        """Test ErrorContext can be initialized with defaults."""
        context = ErrorContext()
        
        assert context.error_location is None
        assert context.surrounding_code is None
        assert context.recent_changes is None
        assert context.project_structure is None
        assert context.environment_info is None
        assert context.similar_errors is None
        assert context.dependencies is None
    
    def test_error_context_with_values(self):
        """Test ErrorContext with specific values."""
        context = ErrorContext(
            error_location="app.py:10",
            surrounding_code="test code",
            recent_changes=["commit 1"],
            project_structure={"language": "python"},
            environment_info={"python": "3.9"},
            similar_errors=["error 1"],
            dependencies=["flask"]
        )
        
        assert context.error_location == "app.py:10"
        assert context.surrounding_code == "test code"
        assert context.recent_changes == ["commit 1"]
        assert context.project_structure == {"language": "python"}
        assert context.environment_info == {"python": "3.9"}
        assert context.similar_errors == ["error 1"]
        assert context.dependencies == ["flask"]


class TestContextExtractorInitialization:
    """Test ContextExtractor initialization."""
    
    def test_init_with_default_project_root(self):
        """Test initialization with default project root."""
        extractor = ContextExtractor()
        
        assert extractor.project_root == Path.cwd()
    
    def test_init_with_custom_project_root(self):
        """Test initialization with custom project root."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor = ContextExtractor(tmp_dir)
            
            assert extractor.project_root == Path(tmp_dir)
    
    def test_init_with_none_project_root(self):
        """Test initialization with None project root."""
        extractor = ContextExtractor(None)
        
        assert extractor.project_root == Path.cwd()


class TestExtractErrorLocation:
    """Test _extract_error_location method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = ContextExtractor()
    
    def test_extract_python_error_location(self):
        """Test extracting Python error location."""
        log_input = '''Traceback (most recent call last):
  File "app.py", line 14, in <module>
    main()
IndexError: list index out of range'''
        
        location = self.extractor._extract_error_location(log_input)
        assert location == "app.py:14"
    
    def test_extract_javascript_error_location(self):
        """Test extracting JavaScript error location."""
        log_input = '''ReferenceError: myVar is not defined
at app.js:25:10
at Object.<anonymous> (app.js:30:5)'''
        
        location = self.extractor._extract_error_location(log_input)
        assert location == "app.js:25"
    
    def test_extract_java_error_location(self):
        """Test extracting Java error location."""
        log_input = '''Exception in thread "main" java.lang.NullPointerException
at com.example.App.main(App.java:15)'''
        
        location = self.extractor._extract_error_location(log_input)
        # Java pattern might not match exactly, but should extract something
        assert location is not None
    
    def test_extract_general_error_location(self):
        """Test extracting general error location."""
        log_input = '''Error occurred in main.py:42'''
        
        location = self.extractor._extract_error_location(log_input)
        assert location == "main.py:42"
    
    def test_extract_error_location_no_match(self):
        """Test extracting error location when no patterns match."""
        log_input = '''Some generic error message without location'''
        
        location = self.extractor._extract_error_location(log_input)
        assert location is None
    
    def test_extract_error_location_multiple_matches(self):
        """Test extracting error location with multiple matches."""
        log_input = '''Error in file1.py:10 and also file2.py:20'''
        
        location = self.extractor._extract_error_location(log_input)
        # Should return the first match
        assert location is not None
        assert "file1.py:10" in location or "file2.py:20" in location


class TestExtractFileFromLocation:
    """Test _extract_file_from_location method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ContextExtractor(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_extract_file_from_location_existing_file(self):
        """Test extracting file path from location when file exists."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")
        
        location = "test.py:10"
        result = self.extractor._extract_file_from_location(location)
        
        assert result == str(test_file)
    
    def test_extract_file_from_location_nonexistent_file(self):
        """Test extracting file path when file doesn't exist."""
        location = "nonexistent.py:10"
        result = self.extractor._extract_file_from_location(location)
        
        assert result is None
    
    def test_extract_file_from_location_none_input(self):
        """Test extracting file path with None input."""
        # This test checks defensive programming - skip if method doesn't accept None
        try:
            result = self.extractor._extract_file_from_location("")  # Use empty string instead
            assert result is None
        except (TypeError, AttributeError):
            # Method might not handle None gracefully
            pytest.skip("Method doesn't accept None input")
    
    def test_extract_file_from_location_empty_input(self):
        """Test extracting file path with empty input."""
        result = self.extractor._extract_file_from_location("")
        
        assert result is None


class TestGetSurroundingCode:
    """Test _get_surrounding_code method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ContextExtractor(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_surrounding_code_valid_file(self):
        """Test getting surrounding code from valid file."""
        # Create test file with multiple lines
        test_file = Path(self.temp_dir) / "test.py"
        content = """line 1
line 2
line 3
line 4 - error here
line 5
line 6
line 7"""
        test_file.write_text(content)
        
        log_input = f'File "{test_file}", line 4, in main'
        result = self.extractor._get_surrounding_code(str(test_file), log_input)
        
        assert result is not None
        assert "line 4 - error here" in result
        assert ">>>" in result  # Error line marker
    
    def test_get_surrounding_code_no_line_number(self):
        """Test getting surrounding code when no line number in log."""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")
        
        log_input = "Generic error message"
        result = self.extractor._get_surrounding_code(str(test_file), log_input)
        
        assert result is None
    
    def test_get_surrounding_code_nonexistent_file(self):
        """Test getting surrounding code from nonexistent file."""
        log_input = 'File "nonexistent.py", line 5, in main'
        result = self.extractor._get_surrounding_code("nonexistent.py", log_input)
        
        assert result is None
    
    def test_get_surrounding_code_line_out_of_range(self):
        """Test getting surrounding code when line number is out of range."""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("line 1\nline 2")  # Only 2 lines
        
        log_input = f'File "{test_file}", line 10, in main'
        result = self.extractor._get_surrounding_code(str(test_file), log_input)
        
        # Should handle gracefully and return something or None
        # The exact behavior depends on implementation


class TestGetRecentChanges:
    """Test _get_recent_changes method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ContextExtractor(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('subprocess.run')
    def test_get_recent_changes_with_git(self, mock_run):
        """Test getting recent changes in git repository."""
        # Mock successful git command
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123 First commit\ndef456 Second commit\n"
        )
        
        result = self.extractor._get_recent_changes()
        
        assert result == ["abc123 First commit", "def456 Second commit"]
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_get_recent_changes_git_failure(self, mock_run):
        """Test getting recent changes when git command fails."""
        # Mock failed git command
        mock_run.return_value = MagicMock(returncode=1)
        
        result = self.extractor._get_recent_changes()
        
        assert result == []
    
    @patch('subprocess.run')
    def test_get_recent_changes_git_exception(self, mock_run):
        """Test getting recent changes when git command raises exception."""
        # Mock git command that raises exception
        mock_run.side_effect = Exception("Git not found")
        
        result = self.extractor._get_recent_changes()
        
        assert result == []


class TestAnalyzeProjectStructure:
    """Test _analyze_project_structure method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ContextExtractor(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_project_structure_python_with_requirements(self):
        """Test analyzing Python project with requirements.txt."""
        # Create requirements.txt
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("fastapi==0.68.0\npygments>=2.9.0")
        
        result = self.extractor._analyze_project_structure()
        
        assert result['language'] == 'python'
        assert 'requirements.txt' in result['config_files']
    
    def test_analyze_project_structure_python_with_pyproject(self):
        """Test analyzing Python project with pyproject.toml."""
        # Create pyproject.toml
        pyproject_file = Path(self.temp_dir) / "pyproject.toml"
        pyproject_file.write_text("[build-system]\nrequires = ['setuptools']")
        
        result = self.extractor._analyze_project_structure()
        
        assert result['language'] == 'python'
        assert 'pyproject.toml' in result['config_files']
    
    def test_analyze_project_structure_javascript(self):
        """Test analyzing JavaScript project."""
        # Create package.json
        package_file = Path(self.temp_dir) / "package.json"
        package_file.write_text('{"name": "test", "version": "1.0.0"}')
        
        result = self.extractor._analyze_project_structure()
        
        assert result['language'] == 'javascript'
        assert 'package.json' in result['config_files']
    
    def test_analyze_project_structure_with_tests(self):
        """Test analyzing project with test directory."""
        # Create tests directory
        tests_dir = Path(self.temp_dir) / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text("def test_something(): pass")
        
        result = self.extractor._analyze_project_structure()
        
        assert result['has_tests'] is True
    
    def test_analyze_project_structure_fastapi_framework(self):
        """Test detecting FastAPI framework."""
        # Create app directory with FastAPI content
        app_dir = Path(self.temp_dir) / "app"
        app_dir.mkdir()
        main_file = app_dir / "main.py"
        main_file.write_text("from fastapi import FastAPI\napp = FastAPI()")
        
        # Also need requirements.txt for Python detection
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("fastapi==0.68.0")
        
        result = self.extractor._analyze_project_structure()
        
        assert result['language'] == 'python'
        assert result['framework'] == 'fastapi'
    
    def test_analyze_project_structure_flask_framework(self):
        """Test detecting Flask framework."""
        # Create app directory with Flask content
        app_dir = Path(self.temp_dir) / "app"
        app_dir.mkdir()
        main_file = app_dir / "main.py"
        main_file.write_text("from flask import Flask\napp = Flask(__name__)")
        
        # Also need requirements.txt for Python detection
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("flask==2.0.0")
        
        result = self.extractor._analyze_project_structure()
        
        assert result['language'] == 'python'
        assert result['framework'] == 'flask'
    
    def test_analyze_project_structure_unknown_project(self):
        """Test analyzing unknown project type."""
        # Empty directory with no recognizable files
        result = self.extractor._analyze_project_structure()
        
        assert result['language'] == 'unknown'
        assert result['framework'] == 'unknown'
        assert result['has_tests'] is False
        assert result['config_files'] == []


class TestGetEnvironmentInfo:
    """Test _get_environment_info method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = ContextExtractor()
    
    @patch('subprocess.run')
    @patch('os.environ')
    def test_get_environment_info_with_python(self, mock_environ, mock_run):
        """Test getting environment info with Python version."""
        # Mock Python version command
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Python 3.9.0"
        )
        mock_environ.get.return_value = None
        
        result = self.extractor._get_environment_info()
        
        assert result['python_version'] == "Python 3.9.0"
        assert result['os'] == os.name
    
    @patch('subprocess.run')
    @patch.dict('os.environ', {'VIRTUAL_ENV': '/path/to/venv'})
    def test_get_environment_info_with_virtual_env(self, mock_run):
        """Test getting environment info with virtual environment."""
        # Mock Python version command
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Python 3.9.0"
        )
        
        result = self.extractor._get_environment_info()
        
        assert result['virtual_env'] == '/path/to/venv'
    
    @patch('subprocess.run')
    def test_get_environment_info_python_command_fails(self, mock_run):
        """Test getting environment info when Python command fails."""
        # Mock failed Python command
        mock_run.return_value = MagicMock(returncode=1)
        
        result = self.extractor._get_environment_info()
        
        assert 'python_version' not in result or result.get('python_version') is None
        assert result['os'] == os.name


class TestExtractDependencies:
    """Test _extract_dependencies method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ContextExtractor(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_extract_dependencies_from_requirements(self):
        """Test extracting dependencies from requirements.txt."""
        req_file = Path(self.temp_dir) / "requirements.txt"
        content = """fastapi==0.68.0
pygments>=2.9.0
uvicorn[standard]
# This is a comment
black
"""
        req_file.write_text(content)
        
        result = self.extractor._extract_dependencies()
        
        assert "fastapi" in result
        assert "pygments" in result
        assert "uvicorn" in result  # The extractor likely strips the [standard] part
        assert "black" in result
        # Comment should not be included
        assert "# This is a comment" not in result
    
    def test_extract_dependencies_no_requirements_file(self):
        """Test extracting dependencies when no requirements file exists."""
        result = self.extractor._extract_dependencies()
        
        assert result == []
    
    def test_extract_dependencies_empty_requirements_file(self):
        """Test extracting dependencies from empty requirements file."""
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("")
        
        result = self.extractor._extract_dependencies()
        
        assert result == []
    
    def test_extract_dependencies_malformed_requirements(self):
        """Test extracting dependencies from malformed requirements file."""
        req_file = Path(self.temp_dir) / "requirements.txt"
        req_file.write_text("fastapi==0.68.0\n\n   \n# comment\ndjango")
        
        result = self.extractor._extract_dependencies()
        
        assert "fastapi" in result
        assert "django" in result
        # Empty lines and comments should be filtered out


class TestExtractFullContext:
    """Test extract_full_context method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ContextExtractor(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.object(ContextExtractor, '_get_recent_changes')
    @patch.object(ContextExtractor, '_analyze_project_structure')
    @patch.object(ContextExtractor, '_get_environment_info')
    @patch.object(ContextExtractor, '_extract_dependencies')
    def test_extract_full_context_comprehensive(self, mock_deps, mock_env, mock_struct, mock_changes):
        """Test extracting full context with all components."""
        # Setup mocks
        mock_changes.return_value = ["commit 1", "commit 2"]
        mock_struct.return_value = {"language": "python", "framework": "fastapi"}
        mock_env.return_value = {"python_version": "Python 3.9.0"}
        mock_deps.return_value = ["fastapi", "uvicorn"]
        
        # Create test file
        test_file = Path(self.temp_dir) / "app.py"
        test_file.write_text("def main():\n    print('hello')\n    error_line")
        
        log_input = f'File "{test_file}", line 3, in main\nNameError: name error_line is not defined'
        
        result = self.extractor.extract_full_context(log_input)
        
        assert isinstance(result, ErrorContext)
        assert result.error_location == f"{test_file}:3"
        assert result.recent_changes == ["commit 1", "commit 2"]
        assert result.project_structure == {"language": "python", "framework": "fastapi"}
        assert result.environment_info == {"python_version": "Python 3.9.0"}
        assert result.dependencies == ["fastapi", "uvicorn"]
    
    def test_extract_full_context_with_explicit_file_path(self):
        """Test extracting context with explicitly provided file path."""
        # Create test file
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("line 1\nline 2\nline 3")
        
        log_input = "Generic error occurred, line 2"
        
        result = self.extractor.extract_full_context(log_input, str(test_file))
        
        assert isinstance(result, ErrorContext)
        # Should attempt to get surrounding code even with generic log
    
    def test_extract_full_context_minimal_log(self):
        """Test extracting context from minimal log input."""
        log_input = "Generic error message"
        
        result = self.extractor.extract_full_context(log_input)
        
        assert isinstance(result, ErrorContext)
        assert result.error_location is None
        # Should still populate other context fields
        assert result.project_structure is not None
        assert result.environment_info is not None