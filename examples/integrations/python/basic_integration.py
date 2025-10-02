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
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def process_log(self, content: str, language: str = "auto", highlight: bool = True, 
                   summarize: bool = True, tags: bool = True) -> Dict[str, Any]:
        """Process a single log entry using the beautify endpoint"""
        url = f"{self.base_url}/api/v1/beautify"
        data = {
            "log_input": content,
            "language": language,
            "options": {
                "highlight": highlight,
                "summarize": summarize,
                "tags": tags,
                "max_lines": 1000
            }
        }
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}
    
    def upload_file(self, file_path: str, language: str = "auto", highlight: bool = True,
                   summarize: bool = True, tags: bool = True) -> Dict[str, Any]:
        """Upload and process a log file"""
        url = f"{self.base_url}/api/v1/upload-log"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'language': language,
                    'highlight': highlight,
                    'summarize': summarize,
                    'tags': tags,
                    'max_lines': 1000
                }
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
        result = client.process_log(log_entry)
        if 'cleaned_log' in result:
            print(f"✅ {result['cleaned_log'][:100]}...")  # Show first 100 chars
            if result.get('summary'):
                print(f"   Summary: {result['summary'][:50]}...")
        else:
            print(f"❌ Failed to process: {result}")
    
    # Example 2: Process with different options
    print("\n⚙️ Testing different processing options...")
    
    test_log = "2025-01-01 12:00:00 ERROR: Critical system failure"
    
    options = [
        {"name": "Full Analysis", "highlight": True, "summarize": True, "tags": True},
        {"name": "Basic Clean", "highlight": False, "summarize": False, "tags": False},
        {"name": "Summary Only", "highlight": False, "summarize": True, "tags": False}
    ]
    
    for option in options:
        result = client.process_log(test_log, **{k: v for k, v in option.items() if k != "name"})
        if 'cleaned_log' in result:
            print(f"✅ [{option['name']}] Processing successful")
            if result.get('summary'):
                print(f"   Summary: {result['summary'][:80]}...")
        else:
            print(f"❌ [{option['name']}] Failed: {result}")
    
    # Example 3: File upload (if sample file exists)
    print("\n📁 Testing file upload...")
    
    sample_file = "../sample_logs/application.log"
    try:
        result = client.upload_file(sample_file)
        if 'cleaned_log' in result:
            print(f"✅ File processed: {result['metadata']['filename']}")
            print(f"   File size: {result['metadata']['file_size']} bytes")
            print(f"   Processing time: {result['metadata'].get('processing_time', 'N/A')}s")
            if result.get('summary'):
                print(f"   Summary: {result['summary'][:100]}...")
        else:
            print(f"❌ File upload failed: {result}")
    except FileNotFoundError:
        print("⚠️  Sample file not found, skipping file upload test")
    
    print("\n🎉 Integration example completed!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)