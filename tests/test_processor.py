import pytest
from app.processor import LogProcessor


class TestLogProcessor:
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = LogProcessor()
    
    def test_detect_language_python(self):
        """Test Python language detection from traceback."""
        log_text = """
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
        IndexError: list index out of range
        """
        
        language = self.processor.detect_language(log_text)
        assert language == "python"
    
    def test_detect_language_javascript(self):
        """Test JavaScript language detection."""
        log_text = """
        ReferenceError: undefined is not defined
        at app.js:25:10
        at Object.<anonymous> (app.js:30:5)
        """
        
        language = self.processor.detect_language(log_text)
        assert language == "javascript"
    
    def test_detect_language_java(self):
        """Test Java language detection."""
        log_text = """
        Exception in thread "main" java.lang.NullPointerException
        at com.example.Main.main(Main.java:15)
        at java.base/java.lang.String.charAt(String.java:1555)
        """
        
        language = self.processor.detect_language(log_text)
        assert language == "java"
    
    def test_extract_error_tags_python_indexerror(self):
        """Test extracting tags from Python IndexError."""
        log_text = "IndexError: list index out of range"
        
        tags = self.processor.extract_error_tags(log_text)
        assert "IndexError" in tags
        assert "Python" in tags
        assert "Error" in tags
    
    def test_extract_error_tags_javascript_reference_error(self):
        """Test extracting tags from JavaScript ReferenceError."""
        log_text = "ReferenceError: myVariable is not defined"
        
        tags = self.processor.extract_error_tags(log_text)
        assert "ReferenceError" in tags
        assert "Error" in tags
    
    def test_extract_error_tags_stack_trace(self):
        """Test extracting stack trace tag."""
        log_text = """
        Traceback (most recent call last):
          File "test.py", line 1
        Error: something went wrong
        """
        
        tags = self.processor.extract_error_tags(log_text)
        assert "StackTrace" in tags
    
    def test_generate_summary_indexerror(self):
        """Test generating summary for IndexError."""
        log_text = "IndexError: list index out of range"
        
        summary = self.processor.generate_summary(log_text)
        assert summary is not None
        assert "index" in summary.lower()
        assert "exist" in summary.lower()
    
    def test_generate_summary_keyerror(self):
        """Test generating summary for KeyError."""
        log_text = "KeyError: 'missing_key'"
        
        summary = self.processor.generate_summary(log_text)
        assert summary is not None
        assert "key" in summary.lower()
        assert "not found" in summary.lower()
    
    def test_generate_summary_generic_traceback(self):
        """Test generating generic summary for traceback."""
        log_text = """
        Traceback (most recent call last):
          File "test.py", line 5
        SomeUnknownError: something happened
        """
        
        summary = self.processor.generate_summary(log_text)
        assert summary is not None
        assert "error" in summary.lower()
        assert "stack trace" in summary.lower()
    
    def test_clean_and_deduplicate(self):
        """Test cleaning and deduplicating repetitive lines."""
        log_text = """
        Error occurred
        Error occurred
        Error occurred
        Different line
        """
        
        cleaned = self.processor.clean_and_deduplicate(log_text)
        assert "[repeated 3 times]" in cleaned
        assert "Different line" in cleaned
    
    def test_process_log_full_pipeline(self):
        """Test complete log processing pipeline."""
        log_input = """
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
        IndexError: list index out of range
        """
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=log_input,
            language="auto",
            highlight=True,
            summarize=True,
            tags=True,
            max_lines=1000
        )
        
        # Check all components were processed
        assert cleaned_log is not None
        assert len(cleaned_log) > 0
        
        assert summary is not None
        assert "index" in summary.lower()
        
        assert len(tags) > 0
        assert "IndexError" in tags
        
        assert metadata["language_detected"] == "python"
        assert metadata["lines"] > 0
        assert metadata["processing_time_ms"] >= 0
        assert metadata["truncated"] == False
    
    def test_process_log_truncation(self):
        """Test log truncation when exceeding max_lines."""
        # Create a large log
        large_log = "\n".join([f"Line {i}: Error message" for i in range(100)])
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=large_log,
            max_lines=50
        )
        
        assert metadata["lines"] == 50
        assert metadata["truncated"] == True
    
    def test_process_log_no_highlighting(self):
        """Test processing without syntax highlighting."""
        log_input = "Simple error message"
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=log_input,
            highlight=False,
            summarize=False,
            tags=False
        )
        
        # Should return original text without ANSI codes
        assert cleaned_log == log_input
        assert summary is None
        assert len(tags) == 0