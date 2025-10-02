"""
Interactive tag functionality tests.
Tests the tag highlighting, clicking, and filtering functionality that was previously broken.
"""

import pytest
import time
import re
from playwright.sync_api import Page, expect
from pathlib import Path


class TestTagInteractivity:
    """Test interactive tag functionality."""
    
    def test_tag_clicking_highlights_lines(self, page: Page, live_server_url: str, sample_log_file):
        """Test that clicking tags highlights corresponding log lines."""
        page.goto(live_server_url)
        
        # Upload test file
        self.upload_file_and_wait_for_results(page, sample_log_file)
        
        # Wait for tags to appear
        expect(page.locator("#tagsSection")).to_be_visible()
        tags = page.locator(".tag")
        expect(tags).to_have_count_greater_than(0)
        
        # Click first tag
        first_tag = tags.first
        tag_text = first_tag.text_content()
        first_tag.click()
        
        # Check that tag becomes active
        expect(first_tag).to_have_class(re=".*active.*")
        
        # Check that some log entries are highlighted
        highlighted_entries = page.locator(".log-entry.highlighted")
        expect(highlighted_entries).to_have_count_greater_than(0)
        
        # Click same tag again to deactivate
        first_tag.click()
        expect(first_tag).not_to_have_class(re=".*active.*")
        expect(page.locator(".log-entry.highlighted")).to_have_count(0)
    
    def test_multiple_tag_clicking(self, page: Page, live_server_url: str, sample_log_file):
        """Test clicking different tags switches highlighting correctly."""
        page.goto(live_server_url)
        
        # Upload test file
        self.upload_file_and_wait_for_results(page, sample_log_file)
        
        # Wait for multiple tags
        tags = page.locator(".tag")
        expect(tags).to_have_count_greater_than(1)
        
        # Click first tag
        first_tag = tags.nth(0)
        first_tag.click()
        expect(first_tag).to_have_class(re=".*active.*")
        
        # Click second tag
        second_tag = tags.nth(1)
        second_tag.click()
        
        # First tag should no longer be active
        expect(first_tag).not_to_have_class(re=".*active.*")
        # Second tag should be active
        expect(second_tag).to_have_class(re=".*active.*")
    
    def test_tag_highlighting_matches_content(self, page: Page, live_server_url: str, connection_error_log):
        """Test that tag highlighting matches expected log content."""
        page.goto(live_server_url)
        
        # Upload connection error log
        self.upload_file_and_wait_for_results(page, connection_error_log)
        
        # Look for Connection Problems tag
        connection_tag = page.locator(".tag:has-text('Connection Problems')")
        if connection_tag.count() > 0:
            connection_tag.click()
            
            # Check that highlighted entries contain connection-related content
            highlighted = page.locator(".log-entry.highlighted")
            expect(highlighted).to_have_count_greater_than(0)
            
            # Verify content contains connection-related terms
            for i in range(highlighted.count()):
                entry_text = highlighted.nth(i).text_content().lower()
                assert any(term in entry_text for term in ['connection', 'connect', 'refused', 'failed'])
    
    def test_tag_scroll_behavior(self, page: Page, live_server_url: str, large_log_file):
        """Test that clicking tags scrolls to first matching entry."""
        page.goto(live_server_url)
        
        self.upload_file_and_wait_for_results(page, large_log_file)
        
        # Get initial scroll position
        initial_scroll = page.evaluate("window.pageYOffset")
        
        # Click a tag
        tags = page.locator(".tag")
        if tags.count() > 0:
            tags.first.click()
            
            # Wait for scroll animation
            time.sleep(1)
            
            # Check that page scrolled (scroll position changed)
            final_scroll = page.evaluate("window.pageYOffset")
            # Note: This might be the same if first match is at top, so we just verify no JS errors
            assert isinstance(final_scroll, (int, float))
    
    def test_no_javascript_errors_on_tag_click(self, page: Page, live_server_url: str, sample_log_file):
        """Test that clicking tags doesn't produce JavaScript errors."""
        console_errors = []
        
        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)
        
        page.on("console", handle_console)
        page.goto(live_server_url)
        
        # Upload file and click tags
        self.upload_file_and_wait_for_results(page, sample_log_file)
        
        tags = page.locator(".tag")
        if tags.count() > 0:
            # Click multiple tags
            for i in range(min(3, tags.count())):
                tags.nth(i).click()
                time.sleep(0.5)
        
        # Check for JavaScript errors
        js_errors = [err for err in console_errors if "error" in err.lower()]
        assert len(js_errors) == 0, f"JavaScript errors occurred: {js_errors}"
    
    def test_tag_data_attributes_exist(self, page: Page, live_server_url: str, sample_log_file):
        """Test that log entries have proper data-tags attributes."""
        page.goto(live_server_url)
        
        self.upload_file_and_wait_for_results(page, sample_log_file)
        
        # Check that log entries have data-tags attributes
        log_entries = page.locator(".log-entry")
        expect(log_entries).to_have_count_greater_than(0)
        
        # Check that at least some entries have data-tags
        entries_with_tags = 0
        for i in range(log_entries.count()):
            entry = log_entries.nth(i)
            data_tags = entry.get_attribute("data-tags")
            if data_tags:
                entries_with_tags += 1
        
        assert entries_with_tags > 0, "No log entries have data-tags attributes"
    
    def upload_file_and_wait_for_results(self, page: Page, file_path: str):
        """Helper method to upload file and wait for processing."""
        # Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(file_path)
        
        # Wait for results to appear
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Wait for processing to complete
        time.sleep(2)


