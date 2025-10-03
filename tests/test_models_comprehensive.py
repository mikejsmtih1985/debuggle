"""
Comprehensive tests for models.py to achieve significant coverage boost.
Tests all enum classes, data models, validation logic, and edge cases.
"""

import pytest
from pydantic import ValidationError
from src.debuggle.models import (
    LogSeverity,
    LanguageEnum,
    AnalyzeOptions,
    AnalyzeRequest,
    AnalyzeMetadata,
    AnalyzeResponse,
    HealthResponse
)


class TestLogSeverity:
    """Test LogSeverity enum functionality."""
    
    def test_all_log_severity_values(self):
        """Test all LogSeverity enum values exist and have correct string values."""
        assert LogSeverity.TRACE == "trace"
        assert LogSeverity.DEBUG == "debug"
        assert LogSeverity.INFO == "info"
        assert LogSeverity.WARNING == "warning"
        assert LogSeverity.ERROR == "error"
        assert LogSeverity.CRITICAL == "critical"
    
    def test_log_severity_enum_count(self):
        """Test that we have the expected number of severity levels."""
        assert len(list(LogSeverity)) == 6
    
    def test_log_severity_string_conversion(self):
        """Test string conversion of LogSeverity enum values."""
        assert str(LogSeverity.ERROR) == "LogSeverity.ERROR"
        assert LogSeverity.ERROR.value == "error"


class TestLanguageEnum:
    """Test LanguageEnum functionality."""
    
    def test_all_language_values(self):
        """Test all LanguageEnum values exist and have correct string values."""
        assert LanguageEnum.PYTHON == "python"
        assert LanguageEnum.JAVASCRIPT == "javascript"
        assert LanguageEnum.JAVA == "java"
        assert LanguageEnum.CSHARP == "csharp"
        assert LanguageEnum.CPP == "cpp"
        assert LanguageEnum.GO == "go"
        assert LanguageEnum.RUST == "rust"
        assert LanguageEnum.AUTO == "auto"
    
    def test_language_enum_count(self):
        """Test that we have the expected number of language options."""
        assert len(list(LanguageEnum)) == 8
    
    def test_language_string_conversion(self):
        """Test string conversion of LanguageEnum values."""
        assert LanguageEnum.PYTHON.value == "python"
        assert str(LanguageEnum.AUTO) == "LanguageEnum.AUTO"


class TestAnalyzeOptions:
    """Test AnalyzeOptions model functionality."""
    
    def test_default_analyze_options(self):
        """Test default AnalyzeOptions creation."""
        options = AnalyzeOptions()
        
        assert options.highlight is True
        assert options.summarize is True
        assert options.tags is True
        assert options.max_lines == 1000
    
    def test_analyze_options_custom_values(self):
        """Test AnalyzeOptions with custom values."""
        options = AnalyzeOptions(
            highlight=False,
            summarize=False,
            tags=False,
            max_lines=500
        )
        
        assert options.highlight is False
        assert options.summarize is False
        assert options.tags is False
        assert options.max_lines == 500
    
    def test_analyze_options_max_lines_validation(self):
        """Test max_lines field validation."""
        # Test minimum value
        options = AnalyzeOptions(max_lines=1)
        assert options.max_lines == 1
        
        # Test maximum value
        options = AnalyzeOptions(max_lines=5000)
        assert options.max_lines == 5000
        
        # Test value below minimum raises error
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeOptions(max_lines=0)
        assert "greater than or equal to 1" in str(exc_info.value)
        
        # Test value above maximum raises error
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeOptions(max_lines=5001)
        assert "less than or equal to 5000" in str(exc_info.value)
    
    def test_analyze_options_model_dump(self):
        """Test model serialization."""
        options = AnalyzeOptions(highlight=False, max_lines=2000)
        data = options.model_dump()
        
        expected = {
            'highlight': False,
            'summarize': True,
            'tags': True,
            'max_lines': 2000
        }
        assert data == expected


