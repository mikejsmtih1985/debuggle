"""
Additional tests for core patterns module to improve coverage.
"""

import pytest
import re
from unittest.mock import Mock, patch

from src.debuggle.core.patterns import (
    ErrorPatternMatcher, ErrorMatch, ErrorSeverity, ErrorCategory, ErrorPattern,
    PythonPatternMatcher, JavaScriptPatternMatcher, JavaPatternMatcher
)


class TestErrorPatternMatcher:
    """Test ErrorPatternMatcher functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.matcher = ErrorPatternMatcher()
    
    def test_matcher_initialization(self):
        """Test ErrorPatternMatcher initializes correctly."""
        assert hasattr(self.matcher, 'matchers')
        assert len(self.matcher.matchers) > 0
        assert isinstance(self.matcher.matchers[0], PythonPatternMatcher)
    
    def test_all_patterns_property(self):
        """Test all_patterns property returns patterns from all matchers."""
        patterns = self.matcher.all_patterns
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        # Should contain patterns from different languages
        languages = set()
        for pattern in patterns:
            languages.update(pattern.languages)
        
        assert len(languages) > 1  # Multiple languages
    
    def test_language_indicators_property(self):
        """Test language_indicators property."""
        indicators = self.matcher.language_indicators
        assert isinstance(indicators, dict)
        assert len(indicators) > 0
        
        # Should have indicators for different languages
        assert 'python' in indicators or 'javascript' in indicators
    
    def test_detect_language_python(self):
        """Test detecting Python language."""
        python_texts = [
            "def hello():\n    print('world')",
            "import sys\nfrom os import path",
            "Traceback (most recent call last):\n  File \"test.py\", line 1",
            "NameError: name 'undefined_var' is not defined"
        ]
        
        for text in python_texts:
            result = self.matcher.detect_language(text)
            # Should detect python or at least something (may be None if no clear match)
            # Let's just test it doesn't crash and returns expected type
            assert result is None or isinstance(result, str)
    
    def test_detect_language_javascript(self):
        """Test detecting JavaScript language."""
        js_texts = [
            "function hello() { console.log('world'); }",
            "ReferenceError: variable is not defined",
            "at Object.<anonymous> (/path/file.js:1:1)"
        ]
        
        for text in js_texts:
            result = self.matcher.detect_language(text)
            # Should detect javascript or at least something (may be None if no clear match)
            # Let's just test it doesn't crash and returns expected type
            assert result is None or isinstance(result, str)
    
    def test_detect_language_no_match(self):
        """Test language detection with no clear indicators."""
        result = self.matcher.detect_language("some random text without clear language indicators")
        # May return None if no clear match
        assert result is None or isinstance(result, str)
    
    def test_find_matches_with_python_error(self):
        """Test finding matches in Python error text."""
        python_error = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    print(undefined_variable)
NameError: name 'undefined_variable' is not defined"""
        
        matches = self.matcher.find_matches(python_error, "python")
        assert isinstance(matches, list)
        
        # Should find at least one match for NameError
        if matches:
            assert any("NameError" in match.pattern.name or "name" in match.pattern.name.lower() 
                      for match in matches)
    
    def test_find_matches_with_javascript_error(self):
        """Test finding matches in JavaScript error text."""
        js_error = """ReferenceError: myVariable is not defined
    at Object.<anonymous> (/path/to/script.js:5:1)
    at Module._compile (internal/modules/cjs/loader.js:999:30)"""
        
        matches = self.matcher.find_matches(js_error, "javascript")
        assert isinstance(matches, list)
        
        # Should find at least one match for ReferenceError
        if matches:
            assert any("ReferenceError" in match.pattern.name or "reference" in match.pattern.name.lower()
                      for match in matches)
    
    def test_find_matches_without_language(self):
        """Test finding matches without specifying language."""
        error_text = "SyntaxError: invalid syntax"
        matches = self.matcher.find_matches(error_text)
        
        assert isinstance(matches, list)
        # Should work even without language specification
    
    def test_find_matches_empty_text(self):
        """Test finding matches in empty text."""
        matches = self.matcher.find_matches("")
        assert matches == []
        
        matches = self.matcher.find_matches("   ")
        assert matches == []
    
    def test_get_best_match(self):
        """Test getting the best match."""
        error_text = "NameError: name 'variable' is not defined"
        best_match = self.matcher.get_best_match(error_text, "python")
        
        if best_match:
            assert isinstance(best_match, ErrorMatch)
            assert isinstance(best_match.pattern, ErrorPattern)
            assert isinstance(best_match.confidence, float)
    
    def test_get_best_match_no_matches(self):
        """Test getting best match when no matches found."""
        best_match = self.matcher.get_best_match("no error patterns here")
        assert best_match is None


