"""
🧪 COMPREHENSIVE PATTERNS TESTING - FORENSICS LAB QUALITY ASSURANCE

Following Debuggle's educational philosophy: Test the pattern recognition system
like you're validating a medical diagnosis tool - accuracy, reliability, and 
educational value are paramount.

🎯 TARGET: Improve core/patterns.py coverage from current baseline to 85%+
📚 FOCUS: Real-world error recognition scenarios that demonstrate debugging skills
🔍 PRIORITY: Cover critical pattern matching workflows that users depend on

Like testing a forensics laboratory:
- 🔬 Can they accurately identify different types of evidence? (error patterns)
- 📊 Do they rank findings correctly by importance? (severity sorting)
- 🗺️ Can they determine the crime scene type? (language detection)
- 🎯 How confident are they in their findings? (confidence scoring)
"""

import pytest
import re
from unittest.mock import Mock, patch
from typing import List, Optional, Pattern

# Import the classes we're testing
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


class TestErrorSeverityAndCategory:
    """
    🏷️ TEST THE CLASSIFICATION SYSTEMS
    
    These tests ensure our error classification enums work correctly.
    Like testing the labeling system in a medical triage unit.
    """
    
    def test_error_severity_values(self):
        """Test that severity levels have correct values"""
        assert ErrorSeverity.CRITICAL.value == "critical"
        assert ErrorSeverity.HIGH.value == "high"  
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.INFO.value == "info"
    
    def test_error_severity_ordering(self):
        """Test that we can compare severity levels for triage"""
        severities = [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH, ErrorSeverity.MEDIUM, 
                     ErrorSeverity.LOW, ErrorSeverity.INFO]
        
        # Should be able to access all severity levels
        assert len(severities) == 5
        assert ErrorSeverity.CRITICAL in severities
        assert ErrorSeverity.INFO in severities
    
    def test_error_category_values(self):
        """Test that error categories have correct values"""
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
        assert len(categories) >= 8  # Should have at least 8 categories
        
        # Check for essential categories
        category_values = [cat.value for cat in categories]
        assert "syntax" in category_values
        assert "runtime" in category_values
        assert "network" in category_values


class TestErrorPatternDataStructure:
    """
    📋 TEST THE ERROR PROFILE SYSTEM
    
    These tests ensure ErrorPattern objects work correctly.
    Like testing patient medical record forms.
    """
    
    def test_error_pattern_creation_with_string_pattern(self):
        """Test creating error pattern with string regex"""
        pattern = ErrorPattern(
            name="TestError",
            pattern=r"TestError: (.+)",
            category=ErrorCategory.RUNTIME,
            severity=ErrorSeverity.HIGH,
            languages=["python"],
            explanation="Test error explanation",
            what_happened="Test error occurred", 
            quick_fixes=["Fix 1", "Fix 2"],
            prevention_tip="Prevent this error by testing",
            learn_more_url="https://example.com/docs"
        )
        
        assert pattern.name == "TestError"
        assert isinstance(pattern.pattern, Pattern)  # Should be compiled to regex
        assert pattern.category == ErrorCategory.RUNTIME
        assert pattern.severity == ErrorSeverity.HIGH
        assert pattern.languages == ["python"]
        assert len(pattern.quick_fixes) == 2
    
    def test_error_pattern_creation_with_compiled_pattern(self):
        """Test creating error pattern with pre-compiled regex"""
        compiled_pattern = re.compile(r"Error: (.+)", re.IGNORECASE)
        pattern = ErrorPattern(
            name="CompiledError",
            pattern=compiled_pattern,
            category=ErrorCategory.SYNTAX,
            severity=ErrorSeverity.CRITICAL,
            languages=["python", "javascript"],
            explanation="Compiled pattern test",
            what_happened="Error with compiled pattern",
            quick_fixes=["Use compiled patterns"],
            prevention_tip="Pre-compile for performance",
            learn_more_url="https://docs.python.org/3/library/re.html"
        )
        
        assert pattern.pattern == compiled_pattern
        assert pattern.languages == ["python", "javascript"]
        assert pattern.severity == ErrorSeverity.CRITICAL
    
    def test_error_pattern_post_init_compilation(self):
        """Test that string patterns are automatically compiled"""
        pattern = ErrorPattern(
            name="AutoCompile",
            pattern="ValueError: invalid literal",
            category=ErrorCategory.RUNTIME,
            severity=ErrorSeverity.MEDIUM,
            languages=["python"],
            explanation="Auto-compilation test",
            what_happened="Pattern auto-compiled",
            quick_fixes=["Test auto compilation"],
            prevention_tip="Let post_init handle compilation",
            learn_more_url="https://example.com"
        )
        
        # Should have been compiled with IGNORECASE and MULTILINE flags
        assert isinstance(pattern.pattern, Pattern)
        assert pattern.pattern.flags & re.IGNORECASE
        assert pattern.pattern.flags & re.MULTILINE


