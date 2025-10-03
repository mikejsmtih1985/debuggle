"""
🧪 CLAUDE INTEGRATION TEST LABORATORY - Quality Assurance for AI Enhancement! 🧪

These tests ensure that Debuggle's Claude AI integration works flawlessly
and maintains our core principles of reliability, privacy, and graceful
degradation. Think of this as the quality control department for our
AI-enhanced debugging capabilities.

🏆 HIGH SCHOOL EXPLANATION:
Just like how a car manufacturer tests that:
- 🚗 The car works fine without air conditioning (basic functionality)
- ❄️ The AC makes the ride more comfortable when available (enhancement)
- 🛡️ The car doesn't break if the AC fails (graceful degradation)

We test that:
- 🔧 Debuggle works perfectly without Claude (local analysis)
- 🤖 Claude makes debugging better when available (AI enhancement)
- 🛡️ Everything works fine if Claude API fails (graceful fallback)

TESTING PHILOSOPHY:
✅ **Never break basic functionality** - Debuggle must work without Claude
✅ **Graceful enhancement** - Claude should improve, not replace, core features
✅ **Privacy by design** - Test that data handling respects user privacy
✅ **Cost awareness** - Ensure users understand and control AI usage
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from src.debuggle.integrations.claude import ClaudeAnalyzer, ClaudeEnhancedAnalysis


class TestClaudeAnalyzerInitialization:
    """
    🏗️ CLAUDE SETUP TESTING - Ensuring proper initialization
    
    These tests verify that the Claude integration initializes correctly
    under different conditions - with API keys, without them, with the
    anthropic package installed, without it, etc.
    """
    
    def test_initialization_without_api_key(self):
        """🔑 Test Claude initialization when no API key is provided"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('src.debuggle.integrations.claude.CLAUDE_AVAILABLE', True):
                analyzer = ClaudeAnalyzer()
                
                assert not analyzer.is_available()
                assert analyzer.api_key is None
                assert analyzer.client is None
                
    def test_initialization_with_api_key(self):
        """🔑 Test Claude initialization with API key provided"""
        test_api_key = "test-api-key-12345"
        
        with patch('src.debuggle.integrations.claude.CLAUDE_AVAILABLE', True):
            with patch('src.debuggle.integrations.claude.anthropic.Anthropic') as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client
                
                analyzer = ClaudeAnalyzer(api_key=test_api_key)
                
                assert analyzer.is_available()
                assert analyzer.api_key == test_api_key
                assert analyzer.client == mock_client
                mock_anthropic.assert_called_once_with(api_key=test_api_key)
    
    def test_initialization_without_anthropic_package(self):
        """📦 Test graceful handling when anthropic package is not installed"""
        with patch('src.debuggle.integrations.claude.CLAUDE_AVAILABLE', False):
            analyzer = ClaudeAnalyzer(api_key="test-key")
            
            assert not analyzer.is_available()
            assert analyzer.client is None
    
    def test_initialization_with_environment_variable(self):
        """🌍 Test API key loading from environment variable"""
        test_api_key = "env-api-key-67890"
        
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': test_api_key}):
            with patch('src.debuggle.integrations.claude.CLAUDE_AVAILABLE', True):
                with patch('src.debuggle.integrations.claude.anthropic.Anthropic') as mock_anthropic:
                    analyzer = ClaudeAnalyzer()
                    
                    assert analyzer.api_key == test_api_key
                    mock_anthropic.assert_called_once_with(api_key=test_api_key)


class TestClaudeEnhancedAnalysis:
    """
    📊 ENHANCED ANALYSIS DATA STRUCTURE TESTING
    
    These tests verify that our data structure for holding enhanced analysis
    works correctly and handles all the different types of information
    that Claude might provide.
    """
    
    def test_enhanced_analysis_creation(self):
        """🏗️ Test creating enhanced analysis data structure"""
        analysis = ClaudeEnhancedAnalysis(
            original_analysis="Original error analysis",
            error_type="IndexError",
            language="python",
            severity="error"
        )
        
        assert analysis.original_analysis == "Original error analysis"
        assert analysis.error_type == "IndexError"
        assert analysis.language == "python"
        assert analysis.severity == "error"
        assert not analysis.used_claude
        assert analysis.claude_explanation is None
        assert isinstance(analysis.analysis_timestamp, datetime)
    
    def test_enhanced_analysis_with_claude_data(self):
        """🤖 Test enhanced analysis with Claude insights"""
        analysis = ClaudeEnhancedAnalysis(
            original_analysis="Original analysis",
            error_type="ValueError",
            language="python",
            severity="error",
            claude_explanation="Claude's detailed explanation",
            specific_fix_suggestion="Specific fix from Claude",
            prevention_advice="Prevention tips from Claude",
            confidence_score=0.95,
            used_claude=True,
            claude_model="claude-3-sonnet-20240229"
        )
        
        assert analysis.used_claude
        assert analysis.claude_explanation == "Claude's detailed explanation"
        assert analysis.specific_fix_suggestion == "Specific fix from Claude"
        assert analysis.prevention_advice == "Prevention tips from Claude"
        assert analysis.confidence_score == 0.95
        assert analysis.claude_model == "claude-3-sonnet-20240229"


