#!/usr/bin/env python3
"""
Debuggle Universal Installer
============================

The ultimate one-click installation experience for Debuggle.

This single script can be downloaded and run from anywhere to install Debuggle
with zero configuration required. It automatically detects the environment,
installs dependencies, configures integrations, and provides AI-powered
troubleshooting when needed.

Usage:
    # Download and run (easiest method)
    curl -fsSL https://raw.githubusercontent.com/mikejsmtih1985/debuggle/main/install.py | python3
    
    # Or download first, then run
    wget https://raw.githubusercontent.com/mikejsmtih1985/debuggle/main/install.py
    python3 install.py
    
    # Interactive web installer
    python3 install.py --web
    
    # Silent installation
    python3 install.py --silent
    
    # VS Code integration only
    python3 install.py --vscode-only
    
    # Custom workspace
    python3 install.py --workspace /path/to/project

Features:
✨ One-click installation from any environment
🔍 Intelligent environment detection (WSL, Docker, Cloud, etc.)
🚀 Automatic dependency installation
💻 VS Code integration with real-time error monitoring
🤖 AI-powered troubleshooting assistance
📝 Automatic GitHub issue creation for edge cases
🌐 Beautiful web interface option
"""

import os
import sys
import json
import subprocess
import tempfile
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional
import argparse
import shutil

# Version and repository info
DEBUGGLE_VERSION = "1.0.0"
GITHUB_REPO = "https://github.com/mikejsmtih1985/debuggle"
INSTALL_URL = f"{GITHUB_REPO}/archive/main.zip"

