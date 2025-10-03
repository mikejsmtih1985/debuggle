"""
Comprehensive tests for error_fixes.py module.
Tests error pattern matching, context extraction, and error summary generation.
"""

import pytest
from src.debuggle.error_fixes import (
    ERROR_FIX_PATTERNS,
    extract_error_context,
    generate_enhanced_error_summary
)


class TestErrorFixPatterns:
    """Test the ERROR_FIX_PATTERNS dictionary structure."""
    
    def test_error_patterns_exist(self):
        """Test that ERROR_FIX_PATTERNS is properly defined."""
        assert isinstance(ERROR_FIX_PATTERNS, dict)
        assert len(ERROR_FIX_PATTERNS) > 0
    
    def test_python_error_patterns(self):
        """Test Python error patterns are included."""
        python_errors = [
            'IndexError', 'KeyError', 'AttributeError', 
            'TypeError', 'ValueError', 'FileNotFoundError', 
            'ZeroDivisionError'
        ]
        
        for error_type in python_errors:
            assert error_type in ERROR_FIX_PATTERNS
            pattern = ERROR_FIX_PATTERNS[error_type]
            
            # Check required fields
            assert 'explanation' in pattern
            assert 'what_happened' in pattern
            assert 'quick_fixes' in pattern
            assert 'prevention' in pattern
            assert 'learn_more' in pattern
            
            # Check field types
            assert isinstance(pattern['explanation'], str)
            assert isinstance(pattern['what_happened'], str)
            assert isinstance(pattern['quick_fixes'], list)
            assert isinstance(pattern['prevention'], str)
            assert isinstance(pattern['learn_more'], str)
            
            # Check quick_fixes is non-empty
            assert len(pattern['quick_fixes']) > 0
    
    def test_javascript_error_patterns(self):
        """Test JavaScript error patterns are included."""
        js_errors = ['ReferenceError', 'TypeError (JavaScript)']
        
        for error_type in js_errors:
            if error_type in ERROR_FIX_PATTERNS:
                pattern = ERROR_FIX_PATTERNS[error_type]
                assert 'explanation' in pattern
                assert 'quick_fixes' in pattern
    
    def test_pattern_completeness(self):
        """Test that all patterns have complete information."""
        for error_type, pattern in ERROR_FIX_PATTERNS.items():
            # All patterns should have these fields
            required_fields = ['explanation', 'what_happened', 'quick_fixes', 'prevention']
            
            for field in required_fields:
                assert field in pattern, f"{error_type} missing field: {field}"
                assert pattern[field], f"{error_type} has empty field: {field}"
            
            # Quick fixes should be a non-empty list
            assert isinstance(pattern['quick_fixes'], list)
            assert len(pattern['quick_fixes']) > 0
            
            # Each quick fix should be a non-empty string
            for fix in pattern['quick_fixes']:
                assert isinstance(fix, str)
                assert len(fix.strip()) > 0


class TestExtractErrorContext:
    """Test the extract_error_context function."""
    
    def test_index_error_context(self):
        """Test extracting context for IndexError."""
        error_text = "IndexError: list index out of range"
        context = extract_error_context(error_text, "IndexError")
        
        assert isinstance(context, str)
        assert len(context) > 0
        assert "index" in context.lower() or "doesn't exist" in context.lower()
    
    def test_key_error_context(self):
        """Test extracting context for KeyError."""
        error_text = "KeyError: 'missing_key'"
        context = extract_error_context(error_text, "KeyError")
        
        assert isinstance(context, str)
        assert "missing_key" in context or "not found" in context.lower()
    
    def test_attribute_error_context(self):
        """Test extracting context for AttributeError."""
        error_text = "AttributeError: 'str' object has no attribute 'append'"
        context = extract_error_context(error_text, "AttributeError")
        
        assert isinstance(context, str)
        assert "append" in context or "doesn't exist" in context.lower()
    
    def test_type_error_context(self):
        """Test extracting context for TypeError."""
        error_text = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
        context = extract_error_context(error_text, "TypeError")
        
        assert isinstance(context, str)
        assert "incompatible types" in context.lower() or "unsupported operand" in context.lower()
    
    def test_unknown_error_context(self):
        """Test extracting context for unknown error types."""
        error_text = "CustomError: something went wrong"
        context = extract_error_context(error_text, "CustomError")
        
        assert isinstance(context, str)
        # Should return the error line or a fallback message
        assert len(context) > 0
    
    def test_multiline_error_context(self):
        """Test extracting context from multiline error messages."""
        error_text = """Traceback (most recent call last):
  File "test.py", line 5, in <module>
    print(my_list[10])
IndexError: list index out of range"""
        
        context = extract_error_context(error_text, "IndexError")
        assert isinstance(context, str)
        assert len(context) > 0
    
    def test_empty_input_context(self):
        """Test extracting context with empty inputs."""
        context = extract_error_context("", "IndexError")
        assert isinstance(context, str)
        
        context = extract_error_context("IndexError: test", "")
        assert isinstance(context, str)


