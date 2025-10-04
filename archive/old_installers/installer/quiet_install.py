#!/usr/bin/env python3
"""
Quiet Mode - Debuggle Installer Without Debug AI
================================================

For users who prefer a silent installation without AI assistance.
"""

import os
import sys
from pathlib import Path

# Add installer directory to path
sys.path.insert(0, str(Path(__file__).parent))

from one_click_install import OneClickInstaller, InstallationConfig

def quiet_install():
    """Install Debuggle without any AI assistance"""
    
    print("🤫 QUIET MODE - Installing Debuggle without Debug AI")
    print("=" * 60)
    
    # Create configuration with AI assistance disabled
    config = InstallationConfig(
        install_vscode_extension=True,
        install_dependencies=True,
        configure_workspace=True,
        create_desktop_shortcut=False,
        enable_auto_start=False,
        silent_mode=True,  # This keeps Debug quiet
        ui_mode=False
    )
    
    # Install without AI chatter
    installer = OneClickInstaller(config)
    result = installer.install()
    
    # Simple, non-chatty results
    if result.status.value == "success":
        print("✅ Debuggle installed successfully")
        print(f"📍 Location: {result.installation_path}")
        print(f"🌐 Access: http://localhost:8000")
    else:
        print(f"❌ Installation failed: {result.message}")
        print("💡 Check logs for details")

if __name__ == '__main__':
    quiet_install()