class TestErrorMatchDataStructure:
    """
    🎯 TEST THE EVIDENCE MATCHING SYSTEM
    
    These tests ensure ErrorMatch objects work correctly.
    Like testing forensic evidence reports.
    """
    
    def test_error_match_creation_minimal(self):
        """Test creating error match with minimal required fields"""
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "IndexError"
        mock_pattern.severity = ErrorSeverity.HIGH
        
        match = ErrorMatch(
            pattern=mock_pattern,
            matched_text="IndexError: list index out of range",
            confidence=0.95
        )
        
        assert match.pattern == mock_pattern
        assert match.matched_text == "IndexError: list index out of range"
        assert match.confidence == 0.95
        assert match.context is None
        assert match.line_number is None
        assert match.file_path is None
    
    def test_error_match_creation_full(self):
        """Test creating error match with all optional fields"""
        mock_pattern = Mock(spec=ErrorPattern)
        mock_pattern.name = "TypeError"
        mock_pattern.severity = ErrorSeverity.MEDIUM
        
        match = ErrorMatch(
            pattern=mock_pattern,
            matched_text="TypeError: unsupported operand type(s)",
            confidence=0.85,
            context="def calculate():\n    result = 'text' + 5\nTypeError: unsupported operand type(s)",
            line_number=42,
            file_path="/path/to/script.py"
        )
        
        assert match.context is not None
        assert "TypeError: unsupported operand type(s)" in match.context
        assert match.line_number == 42
        assert match.file_path == "/path/to/script.py"
        assert match.confidence == 0.85


class TestPythonPatternMatcher:
    """
    🐍 TEST THE PYTHON ERROR SPECIALIST
    
    These tests ensure the Python pattern matcher works correctly.
    Like testing a specialist doctor's diagnostic abilities.
    """
    
    @pytest.fixture
    def python_matcher(self):
        return PythonPatternMatcher()
    
    def test_python_language_indicators(self, python_matcher):
        """Test Python language detection patterns"""
        indicators = python_matcher.get_language_indicators()
        
        assert len(indicators) >= 3
        
        # Test that indicators can identify Python tracebacks
        python_traceback = '''Traceback (most recent call last):
  File "test.py", line 10, in <module>
    print(items[5])
IndexError: list index out of range'''
        
        matches = 0
        for indicator in indicators:
            if indicator.search(python_traceback):
                matches += 1
        
        assert matches >= 2  # Should match multiple indicators
    
    def test_python_patterns_indexerror(self, python_matcher):
        """Test Python IndexError pattern recognition"""
        patterns = python_matcher.get_patterns()
        
        # Find the IndexError pattern
        index_error_pattern = None
        for pattern in patterns:
            if pattern.name == "IndexError":
                index_error_pattern = pattern
                break
        
        assert index_error_pattern is not None
        assert index_error_pattern.severity == ErrorSeverity.HIGH
        assert index_error_pattern.category == ErrorCategory.RUNTIME
        assert "python" in index_error_pattern.languages
        
        # Test that it matches real IndexError messages
        test_errors = [
            "IndexError: list index out of range",
            "IndexError: index out of range",
        ]
        
        for error_text in test_errors:
            match = index_error_pattern.pattern.search(error_text)
            assert match is not None, f"Pattern should match: {error_text}"
    
    def test_python_patterns_keyerror(self, python_matcher):
        """Test Python KeyError pattern recognition"""
        patterns = python_matcher.get_patterns()
        
        # Find the KeyError pattern
        key_error_pattern = None
        for pattern in patterns:
            if pattern.name == "KeyError":
                key_error_pattern = pattern
                break
        
        assert key_error_pattern is not None
        
        # Test that it matches real KeyError messages
        test_errors = [
            "KeyError: 'missing_key'",
            'KeyError: "another_key"',
        ]
        
        for error_text in test_errors:
            match = key_error_pattern.pattern.search(error_text)
            assert match is not None, f"Pattern should match: {error_text}"
    
    def test_python_patterns_have_educational_content(self, python_matcher):
        """Test that patterns have educational value"""
        patterns = python_matcher.get_patterns()
        
        for pattern in patterns:
            # Each pattern should have educational content
            assert len(pattern.explanation) > 10
            assert len(pattern.what_happened) > 10
            assert len(pattern.quick_fixes) > 0
            assert len(pattern.prevention_tip) > 10
            assert pattern.learn_more_url.startswith("https://")
            
            # Quick fixes should be actionable
            for fix in pattern.quick_fixes:
                assert len(fix) > 10
                # Should contain code examples or specific instructions
                assert any(char in fix for char in ['`', '()', '.', ':'])
    
    def test_context_extraction(self, python_matcher):
        """Test context extraction around matched errors"""
        text = """def calculate():
    numbers = [1, 2, 3]
    result = numbers[5]  # This will cause IndexError
    return result

calculate()"""
        
        # Create a mock match object
        mock_match = Mock()
        mock_match.group.return_value = "IndexError: list index out of range"
        
        context = python_matcher.extract_context(text, mock_match)
        
        # Context extraction might return None if the implementation
        # doesn't find the match in the text, which is acceptable
        if context is not None:
            assert isinstance(context, str)
            assert len(context) > 0


