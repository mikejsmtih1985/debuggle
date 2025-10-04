#!/usr/bin/env python3
"""
🚀 DEBUGGLE ONE-CLICK INSTALLER
Installs Debuggle with all Pro tier dependencies for viral demos.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command with pretty output."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🚀 DEBUGGLE INSTALLER")
    print("=" * 40)
    print("Installing Debuggle with Pro tier features...")
    print("Perfect for viral demos and serious debugging!\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Please upgrade Python.")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    success = True
    
    # Core dependencies
    success &= run_command(
        "pip install fastapi uvicorn pydantic pydantic-settings", 
        "Installing FastAPI core"
    )
    
    # Processing dependencies  
    success &= run_command(
        "pip install pygments rich langdetect",
        "Installing log processing tools"
    )
    
    # Pro tier dependencies
    success &= run_command(
        "pip install whoosh aiofiles aiohttp aiosmtplib",
        "Installing Pro tier features (search, analytics)"
    )
    
    # Development dependencies
    success &= run_command(
        "pip install pytest pytest-asyncio pytest-cov httpx",
        "Installing testing framework"
    )
    
    if success:
        print("\n🎉 INSTALLATION COMPLETE!")
        print("=" * 40)
        print("Ready to blow minds with Debuggle!")
        print("\n🚀 Try the viral demo:")
        print("   python examples/viral_demo.py")
        print("\n💡 Analyze your first error:")
        print("   python cli/debuggle_cli.py < your_error.log")
        print("\n📚 Read the docs:")
        print("   cat README.md")
        print("\n🌟 Star us on GitHub!")
        print("   https://github.com/mikejsmtih1985/debuggle")
    else:
        print("\n❌ Installation had issues. Check the errors above.")
        print("💡 Try: pip install --upgrade pip")
        print("💡 Or: pip install -r requirements.txt")

if __name__ == "__main__":
    main()