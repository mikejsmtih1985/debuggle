#!/usr/bin/env python3
"""
🎯 DEBUGGLE TIER SYSTEM DEMO - See the Power of Feature Toggles! 

This demonstrates how Debuggle's new unified codebase works with different tiers:
- Same code, different features unlocked based on your subscription
- No need for separate branches or installations
- Clean, professional feature flagging system

🏫 HIGH SCHOOL EXPLANATION:
Think of this like having one Netflix app that shows different content based on your plan:
- Basic Plan: Standard shows
- Premium Plan: Same app + 4K movies + multiple screens  
- Enterprise Plan: Same app + advanced admin features

Run this script with different DEBUGGLE_TIER environment variables to see it in action!

USAGE:
    # Free tier (default)
    python examples/tier_demo.py
    
    # Pro tier  
    DEBUGGLE_TIER=pro python examples/tier_demo.py
    
    # Enterprise tier
    DEBUGGLE_TIER=enterprise python examples/tier_demo.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path so we can import debuggle modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from debuggle.tiers import TierManager, get_current_tier, has_feature, require_feature
from debuggle.config_v2 import get_settings

def print_banner(tier_name: str):
    """Print a fancy banner showing the current tier."""
    banners = {
        "FREE": """
╔═══════════════════════════════════════╗
║         🆓 DEBUGGLE FREE TIER         ║
║    Perfect for personal debugging!    ║
╚═══════════════════════════════════════╝
""",
        "PRO": """
╔═══════════════════════════════════════╗
║         💎 DEBUGGLE PRO TIER          ║
║   Cloud sharing + Advanced features   ║
╚═══════════════════════════════════════╝
""",
        "ENTERPRISE": """
