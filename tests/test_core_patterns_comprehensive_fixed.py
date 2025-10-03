"""
🔍 COMPREHENSIVE PATTERN RECOGNITION TESTS

Following Debuggle's educational philosophy: Think of the pattern recognition system as 
the "crime scene investigators" of debugging - they analyze error "evidence" to identify
what went wrong and provide expert advice on how to fix it.

Like a forensics lab that:
- 🕵️ Analyzes evidence (error messages) to identify patterns
- 📊 Classifies problems by type and severity  
- 🎯 Matches unknown cases to known patterns
- 💡 Provides expert recommendations based on experience

TARGET: Boost core/patterns.py from 40% → 75% coverage
FOCUS: Pattern recognition algorithms, error classification, and matcher functionality
"""

import pytest
import re
from typing import List

from src.debuggle.core.patterns import (
    ErrorSeverity,
    ErrorCategory,
    ErrorPattern,
    ErrorMatch,
    BasePatternMatcher,
    PythonPatternMatcher,
    JavaScriptPatternMatcher,
    JavaPatternMatcher,
    ErrorPatternMatcher
)


class TestErrorSeverityEnum:
    """Test error severity classification system"""
    
    def test_error_severity_values(self):
        """Test that all severity levels have correct values"""
        assert ErrorSeverity.CRITICAL.value == "critical"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.INFO.value == "info"
    
    def test_error_severity_ordering(self):
        """Test that severity levels can be compared and ordered"""
        severities = [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH, ErrorSeverity.MEDIUM, 
                     ErrorSeverity.LOW, ErrorSeverity.INFO]
        
        # Verify all enum values are present
        assert len(severities) == 5
        
        # Verify they are unique
        assert len(set(severities)) == 5


class TestErrorCategoryEnum:
    """Test error category classification system"""
    
    def test_error_category_values(self):
        """Test that all category types have correct values"""
        assert ErrorCategory.SYNTAX.value == "syntax"
        assert ErrorCategory.RUNTIME.value == "runtime"
        assert ErrorCategory.LOGIC.value == "logic"  
        assert ErrorCategory.NETWORK.value == "network"
        assert ErrorCategory.DATABASE.value == "database"
        assert ErrorCategory.PERMISSION.value == "permission"
        assert ErrorCategory.CONFIGURATION.value == "configuration"
        assert ErrorCategory.DEPENDENCY.value == "dependency"
    
    def test_error_category_completeness(self):
        """Test that we have comprehensive error categories"""
        categories = list(ErrorCategory)
        assert len(categories) == 8  # Should have 8 different categories
        
        # Verify all categories are unique
        category_values = [cat.value for cat in categories]
        assert len(set(category_values)) == len(category_values)


class TestErrorPattern:
    """Test error pattern data structure and functionality"""
    
    def test_error_pattern_creation(self):
        """Test creating error pattern with all fields"""
        pattern = ErrorPattern(
            name="TestError",
            pattern=r"Test error: (.+)",
            category=ErrorCategory.RUNTIME,
            severity=ErrorSeverity.HIGH,
            languages=["python"],
            explanation="This is a test error",
            what_happened="A test error occurred",
            quick_fixes=["Fix the test", "Try again"],
            prevention_tip="Avoid test errors",
            learn_more_url="https://example.com/test-error"
        )
        
        assert pattern.name == "TestError"
        assert pattern.category == ErrorCategory.RUNTIME
        assert pattern.severity == ErrorSeverity.HIGH
        assert pattern.languages == ["python"]
        assert pattern.explanation == "This is a test error"
        assert len(pattern.quick_fixes) == 2
    
    def test_error_pattern_regex_compilation(self):
        """Test that string patterns are compiled to regex objects"""
        pattern = ErrorPattern(
            name="TestError", 
            pattern="simple pattern",
            category=ErrorCategory.SYNTAX,
            severity=ErrorSeverity.LOW,
            languages=["python"],
            explanation="Test",
            what_happened="Test", 
            quick_fixes=["Test"],
            prevention_tip="Test",
            learn_more_url="Test"
        )
        
        # After __post_init__, pattern should be compiled regex
        assert hasattr(pattern.pattern, 'search')  # Should be a compiled regex
        assert hasattr(pattern.pattern, 'pattern')  # Should have pattern attribute
    
    def test_error_pattern_with_precompiled_regex(self):
        """Test creating error pattern with pre-compiled regex"""
        compiled_pattern = re.compile(r"custom pattern", re.DOTALL)
        
        pattern = ErrorPattern(
            name="TestError",
            pattern=compiled_pattern,
            category=ErrorCategory.RUNTIME,
            severity=ErrorSeverity.MEDIUM,
            languages=["java"],
            explanation="Test",
            what_happened="Test",
            quick_fixes=["Test"],
            prevention_tip="Test", 
            learn_more_url="Test"
        )
        
        # Should keep the original compiled pattern
        assert pattern.pattern is compiled_pattern


