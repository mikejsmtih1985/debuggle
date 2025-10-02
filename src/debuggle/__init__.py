"""
Debuggle Core - Source package
"""

__version__ = "1.0.0"
__author__ = "Mike Smith"
__email__ = "mike@debuggle.com"

# Import core modules - use new modular structure
from .config_v2 import get_settings
from .core.processor import LogProcessor
from .core.context import ContextExtractor

# Initialize settings
settings = get_settings()

# Conditionally import FastAPI app (only when needed)
try:
    from .main import app
    __all__ = ["app", "settings", "LogProcessor", "ContextExtractor"]
except ImportError:
    # FastAPI not available, skip web app
    __all__ = ["settings", "LogProcessor", "ContextExtractor"]