"""
🧪 COMPREHENSIVE CORE ANALYZER TESTS

Following Debuggle's educational philosophy: Think of the analyzer as the 
"master detective" of your debugging process - it needs to be thoroughly 
tested because it's the brain that figures out what went wrong.

Like testing a detective's ability to:
- 🕵️ Examine crime scenes (analyze error messages)  
- 🧠 Connect clues (identify error patterns)
- 📝 Write reports (generate analysis summaries)
- 🎯 Solve cases (provide actionable solutions)

TARGET: Boost core/analyzer.py from 20% → 75% coverage
FOCUS: Real-world error scenarios that users actually encounter
"""

import pytest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.debuggle.core.analyzer import (
    DebuggleAnalyzer, 
    AnalysisResult,
    ErrorSeverity,
    AnalysisContext
)


class TestDebuggleAnalyzerInitialization:
    """Test analyzer setup and configuration - the detective's toolkit"""
    
    def test_analyzer_creates_successfully(self):
        """Basic analyzer creation should work like hiring a detective"""
        analyzer = DebuggleAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
    def test_analyzer_with_custom_config(self):
        """Analyzer should accept custom configuration"""
        config = {'max_depth': 5, 'timeout': 30}
        analyzer = DebuggleAnalyzer(config=config)
        # Verify configuration is applied
        assert analyzer.config is not None
    
    def test_analyzer_initializes_dependencies(self):
        """Analyzer should set up its internal components"""
        analyzer = DebuggleAnalyzer()
        # Test that internal components exist
        assert hasattr(analyzer, 'pattern_matcher')
        assert hasattr(analyzer, 'context_extractor')


class TestErrorAnalysisCore:
    """Test the core error analysis functionality - the detective work"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing"""
        return DebuggleAnalyzer()
    
    def test_analyze_python_traceback(self, analyzer):
        """Test analysis of Python traceback - most common error type"""
        error_text = '''
        Traceback (most recent call last):
          File "app.py", line 42, in process_data
            result = data[index]
        IndexError: list index out of range
        '''
        
        result = analyzer.analyze(error_text)
        
        # Verify comprehensive analysis
        assert isinstance(result, AnalysisResult)
        assert result.error_type == "IndexError"
        assert result.severity in [ErrorSeverity.HIGH, ErrorSeverity.MEDIUM]
        assert "list index out of range" in result.message.lower()
        assert len(result.suggestions) > 0
    
    def test_analyze_javascript_error(self, analyzer):
        """Test JavaScript error analysis - web development errors"""
        error_text = '''
        TypeError: Cannot read property 'length' of undefined
            at processArray (main.js:15:23)
            at Object.handler (main.js:42:15)
        '''
        
        result = analyzer.analyze(error_text)
        
        assert result.error_type == "TypeError"
        assert "undefined" in result.message.lower()
        assert any("check if variable is defined" in s.lower() 
                  for s in result.suggestions)
    
    def test_analyze_sql_error(self, analyzer):
        """Test SQL error analysis - database errors"""
        error_text = '''
        ERROR 1064 (42000): You have an error in your SQL syntax; 
        check the manual that corresponds to your MySQL server version 
        for the right syntax to use near 'FORM users WHERE id = 1' at line 1
        '''
        
        result = analyzer.analyze(error_text)
        
        assert "sql" in result.error_type.lower() or "syntax" in result.error_type.lower()
        assert result.severity == ErrorSeverity.HIGH
        assert any("syntax" in s.lower() for s in result.suggestions)
    
    def test_analyze_compilation_error(self, analyzer):
        """Test compilation error analysis - build/compile errors"""
        error_text = '''
        gcc: error: undefined reference to `main'
        collect2: error: ld returned 1 exit status
        '''
        
        result = analyzer.analyze(error_text)
        
        assert "undefined reference" in result.message.lower()
        assert result.severity >= ErrorSeverity.MEDIUM
    
    def test_analyze_empty_input(self, analyzer):
        """Test handling of empty input - edge case"""
        result = analyzer.analyze("")
        
        assert result.error_type == "Unknown"
        assert result.severity == ErrorSeverity.LOW
        assert len(result.suggestions) > 0  # Should still provide help
    
    def test_analyze_non_error_text(self, analyzer):
        """Test handling of non-error text - normal output"""
        normal_text = "Application started successfully on port 8000"
        
        result = analyzer.analyze(normal_text)
        
        # Should gracefully handle non-error input
        assert isinstance(result, AnalysisResult)
        assert result.severity == ErrorSeverity.LOW


