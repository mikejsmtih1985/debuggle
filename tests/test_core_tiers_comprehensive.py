"""
🎓 DEBUGGLE UNIVERSITY ACCESS CONTROL SYSTEM - COMPREHENSIVE TESTING 🏫

Welcome to Debuggle University! We're testing the campus access control system that determines
which facilities students, faculty, and VIPs can access based on their membership cards.

Think of this like a university where:
- 🎒 STUDENTS (FREE): Basic classroom access, library, cafeteria
- 👨‍🎓 FACULTY (PRO): All student access + faculty lounge, research labs, parking
- 🎩 ADMINISTRATION (ENTERPRISE): All access + executive suite, board rooms, server room

Our mission: Test every door, every card reader, every access scenario to ensure 
the campus security system works flawlessly! 🚨🔐

COVERAGE TARGET: 76% → 95%+ (aiming for Dean's List performance!)

TEST ARCHITECTURE:
1. 🏛️ TestUniversityAccessControlSetup - Basic system initialization
2. 🎓 TestStudentAccessLevel - FREE tier functionality  
3. 👨‍🎓 TestFacultyAccessLevel - PRO tier features
4. 🎩 TestAdministrationAccessLevel - ENTERPRISE tier privileges
5. 🚪 TestAccessControlEnforcement - Feature requirement validation
6. 🔄 TestTierDetectionSystem - Environment-based tier detection
7. 📊 TestCampusInformationSystem - Tier info and upgrade benefits
8. 🚨 TestSecurityProtocols - Error handling and edge cases
9. 🏫 TestGlobalCampusSecurity - Singleton manager and convenience functions
10. 🎯 TestRealWorldAccessScenarios - Integration scenarios
"""

import unittest
import os
from unittest.mock import patch, Mock
from dataclasses import asdict

from src.debuggle.core.tiers import (
    DebuggleTier, TierFeatures, TierManager, FeatureNotAvailableError,
    get_tier_manager, has_feature, require_feature, get_current_tier,
    is_free_tier, is_pro_tier, is_enterprise_tier
)


class TestUniversityAccessControlSetup(unittest.TestCase):
    """
    🏛️ University Campus Security System Initialization Testing
    
    Like testing the main security console when the university opens each morning.
    We need to verify all the basic systems are working before students arrive!
    """
    
    def test_tier_enum_values_defined(self):
        """Test that all university membership levels are properly defined"""
        # Verify all three membership levels exist
        self.assertEqual(DebuggleTier.FREE.value, "free")
        self.assertEqual(DebuggleTier.PRO.value, "pro") 
        self.assertEqual(DebuggleTier.ENTERPRISE.value, "enterprise")
        
        # Should be exactly 3 tiers - no more, no less
        all_tiers = list(DebuggleTier)
        self.assertEqual(len(all_tiers), 3)
    
    def test_tier_features_dataclass_structure(self):
        """Test that the feature checklist structure is correct"""
        features = TierFeatures()
        
        # Basic features should be enabled by default (like campus walkways)
        self.assertTrue(features.basic_error_analysis)
        self.assertTrue(features.local_search)
        self.assertTrue(features.syntax_highlighting)
        self.assertTrue(features.error_explanations)
        
        # Premium features should be disabled by default
        self.assertFalse(features.cloud_sharing)
        self.assertFalse(features.advanced_analytics)
        self.assertFalse(features.team_management)
        self.assertFalse(features.sso_integration)
    
    def test_tier_manager_initialization_defaults(self):
        """Test security system initialization with default settings"""
        with patch.dict(os.environ, {}, clear=True):
            manager = TierManager()
            
            # Should default to FREE tier (like visitor access)
            self.assertEqual(manager.current_tier, DebuggleTier.FREE)
            self.assertIsInstance(manager.features, TierFeatures)
    
    def test_tier_manager_initialization_with_override(self):
        """Test security system with specific tier override"""
        # Test each tier override
        for tier in [DebuggleTier.FREE, DebuggleTier.PRO, DebuggleTier.ENTERPRISE]:
            with self.subTest(tier=tier):
                manager = TierManager(tier=tier.value)
                self.assertEqual(manager.current_tier, tier)


