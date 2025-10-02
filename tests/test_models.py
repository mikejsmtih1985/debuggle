import pytest
from pydantic import ValidationError
from src.debuggle.models import AnalyzeRequest, AnalyzeOptions, LanguageEnum


class TestAnalyzeRequest:
    def test_valid_request(self):
        """Test creating a valid analyzy request."""
        request = AnalyzeRequest(
            log_input="IndexError: list index out of range",
            language=LanguageEnum.PYTHON,
            options=AnalyzeOptions(highlight=True, summarize=True)
        )
        
        assert request.log_input == "IndexError: list index out of range"
        assert request.language == LanguageEnum.PYTHON
        assert request.options.highlight == True
        assert request.options.summarize == True
    
    def test_default_values(self):
        """Test default values are set correctly."""
        request = AnalyzeRequest(log_input="test error")
        
        assert request.language == LanguageEnum.AUTO
        assert request.options.highlight == True
        assert request.options.summarize == True
        assert request.options.tags == True
        assert request.options.max_lines == 1000
    
    def test_empty_log_input_error(self):
        """Test validation error for empty log input."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(log_input="")
        
        errors = exc_info.value.errors()
        assert any("String should have at least 1 character" in str(error) for error in errors)
    
    def test_whitespace_only_log_input_error(self):
        """Test validation error for whitespace-only log input."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(log_input="   \n  \t  ")
        
        errors = exc_info.value.errors()
        assert any("log_input cannot be empty or whitespace only" in str(error) for error in errors)
    
    def test_log_input_too_long_error(self):
        """Test validation error for log input exceeding max length."""
        long_input = "x" * 50001  # Exceeds 50000 character limit
        
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(log_input=long_input)
        
        errors = exc_info.value.errors()
        assert any("String should have at most 50000 characters" in str(error) for error in errors)


class TestAnalyzeOptions:
    def test_valid_options(self):
        """Test creating valid analyzy options."""
        options = AnalyzeOptions(
            highlight=False,
            summarize=False,
            tags=True,
            max_lines=500
        )
        
        assert options.highlight == False
        assert options.summarize == False
        assert options.tags == True
        assert options.max_lines == 500
    
    def test_max_lines_bounds(self):
        """Test max_lines validation bounds."""
        # Test minimum bound
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeOptions(max_lines=0)
        
        errors = exc_info.value.errors()
        assert any("Input should be greater than or equal to 1" in str(error) for error in errors)
        
        # Test maximum bound
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeOptions(max_lines=5001)
        
        errors = exc_info.value.errors()
        assert any("Input should be less than or equal to 5000" in str(error) for error in errors)
        
        # Test valid values
        valid_options = AnalyzeOptions(max_lines=1)
        assert valid_options.max_lines == 1
        
        valid_options = AnalyzeOptions(max_lines=5000)
        assert valid_options.max_lines == 5000


class TestLanguageEnum:
    def test_all_language_values(self):
        """Test all supported language enum values."""
        languages = [
            LanguageEnum.PYTHON,
            LanguageEnum.JAVASCRIPT,
            LanguageEnum.JAVA,
            LanguageEnum.CSHARP,
            LanguageEnum.CPP,
            LanguageEnum.GO,
            LanguageEnum.RUST,
            LanguageEnum.AUTO
        ]
        
        expected_values = [
            "python", "javascript", "java", "csharp",
            "cpp", "go", "rust", "auto"
        ]
        
        for lang, expected in zip(languages, expected_values):
            assert lang.value == expected
    
    def test_invalid_language_enum(self):
        """Test validation error for invalid language."""
        with pytest.raises(ValidationError) as exc_info:
            AnalyzeRequest(
                log_input="test error",
                language="invalid_language"
            )
        
        errors = exc_info.value.errors()
        assert any("Input should be" in str(error) for error in errors)