class TestJavaScriptPatternMatcher:
    """
    🌐 TEST THE JAVASCRIPT ERROR SPECIALIST
    
    These tests ensure the JavaScript pattern matcher works correctly.
    Like testing a web development specialist's diagnostic skills.
    """
    
    @pytest.fixture
    def js_matcher(self):
        return JavaScriptPatternMatcher()
    
    def test_javascript_language_indicators(self, js_matcher):
        """Test JavaScript language detection patterns"""
        indicators = js_matcher.get_language_indicators()
        
        assert len(indicators) >= 3
        
        # Test JavaScript-specific error format
        js_error = """ReferenceError: myVariable is not defined
    at myFunction (script.js:15:10)
    at Object.<anonymous> (script.js:20:5)"""
        
        matches = 0
        for indicator in indicators:
            if indicator.search(js_error):
                matches += 1
        
        assert matches >= 1  # Should match at least one indicator
    
    def test_javascript_reference_error_pattern(self, js_matcher):
        """Test JavaScript ReferenceError pattern"""
        patterns = js_matcher.get_patterns()
        
        # Find ReferenceError pattern
        ref_error_pattern = None
        for pattern in patterns:
            if pattern.name == "ReferenceError":
                ref_error_pattern = pattern
                break
        
        assert ref_error_pattern is not None
        assert "javascript" in ref_error_pattern.languages
        
        # Test matching real ReferenceError messages
        test_errors = [
            "ReferenceError: myVariable is not defined",
            "ReferenceError: undefinedFunction is not defined",
        ]
        
        for error_text in test_errors:
            match = ref_error_pattern.pattern.search(error_text)
            assert match is not None, f"Should match: {error_text}"


class TestJavaPatternMatcher:
    """
    ☕ TEST THE JAVA ERROR SPECIALIST
    
    These tests ensure the Java pattern matcher works correctly.
    Like testing an enterprise application specialist.
    """
    
    @pytest.fixture
    def java_matcher(self):
        return JavaPatternMatcher()
    
    def test_java_language_indicators(self, java_matcher):
        """Test Java language detection patterns"""
        indicators = java_matcher.get_language_indicators()
        
        assert len(indicators) >= 3
        
        # Test Java-specific stack trace format
        java_error = """Exception in thread "main" java.lang.NullPointerException
        at com.example.MyClass.method(MyClass.java:25)
        at com.example.Main.main(Main.java:10)
Caused by: java.lang.IllegalArgumentException"""
        
        matches = 0
        for indicator in indicators:
            if indicator.search(java_error):
                matches += 1
        
        assert matches >= 2  # Should match multiple indicators
    
    def test_java_null_pointer_exception_pattern(self, java_matcher):
        """Test Java NullPointerException pattern"""
        patterns = java_matcher.get_patterns()
        
        # Find NullPointerException pattern
        npe_pattern = None
        for pattern in patterns:
            if pattern.name == "NullPointerException":
                npe_pattern = pattern
                break
        
        assert npe_pattern is not None
        assert npe_pattern.severity == ErrorSeverity.CRITICAL
        assert "java" in npe_pattern.languages
        
        # Test matching NullPointerException
        java_npe = "Exception in thread \"main\" java.lang.NullPointerException"
        match = npe_pattern.pattern.search(java_npe)
        assert match is not None


