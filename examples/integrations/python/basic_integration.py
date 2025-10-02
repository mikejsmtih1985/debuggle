#!/usr/bin/env python3
"""
Basic Python integration example for Debuggle

This example shows how to integrate Debuggle log processing
into a Python application.
"""

import requests
import json
import sys
from typing import Optional, Dict, Any


class DebuggleClient:
    """Simple Debuggle API client"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def process_log(self, content: str, tier: str = "core") -> Dict[str, Any]:
        """Process a single log entry"""
        url = f"{self.base_url}/debuggle-log"
        data = {
            "content": content,
            "tier": tier
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def upload_file(self, file_path: str, tier: str = "core") -> Dict[str, Any]:
        """Upload and process a log file"""
        url = f"{self.base_url}/upload-file"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'tier': tier}
                response = self.session.post(url, files=files, data=data)
                response.raise_for_status()
                return response.json()
        except (requests.exceptions.RequestException, IOError) as e:
            return {"error": str(e), "success": False}
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        url = f"{self.base_url}/health"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "unhealthy"}


def main():
    """Main example function"""
    
    # Initialize client
    client = DebuggleClient()
    
    # Check API health
    print("🏥 Checking API health...")
    health = client.health_check()
    if health.get("status") == "healthy":
        print("✅ API is healthy")
    else:
        print("❌ API health check failed:", health.get("error"))
        return 1
    
    # Example 1: Process simple log entries
    print("\n📝 Processing simple log entries...")
    
    sample_logs = [
        "2025-01-01 12:00:00 INFO: Application started",
        "2025-01-01 12:00:01 ERROR: Database connection failed",
        "2025-01-01 12:00:02 WARN: High memory usage detected",
        "2025-01-01 12:00:03 DEBUG: Processing user request"
    ]
    
    for log_entry in sample_logs:
        result = client.process_log(log_entry, tier="core")
        if result.get("success"):
            print(f"✅ {result['processed_content']}")
        else:
            print(f"❌ Failed to process: {result.get('error')}")
    
    # Example 2: Process with different tiers
    print("\n🏆 Testing different service tiers...")
    
    tiers = ["core", "pro", "team"]
    test_log = "2025-01-01 12:00:00 ERROR: Critical system failure"
    
    for tier in tiers:
        result = client.process_log(test_log, tier=tier)
        if result.get("success"):
            print(f"✅ [{tier.upper()}] {result['processed_content']}")
        else:
            print(f"❌ [{tier.upper()}] Failed: {result.get('error')}")
    
    # Example 3: File upload (if sample file exists)
    print("\n📁 Testing file upload...")
    
    sample_file = "../../logs/application.log"
    try:
        result = client.upload_file(sample_file, tier="pro")
        if result.get("success"):
            print(f"✅ File processed: {result['filename']}")
            print(f"   Lines processed: {result.get('lines_processed', 'N/A')}")
            print(f"   Processing time: {result.get('processing_time', 'N/A')}s")
        else:
            print(f"❌ File upload failed: {result.get('error')}")
    except FileNotFoundError:
        print("⚠️  Sample file not found, skipping file upload test")
    
    print("\n🎉 Integration example completed!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)