#!/usr/bin/env python3
"""
Build standalone executables for Debuggle
Supports Windows, Linux, and macOS with no admin privileges required
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def get_platform_info():
    """Get current platform information"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Normalize system names to match GitHub Actions matrix
    if system == 'darwin':
        system = 'macos'
    elif system == 'win32' or system == 'windows':
        system = 'windows'
    elif system == 'linux':
        system = 'linux'
    
    # Normalize architecture names
    if arch in ['x86_64', 'amd64']:
        arch = 'x64'
    elif arch in ['i386', 'i686']:
        arch = 'x86'
    elif arch in ['aarch64', 'arm64']:
        arch = 'arm64'
    
    # Handle environment variables from GitHub Actions
    target_platform = os.environ.get('TARGET_PLATFORM')
    target_arch = os.environ.get('TARGET_ARCH')
    
    if target_platform:
        system = target_platform.lower()
    if target_arch:
        arch = target_arch.lower()
    
    return system, arch

def ensure_pyinstaller():
    """Ensure PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} is installed")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller")
            return False

def create_spec_file(system, arch):
    """Create PyInstaller spec file for Debuggle"""
    
    # Convert arch names for PyInstaller on macOS
    pyinstaller_arch = arch
    if system == 'macos':
        if arch == 'x64':
            pyinstaller_arch = 'x86_64'
        elif arch == 'arm64':
            pyinstaller_arch = 'arm64'
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# Get the project root directory
project_root = Path('.').absolute()

a = Analysis(
    ['debuggle_standalone.py'],  # Use unified standalone entry point
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include static assets (conditionally if they exist)
        *([('assets', 'assets')] if os.path.exists('assets') else []),
        # Include CLI
        ('cli', 'cli'),
        # Include src if it exists  
        ('src', 'src'),
        # Include configuration files (conditionally)
        *([('pyproject.toml', '.')] if os.path.exists('pyproject.toml') else []),
    ],
    hiddenimports=[
        # Core Debuggle modules
        'src.debuggle.core.analyzer',
        'src.debuggle.core.context',
        'src.debuggle.core.patterns',
        'src.debuggle.core.processor',
        'src.debuggle.integrations.claude',
        'src.debuggle.storage.database',
        'src.debuggle.config_v2',
        # FastAPI and Uvicorn (if web interface needed)
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.http.h11_impl', 
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan.on',
        'fastapi.applications',
        'fastapi.routing',
        'fastapi.staticfiles',
        'fastapi.middleware.cors',
        # Core dependencies
        'pydantic',
        'pydantic_settings',
        'pygments',
        'pygments.lexers',
        'pygments.formatters',
        'rich',
        'rich.console',
        'rich.text',
        'langdetect',
        'langdetect.detector',
        'multipart',
        'slowapi',
        # Claude AI integration (optional)
        'anthropic',
        # Additional imports that might be needed
        'email.mime.multipart',
        'email.mime.text',
        'json',
        'pathlib',
        'typing',
        'sqlite3',
        'logging',
        'argparse',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='debuggle{"" if system != "windows" else ".exe"}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='{pyinstaller_arch}',
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
'''
    
    spec_path = Path('debuggle_standalone.spec')
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    return spec_path

def create_launcher_script(system, output_dir):
    """Create platform-specific launcher script"""
    
    if system == 'windows':
        launcher_content = '''@echo off
echo Starting Debuggle...
echo.
echo Debuggle - Log File Processor
echo ================================
echo.
echo Starting web server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Start Debuggle
"%SCRIPT_DIR%debuggle.exe" serve --host 0.0.0.0 --port 8000

pause
'''
        launcher_path = output_dir / 'start_debuggle.bat'
    else:
        launcher_content = '''#!/bin/bash
echo "Starting Debuggle..."
echo ""
echo "Debuggle - Log File Processor"
echo "================================"
echo ""
echo "Starting web server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Start Debuggle
"$SCRIPT_DIR/debuggle" serve --host 0.0.0.0 --port 8000
'''
        launcher_path = output_dir / 'start_debuggle.sh'
    
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    # Make executable on Unix systems
    if system != 'windows':
        os.chmod(launcher_path, 0o755)
    
    return launcher_path

def create_readme(output_dir):
    """Create README for standalone distribution"""
    
    readme_content = '''# Debuggle - Standalone Distribution

## Quick Start

### Windows:
1. Double-click `start_debuggle.bat`
2. Open your browser to http://localhost:8000
3. Drag & drop your log files to analyze them!

### Linux/macOS:
1. Open terminal in this directory
2. Run: `./start_debuggle.sh`
3. Open your browser to http://localhost:8000
4. Drag & drop your log files to analyze them!

## Features

* **Drag & Drop Interface** - Simply drag your log files into the browser
* **Smart Analysis** - AI-powered error detection and summaries
* **Interactive Tags** - Click tags to highlight related log entries
* **Enhanced Formatting** - Color-coded log output with syntax highlighting
* **Multi-file Support** - Process multiple files with tabbed interface
* **Fast Processing** - Local processing, no internet required
* **Privacy First** - Your logs never leave your computer

## What's Included

- `debuggle` / `debuggle.exe` - Main executable
- `start_debuggle.sh` / `start_debuggle.bat` - Launcher script
- This README file

## System Requirements

- **Windows**: Windows 10 or later (64-bit)
- **Linux**: Most modern distributions (64-bit)
- **macOS**: macOS 10.14 or later (64-bit)

## No Installation Required!

This is a portable application - no admin privileges needed!
Just extract and run. You can move this folder anywhere on your system.

## Command Line Usage

You can also use Debuggle from the command line:

```bash
# Analyze a single file
./debuggle analyze mylog.txt

# Start the web server manually
./debuggle serve --port 8000

# Get help
./debuggle --help
```

## Troubleshooting

**Port 8000 is busy?**
- Try: `./debuggle serve --port 8080` (or any other port)

**Antivirus flags the executable?**
- This is common with PyInstaller executables
- The binary is safe - it's just bundled Python code
- Add an exception in your antivirus if needed

**Browser doesn't open automatically?**
- Manually navigate to http://localhost:8000

## Support

- Documentation: https://github.com/mikejsmtih1985/debuggle
- Issues: https://github.com/mikejsmtih1985/debuggle/issues

---

Made with love by the Debuggle team
'''
    
    readme_path = output_dir / 'README.txt'
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    return readme_path

def build_executable():
    """Build the standalone executable"""
    
    print("Building Debuggle Standalone Executable")
    print("=" * 50)
    
    # Get platform info
    system, arch = get_platform_info()
    print(f"Platform: {system}-{arch}")
    
    # Ensure PyInstaller is available
    if not ensure_pyinstaller():
        return False
    
    # Create build directory
    build_dir = Path('build_standalone')
    build_dir.mkdir(exist_ok=True)
    
    # Create output directory
    output_dir = build_dir / f'debuggle-{system}-{arch}'
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"Build directory: {build_dir}")
    print(f"Output directory: {output_dir}")
    
    # Create spec file
    print("Creating PyInstaller spec file...")
    spec_path = create_spec_file(system, arch)
    
    # Build the executable
    print("Building executable (this may take a few minutes)...")
    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--distpath', str(output_dir),
            '--workpath', str(build_dir / 'work'),
            str(spec_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")
            return False
            
        print("Executable built successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    # Create launcher script
    print("Creating launcher script...")
    launcher_path = create_launcher_script(system, output_dir)
    print(f"Launcher created: {launcher_path}")
    
    # Create README
    print("Creating README...")
    readme_path = create_readme(output_dir)
    print(f"README created: {readme_path}")
    
    # Create archive
    print("Creating distribution archive...")
    archive_name = f'debuggle-{system}-{arch}'
    
    if system == 'windows':
        # Create zip archive from the output directory contents
        shutil.make_archive(
            str(build_dir / archive_name), 
            'zip', 
            str(output_dir.parent),  # Parent directory
            str(output_dir.name)     # Directory name to archive
        )
        archive_path = build_dir / f'{archive_name}.zip'
    else:
        # Create tar.gz archive from the output directory contents
        shutil.make_archive(
            str(build_dir / archive_name), 
            'gztar', 
            str(output_dir.parent),  # Parent directory
            str(output_dir.name)     # Directory name to archive
        )
        archive_path = build_dir / f'{archive_name}.tar.gz'
    
    print(f"Distribution archive created: {archive_path}")
    
    # Cleanup
    if spec_path.exists():
        spec_path.unlink()
    
    print("\nBuild completed successfully!")
    print(f"Distribution: {archive_path}")
    print(f"Extracted files: {output_dir}")
    print("\nTo test:")
    print(f"1. Extract {archive_path}")
    if system == 'windows':
        print("2. Run start_debuggle.bat")
    else:
        print("2. Run ./start_debuggle.sh")
    print("3. Open http://localhost:8000")
    
    return True

if __name__ == '__main__':
    if build_executable():
        sys.exit(0)
    else:
        sys.exit(1)