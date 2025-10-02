"""
Test fixtures using the comprehensive stack trace samples.
"""

import pytest
from tests.fixtures.stack_traces import (
    STACK_TRACE_SAMPLES, 
    NON_STACK_TRACE_SAMPLES, 
    EXPECTED_OUTCOMES
)
from app.processor import LogProcessor


class TestStackTraceFixtures:
    """Test various stack trace samples to ensure robust processing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = LogProcessor()
    
    @pytest.mark.parametrize("language,samples", STACK_TRACE_SAMPLES.items())
    def test_language_detection_with_fixtures(self, language, samples):
        """Test language detection with various stack trace samples."""
        for sample_name, sample_text in samples.items():
            if language == "mixed" or language == "mock_data":
                continue  # Skip mixed language samples for this test
                
            detected = self.processor.detect_language(sample_text)
            assert detected == language, f"Failed to detect {language} for {sample_name}"
    
    @pytest.mark.parametrize("language,samples", STACK_TRACE_SAMPLES.items()) 
    def test_stack_trace_detection_with_fixtures(self, language, samples):
        """Test stack trace detection with various samples."""
        for sample_name, sample_text in samples.items():
            is_stack = self.processor._is_stack_trace(sample_text)
            assert is_stack == True, f"Failed to detect stack trace for {language}/{sample_name}"
    
    @pytest.mark.parametrize("sample_name,sample_text", NON_STACK_TRACE_SAMPLES.items())
    def test_non_stack_trace_detection(self, sample_name, sample_text):
        """Test that non-stack-trace content is not detected as stack traces."""
        is_stack = self.processor._is_stack_trace(sample_text)
        assert is_stack == False, f"Incorrectly detected stack trace for {sample_name}"
    
    def test_java_complex_multi_cause_processing(self):
        """Test processing of complex Java stack trace with multiple causes."""
        sample = STACK_TRACE_SAMPLES["java"]["complex"]
        
        # Test full processing pipeline
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="java",
            highlight=True,
            summarize=True,
            tags=True,
            max_lines=1000
        )
        
        expected = EXPECTED_OUTCOMES[sample]
        
        # Check all expected sections are present
        for section in expected["should_have_sections"]:
            assert section in cleaned_log, f"Missing section: {section}"
        
        # Check main exception is mentioned
        assert expected["main_exception"] in cleaned_log
        
        # Check expected tags
        for expected_tag in expected["tags_should_contain"]:
            assert expected_tag in tags, f"Missing expected tag: {expected_tag}"
        
        # Check language detection
        assert metadata["language_detected"] == expected["language"]
        
        # Should have meaningful summary
        assert summary is not None
        assert len(summary) > 20
    
    def test_python_index_error_processing(self):
        """Test processing of Python IndexError."""
        sample = STACK_TRACE_SAMPLES["python"]["simple"]
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="python",
            highlight=True,
            summarize=True,
            tags=True,
            max_lines=1000
        )
        
        expected = EXPECTED_OUTCOMES[sample]
        
        # Check main exception
        assert expected["main_exception"] in cleaned_log
        
        # Check expected tags
        for expected_tag in expected["tags_should_contain"]:
            assert expected_tag in tags, f"Missing expected tag: {expected_tag}"
        
        # Check suggestions contain relevant content
        for suggestion_keyword in expected["suggestions_should_contain"]:
            assert any(suggestion_keyword in cleaned_log.lower() for suggestion_keyword in expected["suggestions_should_contain"])
    
    def test_mock_data_detection(self):
        """Test detection of test/mock data in stack traces."""
        mock_samples = STACK_TRACE_SAMPLES["mock_data"]
        
        for sample_name, sample_text in mock_samples.items():
            tags = self.processor.extract_error_tags(sample_text)
            assert "Test/Mock Data" in tags, f"Failed to detect mock data in {sample_name}"
    
    def test_concurrent_modification_specific_suggestions(self):
        """Test specific suggestions for ConcurrentModificationException."""
        sample = STACK_TRACE_SAMPLES["java"]["concurrent"]
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="java",
            summarize=True,
            tags=True
        )
        
        # Should identify threading issue
        threading_tags = [tag for tag in tags if any(keyword in tag for keyword in ["Thread", "Concurrent", "Race", "Safety"])]
        assert len(threading_tags) > 0, "Should identify threading-related tags"
        
        # Should suggest thread safety solutions
        suggestions_section = cleaned_log.lower()
        thread_safety_keywords = ["thread-safe", "synchronization", "concurrent", "iterator"]
        assert any(keyword in suggestions_section for keyword in thread_safety_keywords), "Should suggest thread safety solutions"
    
    def test_spring_boot_dependency_injection_error(self):
        """Test processing of Spring Boot dependency injection error."""
        sample = STACK_TRACE_SAMPLES["java"]["spring"]
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="java",
            summarize=True,
            tags=True
        )
        
        # Should identify Spring-related tags
        spring_tags = [tag for tag in tags if "Spring" in tag or "Bean" in tag or "Injection" in tag or "Dependency" in tag]
        assert len(spring_tags) > 0, "Should identify Spring/dependency injection tags"
        
        # Should mention key Spring concepts
        assert "BeanCreationException" in cleaned_log
        assert any(keyword in cleaned_log.lower() for keyword in ["bean", "autowired", "dependency"])
    
    def test_very_long_stack_trace_handling(self):
        """Test handling of very long stack traces."""
        sample = STACK_TRACE_SAMPLES["java"]["very_long"]
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="java",
            max_lines=50  # Limit processing
        )
        
        # Should be truncated
        assert metadata["truncated"] == True
        assert metadata["lines"] == 50
        
        # Should still identify the main problem
        assert "StackOverflowError" in cleaned_log
        assert "🚨 **Main Problem**" in cleaned_log
    
    def test_suppressed_exceptions_handling(self):
        """Test handling of suppressed exceptions."""
        sample = STACK_TRACE_SAMPLES["java"]["suppressed"]
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="java",
            summarize=True,
            tags=True
        )
        
        # Should mention suppressed exceptions
        assert "Suppressed" in cleaned_log or "suppressed" in cleaned_log.lower()
        assert "RuntimeException" in cleaned_log
        assert "IOException" in cleaned_log
        assert "SQLException" in cleaned_log
    
    def test_csharp_async_exception_handling(self):
        """Test handling of C# async exceptions."""
        sample = STACK_TRACE_SAMPLES["csharp"]["async"]
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="csharp",
            summarize=True,
            tags=True
        )
        
        # Should identify async-related issues
        async_tags = [tag for tag in tags if any(keyword in tag for keyword in ["Async", "Aggregate", "Task"])]
        assert len(async_tags) > 0, "Should identify async-related tags"
        
        # Should mention async concepts
        assert "AggregateException" in cleaned_log
        assert any(keyword in cleaned_log.lower() for keyword in ["async", "task", "await"])
    
    def test_javascript_module_error_handling(self):
        """Test handling of JavaScript module errors."""
        sample = STACK_TRACE_SAMPLES["javascript"]["module"]
        
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample,
            language="javascript",
            summarize=True,
            tags=True
        )
        
        # Should identify module-related issues
        module_tags = [tag for tag in tags if any(keyword in tag for keyword in ["Module", "Import", "Package", "Dependency"])]
        assert len(module_tags) > 0, "Should identify module-related tags"
        
        # Should suggest module-related solutions
        suggestions_section = cleaned_log.lower()
        module_keywords = ["install", "package", "dependency", "module", "npm"]
        assert any(keyword in suggestions_section for keyword in module_keywords), "Should suggest module installation solutions"
    
    @pytest.mark.parametrize("sample_key,sample_text", [
        ("java_simple", STACK_TRACE_SAMPLES["java"]["simple"]),
        ("python_simple", STACK_TRACE_SAMPLES["python"]["simple"]),
        ("csharp_null", STACK_TRACE_SAMPLES["csharp"]["null_reference"]),
        ("js_type", STACK_TRACE_SAMPLES["javascript"]["type_error"])
    ])
    def test_consistent_enhanced_processing(self, sample_key, sample_text):
        """Test that all stack traces get consistent enhanced processing."""
        cleaned_log, summary, tags, metadata = self.processor.process_log(
            log_input=sample_text,
            language="auto",
            highlight=True,
            summarize=True,
            tags=True
        )
        
        # All stack traces should have enhanced processing
        assert "🚨 **Main Problem**" in cleaned_log, f"Missing main problem section in {sample_key}"
        assert "📋 **What Happened**" in cleaned_log or "💡 **Suggested Actions**" in cleaned_log, f"Missing analysis sections in {sample_key}"
        
        # Should have meaningful tags (not just generic ones)
        generic_tags = {"Error", "Exception"}
        specific_tags = set(tags) - generic_tags
        assert len(specific_tags) > 0, f"No specific tags for {sample_key}, only generic ones"
        
        # Should have a summary
        assert summary is not None, f"No summary generated for {sample_key}"
        assert len(summary) > 10, f"Summary too short for {sample_key}"
        
        # Should detect language correctly
        assert metadata["language_detected"] in ["java", "python", "csharp", "javascript"], f"Invalid language detection for {sample_key}"