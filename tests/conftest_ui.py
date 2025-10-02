"""
Pytest configuration for UI tests.
Configures Playwright integration and provides common fixtures for UI testing.
"""

import pytest
import asyncio
import subprocess
import time
import sys
from pathlib import Path

# Pytest Playwright integration
pytest_plugins = ["pytest_playwright"]


@pytest.fixture(scope="session")
def debuggle_server():
    """Start Debuggle server for testing and clean up afterwards."""
    import os
    import signal
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Start server process
    process = subprocess.Popen(
        [sys.executable, "entry_point.py", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONPATH": str(project_root / "src")}
    )
    
    # Wait for server to start
    time.sleep(3)
    
    # Check if server is running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        pytest.fail(f"Server failed to start. STDOUT: {stdout.decode()}, STDERR: {stderr.decode()}")
    
    yield "http://localhost:8000"
    
    # Cleanup
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


@pytest.fixture
def live_server_url(debuggle_server):
    """Provide the live server URL."""
    return debuggle_server


@pytest.fixture(scope="session") 
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def test_log_file(tmp_path):
    """Create a test log file for UI tests."""
    log_file = tmp_path / "test.log"
    log_file.write_text("""
2024-10-02 10:30:15 ERROR: Test error occurred
Traceback (most recent call last):
  File "app.py", line 42, in test_function
    connection = database.connect()
ConnectionError: could not connect to server
AttributeError: 'NoneType' object has no attribute '_raw_columns'
2024-10-02 10:30:16 WARNING: Slow query detected
2024-10-02 10:30:17 INFO: Retrying connection...
""")
    return str(log_file)


@pytest.fixture 
def multiple_test_files(tmp_path):
    """Create multiple test files for testing multiple file upload."""
    files = []
    for i in range(3):
        log_file = tmp_path / f"test_{i}.log"
        log_file.write_text(f"""
2024-10-02 ERROR: Error in file {i}
ConnectionError: Connection failed in test {i}
AttributeError: Error {i} occurred
""")
        files.append(str(log_file))
    return files


# Playwright-specific configurations
def pytest_configure(config):
    """Configure pytest for UI testing."""
    # Add markers for UI tests
    config.addinivalue_line(
        "markers", "ui: mark test as a UI test requiring browser"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "websocket: mark test as requiring WebSocket functionality"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark all UI tests
        if "test_ui_" in item.nodeid:
            item.add_marker(pytest.mark.ui)
        
        # Mark WebSocket tests as slow
        if "websocket" in item.nodeid.lower():
            item.add_marker(pytest.mark.websocket)
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # This runs before each test
    yield
    # This runs after each test (cleanup if needed)
    pass


# Custom assertion helpers for UI tests
def assert_no_javascript_errors(page):
    """Helper function to assert no JavaScript errors occurred."""
    # This would be implemented to check console errors
    pass


def assert_element_visible_with_text(page, selector, text):
    """Helper function to assert element is visible and contains text."""
    from playwright.sync_api import expect
    element = page.locator(selector)
    expect(element).to_be_visible()
    expect(element).to_contain_text(text)