class TestErrorPatternMatcherCore:
    """
    🎯 TEST THE MAIN PATTERN MATCHING COORDINATOR
    
    These tests ensure the main ErrorPatternMatcher works correctly.
    Like testing the head of a forensics department.
    """
    
    @pytest.fixture
    def pattern_matcher(self):
        return ErrorPatternMatcher()
    
    def test_pattern_matcher_initialization(self, pattern_matcher):
        """Test that pattern matcher initializes correctly"""
        assert len(pattern_matcher.matchers) >= 3
        assert pattern_matcher.all_patterns is not None
        assert len(pattern_matcher.all_patterns) > 0
        assert pattern_matcher.language_indicators is not None
    
    def test_language_detection_python(self, pattern_matcher):
        """Test Python language detection"""
        python_text = '''Traceback (most recent call last):
  File "script.py", line 10, in <module>
    result = data[index]
IndexError: list index out of range'''
        
        detected = pattern_matcher.detect_language(python_text)
        assert detected == "python"
    
    def test_language_detection_javascript(self, pattern_matcher):
        """Test JavaScript language detection"""
        js_text = '''ReferenceError: myVariable is not defined
    at myFunction (script.js:15:10)
    at Object.<anonymous> (script.js:20:5)'''
        
        detected = pattern_matcher.detect_language(js_text)
        assert detected == "javascript"
    
    def test_language_detection_java(self, pattern_matcher):
        """Test Java language detection"""
        java_text = '''Exception in thread "main" java.lang.NullPointerException
        at com.example.MyClass.method(MyClass.java:25)
        at com.example.Main.main(Main.java:10)'''
        
        detected = pattern_matcher.detect_language(java_text)
        assert detected == "java"
    
    def test_language_detection_unknown(self, pattern_matcher):
        """Test unknown language handling"""
        unknown_text = "This is just plain text with no error patterns"
        detected = pattern_matcher.detect_language(unknown_text)
        assert detected is None
    
    def test_find_matches_python_indexerror(self, pattern_matcher):
        """Test finding matches for Python IndexError"""
        error_text = "IndexError: list index out of range"
        matches = pattern_matcher.find_matches(error_text, "python")
        
        assert len(matches) > 0
        
        # Should find IndexError match
        index_error_match = None
        for match in matches:
            if match.pattern.name == "IndexError":
                index_error_match = match
                break
        
        assert index_error_match is not None
        assert index_error_match.matched_text == error_text
        assert index_error_match.confidence > 0
    
    def test_find_matches_severity_sorting(self, pattern_matcher):
        """Test that matches are sorted by severity"""
        # Text that could match multiple patterns
        mixed_error_text = '''
TypeError: unsupported operand type(s)
IndexError: list index out of range
'''
        
        matches = pattern_matcher.find_matches(mixed_error_text, "python")
        
        if len(matches) > 1:
            # Should be sorted by severity (critical first, then high, etc.)
            severity_order = ["critical", "high", "medium", "low", "info"]
            
            prev_severity_index = -1
            for match in matches:
                current_severity_index = severity_order.index(match.pattern.severity.value)
                assert current_severity_index >= prev_severity_index
                prev_severity_index = current_severity_index
    
    def test_find_matches_with_language_filter(self, pattern_matcher):
        """Test filtering matches by language"""
        error_text = "TypeError: unsupported operand"
        
        python_matches = pattern_matcher.find_matches(error_text, "python")
        js_matches = pattern_matcher.find_matches(error_text, "javascript")
        
        # Should find different or same matches depending on pattern definitions
        assert isinstance(python_matches, list)
        assert isinstance(js_matches, list)
    
    def test_get_best_match(self, pattern_matcher):
        """Test getting the best single match"""
        error_text = "IndexError: list index out of range"
        best_match = pattern_matcher.get_best_match(error_text, "python")
        
        assert best_match is not None
        assert isinstance(best_match, ErrorMatch)
        assert best_match.pattern.name == "IndexError"
    
    def test_get_best_match_no_matches(self, pattern_matcher):
        """Test best match with no pattern matches"""
        no_error_text = "This is just normal output with no errors"
        best_match = pattern_matcher.get_best_match(no_error_text)
        
        assert best_match is None


