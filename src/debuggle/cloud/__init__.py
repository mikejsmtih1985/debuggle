"""
🌤️ DEBUGGLE CLOUD MODULE - Your Errors in the Sky! ☁️

Think of this like upgrading from a personal diary to a shared online journal:
- Your LOCAL Debuggle = Private diary you keep in your room
- DEBUGGLE CLOUD = Online journal you can share with friends and teammates

🏗️ HIGH SCHOOL EXPLANATION:
Imagine you're working on a group project and everyone's getting different errors:
- Before: Everyone emails screenshots of errors back and forth (messy!)
- After: Upload errors to Debuggle Cloud, share a link, everyone sees the same analysis

This is like having a "Google Docs for error messages" - but way smarter because
it actually analyzes your errors and gives you solutions!

🎯 WHAT THIS MODULE DOES:
- Uploads your error logs to free cloud storage (24 hours)
- Creates shareable links so teammates can see your errors
- Provides fast cloud-based search across all your uploaded logs
- Hooks into Pro/Enterprise tiers for longer retention and advanced features

📚 MODULE STRUCTURE:
- cloud_storage.py: The "cloud filing cabinet" - stores and retrieves logs
- cloud_api.py: The "cloud reception desk" - handles web requests  
- cloud_share.py: The "link generator" - creates shareable error URLs
- cloud_deploy.py: The "cloud setup assistant" - deployment utilities

🔒 PRIVACY & SECURITY:
- 24-hour auto-delete keeps your data private
- Only you control what gets uploaded
- Local CLI mode still works exactly the same
- Cloud is 100% optional - use it when you want to share!

This extends Debuggle without changing anything you already love about it!
"""

# Export all the cloud components for easy importing
from .cloud_storage import CloudStorageManager
from .cloud_api import setup_cloud_routes
from .cloud_share import CloudShareManager
from .cloud_deploy import CloudDeploymentHelper

__all__ = [
    'CloudStorageManager',
    'setup_cloud_routes', 
    'CloudShareManager',
    'CloudDeploymentHelper'
]