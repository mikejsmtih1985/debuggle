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

# Define available exports (app is imported on-demand)
__all__ = ["settings", "LogProcessor", "ContextExtractor"]

def get_app():
    """Get the FastAPI app instance (imported on-demand to avoid import issues)"""
    from .main import app
    return app