"""
Debuggle Core - Init module
"""

from .main import app
from .config_v2 import get_settings
from .core.processor import LogProcessor

# Initialize settings
settings = get_settings()

__version__ = "1.0.0"
__all__ = ["app", "settings", "LogProcessor"]