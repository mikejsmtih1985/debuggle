"""
Refactored log processor using modular architecture.

This is the main interface that orchestrates error analysis, context extraction,
and response formatting.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any

from .analyzer import ErrorAnalyzer, AnalysisRequest, AnalysisResult
from .context import ContextExtractor, DevelopmentContext
from .patterns import ErrorPatternMatcher


logger = logging.getLogger(__name__)


class LogProcessor:
    """
    Main log processing engine with modular architecture.
    
    This class provides a clean interface for the legacy API while using
    the new modular components internally.
    """
    
    def __init__(self):
        """Initialize processor with core components."""
        self.analyzer = ErrorAnalyzer()
        self.context_extractor = None  # Lazy initialization
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def process_log(
        self, 
        log_input: str, 
        language: str = 'auto', 
        highlight: bool = True, 
        summarize: bool = True, 
        tags: bool = True, 
        max_lines: int = 1000
    ) -> Tuple[str, Optional[str], List[str], Dict[str, Any]]:
        """
        Process a log entry with beautification and analysis.
        
        This maintains compatibility with the existing API while using
        the new modular architecture internally.
        
        Args:
            log_input: Raw log or stack trace text
            language: Programming language hint
            highlight: Whether to apply syntax highlighting (legacy parameter)
            summarize: Whether to generate a summary
            tags: Whether to generate tags
            max_lines: Maximum lines to process
            
        Returns:
            Tuple of (cleaned_log, summary, tags, metadata)
        """
        start_time = time.time()
        
        try:
            # Truncate if necessary
            lines = log_input.split('\n')
            truncated = len(lines) > max_lines
            if truncated:
                lines = lines[:max_lines]
                log_input = '\n'.join(lines)
            
            # Create analysis request
            request = AnalysisRequest(
                text=log_input,
                language=language if language != 'auto' else None,
                include_context=True,
                include_suggestions=summarize,
                include_tags=tags,
                max_matches=5
            )
            
            # Perform analysis
            result = self.analyzer.analyze(request)
            
            # Format the cleaned log (for now, just return the original with some cleanup)
            cleaned_log = self._format_cleaned_log(log_input, result)
            
            # Generate summary if requested
            summary = result.summary if summarize else None
            
            # Get tags
            tags_list = result.tags if tags else []
            
            # Build metadata
            processing_time = int((time.time() - start_time) * 1000)
            metadata = {
                'lines': len(lines),
                'language_detected': result.detected_language or 'unknown',
                'processing_time_ms': processing_time,
                'truncated': truncated,
                'errors_found': len(result.all_matches),
                'primary_error': result.primary_error.pattern.name if result.primary_error else None
            }
            
            return cleaned_log, summary, tags_list, metadata
            
        except Exception as e:
            self.logger.error(f"Log processing failed: {e}", exc_info=True)
            
            # Return basic fallback result
            processing_time = int((time.time() - start_time) * 1000)
            return (
                log_input,  # Return original input
                f"Processing failed: {str(e)}",
                ["processing-error"],
                {
                    'lines': len(log_input.split('\n')),
                    'language_detected': 'unknown',
                    'processing_time_ms': processing_time,
                    'truncated': False,
                    'error': str(e)
                }
            )
    
    def process_log_with_context(
        self,
        log_input: str,
        project_root: Optional[str] = None,
        file_path: Optional[str] = None,
        language: str = 'auto',
        highlight: bool = True,
        summarize: bool = True,
        tags: bool = True,
        max_lines: int = 1000
    ) -> Tuple[str, Optional[str], List[str], Dict[str, Any], str]:
        """
        Process log with full development context extraction.
        
        This is our "ChatGPT killer" feature that provides context
        that developers never include when copy-pasting to ChatGPT.
        
        Args:
            log_input: Raw log or stack trace text
            project_root: Root directory for context extraction
            file_path: Specific file path if known
            language: Programming language hint
            highlight: Whether to apply syntax highlighting (legacy)
            summarize: Whether to generate a summary
            tags: Whether to generate tags
            max_lines: Maximum lines to process
            
        Returns:
            Tuple of (cleaned_log, summary, tags, metadata, rich_context)
        """
        start_time = time.time()
        
        try:
            # First do the basic processing
            cleaned_log, summary, tags_list, metadata = self.process_log(
                log_input, language, highlight, summarize, tags, max_lines
            )
            
            # Extract development context
            if self.context_extractor is None:
                self.context_extractor = ContextExtractor(project_root)
            
            dev_context = self.context_extractor.extract_full_context(log_input, file_path)
            
            # Format context for display
            rich_context = self.context_extractor.format_context_for_display(dev_context)
            
            # Add context extraction time to metadata
            context_time = int((time.time() - start_time) * 1000)
            metadata['context_extraction_time_ms'] = context_time - metadata['processing_time_ms']
            metadata['has_rich_context'] = True
            metadata['context_sources'] = dev_context.extraction_metadata.get('context_sources', [])
            
            return cleaned_log, summary, tags_list, metadata, rich_context
            
        except Exception as e:
            self.logger.error(f"Context processing failed: {e}", exc_info=True)
            
            # Fall back to basic processing
            cleaned_log, summary, tags_list, metadata = self.process_log(
                log_input, language, highlight, summarize, tags, max_lines
            )
            
            error_context = f"❌ Context extraction failed: {str(e)}\n\n"
            error_context += "📋 **Basic Error Analysis:**\n"
            error_context += f"```\n{cleaned_log}\n```\n\n"
            if summary:
                error_context += f"**Summary:** {summary}"
            
            metadata['context_extraction_error'] = str(e)
            
            return cleaned_log, summary, tags_list, metadata, error_context
    
    def _format_cleaned_log(self, original_text: str, analysis_result: AnalysisResult) -> str:
        """
        Format the cleaned log output.
        
        For now, this does basic cleanup. In the future, this could include
        syntax highlighting, line numbering, etc.
        """
        # Basic cleanup: remove excessive whitespace and empty lines
        lines = original_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.rstrip()
            if stripped or (cleaned_lines and cleaned_lines[-1]):  # Keep non-empty lines and single empty lines
                cleaned_lines.append(stripped)
        
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def detect_language(self, text: str) -> str:
        """Detect programming language from text."""
        detected = self.analyzer.pattern_matcher.detect_language(text)
        return detected or 'unknown'
    
    def extract_error_tags(self, text: str) -> List[str]:
        """Extract error tags from text."""
        request = AnalysisRequest(
            text=text,
            include_context=False,
            include_suggestions=False,
            include_tags=True,
            max_matches=10
        )
        
        result = self.analyzer.analyze(request)
        return result.tags
    
    def generate_summary(self, text: str) -> Optional[str]:
        """Generate error summary from text."""
        request = AnalysisRequest(
            text=text,
            include_context=False,
            include_suggestions=True,
            include_tags=False,
            max_matches=1
        )
        
        result = self.analyzer.analyze(request)
        return result.summary
    
    def quick_analyze(self, text: str, language: Optional[str] = None) -> Optional[str]:
        """Quick analysis for simple use cases."""
        return self.analyzer.quick_analyze(text, language)


# Legacy compatibility: maintain the old class structure for imports
class ErrorAnalysis:
    """Legacy compatibility class."""
    
    def __init__(self):
        self.processor = LogProcessor()
    
    def analyze_error(self, text: str) -> str:
        """Analyze error and return simple string result."""
        result = self.processor.quick_analyze(text)
        return result or "No specific error patterns detected."