class TestAnalysisContextHandling:
    """Test context-aware analysis - understanding the bigger picture"""
    
    @pytest.fixture
    def analyzer(self):
        return DebuggleAnalyzer()
    
    def test_analyze_with_file_context(self, analyzer):
        """Test analysis when file context is provided"""
        error_text = "NameError: name 'user_data' is not defined"
        context = AnalysisContext(
            file_path="user_manager.py",
            line_number=45,
            function_name="process_user"
        )
        
        result = analyzer.analyze(error_text, context=context)
        
        assert result.context.file_path == "user_manager.py"
        assert result.context.line_number == 45
        # Context should improve suggestions
        assert len(result.suggestions) > 0
    
    def test_analyze_with_stack_trace_context(self, analyzer):
        """Test analysis with full stack trace context"""
        error_text = '''
        File "api.py", line 23, in handle_request
            response = database.fetch_user(user_id)  
        File "database.py", line 67, in fetch_user
            cursor.execute("SELECT * FROM users WHERE id = %s", user_id)
        sqlite3.OperationalError: no such table: users
        '''
        
        result = analyzer.analyze(error_text)
        
        # Should extract context from stack trace
        assert "sqlite3" in result.error_type.lower() or "operational" in result.error_type.lower()
        assert any("table" in s.lower() for s in result.suggestions)
        assert any("migration" in s.lower() or "create" in s.lower() 
                  for s in result.suggestions)


class TestAnalysisResultFormatting:
    """Test analysis result formatting and output"""
    
    @pytest.fixture
    def analyzer(self):
        return DebuggleAnalyzer()
    
    def test_analysis_result_has_required_fields(self, analyzer):
        """Test that analysis results have all required fields"""
        error_text = "ValueError: invalid literal for int() with base 10: 'abc'"
        
        result = analyzer.analyze(error_text)
        
        # Verify all required fields are present
        assert hasattr(result, 'error_type')
        assert hasattr(result, 'message')
        assert hasattr(result, 'severity')
        assert hasattr(result, 'suggestions')
        assert hasattr(result, 'confidence')
        
        # Verify field types
        assert isinstance(result.error_type, str)
        assert isinstance(result.message, str)
        assert isinstance(result.severity, ErrorSeverity)
        assert isinstance(result.suggestions, list)
        assert isinstance(result.confidence, (int, float))
    
    def test_analysis_result_json_serializable(self, analyzer):
        """Test that analysis results can be serialized to JSON"""
        error_text = "FileNotFoundError: [Errno 2] No such file or directory: 'config.txt'"
        
        result = analyzer.analyze(error_text)
        
        # Should be serializable for API responses
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)
        assert len(json_str) > 0
        
        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed['error_type'] == result.error_type


class TestAnalysisPerformance:
    """Test analysis performance and resource usage"""
    
    @pytest.fixture
    def analyzer(self):
        return DebuggleAnalyzer()
    
    def test_analysis_completes_quickly(self, analyzer):
        """Test that analysis completes within reasonable time"""
        import time
        
        error_text = "RuntimeError: Something went wrong in the application"
        
        start_time = time.time()
        result = analyzer.analyze(error_text)
        end_time = time.time()
        
        # Should complete within 1 second for simple errors
        assert (end_time - start_time) < 1.0
        assert isinstance(result, AnalysisResult)
    
    def test_handles_large_error_text(self, analyzer):
        """Test handling of very large error messages"""
        # Create large error text (simulating huge stack trace)
        large_error = "RuntimeError: Error occurred\n" + "Stack trace line\n" * 1000
        
        result = analyzer.analyze(large_error)
        
        # Should handle gracefully without crashing
        assert isinstance(result, AnalysisResult)
        assert len(result.message) > 0