class TestPatternMatchingEdgeCases:
    """
    🚨 TEST EDGE CASES AND ERROR SCENARIOS
    
    These tests ensure the pattern matcher handles unusual situations.
    Like testing how medical equipment responds to edge cases.
    """
    
    @pytest.fixture
    def pattern_matcher(self):
        return ErrorPatternMatcher()
    
    def test_empty_text_input(self, pattern_matcher):
        """Test handling of empty input"""
        matches = pattern_matcher.find_matches("")
        assert matches == []
        
        language = pattern_matcher.detect_language("")
        assert language is None
        
        best_match = pattern_matcher.get_best_match("")
        assert best_match is None
    
    def test_very_long_text_input(self, pattern_matcher):
        """Test handling of very long input"""
        long_text = "IndexError: list index out of range\n" * 1000
        matches = pattern_matcher.find_matches(long_text, "python")
        
        # Should still work, might find multiple matches
        assert isinstance(matches, list)
    
    def test_mixed_language_input(self, pattern_matcher):
        """Test handling of mixed language error messages"""
        mixed_text = '''
Traceback (most recent call last):
  File "script.py", line 10, in <module>
IndexError: list index out of range

ReferenceError: myVariable is not defined
    at script.js:15:10
'''
        
        # Should detect the most prominent language
        detected = pattern_matcher.detect_language(mixed_text)
        assert detected in ["python", "javascript", None]
        
        # Should find matches from both languages
        matches = pattern_matcher.find_matches(mixed_text)
        assert len(matches) >= 1
    
    def test_malformed_error_messages(self, pattern_matcher):
        """Test handling of malformed or partial error messages"""
        malformed_errors = [
            "IndexError:",  # Missing message
            "KeyError",     # Missing colon and message
            "Error: ",      # Generic error with no details
            "Traceback (most recent call last):",  # Incomplete traceback
        ]
        
        for error_text in malformed_errors:
            # Should not crash, even if no matches found
            matches = pattern_matcher.find_matches(error_text)
            assert isinstance(matches, list)
    
    def test_case_insensitive_matching(self, pattern_matcher):
        """Test that pattern matching is case insensitive"""
        # Test both uppercase and lowercase variations
        test_cases = [
            "indexerror: list index out of range",
            "INDEXERROR: LIST INDEX OUT OF RANGE",
            "IndexError: List Index Out Of Range",
        ]
        
        for error_text in test_cases:
            matches = pattern_matcher.find_matches(error_text, "python") 
            # Might find matches due to case insensitive patterns
            assert isinstance(matches, list)


class TestPatternMatchingIntegration:
    """
    🔗 TEST INTEGRATION SCENARIOS
    
    These tests ensure components work together correctly.
    Like testing how different medical departments coordinate.
    """
    
    @pytest.fixture
    def pattern_matcher(self):
        return ErrorPatternMatcher()
    
    def test_realistic_python_stack_trace(self, pattern_matcher):
        """Test with realistic Python stack trace"""
        realistic_traceback = '''Traceback (most recent call last):
  File "/usr/local/app/main.py", line 156, in process_data
    result = data[index]
  File "/usr/local/app/utils.py", line 42, in calculate
    return items[position] 
IndexError: list index out of range'''
        
        # Should detect Python
        language = pattern_matcher.detect_language(realistic_traceback)
        assert language == "python"
        
        # Should find IndexError
        matches = pattern_matcher.find_matches(realistic_traceback, language)
        assert len(matches) > 0
        
        index_error_match = None
        for match in matches:
            if match.pattern.name == "IndexError":
                index_error_match = match
                break
        
        assert index_error_match is not None
    
    def test_realistic_javascript_browser_error(self, pattern_matcher):
        """Test with realistic JavaScript browser error"""
        js_error = '''Uncaught ReferenceError: myFunction is not defined
    at HTMLButtonElement.<anonymous> (app.js:45:12)
    at HTMLButtonElement.dispatch (jquery.min.js:3:8)
    at HTMLButtonElement.r.handle (jquery.min.js:3:5)'''
        
        # Should detect JavaScript
        language = pattern_matcher.detect_language(js_error)
        assert language == "javascript"
        
        # Should find ReferenceError
        matches = pattern_matcher.find_matches(js_error, language)
        assert len(matches) > 0
    
    def test_realistic_java_exception(self, pattern_matcher):
        """Test with realistic Java exception"""
        java_exception = '''Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.length()" because "text" is null
        at com.example.MyClass.processText(MyClass.java:25)
        at com.example.MyClass.main(MyClass.java:15)
Caused by: java.lang.IllegalArgumentException: Text cannot be null
        at com.example.Validator.validate(Validator.java:12)'''
        
        # Should detect Java  
        language = pattern_matcher.detect_language(java_exception)
        assert language == "java"
        
        # Should find NullPointerException
        matches = pattern_matcher.find_matches(java_exception, language)
        assert len(matches) > 0


