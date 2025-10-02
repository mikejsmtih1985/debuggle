#!/usr/bin/env python3
"""
Test script to verify Debuggle server integration endpoints for VS Code extension.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class DebugglerServerTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_self_monitor_status(self) -> Dict[str, Any]:
        """Test the self-monitor status endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/self-monitor/status")
            response.raise_for_status()
            data = response.json()
            print(f"✓ Self-monitor status: {json.dumps(data, indent=2)}")
            return data
        except Exception as e:
            print(f"✗ Self-monitor status failed: {e}")
            return {}
    
    def test_toggle_monitoring(self, enabled: bool = True) -> bool:
        """Test toggling monitoring on/off."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/self-monitor/toggle",
                json={"enabled": enabled}
            )
            response.raise_for_status()
            data = response.json()
            print(f"✓ Toggle monitoring {'ON' if enabled else 'OFF'}: {data['message']}")
            return True
        except Exception as e:
            print(f"✗ Toggle monitoring failed: {e}")
            return False
    
    def test_clear_errors(self) -> bool:
        """Test clearing errors."""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/self-monitor/clear")
            response.raise_for_status()
            data = response.json()
            print(f"✓ Clear errors: {data['message']}")
            return True
        except Exception as e:
            print(f"✗ Clear errors failed: {e}")
            return False
    
    def test_generate_error(self) -> bool:
        """Test generating a test error."""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/self-monitor/test-error")
            response.raise_for_status()
            data = response.json()
            print(f"✓ Generate test error: {data['message']}")
            return True
        except Exception as e:
            print(f"✗ Generate test error failed: {e}")
            return False
    
    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection availability."""
        try:
            import websocket
            
            def on_message(ws, message):
                print(f"✓ WebSocket message received: {message}")
                ws.close()
            
            def on_error(ws, error):
                print(f"✗ WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print("✓ WebSocket connection closed")
            
            def on_open(ws):
                print("✓ WebSocket connection opened")
                # Send a test message after connecting
                time.sleep(1)
                
            ws_url = self.base_url.replace('http', 'ws') + '/ws'
            ws = websocket.WebSocketApp(ws_url,
                                      on_open=on_open,
                                      on_message=on_message,
                                      on_error=on_error,
                                      on_close=on_close)
            
            # Run for a short time to test connection
            ws.run_forever(timeout=5)
            return True
            
        except ImportError:
            print("✗ WebSocket test skipped (websocket-client not installed)")
            print("  Install with: pip install websocket-client")
            return False
        except Exception as e:
            print(f"✗ WebSocket test failed: {e}")
            return False
    
    def run_full_test(self):
        """Run complete integration test."""
        print("🔧 Testing Debuggle Server Integration for VS Code Extension")
        print("=" * 60)
        
        # Test basic endpoints
        print("\n1. Testing API Endpoints:")
        status_data = self.test_self_monitor_status()
        
        print("\n2. Testing Monitoring Control:")
        self.test_toggle_monitoring(True)
        time.sleep(1)
        
        print("\n3. Testing Error Generation:")
        self.test_generate_error()
        time.sleep(1)
        
        print("\n4. Checking Status After Error:")
        self.test_self_monitor_status()
        
        print("\n5. Testing Error Clearing:")
        self.test_clear_errors()
        
        print("\n6. Testing WebSocket Connection:")
        self.test_websocket_connection()
        
        print("\n✅ Integration test completed!")
        print("\n📋 VS Code Extension Setup Instructions:")
        print("1. Open VS Code in the debuggle project directory")
        print("2. Go to Extensions (Ctrl+Shift+X)")
        print("3. Install the extension from vscode-extension/ folder")
        print("4. Use Ctrl+Shift+P and search for 'Debuggle' commands")
        print("5. Try 'Debuggle: Show Monitoring Dashboard'")


if __name__ == "__main__":
    # Get server URL from command line or use default
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    tester = DebugglerServerTest(server_url)
    tester.run_full_test()