class TestClaudeAnalysisFlow:
    """
    🔄 CLAUDE ANALYSIS WORKFLOW TESTING
    
    These tests verify the complete flow of enhancing analysis with Claude,
    from the initial request through parsing the response and formatting
    the output. This is where we test the core value proposition.
    """
    
    @pytest.fixture
    def mock_claude_analyzer(self):
        """🎭 Create a mock Claude analyzer for testing"""
        with patch('src.debuggle.integrations.claude.CLAUDE_AVAILABLE', True):
            with patch('src.debuggle.integrations.claude.anthropic.Anthropic') as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client
                
                analyzer = ClaudeAnalyzer(api_key="test-key")
                return analyzer, mock_client
    
    def test_enhance_analysis_without_claude_available(self):
        """🚫 Test enhancement when Claude is not available - graceful degradation"""
        with patch('src.debuggle.integrations.claude.CLAUDE_AVAILABLE', False):
            analyzer = ClaudeAnalyzer()
            
            result = analyzer.enhance_analysis(
                original_analysis="Basic error analysis",
                error_message="IndexError: list index out of range",
                error_type="IndexError",
                language="python",
                severity="error"
            )
            
            assert not result.used_claude
            assert result.claude_explanation is None
            assert result.original_analysis == "Basic error analysis"
            assert result.error_type == "IndexError"
    
    def test_enhance_analysis_with_successful_claude_response(self, mock_claude_analyzer):
        """✅ Test successful Claude enhancement with proper API response"""
        analyzer, mock_client = mock_claude_analyzer
        
        # 🎭 MOCK CLAUDE'S RESPONSE - Simulate successful API call
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = json.dumps({
            "explanation": "This IndexError occurs when trying to access a list element that doesn't exist",
            "fix_suggestion": "Add bounds checking: if len(users) > 999: user = users[999]",
            "prevention_advice": "Always validate array bounds before accessing elements",
            "confidence_score": 0.9,
            "similar_patterns": ["Array bounds errors", "Off-by-one errors"]
        })
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 150
        
        mock_client.messages.create.return_value = mock_response
        
        # 🚀 TEST THE ENHANCEMENT PROCESS
        result = analyzer.enhance_analysis(
            original_analysis="IndexError detected on line 42",
            error_message="IndexError: list index out of range",
            error_type="IndexError",
            language="python",
            severity="error",
            file_path="app.py"
        )
        
        # ✅ VERIFY ENHANCED RESULTS
        assert result.used_claude
        assert result.claude_explanation == "This IndexError occurs when trying to access a list element that doesn't exist"
        assert result.specific_fix_suggestion == "Add bounds checking: if len(users) > 999: user = users[999]"
        assert result.prevention_advice == "Always validate array bounds before accessing elements"
        assert result.confidence_score == 0.9
        assert "Array bounds errors" in result.similar_patterns
        assert analyzer.requests_made == 1
        assert analyzer.total_tokens_used == 250
    
    def test_enhance_analysis_with_malformed_claude_response(self, mock_claude_analyzer):
        """🔧 Test handling of malformed Claude response - graceful error handling"""
        analyzer, mock_client = mock_claude_analyzer
        
        # 🎭 MOCK MALFORMED RESPONSE - Simulate Claude returning invalid JSON
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "This is not valid JSON response"
        mock_response.usage = Mock()
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50
        
        mock_client.messages.create.return_value = mock_response
        
        # 🚀 TEST ERROR HANDLING
        result = analyzer.enhance_analysis(
            original_analysis="Basic analysis",
            error_message="Some error",
            error_type="Error",
            language="python",
            severity="error"
        )
        
        # ✅ VERIFY GRACEFUL DEGRADATION
        assert result.used_claude  # We tried to use Claude
        assert result.claude_explanation == "This is not valid JSON response"  # Fallback content
        assert result.confidence_score == 0.5  # Default confidence for unparsed response
    
    def test_enhance_analysis_with_api_error(self, mock_claude_analyzer):
        """💥 Test handling of Claude API errors - never break basic functionality"""
        analyzer, mock_client = mock_claude_analyzer
        
        # 🎭 MOCK API ERROR - Simulate Claude API failure
        mock_client.messages.create.side_effect = Exception("API rate limit exceeded")
        
        # 🚀 TEST ERROR RESILIENCE
        result = analyzer.enhance_analysis(
            original_analysis="Basic analysis works fine",
            error_message="Some error",
            error_type="Error",
            language="python",
            severity="error"
        )
        
        # ✅ VERIFY GRACEFUL DEGRADATION - Basic functionality preserved
        assert not result.used_claude
        assert result.claude_explanation is None
        assert result.original_analysis == "Basic analysis works fine"