class TestStudentAccessLevel(unittest.TestCase):
    """
    🎒 Student Access Level Testing (FREE Tier)
    
    Testing what basic students can access on campus. Like checking that
    student ID cards work for classrooms and cafeteria but not faculty areas.
    """
    
    def setUp(self):
        """Set up student access testing environment"""
        self.student_manager = TierManager(tier="free")
    
    def test_student_basic_features_enabled(self):
        """Test that students have access to basic campus facilities"""
        # Students should have access to basic learning tools
        self.assertTrue(self.student_manager.has_feature('basic_error_analysis'))
        self.assertTrue(self.student_manager.has_feature('local_search'))
        self.assertTrue(self.student_manager.has_feature('syntax_highlighting'))
        self.assertTrue(self.student_manager.has_feature('error_explanations'))
    
    def test_student_premium_features_blocked(self):
        """Test that students are blocked from premium facilities"""
        # Students should NOT have access to premium features
        self.assertFalse(self.student_manager.has_feature('cloud_sharing'))
        self.assertFalse(self.student_manager.has_feature('advanced_analytics'))
        self.assertFalse(self.student_manager.has_feature('priority_support'))
        self.assertFalse(self.student_manager.has_feature('custom_dashboards'))
    
    def test_student_enterprise_features_blocked(self):
        """Test that students are blocked from administrative areas"""
        # Students should NOT have access to enterprise features
        self.assertFalse(self.student_manager.has_feature('team_management'))
        self.assertFalse(self.student_manager.has_feature('sso_integration'))
        self.assertFalse(self.student_manager.has_feature('audit_logs'))
        self.assertFalse(self.student_manager.has_feature('dedicated_support'))
    
    def test_student_access_control_enforcement(self):
        """Test that access control properly blocks students from restricted areas"""
        # Attempting to access premium features should raise security error
        with self.assertRaises(FeatureNotAvailableError):
            self.student_manager.require_feature('cloud_sharing')
        
        with self.assertRaises(FeatureNotAvailableError):
            self.student_manager.require_feature('team_management')
    
    def test_student_tier_information(self):
        """Test student membership card information display"""
        info = self.student_manager.get_tier_info()
        
        self.assertEqual(info['current_tier'], 'free')
        self.assertEqual(info['tier_display_name'], 'Free')
        self.assertTrue(info['can_upgrade'])  # Students can upgrade to faculty
        
        # Should have exactly the basic features enabled
        enabled_features = [name for name, enabled in info['features_enabled'].items() if enabled]
        expected_basic_features = ['basic_error_analysis', 'local_search', 'syntax_highlighting', 'error_explanations']
        
        for feature in expected_basic_features:
            self.assertIn(feature, enabled_features)