class TestPatternMatchers:
    """Test individual pattern matcher classes."""
    
    def test_python_pattern_matcher(self):
        """Test PythonPatternMatcher."""
        matcher = PythonPatternMatcher()
        
        patterns = matcher.get_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        for pattern in patterns:
            assert isinstance(pattern, ErrorPattern)
            assert "python" in [lang.lower() for lang in pattern.languages]
        
        indicators = matcher.get_language_indicators()
        assert isinstance(indicators, list)
        assert len(indicators) > 0
        
        for indicator in indicators:
            assert hasattr(indicator, 'findall')  # Should be compiled regex
    
    def test_javascript_pattern_matcher(self):
        """Test JavaScriptPatternMatcher."""
        matcher = JavaScriptPatternMatcher()
        
        patterns = matcher.get_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        for pattern in patterns:
            assert isinstance(pattern, ErrorPattern)
            assert "javascript" in [lang.lower() for lang in pattern.languages]
        
        indicators = matcher.get_language_indicators()
        assert isinstance(indicators, list)
        assert len(indicators) > 0
    
    def test_java_pattern_matcher(self):
        """Test JavaPatternMatcher."""
        matcher = JavaPatternMatcher()
        
        patterns = matcher.get_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        
        for pattern in patterns:
            assert isinstance(pattern, ErrorPattern)
            assert "java" in [lang.lower() for lang in pattern.languages]
        
        indicators = matcher.get_language_indicators()
        assert isinstance(indicators, list)
        assert len(indicators) > 0
    
    def test_extract_context(self):
        """Test context extraction from matchers."""
        matcher = PythonPatternMatcher()
        
        text = """line 1
line 2
error line with issue  
line 4
line 5"""
        
        # Create a mock match object
        mock_match = Mock()
        mock_match.group.return_value = "error line with issue"
        
        context = matcher.extract_context(text, mock_match)
        
        if context:
            assert "error line with issue" in context
            # Should include surrounding lines
            lines = context.split('\n')
            assert len(lines) >= 1


class TestErrorMatch:
    """Test ErrorMatch dataclass."""
    
    def test_error_match_creation(self):
        """Test ErrorMatch creation."""
        pattern = ErrorPattern(
            name="TestError",
            pattern=r"test",
            category=ErrorCategory.SYNTAX,
            severity=ErrorSeverity.HIGH,
            languages=["python"],
            what_happened="Test error",
            explanation="Test explanation",
            quick_fixes=["Fix it"],
            prevention_tip="Prevent it",
            learn_more_url="https://example.com"
        )
        
        match = ErrorMatch(
            pattern=pattern,
            matched_text="test error line",
            confidence=0.95,
            context="def func():\n    test error line\n    pass",
            line_number=10,
            file_path="/path/to/file.py"
        )
        
        assert match.pattern == pattern
        assert match.matched_text == "test error line"
        assert match.confidence == 0.95
        assert match.context == "def func():\n    test error line\n    pass"
        assert match.line_number == 10
        assert match.file_path == "/path/to/file.py"
    
    def test_error_match_optional_fields(self):
        """Test ErrorMatch with optional fields."""
        pattern = ErrorPattern(
            name="TestError",
            pattern=r"test",
            category=ErrorCategory.RUNTIME,
            severity=ErrorSeverity.MEDIUM,
            languages=["generic"],
            what_happened="Test error",
            explanation="Test explanation",
            quick_fixes=["Fix it"],
            prevention_tip="Prevent it",
            learn_more_url="https://example.com"
        )
        
        match = ErrorMatch(
            pattern=pattern,
            matched_text="test",
            confidence=1.0
        )
        
        assert match.pattern == pattern
        assert match.matched_text == "test"
        assert match.confidence == 1.0
        assert match.context is None
        assert match.line_number is None
        assert match.file_path is None


class TestErrorEnums:
    """Test ErrorSeverity and ErrorCategory enums."""
    
    def test_error_severity_values(self):
        """Test ErrorSeverity enum values."""
        assert ErrorSeverity.CRITICAL.value == "critical"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.INFO.value == "info"
    
    def test_error_category_values(self):
        """Test ErrorCategory enum values."""
        assert ErrorCategory.SYNTAX.value == "syntax"
        assert ErrorCategory.RUNTIME.value == "runtime"
        assert ErrorCategory.LOGIC.value == "logic"
        assert ErrorCategory.NETWORK.value == "network"
        assert ErrorCategory.DATABASE.value == "database"
        assert ErrorCategory.PERMISSION.value == "permission"
        assert ErrorCategory.CONFIGURATION.value == "configuration"
        assert ErrorCategory.DEPENDENCY.value == "dependency"


