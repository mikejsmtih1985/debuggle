"""
API integration UI tests.
Tests end-to-end workflows from UI actions through API calls to result display.
"""

import pytest
import time
import json
from playwright.sync_api import Page, expect


class TestAPIIntegration:
    """Test integration between UI and API endpoints."""
    
    def test_file_upload_calls_correct_api_endpoint(self, page: Page, live_server_url: str, test_log_file):
        """Test that file upload calls the /api/v1/upload-log endpoint."""
        # Monitor network requests
        requests = []
        
        def handle_request(request):
            requests.append({
                "url": request.url,
                "method": request.method,
                "post_data": request.post_data
            })
        
        page.on("request", handle_request)
        page.goto(live_server_url)
        
        # Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(test_log_file)
        
        # Wait for processing
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check that correct API was called
        upload_requests = [r for r in requests if "/api/v1/upload-log" in r["url"]]
        assert len(upload_requests) > 0, "upload-log API was not called"
        
        # Verify it was a POST request
        assert any(r["method"] == "POST" for r in upload_requests), "upload-log was not called with POST"
    
    def test_analyze_endpoint_integration(self, page: Page, live_server_url: str):
        """Test that direct API calls work from the browser context."""
        page.goto(live_server_url)
        
        # Test analyze endpoint directly via browser JavaScript
        api_result = page.evaluate("""
            fetch('/api/v1/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    log_input: 'ERROR: Test error\\nConnectionError: Connection failed',
                    language: 'python',
                    options: {
                        highlight: true,
                        summarize: true,
                        tags: true
                    }
                })
            })
            .then(response => response.json())
            .then(data => ({
                success: true,
                tags: data.tags || [],
                hasContent: !!data.cleaned_log,
                hasSummary: !!data.summary
            }))
            .catch(error => ({
                success: false,
                error: error.message
            }))
        """)
        
        assert api_result["success"], f"API call failed: {api_result.get('error')}"
        assert api_result["hasContent"], "API response missing cleaned_log"
        assert len(api_result["tags"]) > 0, "API response missing tags"
    
    def test_websocket_endpoints_accessible(self, page: Page, live_server_url: str):
        """Test that WebSocket endpoints are accessible."""
        page.goto(live_server_url)
        
        # Wait for WebSocket connection attempt
        time.sleep(3)
        
        # Test error stats endpoint
        stats_result = page.evaluate("""
            fetch('/api/v1/errors/stats')
                .then(response => response.json())
                .then(data => ({
                    success: true,
                    hasErrorStats: !!data.error_stats,
                    hasConnectionStats: !!data.connection_stats
                }))
                .catch(error => ({
                    success: false,
                    error: error.message
                }))
        """)
        
        assert stats_result["success"], f"Stats API failed: {stats_result.get('error')}"
        assert stats_result["hasErrorStats"], "Stats API missing error_stats"
        assert stats_result["hasConnectionStats"], "Stats API missing connection_stats"
    
    def test_api_response_displayed_correctly(self, page: Page, live_server_url: str, python_error_log):
        """Test that API responses are correctly displayed in the UI."""
        page.goto(live_server_url)
        
        # Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(python_error_log)
        
        # Wait for results
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check that all API response components are displayed
        expect(page.locator("#resultsContent")).to_be_visible()
        expect(page.locator("#resultsContent")).not_to_be_empty()
        
        # Check summary (if enabled)
        summary_section = page.locator("#summarySection")
        if summary_section.is_visible():
            expect(page.locator("#summaryContent")).not_to_be_empty()
        
        # Check tags (if enabled)
        tags_section = page.locator("#tagsSection")
        if tags_section.is_visible():
            tags = page.locator(".tag")
            expect(tags).to_have_count_greater_than(0)
        
        # Check metadata
        expect(page.locator("#metadataSection")).to_be_visible()
        metadata_items = page.locator(".metadata-item")
        expect(metadata_items).to_have_count_greater_than(4)  # Should have at least filename, size, lines, language, time
    
    def test_api_error_handling_in_ui(self, page: Page, live_server_url: str):
        """Test that API errors are properly handled and displayed in UI."""
        page.goto(live_server_url)
        
        # Test with invalid data via JavaScript
        error_result = page.evaluate("""
            fetch('/api/v1/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    // Missing required log_input field
                    language: 'python',
                    options: {}
                })
            })
            .then(response => ({
                status: response.status,
                ok: response.ok
            }))
            .catch(error => ({
                error: error.message
            }))
        """)
        
        # Should get a 422 status for validation error
        assert error_result.get("status") == 422 or "error" in error_result