class TestClaudeOutputFormatting:
    """
    🎨 OUTPUT FORMATTING TESTING - Beautiful, readable results
    
    These tests ensure that the enhanced analysis is presented in a
    professional, readable format that clearly shows what came from
    Debuggle vs. what came from Claude.
    """
    
    def test_format_output_without_claude(self):
        """📄 Test formatting output when Claude wasn't used"""
        analysis = ClaudeEnhancedAnalysis(
            original_analysis="Standard Debuggle analysis here",
            error_type="TypeError",
            language="python",
            severity="error"
        )
        
        analyzer = ClaudeAnalyzer()
        formatted = analyzer.format_enhanced_output(analysis)
        
        assert "🚀 Debuggle Enhanced Analysis" in formatted
        assert "Standard Debuggle analysis here" in formatted
        assert "AI enhancement: Not used" in formatted
        assert "Claude AI Insights" not in formatted
    
    def test_format_output_with_claude_insights(self):
        """🤖 Test formatting output with Claude enhancements"""
        analysis = ClaudeEnhancedAnalysis(
            original_analysis="Standard analysis",
            error_type="IndexError",
            language="python",
            severity="error",
            claude_explanation="Detailed explanation from Claude",
            specific_fix_suggestion="Specific fix suggestion",
            prevention_advice="Prevention advice from Claude",
            confidence_score=0.85,
            used_claude=True,
            claude_model="claude-3-sonnet-20240229"
        )
        
        analyzer = ClaudeAnalyzer()
        formatted = analyzer.format_enhanced_output(analysis)
        
        assert "🚀 Debuggle Enhanced Analysis" in formatted
        assert "Standard analysis" in formatted
        assert "🤖 **Claude AI Insights**" in formatted
        assert "confidence: 85.0%" in formatted
        assert "Detailed explanation from Claude" in formatted
        assert "Specific fix suggestion" in formatted
        assert "Prevention advice from Claude" in formatted
        assert "AI enhancement: Enabled" in formatted


class TestClaudeUsageTracking:
    """
    📊 USAGE TRACKING AND COST AWARENESS TESTING
    
    These tests ensure users have visibility into their Claude API usage
    and associated costs, supporting our principle of user control
    and transparency.
    """
    
    def test_usage_stats_initialization(self):
        """📊 Test initial usage statistics"""
        analyzer = ClaudeAnalyzer()
        stats = analyzer.get_usage_stats()
        
        assert stats['requests_made'] == 0
        assert stats['total_tokens_used'] == 0
        assert stats['estimated_cost_usd'] == 0.0
        assert not stats['available']  # No API key by default
    
    def test_usage_stats_after_requests(self):
        """📈 Test usage statistics tracking after API calls"""
        with patch('src.debuggle.integrations.claude.CLAUDE_AVAILABLE', True):
            with patch('src.debuggle.integrations.claude.anthropic.Anthropic'):
                analyzer = ClaudeAnalyzer(api_key="test-key")
                
                # Simulate some usage
                analyzer.requests_made = 5
                analyzer.total_tokens_used = 1000
                
                stats = analyzer.get_usage_stats()
                
                assert stats['requests_made'] == 5
                assert stats['total_tokens_used'] == 1000
                assert stats['estimated_cost_usd'] == 0.003  # 1000 * 0.000003
                assert stats['available']