class TestFacultyAccessLevel(unittest.TestCase):
    """
    👨‍🎓 Faculty Access Level Testing (PRO Tier)
    
    Testing faculty privileges - they should have all student access PLUS
    additional research facilities and professional tools.
    """
    
    def setUp(self):
        """Set up faculty access testing environment"""
        self.faculty_manager = TierManager(tier="pro")
    
    def test_faculty_inherits_all_student_features(self):
        """Test that faculty have all basic student privileges"""
        # Faculty should have all basic features
        self.assertTrue(self.faculty_manager.has_feature('basic_error_analysis'))
        self.assertTrue(self.faculty_manager.has_feature('local_search'))
        self.assertTrue(self.faculty_manager.has_feature('syntax_highlighting'))
        self.assertTrue(self.faculty_manager.has_feature('error_explanations'))
    
    def test_faculty_premium_features_enabled(self):
        """Test that faculty have access to professional research tools"""
        # Faculty should have access to PRO features
        self.assertTrue(self.faculty_manager.has_feature('cloud_sharing'))
        self.assertTrue(self.faculty_manager.has_feature('advanced_analytics'))
        self.assertTrue(self.faculty_manager.has_feature('priority_support'))
        self.assertTrue(self.faculty_manager.has_feature('unlimited_storage'))
        self.assertTrue(self.faculty_manager.has_feature('custom_dashboards'))
        self.assertTrue(self.faculty_manager.has_feature('api_access'))
    
    def test_faculty_enterprise_features_blocked(self):
        """Test that faculty are still blocked from administrative areas"""
        # Faculty should NOT have access to enterprise features
        self.assertFalse(self.faculty_manager.has_feature('team_management'))
        self.assertFalse(self.faculty_manager.has_feature('sso_integration'))
        self.assertFalse(self.faculty_manager.has_feature('audit_logs'))
        self.assertFalse(self.faculty_manager.has_feature('custom_branding'))
    
    def test_faculty_access_control_mixed(self):
        """Test mixed access control - some features allowed, others blocked"""
        # These should work (no exception)
        try:
            self.faculty_manager.require_feature('cloud_sharing')
            self.faculty_manager.require_feature('advanced_analytics')
        except FeatureNotAvailableError:
            self.fail("Faculty should have access to PRO features")
        
        # This should still be blocked
        with self.assertRaises(FeatureNotAvailableError):
            self.faculty_manager.require_feature('team_management')


class TestAdministrationAccessLevel(unittest.TestCase):
    """
    🎩 Administrative Access Level Testing (ENTERPRISE Tier)
    
    Testing the highest privilege level - administrators should have access
    to everything including sensitive systems and management tools.
    """
    
    def setUp(self):
        """Set up administrative access testing environment"""
        self.admin_manager = TierManager(tier="enterprise")
    
    def test_admin_has_all_features(self):
        """Test that administrators have access to everything on campus"""
        # Get all possible features
        all_features = TierFeatures()
        
        for attr_name in dir(all_features):
            if not attr_name.startswith('_'):
                with self.subTest(feature=attr_name):
                    self.assertTrue(self.admin_manager.has_feature(attr_name))
    
    def test_admin_enterprise_features_enabled(self):
        """Test that administrators have access to executive facilities"""
        # Administrators should have access to enterprise features
        self.assertTrue(self.admin_manager.has_feature('team_management'))
        self.assertTrue(self.admin_manager.has_feature('sso_integration'))
        self.assertTrue(self.admin_manager.has_feature('audit_logs'))
        self.assertTrue(self.admin_manager.has_feature('custom_branding'))
        self.assertTrue(self.admin_manager.has_feature('dedicated_support'))
        self.assertTrue(self.admin_manager.has_feature('on_premise_deployment'))
        self.assertTrue(self.admin_manager.has_feature('compliance_reports'))
        self.assertTrue(self.admin_manager.has_feature('advanced_integrations'))
    
    def test_admin_no_access_restrictions(self):
        """Test that no features are blocked for administrators"""
        # All feature requirements should pass
        features_to_test = [
            'basic_error_analysis', 'cloud_sharing', 'team_management',
            'advanced_analytics', 'sso_integration', 'custom_branding'
        ]
        
        for feature in features_to_test:
            with self.subTest(feature=feature):
                try:
                    self.admin_manager.require_feature(feature)
                except FeatureNotAvailableError:
                    self.fail(f"Administrator should have access to {feature}")
    
    def test_admin_cannot_upgrade(self):
        """Test that administrators are already at the highest level"""
        info = self.admin_manager.get_tier_info()
        self.assertFalse(info['can_upgrade'])