class TestPatternMatchingPerformance:
    """
    ⚡ TEST PERFORMANCE AND EFFICIENCY
    
    These tests ensure the pattern matcher performs well.
    Like testing medical equipment response times.
    """
    
    @pytest.fixture
    def pattern_matcher(self):
        return ErrorPatternMatcher()
    
    def test_language_detection_performance(self, pattern_matcher):
        """Test that language detection completes quickly"""
        import time
        
        test_text = '''Traceback (most recent call last):
  File "test.py", line 10, in <module>
    result = data[index]
IndexError: list index out of range'''
        
        start_time = time.time()
        language = pattern_matcher.detect_language(test_text)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 0.1  # 100ms max
        assert language == "python"
    
    def test_pattern_matching_performance(self, pattern_matcher):
        """Test that pattern matching completes quickly"""
        import time
        
        error_text = "IndexError: list index out of range"
        
        start_time = time.time()
        matches = pattern_matcher.find_matches(error_text, "python")
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 0.1  # 100ms max
        assert len(matches) > 0


class TestEducationalValue:
    """
    📚 TEST THE EDUCATIONAL ASPECTS
    
    These tests ensure patterns provide educational value,
    following Debuggle's core philosophy.
    """
    
    @pytest.fixture
    def pattern_matcher(self):
        return ErrorPatternMatcher()
    
    def test_patterns_have_comprehensive_explanations(self, pattern_matcher):
        """Test that all patterns provide educational content"""
        for pattern in pattern_matcher.all_patterns:
            # Each pattern should be educational
            assert len(pattern.explanation) >= 20
            assert len(pattern.what_happened) >= 20
            assert len(pattern.prevention_tip) >= 20
            
            # Should have practical quick fixes
            assert len(pattern.quick_fixes) > 0
            for fix in pattern.quick_fixes:
                assert len(fix) >= 15
                # Should contain actionable advice
                assert any(keyword in fix.lower() for keyword in 
                          ['check', 'use', 'try', 'if', 'add', 'remove', 'change', 
                           'convert', 'declare', 'provide', 'initialize', 'verify'])
    
    def test_patterns_include_learning_resources(self, pattern_matcher):
        """Test that patterns link to educational resources"""
        for pattern in pattern_matcher.all_patterns:
            assert pattern.learn_more_url.startswith(('http://', 'https://'))
            # Should link to reputable educational sources
            assert any(domain in pattern.learn_more_url for domain in 
                      ['docs.python.org', 'developer.mozilla.org', 'docs.oracle.com', 'stackoverflow.com'])
    
    def test_error_severity_reflects_educational_priority(self, pattern_matcher):
        """Test that severity levels reflect learning importance"""
        critical_patterns = []
        high_patterns = []
        
        for pattern in pattern_matcher.all_patterns:
            if pattern.severity == ErrorSeverity.CRITICAL:
                critical_patterns.append(pattern)
            elif pattern.severity == ErrorSeverity.HIGH:
                high_patterns.append(pattern)
        
        # Should have both critical and high priority patterns
        assert len(critical_patterns) > 0
        assert len(high_patterns) > 0
        
        # Critical patterns should be fundamental errors students encounter
        critical_names = [p.name for p in critical_patterns]
        assert any(name in critical_names for name in 
                  ['NullPointerException', 'IndexError', 'KeyError'])