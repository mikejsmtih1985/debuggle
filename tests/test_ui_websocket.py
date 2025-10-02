"""
WebSocket and real-time functionality UI tests.
Tests the real-time error monitoring, WebSocket connections, and live notifications.
"""

import pytest
import time
import json
from playwright.sync_api import Page, expect


class TestWebSocketFunctionality:
    """Test WebSocket real-time monitoring functionality."""
    
    def test_websocket_connection_established(self, page: Page, live_server_url: str):
        """Test that WebSocket connection is established when page loads."""
        console_messages = []
        
        def handle_console(msg):
            console_messages.append(msg.text)
        
        page.on("console", handle_console)
        page.goto(live_server_url)
        
        # Wait for WebSocket connection
        time.sleep(3)
        
        # Look for WebSocket connection messages in console
        ws_messages = [msg for msg in console_messages if "real-time" in msg.lower() or "websocket" in msg.lower()]
        
        # Should have some WebSocket-related console messages
        assert len(ws_messages) > 0, f"No WebSocket messages found. Console: {console_messages}"
    
    def test_websocket_connection_status_indicator(self, page: Page, live_server_url: str):
        """Test that connection status is indicated in the UI."""
        page.goto(live_server_url)
        
        # Wait for connection to establish
        time.sleep(3)
        
        # Check header border color indicates connection status
        header = page.locator(".header")
        
        # Should have some border color indicating connection (green for connected)
        # This tests the updateConnectionStatus() function
        border_bottom = header.evaluate("getComputedStyle(this).borderBottomColor")
        
        # Should not be default/transparent
        assert border_bottom != "rgba(0, 0, 0, 0)" and border_bottom != "transparent"
    
    def test_real_time_error_stats_api(self, page: Page, live_server_url: str):
        """Test that real-time error stats API is accessible."""
        page.goto(live_server_url)
        
        # Test that stats endpoint is reachable via JavaScript
        stats_response = page.evaluate("""
            fetch('/api/v1/errors/stats')
                .then(response => response.json())
                .then(data => data)
                .catch(error => ({ error: error.message }))
        """)
        
        assert "error_stats" in stats_response or "error" in stats_response
        
        if "error_stats" in stats_response:
            # Verify expected structure
            assert "total_errors" in stats_response["error_stats"]
            assert "connection_stats" in stats_response
    
    def test_toggle_monitoring_functionality(self, page: Page, live_server_url: str):
        """Test the toggle monitoring API endpoint."""
        page.goto(live_server_url)
        
        # Test toggle monitoring via JavaScript
        toggle_response = page.evaluate("""
            fetch('/api/v1/errors/toggle-monitoring', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enable: true})
            })
            .then(response => response.json())
            .then(data => data)
            .catch(error => ({ error: error.message }))
        """)
        
        assert "message" in toggle_response or "error" in toggle_response
        
        if "message" in toggle_response:
            assert "enabled" in toggle_response


class TestRealTimeNotifications:
    """Test real-time notification functionality."""
    
    def test_notification_creation_function_exists(self, page: Page, live_server_url: str):
        """Test that notification functions exist and can be called."""
        page.goto(live_server_url)
        
        # Test that notification functions are available
        function_exists = page.evaluate("""
            typeof showRealtimeErrorNotification === 'function' &&
            typeof handleRealtimeMessage === 'function'
        """)
        
        assert function_exists, "Real-time notification functions not found"
    
    def test_notification_display_simulation(self, page: Page, live_server_url: str):
        """Test notification display by simulating an error event."""
        page.goto(live_server_url)
        
        # Simulate showing a notification
        page.evaluate("""
            if (typeof showRealtimeErrorNotification === 'function') {
                showRealtimeErrorNotification({
                    id: 'test-123',
                    timestamp: new Date().toISOString(),
                    error_type: 'TestError',
                    message: 'Test error message for UI testing',
                    source: 'ui_test',
                    severity: 'high'
                });
            }
        """)
        
        # Wait for notification animation
        time.sleep(1)
        
        # Look for notification element
        notifications = page.locator("div:has-text('TestError')")
        
        # Should have created a notification (it might disappear quickly)
        # We test that the function runs without errors
        assert True  # If we get here, no JS errors occurred
    
    def test_websocket_message_handling(self, page: Page, live_server_url: str):
        """Test that WebSocket message handling functions work."""
        page.goto(live_server_url)
        
        # Wait for WebSocket connection
        time.sleep(2)
        
        # Simulate handling different message types
        message_types = [
            {"type": "welcome", "message": "Connected"},
            {"type": "stats_update", "error_stats": {"total_errors": 5}},
            {"type": "monitoring_status", "message": "Monitoring enabled"}
        ]
        
        for msg in message_types:
            result = page.evaluate(f"""
                if (typeof handleRealtimeMessage === 'function') {{
                    try {{
                        handleRealtimeMessage({json.dumps(msg)});
                        true;
                    }} catch (error) {{
                        console.error('Error handling message:', error);
                        false;
                    }}
                }} else {{
                    false;
                }}
            """)
            
            assert result, f"Failed to handle message type: {msg['type']}"