def check_python_version():
    """Ensure we have a compatible Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again")
        sys.exit(1)

def download_and_extract_debuggle(temp_dir: Path) -> Path:
    """Download and extract Debuggle source code"""
    print("📥 Downloading Debuggle...")
    
    # Download archive
    archive_path = temp_dir / "debuggle.zip"
    try:
        urllib.request.urlretrieve(INSTALL_URL, archive_path)
    except Exception as e:
        print(f"❌ Failed to download Debuggle: {e}")
        print(f"   Please check your internet connection and try again")
        sys.exit(1)
    
    # Extract archive
    print("📂 Extracting files...")
    try:
        import zipfile
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find extracted directory
        extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir() and d.name.startswith('debuggle')]
        if not extracted_dirs:
            raise Exception("Could not find extracted Debuggle directory")
        
        return extracted_dirs[0]
        
    except Exception as e:
        print(f"❌ Failed to extract Debuggle: {e}")
        sys.exit(1)

def install_requirements(debuggle_dir: Path):
    """Install basic requirements needed for the installer"""
    print("📦 Installing installer requirements...")
    
    # Basic requirements for the installer itself
    basic_reqs = [
        "requests>=2.25.0",
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0",
        "jinja2>=3.0.0",
        "python-multipart>=0.0.5"
    ]
    
    try:
        for req in basic_reqs:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], 
                         check=True, capture_output=True)
        print("✅ Installer requirements installed")
    except Exception as e:
        print(f"⚠️  Warning: Could not install some requirements: {e}")
        print("   The installer will still work but some features may be limited")

def setup_debuggle_directory(debuggle_dir: Path, target_dir: Optional[Path] = None) -> Path:
    """Set up Debuggle in the target directory"""
    if target_dir is None:
        target_dir = Path.cwd() / "debuggle"
    
    print(f"📁 Setting up Debuggle in {target_dir}...")
    
    # Copy files to target directory
    if target_dir.exists():
        print(f"   Directory {target_dir} already exists")
        response = input("   Overwrite? (y/N): ").lower().strip()
        if response != 'y':
            print("   Installation cancelled")
            sys.exit(0)
        shutil.rmtree(target_dir)
    
    shutil.copytree(debuggle_dir, target_dir)
    print(f"✅ Debuggle source code copied to {target_dir}")
    return target_dir

def run_installer(debuggle_dir: Path, args):
    """Run the appropriate installer based on arguments"""
    print("🚀 Starting Debuggle installer...")
    
    # Change to debuggle directory
    os.chdir(debuggle_dir)
    
    # Add installer directory to Python path
    installer_dir = debuggle_dir / "installer"
    if installer_dir.exists():
        sys.path.insert(0, str(installer_dir))
    
    try:
        if args.web:
            # Run web installer
            print("🌐 Starting web-based installer...")
            from web_installer import run_web_installer
            run_web_installer(port=args.port, open_browser=not args.no_browser)
        
        else:
            # Run CLI installer
            print("⚡ Running one-click installer...")
            from one_click_install import OneClickInstaller, InstallationConfig
            
            config = InstallationConfig(
                install_vscode_extension=not args.no_vscode and not args.vscode_only,
                install_dependencies=not args.no_deps,
                configure_workspace=not args.no_workspace,
                create_desktop_shortcut=not args.no_shortcut,
                enable_auto_start=args.auto_start,
                custom_port=args.custom_port,
                workspace_path=args.workspace,
                silent_mode=args.silent,
                ui_mode=False
            )
            
            installer = OneClickInstaller(config)
            result = installer.install()
            
            # Display results
            print(f"\n{'='*60}")
            print(f"🎯 DEBUGGLE INSTALLATION {result.status.value.upper()}")
            print(f"{'='*60}")
            
            if result.status.value == "success":
                print("✅ Installation completed successfully!")
                print(f"📍 Installed at: {result.installation_path}")
                if result.config_used.install_vscode_extension:
                    print("💻 VS Code integration configured")
                print(f"🌐 Access Debuggle at: http://localhost:{result.config_used.custom_port or 8000}")
                
                if not args.silent:
                    print("\n🎉 Debuggle is ready to use!")
                    print("   Run 'python entry_point.py server' to start the server")
                    print("   Or use VS Code command 'Debuggle: Start Monitoring'")
            else:
                print(f"❌ Installation failed: {result.message}")
                if result.github_issue_url:
                    print(f"📝 Support issue created: {result.github_issue_url}")
                elif result.manual_steps:
                    print("\n🔧 Manual steps required:")
                    for step in result.manual_steps:
                        print(f"   • {step}")
    
    except ImportError as e:
        print(f"❌ Could not import installer modules: {e}")
        print("   This might be due to missing dependencies")
        print("   Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Installation failed with error: {e}")
        print("   Please create a manual issue at:")
        print(f"   {GITHUB_REPO}/issues/new")
        sys.exit(1)

def main():
    """Main installer entry point"""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          🐛 DEBUGGLE INSTALLER v{DEBUGGLE_VERSION}                          ║
║                     Intelligent Error Analysis Made Easy                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check Python version first
    check_python_version()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Debuggle Universal One-Click Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive installation
  %(prog)s --web                    # Web-based installer
  %(prog)s --silent                 # Silent installation
  %(prog)s --vscode-only            # VS Code integration only
  %(prog)s --workspace ~/myproject  # Custom workspace
        """
    )
    
    # Installation modes
    parser.add_argument('--web', action='store_true', 
                       help='Launch web-based installer')
    parser.add_argument('--silent', action='store_true', 
                       help='Silent installation with defaults')
    parser.add_argument('--vscode-only', action='store_true',
                       help='Only install VS Code integration')
    
    # Configuration options
    parser.add_argument('--workspace', type=str, 
                       help='Custom workspace directory')
    parser.add_argument('--custom-port', type=int, default=8000,
                       help='Custom port for Debuggle server')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port for web installer (web mode only)')
    
    # Feature toggles
    parser.add_argument('--no-vscode', action='store_true',
                       help='Skip VS Code integration')
    parser.add_argument('--no-deps', action='store_true',
                       help='Skip dependency installation')
    parser.add_argument('--no-workspace', action='store_true',
                       help='Skip workspace configuration')
    parser.add_argument('--no-shortcut', action='store_true',
                       help='Skip desktop shortcut creation')
    parser.add_argument('--no-browser', action='store_true',
                       help='Don\'t open browser (web mode only)')
    parser.add_argument('--auto-start', action='store_true',
                       help='Enable auto-start on system boot')
    
    # Development options
    parser.add_argument('--local', type=str,
                       help='Use local Debuggle directory instead of downloading')
    parser.add_argument('--target', type=str,
                       help='Target installation directory')
    
    args = parser.parse_args()
    
    # Use local directory if specified
    if args.local:
        debuggle_dir = Path(args.local).resolve()
        if not debuggle_dir.exists():
            print(f"❌ Local directory not found: {debuggle_dir}")
            sys.exit(1)
        print(f"📁 Using local Debuggle directory: {debuggle_dir}")
    else:
        # Create temporary directory for download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Download and extract Debuggle
            extracted_dir = download_and_extract_debuggle(temp_path)
            
            # Set up in target directory
            target_dir = Path(args.target) if args.target else None
            debuggle_dir = setup_debuggle_directory(extracted_dir, target_dir)
    
    # Install basic requirements
    install_requirements(debuggle_dir)
    
    # Run the appropriate installer
    run_installer(debuggle_dir, args)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        print("Please report this issue at:")
        print(f"{GITHUB_REPO}/issues/new")
        sys.exit(1)