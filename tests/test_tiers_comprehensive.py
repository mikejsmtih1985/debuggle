"""
🎯 COMPREHENSIVE TIER SYSTEM COVERAGE TESTS

This test suite is designed to boost tiers.py coverage from 60% to 85%+ by testing:
- All tier detection scenarios and edge cases
- Feature availability checking and validation  
- Error handling for invalid tiers and configurations
- Integration with environment variables
- All helper functions and convenience methods
- Tier manager initialization and state management

These tests cover the previously untested branches and error paths.
"""

import pytest
import os
from unittest.mock import patch, Mock
from src.debuggle.core.tiers import (
    DebuggleTier, 
    TierFeatures, 
    TierManager, 
    get_current_tier, 
    has_feature, 
    require_feature,
    FeatureNotAvailableError
)


class TestDebuggleTierEnum:
    """Test the DebuggleTier enum and its properties"""
    
    def test_tier_enum_values(self):
        """Test that all tier enum values are correct"""
        assert DebuggleTier.FREE.value == "free"
        assert DebuggleTier.PRO.value == "pro" 
        assert DebuggleTier.ENTERPRISE.value == "enterprise"
    
    def test_tier_enum_comparison(self):
        """Test tier enum comparison operations"""
        assert DebuggleTier.FREE != DebuggleTier.PRO
        assert DebuggleTier.PRO != DebuggleTier.ENTERPRISE
        
        # Test string comparisons
        assert DebuggleTier.FREE == "free"
        assert DebuggleTier.PRO == "pro"
        assert DebuggleTier.ENTERPRISE == "enterprise"
    
    def test_tier_enum_iteration(self):
        """Test that we can iterate over all tiers"""
        all_tiers = list(DebuggleTier)
        assert len(all_tiers) == 3
        assert DebuggleTier.FREE in all_tiers
        assert DebuggleTier.PRO in all_tiers
        assert DebuggleTier.ENTERPRISE in all_tiers


class TestTierFeatures:
    """Test the TierFeatures dataclass"""
    
    def test_tier_features_creation(self):
        """Test creating TierFeatures instances"""
        features = TierFeatures(
            cloud_sharing=True,
            advanced_analytics=True,
            priority_support=True,
            team_management=False,
            sso_integration=False,
            custom_branding=False
        )
        
        assert features.cloud_sharing is True
        assert features.advanced_analytics is True
        assert features.team_management is False
    
    def test_tier_features_defaults(self):
        """Test TierFeatures default values"""
        features = TierFeatures()
        
        # Premium features should default to False
        assert features.cloud_sharing is False
        assert features.advanced_analytics is False
        assert features.priority_support is False
        assert features.team_management is False
        assert features.sso_integration is False
        assert features.custom_branding is False
        
        # Basic features should default to True
        assert features.basic_error_analysis is True
        assert features.local_search is True


