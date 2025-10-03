"""
Pytest plugin for graceful coverage handling.
Provides better error messages when coverage thresholds are not met.
"""

import pytest
from typing import Optional


class CoverageHandler:
    """Handle coverage failures gracefully with better messaging."""
    
    def __init__(self):
        self.coverage_data: Optional[dict] = None
    
    def handle_coverage_failure(self, required: float, actual: float, details: Optional[dict] = None):
        """Provide graceful handling when coverage fails below threshold."""
        
        gap = required - actual
        
        print(f"\n{'='*60}")
        print("🎯 COVERAGE THRESHOLD NOT MET")
        print("="*60)
        print(f"📊 Required Coverage: {required:.1f}%")
        print(f"📈 Current Coverage: {actual:.1f}%") 
        print(f"📉 Coverage Gap: {gap:.1f}%")
        
        if gap <= 5.0:
            print("✅ You're very close! Just a few more tests needed.")
            print("💡 Suggestion: Add tests for the missing lines shown above.")
        elif gap <= 15.0:
            print("⚠️  Moderate coverage gap. Consider adding comprehensive tests.")
            print("💡 Suggestion: Focus on testing core functionality first.")
        else:
            print("🚨 Large coverage gap. Significant testing effort needed.")
            print("💡 Suggestion: Start with high-impact modules (models, core logic).")
        
        print("\n🔧 Quick Coverage Boost Ideas:")
        print("• Add tests for data models and validation")
        print("• Test error handling and edge cases") 
        print("• Test configuration and settings")
        print("• Test utility functions and helpers")
        
        if details:
            print(f"\n📋 Module Coverage Summary:")
            for module, cov in details.items():
                if isinstance(cov, dict) and 'percent' in cov:
                    print(f"  {module}: {cov['percent']:.1f}%")
        
        print(f"\n{'='*60}")
        print("Remember: Good tests are better than just hitting numbers! 🎯")
        print("="*60)
        
        return False  # Still indicate failure, but with better messaging


def graceful_coverage_check(required_coverage: float, actual_coverage: float) -> bool:
    """
    Standalone function for graceful coverage checking.
    
    Args:
        required_coverage: The required coverage threshold (e.g., 80.0 for 80%)
        actual_coverage: The actual coverage achieved (e.g., 75.5 for 75.5%)
    
    Returns:
        bool: True if coverage meets threshold, False otherwise
    """
    handler = CoverageHandler()
    
    if actual_coverage >= required_coverage:
        print(f"✅ Coverage threshold met: {actual_coverage:.1f}% >= {required_coverage:.1f}%")
        return True
    else:
        return handler.handle_coverage_failure(required_coverage, actual_coverage)


# Export main functions
__all__ = ['graceful_coverage_check', 'CoverageHandler']