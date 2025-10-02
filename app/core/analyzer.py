"""
Core error analysis engine.

This module provides the main error analysis functionality,
orchestrating pattern matching, context extraction, and response generation.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from .patterns import ErrorPatternMatcher, ErrorMatch, ErrorSeverity


logger = logging.getLogger(__name__)


@dataclass
class AnalysisRequest:
    """Request for error analysis."""
    text: str
    language: Optional[str] = None
    include_context: bool = True
    include_suggestions: bool = True
    include_tags: bool = True
    max_matches: int = 5


@dataclass
class AnalysisResult:
    """Result of error analysis."""
    original_text: str
    detected_language: Optional[str]
    primary_error: Optional[ErrorMatch]
    all_matches: List[ErrorMatch]
    tags: List[str]
    summary: Optional[str]
    suggestions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        """Whether any errors were detected."""
        return len(self.all_matches) > 0
    
    @property
    def severity_level(self) -> Optional[str]:
        """Get the highest severity level from all matches."""
        if not self.all_matches:
            return None
        
        severities = [match.pattern.severity.value for match in self.all_matches]
        severity_order = ["critical", "high", "medium", "low", "info"]
        
        for level in severity_order:
            if level in severities:
                return level
        
        return None


class ErrorAnalyzer:
    """
    Main error analysis engine.
    
    This class orchestrates the error analysis process, from pattern matching
    to generating human-readable explanations and suggestions.
    """
    
    def __init__(self):
        """Initialize the analyzer with pattern matcher."""
        self.pattern_matcher = ErrorPatternMatcher()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Perform comprehensive error analysis.
        
        Args:
            request: Analysis request with text and options
            
        Returns:
            Comprehensive analysis result
        """
        start_time = time.time()
        
        try:
            # Detect language if not provided
            detected_language = request.language
            if not detected_language or detected_language.lower() == 'auto':
                detected_language = self.pattern_matcher.detect_language(request.text)
                self.logger.debug(f"Detected language: {detected_language}")
            
            # Find error matches
            matches = self.pattern_matcher.find_matches(
                request.text, 
                detected_language
            )[:request.max_matches]
            
            # Get primary error (most severe/confident)
            primary_error = matches[0] if matches else None
            
            # Generate tags
            tags = []
            if request.include_tags:
                tags = self._generate_tags(matches, detected_language, request.text)
            
            # Generate summary
            summary = None
            if request.include_suggestions and primary_error:
                summary = self._generate_summary(primary_error, request.text)
            
            # Generate suggestions
            suggestions = []
            if request.include_suggestions and matches:
                suggestions = self._generate_suggestions(matches)
            
            # Build metadata
            processing_time = time.time() - start_time
            metadata = {
                'processing_time_ms': int(processing_time * 1000),
                'patterns_checked': len(self.pattern_matcher.all_patterns),
                'matches_found': len(matches),
                'language_detection_used': request.language is None or request.language.lower() == 'auto'
            }
            
            return AnalysisResult(
                original_text=request.text,
                detected_language=detected_language,
                primary_error=primary_error,
                all_matches=matches,
                tags=tags,
                summary=summary,
                suggestions=suggestions,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {e}", exc_info=True)
            # Return a basic result even if analysis fails
            return AnalysisResult(
                original_text=request.text,
                detected_language=detected_language,
                primary_error=None,
                all_matches=[],
                tags=["analysis-failed"],
                summary=f"Error analysis failed: {str(e)}",
                suggestions=["Please check the input format and try again"],
                metadata={'error': str(e), 'processing_time_ms': int((time.time() - start_time) * 1000)}
            )
    
    def _generate_tags(self, matches: List[ErrorMatch], language: Optional[str], text: str) -> List[str]:
        """Generate descriptive tags for the error analysis."""
        tags = set()
        
        # Add language tag
        if language:
            tags.add(f"{language.title()}")
        
        # Add error type tags
        for match in matches:
            tags.add(match.pattern.name)
            tags.add(match.pattern.category.value.title().replace("_", " "))
            
            if match.pattern.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                tags.add("Needs Immediate Attention")
            
        # Add contextual tags
        if "stack trace" in text.lower() or "traceback" in text.lower():
            tags.add("Stack Trace")
        
        if len(matches) > 1:
            tags.add("Multiple Errors")
        elif len(matches) == 1:
            tags.add("Single Error")
        else:
            tags.add("No Errors Detected")
        
        # Add severity tag
        if matches:
            severity_levels = [match.pattern.severity.value for match in matches]
            if "critical" in severity_levels:
                tags.add("Critical Issue")
            elif "high" in severity_levels:
                tags.add("High Priority")
            else:
                tags.add("Medium Priority")
        
        return sorted(list(tags))
    
    def _generate_summary(self, primary_error: ErrorMatch, original_text: str) -> str:
        """Generate a human-readable summary of the primary error."""
        pattern = primary_error.pattern
        
        summary_parts = [
            f"🚨 **{pattern.name} Detected**",
            "",
            f"🔍 **What happened:** {pattern.what_happened}",
            ""
        ]
        
        # Add context-specific information if available
        if primary_error.context:
            summary_parts.extend([
                f"📋 **Code context:**",
                f"```",
                primary_error.context,
                f"```",
                ""
            ])
        
        # Add quick fixes
        if pattern.quick_fixes:
            summary_parts.extend([
                "🛠️ **Quick fixes:**"
            ])
            for i, fix in enumerate(pattern.quick_fixes, 1):
                summary_parts.append(f"   {i}. {fix}")
            
            summary_parts.extend([
                "",
                f"💡 **Prevention tip:** {pattern.prevention_tip}",
                "",
                f"📚 **Learn more:** {pattern.learn_more_url}"
            ])
        
        return "\n".join(summary_parts)
    
    def _generate_suggestions(self, matches: List[ErrorMatch]) -> List[str]:
        """Generate actionable suggestions based on all matches."""
        suggestions = []
        
        if not matches:
            suggestions.append("No specific errors detected. Consider checking for:")
            suggestions.extend([
                "- Syntax errors or typos",
                "- Logic errors in your code flow",
                "- Environment or configuration issues"
            ])
            return suggestions
        
        # Add suggestions from each match
        for match in matches[:3]:  # Limit to top 3 matches
            pattern = match.pattern
            
            suggestions.append(f"For {pattern.name}:")
            for fix in pattern.quick_fixes[:2]:  # Limit to 2 fixes per error
                suggestions.append(f"  • {fix}")
        
        # Add general suggestions based on error categories
        categories = set(match.pattern.category for match in matches)
        
        if any(cat.value in ['syntax', 'runtime'] for cat in categories):
            suggestions.append("General debugging tips:")
            suggestions.extend([
                "  • Use a debugger to step through your code",
                "  • Add print statements to trace execution flow",
                "  • Check your IDE for syntax highlighting and warnings"
            ])
        
        return suggestions
    
    def quick_analyze(self, text: str, language: Optional[str] = None) -> Optional[str]:
        """
        Quick analysis for simple use cases.
        
        Args:
            text: Error text to analyze
            language: Optional language hint
            
        Returns:
            Simple string summary or None if no errors found
        """
        request = AnalysisRequest(
            text=text,
            language=language,
            include_context=False,
            include_suggestions=True,
            include_tags=False,
            max_matches=1
        )
        
        result = self.analyze(request)
        
        if result.primary_error:
            pattern = result.primary_error.pattern
            return f"{pattern.name}: {pattern.explanation}"
        
        return None