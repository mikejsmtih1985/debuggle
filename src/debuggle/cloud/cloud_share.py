"""
🔗 CLOUD SHARING MANAGER - Turn Errors into Shareable Links! 🌐📤

Think of this like turning your homework into a Google Drive share link:
- BEFORE: "Here's a screenshot of my error" (hard to help with)
- AFTER: "Check out my error analysis: debuggle.cloud/share/abc123" (full context!)

🏗️ HIGH SCHOOL EXPLANATION:
Imagine you're stuck on a math problem and want help from your study group:

OLD WAY (painful):
1. Take a photo of your work with phone (blurry, missing context)
2. Text the photo to friends (they can't see the full problem)
3. Try to explain over text what you were trying to do
4. Friends give generic advice because they can't see everything

NEW WAY (with Debuggle Cloud Sharing):
1. Upload your error log to Debuggle Cloud (2 seconds)
2. Get a shareable link like "debuggle.cloud/share/abc123"
3. Send link to friends/colleagues/Stack Overflow
4. Everyone sees the SAME detailed analysis you see
5. They can give specific, actionable advice!

🎯 WHAT THIS CLASS DOES:
- Creates unique, secure links for sharing error analyses
- Tracks who views shared links (for viral growth metrics)
- Provides different sharing modes (anonymous, temporary, public)
- Hooks into Pro/Enterprise features for advanced sharing
- Generates viral calls-to-action to grow Debuggle usage

🔒 PRIVACY & SECURITY:
- Links expire automatically (24 hours for free tier)
- Only the specific error log is shared (not your whole system)
- No personal information exposed unless you choose to include it
- Option to create anonymous shares (no attribution)

This makes getting help with errors as easy as sharing a Google Doc!
"""

import os
import json
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)

@dataclass
class ShareMetrics:
    """
    📊 Metrics for tracking shared error logs (viral growth data).
    
    Think of this like YouTube video stats:
    - How many people viewed your shared error
    - Where the views came from (Twitter, Slack, email, etc.)
    - How many people clicked "Try Debuggle" after seeing it
    - Which shares lead to the most conversions
    """
    share_id: str
    views: int = 0
    unique_viewers: int = 0
    referrer_sources: Optional[Dict[str, int]] = None  # {"twitter": 5, "slack": 12}
    conversion_clicks: int = 0  # People who clicked "Try Debuggle"
    created_at: Optional[datetime] = None
    last_viewed: Optional[datetime] = None
    viral_score: float = 0.0  # Calculated viral potential (0-10)
    
    def __post_init__(self):
        if self.referrer_sources is None:
            self.referrer_sources = {}
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ShareTemplate:
    """
    📝 Template for how shared error logs are displayed.
    
    Like choosing a template for your Google Slides presentation:
    - Clean, professional layout
    - Clear call-to-action buttons
    - Viral sharing hooks
    - Mobile-friendly design
    """
    template_id: str
    title_format: str  # "🔍 {user} needs help with a {language} error"
    description_format: str
    cta_text: str  # "Try Debuggle for your errors"
    social_tags: List[str]  # For Twitter/LinkedIn sharing
    include_branding: bool = True
    anonymous_mode: bool = False

