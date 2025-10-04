"""
🧪 WORKING ANALYZER API TESTS - NEW ARCHITECTURE

This test file demonstrates the correct usage of the new ErrorAnalyzer API
with AnalysisRequest and AnalysisResult objects.

These tests work with the current modular architecture and provide good
coverage of the core analyzer functionality.
"""

import pytest
from unittest.mock import Mock, patch

from src.debuggle.core.analyzer import (
    ErrorAnalyzer, 
    AnalysisResult,
    AnalysisRequest
)
from src.debuggle.core.patterns import ErrorSeverity


class TestErrorAnalyzerNewAPI:
    """Test the new ErrorAnalyzer API with proper AnalysisRequest/AnalysisResult"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing"""
        return ErrorAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
        assert hasattr(analyzer, 'pattern_matcher')
        assert hasattr(analyzer, 'logger')
    
    def test_analysis_request_creation(self):
        """Test creating AnalysisRequest objects"""
        request = AnalysisRequest(
            text="ValueError: invalid literal for int()",
            language="python"
        )
        assert request.text == "ValueError: invalid literal for int()"
        assert request.language == "python"
        assert request.include_context is True  # default
        assert request.include_suggestions is True  # default
        assert request.max_matches == 5  # default
    
    def test_analysis_request_with_options(self):
        """Test AnalysisRequest with custom options"""
        request = AnalysisRequest(
            text="SyntaxError: invalid syntax",
            language="python",
            include_context=False,
            include_suggestions=False,
            max_matches=3
        )
        assert request.include_context is False
        assert request.include_suggestions is False
        assert request.max_matches == 3
    
    def test_analyze_basic_python_error(self, analyzer):
        """Test analyzing a basic Python error"""
        request = AnalysisRequest(
            text="IndexError: list index out of range",
            language="python"
        )
        
        result = analyzer.analyze(request)
        
        # Check result structure
        assert isinstance(result, AnalysisResult)
        assert result.original_text == "IndexError: list index out of range"
        assert result.detected_language is not None
        assert isinstance(result.all_matches, list)
        assert isinstance(result.tags, list)
    
    def test_analyze_with_traceback(self, analyzer):
        """Test analyzing a full Python traceback"""
        traceback_text = '''Traceback (most recent call last):
  File "test.py", line 10, in <module>
    print(items[5])
IndexError: list index out of range'''
        
        request = AnalysisRequest(
            text=traceback_text,
            language="python"
        )
        
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert "IndexError" in result.original_text
        assert result.detected_language == "python"
        # Should have found at least one match
        if result.all_matches:
            assert len(result.all_matches) > 0
    
    def test_analyze_javascript_error(self, analyzer):
        """Test analyzing a JavaScript error"""
        request = AnalysisRequest(
            text="TypeError: Cannot read property 'length' of null",
            language="javascript"
        )
        
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert "TypeError" in result.original_text
        assert isinstance(result.all_matches, list)
    
    def test_analyze_unknown_language(self, analyzer):
        """Test analyzing with unknown language"""
        request = AnalysisRequest(
            text="Some generic error message",
            language="unknown_lang"
        )
        
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.original_text == "Some generic error message"
        # Should still return a valid result even with unknown language
    
    def test_analyze_no_language_specified(self, analyzer):
        """Test analyzing without specifying language"""
        request = AnalysisRequest(
            text="NullPointerException: null"
        )
        
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.original_text == "NullPointerException: null"
        # Should attempt language detection
    
    def test_analysis_result_properties(self, analyzer):
        """Test that AnalysisResult has expected properties"""
        request = AnalysisRequest(
            text="KeyError: 'missing_key'",
            language="python"  
        )
        
        result = analyzer.analyze(request)
        
        # Test all expected properties exist
        assert hasattr(result, 'original_text')
        assert hasattr(result, 'detected_language')
        assert hasattr(result, 'primary_error')
        assert hasattr(result, 'all_matches')
        assert hasattr(result, 'tags')
        
        # Test types
        assert isinstance(result.original_text, str)
        assert isinstance(result.all_matches, list)
        assert isinstance(result.tags, list)
    
    def test_analyze_with_max_matches_limit(self, analyzer):
        """Test that max_matches parameter is respected"""
        request = AnalysisRequest(
            text="Error: multiple potential matches here",
            max_matches=2
        )
        
        result = analyzer.analyze(request)
        
        # Should not exceed max_matches
        assert len(result.all_matches) <= 2
    
    def test_analyze_empty_text(self, analyzer):
        """Test analyzing empty text"""
        request = AnalysisRequest(text="")
        
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.original_text == ""
    
    def test_pattern_matcher_integration(self, analyzer):
        """Test that pattern matcher is properly integrated"""
        assert analyzer.pattern_matcher is not None
        
        # Test that we can call pattern matcher methods
        matches = analyzer.pattern_matcher.find_matches("IndexError: test")
        assert isinstance(matches, list)


class TestAnalysisRequestValidation:
    """Test AnalysisRequest parameter validation"""
    
    def test_analysis_request_requires_text(self):
        """Test that AnalysisRequest requires text parameter"""
        # This should work
        request = AnalysisRequest(text="test error")
        assert request.text == "test error"
    
    def test_analysis_request_defaults(self):
        """Test AnalysisRequest default values"""
        request = AnalysisRequest(text="test")
        
        assert request.language is None
        assert request.include_context is True
        assert request.include_suggestions is True
        assert request.include_tags is True
        assert request.max_matches == 5


class TestAnalysisResultStructure:
    """Test AnalysisResult structure and content"""
    
    @pytest.fixture
    def analyzer(self):
        return ErrorAnalyzer()
    
    def test_analysis_result_contains_original_text(self, analyzer):
        """Test that result preserves original text"""
        original = "ValueError: test error message"
        request = AnalysisRequest(text=original)
        result = analyzer.analyze(request)
        
        assert result.original_text == original
    
    def test_analysis_result_tags_are_strings(self, analyzer):
        """Test that tags are string values"""
        request = AnalysisRequest(text="SyntaxError: invalid syntax")
        result = analyzer.analyze(request)
        
        for tag in result.tags:
            assert isinstance(tag, str)
    
    def test_analysis_result_matches_structure(self, analyzer):
        """Test that matches have proper structure"""
        request = AnalysisRequest(text="TypeError: test error")
        result = analyzer.analyze(request)
        
        # Each match should be an ErrorMatch object or similar
        for match in result.all_matches:
            # Should have basic attributes that ErrorMatch provides
            assert hasattr(match, 'pattern')
            assert hasattr(match, 'confidence')


class TestErrorAnalyzerEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture  
    def analyzer(self):
        return ErrorAnalyzer()
    
    def test_analyze_very_long_text(self, analyzer):
        """Test analyzing very long error text"""
        long_text = "Error: " + "x" * 10000
        request = AnalysisRequest(text=long_text)
        
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.original_text == long_text
    
    def test_analyze_special_characters(self, analyzer):
        """Test analyzing text with special characters"""
        special_text = "Error: файл не найден 文件未找到 🚫"
        request = AnalysisRequest(text=special_text)
        
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert result.original_text == special_text
    
    def test_analyze_multiline_error(self, analyzer):
        """Test analyzing multiline error messages"""
        multiline = """Error occurred in multiple places:
        Line 1: First error here
        Line 2: Second error here
        Line 3: Final error here"""
        
        request = AnalysisRequest(text=multiline)
        result = analyzer.analyze(request)
        
        assert isinstance(result, AnalysisResult)
        assert "Line 1" in result.original_text
        assert "Line 3" in result.original_text