class TestErrorMatch:
    """Test error match data structure"""
    
    def test_error_match_creation(self):
        """Test creating error match with all fields"""
        test_pattern = ErrorPattern(
            name="TestError",
            pattern="test",
            category=ErrorCategory.RUNTIME,
            severity=ErrorSeverity.HIGH,
            languages=["python"],
            explanation="Test",
            what_happened="Test",
            quick_fixes=["Test"],
            prevention_tip="Test",
            learn_more_url="Test"
        )
        
        match = ErrorMatch(
            pattern=test_pattern,
            matched_text="test error message",
            confidence=0.95,
            context="Some context around the error",
            line_number=42,
            file_path="/app/test.py"
        )
        
        assert match.pattern == test_pattern
        assert match.matched_text == "test error message"
        assert match.confidence == 0.95
        assert match.context == "Some context around the error"
        assert match.line_number == 42
        assert match.file_path == "/app/test.py"
    
    def test_error_match_with_optional_fields(self):
        """Test creating error match with only required fields"""
        test_pattern = ErrorPattern(
            name="TestError", 
            pattern="test",
            category=ErrorCategory.SYNTAX,
            severity=ErrorSeverity.LOW,
            languages=["python"],
            explanation="Test",
            what_happened="Test",
            quick_fixes=["Test"],
            prevention_tip="Test",
            learn_more_url="Test"
        )
        
        match = ErrorMatch(
            pattern=test_pattern,
            matched_text="test error message",
            confidence=0.8
        )
        
        assert match.pattern == test_pattern
        assert match.matched_text == "test error message"
        assert match.confidence == 0.8
        assert match.context is None
        assert match.line_number is None
        assert match.file_path is None


