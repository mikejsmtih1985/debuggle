"""
🎯 DEBUGGLE TIER MANAGEMENT SYSTEM

This is like having different membership levels at a gym! 🏋️‍♂️
- FREE: Basic gym access (core debugging)
- PRO: Premium equipment (cloud sharing, advanced analytics)  
- ENTERPRISE: Personal trainer + VIP lounge (team features, SSO)

🏫 HIGH SCHOOL EXPLANATION:
Think of this like different Netflix plans:
- Basic: Watch on one device, standard quality
- Standard: Watch on 2 devices, HD quality
- Premium: Watch on 4 devices, 4K quality, multiple profiles

Same Netflix, different features unlocked based on what you pay for!
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import os
import logging

logger = logging.getLogger(__name__)

class DebuggleTier(str, Enum):
    """
    🎭 THE MEMBERSHIP LEVELS
    
    Like different levels of club membership - each level gets
    more perks and privileges!
    """
    FREE = "free"           # 🆓 Basic debugging, local only
    PRO = "pro"             # 💰 Cloud sharing, advanced features  
    ENTERPRISE = "enterprise"  # 🏢 Team management, SSO, custom features

@dataclass
class TierFeatures:
    """
    📋 FEATURE CHECKLIST FOR EACH TIER
    
    Like a menu at a restaurant - shows what comes with each meal plan!
    Each tier includes everything from lower tiers PLUS new features.
    """
    
    # Core features (available to everyone)
    basic_error_analysis: bool = True
    local_search: bool = True
    syntax_highlighting: bool = True
    error_explanations: bool = True
    
    # PRO features 
    cloud_sharing: bool = False
    advanced_analytics: bool = False
    priority_support: bool = False
    unlimited_storage: bool = False
    custom_dashboards: bool = False
    api_access: bool = False
    
    # ENTERPRISE features
    team_management: bool = False
    sso_integration: bool = False
    audit_logs: bool = False
    custom_branding: bool = False
    dedicated_support: bool = False
    on_premise_deployment: bool = False
    compliance_reports: bool = False
    advanced_integrations: bool = False

class TierManager:
    """
    🎛️ THE FEATURE TOGGLE CONTROL PANEL
    
    This is like the control room of a theme park! 🎢
    It decides which rides (features) each visitor (user) can access
    based on their ticket type (tier).
    
    🎓 EDUCATIONAL ANALOGY:
    Think of this like a school's access control system:
    - Students: Can access classrooms, cafeteria, library
    - Teachers: All student access + teacher's lounge, grade systems
    - Admin: All access + sensitive areas, system controls
    """
    
    def __init__(self, tier: Optional[str] = None):
        """
        Initialize the tier manager with current settings.
        
        Args:
            tier: Optional tier override. If not provided, detects from environment.
        """
        self._current_tier = self._detect_tier(tier)
        self._features = self._get_tier_features(self._current_tier)
        logger.info(f"🎯 Tier Manager initialized: {self._current_tier.upper()} tier active")
    
    def _detect_tier(self, tier_override: Optional[str] = None) -> DebuggleTier:
        """
        🕵️ DETECT CURRENT TIER FROM ENVIRONMENT
        
        Like checking someone's membership card at the gym entrance.
        We look for environment variables or license keys to determine
        what features this installation should have access to.
        
        Args:
            tier_override: Optional tier to use instead of environment detection
        """
        # Use override if provided, otherwise check environment variable
        if tier_override:
            tier_env = tier_override.lower()
        else:
            tier_env = os.getenv('DEBUGGLE_TIER', 'free').lower()
        
        # Validate against known tiers
        try:
            return DebuggleTier(tier_env)
        except ValueError:
            logger.warning(f"⚠️ Invalid tier '{tier_env}' specified, defaulting to FREE")
            return DebuggleTier.FREE
    
    def _get_tier_features(self, tier: DebuggleTier) -> TierFeatures:
        """
        🎁 BUILD FEATURE SET FOR TIER
        
        Like assembling a care package - start with basic items,
        then add premium items based on membership level.
        """
        features = TierFeatures()  # Start with FREE features
        
        if tier in [DebuggleTier.PRO, DebuggleTier.ENTERPRISE]:
            # Add PRO features
            features.cloud_sharing = True
            features.advanced_analytics = True
            features.priority_support = True
            features.unlimited_storage = True
            features.custom_dashboards = True
            features.api_access = True
        
        if tier == DebuggleTier.ENTERPRISE:
            # Add ENTERPRISE features
            features.team_management = True
            features.sso_integration = True
            features.audit_logs = True
            features.custom_branding = True
            features.dedicated_support = True
            features.on_premise_deployment = True
            features.compliance_reports = True
            features.advanced_integrations = True
        
        return features
    
    @property
    def current_tier(self) -> DebuggleTier:
        """Get the current active tier."""
        return self._current_tier
    
    @property 
    def features(self) -> TierFeatures:
        """Get the feature set for current tier."""
        return self._features
    
    def has_feature(self, feature_name: str) -> bool:
        """
        ✅ CHECK IF FEATURE IS ENABLED
        
        Like checking if your gym membership includes pool access.
        Returns True if the current tier includes this feature.
        """
        return getattr(self._features, feature_name, False)
    
    def require_feature(self, feature_name: str, error_message: Optional[str] = None) -> None:
        """
        🚫 ENFORCE FEATURE REQUIREMENT
        
        Like a bouncer at a VIP section - throws an error if you
        don't have the right membership level to access this feature.
        """
        if not self.has_feature(feature_name):
            if not error_message:
                error_message = f"Feature '{feature_name}' requires {DebuggleTier.PRO.upper()} tier or higher"
            raise FeatureNotAvailableError(error_message)
    
    def get_tier_info(self) -> Dict[str, Any]:
        """
        📊 GET COMPLETE TIER INFORMATION
        
        Like getting a detailed membership benefits summary.
        Useful for displaying to users what they have access to.
        """
        return {
            "current_tier": self._current_tier.value,
            "tier_display_name": self._current_tier.value.title(),
            "features_enabled": {
                name: getattr(self._features, name)
                for name in dir(self._features)
                if not name.startswith('_')
            },
            "can_upgrade": self._current_tier != DebuggleTier.ENTERPRISE
        }
    
    def get_upgrade_benefits(self) -> Dict[str, List[str]]:
        """
        🎁 SHOW UPGRADE BENEFITS
        
        Like showing what you get if you upgrade your Netflix plan.
        Helps users understand the value of upgrading.
        """
        current_features = set(name for name in dir(self._features) 
                             if not name.startswith('_') and getattr(self._features, name))
        
        benefits = {}
        
        if self._current_tier == DebuggleTier.FREE:
            pro_features = self._get_tier_features(DebuggleTier.PRO)
            benefits["PRO"] = [
                name.replace('_', ' ').title() 
                for name in dir(pro_features)
                if not name.startswith('_') 
                and getattr(pro_features, name)
                and name not in current_features
            ]
            
        if self._current_tier in [DebuggleTier.FREE, DebuggleTier.PRO]:
            enterprise_features = self._get_tier_features(DebuggleTier.ENTERPRISE)
            benefits["ENTERPRISE"] = [
                name.replace('_', ' ').title()
                for name in dir(enterprise_features) 
                if not name.startswith('_')
                and getattr(enterprise_features, name)
                and name not in current_features
            ]
            
        return benefits

class FeatureNotAvailableError(Exception):
    """
    🚫 FEATURE ACCESS DENIED ERROR
    
    Raised when code tries to use a feature that's not available
    in the current tier. Like trying to use the VIP lounge with
    a basic membership card.
    """
    pass

# Global tier manager instance
# Like having one master key card reader for the whole building
_tier_manager: Optional[TierManager] = None

def get_tier_manager() -> TierManager:
    """
    🎯 GET THE GLOBAL TIER MANAGER
    
    Like getting the main security system for the building.
    Creates one if it doesn't exist (singleton pattern).
    """
    global _tier_manager
    if _tier_manager is None:
        _tier_manager = TierManager()
    return _tier_manager

def has_feature(feature_name: str) -> bool:
    """🔍 Quick check if a feature is enabled."""
    return get_tier_manager().has_feature(feature_name)

def require_feature(feature_name: str, error_message: Optional[str] = None) -> None:
    """🚫 Require a feature or throw an error."""
    get_tier_manager().require_feature(feature_name, error_message)

def get_current_tier() -> DebuggleTier:
    """📊 Get the current active tier."""
    return get_tier_manager().current_tier

# Convenience functions for common checks
def is_free_tier() -> bool:
    """Check if running on FREE tier."""
    return get_current_tier() == DebuggleTier.FREE

def is_pro_tier() -> bool:
    """Check if running on PRO tier or higher."""
    return get_current_tier() in [DebuggleTier.PRO, DebuggleTier.ENTERPRISE]

def is_enterprise_tier() -> bool:
    """Check if running on ENTERPRISE tier."""
    return get_current_tier() == DebuggleTier.ENTERPRISE