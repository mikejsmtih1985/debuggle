"""
Edge Case Tests for LogProcessor - Target Remaining 14% Coverage! 🎯🔍

These tests target the specific uncovered lines to push coverage from 86% to 90%+.
We're like CSI investigators examining the most obscure evidence trails that
other detectives missed!

Coverage Targets:
- Lines 268->279: Context extractor lazy initialization 
- Lines 295-311: Exception handling fallback in process_log_with_context

This is forensic-level precision testing! 🕵️‍♂️📊
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.debuggle.core.processor import LogProcessor


class TestProcessorEdgeCaseCoverage(unittest.TestCase):
    """
    Forensic Coverage Investigation - Target the Hidden Code Paths! 🔍💎
    
    These are the test cases that separate amateur testers from elite forensic
    investigators. We're hunting down every single line of code like a detective
    following the faintest clues at a crime scene!
    """
    
    def setUp(self):
        """Set up our ultra-precise forensic investigation tools"""
        self.processor = LogProcessor()
    
    def test_context_extractor_lazy_initialization_coverage(self):
        """
        🎯 TARGET: Lines 268-279 - Context Extractor Lazy Loading Path
        
        This test specifically triggers the context_extractor initialization
        path that happens when process_log_with_context is called for the
        first time. It's like catching a criminal in the act of their first crime!
        """
        # Ensure context_extractor starts as None (fresh processor)
        assert self.processor.context_extractor is None, "Context extractor should start as None"
        
        # Create a temporary project structure to work with
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple error that will trigger context processing
            simple_error = "NameError: name 'undefined_variable' is not defined"
            
            # This call should trigger the lazy initialization path (lines 268-279)
            cleaned_log, summary, tags, metadata, rich_context = self.processor.process_log_with_context(
                simple_error,
                project_root=temp_dir,
                language='python'
            )
            
            # Verify the lazy initialization worked
            assert self.processor.context_extractor is not None, "Context extractor should be initialized"
            assert "NameError" in cleaned_log
            assert "FULL DEVELOPMENT CONTEXT ANALYSIS" in rich_context
            assert 'has_rich_context' in metadata
            assert metadata['has_rich_context'] is True
            
            # Verify the initialization happened properly
            assert hasattr(self.processor.context_extractor, 'extract_full_context')
            assert hasattr(self.processor.context_extractor, 'format_context_for_display')
    
    def test_context_processing_exception_fallback_coverage(self):
        """
        🎯 TARGET: Lines 295-311 - Exception Handling Fallback Path
        
        This test forces an exception during context processing to trigger
        the graceful degradation fallback code. It's like testing what happens
        when the CSI lab equipment fails during a critical investigation!
        """
        # Force an exception by mocking the context extractor to fail
        with patch.object(self.processor, 'context_extractor', None):
            # Mock ContextExtractor to raise an exception
            with patch('src.debuggle.core.processor.ContextExtractor') as mock_context_class:
                mock_extractor = Mock()
                mock_context_class.return_value = mock_extractor
                
                # Make extract_full_context raise an exception
                mock_extractor.extract_full_context.side_effect = Exception("CSI equipment malfunction!")
                
                error_text = "RuntimeError: Critical system failure"
                
                # This should trigger the exception handling path (lines 295-311)
                cleaned_log, summary, tags, metadata, rich_context = self.processor.process_log_with_context(
                    error_text,
                    project_root="/valid/path",
                    language='python'
                )
                
                # Verify fallback behavior
                assert "RuntimeError" in cleaned_log
                assert "Context extraction failed" in rich_context or "Basic Error Analysis" in rich_context
                assert 'context_extraction_error' in metadata
                assert "CSI equipment malfunction!" in metadata['context_extraction_error']
                
                # Should still return basic analysis
                assert cleaned_log is not None
                assert isinstance(tags, list)
    
    def test_context_extractor_format_display_exception_coverage(self):
        """
        🎯 Additional Coverage: Test exception in format_context_for_display
        
        This targets any remaining exception handling paths in the context
        processing workflow. Like testing backup detectives when the lead
        investigator gets called away!
        """
        with patch('src.debuggle.core.processor.ContextExtractor') as mock_context_class:
            mock_extractor = Mock()
            mock_context_class.return_value = mock_extractor
            
            # Make extract_full_context work but format_context_for_display fail
            mock_dev_context = Mock()
            mock_dev_context.extraction_metadata = {'context_sources': ['test']}
            mock_extractor.extract_full_context.return_value = mock_dev_context
            mock_extractor.format_context_for_display.side_effect = Exception("Display formatting failed!")
            
            error_text = "ValueError: Display test error"
            
            # This should trigger exception handling during formatting
            cleaned_log, summary, tags, metadata, rich_context = self.processor.process_log_with_context(
                error_text,
                project_root="/test/path",
                language='python'
            )
            
            # Should fall back gracefully
            assert "ValueError" in cleaned_log
            assert "Context extraction failed" in rich_context or "Basic Error Analysis" in rich_context
            assert 'context_extraction_error' in metadata
    
    def test_metadata_timing_calculation_edge_case(self):
        """
        🎯 Coverage: Ensure timing calculations work correctly
        
        This tests the timing metadata calculation paths to ensure we hit
        all the statistics gathering code. Like testing the stopwatch accuracy
        of our crime scene investigation timing!
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple test case
            error_text = "IndexError: list index out of range"
            
            # Process with context to trigger timing calculations
            cleaned_log, summary, tags, metadata, rich_context = self.processor.process_log_with_context(
                error_text,
                project_root=temp_dir,
                language='python'
            )
            
            # Verify timing metadata is present and reasonable
            assert 'processing_time_ms' in metadata
            assert 'context_extraction_time_ms' in metadata
            assert isinstance(metadata['processing_time_ms'], int)
            assert isinstance(metadata['context_extraction_time_ms'], int)
            assert metadata['processing_time_ms'] >= 0
            assert metadata['context_extraction_time_ms'] >= 0
    
    def test_context_sources_metadata_edge_case(self):
        """
        🎯 Coverage: Test context_sources metadata handling
        
        This ensures we hit the metadata extraction paths for context sources.
        Like documenting which detective units contributed to solving the case!
        """
        with patch('src.debuggle.core.processor.ContextExtractor') as mock_context_class:
            mock_extractor = Mock()
            mock_context_class.return_value = mock_extractor
            
            # Mock successful context extraction with specific metadata
            mock_dev_context = Mock()
            mock_dev_context.extraction_metadata = {
                'context_sources': ['file_analysis', 'git_analysis', 'env_analysis']
            }
            mock_extractor.extract_full_context.return_value = mock_dev_context
            mock_extractor.format_context_for_display.return_value = "Mock context display"
            
            error_text = "SyntaxError: invalid syntax"
            
            cleaned_log, summary, tags, metadata, rich_context = self.processor.process_log_with_context(
                error_text,
                project_root="/test/path",
                language='python'
            )
            
            # Verify context_sources metadata is properly extracted
            assert 'context_sources' in metadata
            assert metadata['context_sources'] == ['file_analysis', 'git_analysis', 'env_analysis']
            assert metadata['has_rich_context'] is True


if __name__ == '__main__':
    # Run our forensic edge case investigation!
    unittest.main()