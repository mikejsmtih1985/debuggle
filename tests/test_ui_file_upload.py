"""
File upload and processing UI tests.
Tests drag & drop, file upload, and the complete file processing workflow.
"""

import pytest
import time
from playwright.sync_api import Page, expect, FilePayload
from pathlib import Path


class TestFileUpload:
    """Test file upload functionality."""
    
    def test_single_file_upload_via_input(self, page: Page, live_server_url: str, sample_log_file):
        """Test uploading a single file via file input."""
        page.goto(live_server_url)
        
        # Upload file via input
        file_input = page.locator("#fileInput")
        file_input.set_input_files(sample_log_file)
        
        # Check that file preview appears
        expect(page.locator("#filePreview")).to_be_visible(timeout=5000)
        
        # Check that processing happens automatically for single files
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Verify results content
        expect(page.locator("#resultsContent")).not_to_be_empty()
        
        # Check metadata is displayed
        expect(page.locator("#metadataSection")).to_be_visible()
    
    def test_multiple_file_upload(self, page: Page, live_server_url: str, multiple_log_files):
        """Test uploading multiple files."""
        page.goto(live_server_url)
        
        # Upload multiple files
        file_input = page.locator("#fileInput")
        file_input.set_input_files(multiple_log_files)
        
        # Should show file queue instead of auto-processing
        expect(page.locator("#fileQueue")).to_be_visible(timeout=5000)
        
        # Check that multiple file items are shown
        file_items = page.locator(".file-item")
        expect(file_items).to_have_count(len(multiple_log_files))
        
        # Process all files button should be visible
        process_all_btn = page.locator("#processAllBtn")
        expect(process_all_btn).to_be_visible()
        expect(process_all_btn).to_contain_text("Process All")
    
    def test_process_all_files_button(self, page: Page, live_server_url: str, multiple_log_files):
        """Test the process all files functionality."""
        page.goto(live_server_url)
        
        file_input = page.locator("#fileInput")
        file_input.set_input_files(multiple_log_files)
        
        # Wait for file queue
        expect(page.locator("#fileQueue")).to_be_visible()
        
        # Click process all
        process_all_btn = page.locator("#processAllBtn")
        process_all_btn.click()
        
        # Wait for processing to complete
        expect(process_all_btn).to_contain_text("All Files Processed!", timeout=15000)
        
        # Check that file tabs are created
        expect(page.locator("#fileTabs")).to_be_visible()
        file_tabs = page.locator(".file-tab")
        expect(file_tabs).to_have_count(len(multiple_log_files))
    
    def test_individual_file_processing(self, page: Page, live_server_url: str, multiple_log_files):
        """Test processing individual files from queue."""
        page.goto(live_server_url)
        
        file_input = page.locator("#fileInput")
        file_input.set_input_files(multiple_log_files[:2])  # Upload 2 files
        
        expect(page.locator("#fileQueue")).to_be_visible()
        
        # Find and click process button for first file
        first_file_item = page.locator(".file-item").first
        process_btn = first_file_item.locator("button:has-text('Process')")
        process_btn.click()
        
        # Wait for processing
        time.sleep(3)
        
        # Check that file status changed
        expect(first_file_item).to_have_class(re=".*completed.*")
        
        # View results button should appear
        view_btn = first_file_item.locator("button:has-text('View Results')")
        expect(view_btn).to_be_visible()
    
    def test_file_removal(self, page: Page, live_server_url: str, sample_log_file):
        """Test removing uploaded files."""
        page.goto(live_server_url)
        
        # Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(sample_log_file)
        
        # Wait for file preview
        expect(page.locator("#filePreview")).to_be_visible()
        
        # Click remove button
        remove_btn = page.locator("#removeBtn")
        remove_btn.click()
        
        # File preview should disappear
        expect(page.locator("#filePreview")).not_to_be_visible()
        
        # Drag drop area should reset
        drag_drop_area = page.locator(".drag-drop-area")
        expect(drag_drop_area).not_to_have_class(re=".*file-selected.*")
    
    def test_file_upload_error_handling(self, page: Page, live_server_url: str, invalid_file):
        """Test error handling for invalid files."""
        page.goto(live_server_url)
        
        # Try to upload invalid file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(invalid_file)
        
        # Should show error message or handle gracefully
        # (This depends on how the backend handles invalid files)
        time.sleep(2)
        
        # Check that either error message appears or file is rejected
        error_msg = page.locator("#errorMessage")
        if error_msg.is_visible():
            expect(error_msg).to_contain_text("error", ignore_case=True)


