"""
Debuggle Core - Advanced error analysis and context extraction.

This package provides the core functionality for intelligent error analysis,
transforming cryptic stack traces into actionable insights.
"""

from .analyzer import ErrorAnalyzer
from .processor import LogProcessor
from .context import ContextExtractor
from .patterns import ErrorPatternMatcher

__all__ = [
    "ErrorAnalyzer",
    "LogProcessor", 
    "ContextExtractor",
    "ErrorPatternMatcher"
]