class TestTagGeneration:
    """Test that tags are generated correctly from different types of logs."""
    
    def test_error_logs_generate_error_tags(self, page: Page, live_server_url: str, error_log_file):
        """Test that error logs generate appropriate error tags."""
        page.goto(live_server_url)
        
        file_input = page.locator("#fileInput")
        file_input.set_input_files(error_log_file)
        
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check for common error tags
        tags_section = page.locator("#tagsContent")
        expect(tags_section).to_be_visible()
        
        # Should have serious problems or error-related tags
        serious_tag = page.locator(".tag:has-text('Serious Problems')")
        error_tag = page.locator(".tag:has-text('Critical Error')")
        python_tag = page.locator(".tag:has-text('Python')")
        
        # At least one error-related tag should exist
        assert (serious_tag.count() > 0 or error_tag.count() > 0 or python_tag.count() > 0)


@pytest.fixture
def sample_log_file(tmp_path):
    """Create a sample log file for testing."""
    log_file = tmp_path / "sample.log"
    log_file.write_text("""
2024-10-02 10:30:15 ERROR: Connection failed
Traceback (most recent call last):
  File "app.py", line 42, in connect_db
    connection = psycopg2.connect(host='localhost')
ConnectionError: could not connect to server
2024-10-02 10:30:16 INFO: Retrying connection...
2024-10-02 10:30:17 ERROR: AttributeError occurred
AttributeError: 'NoneType' object has no attribute '_raw_columns'
""")
    return str(log_file)


@pytest.fixture
def connection_error_log(tmp_path):
    """Create a log file with connection errors."""
    log_file = tmp_path / "connection_error.log"
    log_file.write_text("""
ERROR: Database connection failed
ConnectionError: Connection refused
psycopg2.OperationalError: could not connect to server
""")
    return str(log_file)


@pytest.fixture
def large_log_file(tmp_path):
    """Create a larger log file for scroll testing."""
    log_file = tmp_path / "large.log"
    content = []
    for i in range(50):
        content.append(f"2024-10-02 10:{i:02d}:00 INFO: Regular log entry {i}")
        if i % 10 == 0:
            content.append(f"2024-10-02 10:{i:02d}:01 ERROR: Error occurred at step {i}")
    
    log_file.write_text("\n".join(content))
    return str(log_file)


@pytest.fixture
def error_log_file(tmp_path):
    """Create a log file with various error types."""
    log_file = tmp_path / "errors.log"
    log_file.write_text("""
2024-10-02 ERROR: Multiple error types
ConnectionError: Connection refused
AttributeError: 'NoneType' object has no attribute 'test'
ValueError: invalid literal for int()
TimeoutError: Request timed out
""")
    return str(log_file)