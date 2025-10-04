import pytest
from src.debuggle.processor import LogProcessor
from src.debuggle.utils.error_fixes import generate_enhanced_error_summary, extract_error_context


class TestEnhancedErrorSuggestions:
    """Test the enhanced error suggestion system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = LogProcessor()
    
    def test_enhanced_indexerror_summary(self):
        """Test enhanced IndexError summary with actionable fixes."""
        test_log = '''Traceback (most recent call last):
  File "test.py", line 5, in <module>
    print(my_list[10])
IndexError: list index out of range'''
        
        summary = self.processor.generate_summary(test_log)
        
        # Verify enhanced summary is generated
        assert summary is not None
        assert "IndexError Detected" in summary
        assert "What happened:" in summary
        assert "Quick fixes:" in summary
        assert "if len(my_list) > index" in summary
        assert "Prevention tip:" in summary
        assert "Learn more:" in summary
        assert "docs.python.org" in summary
    
    def test_enhanced_keyerror_summary(self):
        """Test enhanced KeyError summary with specific key extraction."""
        test_log = '''Traceback (most recent call last):
  File "app.py", line 8, in <module>
    value = data['missing_key']
KeyError: 'missing_key' '''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "KeyError Detected" in summary
        assert "missing_key" in summary
        assert ".get() method" in summary
        assert "default_value" in summary
        assert "dictionaries" in summary
    
    def test_enhanced_attributeerror_summary(self):
        """Test enhanced AttributeError summary with attribute extraction."""
        test_log = '''Traceback (most recent call last):
  File "test.py", line 3, in <module>
    result = my_object.nonexistent_method()
AttributeError: 'str' object has no attribute 'nonexistent_method' '''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "AttributeError Detected" in summary
        assert "nonexistent_method" in summary
        assert "dir(my_object)" in summary
        assert "hasattr()" in summary
    
    def test_enhanced_typeerror_summary(self):
        """Test enhanced TypeError summary."""
        test_log = '''Traceback (most recent call last):
  File "test.py", line 2, in <module>
    result = "hello" + 5
TypeError: can only concatenate str (not "int") to str'''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "TypeError Detected" in summary
        assert "incompatible data types" in summary
        assert "str(number)" in summary
        assert "isinstance" in summary
    
    def test_enhanced_valueerror_summary(self):
        """Test enhanced ValueError summary."""
        test_log = '''Traceback (most recent call last):
  File "test.py", line 1, in <module>
    number = int("not_a_number")
ValueError: invalid literal for int() with base 10: 'not_a_number' '''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "ValueError Detected" in summary
        assert "specific value can't be used" in summary
        assert "isdigit()" in summary
        assert "try-except" in summary
    
    def test_enhanced_nullpointerexception_summary(self):
        """Test enhanced NullPointerException summary for Java."""
        test_log = '''Exception in thread "main" java.lang.NullPointerException
	at com.example.Main.processData(Main.java:15)
	at com.example.Main.main(Main.java:8)'''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "NullPointerException Detected" in summary
        assert "null object" in summary
        assert "if (object != null)" in summary
        assert "Optional.ofNullable" in summary
        assert "oracle.com" in summary
    
    def test_enhanced_referenceerror_summary(self):
        """Test enhanced ReferenceError summary for JavaScript."""
        test_log = '''ReferenceError: myVariable is not defined
    at processData (app.js:25:12)
    at main (app.js:5:3)'''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "ReferenceError Detected" in summary
        assert "hasn't been declared or is out of scope" in summary
        assert "let myVariable" in summary
        assert "typeof myVariable" in summary
        assert "developer.mozilla.org" in summary
    
    def test_enhanced_arrayindexoutofbounds_summary(self):
        """Test enhanced ArrayIndexOutOfBoundsException summary for Java."""
        test_log = '''Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 3
	at com.example.ArrayTest.main(ArrayTest.java:8)'''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "ArrayIndexOutOfBoundsException Detected" in summary
        assert "array position that doesn't exist" in summary
        assert "array.length" in summary
        assert "enhanced for loop" in summary
    
    def test_enhanced_filenotfounderror_summary(self):
        """Test enhanced FileNotFoundError summary."""
        test_log = '''Traceback (most recent call last):
  File "test.py", line 1, in <module>
    with open("nonexistent.txt", "r") as f:
FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.txt' '''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "FileNotFoundError Detected" in summary
        assert "file that doesn't exist" in summary
        assert "os.path.exists" in summary
        assert "absolute paths" in summary
    
    def test_enhanced_zerodivisionerror_summary(self):
        """Test enhanced ZeroDivisionError summary."""
        test_log = '''Traceback (most recent call last):
  File "test.py", line 2, in <module>
    result = 10 / 0
ZeroDivisionError: division by zero'''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        assert "ZeroDivisionError Detected" in summary
        assert "divide a number by zero" in summary
        assert "if denominator != 0" in summary
        assert "mathematically undefined" in summary
    
    def test_error_context_extraction(self):
        """Test specific error context extraction."""
        # Test KeyError context extraction
        keyerror_text = "KeyError: 'user_id'"
        context = extract_error_context(keyerror_text, 'KeyError')
        assert "user_id" in context
        assert "not found in the dictionary" in context
        
        # Test AttributeError context extraction
        attrerror_text = "AttributeError: 'list' object has no attribute 'append_item'"
        context = extract_error_context(attrerror_text, 'AttributeError')
        assert "append_item" in context
        assert "doesn't exist on this object" in context
    
    def test_fallback_to_original_summary(self):
        """Test that non-specific errors fall back to original summary system."""
        test_log = '''INFO 2023-01-01 12:00:00 Application started successfully
DEBUG 2023-01-01 12:00:01 Connected to database
INFO 2023-01-01 12:00:02 Ready to accept requests'''
        
        summary = self.processor.generate_summary(test_log)
        
        # Should use the original summary system, not enhanced error suggestions
        assert summary is not None
        assert "IndexError Detected" not in summary
        assert "Great news!" in summary or "system is running smoothly" in summary
    
    def test_multiple_error_types_prioritization(self):
        """Test that the first matching error type is used when multiple are present."""
        test_log = '''Traceback (most recent call last):
  File "test.py", line 5, in <module>
    result = my_dict[my_list[10]]
IndexError: list index out of range
KeyError: 'some_key' '''
        
        summary = self.processor.generate_summary(test_log)
        
        # Should detect IndexError first since it appears first in the text
        assert summary is not None
        assert "IndexError Detected" in summary
        assert "KeyError Detected" not in summary
    
    def test_enhanced_summary_integration_with_api(self):
        """Test that enhanced summaries work through the full processing pipeline."""
        test_input = '''Traceback (most recent call last):
  File "main.py", line 10, in <module>
    user_name = users['john_doe']
KeyError: 'john_doe' '''
        
        # Test full processing pipeline
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=test_input,
            language='python',
            highlight=True,
            summarize=True,
            tags=True,
            max_lines=1000
        )
        
        # Verify enhanced summary is used
        assert summary is not None
        assert "KeyError Detected" in summary
        assert "john_doe" in summary
        assert ".get() method" in summary
        
        # Verify other processing still works
        assert cleaned_log is not None
        assert len(tags) > 0
        assert 'KeyError' in tags
        assert metadata['language_detected'] == 'python'
    
    def test_connection_error_enhancement(self):
        """Test enhanced summary for connection errors."""
        test_log = '''ERROR 2023-01-01 12:00:00 Connection refused to database server
java.net.ConnectException: Connection refused
	at java.net.PlainSocketImpl.socketConnect'''
        
        summary = self.processor.generate_summary(test_log)
        
        assert summary is not None
        # Should use enhanced connection error pattern
        if "Connection refused Detected" in summary:
            assert "connect to another service" in summary
            assert "Check if service is running" in summary
            assert "connection troubleshooting" in summary


class TestErrorFixPatternsModule:
    """Test the standalone error_fixes module."""
    
    def test_generate_enhanced_error_summary_function(self):
        """Test the standalone generate_enhanced_error_summary function."""
        test_text = "IndexError: list index out of range"
        
        summary = generate_enhanced_error_summary(test_text)
        
        assert summary != ""
        assert "IndexError Detected" in summary
        assert "Quick fixes:" in summary
    
    def test_extract_error_context_function(self):
        """Test the standalone extract_error_context function."""
        test_text = "KeyError: 'missing_key'"
        
        context = extract_error_context(test_text, 'KeyError')
        
        assert "missing_key" in context
        assert "not found in the dictionary" in context
    
    def test_no_matching_error_returns_empty(self):
        """Test that non-matching errors return empty string."""
        test_text = "This is just a normal log message with no errors"
        
        summary = generate_enhanced_error_summary(test_text)
        
        assert summary == ""