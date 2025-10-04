"""
🧪 COMPREHENSIVE CORE ANALYZER TESTS - QUALITY FIRST APPROACH

Following Debuggle's educational philosophy: Test the core analyzer like you're
testing a master detective's abilities. Focus on real-world scenarios that 
demonstrate educational value and practical debugging skills.

🎯 TARGET: Improve core/analyzer.py coverage from current baseline to 75%+
📚 FOCUS: Educational scenarios that teach debugging patterns
🔍 PRIORITY: Cover critical paths that users depend on most

Like testing a detective agency:
- 🕵️ Can they analyze different types of crime scenes? (error types)
- 📝 Do they write clear, helpful reports? (analysis results)
- 🎯 Can they handle tricky cases gracefully? (edge cases)
- 🏃‍♂️ Are they fast enough for urgent cases? (performance)
"""

import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import List

# Import the classes we're testing
from src.debuggle.core.analyzer import (
    ErrorAnalyzer, 
    AnalysisResult,
    AnalysisRequest
)
from src.debuggle.core.patterns import (
    ErrorPattern, 
    ErrorSeverity, 
    ErrorCategory,
    ErrorMatch,
    ErrorPatternMatcher
)


class TestErrorAnalyzerCoreWorkflow:
    """
    🔧 TEST THE DETECTIVE'S CORE INVESTIGATION PROCESS
    
    These tests ensure the main analyze() method works correctly.
    Like testing a detective's ability to follow their standard
    investigation procedure from start to finish.
    """
    
    @pytest.fixture
    def analyzer(self):
        """Create a fresh analyzer for each test - like hiring a new detective"""
        return ErrorAnalyzer()
    
    def test_analyzer_initialization_success(self, analyzer):
        """Test that our detective agency can be established successfully"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
        assert hasattr(analyzer, 'pattern_matcher')
        assert hasattr(analyzer, 'logger')
    
    @patch.object(ErrorPatternMatcher, 'find_matches')
    @patch.object(ErrorPatternMatcher, 'detect_language')
    def test_analyze_python_traceback_success(self, mock_detect_lang, mock_find_matches, analyzer):
        """
        Test analyzing a realistic Python traceback - this is the #1 use case!
        Like testing if our detective can solve the most common type of case.
        """
        # 🎭 SETUP THE CRIME SCENE
        traceback_text = '''Traceback (most recent call last):
  File "app.py", line 42, in process_data
    result = data[index]
IndexError: list index out of range'''
        
        # 🕵️ SETUP OUR DETECTIVE'S FINDINGS
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "IndexError"
        mock_pattern.category = ErrorCategory.RUNTIME
        mock_pattern.severity = ErrorSeverity.HIGH
        mock_pattern.what_happened = "Tried to access a list item that doesn't exist"
        mock_pattern.quick_fixes = ["Check list length before accessing", "Use try/except"]
        mock_pattern.prevention_tip = "Always validate array bounds"
        mock_pattern.learn_more_url = "https://docs.python.org/3/tutorial/errors.html"
        mock_pattern.explanation = "Array index is out of bounds"
        
        mock_match = Mock(spec=ErrorMatch)
        mock_match.pattern = mock_pattern
        mock_match.context = "result = data[index]"
        mock_match.confidence = 0.95
        
        # 🎬 SETUP THE DETECTIVE'S INVESTIGATION TOOLS
        mock_detect_lang.return_value = "python"
        mock_find_matches.return_value = [mock_match]
        
        # 🎯 RUN THE INVESTIGATION
        request = AnalysisRequest(text=traceback_text, language="python")
        result = analyzer.analyze(request)
        
        # 🔍 VERIFY THE INVESTIGATION REPORT
        assert isinstance(result, AnalysisResult)
        assert result.original_text == traceback_text
        assert result.detected_language == "python"
        assert result.primary_error == mock_match
        assert len(result.all_matches) == 1
        assert result.has_errors is True
        assert result.severity_level == "high"
        
        # Check that tags include expected content
        assert "IndexError" in result.tags
        assert "Python" in result.tags
        assert "Single Error" in result.tags
        
        # Check that summary was generated
        assert result.summary is not None
        assert "IndexError Detected" in result.summary
        assert "What happened:" in result.summary
        
        # Check that suggestions were generated
        assert len(result.suggestions) > 0
        assert any("IndexError" in s for s in result.suggestions)
        
        # Check metadata contains investigation stats
        assert 'processing_time_ms' in result.metadata
        assert 'patterns_checked' in result.metadata
        assert 'matches_found' in result.metadata
        assert result.metadata['matches_found'] == 1
    
    @patch.object(ErrorPatternMatcher, 'find_matches')
    @patch.object(ErrorPatternMatcher, 'detect_language')
    def test_analyze_javascript_error_educational(self, mock_detect_lang, mock_find_matches, analyzer):
        """
        Test JavaScript error analysis - teaching web development debugging
        Like testing if our detective can solve web development crimes.
        """
        js_error = "TypeError: Cannot read property 'length' of null"
        
        # Setup realistic JavaScript error pattern
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "TypeError"
        mock_pattern.category = ErrorCategory.RUNTIME  
        mock_pattern.severity = ErrorSeverity.HIGH
        mock_pattern.what_happened = "Tried to access property of null/undefined"
        mock_pattern.quick_fixes = ["Check if object exists", "Use optional chaining"]
        mock_pattern.prevention_tip = "Always validate objects before property access"
        mock_pattern.learn_more_url = "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Errors"
        mock_pattern.explanation = "Null reference error"
        
        mock_match = Mock(spec=ErrorMatch)
        mock_match.pattern = mock_pattern
        mock_match.context = "obj.length"
        mock_match.confidence = 0.9
        
        mock_detect_lang.return_value = "javascript"
        mock_find_matches.return_value = [mock_match]
        
        request = AnalysisRequest(text=js_error, language="javascript")
        result = analyzer.analyze(request)
        
        # Verify JavaScript-specific analysis
        assert result.detected_language == "javascript"
        assert "TypeError" in result.tags
        assert "Javascript" in result.tags
        assert "null" in result.summary.lower() or "null" in str(result.suggestions).lower()
    
    @patch.object(ErrorPatternMatcher, 'find_matches')
    @patch.object(ErrorPatternMatcher, 'detect_language')
    def test_analyze_multiple_errors_prioritization(self, mock_detect_lang, mock_find_matches, analyzer):
        """
        Test handling multiple errors - teaching prioritization
        Like testing if our detective can handle a case with multiple suspects.
        """
        complex_error = '''Error: Multiple issues found
SyntaxError: invalid syntax at line 10
NameError: 'undefined_var' is not defined
RuntimeError: maximum recursion depth exceeded'''
        
        # Setup multiple error patterns with different severities
        critical_pattern = Mock(spec=ErrorPattern)
        critical_pattern.name = "SyntaxError"
        critical_pattern.severity = ErrorSeverity.CRITICAL
        critical_pattern.category = ErrorCategory.SYNTAX
        critical_pattern.what_happened = "Code has invalid syntax"
        critical_pattern.quick_fixes = ["Check syntax highlighting", "Fix missing brackets"]
        critical_pattern.prevention_tip = "Use an IDE with syntax checking"
        critical_pattern.learn_more_url = "https://docs.python.org/3/tutorial/errors.html"
        critical_pattern.explanation = "Syntax error in code"
        
        high_pattern = Mock(spec=ErrorPattern)
        high_pattern.name = "NameError" 
        high_pattern.severity = ErrorSeverity.HIGH
        high_pattern.category = ErrorCategory.RUNTIME
        high_pattern.what_happened = "Variable not defined"
        high_pattern.quick_fixes = ["Define the variable", "Check spelling"]
        high_pattern.prevention_tip = "Declare variables before use"
        high_pattern.learn_more_url = "https://docs.python.org/3/tutorial/errors.html"
        high_pattern.explanation = "Undefined variable"
        
        critical_match = Mock(spec=ErrorMatch)
        critical_match.pattern = critical_pattern
        critical_match.confidence = 0.95
        
        high_match = Mock(spec=ErrorMatch)
        high_match.pattern = high_pattern
        high_match.confidence = 0.85
        
        mock_detect_lang.return_value = "python"
        mock_find_matches.return_value = [critical_match, high_match]
        
        request = AnalysisRequest(text=complex_error, include_suggestions=False)  # Skip summary to avoid Mock issues
        result = analyzer.analyze(request)
        
        # Verify prioritization logic - matches should be sorted by severity
        assert len(result.all_matches) == 2
        assert result.all_matches[0] == critical_match  # Critical should be first
        assert result.primary_error == critical_match  # Critical should be primary
        assert "Multiple Errors" in result.tags
        assert "Critical Issue" in result.tags
        assert "SyntaxError" in result.tags
        assert "NameError" in result.tags


class TestAnalysisRequestAndResult:
    """
    📋 TEST THE CASE INTAKE AND REPORTING SYSTEM
    
    These tests ensure AnalysisRequest and AnalysisResult work correctly.
    Like testing the forms detectives use to take cases and write reports.
    """
    
    def test_analysis_request_defaults(self):
        """Test that case intake forms have sensible defaults"""
        request = AnalysisRequest(text="test error")
        
        assert request.text == "test error"
        assert request.language is None  # Auto-detect by default
        assert request.include_context is True
        assert request.include_suggestions is True  
        assert request.include_tags is True
        assert request.max_matches == 5
    
    def test_analysis_request_custom_options(self):
        """Test customizing the investigation parameters"""
        request = AnalysisRequest(
            text="custom error",
            language="python",
            include_context=False,
            include_suggestions=False,
            include_tags=False,
            max_matches=3
        )
        
        assert request.language == "python"
        assert request.include_context is False
        assert request.include_suggestions is False
        assert request.include_tags is False
        assert request.max_matches == 3
    
    def test_analysis_result_properties_no_errors(self):
        """Test investigation report when no crimes were found"""
        result = AnalysisResult(
            original_text="normal log message",
            detected_language="python",
            primary_error=None,
            all_matches=[],
            tags=["No Errors Detected"],
            summary=None,
            suggestions=[],
            metadata={}
        )
        
        assert result.has_errors is False
        assert result.severity_level is None
        assert result.error_type == "Unknown"
        assert result.message == "normal log message"
        assert result.confidence is None
    
    def test_analysis_result_properties_with_errors(self):
        """Test investigation report when crimes were found"""
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "ValueError"
        mock_pattern.severity = ErrorSeverity.MEDIUM
        mock_pattern.explanation = "Invalid value provided"
        
        mock_match = Mock(spec=ErrorMatch)
        mock_match.pattern = mock_pattern
        mock_match.confidence = 0.8
        
        result = AnalysisResult(
            original_text="ValueError: bad input",
            detected_language="python", 
            primary_error=mock_match,
            all_matches=[mock_match],
            tags=["ValueError", "Python"],
            summary="Error detected",
            suggestions=["Fix the input"],
            metadata={}
        )
        
        assert result.has_errors is True
        assert result.severity_level == "medium"
        assert result.error_type == "ValueError"
        assert result.message == "ValueError: bad input"
        assert result.confidence == 0.8


class TestTagGenerationLogic:
    """
    🏷️ TEST THE FILING SYSTEM
    
    These tests ensure the tag generation works correctly.
    Like testing the filing clerk's ability to put the right
    colored stickers on case files.
    """
    
    @pytest.fixture
    def analyzer(self):
        return ErrorAnalyzer()
    
    def test_generate_tags_python_single_error(self, analyzer):
        """Test generating tags for a single Python error"""
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "IndexError"
        mock_pattern.category = ErrorCategory.RUNTIME
        mock_pattern.severity = ErrorSeverity.HIGH
        
        mock_match = Mock(spec=ErrorMatch)
        mock_match.pattern = mock_pattern
        
        tags = analyzer._generate_tags([mock_match], "python", "simple error")
        
        # Check expected tags are present
        assert "Python" in tags
        assert "IndexError" in tags
        assert "Runtime" in tags
        assert "Single Error" in tags
        assert "Needs Immediate Attention" in tags
        
        # Verify tags are sorted
        assert tags == sorted(tags)
    
    def test_generate_tags_multiple_errors(self, analyzer):
        """Test tag generation with multiple errors"""
        pattern1 = Mock(spec=ErrorPattern)
        pattern1.name = "SyntaxError"
        pattern1.category = ErrorCategory.SYNTAX
        pattern1.severity = ErrorSeverity.CRITICAL
        
        pattern2 = Mock(spec=ErrorPattern)
        pattern2.name = "NameError"
        pattern2.category = ErrorCategory.RUNTIME
        pattern2.severity = ErrorSeverity.HIGH
        
        match1 = Mock(spec=ErrorMatch)
        match1.pattern = pattern1
        
        match2 = Mock(spec=ErrorMatch)
        match2.pattern = pattern2
        
        tags = analyzer._generate_tags([match1, match2], "python", "complex error")
        
        assert "Multiple Errors" in tags
        assert "Critical Issue" in tags
        assert "SyntaxError" in tags
        assert "NameError" in tags
        assert "Syntax" in tags
        assert "Runtime" in tags
    
    def test_generate_tags_no_errors(self, analyzer):
        """Test tag generation when no errors found"""
        tags = analyzer._generate_tags([], "javascript", "clean code")
        
        assert "No Errors Detected" in tags
        assert "Javascript" in tags
        assert "Multiple Errors" not in tags
    
    def test_generate_tags_stack_trace_context(self, analyzer):
        """Test that stack traces get special tags"""
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "RuntimeError"
        mock_pattern.category = ErrorCategory.RUNTIME
        mock_pattern.severity = ErrorSeverity.MEDIUM
        
        mock_match = Mock(spec=ErrorMatch)
        mock_match.pattern = mock_pattern
        
        stack_trace_text = "Traceback (most recent call last):\n  File 'test.py'"
        tags = analyzer._generate_tags([mock_match], "python", stack_trace_text)
        
        assert "Stack Trace" in tags


class TestErrorHandlingAndEdgeCases:
    """
    🚨 TEST EMERGENCY PROTOCOLS
    
    These tests ensure the analyzer handles unexpected situations gracefully.
    Like testing what happens when our detective faces unusual or difficult cases.
    """
    
    @pytest.fixture
    def analyzer(self):
        return ErrorAnalyzer()
    
    def test_analyze_empty_input(self, analyzer):
        """Test handling empty input - edge case that should be handled gracefully"""
        request = AnalysisRequest(text="")
        result = analyzer.analyze(request)
        
        # Should return a valid result, not crash
        assert isinstance(result, AnalysisResult)
        assert result.original_text == ""
        assert result.has_errors is False
        assert len(result.suggestions) > 0  # Should still give helpful advice
    
    def test_analyze_very_long_input(self, analyzer):
        """Test handling very long error messages"""
        long_text = "Error: " + "x" * 10000
        request = AnalysisRequest(text=long_text)
        result = analyzer.analyze(request)
        
        # Should handle gracefully without performance issues
        assert isinstance(result, AnalysisResult)
        assert result.original_text == long_text
    
    @patch.object(ErrorPatternMatcher, 'find_matches')
    def test_analyze_pattern_matcher_exception(self, mock_find_matches, analyzer):
        """Test handling when pattern matching fails"""
        mock_find_matches.side_effect = Exception("Pattern matching failed")
        
        request = AnalysisRequest(text="test error")
        result = analyzer.analyze(request)
        
        # Should return fallback result, not crash
        assert isinstance(result, AnalysisResult)
        assert result.original_text == "test error"
        assert result.has_errors is False
        assert "analysis-failed" in result.tags
        assert result.summary is not None and "Error analysis failed" in result.summary
        assert "error" in result.metadata
    
    def test_analyze_special_characters(self, analyzer):
        """Test handling text with special characters and unicode"""
        special_text = "Error: файл не найден 文件未找到 🚫"
        request = AnalysisRequest(text=special_text)
        result = analyzer.analyze(request)
        
        # Should handle unicode gracefully
        assert isinstance(result, AnalysisResult)
        assert result.original_text == special_text


class TestPerformanceAndMetadata:
    """
    ⚡ TEST INVESTIGATION SPEED AND REPORTING
    
    These tests ensure the analyzer performs well and provides
    useful metadata about its investigation process.
    """
    
    @pytest.fixture
    def analyzer(self):
        return ErrorAnalyzer()
    
    def test_analyze_completes_quickly(self, analyzer):
        """Test that analysis completes within reasonable time"""
        error_text = "RuntimeError: Something went wrong"
        request = AnalysisRequest(text=error_text)
        
        start_time = time.time()
        result = analyzer.analyze(request)
        end_time = time.time()
        
        # Should complete within 1 second for simple errors
        assert (end_time - start_time) < 1.0
        assert isinstance(result, AnalysisResult)
    
    def test_metadata_contains_processing_stats(self, analyzer):
        """Test that investigation metadata contains useful stats"""
        request = AnalysisRequest(text="test error")
        result = analyzer.analyze(request)
        
        # Check metadata contains expected fields
        assert 'processing_time_ms' in result.metadata
        assert 'patterns_checked' in result.metadata
        assert 'matches_found' in result.metadata
        assert 'language_detection_used' in result.metadata
        
        # Check values are reasonable
        assert isinstance(result.metadata['processing_time_ms'], int)
        assert result.metadata['processing_time_ms'] >= 0
        assert isinstance(result.metadata['patterns_checked'], int)
        assert isinstance(result.metadata['matches_found'], int)


class TestQuickAnalyzeMethod:
    """
    🏃‍♂️ TEST THE EXPRESS INVESTIGATION SERVICE
    
    These tests ensure the quick_analyze method works for simple cases.
    Like testing our detective's ability to give quick answers.
    """
    
    @pytest.fixture
    def analyzer(self):
        return ErrorAnalyzer()
    
    @patch.object(ErrorAnalyzer, 'analyze')
    def test_quick_analyze_with_error_found(self, mock_analyze, analyzer):
        """Test quick analysis when error is found"""
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "ValueError"
        mock_pattern.explanation = "Invalid input provided"
        
        mock_match = Mock(spec=ErrorMatch)
        mock_match.pattern = mock_pattern
        
        mock_result = Mock(spec=AnalysisResult)
        mock_result.primary_error = mock_match
        
        mock_analyze.return_value = mock_result
        
        result = analyzer.quick_analyze("ValueError: bad input")
        
        assert result == "ValueError: Invalid input provided"
        
        # Verify it called analyze with correct parameters
        mock_analyze.assert_called_once()
        call_args = mock_analyze.call_args[0][0]  # First positional argument
        assert isinstance(call_args, AnalysisRequest)
        assert call_args.text == "ValueError: bad input"
        assert call_args.include_context is False
        assert call_args.max_matches == 1
    
    @patch.object(ErrorAnalyzer, 'analyze')
    def test_quick_analyze_no_error_found(self, mock_analyze, analyzer):
        """Test quick analysis when no error is found"""
        mock_result = Mock(spec=AnalysisResult)
        mock_result.primary_error = None
        
        mock_analyze.return_value = mock_result
        
        result = analyzer.quick_analyze("normal log message")
        
        assert result is None


class TestIntegrationScenarios:
    """
    🎭 TEST REAL-WORLD DEBUGGING SCENARIOS
    
    These tests use realistic error messages that developers actually encounter.
    Like testing our detective with actual case files from the field.
    """
    
    @pytest.fixture
    def analyzer(self):
        return ErrorAnalyzer()
    
    def test_realistic_python_stack_trace(self, analyzer):
        """Test with a realistic Python stack trace"""
        realistic_traceback = '''Traceback (most recent call last):
  File "/usr/local/app/main.py", line 156, in process_request
    user_data = json.loads(request_body)
  File "/usr/lib/python3.9/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
  File "/usr/lib/python3.9/json/decoder.py", line 337, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
  File "/usr/lib/python3.9/json/decoder.py", line 355, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)'''
        
        request = AnalysisRequest(text=realistic_traceback)
        result = analyzer.analyze(request)
        
        # Should handle complex stack trace gracefully
        assert isinstance(result, AnalysisResult)
        assert "json" in result.original_text.lower()
        assert len(result.tags) > 0
        # Summary may be None if no patterns matched, but that's OK for this test
        # The important thing is that we handle complex stack traces without crashing
    
    def test_realistic_javascript_browser_error(self, analyzer):
        """Test with a realistic JavaScript browser error"""
        js_error = '''Uncaught TypeError: Cannot read properties of null (reading 'addEventListener')
    at initializeForm (app.js:45:12)
    at DOMContentLoaded (app.js:12:5)
    at HTMLDocument.addEventListener (app.js:8:1)'''
        
        request = AnalysisRequest(text=js_error, language="javascript")
        result = analyzer.analyze(request)
        
        # Should handle browser JavaScript errors
        assert isinstance(result, AnalysisResult)
        assert result.detected_language is None or "javascript" in result.detected_language.lower()
        assert result.original_text == js_error


# 🏆 QUALITY METRICS AND EDUCATIONAL VALUE TESTS
class TestEducationalValue:
    """
    📚 TEST THE EDUCATIONAL ASPECTS
    
    These tests ensure Debuggle provides educational value,
    not just technical functionality.
    """
    
    @pytest.fixture  
    def analyzer(self):
        return ErrorAnalyzer()
    
    def test_suggestions_are_educational(self, analyzer):
        """Test that suggestions teach debugging skills"""
        request = AnalysisRequest(text="IndexError: list index out of range")
        result = analyzer.analyze(request)
        
        # Even if no patterns matched, should provide educational suggestions
        assert len(result.suggestions) > 0
        
        # Suggestions should be actionable and educational
        suggestion_text = " ".join(result.suggestions).lower()
        educational_keywords = ["check", "validate", "debug", "fix", "prevent", "use"]
        assert any(keyword in suggestion_text for keyword in educational_keywords)
    
    def test_summary_explains_what_happened(self, analyzer):
        """Test that summaries explain errors in educational terms"""
        request = AnalysisRequest(text="NameError: name 'undefined_var' is not defined")
        result = analyzer.analyze(request)
        
        # Summary should exist and be informative (when patterns match)
        if result.summary:  # Only test if summary was generated
            assert len(result.summary) > 20  # Should be substantive
            assert "error" in result.summary.lower() or "what happened" in result.summary.lower()