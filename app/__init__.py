"""
Debuggle Core - Init module
"""

from .main import app
from .config import settings
from .processor import LogProcessor

__version__ = "1.0.0"
__all__ = ["app", "settings", "LogProcessor"]