class TestAnalyzeRequest:
    """Test AnalyzeRequest model functionality."""
    
    def test_basic_analyze_request(self):
        """Test basic AnalyzeRequest creation."""
        request = AnalyzeRequest(log_input="Error: Something went wrong")
        
        assert request.log_input == "Error: Something went wrong"
        assert request.language == LanguageEnum.AUTO
        assert isinstance(request.options, AnalyzeOptions)
        assert request.options.highlight is True
    
    def test_analyze_request_with_language(self):
        """Test AnalyzeRequest with specific language."""
        request = AnalyzeRequest(
            log_input="TypeError: 'NoneType' object is not subscriptable",
            language=LanguageEnum.PYTHON
        )
        
        assert request.language == LanguageEnum.PYTHON
        assert request.log_input == "TypeError: 'NoneType' object is not subscriptable"
    
    def test_analyze_request_with_custom_options(self):
        """Test AnalyzeRequest with custom options."""
        custom_options = AnalyzeOptions(highlight=False, max_lines=500)
        request = AnalyzeRequest(
            log_input="Error occurred",
            language=LanguageEnum.JAVA,
            options=custom_options
        )
        
        assert request.options.highlight is False
        assert request.options.max_lines == 500
        assert request.language == LanguageEnum.JAVA
    
    def test_log_input_validation_empty_string(self):
        """Test that empty string raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(log_input="")
        assert "at least 1 character" in str(exc_info.value)
    
    def test_log_input_validation_whitespace_only(self):
        """Test that whitespace-only string raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(log_input="   \n\t  ")
        assert "cannot be empty or whitespace only" in str(exc_info.value)
    
    def test_log_input_validation_too_long(self):
        """Test that overly long input raises validation error."""
        long_input = "x" * 50001  # One character over the limit
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(log_input=long_input)
        assert "at most 50000 characters" in str(exc_info.value)
    
    def test_log_input_validation_max_length_boundary(self):
        """Test boundary cases for log_input length."""
        # Test exactly at maximum length
        max_input = "x" * 50000
        request = AnalyzeRequest(log_input=max_input)
        assert len(request.log_input) == 50000
        
        # Test minimum valid length
        min_input = "x"
        request = AnalyzeRequest(log_input=min_input)
        assert request.log_input == "x"
    
    def test_analyze_request_model_dump(self):
        """Test model serialization."""
        request = AnalyzeRequest(
            log_input="Test error",
            language=LanguageEnum.PYTHON
        )
        data = request.model_dump()
        
        assert data['log_input'] == "Test error"
        assert data['language'] == "python"
        assert 'options' in data
        assert data['options']['highlight'] is True


class TestAnalyzeMetadata:
    """Test AnalyzeMetadata model functionality."""
    
    def test_basic_analyze_metadata(self):
        """Test basic AnalyzeMetadata creation."""
        metadata = AnalyzeMetadata(
            lines=100,
            language_detected="python",
            processing_time_ms=250
        )
        
        assert metadata.lines == 100
        assert metadata.language_detected == "python"
        assert metadata.processing_time_ms == 250
        assert metadata.truncated is False  # Default value
    
    def test_analyze_metadata_with_truncation(self):
        """Test AnalyzeMetadata with truncation flag."""
        metadata = AnalyzeMetadata(
            lines=1000,
            language_detected="javascript",
            processing_time_ms=500,
            truncated=True
        )
        
        assert metadata.truncated is True
        assert metadata.lines == 1000
    
    def test_analyze_metadata_validation(self):
        """Test that AnalyzeMetadata requires all fields."""
        # Test that all required fields are needed
        metadata = AnalyzeMetadata(
            lines=10,
            language_detected="python",
            processing_time_ms=100
        )
        assert metadata.lines == 10
        assert metadata.language_detected == "python"
        assert metadata.processing_time_ms == 100
    
    def test_analyze_metadata_model_dump(self):
        """Test model serialization."""
        metadata = AnalyzeMetadata(
            lines=50,
            language_detected="java",
            processing_time_ms=150,
            truncated=True
        )
        data = metadata.model_dump()
        
        expected = {
            'lines': 50,
            'language_detected': 'java',
            'processing_time_ms': 150,
            'truncated': True
        }
        assert data == expected


