#!/usr/bin/env python3
"""
Debuggle UI Test Runner
Comprehensive test runner for UI tests with server management and reporting.
"""

import subprocess
import sys
import time
import signal
import os
import argparse
from pathlib import Path


class DebugglerTestRunner:
    def __init__(self):
        self.server_process = None
        self.project_root = Path(__file__).parent
        
    def start_server(self):
        """Start Debuggle server for testing."""
        print("🚀 Starting Debuggle server...")
        
        # Change to project root
        os.chdir(self.project_root)
        
        # Start server
        self.server_process = subprocess.Popen(
            [sys.executable, "entry_point.py", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "PYTHONPATH": str(self.project_root / "src")}
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Check if server started successfully
        if self.server_process.poll() is not None:
            stdout, stderr = self.server_process.communicate()
            print(f"❌ Server failed to start!")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
        
        # Test server is responding
        try:
            import requests
            response = requests.get("http://localhost:8000", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully on http://localhost:8000")
                return True
        except Exception as e:
            print(f"❌ Server not responding: {e}")
            return False
        
        return False
    
    def stop_server(self):
        """Stop the Debuggle server."""
        if self.server_process:
            print("🛑 Stopping server...")
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            print("✅ Server stopped")
    
    def run_ui_tests(self, test_args=None):
        """Run UI tests with pytest."""
        if test_args is None:
            test_args = []
            
        print("🧪 Running UI tests...")
        
        # Base pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_ui_*.py",
            "-v",
            "--tb=short",
            "--color=yes"
        ]
        
        # Add custom arguments
        cmd.extend(test_args)
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
            return False
    
    def setup_environment(self):
        """Set up test environment."""
        print("⚙️ Setting up test environment...")
        
        # Install dependencies if needed
        try:
            import playwright
            print("✅ Playwright already installed")
        except ImportError:
            print("📦 Installing Playwright...")
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright>=1.40.0", "pytest-playwright>=0.4.3"])
            
        # Install browsers
        print("🌐 Installing/updating browser binaries...")
        try:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "firefox"], check=True)
            print("✅ Browsers installed")
        except subprocess.CalledProcessError:
            print("⚠️ Browser installation failed, but continuing...")
        
        return True
    
    def run_specific_test_category(self, category):
        """Run specific category of tests."""
        category_args = {
            "basic": ["tests/test_ui_basic.py"],
            "tags": ["tests/test_ui_tags.py"],
            "upload": ["tests/test_ui_file_upload.py"],
            "websocket": ["tests/test_ui_websocket.py"],
            "integration": ["tests/test_ui_api_integration.py"],
            "fast": ["-m", "ui and not slow"],
            "slow": ["-m", "slow"],
        }
        
        if category not in category_args:
            print(f"❌ Unknown test category: {category}")
            print(f"Available categories: {', '.join(category_args.keys())}")
            return False
        
        return self.run_ui_tests(category_args[category])
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("📊 Generating test report...")
        
        report_args = [
            "--html=test-results/ui-test-report.html",
            "--self-contained-html",
            "--cov=src/debuggle",
            "--cov-report=html:test-results/coverage"
        ]
        
        return self.run_ui_tests(report_args)


def main():
    parser = argparse.ArgumentParser(description="Debuggle UI Test Runner")
    parser.add_argument("--category", "-c", help="Test category to run", 
                       choices=["basic", "tags", "upload", "websocket", "integration", "fast", "slow"])
    parser.add_argument("--no-server", action="store_true", help="Don't start/stop server (assume it's running)")
    parser.add_argument("--setup", action="store_true", help="Set up test environment only")
    parser.add_argument("--report", action="store_true", help="Generate detailed HTML report")
    parser.add_argument("--headed", action="store_true", help="Run tests with visible browser")
    parser.add_argument("--debug", action="store_true", help="Run with debugging options")
    
    args = parser.parse_args()
    
    runner = DebugglerTestRunner()
    
    # Handle setup mode
    if args.setup:
        return 0 if runner.setup_environment() else 1
    
    # Set up signal handler for cleanup
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal, cleaning up...")
        runner.stop_server()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Setup environment
        if not runner.setup_environment():
            return 1
        
        # Start server unless told not to
        if not args.no_server:
            if not runner.start_server():
                print("❌ Failed to start server")
                return 1
        
        # Prepare test arguments
        test_args = []
        if args.headed:
            test_args.append("--headed")
        if args.debug:
            test_args.extend(["--pdb", "--log-cli-level=DEBUG"])
        if args.report:
            test_args.extend([
                "--html=test-results/ui-test-report.html",
                "--self-contained-html"
            ])
        
        # Run tests
        success = False
        if args.category:
            success = runner.run_specific_test_category(args.category)
        else:
            success = runner.run_ui_tests(test_args)
        
        if success:
            print("✅ All UI tests passed!")
            if args.report:
                print("📊 Test report generated: test-results/ui-test-report.html")
            return 0
        else:
            print("❌ Some UI tests failed")
            return 1
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    finally:
        # Always clean up
        if not args.no_server:
            runner.stop_server()


if __name__ == "__main__":
    sys.exit(main())