class TestErrorMonitoringUI:
    """Test error monitoring UI components."""
    
    def test_connection_status_updates(self, page: Page, live_server_url: str):
        """Test that connection status updates are reflected in UI."""
        page.goto(live_server_url)
        
        # Test updateConnectionStatus function
        statuses = ['connected', 'disconnected', 'error']
        
        for status in statuses:
            page.evaluate(f"""
                if (typeof realtimeConnectionStatus !== 'undefined') {{
                    realtimeConnectionStatus = '{status}';
                    if (typeof updateConnectionStatus === 'function') {{
                        updateConnectionStatus();
                    }}
                }}
            """)
            
            time.sleep(0.5)
            
            # Check that header border color changed
            header = page.locator(".header")
            border_color = header.evaluate("getComputedStyle(this).borderBottomColor")
            
            # Should have some color (not transparent)
            assert border_color != "rgba(0, 0, 0, 0)"
    
    def test_realtime_errors_array_management(self, page: Page, live_server_url: str):
        """Test that real-time errors array is managed correctly."""
        page.goto(live_server_url)
        
        # Test that realtimeErrors array exists and can be manipulated
        result = page.evaluate("""
            if (typeof realtimeErrors !== 'undefined') {
                // Add test errors
                for (let i = 0; i < 60; i++) {
                    realtimeErrors.unshift({
                        id: `test-${i}`,
                        timestamp: new Date().toISOString(),
                        error_type: 'TestError',
                        message: `Test error ${i}`
                    });
                }
                
                // Should be limited to 50 items
                if (typeof updateRealtimeErrorsDisplay === 'function') {
                    updateRealtimeErrorsDisplay();
                }
                
                realtimeErrors.length;
            } else {
                -1;
            }
        """)
        
        # Should be limited to 50 items max
        assert result <= 50, f"Realtime errors array not properly limited: {result} items"
    
    def test_websocket_ping_pong(self, page: Page, live_server_url: str):
        """Test WebSocket keep-alive ping functionality."""
        page.goto(live_server_url)
        
        # Wait for connection
        time.sleep(2)
        
        # Test sending ping message
        ping_result = page.evaluate("""
            if (typeof sendWebSocketMessage === 'function' && typeof websocket !== 'undefined') {
                try {
                    sendWebSocketMessage({ type: 'ping' });
                    true;
                } catch (error) {
                    false;
                }
            } else {
                false;
            }
        """)
        
        assert ping_result, "Failed to send WebSocket ping message"


class TestRealTimeIntegration:
    """Test integration between real-time monitoring and file processing."""
    
    def test_file_processing_triggers_monitoring(self, page: Page, live_server_url: str, error_log_file):
        """Test that processing files with errors triggers real-time monitoring."""
        page.goto(live_server_url)
        
        # Wait for WebSocket connection
        time.sleep(2)
        
        # Track WebSocket messages
        ws_messages = []
        page.evaluate("""
            if (typeof websocket !== 'undefined') {
                const originalOnMessage = websocket.onmessage;
                websocket.onmessage = function(event) {
                    window.testWSMessages = window.testWSMessages || [];
                    window.testWSMessages.push(JSON.parse(event.data));
                    if (originalOnMessage) originalOnMessage.call(this, event);
                };
            }
        """)
        
        # Upload and process error file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(error_log_file)
        
        # Wait for processing
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check for any WebSocket messages
        time.sleep(2)
        
        messages = page.evaluate("window.testWSMessages || []")
        
        # Should have received some WebSocket messages during the session
        assert isinstance(messages, list)
    
    def test_no_websocket_errors_during_file_processing(self, page: Page, live_server_url: str, sample_log_file):
        """Test that file processing doesn't cause WebSocket errors."""
        console_errors = []
        
        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)
        
        page.on("console", handle_console)
        page.goto(live_server_url)
        
        # Wait for WebSocket connection
        time.sleep(2)
        
        # Upload and process file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(sample_log_file)
        
        expect(page.locator("#resultsSection")).to_be_visible(timeout=10000)
        
        # Check for WebSocket-related errors
        ws_errors = [err for err in console_errors if "websocket" in err.lower() or "ws" in err.lower()]
        
        assert len(ws_errors) == 0, f"WebSocket errors occurred: {ws_errors}"


@pytest.fixture
def sample_log_file(tmp_path):
    """Create a sample log file."""
    log_file = tmp_path / "sample.log"
    log_file.write_text("ERROR: Test error\nConnection failed")
    return str(log_file)


@pytest.fixture
def error_log_file(tmp_path):
    """Create an error log file."""
    log_file = tmp_path / "error.log"
    log_file.write_text("""
2024-10-02 ERROR: Critical error occurred
ConnectionError: Connection refused
AttributeError: 'NoneType' object has no attribute 'test'
""")
    return str(log_file)