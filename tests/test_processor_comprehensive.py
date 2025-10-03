"""
Comprehensive tests for the core processor functionality.

This module provides extensive testing for the main log processing pipeline,
covering all aspects of error detection, language identification, and analysis.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.debuggle.processor import LogProcessor


class TestLogProcessorInitialization:
    """Test LogProcessor initialization and configuration."""
    
    def test_processor_initialization_default(self):
        """Test processor initializes with default settings."""
        processor = LogProcessor()
        assert processor is not None
        # Test internal components are initialized
        assert hasattr(processor, 'formatter')
    
    def test_processor_has_required_methods(self):
        """Test processor has all required public methods."""
        processor = LogProcessor()
        assert hasattr(processor, 'detect_language')
        assert hasattr(processor, 'extract_error_tags')
        assert hasattr(processor, 'process_log')
        assert hasattr(processor, 'process_log_with_context')


class TestLanguageDetection:
    """Test language detection functionality."""
    
    def test_detect_language_python_traceback(self):
        """Test Python language detection from traceback."""
        processor = LogProcessor()
        python_log = """
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
          File "app.py", line 10, in main
            print(items[5])
        IndexError: list index out of range
        """
        
        result = processor.detect_language(python_log)
        assert result == "python"
    
    def test_detect_language_javascript_error(self):
        """Test JavaScript language detection from error."""
        processor = LogProcessor()
        js_log = """
        ReferenceError: myVariable is not defined
            at Object.<anonymous> (app.js:5:13)
            at Module._compile (module.js:652:30)
            at Object.Module._extensions..js (module.js:663:10)
        """
        
        result = processor.detect_language(js_log)
        assert result == "javascript"
    
    def test_detect_language_java_exception(self):
        """Test Java language detection from exception."""
        processor = LogProcessor()
        java_log = """
        Exception in thread "main" java.lang.NullPointerException
            at com.example.MyClass.main(MyClass.java:15)
            at java.base/java.lang.reflect.Method.invoke(Method.java:568)
        """
        
        result = processor.detect_language(java_log)
        assert result == "java"
    
    def test_detect_language_csharp_exception(self):
        """Test C# language detection from exception."""
        processor = LogProcessor()
        csharp_log = """
        System.NullReferenceException: Object reference not set to an instance of an object.
           at MyApp.Services.UserService.GetUser(Int32 userId)
           at MyApp.Controllers.UserController.GetUserDetails(Int32 id)
        """
        
        result = processor.detect_language(csharp_log)
        assert result == "csharp"
    
    def test_detect_language_unknown_defaults_to_python(self):
        """Test unknown language defaults to python."""
        processor = LogProcessor()
        unknown_log = "Some generic error message without language-specific patterns"
        
        result = processor.detect_language(unknown_log)
        assert result == "python"  # Default fallback
    
    def test_detect_language_mixed_content(self):
        """Test language detection with mixed content."""
        processor = LogProcessor()
        mixed_log = """
        2024-01-01 10:00:00 INFO Starting application
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
        IndexError: list index out of range
        """
        
        result = processor.detect_language(mixed_log)
        assert result == "python"  # Should detect Python from traceback


class TestErrorTagExtraction:
    """Test error tag extraction functionality."""
    
    def test_extract_error_tags_python_indexerror(self):
        """Test extracting tags from Python IndexError."""
        processor = LogProcessor()
        python_log = """
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
          File "app.py", line 10, in main
            print(items[5])
        IndexError: list index out of range
        """
        
        tags = processor.extract_error_tags(python_log)
        assert "IndexError" in tags or "Index Error" in tags
        assert "Stack Trace" in tags
    
    def test_extract_error_tags_javascript_reference_error(self):
        """Test extracting tags from JavaScript ReferenceError."""
        processor = LogProcessor()
        js_log = """
        ReferenceError: myVariable is not defined
            at Object.<anonymous> (app.js:5:13)
        """
        
        tags = processor.extract_error_tags(js_log)
        assert "ReferenceError" in tags or "Reference Error" in tags
    
    def test_extract_error_tags_stack_trace(self):
        """Test extracting stack trace tags."""
        processor = LogProcessor()
        log_with_stack = """
        Exception in thread "main" java.lang.NullPointerException
            at com.example.service.UserService.getUser(UserService.java:45)
            at com.example.controller.UserController.handleGetUser(UserController.java:23)
        """
        
        tags = processor.extract_error_tags(log_with_stack)
        assert "Stack Trace" in tags
        assert "NullPointerException" in tags or "Null Pointer" in tags
    
    def test_extract_error_tags_no_errors(self):
        """Test extracting tags from logs with no errors."""
        processor = LogProcessor()
        info_log = "2024-01-01 10:00:00 INFO Application started successfully"
        
        tags = processor.extract_error_tags(info_log)
        assert isinstance(tags, list)  # Should return a list even if empty


