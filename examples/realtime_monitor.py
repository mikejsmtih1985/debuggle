#!/usr/bin/env python3
"""
WebSocket client test for real-time error monitoring.
This demonstrates how to connect to the real-time error stream.
"""

import asyncio
import websockets
import json
import sys

async def monitor_realtime_errors():
    """Connect to the real-time error monitoring WebSocket."""
    uri = "ws://localhost:8000/ws/errors"
    
    try:
        print("🔌 Connecting to real-time error monitoring...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected! Monitoring for real-time errors...")
            print("📡 WebSocket URL:", uri)
            print("-" * 50)
            
            # Send a ping to test connection
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "welcome":
                        print("👋 Welcome message received")
                        print(f"   Message: {data.get('message')}")
                        print(f"   Recent errors: {len(data.get('recent_errors', []))}")
                        
                    elif data.get("type") == "error":
                        print("🚨 NEW ERROR DETECTED!")
                        print(f"   Type: {data.get('error_type')}")
                        print(f"   Message: {data.get('message')}")
                        print(f"   Source: {data.get('source')}")
                        print(f"   Severity: {data.get('severity')}")
                        print(f"   Time: {data.get('timestamp')}")
                        print(f"   Metadata: {data.get('metadata', {})}")
                        print("-" * 50)
                        
                    elif data.get("type") == "pong":
                        print("🏓 Pong received - connection alive")
                        
                    elif data.get("type") == "stats_update":
                        print("📊 Stats updated")
                        print(f"   Error stats: {data.get('error_stats', {})}")
                        
                    elif data.get("type") == "monitoring_status":
                        print("⚙️ Monitoring status changed")
                        print(f"   Status: {data.get('message')}")
                        
                    else:
                        print(f"📝 Message: {data}")
                        
                except json.JSONDecodeError:
                    print(f"⚠️  Invalid JSON received: {message}")
                    
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the Debuggle server running?")
        print("   Start it with: python entry_point.py serve")
        return False
    except KeyboardInterrupt:
        print("\n👋 Disconnecting from real-time monitoring...")
        return True
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def test_error_reporting():
    """Simulate error reporting to test the real-time stream."""
    import urllib.request
    import urllib.parse
    
    test_errors = [
        {
            "log_input": "IndexError: list index out of range\nTraceback...",
            "language": "python"
        },
        {
            "log_input": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
            "language": "python"
        },
        {
            "log_input": "NullPointerException at line 42",
            "language": "java"
        }
    ]
    
    print("🧪 Testing error reporting...")
    print("   (Use curl in another terminal to send errors)")
    print("   Example: curl -X POST http://localhost:8000/api/v1/beautify \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"log_input\": \"IndexError: test error\", \"language\": \"python\"}'")
    print("   Monitoring will show any errors that occur...")
    
    # Just wait and let user send requests manually
    await asyncio.sleep(60)

async def main():
    """Main function to run the WebSocket client."""
    print("🐞 Debuggle Real-Time Error Monitor")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run in test mode - simulate errors
        print("🧪 TEST MODE: Will generate test errors")
        
        # Start monitoring in background
        monitor_task = asyncio.create_task(monitor_realtime_errors())
        
        # Wait a bit then send test errors
        await asyncio.sleep(2)
        await test_error_reporting()
        
        # Wait for monitoring to finish
        await monitor_task
        
    else:
        # Normal monitoring mode
        print("📡 MONITOR MODE: Listening for real-time errors")
        print("   Press Ctrl+C to stop")
        await monitor_realtime_errors()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")