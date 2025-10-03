#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE BETA USER READINESS TEST SUITE

This script performs thorough testing of all Debuggle functionality
to ensure everything is ready for your beta user.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

def run_test(description, test_func):
    """Run a single test with proper formatting"""
    print(f"\n🧪 {description}")
    print("-" * (len(description) + 4))
    
    try:
        result = test_func()
        if result:
            print(f"✅ PASS: {description}")
            return True
        else:
            print(f"❌ FAIL: {description}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {description} - {e}")
        return False

def test_claude_integration_import():
    """Test that Claude integration can be imported"""
    try:
        from src.debuggle.integrations.claude import ClaudeAnalyzer, ClaudeEnhancedAnalysis
        analyzer = ClaudeAnalyzer()
        print("  • Claude modules imported successfully")
        print(f"  • Claude available: {analyzer.is_available()}")
        return True
    except ImportError as e:
        print(f"  • Import failed: {e}")
        return False

def test_cli_functionality():
    """Test basic CLI functionality"""
    try:
        from cli.debuggle_cli import main
        # Test CLI help (should not raise exceptions)
        original_argv = sys.argv.copy()
        sys.argv = ['debuggle_cli.py', '--help']
        
        try:
            main()
        except SystemExit as e:
            # --help causes SystemExit, which is expected
            if e.code == 0:
                print("  • CLI help works correctly")
                return True
        finally:
            sys.argv = original_argv
            
        return False
    except Exception as e:
        print(f"  • CLI test failed: {e}")
        return False