class TestAccessControlEnforcement(unittest.TestCase):
    """
    🚪 Access Control Enforcement Testing
    
    Testing the security gates and card readers - ensuring that access
    control properly blocks unauthorized attempts and allows valid access.
    """
    
    def test_feature_requirement_with_access(self):
        """Test that feature requirements pass when user has access"""
        pro_manager = TierManager(tier="pro")
        
        # This should not raise an exception
        try:
            pro_manager.require_feature('cloud_sharing')
        except FeatureNotAvailableError:
            self.fail("PRO user should have access to cloud_sharing")
    
    def test_feature_requirement_without_access(self):
        """Test that feature requirements block unauthorized access"""
        free_manager = TierManager(tier="free")
        
        # This should raise FeatureNotAvailableError
        with self.assertRaises(FeatureNotAvailableError) as cm:
            free_manager.require_feature('cloud_sharing')
        
        # Error message should be informative
        self.assertIn('cloud_sharing', str(cm.exception))
        self.assertIn('PRO', str(cm.exception).upper())
    
    def test_custom_error_messages(self):
        """Test that custom error messages work for access denials"""
        free_manager = TierManager(tier="free")
        custom_message = "Sorry, this research lab requires faculty access!"
        
        with self.assertRaises(FeatureNotAvailableError) as cm:
            free_manager.require_feature('advanced_analytics', custom_message)
        
        self.assertEqual(str(cm.exception), custom_message)
    
    def test_nonexistent_feature_handling(self):
        """Test how system handles requests for nonexistent features"""
        manager = TierManager(tier="enterprise")
        
        # Should return False for nonexistent features
        self.assertFalse(manager.has_feature('nonexistent_feature'))
        
        # Should raise error when requiring nonexistent feature
        with self.assertRaises(FeatureNotAvailableError):
            manager.require_feature('nonexistent_feature')


class TestTierDetectionSystem(unittest.TestCase):
    """
    🔍 Tier Detection System Testing
    
    Testing how the system figures out what membership level someone has
    by checking their environment variables and credentials.
    """
    
    def test_environment_variable_detection(self):
        """Test tier detection from DEBUGGLE_TIER environment variable"""
        test_cases = [
            ("free", DebuggleTier.FREE),
            ("pro", DebuggleTier.PRO),
            ("enterprise", DebuggleTier.ENTERPRISE),
            ("FREE", DebuggleTier.FREE),  # Case insensitive
            ("Pro", DebuggleTier.PRO),
            ("ENTERPRISE", DebuggleTier.ENTERPRISE)
        ]
        
        for env_value, expected_tier in test_cases:
            with self.subTest(env_value=env_value):
                with patch.dict(os.environ, {'DEBUGGLE_TIER': env_value}):
                    manager = TierManager()
                    self.assertEqual(manager.current_tier, expected_tier)
    
    def test_invalid_tier_fallback(self):
        """Test that invalid tier values fall back to FREE with warning"""
        invalid_values = ["invalid", "premium", "basic", "gold", ""]
        
        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                with patch.dict(os.environ, {'DEBUGGLE_TIER': invalid_value}):
                    manager = TierManager()
                    self.assertEqual(manager.current_tier, DebuggleTier.FREE)
    
    def test_no_environment_variable_defaults_to_free(self):
        """Test that missing environment variable defaults to FREE tier"""
        with patch.dict(os.environ, {}, clear=True):
            manager = TierManager()
            self.assertEqual(manager.current_tier, DebuggleTier.FREE)
    
    def test_tier_override_priority(self):
        """Test that explicit tier override takes priority over environment"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'free'}):
            # Override should win over environment variable
            manager = TierManager(tier="enterprise")
            self.assertEqual(manager.current_tier, DebuggleTier.ENTERPRISE)


class TestCampusInformationSystem(unittest.TestCase):
    """
    📊 Campus Information System Testing
    
    Testing the information kiosks that show students what facilities
    they can access and what benefits they'd get from upgrading.
    """
    
    def test_tier_info_structure(self):
        """Test that tier information contains all expected fields"""
        manager = TierManager(tier="pro")
        info = manager.get_tier_info()
        
        required_fields = ['current_tier', 'tier_display_name', 'features_enabled', 'can_upgrade']
        for field in required_fields:
            self.assertIn(field, info)
    
    def test_upgrade_benefits_for_students(self):
        """Test upgrade benefits display for FREE tier users"""
        free_manager = TierManager(tier="free")
        benefits = free_manager.get_upgrade_benefits()
        
        # Should show benefits for both PRO and ENTERPRISE
        self.assertIn("PRO", benefits)
        self.assertIn("ENTERPRISE", benefits)
        
        # PRO benefits should include things not in FREE
        pro_benefits = benefits["PRO"]
        self.assertIn("Cloud Sharing", pro_benefits)
        self.assertIn("Advanced Analytics", pro_benefits)
        
        # Should not include basic features already in FREE
        self.assertNotIn("Basic Error Analysis", pro_benefits)
    
    def test_upgrade_benefits_for_faculty(self):
        """Test upgrade benefits display for PRO tier users"""
        pro_manager = TierManager(tier="pro")
        benefits = pro_manager.get_upgrade_benefits()
        
        # Should only show ENTERPRISE benefits
        self.assertNotIn("PRO", benefits)
        self.assertIn("ENTERPRISE", benefits)
        
        # Should show enterprise-only features
        enterprise_benefits = benefits["ENTERPRISE"]
        self.assertIn("Team Management", enterprise_benefits)
        self.assertIn("Sso Integration", enterprise_benefits)
    
    def test_no_upgrade_benefits_for_administrators(self):
        """Test that administrators see no upgrade benefits (already maxed out)"""
        enterprise_manager = TierManager(tier="enterprise")
        benefits = enterprise_manager.get_upgrade_benefits()
        
        # Should be empty - nowhere to upgrade to
        self.assertEqual(len(benefits), 0)


class TestSecurityProtocols(unittest.TestCase):
    """
    🚨 Security Protocols and Error Handling Testing
    
    Testing what happens when the security system encounters problems
    or unusual situations - like fire drills or system malfunctions.
    """
    
    def test_feature_not_available_error_properties(self):
        """Test that security error has proper properties"""
        error = FeatureNotAvailableError("Access denied")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Access denied")
    
    def test_manager_with_none_tier_override(self):
        """Test manager behavior when explicitly passed None"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'pro'}):
            manager = TierManager(tier=None)
            # Should use environment variable
            self.assertEqual(manager.current_tier, DebuggleTier.PRO)
    
    def test_feature_check_with_empty_string(self):
        """Test feature checking with edge case inputs"""
        manager = TierManager(tier="free")
        
        # Empty string should return False
        self.assertFalse(manager.has_feature(""))
        
        # Should not crash on weird inputs
        self.assertFalse(manager.has_feature(" "))


