#!/usr/bin/env python3
"""
🔧 Debuggle Simple Installer

One script, one purpose: Get Debuggle CLI working reliably.

Usage:
    python install_simple.py

That's it. No options, no complexity, just works.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command with clear feedback."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} failed:")
            print(f"   {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🔧 Debuggle Simple Installer")
    print("=" * 40)
    print("Installing the core CLI functionality only.")
    print("No web servers, no cloud features, just reliable error analysis.\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. You have:", sys.version)
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Determine if we're in the debuggle directory already
    current_dir = Path.cwd()
    if (current_dir / "cli" / "debuggle_cli.py").exists():
        repo_dir = current_dir
        print(f"✅ Found Debuggle repository at {repo_dir}")
    else:
        print("❌ This installer must be run from the Debuggle repository directory.")
        print("   Clone the repository first:")
        print("   git clone https://github.com/mikejsmtih1985/debuggle.git")
        print("   cd debuggle")
        print("   python install_simple.py")
        sys.exit(1)
    
    # Check if virtual environment exists
    venv_path = repo_dir / ".venv"
    if not venv_path.exists():
        print("Creating Python virtual environment...")
        if not run_command(f"python3 -m venv {venv_path}", "Create virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Install core dependencies only
    pip_path = venv_path / "bin" / "pip"
    if not pip_path.exists():
        pip_path = venv_path / "Scripts" / "pip.exe"  # Windows
    
    # Create minimal requirements file for CLI only
    core_requirements = """
# Core dependencies for CLI functionality only
rich==13.7.0
pygments==2.17.2
langdetect==1.0.9

# Optional AI enhancement (can work without)
anthropic==0.7.8
""".strip()
    
    req_file = repo_dir / "requirements_cli.txt"
    req_file.write_text(core_requirements)
    
    if not run_command(f"{pip_path} install -r requirements_cli.txt", 
                      "Install core dependencies", cwd=repo_dir):
        sys.exit(1)
    
    # Test the CLI works
    cli_path = repo_dir / "cli" / "debuggle_cli.py"
    python_path = venv_path / "bin" / "python"
    if not python_path.exists():
        python_path = venv_path / "Scripts" / "python.exe"  # Windows
    
    if not run_command(f"{python_path} {cli_path} --version", 
                      "Test CLI functionality", cwd=repo_dir):
        print("❌ CLI test failed. Installation incomplete.")
        sys.exit(1)
    
    # Success!
    print("\n🎉 Installation complete!")
    print(f"📍 Debuggle installed at: {repo_dir}")
    print("\n🚀 Try it now:")
    print(f"   source {venv_path}/bin/activate")
    print(f"   echo 'NameError: undefined_variable' | python {cli_path}")
    print("\n💡 Add to your workflow:")
    print(f"   python your_script.py 2>&1 | python {cli_path}")
    print("\n📚 For help:")
    print(f"   python {cli_path} --help")

if __name__ == "__main__":
    main()