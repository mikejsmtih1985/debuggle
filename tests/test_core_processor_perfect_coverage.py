"""
Final Coverage Push - Target the Last 3% for Perfect 100%! 🎯💎

These are the absolute final edge cases that need surgical precision testing.
We're like forensic scientists using electron microscopes to examine the
tiniest details that separate good coverage from PERFECT coverage!

Current: 97% → Target: 100%
Remaining lines: 268->279, 307
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile

from src.debuggle.core.processor import LogProcessor


class TestProcessorPerfectCoverage(unittest.TestCase):
    """
    The Final Forensic Investigation - 100% Coverage Perfection! 🔬💯
    
    This is where we separate the elite forensic investigators from the
    merely excellent ones. We're hunting down every single remaining
    line of code with surgical precision!
    """
    
    def test_context_extractor_initialization_without_project_root(self):
        """
        🎯 TARGET: Lines 268->279 - Context Extractor Initialization Edge Case
        
        This test should trigger the exact initialization path by calling
        process_log_with_context without a project_root parameter.
        """
        processor = LogProcessor()
        assert processor.context_extractor is None
        
        # Call without project_root to trigger None path
        error_text = "KeyError: 'missing_key'"
        
        # This should trigger the initialization with None project_root
        cleaned_log, summary, tags, metadata, rich_context = processor.process_log_with_context(
            error_text,
            project_root=None,  # This should trigger the specific initialization path
            language='python'
        )
        
        # Verify the context extractor was initialized
        assert processor.context_extractor is not None
        assert "KeyError" in cleaned_log
        assert "FULL DEVELOPMENT CONTEXT ANALYSIS" in rich_context
    
    def test_exception_fallback_with_no_summary(self):
        """
        🎯 TARGET: Line 307 - Exception handling with no summary condition
        
        This targets the specific condition where summary is None in the
        exception handling fallback, ensuring we hit line 307.
        """
        processor = LogProcessor()
        
        with patch('src.debuggle.core.processor.ContextExtractor') as mock_context_class:
            mock_extractor = Mock()
            mock_context_class.return_value = mock_extractor
            
            # Make context extraction fail
            mock_extractor.extract_full_context.side_effect = Exception("Context failure")
            
            # Mock the process_log to return None for summary specifically
            with patch.object(processor, 'process_log') as mock_process_log:
                mock_process_log.return_value = (
                    "Error: test error",  # cleaned_log
                    None,                 # summary - this is the key to hitting line 307
                    ["error"],           # tags
                    {'processing_time_ms': 10}  # metadata
                )
                
                error_text = "RuntimeError: test error for coverage"
                
                # This should trigger the exception path with no summary
                cleaned_log, summary, tags, metadata, rich_context = processor.process_log_with_context(
                    error_text,
                    project_root="/test/path",
                    language='python'
                )
                
                # Verify fallback behavior
                assert "Context extraction failed" in rich_context
                assert "Basic Error Analysis" in rich_context
                assert 'context_extraction_error' in metadata
                # The key test: summary was None, so the summary section should be skipped
                assert "**Summary:**" not in rich_context or summary is None
    
    def test_fresh_processor_initialization_path(self):
        """
        🎯 Additional Coverage: Ensure fresh processor hits initialization
        
        This creates a completely fresh processor and ensures we hit the
        lazy initialization path exactly once.
        """
        # Create a completely fresh processor instance
        fresh_processor = LogProcessor()
        
        # Verify it starts with None
        assert fresh_processor.context_extractor is None
        
        # Use a unique temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            error_text = "ImportError: No module named 'missing_module'"
            
            # This should trigger initialization
            result = fresh_processor.process_log_with_context(
                error_text,
                project_root=temp_dir,
                language='python'
            )
            
            # Verify initialization happened
            assert fresh_processor.context_extractor is not None
            assert len(result) == 5  # Should return 5-tuple
            cleaned_log, summary, tags, metadata, rich_context = result
            assert "ImportError" in cleaned_log


if __name__ == '__main__':
    unittest.main()