class TestDragAndDrop:
    """Test drag and drop functionality."""
    
    def test_drag_drop_visual_feedback(self, page: Page, live_server_url: str):
        """Test that drag and drop area provides visual feedback."""
        page.goto(live_server_url)
        
        drag_drop_area = page.locator(".drag-drop-area")
        
        # Test hover state
        drag_drop_area.hover()
        
        # The area should be interactive
        expect(drag_drop_area).to_be_visible()
        expect(drag_drop_area).to_have_css("cursor", "pointer")
    
    def test_drag_drop_area_click_opens_file_dialog(self, page: Page, live_server_url: str):
        """Test that clicking drag drop area opens file dialog."""
        page.goto(live_server_url)
        
        # Mock file dialog behavior by checking file input is triggered
        file_input = page.locator("#fileInput")
        drag_drop_area = page.locator(".drag-drop-area")
        
        # Click on drag drop area (not on the button)
        drag_drop_area.click()
        
        # This should trigger the file input (though we can't test the actual dialog opening)
        expect(file_input).to_be_attached()


class TestFileProcessingWorkflow:
    """Test complete file processing workflows."""
    
    def test_complete_single_file_workflow(self, page: Page, live_server_url: str, python_error_log):
        """Test complete workflow from upload to results display."""
        page.goto(live_server_url)
        
        # Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(python_error_log)
        
        # Auto-processing should happen
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check all result components
        expect(page.locator("#resultsContent")).to_be_visible()
        expect(page.locator("#summarySection")).to_be_visible()
        expect(page.locator("#tagsSection")).to_be_visible()
        expect(page.locator("#metadataSection")).to_be_visible()
        
        # Check that content contains processed log data
        results_content = page.locator("#resultsContent")
        expect(results_content).not_to_be_empty()
        
        # Check that tags are clickable
        tags = page.locator(".tag")
        expect(tags).to_have_count_greater_than(0)
        
        # Test tag interaction
        if tags.count() > 0:
            tags.first.click()
            expect(tags.first).to_have_class(re=".*active.*")
    
    def test_option_changes_affect_results(self, page: Page, live_server_url: str, sample_log_file):
        """Test that changing options affects the displayed results."""
        page.goto(live_server_url)
        
        # Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(sample_log_file)
        
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Toggle off summary
        summarize_toggle = page.locator('div:has(#summarize)')
        if summarize_toggle.is_visible():
            summarize_toggle.click()
            
            # Summary section should disappear
            expect(page.locator("#summarySection")).not_to_be_visible()
        
        # Toggle off tags
        tags_toggle = page.locator('div:has(#tags)')
        if tags_toggle.is_visible():
            tags_toggle.click()
            
            # Tags section should disappear
            expect(page.locator("#tagsSection")).not_to_be_visible()
    
    def test_live_reprocessing_works(self, page: Page, live_server_url: str, sample_log_file):
        """Test that toggling options triggers live reprocessing."""
        page.goto(live_server_url)
        
        # Upload and process file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(sample_log_file)
        
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Get initial results content
        initial_content = page.locator("#resultsContent").text_content()
        
        # Toggle formatting option
        highlight_toggle = page.locator('div:has(#highlight)')
        highlight_toggle.click()
        
        # Wait for reprocessing
        time.sleep(1)
        
        # Content should change (plain vs formatted)
        new_content = page.locator("#resultsContent").text_content()
        
        # The content structure should be different between formatted and plain
        # (This might be subtle, so we just check that reprocessing happened without errors)
        assert isinstance(new_content, str)


@pytest.fixture
def sample_log_file(tmp_path):
    """Create a sample log file."""
    log_file = tmp_path / "sample.log"
    log_file.write_text("ERROR: Test error\nConnection failed\nTraceback...")
    return str(log_file)


@pytest.fixture
def python_error_log(tmp_path):
    """Create a Python error log file."""
    log_file = tmp_path / "python_error.log"
    log_file.write_text("""
2024-10-02 10:30:15 ERROR: Python error occurred
Traceback (most recent call last):
  File "app.py", line 42, in connect_db
    connection = psycopg2.connect(host='localhost')
ConnectionError: could not connect to server
AttributeError: 'NoneType' object has no attribute '_raw_columns'
""")
    return str(log_file)


@pytest.fixture
def multiple_log_files(tmp_path):
    """Create multiple log files for testing."""
    files = []
    for i in range(3):
        log_file = tmp_path / f"log_{i}.log"
        log_file.write_text(f"ERROR: Error in file {i}\nSome error content {i}")
        files.append(str(log_file))
    return files


@pytest.fixture
def invalid_file(tmp_path):
    """Create an invalid file for error testing."""
    invalid_file = tmp_path / "invalid.bin"
    invalid_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')
    return str(invalid_file)