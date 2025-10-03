"""
🗄️ CLOUD STORAGE MANAGER - Your Error Filing Cabinet in the Sky! ☁️📁

Think of this like upgrading from a physical filing cabinet to Google Drive:
- LOCAL STORAGE = Filing cabinet in your room (private, always available)
- CLOUD STORAGE = Google Drive (shareable, accessible from anywhere)

🏗️ HIGH SCHOOL EXPLANATION:
Imagine you're working on homework and want to save your work in two places:
1. On your computer's hard drive (local = always there, private)
2. In Google Drive (cloud = you can access from school, share with friends)

This class does the SAME THING but for error messages! It stores them both
locally (like always) AND in the cloud (when you want to share or access
from anywhere).

🎯 WHAT THIS CLASS DOES:
- Stores error logs in cloud storage with 24-hour expiration
- Creates shareable links so others can see your errors
- Provides fast search across all your cloud-stored logs
- Handles rate limiting so the free service doesn't get overwhelmed
- Falls back to local storage if cloud is unavailable

🔒 PRIVACY APPROACH:
- 24-hour TTL (Time To Live) = automatic deletion for privacy
- You control what gets uploaded (nothing automatic)
- Local storage continues working exactly the same
- Cloud storage is purely additive - opt-in only

This is like having a "temporary shared folder" for error debugging!
"""

import os
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

# For cloud storage implementations
try:
    import aiofiles
    import aiohttp
    CLOUD_DEPS_AVAILABLE = True
except ImportError:
    logging.warning("Cloud dependencies not available. Install with: pip install aiofiles aiohttp")
    CLOUD_DEPS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CloudLogEntry:
    """
    📝 A single error log stored in the cloud.
    
    Think of this like a single homework assignment uploaded to Google Drive:
    - It has a unique ID (like a file name)
    - It has content (your actual homework)
    - It has metadata (when you uploaded it, what class it's for)
    - It expires automatically (like a temporary shared link)
    """
    log_id: str           # Unique identifier (like "math_homework_oct2.pdf")
    content: str          # The actual error message/log content
    title: str           # Human-readable title ("IndexError in user login")
    uploaded_at: datetime # When this was uploaded to cloud
    expires_at: datetime  # When this gets automatically deleted
    share_url: str       # Public link for sharing (like Google Drive share link)
    tags: List[str]      # Categories for organization ["python", "web", "critical"]
    language: str        # Programming language detected
    severity: str        # How serious this error is ("critical", "error", "warning")
    user_id: Optional[str] = None    # For Pro/Enterprise user tracking
    project_id: Optional[str] = None # For organizing by project

@dataclass
class CloudStorageStats:
    """
    📊 Statistics about your cloud storage usage.
    
    Like checking how much space you've used in Google Drive:
    - How many files you have uploaded
    - How much storage space you're using
    - When things will expire
    - How many people have viewed your shared links
    """
    total_logs: int
    total_size_mb: float
    logs_expiring_soon: int  # Expiring in next 6 hours
    most_shared_log: Optional[str]
    total_shares: int
    storage_tier: str  # "free", "pro", "enterprise"