class TestGlobalCampusSecurity(unittest.TestCase):
    """
    🏫 Global Campus Security System Testing
    
    Testing the campus-wide security system singleton and convenience
    functions that work across the entire university.
    """
    
    def setUp(self):
        """Reset global state before each test"""
        # Clear the global singleton
        import src.debuggle.core.tiers as tiers_module
        tiers_module._tier_manager = None
    
    def test_global_tier_manager_singleton(self):
        """Test that global tier manager is a singleton"""
        manager1 = get_tier_manager()
        manager2 = get_tier_manager()
        
        # Should be the same instance
        self.assertIs(manager1, manager2)
    
    def test_convenience_function_has_feature(self):
        """Test the global has_feature convenience function"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'pro'}):
            # Clear singleton to pick up new environment
            import src.debuggle.core.tiers as tiers_module
            tiers_module._tier_manager = None
            
            self.assertTrue(has_feature('cloud_sharing'))
            self.assertFalse(has_feature('team_management'))
    
    def test_convenience_function_require_feature(self):
        """Test the global require_feature convenience function"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'free'}):
            # Clear singleton to pick up new environment
            import src.debuggle.core.tiers as tiers_module
            tiers_module._tier_manager = None
            
            # Should work for basic features
            try:
                require_feature('basic_error_analysis')
            except FeatureNotAvailableError:
                self.fail("Should have access to basic features")
            
            # Should fail for premium features
            with self.assertRaises(FeatureNotAvailableError):
                require_feature('cloud_sharing')
    
    def test_convenience_function_get_current_tier(self):
        """Test the global get_current_tier convenience function"""
        with patch.dict(os.environ, {'DEBUGGLE_TIER': 'enterprise'}):
            # Clear singleton to pick up new environment
            import src.debuggle.core.tiers as tiers_module
            tiers_module._tier_manager = None
            
            self.assertEqual(get_current_tier(), DebuggleTier.ENTERPRISE)
    
    def test_tier_check_convenience_functions(self):
        """Test the is_*_tier convenience functions"""
        test_cases = [
            ("free", True, False, False),
            ("pro", False, True, False),
            ("enterprise", False, True, True)
        ]
        
        for tier_name, expect_free, expect_pro, expect_enterprise in test_cases:
            with self.subTest(tier=tier_name):
                with patch.dict(os.environ, {'DEBUGGLE_TIER': tier_name}):
                    # Clear singleton to pick up new environment
                    import src.debuggle.core.tiers as tiers_module
                    tiers_module._tier_manager = None
                    
                    self.assertEqual(is_free_tier(), expect_free)
                    self.assertEqual(is_pro_tier(), expect_pro)
                    self.assertEqual(is_enterprise_tier(), expect_enterprise)