class TestErrorPatternRecognition:
    """Test pattern recognition and error classification"""
    
    @pytest.fixture
    def analyzer(self):
        return DebuggleAnalyzer()
    
    def test_recognizes_import_errors(self, analyzer):
        """Test recognition of import/module errors"""
        test_cases = [
            "ModuleNotFoundError: No module named 'requests'",
            "ImportError: cannot import name 'function' from 'module'",
            "ImportError: attempted relative import with no known parent package"
        ]
        
        for error_text in test_cases:
            result = analyzer.analyze(error_text)
            assert "import" in result.error_type.lower() or "module" in result.error_type.lower()
            assert any("install" in s.lower() or "pip" in s.lower() or "import" in s.lower() 
                      for s in result.suggestions)
    
    def test_recognizes_permission_errors(self, analyzer):
        """Test recognition of permission/access errors"""
        test_cases = [
            "PermissionError: [Errno 13] Permission denied: '/var/log/app.log'",
            "OSError: [Errno 1] Operation not permitted",
            "FileNotFoundError: [Errno 2] No such file or directory"
        ]
        
        for error_text in test_cases:
            result = analyzer.analyze(error_text)
            assert result.severity >= ErrorSeverity.MEDIUM
            assert any("permission" in s.lower() or "access" in s.lower() or "file" in s.lower()
                      for s in result.suggestions)
    
    def test_recognizes_network_errors(self, analyzer):
        """Test recognition of network/connection errors"""
        test_cases = [
            "ConnectionError: HTTPSConnectionPool(host='api.example.com', port=443)",
            "socket.timeout: timed out",
            "urllib.error.URLError: <urlopen error [Errno 111] Connection refused>"
        ]
        
        for error_text in test_cases:
            result = analyzer.analyze(error_text)
            assert any("connection" in result.error_type.lower() or "network" in result.error_type.lower()
                      or "timeout" in result.error_type.lower())
            assert any("network" in s.lower() or "connection" in s.lower() or "url" in s.lower()
                      for s in result.suggestions)


def test_analyzer_integration_with_other_components():
    """Test analyzer integration with other Debuggle components"""
    analyzer = DebuggleAnalyzer()
    
    # Test that analyzer can work with pattern matcher
    error_text = "AttributeError: 'NoneType' object has no attribute 'split'"
    result = analyzer.analyze(error_text)
    
    # Should integrate with pattern recognition
    assert result.error_type == "AttributeError"
    assert "NoneType" in result.message
    
    # Should provide contextual suggestions
    assert len(result.suggestions) > 0
    assert any("None" in s or "null" in s.lower() for s in result.suggestions)


# Integration test with real-world scenarios
def test_real_world_error_scenarios():
    """Test analyzer with real-world error scenarios"""
    analyzer = DebuggleAnalyzer()
    
    # Django-style error
    django_error = '''
    django.db.utils.OperationalError: no such table: auth_user
    '''
    
    result = analyzer.analyze(django_error)
    assert "django" in result.message.lower() or "database" in result.error_type.lower()
    assert any("migration" in s.lower() for s in result.suggestions)
    
    # React/Node.js style error  
    react_error = '''
    Error: Cannot resolve module 'react-router-dom' from 'src/App.js'
    '''
    
    result = analyzer.analyze(react_error)
    assert "module" in result.error_type.lower() or "resolve" in result.error_type.lower()
    assert any("npm install" in s.lower() or "dependency" in s.lower() for s in result.suggestions)