╔═══════════════════════════════════════╗
║      🏢 DEBUGGLE ENTERPRISE TIER      ║
║  Team management + Custom features    ║
╚═══════════════════════════════════════╝
"""
    }
    print(banners.get(tier_name, banners["FREE"]))

async def demo_cloud_features():
    """Demonstrate cloud features with tier checking."""
    print("\n🌤️  CLOUD FEATURES DEMO")
    print("=" * 50)
    
    if has_feature("cloud_sharing"):
        print("✅ Cloud sharing: AVAILABLE")
        try:
            # Try to import and use cloud features  
            from debuggle.cloud import CloudStorageManager, CloudShareManager
            
            print("   📤 Initializing cloud storage...")
            settings = get_settings()
            cloud_storage = CloudStorageManager(tier=settings.tier)
            cloud_share = CloudShareManager(tier=settings.tier)
            
            print("   🔗 Creating demo share link...")
            # This would normally upload real data, but we'll just show the tier checking
            print("   ✨ Cloud features ready!")
            
        except Exception as e:
            print(f"   ⚠️  Cloud features not fully available: {e}")
    else:
        print("🚫 Cloud sharing: NOT AVAILABLE")
        print("   💡 Upgrade to PRO tier to unlock cloud sharing!")

def demo_analytics_features():
    """Demonstrate analytics features with tier checking.""" 
    print("\n📊 ANALYTICS FEATURES DEMO")
    print("=" * 50)
    
    if has_feature("advanced_analytics"):
        print("✅ Advanced analytics: AVAILABLE")
        print("   📈 Pattern recognition: ENABLED")
        print("   🔍 Advanced search: ENABLED") 
        print("   📋 Custom reports: ENABLED")
        print("   ⏰ Extended retention: ENABLED")
    else:
        print("🚫 Advanced analytics: NOT AVAILABLE")
        print("   💡 Upgrade to PRO tier to unlock advanced analytics!")

def demo_team_features():
    """Demonstrate team features with tier checking."""
    print("\n👥 TEAM FEATURES DEMO")
    print("=" * 50)
    
    if has_feature("team_management"):
        print("✅ Team management: AVAILABLE")
        print("   👤 User management: ENABLED")
        print("   🔐 SSO integration: ENABLED")
        print("   📊 Team analytics: ENABLED")
        print("   🎨 Custom branding: ENABLED")
    else:
        print("🚫 Team management: NOT AVAILABLE")  
        print("   💡 Upgrade to ENTERPRISE tier to unlock team features!")

def demo_core_features():
    """Demonstrate core features (always available)."""
    print("\n🛠️  CORE FEATURES DEMO")
    print("=" * 50)
    
    # These should work in all tiers
    print("✅ Error analysis: AVAILABLE")
    print("✅ Pattern matching: AVAILABLE") 
    print("✅ Solution suggestions: AVAILABLE")
    print("✅ Local storage: AVAILABLE")
    print("✅ CLI interface: AVAILABLE")
    print("✅ Web dashboard: AVAILABLE")

def demo_feature_protection():
    """Demonstrate how feature protection works."""
    print("\n🛡️  FEATURE PROTECTION DEMO")
    print("=" * 50)
    
    # Try to access a protected feature
    try:
        require_feature("team_management")
        print("✅ Team management access granted!")
    except Exception as e:
        print(f"🚫 Team management access denied: {e}")
        
    try:
        require_feature("cloud_sharing")
        print("✅ Cloud sharing access granted!")
    except Exception as e:
        print(f"🚫 Cloud sharing access denied: {e}")

def show_tier_comparison():
    """Show a comparison of what each tier includes."""
    print("\n📋 TIER COMPARISON")
    print("=" * 80)
    
    print("Feature                    │ Free │ Pro │ Enterprise")
    print("──────────────────────────│──────│─────│───────────")
    print("Error Analysis             │  ✅  │ ✅  │     ✅    ")
    print("Pattern Matching           │  ✅  │ ✅  │     ✅    ")
    print("Local Storage              │  ✅  │ ✅  │     ✅    ")
    print("Cloud Sharing              │  🚫  │ ✅  │     ✅    ")
    print("Advanced Analytics         │  🚫  │ ✅  │     ✅    ")
    print("Extended Retention         │  🚫  │ ✅  │     ✅    ")
    print("Team Management            │  🚫  │ 🚫  │     ✅    ")
    print("SSO Integration            │  🚫  │ 🚫  │     ✅    ")
    print("Custom Branding            │  🚫  │ 🚫  │     ✅    ")

async def main():
    """Run the tier demo."""
    # Get current tier information
    current_tier = get_current_tier()
    tier_manager = TierManager()
    
    # Show banner
    print_banner(current_tier.value.upper())
    
    # Show current configuration
    print(f"🎯 Current Tier: {current_tier.value.upper()}")
    print(f"🔧 Environment: {os.getenv('DEBUGGLE_TIER', 'free')}")
    print(f"📍 Detected from: {tier_manager._current_tier.value}")
    
    # Show tier comparison table
    show_tier_comparison()
    
    # Demo each feature category
    demo_core_features()
    await demo_cloud_features()
    demo_analytics_features()
    demo_team_features()
    demo_feature_protection()
    
    # Show upgrade message based on current tier
    if current_tier.value == "free":
        print("\n🚀 READY TO UPGRADE?")
        print("═══════════════════════")
        print("💎 Upgrade to PRO for cloud sharing and advanced analytics!")
        print("🏢 Upgrade to ENTERPRISE for team management and SSO!")
        print("📧 Contact: sales@debuggle.com")
    elif current_tier.value == "pro":
        print("\n🏢 WANT TEAM FEATURES?")
        print("═════════════════════")
        print("🚀 Upgrade to ENTERPRISE for team management and SSO!")
        print("📧 Contact: sales@debuggle.com")
    else:
        print("\n🎉 YOU HAVE FULL ACCESS!")
        print("══════════════════════")
        print("✨ All Debuggle features are unlocked!")
        print("🤝 Thanks for being an Enterprise customer!")

if __name__ == "__main__":
    print("🎯 Debuggle Tier System Demo")
    print("═" * 60)
    print("💡 Try running with different DEBUGGLE_TIER values:")
    print("   DEBUGGLE_TIER=free python examples/tier_demo.py")
    print("   DEBUGGLE_TIER=pro python examples/tier_demo.py") 
    print("   DEBUGGLE_TIER=enterprise python examples/tier_demo.py")
    print("═" * 60)
    
    asyncio.run(main())