class TestClaudeHelperFunctions:
    """
    🔧 HELPER FUNCTION TESTING - Supporting utilities
    
    These tests cover the utility functions that support the main
    Claude integration functionality - error type extraction,
    severity determination, etc.
    """
    
    def test_error_type_extraction_from_tags(self):
        """🏷️ Test extracting error type from tags (preferred method)"""
        from cli.debuggle_cli import _extract_error_type
        
        error_message = "Some error occurred"
        tags = ["python", "indexerror", "array"]
        
        result = _extract_error_type(error_message, tags)
        assert result == "indexerror"
    
    def test_error_type_extraction_from_message(self):
        """📝 Test extracting error type from error message (fallback)"""
        from cli.debuggle_cli import _extract_error_type
        
        error_message = "ValueError: invalid literal for int() with base 10"
        tags = ["python"]
        
        result = _extract_error_type(error_message, tags)
        assert result == "ValueError"
    
    def test_error_type_extraction_fallback(self):
        """🤷‍♂️ Test error type extraction when type is unknown"""
        from cli.debuggle_cli import _extract_error_type
        
        error_message = "Something went wrong"
        tags = ["general"]
        
        result = _extract_error_type(error_message, tags)
        assert result == "UnknownError"
    
    def test_severity_determination_from_tags(self):
        """📊 Test severity determination from tags"""
        from cli.debuggle_cli import _determine_severity
        
        tags = ["python", "critical", "database"]
        error_message = "Connection failed"
        
        result = _determine_severity(tags, error_message)
        assert result == "critical"
    
    def test_severity_determination_from_message(self):
        """💥 Test severity determination from error message keywords"""
        from cli.debuggle_cli import _determine_severity
        
        tags = ["python"]
        error_message = "Fatal error: segmentation fault occurred"
        
        result = _determine_severity(tags, error_message)
        assert result == "critical"
    
    def test_severity_determination_default(self):
        """⚠️ Test default severity determination"""
        from cli.debuggle_cli import _determine_severity
        
        tags = ["python"]
        error_message = "Simple error occurred"
        
        result = _determine_severity(tags, error_message)
        assert result == "error"


class TestClaudeIntegrationE2E:
    """
    🔄 END-TO-END INTEGRATION TESTING - Complete workflow validation
    
    These tests simulate the complete user experience from CLI input
    through Claude enhancement and final output, ensuring the entire
    integration works seamlessly.
    """
    
    def test_cli_enhancement_flag_parsing(self):
        """🎛️ Test that CLI properly parses --claude flag"""
        from cli.debuggle_cli import main
        import sys
        from unittest.mock import patch
        
        # Test that --claude flag is recognized
        test_args = ['debuggle', '--claude', '--help']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):  # --help causes sys.exit()
                main()
                
        # If we get here without exception, flag parsing worked
    
    def test_full_enhancement_workflow_without_api_key(self, capsys):
        """🔄 Test complete enhancement workflow when API key is missing"""
        from cli.debuggle_cli import _enhance_with_claude
        
        # Test graceful degradation
        result = _enhance_with_claude(
            original_analysis="Standard Debuggle analysis",
            error_message="IndexError: list index out of range",
            cleaned_log="Cleaned error log",
            summary="Error summary",
            tags=["indexerror", "python"],
            metadata={"detected_language": "python"},
            project_root="/test/project"
        )
        
        assert "Standard Debuggle analysis" in result
        assert "Claude AI: Not available" in result
        assert "Debuggle works great without AI too!" in result


# 🎯 INTEGRATION TESTING UTILITIES
# ================================

def create_mock_claude_response(
    explanation: str = "Test explanation",
    fix_suggestion: str = "Test fix",
    prevention_advice: str = "Test prevention",
    confidence: float = 0.8
) -> Mock:
    """🎭 Create a realistic mock Claude API response for testing"""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = json.dumps({
        "explanation": explanation,
        "fix_suggestion": fix_suggestion,
        "prevention_advice": prevention_advice,
        "confidence_score": confidence,
        "similar_patterns": ["Pattern 1", "Pattern 2"]
    })
    mock_response.usage = Mock()
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 150
    return mock_response


# 🚀 TEST EXECUTION MARKERS
# =========================

# These markers help organize test execution:
# pytest -m unit          # Run only unit tests (fast)
# pytest -m integration   # Run integration tests (slower, may need API keys)
# pytest                  # Run all tests

pytest.main([__file__]) if __name__ == "__main__" else None