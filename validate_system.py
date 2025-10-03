#!/usr/bin/env python3
"""
🔍 Debuggle System Validation - Pre-Installation Checker
Validates system requirements before installation to prevent common issues.
"""

import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("✅ Python version compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        print("   Install Python 3.8+ from https://python.org")
        return False

def check_node_version():
    """Check Node.js version for VS Code extension."""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"📦 Node.js {version}")
            
            # Parse version (format: v18.19.1)
            major_minor = version[1:].split('.')[:2]  # Remove 'v' and get major.minor
            major, minor = int(major_minor[0]), int(major_minor[1])
            
            if major >= 18 and minor >= 19:
                print("✅ Node.js version compatible")
                return True
            else:
                print("⚠️  Node.js 18.19+ recommended for VS Code extension")
                print("   VS Code extension may have packaging issues with older versions")
                return "warning"
        else:
            print("❌ Node.js not found")
            print("   Install from https://nodejs.org for VS Code extension support")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        print("   Install from https://nodejs.org for VS Code extension support")
        return False

def check_git():
    """Check Git availability."""
    if shutil.which('git'):
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"📚 {version}")
                print("✅ Git available (enables project context analysis)")
                return True
        except:
            pass
    
    print("⚠️  Git not found")
    print("   Install Git for enhanced project context analysis")
    print("   Debuggle will work without Git but with limited context")
    return "warning"

def check_vscode():
    """Check VS Code availability."""
    if shutil.which('code'):
        try:
            result = subprocess.run(['code', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"📝 VS Code {version}")
                print("✅ VS Code available (enables real-time integration)")
                return True
        except:
            pass
    
    print("⚠️  VS Code not found")
    print("   Install VS Code for real-time error monitoring integration")
    print("   Debuggle CLI and web interface will work without VS Code")
    return "warning"

def check_java():
    """Check Java availability (optional)."""
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0] if result.stderr else result.stdout.split('\n')[0]
            print(f"☕ {version_line}")
            print("✅ Java available (enables multi-language analysis)")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("ℹ️  Java not found (optional)")
    print("   Install Java for enhanced multi-language project analysis")
    return "optional"

def check_virtual_environment():
    """Check if running in virtual environment."""
    in_venv = (hasattr(sys, 'real_prefix') or 
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
    
    if in_venv:
        venv_path = sys.prefix
        print(f"🏠 Virtual environment: {venv_path}")
        print("✅ Running in virtual environment (recommended)")
        return True
    else:
        print("⚠️  Not in virtual environment")
        print("   Recommended: python -m venv .venv && source .venv/bin/activate")
        return "warning"

def check_disk_space():
    """Check available disk space."""
    current_path = Path.cwd()
    try:
        stat = shutil.disk_usage(current_path)
        free_gb = stat.free / (1024**3)
        print(f"💾 Available disk space: {free_gb:.1f} GB")
        
        if free_gb >= 1.0:
            print("✅ Sufficient disk space")
            return True
        else:
            print("⚠️  Low disk space (< 1GB available)")
            return "warning"
    except:
        print("ℹ️  Could not check disk space")
        return "unknown"

def main():
    """Run comprehensive system validation."""
    print("🔍 DEBUGGLE SYSTEM VALIDATION")
    print("=" * 40)
    print("Checking system requirements before installation...\n")
    
    checks = []
    
    # Critical requirements
    print("🎯 CRITICAL REQUIREMENTS:")
    checks.append(("Python 3.8+", check_python_version()))
    
    print("\n📦 VS CODE EXTENSION REQUIREMENTS:")
    checks.append(("Node.js 18.19+", check_node_version()))
    checks.append(("VS Code", check_vscode()))
    
    print("\n🔧 ENHANCED FEATURES:")
    checks.append(("Git", check_git()))
    checks.append(("Java", check_java()))
    
    print("\n🏠 ENVIRONMENT:")
    checks.append(("Virtual Environment", check_virtual_environment()))
    checks.append(("Disk Space", check_disk_space()))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 VALIDATION SUMMARY:")
    
    critical_issues = 0
    warnings = 0
    
    for name, result in checks:
        if result is True:
            status = "✅ PASS"
        elif result == "warning":
            status = "⚠️  WARNING"
            warnings += 1
        elif result == "optional":
            status = "ℹ️  OPTIONAL"
        else:
            status = "❌ FAIL"
            critical_issues += 1
        
        print(f"  {name:<20} {status}")
    
    print("\n🎯 RECOMMENDATIONS:")
    
    if critical_issues == 0:
        print("✅ System ready for Debuggle installation!")
        if warnings > 0:
            print("⚠️  Some warnings found - Debuggle will work but some features may be limited")
        print("\n🚀 Next steps:")
        print("   1. python install.py")
        print("   2. python entry_point.py serve")
        print("   3. Open VS Code → Load vscode-extension folder → Press F5")
        return True
    else:
        print("❌ Critical issues found - please resolve before installation")
        print("\n🛠️  Fix critical issues, then run this validator again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)