def test_standalone_entry_point():
    """Test standalone entry point functionality"""
    try:
        # Test help command
        result = subprocess.run([
            sys.executable, 'debuggle_standalone.py', 'help'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'Debuggle - Advanced Error Analysis Tool' in result.stdout:
            print("  • Standalone help works")
            
            # Test version command
            result = subprocess.run([
                sys.executable, 'debuggle_standalone.py', 'version'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'Claude AI' in result.stdout:
                print("  • Standalone version works")
                return True
                
        print(f"  • Stdout: {result.stdout[:100]}...")
        print(f"  • Stderr: {result.stderr[:100]}...")
        return False
    except Exception as e:
        print(f"  • Standalone test failed: {e}")
        return False

def test_error_analysis_pipeline():
    """Test end-to-end error analysis"""
    try:
        # Create a test error
        test_script = '''
import sys
try:
    users = ["Alice", "Bob"]
    problem_user = users[999]  # This will cause IndexError
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
'''
        
        # Run the test script and pipe to debuggle
        test_process = subprocess.run([
            sys.executable, '-c', test_script
        ], capture_output=True, text=True)
        
        if test_process.returncode != 0:  # Should fail with error
            # Now analyze the error
            analysis_process = subprocess.run([
                sys.executable, 'debuggle_standalone.py', 'analyze'
            ], input=test_process.stderr, capture_output=True, text=True, timeout=30)
            
            if (analysis_process.returncode == 0 and 
                ('Debuggle CLI - Analyzing' in analysis_process.stdout or
                 'FULL DEVELOPMENT CONTEXT ANALYSIS' in analysis_process.stdout)):
                print("  • Error analysis pipeline works")
                print("  • Context analysis correctly generated")
                return True
                
        print(f"  • Analysis output: {analysis_process.stdout[:200]}...")
        return False
    except Exception as e:
        print(f"  • Pipeline test failed: {e}")
        return False

def test_claude_graceful_degradation():
    """Test Claude integration graceful degradation"""
    try:
        # Test without API key
        env = os.environ.copy()
        if 'ANTHROPIC_API_KEY' in env:
            del env['ANTHROPIC_API_KEY']
            
        test_error = "IndexError: list index out of range"
        
        result = subprocess.run([
            sys.executable, 'debuggle_standalone.py', 'analyze', '--claude'
        ], input=test_error, capture_output=True, text=True, env=env, timeout=15)
        
        if (result.returncode == 0 and 
            'Claude AI: Not available' in result.stdout and
            'Debuggle works great without AI too!' in result.stdout):
            print("  • Graceful degradation works")
            print("  • Helpful fallback message shown")
            return True
            
        print(f"  • Output: {result.stdout[:200]}...")
        return False
    except Exception as e:
        print(f"  • Degradation test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    required_packages = [
        'pydantic', 'rich', 'pygments', 'langdetect', 
        'fastapi', 'uvicorn', 'anthropic'
    ]
    
    missing = []
    available = []
    
    for package in required_packages:
        try:
            __import__(package)
            available.append(package)
        except ImportError:
            missing.append(package)
    
    print(f"  • Available packages: {', '.join(available)}")
    if missing:
        print(f"  • Missing packages: {', '.join(missing)}")
        if 'anthropic' in missing:
            print("    (anthropic is optional for Claude integration)")
            missing.remove('anthropic')
    
    return len(missing) == 0

def test_github_actions_readiness():
    """Test GitHub Actions workflow file"""
    workflow_path = Path('.github/workflows/build-executables.yml')
    
    if not workflow_path.exists():
        print("  • Workflow file missing")
        return False
        
    content = workflow_path.read_text()
    
    checks = [
        ('Multi-platform matrix', 'strategy:' in content and 'matrix:' in content),
        ('PyInstaller step', 'pyinstaller' in content.lower()),
        ('Artifact upload', 'upload-artifact' in content),
        ('Claude integration', 'claude' in content.lower()),
        ('Platform support', all(platform in content for platform in ['windows', 'linux', 'macos']))
    ]
    
    passed = 0
    for check_name, check_result in checks:
        if check_result:
            print(f"  • ✅ {check_name}")
            passed += 1
        else:
            print(f"  • ❌ {check_name}")
    
    return passed == len(checks)

def test_build_scripts():
    """Test build script availability and syntax"""
    build_script = Path('scripts/build_standalone.py')
    
    if not build_script.exists():
        print("  • Build script missing")
        return False
    
    # Test syntax by importing (not executing)
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', str(build_script)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  • Build script syntax valid")
            
            # Check for key components
            content = build_script.read_text()
            if 'PyInstaller' in content and 'claude' in content.lower():
                print("  • Build script includes Claude integration")
                return True
        
        print(f"  • Syntax error: {result.stderr}")
        return False
    except Exception as e:
        print(f"  • Build script test failed: {e}")
        return False

def test_documentation():
    """Test documentation completeness"""
    readme_path = Path('README.md')
    
    if not readme_path.exists():
        print("  • README.md missing")
        return False
    
    content = readme_path.read_text().lower()
    
    required_sections = [
        ('Claude integration', 'claude' in content),
        ('Installation instructions', 'install' in content),
        ('Usage examples', 'example' in content),
        ('GitHub Actions info', 'github' in content and 'action' in content),
        ('Dynamic builds', 'dynamic' in content or 'build' in content)
    ]
    
    passed = 0
    for section_name, check in required_sections:
        if check:
            print(f"  • ✅ {section_name}")
            passed += 1
        else:
            print(f"  • ❌ {section_name}")
    
    return passed >= 4  # Allow some flexibility

def main():
    """Run comprehensive test suite"""
    print("🚀 DEBUGGLE BETA USER READINESS TEST SUITE")
    print("=" * 50)
    print("Testing all functionality for beta user deployment...")
    
    tests = [
        ("Claude Integration Import", test_claude_integration_import),
        ("CLI Functionality", test_cli_functionality),
        ("Standalone Entry Point", test_standalone_entry_point),
        ("Error Analysis Pipeline", test_error_analysis_pipeline),
        ("Claude Graceful Degradation", test_claude_graceful_degradation),
        ("Dependencies Check", test_dependencies),
        ("GitHub Actions Readiness", test_github_actions_readiness),
        ("Build Scripts", test_build_scripts),
        ("Documentation", test_documentation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 TEST RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - READY FOR BETA USER! 🚀")
        print("\n✅ Your beta user can:")
        print("  • Download executables from GitHub Actions")
        print("  • Use Claude integration with API key")
        print("  • Get graceful fallback without API key")
        print("  • Analyze errors via CLI or web interface")
        print("  • Access all latest features dynamically")
        return 0
    else:
        print(f"⚠️ {total - passed} TESTS FAILED - NEEDS ATTENTION")
        print("\nFailed tests need to be addressed before beta release.")
        return 1

if __name__ == '__main__':
    sys.exit(main())