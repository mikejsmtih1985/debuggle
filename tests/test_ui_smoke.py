"""
Simple UI test to verify the testing framework is working.
This test can be run to validate the UI test setup.
"""

import pytest
from playwright.sync_api import Page, expect


def test_debuggle_page_loads(page: Page):
    """Test that the Debuggle page loads correctly."""
    # This test assumes server is running on localhost:8000
    page.goto("http://localhost:8000")
    
    # Check page title
    expect(page).to_have_title("🐞 Debuggle - Error Analysis Tool")
    
    # Check main header
    expect(page.locator("h1")).to_contain_text("🐞 Debuggle")
    
    # Check that main upload area exists
    expect(page.locator(".drag-drop-area")).to_be_visible()
    
    print("✅ Basic UI test passed!")


def test_tag_click_function_exists(page: Page):
    """Test that the tag click function exists (verifying our bug fix)."""
    page.goto("http://localhost:8000")
    
    # Check that the toggleTagHighlight function exists
    function_exists = page.evaluate("typeof toggleTagHighlight === 'function'")
    assert function_exists, "toggleTagHighlight function not found - UI bug not fixed!"
    
    print("✅ Tag interaction function exists!")


if __name__ == "__main__":
    # Allow running this test directly for quick validation
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ])
    
    if result.returncode == 0:
        print("\n🎉 UI testing framework is working correctly!")
    else:
        print("\n❌ UI testing framework setup needs attention")
        
    sys.exit(result.returncode)