class CloudShareManager:
    """
    🔗 The main class that manages sharing error logs publicly.
    
    HIGH SCHOOL ANALOGY:
    This is like having a smart assistant that helps you share your homework:
    
    1. You finish analyzing an error with Debuggle
    2. You say "I want to share this with my team"
    3. Assistant creates a beautiful share page with your analysis
    4. Assistant gives you a link to send to anyone
    5. When people click the link, they see everything you saw
    6. Assistant tracks who viewed it and provides analytics
    7. Assistant subtly encourages viewers to try Debuggle themselves
    
    The result: Getting help becomes viral growth for Debuggle!
    """
    
    def __init__(self, 
                 base_url: str = "https://debuggle.cloud",
                 tier: str = "free",
                 analytics_enabled: bool = True):
        """
        🏗️ Initialize the sharing system.
        
        Like setting up your social media profile:
        - Where should shared links point to?
        - What features are available for your tier?
        - Should we track analytics for viral growth?
        """
        self.base_url = base_url
        self.tier = tier
        self.analytics_enabled = analytics_enabled
        
        # Sharing limits by tier (like social media post limits)
        self.sharing_limits = {
            "free": {
                "max_active_shares": 10,      # Max 10 active shared links
                "expiration_hours": 24,       # Links expire after 24 hours
                "analytics_retention_days": 7, # Keep view stats for 7 days
                "custom_templates": False,    # No custom share templates
                "remove_branding": False      # Debuggle branding stays
            },
            "pro": {
                "max_active_shares": 100,     # 10x more sharing capacity
                "expiration_hours": 24 * 30,  # 30-day link expiration
                "analytics_retention_days": 90,
                "custom_templates": True,     # Design your own share pages
                "remove_branding": True       # Clean, professional look
            },
            "enterprise": {
                "max_active_shares": -1,      # Unlimited
                "expiration_hours": 24 * 365, # 1-year expiration
                "analytics_retention_days": 365,
                "custom_templates": True,
                "remove_branding": True,
                "custom_domain": True         # Use your own domain
            }
        }
        
        # Default share templates
        self.default_templates = {
            "professional": ShareTemplate(
                template_id="professional",
                title_format="🔍 Error Analysis: {error_type} in {language}",
                description_format="Detailed analysis and solution suggestions",
                cta_text="Analyze your own errors with Debuggle",
                social_tags=["debugging", "programming", "erroranalysis"],
                include_branding=True,
                anonymous_mode=False
            ),
            "help_request": ShareTemplate(
                template_id="help_request", 
                title_format="🆘 Need help with {error_type}",
                description_format="Can anyone help me understand this error?",
                cta_text="Get instant error analysis",
                social_tags=["help", "programming", "debugging"],
                include_branding=True,
                anonymous_mode=True
            ),
            "showcase": ShareTemplate(
                template_id="showcase",
                title_format="✨ How I debugged this {error_type}",
                description_format="Complete error analysis and solution walkthrough",
                cta_text="Try this powerful debugging tool",
                social_tags=["tutorial", "debugging", "programming"],
                include_branding=True,
                anonymous_mode=False
            )
        }
        
        # Initialize metrics storage (would be database in production)
        self.share_metrics: Dict[str, ShareMetrics] = {}
        
        logger.info(f"🔗 Cloud sharing initialized for {tier} tier")
    
    async def create_share_link(self, 
                               log_id: str,
                               content: str,
                               analysis: Dict[str, Any],
                               template_id: str = "professional",
                               custom_title: str = "",
                               anonymous: bool = False) -> Optional[str]:
        """
        🔗 Create a shareable link for an error analysis.
        
        HIGH SCHOOL EXPLANATION:
        This is like creating a Google Drive share link for your homework:
        1. You have a completed assignment (your error analysis)
        2. You want to share it with classmates for feedback
        3. This creates a public link anyone can click
        4. When they click, they see your work formatted nicely
        5. At the bottom, there's a note "Try Google Docs yourself!"
        
        Args:
            log_id: Unique ID of the error log
            content: The original error message/log
            analysis: Debuggle's analysis results
            template_id: How to format the share page
            custom_title: Custom title for the share
            anonymous: Hide attribution info
        
        Returns:
            Share URL like "https://debuggle.cloud/share/abc123def456"
        """
        try:
            # Check sharing limits for current tier
            if not await self._check_sharing_limits():
                logger.warning("🚫 Sharing limit exceeded for current tier")
                return None
            
            # Generate unique share ID
            share_id = self._generate_share_id(log_id, content)
            
            # Get template for formatting
            template = self.default_templates.get(template_id, self.default_templates["professional"])
            
            # Create share metadata
            share_data = {
                "share_id": share_id,
                "log_id": log_id,
                "content": content,
                "analysis": analysis,
                "template": asdict(template),
                "custom_title": custom_title,
                "anonymous": anonymous,
                "created_at": datetime.now().isoformat(),
                "expires_at": self._calculate_expiration().isoformat(),
                "tier": self.tier
            }
            
            # Store share data (would be database in production)
            await self._store_share_data(share_id, share_data)
            
            # Initialize metrics tracking
            if self.analytics_enabled:
                self.share_metrics[share_id] = ShareMetrics(share_id=share_id)
            
            # Generate the public URL
            share_url = f"{self.base_url}/share/{share_id}"
            
            logger.info(f"✅ Created share link: {share_url}")
            return share_url
            
        except Exception as e:
            logger.error(f"Error creating share link: {e}")
            return None
    
    async def get_share_data(self, share_id: str, 
                            referrer: str = "", 
                            user_agent: str = "") -> Optional[Dict[str, Any]]:
        """
        📥 Retrieve shared error data and track analytics.
        
        HIGH SCHOOL EXPLANATION:
        This is like someone clicking on your Google Drive share link:
        1. They click the link you sent them
        2. Google Drive shows them your document
        3. Google tracks that someone viewed it (analytics)
        4. At the bottom, there's a "Try Google Drive" button
        
        This does the same thing but for error analysis!
        
        Args:
            share_id: The unique ID from the share URL
            referrer: Where the click came from ("twitter", "slack", etc.)
            user_agent: Browser/device info for analytics
        
        Returns:
            Dictionary with error analysis and share page data
        """
        try:
            # Get stored share data
            share_data = await self._get_share_data(share_id)
            
            if not share_data:
                logger.warning(f"Share not found: {share_id}")
                return None
            
            # Check if expired
            expires_at = datetime.fromisoformat(share_data["expires_at"])
            if datetime.now() > expires_at:
                logger.warning(f"Share expired: {share_id}")
                return None
            
            # Track analytics (viral growth metrics)
            if self.analytics_enabled:
                await self._track_view(share_id, referrer, user_agent)
            
            # Add viral call-to-action based on tier
            viral_cta = self._generate_viral_cta(share_data)
            share_data["viral_cta"] = viral_cta
            
            # Add conversion tracking URLs
            share_data["conversion_urls"] = {
                "try_debuggle": f"{self.base_url}/download?ref=share_{share_id}",
                "upgrade_pro": f"{self.base_url}/pro?ref=share_{share_id}",
                "learn_more": f"{self.base_url}/features?ref=share_{share_id}"
            }
            
            logger.info(f"📊 Served share: {share_id} (referrer: {referrer})")
            return share_data
            
        except Exception as e:
            logger.error(f"Error getting share data {share_id}: {e}")
            return None
    
    async def get_share_analytics(self, share_id: str) -> Optional[ShareMetrics]:
        """
        📊 Get analytics for a shared error log.
        
        Like checking the view count on your YouTube video:
        - How many people saw your shared error?
        - Where did the traffic come from?
        - How many clicked "Try Debuggle"?
        """
        if not self.analytics_enabled:
            return None
        
        return self.share_metrics.get(share_id)
    
    async def get_user_share_stats(self, user_id: str = "anonymous") -> Dict[str, Any]:
        """
        📈 Get overall sharing statistics for a user.
        
        Like your social media analytics dashboard:
        - Total shares created
        - Total views across all shares
        - Most popular shared error type
        - Viral score (potential for organic growth)
        """
        try:
            # Calculate aggregate stats across all user's shares
            stats = {
                "total_shares": 0,
                "total_views": 0,
                "total_conversions": 0,
                "most_viral_share": None,
                "top_referrers": {},
                "viral_potential_score": 0.0
            }
            
            # In production, this would query a database
            for metrics in self.share_metrics.values():
                stats["total_shares"] += 1
                stats["total_views"] += metrics.views
                stats["total_conversions"] += metrics.conversion_clicks
                
                # Track referrer sources
                if metrics.referrer_sources:
                    for source, count in metrics.referrer_sources.items():
                        stats["top_referrers"][source] = stats["top_referrers"].get(source, 0) + count
                
                # Find most viral share
                if not stats["most_viral_share"] or metrics.viral_score > stats["most_viral_share"]["score"]:
                    stats["most_viral_share"] = {
                        "share_id": metrics.share_id,
                        "score": metrics.viral_score,
                        "views": metrics.views
                    }
            
            # Calculate overall viral potential
            if stats["total_shares"] > 0:
                stats["viral_potential_score"] = min(10.0, stats["total_views"] / stats["total_shares"])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user share stats: {e}")
            return {}
    
    # Private helper methods
    
    def _generate_share_id(self, log_id: str, content: str) -> str:
        """Generate a unique, secure share ID."""
        # Combine log_id, content snippet, and timestamp for uniqueness
        timestamp = datetime.now().isoformat()
        hash_input = f"{log_id}{content[:50]}{timestamp}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()[:16]  # 16-char ID
    
    def _calculate_expiration(self) -> datetime:
        """Calculate when this share should expire based on tier."""
        hours = self.sharing_limits[self.tier]["expiration_hours"]
        return datetime.now() + timedelta(hours=hours)
    
    async def _check_sharing_limits(self) -> bool:
        """Check if user has exceeded sharing limits for their tier."""
        max_shares = self.sharing_limits[self.tier]["max_active_shares"]
        if max_shares == -1:  # Unlimited
            return True
        
        # Count active shares (would query database in production)
        active_shares = len(self.share_metrics)
        return active_shares < max_shares
    
    async def _store_share_data(self, share_id: str, data: Dict[str, Any]):
        """Store share data (would use database in production)."""
        # For now, just log that we would store it
        logger.info(f"📁 Would store share data: {share_id}")
    
    async def _get_share_data(self, share_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve share data (would query database in production)."""
        # For now, return None (would implement actual storage)
        return None
    
    async def _track_view(self, share_id: str, referrer: str, user_agent: str):
        """Track a view for analytics and viral growth metrics."""
        if share_id not in self.share_metrics:
            return
        
        metrics = self.share_metrics[share_id]
        metrics.views += 1
        metrics.last_viewed = datetime.now()
        
        # Track referrer source for viral analysis
        if referrer:
            # Extract source from referrer URL
            source = self._extract_referrer_source(referrer)
            if metrics.referrer_sources is None:
                metrics.referrer_sources = {}
            metrics.referrer_sources[source] = metrics.referrer_sources.get(source, 0) + 1
        
        # Calculate viral score (0-10 based on engagement)
        referrer_count = len(metrics.referrer_sources) if metrics.referrer_sources else 0
        metrics.viral_score = min(10.0, metrics.views * 0.1 + referrer_count * 0.5)
        
        logger.info(f"📊 Tracked view for {share_id}: {metrics.views} total views")
    
    def _extract_referrer_source(self, referrer: str) -> str:
        """Extract the source platform from a referrer URL."""
        referrer_lower = referrer.lower()
        
        if "twitter.com" in referrer_lower or "t.co" in referrer_lower:
            return "twitter"
        elif "linkedin.com" in referrer_lower:
            return "linkedin"
        elif "slack.com" in referrer_lower:
            return "slack"
        elif "github.com" in referrer_lower:
            return "github"
        elif "stackoverflow.com" in referrer_lower:
            return "stackoverflow"
        elif "reddit.com" in referrer_lower:
            return "reddit"
        else:
            return "direct"
    
    def _generate_viral_cta(self, share_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate viral call-to-action based on the shared content."""
        error_type = share_data.get("analysis", {}).get("error_type", "error")
        language = share_data.get("analysis", {}).get("language", "code")
        
        return {
            "primary": f"🚀 Get instant {language} error analysis like this",
            "secondary": f"Debuggle helped solve this {error_type} in seconds",
            "button_text": "Try Debuggle Free",
            "social_text": f"Just used Debuggle to debug a {error_type} - amazing tool! 🔍",
            "hashtags": f"#debugging #{language} #programming #debuggle"
        }

# Export the main class
__all__ = ['CloudShareManager', 'ShareMetrics', 'ShareTemplate']