class TestTierManager:
    """Test the TierManager class and its methods"""
    
    def test_tier_manager_initialization_default(self):
        """Test TierManager initialization with default settings"""
        with patch.dict(os.environ, {}, clear=True):
            # Clear any existing DEBUGGLE_TIER env var
            if 'DEBUGGLE_TIER' in os.environ:
                del os.environ['DEBUGGLE_TIER']
            
            manager = TierManager()
            assert manager._current_tier == DebuggleTier.FREE
    
    def test_tier_manager_initialization_with_env(self):
        """Test TierManager initialization with environment variable"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'pro'}):
            manager = TierManager()
            assert manager._current_tier == DebuggleTier.PRO
        
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'enterprise'}):
            manager = TierManager()
            assert manager._current_tier == DebuggleTier.ENTERPRISE
    
    def test_tier_manager_initialization_with_parameter(self):
        """Test TierManager initialization with tier parameter"""
        manager = TierManager(tier="pro")
        assert manager._current_tier == DebuggleTier.PRO
        
        manager = TierManager(tier="enterprise")
        assert manager._current_tier == DebuggleTier.ENTERPRISE
        
        manager = TierManager(tier="free")
        assert manager._current_tier == DebuggleTier.FREE
    
    def test_tier_manager_invalid_tier_handling(self):
        """Test TierManager handling of invalid tier values"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'invalid_tier'}):
            with patch('src.debuggle.tiers.logger') as mock_logger:
                manager = TierManager()
                # Should default to FREE and log warning
                assert manager._current_tier == DebuggleTier.FREE
                mock_logger.warning.assert_called_once()
    
    def test_tier_manager_case_insensitive(self):
        """Test that tier detection is case insensitive"""
        manager = TierManager(tier="PRO")
        assert manager._current_tier == DebuggleTier.PRO
        
        manager = TierManager(tier="Enterprise")
        assert manager._current_tier == DebuggleTier.ENTERPRISE
        
        manager = TierManager(tier="FREE")
        assert manager._current_tier == DebuggleTier.FREE
    
    def test_get_current_tier_method(self):
        """Test the current_tier property"""
        manager = TierManager(tier="pro")
        assert manager.current_tier == DebuggleTier.PRO
        
        manager = TierManager(tier="enterprise")
        assert manager.current_tier == DebuggleTier.ENTERPRISE
    
    def test_has_feature_method_free_tier(self):
        """Test has_feature method for FREE tier"""
        manager = TierManager(tier="free")
        
        # FREE tier should not have premium features
        assert manager.has_feature("cloud_sharing") is False
        assert manager.has_feature("advanced_analytics") is False
        assert manager.has_feature("extended_retention") is False
        assert manager.has_feature("team_management") is False
        assert manager.has_feature("sso_integration") is False
        assert manager.has_feature("custom_branding") is False
    
    def test_has_feature_method_pro_tier(self):
        """Test has_feature method for PRO tier"""
        manager = TierManager(tier="pro")
        
        # PRO tier should have some premium features
        assert manager.has_feature("cloud_sharing") is True
        assert manager.has_feature("advanced_analytics") is True
        assert manager.has_feature("priority_support") is True
        
        # But not enterprise features
        assert manager.has_feature("team_management") is False
        assert manager.has_feature("sso_integration") is False
        assert manager.has_feature("custom_branding") is False
    
    def test_has_feature_method_enterprise_tier(self):
        """Test has_feature method for ENTERPRISE tier"""
        manager = TierManager(tier="enterprise")
        
        # ENTERPRISE tier should have all features
        assert manager.has_feature("cloud_sharing") is True
        assert manager.has_feature("advanced_analytics") is True
        assert manager.has_feature("priority_support") is True
        assert manager.has_feature("team_management") is True
        assert manager.has_feature("sso_integration") is True
        assert manager.has_feature("custom_branding") is True
    
    def test_has_feature_invalid_feature(self):
        """Test has_feature with invalid feature name"""
        manager = TierManager(tier="pro")
        
        # Invalid feature should return False
        assert manager.has_feature("nonexistent_feature") is False
        assert manager.has_feature("") is False
        
        # None should raise TypeError (can't be used as attribute name)
        with pytest.raises(TypeError):
            manager.has_feature(None)
    
    def test_require_feature_success(self):
        """Test require_feature method when feature is available"""
        manager = TierManager(tier="pro")
        
        # Should not raise exception for available features
        manager.require_feature("cloud_sharing")
        manager.require_feature("advanced_analytics")
    
    def test_require_feature_failure(self):
        """Test require_feature method when feature is not available"""
        manager = TierManager(tier="free")
        
        # Should raise FeatureNotAvailableError for unavailable features
        with pytest.raises(FeatureNotAvailableError) as exc_info:
            manager.require_feature("cloud_sharing")
        
        assert "cloud_sharing" in str(exc_info.value)
        assert "PRO" in str(exc_info.value)
    
    def test_require_feature_enterprise_only(self):
        """Test require_feature for enterprise-only features"""
        manager = TierManager(tier="pro")
        
        # PRO tier should not have enterprise features
        with pytest.raises(FeatureNotAvailableError) as exc_info:
            manager.require_feature("team_management")
        
        assert "team_management" in str(exc_info.value)
        assert "PRO" in str(exc_info.value)
    
    def test_require_feature_invalid_feature(self):
        """Test require_feature with invalid feature name"""
        manager = TierManager(tier="enterprise")
        
        # Invalid feature should raise exception
        with pytest.raises(FeatureNotAvailableError):
            manager.require_feature("nonexistent_feature")


class TestHelperFunctions:
    """Test the module-level helper functions"""
    
    def setup_method(self):
        """Reset global tier manager before each test"""
        # Import the module to access the global variable
        import src.debuggle.tiers as tiers_module
        tiers_module._tier_manager = None
    
    def test_get_current_tier_function(self):
        """Test get_current_tier helper function"""
        import src.debuggle.tiers as tiers_module
        
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'pro'}):
            tiers_module._tier_manager = None  # Reset global
            tier = get_current_tier()
            assert tier == DebuggleTier.PRO
        
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'enterprise'}):
            tiers_module._tier_manager = None  # Reset global  
            tier = get_current_tier()
            assert tier == DebuggleTier.ENTERPRISE
        
        # Test default behavior
        with patch.dict(os.environ, {}, clear=True):
            if 'DEBUGGLE_TIER' in os.environ:
                del os.environ['DEBUGGLE_TIER']
            tiers_module._tier_manager = None  # Reset global
            tier = get_current_tier()
            assert tier == DebuggleTier.FREE
    
    def test_has_feature_function(self):
        """Test has_feature helper function"""
        import src.debuggle.tiers as tiers_module
        
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'pro'}):
            tiers_module._tier_manager = None  # Reset global
            assert has_feature("cloud_sharing") is True
            assert has_feature("team_management") is False
        
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'free'}):
            tiers_module._tier_manager = None  # Reset global
            assert has_feature("cloud_sharing") is False
            assert has_feature("advanced_analytics") is False
    
    def test_require_feature_function(self):
        """Test require_feature helper function"""
        import src.debuggle.tiers as tiers_module
        
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'pro'}):
            tiers_module._tier_manager = None  # Reset global
            # Should not raise for available features
            require_feature("cloud_sharing")
            require_feature("advanced_analytics")
            
            # Should raise for unavailable features
            with pytest.raises(FeatureNotAvailableError):
                require_feature("team_management")
        
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'free'}):
            tiers_module._tier_manager = None  # Reset global
            # Should raise for premium features
            with pytest.raises(FeatureNotAvailableError):
                require_feature("cloud_sharing")