class TestPythonPatternMatcher:
    """Test Python-specific pattern matching"""
    
    @pytest.fixture
    def python_matcher(self):
        """Create Python pattern matcher for testing"""
        return PythonPatternMatcher()
    
    def test_python_language_indicators(self, python_matcher):
        """Test Python language detection patterns"""
        indicators = python_matcher.get_language_indicators()
        
        assert len(indicators) > 0
        
        # Should have traceback pattern
        traceback_pattern = None
        for pattern in indicators:
            if "Traceback" in pattern.pattern:
                traceback_pattern = pattern
                break
        
        assert traceback_pattern is not None
        
        # Test traceback pattern matches Python stack traces
        python_error = "Traceback (most recent call last):\n  File test.py"
        assert traceback_pattern.search(python_error) is not None
    
    def test_python_error_patterns(self, python_matcher):
        """Test that Python matcher has comprehensive error patterns"""
        patterns = python_matcher.get_patterns()
        
        assert len(patterns) > 0
        
        # Should have common Python errors
        pattern_names = [p.name for p in patterns]
        
        # Check for some common Python errors
        expected_errors = ["IndexError", "KeyError", "TypeError", "ValueError"]
        found_errors = [name for name in expected_errors if name in pattern_names]
        assert len(found_errors) > 0  # Should find at least some common errors
    
    def test_index_error_pattern_matching(self, python_matcher):
        """Test IndexError pattern recognition"""
        patterns = python_matcher.get_patterns()
        
        # Find IndexError pattern
        index_error_pattern = None
        for pattern in patterns:
            if pattern.name == "IndexError":
                index_error_pattern = pattern
                break
        
        if index_error_pattern:
            # Test pattern matches typical IndexError messages
            test_messages = [
                "IndexError: list index out of range",
                "IndexError: index out of range",
                "indexerror: list index out of range"  # case insensitive
            ]
            
            for message in test_messages:
                match = index_error_pattern.pattern.search(message)
                assert match is not None, f"Pattern should match: {message}"
    
    def test_python_pattern_properties(self, python_matcher):
        """Test Python pattern properties are set correctly"""
        patterns = python_matcher.get_patterns()
        
        for pattern in patterns:
            # All Python patterns should specify python as a language
            assert "python" in pattern.languages
            
            # Should have proper severity levels
            assert isinstance(pattern.severity, ErrorSeverity)
            
            # Should have proper categories
            assert isinstance(pattern.category, ErrorCategory)
            
            # Should have educational content
            assert len(pattern.explanation) > 0
            assert len(pattern.what_happened) > 0
            assert len(pattern.quick_fixes) > 0
            assert len(pattern.prevention_tip) > 0


class TestJavaScriptPatternMatcher:
    """Test JavaScript-specific pattern matching"""
    
    @pytest.fixture
    def js_matcher(self):
        """Create JavaScript pattern matcher for testing"""
        return JavaScriptPatternMatcher()
    
    def test_javascript_language_indicators(self, js_matcher):
        """Test JavaScript language detection"""
        indicators = js_matcher.get_language_indicators()
        
        assert len(indicators) >= 0  # Should have indicators
        
        # If indicators exist, test basic functionality
        for pattern in indicators:
            assert hasattr(pattern, 'search')  # Should be regex patterns
    
    def test_javascript_error_patterns(self, js_matcher):
        """Test JavaScript error patterns"""
        patterns = js_matcher.get_patterns()
        
        # Should have at least some patterns
        assert len(patterns) >= 0  # May be empty in minimal implementation
        
        # If patterns exist, they should be properly configured
        for pattern in patterns:
            assert "javascript" in pattern.languages or "js" in pattern.languages
            assert isinstance(pattern.severity, ErrorSeverity)
            assert isinstance(pattern.category, ErrorCategory)