class TestRealWorldAccessScenarios(unittest.TestCase):
    """
    🎯 Real-World Access Scenarios Testing
    
    Testing realistic scenarios that would happen in actual university
    operations - like student trying to use research equipment or
    faculty trying to access administrative systems.
    """
    
    def test_student_research_project_workflow(self):
        """Test typical student workflow hitting tier limitations"""
        student_manager = TierManager(tier="free")
        
        # Student should be able to do basic analysis
        self.assertTrue(student_manager.has_feature('basic_error_analysis'))
        self.assertTrue(student_manager.has_feature('local_search'))
        
        # But when trying to share results or get advanced analytics...
        with self.assertRaises(FeatureNotAvailableError):
            student_manager.require_feature('cloud_sharing', 
                "Sharing research requires faculty access")
    
    def test_faculty_collaboration_workflow(self):
        """Test faculty member collaborating with other researchers"""
        faculty_manager = TierManager(tier="pro")
        
        # Faculty should be able to share and collaborate
        try:
            faculty_manager.require_feature('cloud_sharing')
            faculty_manager.require_feature('advanced_analytics')
            faculty_manager.require_feature('api_access')
        except FeatureNotAvailableError:
            self.fail("Faculty should have access to collaboration tools")
        
        # But still can't access administrative functions
        with self.assertRaises(FeatureNotAvailableError):
            faculty_manager.require_feature('audit_logs')
    
    def test_administrative_compliance_audit(self):
        """Test administrator running compliance audit"""
        admin_manager = TierManager(tier="enterprise")
        
        # Admin should have access to all audit and compliance features
        compliance_features = [
            'audit_logs', 'compliance_reports', 'team_management',
            'sso_integration', 'custom_branding'
        ]
        
        for feature in compliance_features:
            try:
                admin_manager.require_feature(feature)
            except FeatureNotAvailableError:
                self.fail(f"Administrator should have access to {feature}")
    
    def test_tier_upgrade_simulation(self):
        """Test what happens when a user upgrades their tier"""
        # Start as student
        original_features = TierManager(tier="free").get_tier_info()['features_enabled']
        
        # Upgrade to faculty
        upgraded_features = TierManager(tier="pro").get_tier_info()['features_enabled']
        
        # Should have more features enabled after upgrade
        original_count = sum(original_features.values())
        upgraded_count = sum(upgraded_features.values())
        self.assertGreater(upgraded_count, original_count)
        
        # All original features should still be enabled
        for feature, enabled in original_features.items():
            if enabled:
                self.assertTrue(upgraded_features[feature], 
                    f"Feature {feature} should still be enabled after upgrade")


if __name__ == '__main__':
    # Run our comprehensive university access control testing!
    unittest.main()