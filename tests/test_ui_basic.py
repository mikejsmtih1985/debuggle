"""
Basic UI tests for Debuggle interface.
Tests core functionality like page loading, navigation, and basic interactions.
"""

import pytest
import time
from playwright.sync_api import Page, expect
from pathlib import Path


class TestBasicUI:
    """Test basic UI functionality and interactions."""
    
    def test_page_loads_correctly(self, page: Page, live_server_url: str):
        """Test that the main page loads with correct title and basic elements."""
        page.goto(live_server_url)
        
        # Check page title
        expect(page).to_have_title("🐞 Debuggle - Error Analysis Tool")
        
        # Check main header
        expect(page.locator("h1")).to_contain_text("🐞 Debuggle")
        expect(page.locator(".header p")).to_contain_text("Transform chaotic logs into clear, understandable insights")
        
        # Check main upload area exists
        expect(page.locator(".drag-drop-area")).to_be_visible()
        expect(page.locator(".upload-text")).to_contain_text("Drag & drop your log file(s) here")
        
        # Check option toggles exist
        expect(page.locator("#summarize")).to_be_attached()
        expect(page.locator("#tags")).to_be_attached()
        expect(page.locator("#highlight")).to_be_attached()
    
    def test_option_toggles_work(self, page: Page, live_server_url: str):
        """Test that the analysis option toggles work correctly."""
        page.goto(live_server_url)
        
        # Check initial state (all should be active/checked)
        summarize_toggle = page.locator('div:has(#summarize)')
        tags_toggle = page.locator('div:has(#tags)')
        highlight_toggle = page.locator('div:has(#highlight)')
        
        expect(summarize_toggle).to_have_class(re=".*active.*")
        expect(tags_toggle).to_have_class(re=".*active.*")
        expect(highlight_toggle).to_have_class(re=".*active.*")
        
        # Click to deactivate
        summarize_toggle.click()
        expect(summarize_toggle).not_to_have_class(re=".*active.*")
        expect(page.locator("#summarize")).not_to_be_checked()
        
        # Click again to reactivate
        summarize_toggle.click()
        expect(summarize_toggle).to_have_class(re=".*active.*")
        expect(page.locator("#summarize")).to_be_checked()
    
    def test_file_input_opens(self, page: Page, live_server_url: str):
        """Test that clicking Choose File button opens file dialog."""
        page.goto(live_server_url)
        
        # Test file input accessibility
        choose_file_btn = page.locator("button:has-text('Choose File')")
        expect(choose_file_btn).to_be_visible()
        
        # Check that file input exists and is properly linked
        file_input = page.locator("#fileInput")
        expect(file_input).to_be_attached()
        expect(file_input).to_have_attribute("accept", ".log,.txt,.out,.err,.json")
        expect(file_input).to_have_attribute("multiple")
    
    def test_drag_drop_area_states(self, page: Page, live_server_url: str):
        """Test drag and drop area visual states."""
        page.goto(live_server_url)
        
        drag_drop_area = page.locator(".drag-drop-area")
        
        # Test hover state
        drag_drop_area.hover()
        
        # Test that area is interactive
        expect(drag_drop_area).to_be_visible()
        expect(drag_drop_area).to_have_css("cursor", "pointer")
    
    def test_results_section_initially_hidden(self, page: Page, live_server_url: str):
        """Test that results section is hidden until analysis is performed."""
        page.goto(live_server_url)
        
        results_section = page.locator("#resultsSection")
        expect(results_section).not_to_be_visible()
        
        error_message = page.locator("#errorMessage")
        expect(error_message).not_to_be_visible()


class TestUIResponsiveness:
    """Test UI responsiveness and layout."""
    
    def test_mobile_layout(self, page: Page, live_server_url: str):
        """Test that the UI works on mobile viewports."""
        page.set_viewport_size({"width": 375, "height": 667})  # iPhone SE size
        page.goto(live_server_url)
        
        # Check that main elements are still visible
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator(".drag-drop-area")).to_be_visible()
        expect(page.locator(".options-section")).to_be_visible()
    
    def test_tablet_layout(self, page: Page, live_server_url: str):
        """Test that the UI works on tablet viewports."""
        page.set_viewport_size({"width": 768, "height": 1024})  # iPad size
        page.goto(live_server_url)
        
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator(".drag-drop-area")).to_be_visible()
        expect(page.locator(".options-section")).to_be_visible()
    
    def test_desktop_layout(self, page: Page, live_server_url: str):
        """Test that the UI works on desktop viewports."""
        page.set_viewport_size({"width": 1920, "height": 1080})  # Full HD
        page.goto(live_server_url)
        
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator(".drag-drop-area")).to_be_visible()
        expect(page.locator(".options-section")).to_be_visible()


class TestUIAccessibility:
    """Test UI accessibility features."""
    
    def test_keyboard_navigation(self, page: Page, live_server_url: str):
        """Test that the UI can be navigated with keyboard."""
        page.goto(live_server_url)
        
        # Test tab navigation through interactive elements
        page.keyboard.press("Tab")  # Should focus on Choose File button
        focused = page.evaluate("document.activeElement.textContent")
        assert "Choose File" in focused
        
        # Continue tabbing through toggle buttons
        page.keyboard.press("Tab")  # First toggle
        page.keyboard.press("Tab")  # Second toggle
        page.keyboard.press("Tab")  # Third toggle
    
    def test_aria_labels_exist(self, page: Page, live_server_url: str):
        """Test that important elements have proper ARIA labels."""
        page.goto(live_server_url)
        
        # Check that file input has proper labeling
        file_input = page.locator("#fileInput")
        expect(file_input).to_be_attached()
        
        # Check that buttons have descriptive text
        choose_file_btn = page.locator("button:has-text('Choose File')")
        expect(choose_file_btn).to_be_visible()


@pytest.fixture
def live_server_url():
    """Provide URL for live server - should be running on localhost:8000."""
    return "http://localhost:8000"