class TestFullProcessingPipeline:
    """Test the complete log processing pipeline."""
    
    def test_process_log_basic_functionality(self):
        """Test the basic process_log functionality."""
        processor = LogProcessor()
        log_input = """
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
          File "app.py", line 10, in main
            print(items[5])
        IndexError: list index out of range
        """
        
        # Test the actual method signature: process_log(log_input, language, highlight, summarize, tags, max_lines)
        result = processor.process_log(log_input)
        
        # Result is a tuple: (cleaned_log, summary, tags, metadata)
        assert isinstance(result, tuple)
        assert len(result) == 4
        
        cleaned_log, summary, tags, metadata = result
        assert isinstance(cleaned_log, str)
        assert isinstance(tags, list)
        assert isinstance(metadata, dict)
        assert len(cleaned_log) > 0
        assert len(tags) > 0
    
    def test_process_log_with_parameters(self):
        """Test process_log with various parameters."""
        processor = LogProcessor()
        log_input = "IndexError: list index out of range"
        
        # Test with different parameters
        result = processor.process_log(
            log_input, 
            language="python", 
            highlight=True, 
            summarize=True, 
            tags=True, 
            max_lines=100
        )
        
        cleaned_log, summary, tags, metadata = result
        assert isinstance(cleaned_log, str)
        assert isinstance(tags, list)
        assert isinstance(metadata, dict)
        assert "language_detected" in metadata
    
    def test_process_log_with_context(self):
        """Test process_log_with_context functionality."""
        processor = LogProcessor()
        log_input = """
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
        IndexError: list index out of range
        """
        
        # Test the context processing method
        result = processor.process_log_with_context(log_input)
        
        # Result should be tuple of 5 elements
        assert isinstance(result, tuple)
        assert len(result) == 5
        
        cleaned_log, summary, tags, metadata, rich_context = result
        assert isinstance(cleaned_log, str)
        assert isinstance(tags, list) 
        assert isinstance(metadata, dict)
        assert isinstance(rich_context, str)
    
    def test_process_log_no_highlighting(self):
        """Test processing without syntax highlighting."""
        processor = LogProcessor()
        log_input = "print('hello world')\nSyntaxError: invalid syntax"
        
        cleaned_log, summary, tags, metadata = processor.process_log(
            log_input, highlight=False
        )
        
        # Should not contain HTML highlighting tags since highlighting is disabled
        assert "<span" not in cleaned_log
        assert "class=" not in cleaned_log
    
    def test_process_log_truncation(self):
        """Test processing with log truncation."""
        processor = LogProcessor()
        
        # Create a log with many lines
        long_log = "\n".join([f"Line {i}: Some error message" for i in range(200)])
        
        cleaned_log, summary, tags, metadata = processor.process_log(
            long_log, max_lines=50
        )
        
        # Check metadata for truncation info
        assert "truncated" in metadata
        if metadata["truncated"]:
            assert metadata["lines"] <= 52  # 50 + some buffer


class TestErrorHandling:
    """Test error handling in the processor."""
    
    def test_process_empty_log(self):
        """Test processing empty log input."""
        processor = LogProcessor()
        
        # Empty log should still process without error
        cleaned_log, summary, tags, metadata = processor.process_log("")
        assert isinstance(cleaned_log, str)
        assert isinstance(tags, list)
    
    def test_process_whitespace_only_log(self):
        """Test processing whitespace-only log."""
        processor = LogProcessor()
        
        cleaned_log, summary, tags, metadata = processor.process_log("   \n\t  \n  ")
        assert isinstance(cleaned_log, str)
        assert isinstance(tags, list)
    
    def test_process_invalid_language(self):
        """Test processing with invalid language parameter."""
        processor = LogProcessor()
        log_input = "Some error message"
        
        # Should handle invalid language gracefully
        cleaned_log, summary, tags, metadata = processor.process_log(
            log_input, language="invalid_language"
        )
        assert isinstance(cleaned_log, str)
        assert isinstance(tags, list)


class TestSpecializedErrorTypes:
    """Test handling of specialized error types."""
    
    def test_connection_error_handling(self):
        """Test handling of connection-related errors."""
        processor = LogProcessor()
        connection_log = """
        requests.exceptions.ConnectionError: HTTPSConnectionPool(host='api.example.com', port=443): 
        Max retries exceeded with url: /data (Caused by NewConnectionError)
        """
        
        cleaned_log, summary, tags, metadata = processor.process_log(connection_log)
        
        # Should extract meaningful tags
        assert len(tags) > 0
        # Look for connection-related tags (exact format may vary)
        tag_text = " ".join(tags).lower()
        assert "connection" in tag_text or "error" in tag_text
    
    def test_timeout_error_handling(self):
        """Test handling of timeout errors."""
        processor = LogProcessor()
        timeout_log = """
        requests.exceptions.Timeout: HTTPSConnectionPool(host='slow-api.com', port=443): 
        Read timed out. (read timeout=30)
        """
        
        cleaned_log, summary, tags, metadata = processor.process_log(timeout_log)
        
        assert len(tags) > 0
        tag_text = " ".join(tags).lower()
        assert "timeout" in tag_text or "error" in tag_text
    
    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        processor = LogProcessor()
        permission_log = """
        PermissionError: [Errno 13] Permission denied: '/protected/file.txt'
        """
        
        cleaned_log, summary, tags, metadata = processor.process_log(permission_log)
        
        assert len(tags) > 0
        tag_text = " ".join(tags).lower()
        assert "permission" in tag_text or "error" in tag_text


class TestSyntaxHighlighting:
    """Test syntax highlighting functionality."""
    
    def test_apply_syntax_highlighting_basic(self):
        """Test basic syntax highlighting."""
        processor = LogProcessor()
        code_text = "def hello():\n    print('world')"
        
        result = processor.apply_syntax_highlighting(code_text, "python")
        
        # Should return formatted text
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_apply_syntax_highlighting_different_languages(self):
        """Test syntax highlighting for different languages."""
        processor = LogProcessor()
        
        test_cases = [
            ("console.log('hello');", "javascript"),
            ("System.out.println('hello');", "java"),
            ("print('hello')", "python"),
        ]
        
        for code, lang in test_cases:
            result = processor.apply_syntax_highlighting(code, lang)
            assert isinstance(result, str)
            assert len(result) > 0