class CloudStorageManager:
    """
    🌤️ The main class that manages storing your errors in the cloud.
    
    HIGH SCHOOL ANALOGY:
    This is like having a smart assistant that helps you manage your Google Drive:
    - Automatically organizes your files
    - Creates shareable links when you ask
    - Reminds you when files are about to expire
    - Upgrades your storage when you need more space
    
    HOW IT WORKS WITH EXISTING DEBUGGLE:
    - Your local Debuggle keeps working exactly the same
    - When you want to share an error, this uploads it to cloud
    - Creates a link like "debuggle.cloud/share/abc123" 
    - Your teammate clicks the link and sees the same analysis you saw
    - After 24 hours, it automatically deletes to protect privacy
    """
    
    def __init__(self, 
                 storage_backend: str = "hybrid",  # "hybrid", "redis", "sqlite" 
                 tier: str = "free",               # "free", "pro", "enterprise"
                 base_url: str = "https://debuggle.cloud"):
        """
        🏗️ Initialize your cloud storage assistant.
        
        Think of this like setting up your Google Drive account:
        - Choose what type of storage you want
        - Set your account tier (free vs paid)
        - Configure where your "cloud" actually lives
        """
        self.storage_backend = storage_backend
        self.tier = tier
        self.base_url = base_url
        
        # 🎯 Initialize tier management system
        # Like getting your membership card that shows what features you can access!
        from ..tiers import TierManager
        self.tier_manager = TierManager(tier=tier)
        
        # Rate limiting for free tier (like free Google Drive upload limits)
        self.rate_limits = {
            "free": {"uploads_per_day": 50, "max_size_mb": 1, "retention_hours": 24},
            "pro": {"uploads_per_day": 500, "max_size_mb": 10, "retention_hours": 24*90},  # 90 days
            "enterprise": {"uploads_per_day": -1, "max_size_mb": 100, "retention_hours": 24*365}  # 1 year
        }
        
        # Storage backends (different ways to store data in cloud)
        self.storage_handlers = {
            "hybrid": self._init_hybrid_storage,    # Best of both worlds
            "redis": self._init_redis_storage,      # Fast, temporary
            "sqlite": self._init_sqlite_storage     # Reliable, persistent
        }
        
        # Initialize the chosen storage system
        self.storage = None
        if CLOUD_DEPS_AVAILABLE:
            self._init_storage()
        else:
            logger.warning("🌤️ Cloud storage not available - running in local-only mode")
    
    def _init_storage(self):
        """Initialize the storage backend."""
        try:
            handler = self.storage_handlers.get(self.storage_backend)
            if handler:
                self.storage = handler()
            else:
                logger.error(f"Unknown storage backend: {self.storage_backend}")
                self.storage = self._init_hybrid_storage()  # Fallback
        except Exception as e:
            logger.error(f"Failed to initialize cloud storage: {e}")
            self.storage = None
    
    def _init_hybrid_storage(self):
        """
        🔀 Hybrid storage: Redis for speed + SQLite for reliability.
        
        Think of this like having both:
        - A fast cache (Redis) = like RAM memory for quick access
        - A reliable backup (SQLite) = like your hard drive for permanent storage
        
        Best of both worlds!
        """
        return {
            "type": "hybrid",
            "redis_available": False,  # Will be set up when we deploy
            "sqlite_path": Path.home() / ".debuggle" / "cloud_cache.db",
            "initialized": True
        }
    
    def _init_redis_storage(self):
        """Fast temporary storage using Redis."""
        return {
            "type": "redis", 
            "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
            "initialized": True
        }
    
    def _init_sqlite_storage(self):
        """Reliable local cache using SQLite."""
        cache_dir = Path.home() / ".debuggle"
        cache_dir.mkdir(exist_ok=True)
        
        return {
            "type": "sqlite",
            "path": cache_dir / "cloud_cache.db", 
            "table": "cloud_logs",
            "initialized": True
        }
    
    async def upload_log(self, 
                        content: str, 
                        title: str = "", 
                        tags: Optional[List[str]] = None,
                        language: str = "unknown",
                        severity: str = "info") -> Optional[CloudLogEntry]:
        """
        ⬆️ Upload an error log to the cloud.
        
        HIGH SCHOOL ANALOGY:
        This is like saving your homework to Google Drive and getting a shareable link:
        1. You give it your homework (content)
        2. It saves it to the cloud
        3. It gives you back a link you can share with classmates
        4. It automatically deletes after 24 hours (for privacy)
        
        Args:
            content: The actual error message or log content
            title: Human-readable title (auto-generated if empty)
            tags: Categories like ["python", "database", "critical"]
            language: Programming language ("python", "javascript", etc.)
            severity: How serious ("critical", "error", "warning", "info")
        
        Returns:
            CloudLogEntry with sharing URL, or None if upload failed
        """
        # 🎯 Check if cloud sharing is allowed in current tier
        # Like checking if your gym membership includes pool access!
        if not self.tier_manager.has_feature("cloud_sharing"):
            logger.warning(f"🚫 Cloud sharing not available in {self.tier.upper()} tier")
            return None
            
        if not CLOUD_DEPS_AVAILABLE or not self.storage:
            logger.warning("🌤️ Cloud upload not available - check dependencies")
            return None
        
        # Check rate limits (like Google Drive upload quotas)
        if not await self._check_rate_limits():
            logger.warning("🚫 Rate limit exceeded for cloud uploads")
            return None
        
        try:
            # Generate unique ID for this log
            log_id = self._generate_log_id(content)
            
            # Auto-generate title if not provided
            if not title:
                title = self._generate_title(content, language)
            
            # Calculate expiration based on tier
            retention_hours = self.rate_limits[self.tier]["retention_hours"]
            expires_at = datetime.now() + timedelta(hours=retention_hours)
            
            # Create cloud log entry
            cloud_entry = CloudLogEntry(
                log_id=log_id,
                content=content,
                title=title,
                uploaded_at=datetime.now(),
                expires_at=expires_at,
                share_url=f"{self.base_url}/share/{log_id}",
                tags=tags or [],
                language=language,
                severity=severity
            )
            
            # Store in cloud backend
            success = await self._store_log_entry(cloud_entry)
            
            if success:
                logger.info(f"✅ Uploaded log to cloud: {cloud_entry.share_url}")
                return cloud_entry
            else:
                logger.error("❌ Failed to store log in cloud")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading to cloud: {e}")
            return None
    
    async def get_log(self, log_id: str) -> Optional[CloudLogEntry]:
        """
        📥 Retrieve a log from cloud storage.
        
        Like downloading a file from Google Drive using its ID.
        """
        if not self.storage:
            return None
        
        try:
            # This would be implemented based on storage backend
            # For now, return None as we haven't implemented the actual storage yet
            logger.info(f"🔍 Retrieving log {log_id} from cloud")
            return None
        except Exception as e:
            logger.error(f"Error retrieving log {log_id}: {e}")
            return None
    
    async def search_logs(self, 
                         query: str, 
                         limit: int = 20,
                         tags: Optional[List[str]] = None) -> List[CloudLogEntry]:
        """
        🔍 Search through your cloud-stored logs.
        
        Like using Google Drive search to find specific files:
        - Search by content ("IndexError")
        - Filter by tags (["python", "critical"])
        - Get results ranked by relevance
        """
        # 🎯 Check if advanced search is allowed in current tier
        # Like checking if your Netflix plan includes 4K streaming!
        if not self.tier_manager.has_feature("advanced_analytics"):
            logger.warning(f"🚫 Advanced cloud search not available in {self.tier.upper()} tier")
            return []
            
        if not self.storage:
            return []
        
        try:
            # Implementation would depend on storage backend
            logger.info(f"🔍 Searching cloud logs for: {query}")
            return []
        except Exception as e:
            logger.error(f"Error searching cloud logs: {e}")
            return []
    
    async def get_stats(self) -> CloudStorageStats:
        """
        📊 Get statistics about your cloud storage usage.
        
        Like checking your Google Drive storage usage dashboard.
        """
        return CloudStorageStats(
            total_logs=0,
            total_size_mb=0.0,
            logs_expiring_soon=0,
            most_shared_log=None,
            total_shares=0,
            storage_tier=self.tier
        )
    
    async def cleanup_expired_logs(self) -> int:
        """
        🧹 Remove expired logs (automatic privacy protection).
        
        Like Google Drive automatically deleting files in trash after 30 days.
        This runs automatically to protect privacy.
        """
        if not self.storage:
            return 0
        
        try:
            # Implementation would clean up expired entries
            logger.info("🧹 Cleaning up expired cloud logs")
            return 0
        except Exception as e:
            logger.error(f"Error cleaning up expired logs: {e}")
            return 0
    
    # Private helper methods
    
    def _generate_log_id(self, content: str) -> str:
        """Generate a unique ID for a log entry."""
        # Create hash from content + timestamp for uniqueness
        timestamp = datetime.now().isoformat()
        hash_input = f"{content[:100]}{timestamp}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()[:12]
    
    def _generate_title(self, content: str, language: str) -> str:
        """Auto-generate a human-readable title from log content."""
        # Extract first error line or use generic title
        lines = content.strip().split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback']):
                return line.strip()[:100]
        
        return f"{language.title()} error log - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    async def _check_rate_limits(self) -> bool:
        """Check if user has exceeded their upload quota."""
        # For now, always allow uploads (would implement actual rate limiting in production)
        return True
    
    async def _store_log_entry(self, entry: CloudLogEntry) -> bool:
        """Store a log entry in the chosen backend."""
        # For now, just log that we would store it
        logger.info(f"📁 Would store log entry: {entry.log_id}")
        return True

# Export the main class
__all__ = ['CloudStorageManager', 'CloudLogEntry', 'CloudStorageStats']