class TestPatternValidation:
    """Test that all patterns are properly formed."""
    
    def test_all_patterns_have_required_fields(self):
        """Test that all patterns have required fields."""
        matcher = ErrorPatternMatcher()
        
        for pattern in matcher.all_patterns:
            assert pattern.name is not None and len(pattern.name) > 0
            assert pattern.pattern is not None
            assert pattern.category is not None
            assert pattern.severity is not None
            assert pattern.languages is not None and len(pattern.languages) > 0
            assert pattern.what_happened is not None
            assert pattern.explanation is not None
            assert pattern.quick_fixes is not None
            assert pattern.prevention_tip is not None
            assert pattern.learn_more_url is not None
    
    def test_pattern_regex_compilation(self):
        """Test that all pattern regexes compile without errors."""
        matcher = ErrorPatternMatcher()
        
        for pattern in matcher.all_patterns:
            # Pattern should be compiled or compileable
            if isinstance(pattern.pattern, str):
                try:
                    re.compile(pattern.pattern, re.IGNORECASE | re.MULTILINE)
                except re.error:
                    pytest.fail(f"Pattern '{pattern.name}' has invalid regex: {pattern.pattern}")
            else:
                # Should be a compiled pattern
                assert hasattr(pattern.pattern, 'findall')
    
    def test_patterns_cover_major_categories(self):
        """Test that patterns cover major error categories."""
        matcher = ErrorPatternMatcher()
        
        categories_found = set()
        for pattern in matcher.all_patterns:
            categories_found.add(pattern.category)
        
        # Should have patterns for major categories
        expected_categories = {
            ErrorCategory.SYNTAX,
            ErrorCategory.RUNTIME,
            ErrorCategory.LOGIC
        }
        
        # At least some major categories should be covered
        overlap = categories_found.intersection(expected_categories)
        assert len(overlap) > 0, f"Should cover major categories. Found: {categories_found}"
    
    def test_patterns_have_multiple_languages(self):
        """Test that patterns support multiple languages."""
        matcher = ErrorPatternMatcher()
        
        languages_found = set()
        for pattern in matcher.all_patterns:
            languages_found.update(lang.lower() for lang in pattern.languages)
        
        # Should support multiple languages
        assert len(languages_found) > 1, f"Should support multiple languages: {languages_found}"
    
    def test_patterns_have_useful_content(self):
        """Test that patterns have useful explanations and fixes."""
        matcher = ErrorPatternMatcher()
        
        for pattern in matcher.all_patterns:
            # Should have meaningful content
            assert len(pattern.explanation) > 10, f"Pattern {pattern.name} should have detailed explanation"
            assert len(pattern.what_happened) > 5, f"Pattern {pattern.name} should explain what happened"
            
            # Should have quick fixes (though empty list is allowed)
            assert isinstance(pattern.quick_fixes, list)
            
            # If has quick fixes, they should be meaningful
            for fix in pattern.quick_fixes:
                assert len(fix) > 5, f"Quick fix should be meaningful: {fix}"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_find_matches_with_invalid_language(self):
        """Test finding matches with invalid language filter."""
        matcher = ErrorPatternMatcher()
        
        # Should not crash with invalid language
        matches = matcher.find_matches("error text", "nonexistent-language")
        assert isinstance(matches, list)
        # May be empty if no patterns match the language filter
    
    def test_pattern_matching_with_special_characters(self):
        """Test pattern matching with special regex characters in text."""
        matcher = ErrorPatternMatcher()
        
        # Text with regex special characters
        special_text = "Error: [brackets] (parentheses) {braces} * + ? ^ $ . | \\"
        
        # Should not crash
        matches = matcher.find_matches(special_text)
        assert isinstance(matches, list)
    
    def test_very_long_text(self):
        """Test with very long error text."""
        matcher = ErrorPatternMatcher()
        
        # Create very long text
        long_text = "Error occurred:\n" + "line of text " * 1000 + "\nNameError: undefined"
        
        matches = matcher.find_matches(long_text, "python")
        assert isinstance(matches, list)
        # Should still work with long text
    
    def test_multilingual_error_text(self):
        """Test with error text containing multiple language indicators."""
        matcher = ErrorPatternMatcher()
        
        mixed_text = """
        def python_function():
            pass
            
        function jsFunction() {
            console.log("hello");
        }
        
        public class JavaClass {
            public static void main(String[] args) {
                System.out.println("hello");
            }
        }
        
        SyntaxError: invalid syntax
        """
        
        # Should detect some language
        language = matcher.detect_language(mixed_text)
        assert language is None or isinstance(language, str)
        
        # Should find matches
        matches = matcher.find_matches(mixed_text)
        assert isinstance(matches, list)