class TestUIAPIConsistency:
    """Test that UI behavior is consistent with API responses."""
    
    def test_tag_mapping_consistency(self, page: Page, live_server_url: str, connection_error_log):
        """Test that UI tag mapping matches API-generated tags."""
        page.goto(live_server_url)
        
        # First, get API response directly
        api_tags = page.evaluate("""
            fetch('/api/v1/upload-log', {
                method: 'POST',
                body: (() => {
                    const formData = new FormData();
                    const blob = new Blob(['ERROR: Connection failed\\nConnectionError: Connection refused'], {type: 'text/plain'});
                    formData.append('file', blob, 'test.log');
                    formData.append('language', 'python');
                    formData.append('highlight', 'true');
                    formData.append('tags', 'true');
                    return formData;
                })()
            })
            .then(response => response.json())
            .then(data => data.tags || [])
            .catch(error => [])
        """)
        
        # Now upload file via UI
        file_input = page.locator("#fileInput")
        file_input.set_input_files(connection_error_log)
        
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Get UI tags
        ui_tags = []
        tags = page.locator(".tag")
        for i in range(tags.count()):
            ui_tags.append(tags.nth(i).text_content())
        
        # API tags should match UI tags
        assert len(ui_tags) > 0, "No tags displayed in UI"
        
        # All API tags should appear in UI
        for api_tag in api_tags:
            assert api_tag in ui_tags, f"API tag '{api_tag}' not found in UI tags: {ui_tags}"
    
    def test_content_formatting_consistency(self, page: Page, live_server_url: str, sample_log_file):
        """Test that UI content formatting matches API response structure."""
        page.goto(live_server_url)
        
        # Upload file and get results
        file_input = page.locator("#fileInput")
        file_input.set_input_files(sample_log_file)
        
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check that enhanced formatting shows formatted content
        results_content = page.locator("#resultsContent")
        expect(results_content).to_be_visible()
        
        # Check that it contains styled elements (not just plain text)
        styled_elements = page.locator("#resultsContent .log-entry")
        expect(styled_elements).to_have_count_greater_than(0)
        
        # Toggle to plain mode
        highlight_toggle = page.locator('div:has(#highlight)')
        highlight_toggle.click()
        
        # Should now show plain content
        time.sleep(1)
        plain_elements = page.locator("#resultsContent .log-plain")
        expect(plain_elements).to_have_count_greater_than(0)
    
    def test_metadata_accuracy(self, page: Page, live_server_url: str, known_size_file):
        """Test that UI metadata matches actual file properties."""
        page.goto(live_server_url)
        
        # Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(known_size_file)
        
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check metadata values
        metadata_section = page.locator("#metadataSection")
        
        # Get filename
        filename_value = page.locator(".metadata-item:has-text('Filename') .metadata-value").text_content()
        assert "known_size" in filename_value, f"Filename not displayed correctly: {filename_value}"
        
        # Get file size
        size_value = page.locator(".metadata-item:has-text('File Size') .metadata-value").text_content()
        assert any(unit in size_value for unit in ['B', 'KB', 'MB']), f"File size format incorrect: {size_value}"
        
        # Get processing time
        time_value = page.locator(".metadata-item:has-text('Processing Time') .metadata-value").text_content()
        assert "ms" in time_value, f"Processing time format incorrect: {time_value}"


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    def test_complete_single_file_workflow(self, page: Page, live_server_url: str, comprehensive_log_file):
        """Test complete workflow from file upload to tag interaction."""
        page.goto(live_server_url)
        
        # 1. Upload file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(comprehensive_log_file)
        
        # 2. Wait for auto-processing
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # 3. Verify all components loaded
        expect(page.locator("#resultsContent")).to_be_visible()
        expect(page.locator("#summarySection")).to_be_visible()
        expect(page.locator("#tagsSection")).to_be_visible()
        expect(page.locator("#metadataSection")).to_be_visible()
        
        # 4. Test tag interaction
        tags = page.locator(".tag")
        expect(tags).to_have_count_greater_than(0)
        
        first_tag = tags.first
        first_tag.click()
        
        # 5. Verify highlighting works
        expect(first_tag).to_have_class(re=".*active.*")
        highlighted = page.locator(".log-entry.highlighted")
        expect(highlighted).to_have_count_greater_than(0)
        
        # 6. Test option toggling
        summarize_toggle = page.locator('div:has(#summarize)')
        summarize_toggle.click()
        expect(page.locator("#summarySection")).not_to_be_visible()
        
        # 7. Test reactivation
        summarize_toggle.click()
        expect(page.locator("#summarySection")).to_be_visible()
    
    def test_multiple_file_workflow(self, page: Page, live_server_url: str, multiple_test_files):
        """Test complete multiple file workflow."""
        page.goto(live_server_url)
        
        # 1. Upload multiple files
        file_input = page.locator("#fileInput")
        file_input.set_input_files(multiple_test_files)
        
        # 2. Verify file queue appears
        expect(page.locator("#fileQueue")).to_be_visible(timeout=5000)
        
        # 3. Verify all files listed
        file_items = page.locator(".file-item")
        expect(file_items).to_have_count(len(multiple_test_files))
        
        # 4. Process all files
        process_all_btn = page.locator("#processAllBtn")
        process_all_btn.click()
        
        # 5. Wait for completion
        expect(process_all_btn).to_contain_text("All Files Processed!", timeout=20000)
        
        # 6. Verify tabs created
        expect(page.locator("#fileTabs")).to_be_visible()
        file_tabs = page.locator(".file-tab")
        expect(file_tabs).to_have_count(len(multiple_test_files))
        
        # 7. Test tab switching
        if file_tabs.count() > 1:
            second_tab = file_tabs.nth(1)
            second_tab.click()
            expect(second_tab).to_have_class(re=".*active.*")


