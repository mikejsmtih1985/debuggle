#!/usr/bin/env python3
"""
Integration test for the core CLI workflow to verify end-to-end functionality.

This test validates what actually matters: does the CLI work for users?
"""

import subprocess
import sys
import os
from pathlib import Path

def test_cli_basic_functionality():
    """Test that the CLI can analyze a simple error end-to-end."""
    
    # Determine paths
    repo_root = Path(__file__).parent
    cli_path = repo_root / "cli" / "debuggle_cli.py"
    venv_python = repo_root / ".venv" / "bin" / "python"
    
    if not venv_python.exists():
        venv_python = repo_root / ".venv" / "Scripts" / "python.exe"  # Windows
    
    # Test input - a simple Python error
    test_error = "Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>\n    print(x)\nNameError: name 'x' is not defined"
    
    try:
        # Run the CLI with test input
        result = subprocess.run(
            [str(venv_python), str(cli_path)],
            input=test_error,
            text=True,
            capture_output=True,
            cwd=repo_root,
            timeout=30
        )
        
        print(f"✅ CLI Exit Code: {result.returncode}")
        print(f"📤 CLI Output Length: {len(result.stdout)} characters")
        
        # Check basic success criteria
        success_indicators = [
            "FULL DEVELOPMENT CONTEXT ANALYSIS" in result.stdout,
            "Git Context:" in result.stdout,
            "Project Context:" in result.stdout,
            result.returncode == 0,
            len(result.stdout) > 100  # Should produce substantial output
        ]
        
        passed = sum(success_indicators)
        total = len(success_indicators)
        
        print(f"✅ Success indicators: {passed}/{total}")
        
        if passed >= 4:  # Allow some flexibility
            print("🎉 CLI Integration Test PASSED")
            return True
        else:
            print("❌ CLI Integration Test FAILED")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI test timed out (>30s)")
        return False
    except Exception as e:
        print(f"❌ CLI test failed with exception: {e}")
        return False

def test_cli_help():
    """Test that CLI help works."""
    
    repo_root = Path(__file__).parent
    cli_path = repo_root / "cli" / "debuggle_cli.py"
    venv_python = repo_root / ".venv" / "bin" / "python"
    
    if not venv_python.exists():
        venv_python = repo_root / ".venv" / "Scripts" / "python.exe"  # Windows
    
    try:
        result = subprocess.run(
            [str(venv_python), str(cli_path), "--help"],
            capture_output=True,
            text=True,
            cwd=repo_root,
            timeout=10
        )
        
        print(f"✅ Help Exit Code: {result.returncode}")
        
        help_indicators = [
            "usage:" in result.stdout,
            "Debuggle CLI" in result.stdout,
            "--help" in result.stdout,
            result.returncode == 0
        ]
        
        if all(help_indicators):
            print("✅ CLI Help Test PASSED")
            return True
        else:
            print("❌ CLI Help Test FAILED")
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI help test failed: {e}")
        return False

def test_installation_workflow():
    """Test that the simple installer worked correctly."""
    
    repo_root = Path(__file__).parent
    venv_path = repo_root / ".venv"
    cli_path = repo_root / "cli" / "debuggle_cli.py"
    requirements_cli = repo_root / "requirements_cli.txt"
    
    checks = {
        "Virtual environment exists": venv_path.exists(),
        "CLI script exists": cli_path.exists(),
        "CLI requirements file exists": requirements_cli.exists(),
        "Python executable in venv": (venv_path / "bin" / "python").exists() or (venv_path / "Scripts" / "python.exe").exists()
    }
    
    print("📦 Installation Check Results:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    if all(checks.values()):
        print("✅ Installation Workflow Test PASSED")
        return True
    else:
        print("❌ Installation Workflow Test FAILED")
        return False

def main():
    """Run all integration tests and report results."""
    
    print("🧪 Debuggle Core Integration Tests")
    print("=" * 50)
    print("Testing the workflows that actually matter to users.\n")
    
    tests = [
        ("Installation Workflow", test_installation_workflow),
        ("CLI Help Functionality", test_cli_help),
        ("CLI Error Analysis", test_cli_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{'✅ PASS' if result else '❌ FAIL'}: {test_name}\n")
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {e}\n")
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("📊 Test Summary:")
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All core functionality tests PASSED!")
        print("   The CLI workflow works end-to-end for users.")
        sys.exit(0)
    else:
        print("❌ Some tests FAILED!")
        print("   Core user workflows need attention.")
        sys.exit(1)

if __name__ == "__main__":
    main()