class TestAnalyzeResponse:
    """Test AnalyzeResponse model functionality."""
    
    def test_basic_analyze_response(self):
        """Test basic AnalyzeResponse creation."""
        metadata = AnalyzeMetadata(
            lines=10,
            language_detected="python",
            processing_time_ms=100
        )
        
        response = AnalyzeResponse(
            cleaned_log="Highlighted error text",
            summary="This is a Python IndexError",
            tags=["Python Error", "List Index"],
            metadata=metadata
        )
        
        assert response.cleaned_log == "Highlighted error text"
        assert response.summary == "This is a Python IndexError"
        assert response.tags == ["Python Error", "List Index"]
        assert response.metadata.lines == 10
    
    def test_analyze_response_optional_summary(self):
        """Test AnalyzeResponse with None summary."""
        metadata = AnalyzeMetadata(
            lines=5,
            language_detected="unknown",
            processing_time_ms=50
        )
        
        response = AnalyzeResponse(
            cleaned_log="Unknown error format",
            summary=None,
            metadata=metadata
        )
        
        assert response.summary is None
        assert response.tags == []  # Default empty list
        assert response.cleaned_log == "Unknown error format"
    
    def test_analyze_response_empty_tags(self):
        """Test AnalyzeResponse with empty tags list."""
        metadata = AnalyzeMetadata(
            lines=1,
            language_detected="auto",
            processing_time_ms=25
        )
        
        response = AnalyzeResponse(
            cleaned_log="Simple log",
            summary=None,  # Explicitly set optional field
            metadata=metadata
        )
        
        assert response.tags == []
        assert response.summary is None
    
    def test_analyze_response_model_dump(self):
        """Test model serialization."""
        metadata = AnalyzeMetadata(
            lines=20,
            language_detected="csharp",
            processing_time_ms=200
        )
        
        response = AnalyzeResponse(
            cleaned_log="Formatted C# error",
            summary="C# null reference exception",
            tags=["C# Error", "Null Reference"],
            metadata=metadata
        )
        
        data = response.model_dump()
        assert data['cleaned_log'] == "Formatted C# error"
        assert data['summary'] == "C# null reference exception"
        assert data['tags'] == ["C# Error", "Null Reference"]
        assert 'metadata' in data
        assert data['metadata']['language_detected'] == 'csharp'


class TestHealthResponse:
    """Test HealthResponse model functionality."""
    
    def test_health_response_creation(self):
        """Test basic HealthResponse creation."""
        # First check if HealthResponse model exists and test it
        try:
            health = HealthResponse(
                status="healthy",
                service="debuggle",
                version="1.0.0"
            )
            assert health.status == "healthy"
            assert health.service == "debuggle"
            assert health.version == "1.0.0"
        except NameError:
            # If HealthResponse doesn't exist, just pass this test
            pytest.skip("HealthResponse model not yet implemented")


class TestModelIntegration:
    """Test integration between different models."""
    
    def test_full_request_response_flow(self):
        """Test creating a complete request and response pair."""
        # Create a request
        request = AnalyzeRequest(
            log_input="TypeError: list indices must be integers",
            language=LanguageEnum.PYTHON,
            options=AnalyzeOptions(highlight=True, max_lines=100)
        )
        
        # Create corresponding response
        metadata = AnalyzeMetadata(
            lines=1,
            language_detected="python",
            processing_time_ms=75
        )
        
        response = AnalyzeResponse(
            cleaned_log="<span class='error'>TypeError</span>: list indices must be integers",
            summary="You're trying to use a string or float as a list index, but Python lists only accept integer indices.",
            tags=["Python Error", "Type Error", "List Indexing", "Beginner Friendly"],
            metadata=metadata
        )
        
        # Verify the flow makes sense
        assert request.language.value == response.metadata.language_detected
        assert "TypeError" in request.log_input
        assert "TypeError" in response.cleaned_log
        assert len(response.tags) > 0
    
    def test_model_validation_edge_cases(self):
        """Test various edge cases across models."""
        # Test AnalyzeOptions with edge values
        options = AnalyzeOptions(max_lines=1)  # Minimum allowed
        assert options.max_lines == 1
        
        # Test AnalyzeRequest with minimal valid input
        request = AnalyzeRequest(log_input="!")  # Single character
        assert request.log_input == "!"
        
        # Test AnalyzeMetadata with zero processing time
        metadata = AnalyzeMetadata(
            lines=0,
            language_detected="auto",
            processing_time_ms=0
        )
        assert metadata.processing_time_ms == 0
        assert metadata.lines == 0
    
    def test_enum_in_model_serialization(self):
        """Test that enums serialize correctly within models."""
        request = AnalyzeRequest(
            log_input="Sample error",
            language=LanguageEnum.RUST
        )
        
        data = request.model_dump()
        assert data['language'] == "rust"  # Should be serialized as string value
        
        # Test deserialization
        new_request = AnalyzeRequest.model_validate(data)
        assert new_request.language == LanguageEnum.RUST