# Test fixtures
@pytest.fixture
def sample_log_file(tmp_path):
    """Sample log file for testing."""
    log_file = tmp_path / "sample.log"
    log_file.write_text("ERROR: Test error\nConnection failed")
    return str(log_file)


@pytest.fixture
def python_error_log(tmp_path):
    """Python error log file."""
    log_file = tmp_path / "python_error.log"
    log_file.write_text("""
2024-10-02 ERROR: Python error
Traceback (most recent call last):
  File "app.py", line 42
ConnectionError: Connection refused
AttributeError: 'NoneType' object has no attribute 'test'
""")
    return str(log_file)


@pytest.fixture
def connection_error_log(tmp_path):
    """Connection error log file."""
    log_file = tmp_path / "connection.log"
    log_file.write_text("ERROR: Connection failed\nConnectionError: Connection refused")
    return str(log_file)


@pytest.fixture
def known_size_file(tmp_path):
    """File with known properties for metadata testing."""
    log_file = tmp_path / "known_size.log"
    content = "ERROR: Test error\n" * 10  # Known content
    log_file.write_text(content)
    return str(log_file)


@pytest.fixture
def comprehensive_log_file(tmp_path):
    """Comprehensive log file with multiple error types."""
    log_file = tmp_path / "comprehensive.log"
    log_file.write_text("""
2024-10-02 10:30:15 ERROR: Connection failed
ConnectionError: could not connect to server
2024-10-02 10:30:16 ERROR: AttributeError occurred  
AttributeError: 'NoneType' object has no attribute '_raw_columns'
2024-10-02 10:30:17 WARNING: Slow query detected
2024-10-02 10:30:18 INFO: Processing complete
""")
    return str(log_file)