class TestTierDetectionEdgeCases:
    """Test edge cases in tier detection and validation"""
    
    def test_empty_environment_variable(self):
        """Test handling of empty DEBUGGLE_TIER environment variable"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': ''}):
            with patch('src.debuggle.tiers.logger') as mock_logger:
                manager = TierManager()
                # Should default to FREE
                assert manager._current_tier == DebuggleTier.FREE
                mock_logger.warning.assert_called_once()
    
    def test_whitespace_environment_variable(self):
        """Test handling of whitespace in environment variable"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': '  pro  '}):
            with patch('src.debuggle.tiers.logger') as mock_logger:
                manager = TierManager()
                # Whitespace not handled, should default to FREE
                assert manager._current_tier == DebuggleTier.FREE
                mock_logger.warning.assert_called_once()
    
    def test_numeric_tier_values(self):
        """Test handling of numeric tier values"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': '1'}):
            with patch('src.debuggle.tiers.logger') as mock_logger:
                manager = TierManager()
                # Should default to FREE and log warning
                assert manager._current_tier == DebuggleTier.FREE
                mock_logger.warning.assert_called_once()
    
    def test_special_characters_in_tier(self):
        """Test handling of special characters in tier names"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'pro@#$'}):
            with patch('src.debuggle.tiers.logger') as mock_logger:
                manager = TierManager()
                # Should default to FREE and log warning
                assert manager._current_tier == DebuggleTier.FREE
                mock_logger.warning.assert_called_once()


class TestTierManagerStateManagement:
    """Test TierManager internal state and consistency"""
    
    def test_tier_features_consistency(self):
        """Test that tier features are consistent across managers"""
        manager1 = TierManager(tier="pro")
        manager2 = TierManager(tier="pro")
        
        # Both managers should have the same features for the same tier
        assert manager1.has_feature("cloud_sharing") == manager2.has_feature("cloud_sharing")
        assert manager1.has_feature("team_management") == manager2.has_feature("team_management")
    
    def test_tier_manager_immutability(self):
        """Test that TierManager state doesn't change after creation"""
        manager = TierManager(tier="pro")
        original_tier = manager.current_tier
        
        # Changing environment shouldn't affect existing manager
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'enterprise'}):
            assert manager.current_tier == original_tier
    
    def test_multiple_tier_managers(self):
        """Test creating multiple TierManager instances"""
        manager1 = TierManager(tier="free")
        manager2 = TierManager(tier="pro")
        manager3 = TierManager(tier="enterprise")
        
        # Each should maintain its own tier
        assert manager1.current_tier == DebuggleTier.FREE
        assert manager2.current_tier == DebuggleTier.PRO
        assert manager3.current_tier == DebuggleTier.ENTERPRISE
    
    def test_tier_manager_feature_caching(self):
        """Test that feature availability is computed correctly"""
        manager = TierManager(tier="pro")
        
        # Multiple calls should return consistent results
        assert manager.has_feature("cloud_sharing") is True
        assert manager.has_feature("cloud_sharing") is True
        assert manager.has_feature("team_management") is False
        assert manager.has_feature("team_management") is False


class TestErrorMessages:
    """Test error message quality and consistency"""
    
    def test_feature_not_available_error_message(self):
        """Test FeatureNotAvailableError message format"""
        manager = TierManager(tier="free")
        
        try:
            manager.require_feature("cloud_sharing")
            assert False, "Should have raised FeatureNotAvailableError"
        except FeatureNotAvailableError as e:
            error_msg = str(e)
            # Error message should be informative
            assert "cloud_sharing" in error_msg
            assert "PRO" in error_msg
            assert len(error_msg) > 20  # Should be reasonably detailed
    
    def test_invalid_tier_warning_message(self):
        """Test invalid tier warning message"""
        with patch('src.debuggle.tiers.logger') as mock_logger:
            TierManager(tier="invalid_tier")
            
            # Should log a warning with helpful information
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args
            warning_msg = warning_call[0][0]  # First argument to warning()
            
            assert "invalid_tier" in warning_msg
            assert "FREE" in warning_msg or "free" in warning_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])