class TestGenerateEnhancedErrorSummary:
    """Test the generate_enhanced_error_summary function."""
    
    def test_index_error_summary(self):
        """Test generating summary for IndexError."""
        error_text = "IndexError: list index out of range"
        summary = generate_enhanced_error_summary(error_text)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should contain helpful information about IndexError
        assert "index" in summary.lower() or "array" in summary.lower() or "list" in summary.lower()
    
    def test_key_error_summary(self):
        """Test generating summary for KeyError."""
        error_text = "KeyError: 'username'"
        summary = generate_enhanced_error_summary(error_text)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should contain helpful information about KeyError
        assert "key" in summary.lower() or "dictionary" in summary.lower()
    
    def test_attribute_error_summary(self):
        """Test generating summary for AttributeError."""
        error_text = "AttributeError: 'str' object has no attribute 'append'" 
        summary = generate_enhanced_error_summary(error_text)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should contain helpful information about AttributeError
        assert "attribute" in summary.lower() or "method" in summary.lower()
    
    def test_type_error_summary(self):
        """Test generating summary for TypeError."""
        error_text = "TypeError: can't multiply sequence by non-int of type 'float'"
        summary = generate_enhanced_error_summary(error_text)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should contain helpful information about TypeError
        assert "type" in summary.lower() or "operation" in summary.lower()
    
    def test_unknown_error_summary(self):
        """Test generating summary for unknown error types."""
        error_text = "CustomError: unknown issue occurred"
        summary = generate_enhanced_error_summary(error_text)
        
        assert isinstance(summary, str)
        # Should still return something, even if generic
        assert len(summary) > 0
    
    def test_multiple_errors_summary(self):
        """Test generating summary when multiple error types are present."""
        error_text = """Multiple errors occurred:
IndexError: list index out of range
KeyError: 'missing_key'"""
        
        summary = generate_enhanced_error_summary(error_text)
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_empty_text_summary(self):
        """Test generating summary with empty or invalid input."""
        summary = generate_enhanced_error_summary("")
        assert isinstance(summary, str)
        
        summary = generate_enhanced_error_summary("No errors here, just text")
        assert isinstance(summary, str)


class TestErrorFixIntegration:
    """Test integration between different error fix components."""
    
    def test_pattern_coverage(self):
        """Test that we have good coverage of common error patterns."""
        # Common errors that should be covered
        common_errors = [
            'IndexError', 'KeyError', 'AttributeError', 'TypeError', 
            'ValueError', 'FileNotFoundError', 'ZeroDivisionError'
        ]
        
        coverage_count = 0
        for error_type in common_errors:
            if error_type in ERROR_FIX_PATTERNS:
                coverage_count += 1
        
        # Should cover at least 80% of common errors
        coverage_ratio = coverage_count / len(common_errors)
        assert coverage_ratio >= 0.8
    
    def test_fix_suggestion_quality(self):
        """Test that fix suggestions are high quality and actionable."""
        for error_type, pattern in ERROR_FIX_PATTERNS.items():
            # Each quick fix should be specific and actionable
            for fix in pattern['quick_fixes']:
                # Should contain actual code or specific instructions
                assert len(fix) > 20  # Reasonably detailed
                # Should contain actionable keywords
                actionable_keywords = ['check', 'use', 'try', 'verify', 'ensure', 'set', 'call', 'add']
                has_actionable_word = any(keyword in fix.lower() for keyword in actionable_keywords)
                assert has_actionable_word, f"Fix suggestion not actionable enough: {fix}"
    
    def test_context_and_summary_integration(self):
        """Test that context extraction and summary generation work well together."""
        test_errors = [
            "IndexError: list index out of range",
            "KeyError: 'missing_key'",
            "AttributeError: 'str' object has no attribute 'append'",
            "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
        ]
        
        for error_text in test_errors:
            # Extract the error type from the text
            error_type = error_text.split(':')[0] if ':' in error_text else "Unknown"
            
            # Test context extraction
            context = extract_error_context(error_text, error_type)
            assert isinstance(context, str)
            assert len(context) > 0
            
            # Test summary generation
            summary = generate_enhanced_error_summary(error_text)
            assert isinstance(summary, str)
            assert len(summary) > 0


class TestErrorFixEdgeCases:
    """Test edge cases and error handling."""
    
    def test_extract_context_edge_cases(self):
        """Test extract_error_context with edge cases."""
        edge_cases = [
            ("", "IndexError"),
            ("IndexError: test", ""),
            ("   ", "KeyError"),
            (None, "TypeError"),
            ("Normal text without errors", "ValueError")
        ]
        
        for text, error_type in edge_cases:
            try:
                if text is None:
                    # Skip None input as it would cause TypeError
                    continue
                result = extract_error_context(text, error_type)
                assert isinstance(result, str)
            except Exception as e:
                pytest.fail(f"extract_error_context crashed on input ({text}, {error_type}): {e}")
    
    def test_generate_summary_edge_cases(self):
        """Test generate_enhanced_error_summary with edge cases."""
        edge_cases = [
            "",
            "   ",
            "\n\n\n",
            "No errors here",
            "Error without proper format",
            "Very long text " * 1000
        ]
        
        for case in edge_cases:
            try:
                result = generate_enhanced_error_summary(case)
                assert isinstance(result, str)
            except Exception as e:
                pytest.fail(f"generate_enhanced_error_summary crashed on input {case}: {e}")
    
    def test_pattern_data_integrity(self):
        """Test that all error patterns have valid data."""
        for error_type, pattern in ERROR_FIX_PATTERNS.items():
            # Verify error_type is a string
            assert isinstance(error_type, str)
            assert len(error_type) > 0
            
            # Verify pattern is a dictionary
            assert isinstance(pattern, dict)
            
            # Check that URLs in learn_more are valid format (if present)
            if 'learn_more' in pattern and pattern['learn_more']:
                learn_more = pattern['learn_more']
                # Should be a string and look like a URL
                assert isinstance(learn_more, str)
                assert learn_more.startswith(('http://', 'https://')) or learn_more.startswith('Check ')
            
            # Verify quick_fixes are all strings
            if 'quick_fixes' in pattern:
                for fix in pattern['quick_fixes']:
                    assert isinstance(fix, str)
                    assert len(fix.strip()) > 0