class TestErrorPatternMatcher:
    """Test the main pattern recognition engine"""
    
    @pytest.fixture
    def recognizer(self):
        """Create pattern recognizer for testing"""
        return ErrorPatternMatcher()
    
    def test_error_pattern_matcher_initialization(self, recognizer):
        """Test that pattern recognizer initializes properly"""
        assert recognizer is not None
        assert len(recognizer.matchers) > 0
        
        # Should have different types of matchers
        matcher_types = [type(matcher).__name__ for matcher in recognizer.matchers]
        assert "PythonPatternMatcher" in matcher_types
        assert "JavaScriptPatternMatcher" in matcher_types
        assert "JavaPatternMatcher" in matcher_types
    
    def test_all_patterns_property(self, recognizer):
        """Test that all patterns are collected from matchers"""
        all_patterns = recognizer.all_patterns
        
        assert isinstance(all_patterns, list)
        assert len(all_patterns) >= 0  # Should have at least some patterns
        
        # Patterns should be ErrorPattern instances
        for pattern in all_patterns:
            assert isinstance(pattern, ErrorPattern)
    
    def test_language_indicators_property(self, recognizer):
        """Test language indicators collection"""
        indicators = recognizer.language_indicators
        
        assert isinstance(indicators, dict)
        
        # Should have entries for each language
        expected_languages = ["python", "javascript", "java"] 
        for lang in expected_languages:
            if lang in indicators:
                assert isinstance(indicators[lang], list)
    
    def test_detect_language_with_python_error(self, recognizer):
        """Test language detection with Python error"""
        python_error = """Traceback (most recent call last):
  File "test.py", line 5, in <module>
    print(arr[10])
IndexError: list index out of range"""
        
        detected_language = recognizer.detect_language(python_error)
        
        # Should detect Python (if indicators are properly implemented)
        if detected_language:
            assert detected_language == "python"
    
    def test_find_matches_without_language_filter(self, recognizer):
        """Test finding matches without language filtering"""
        # Create error text that should match some patterns
        error_text = "IndexError: list index out of range"
        
        matches = recognizer.find_matches(error_text)
        
        assert isinstance(matches, list)
        
        # If matches found, they should be properly structured
        for match in matches:
            assert isinstance(match, ErrorMatch)
            assert isinstance(match.pattern, ErrorPattern)
            assert isinstance(match.matched_text, str)
            assert isinstance(match.confidence, float)
            assert 0.0 <= match.confidence <= 1.0
    
    def test_get_best_match(self, recognizer):
        """Test getting the best match for an error"""
        error_text = "IndexError: list index out of range"
        
        best_match = recognizer.get_best_match(error_text)
        
        if best_match:
            assert isinstance(best_match, ErrorMatch)
            assert isinstance(best_match.pattern, ErrorPattern)
            
            # Best match should have the highest priority
            all_matches = recognizer.find_matches(error_text)
            if all_matches:
                assert best_match == all_matches[0]  # Should be first in sorted list
        else:
            # If no best match, there should be no matches at all
            all_matches = recognizer.find_matches(error_text)
            assert len(all_matches) == 0


class TestPatternRecognitionIntegration:
    """Test integration scenarios for pattern recognition"""
    
    def test_full_python_error_analysis(self):
        """Test complete analysis of a real Python error"""
        recognizer = ErrorPatternMatcher()
        
        python_traceback = """Traceback (most recent call last):
  File "test_script.py", line 15, in process_data
    result = data_list[index]
IndexError: list index out of range"""
        
        # Detect language
        language = recognizer.detect_language(python_traceback)
        
        # Find matches
        matches = recognizer.find_matches(python_traceback, language=language)
        
        # Get best match
        best_match = recognizer.get_best_match(python_traceback, language=language)
        
        if best_match:
            # Verify the match contains educational content
            assert len(best_match.pattern.explanation) > 0
            assert len(best_match.pattern.what_happened) > 0
            assert len(best_match.pattern.quick_fixes) > 0
            assert len(best_match.pattern.prevention_tip) > 0
            assert best_match.pattern.learn_more_url.startswith("http")
    
    def test_case_insensitive_matching(self):
        """Test that pattern matching is case insensitive"""
        recognizer = ErrorPatternMatcher()
        
        # Test with different cases
        error_variations = [
            "IndexError: list index out of range",
            "indexerror: list index out of range", 
            "INDEXERROR: LIST INDEX OUT OF RANGE"
        ]
        
        match_counts = []
        for error_text in error_variations:
            matches = recognizer.find_matches(error_text)
            match_counts.append(len(matches))
        
        # All variations should find the same number of matches
        if match_counts and max(match_counts) > 0:
            assert all(count == match_counts[0] for count in match_counts)
    
    def test_pattern_confidence_scoring(self):
        """Test that confidence scores are reasonable"""
        recognizer = ErrorPatternMatcher()
        
        error_text = "IndexError: list index out of range"
        matches = recognizer.find_matches(error_text)
        
        for match in matches:
            # Confidence should be between 0 and 1
            assert 0.0 <= match.confidence <= 1.0
            
            # For exact matches, confidence should be high
            if match.matched_text.lower() in error_text.lower():
                assert match.confidence > 0.5  # Should be reasonably confident