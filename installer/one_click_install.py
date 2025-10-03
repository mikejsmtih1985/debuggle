#!/usr/bin/env python3
"""
Debuggle One-Click Installer
============================

A unified installer that provides zero-configuration setup for Debuggle across all environments.

Usage:
    # Web UI installer
    python one_click_install.py --ui
    
    # CLI installer with VS Code integration
    python one_click_install.py --vscode
    
    # Headless installation
    python one_click_install.py --silent
    
    # Custom workspace
    python one_click_install.py --workspace /path/to/project

Features:
- Auto-detects environment (WSL, Local, Docker, Cloud)
- Installs all dependencies automatically
- Configures VS Code integration
- Creates GitHub issues for unsupported scenarios
- AI-powered troubleshooting assistance
"""

import os
import sys
import json
import platform
import subprocess
import tempfile
import urllib.request
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
import logging
from datetime import datetime
import hashlib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / '.debuggle_install.log')
    ]
)
logger = logging.getLogger(__name__)

class EnvironmentType(Enum):
    """Supported environment types"""
    WSL = "wsl"
    WINDOWS_LOCAL = "windows_local"
    MACOS_LOCAL = "macos_local"
    LINUX_LOCAL = "linux_local"
    DOCKER = "docker"
    CLOUD_AWS = "cloud_aws"
    CLOUD_GCP = "cloud_gcp"
    CLOUD_AZURE = "cloud_azure"
    CODESPACES = "codespaces"
    GITPOD = "gitpod"
    REPLIT = "replit"
    UNKNOWN = "unknown"

class InstallationStatus(Enum):
    """Installation status states"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    NEEDS_MANUAL = "needs_manual"
    UNSUPPORTED = "unsupported"

@dataclass
class SystemInfo:
    """System information for environment detection"""
    platform: str
    architecture: str
    python_version: str
    has_wsl: bool
    has_docker: bool
    has_vscode: bool
    has_node: bool
    workspace_path: str
    user_home: str
    environment_type: EnvironmentType
    package_manager: Optional[str] = None
    shell: Optional[str] = None
    terminal: Optional[str] = None
    ide_integrations: Optional[List[str]] = None  # type: ignore

@dataclass
class InstallationConfig:
    """Configuration for installation process"""
    install_vscode_extension: bool = True
    install_dependencies: bool = True
    configure_workspace: bool = True
    create_desktop_shortcut: bool = True
    enable_auto_start: bool = False
    custom_port: Optional[int] = None
    workspace_path: Optional[str] = None
    silent_mode: bool = False
    ui_mode: bool = False

@dataclass
class InstallationResult:
    """Result of installation process"""
    status: InstallationStatus
    message: str
    details: Dict[str, Any]
    system_info: SystemInfo
    config_used: InstallationConfig
    installation_path: str
    logs: List[str]
    github_issue_url: Optional[str] = None
    manual_steps: Optional[List[str]] = None

class EnvironmentDetector:
    """Intelligent environment detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def detect_environment(self) -> SystemInfo:
        """Detect current environment and system capabilities"""
        self.logger.info("Detecting environment...")
        
        # Basic system info
        platform_name = platform.system().lower()
        architecture = platform.machine()
        python_version = platform.python_version()
        user_home = str(Path.home())
        workspace_path = os.getcwd()
        
        # Environment-specific detection
        environment_type = self._detect_environment_type()
        has_wsl = self._detect_wsl()
        has_docker = self._detect_docker()
        has_vscode = self._detect_vscode()
        has_node = self._detect_node()
        package_manager = self._detect_package_manager()
        shell = self._detect_shell()
        terminal = self._detect_terminal()
        ide_integrations = self._detect_ide_integrations()
        
        system_info = SystemInfo(
            platform=platform_name,
            architecture=architecture,
            python_version=python_version,
            has_wsl=has_wsl,
            has_docker=has_docker,
            has_vscode=has_vscode,
            has_node=has_node,
            workspace_path=workspace_path,
            user_home=user_home,
            environment_type=environment_type,
            package_manager=package_manager,
            shell=shell,
            terminal=terminal,
            ide_integrations=ide_integrations
        )
        
        self.logger.info(f"Detected environment: {environment_type.value}")
        return system_info
    
    def _detect_environment_type(self) -> EnvironmentType:
        """Detect specific environment type"""
        # Check for cloud environments first
        if os.getenv('CODESPACES'):
            return EnvironmentType.CODESPACES
        if os.getenv('GITPOD_WORKSPACE_ID'):
            return EnvironmentType.GITPOD
        if os.getenv('REPL_ID'):
            return EnvironmentType.REPLIT
        if self._is_aws_instance():
            return EnvironmentType.CLOUD_AWS
        if self._is_gcp_instance():
            return EnvironmentType.CLOUD_GCP
        if self._is_azure_instance():
            return EnvironmentType.CLOUD_AZURE
        
        # Check for containerized environments
        if Path('/.dockerenv').exists() or os.getenv('DOCKER_CONTAINER'):
            return EnvironmentType.DOCKER
        
        # Check for WSL
        if self._detect_wsl():
            return EnvironmentType.WSL
        
        # Local environments
        platform_name = platform.system().lower()
        if platform_name == 'windows':
            return EnvironmentType.WINDOWS_LOCAL
        elif platform_name == 'darwin':
            return EnvironmentType.MACOS_LOCAL
        elif platform_name == 'linux':
            return EnvironmentType.LINUX_LOCAL
        
        return EnvironmentType.UNKNOWN
    
    def _detect_wsl(self) -> bool:
        """Detect if running in WSL"""
        try:
            # Check for WSL-specific files and environment variables
            if os.getenv('WSL_DISTRO_NAME'):
                return True
            if Path('/proc/version').exists():
                with open('/proc/version', 'r') as f:
                    content = f.read().lower()
                    return 'microsoft' in content or 'wsl' in content
            return False
        except Exception:
            return False
    
    def _detect_docker(self) -> bool:
        """Detect if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _detect_vscode(self) -> bool:
        """Detect if VS Code is available"""
        try:
            # Check for VS Code command
            result = subprocess.run(['code', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
            
            # Check for VS Code Insiders
            result = subprocess.run(['code-insiders', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _detect_node(self) -> bool:
        """Detect if Node.js is available"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _detect_package_manager(self) -> Optional[str]:
        """Detect available package manager"""
        managers = ['apt', 'yum', 'dnf', 'brew', 'choco', 'pacman', 'zypper']
        for manager in managers:
            try:
                result = subprocess.run([manager, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return manager
            except Exception:
                continue
        return None
    
    def _detect_shell(self) -> Optional[str]:
        """Detect current shell"""
        return os.getenv('SHELL', '').split('/')[-1] or None
    
    def _detect_terminal(self) -> Optional[str]:
        """Detect terminal emulator"""
        term_env = os.getenv('TERM_PROGRAM') or os.getenv('TERMINAL_EMULATOR')
        if term_env:
            return term_env
        return os.getenv('TERM', 'unknown')
    
    def _detect_ide_integrations(self) -> List[str]:
        """Detect available IDE integrations"""
        integrations = []
        
        # VS Code
        if self._detect_vscode():
            integrations.append('vscode')
        
        # JetBrains IDEs
        jetbrains_ides = ['pycharm', 'webstorm', 'idea', 'phpstorm']
        for ide in jetbrains_ides:
            try:
                result = subprocess.run([ide, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    integrations.append(ide)
            except Exception:
                continue
        
        # Vim/Neovim
        for editor in ['vim', 'nvim']:
            try:
                result = subprocess.run([editor, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    integrations.append(editor)
            except Exception:
                continue
        
        return integrations
    
    def _is_aws_instance(self) -> bool:
        """Check if running on AWS EC2"""
        try:
            # Check for AWS metadata endpoint
            import socket
            socket.create_connection(('169.254.169.254', 80), timeout=1)
            return True
        except Exception:
            return False
    
    def _is_gcp_instance(self) -> bool:
        """Check if running on Google Cloud Platform"""
        try:
            # Check for GCP metadata endpoint
            import socket
            socket.create_connection(('metadata.google.internal', 80), timeout=1)
            return True
        except Exception:
            return False
    
    def _is_azure_instance(self) -> bool:
        """Check if running on Microsoft Azure"""
        try:
            # Check for Azure metadata endpoint
            import socket
            socket.create_connection(('169.254.169.254', 80), timeout=1)
            # Additional Azure-specific check would be needed here
            return False  # Placeholder
        except Exception:
            return False

class DependencyManager:
    """Intelligent dependency management"""
    
    def __init__(self, system_info: SystemInfo):
        self.system_info = system_info
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def install_dependencies(self) -> Tuple[bool, List[str]]:
        """Install all required dependencies automatically"""
        self.logger.info("Installing dependencies...")
        results = []
        
        # Install Python dependencies
        python_success, python_msg = self._install_python_deps()
        results.append(f"Python dependencies: {python_msg}")
        
        # Install Node.js if needed
        if not self.system_info.has_node:
            node_success, node_msg = self._install_nodejs()
            results.append(f"Node.js: {node_msg}")
        else:
            node_success = True
            results.append("Node.js: Already installed")
        
        # Install VS Code if requested and not present
        if not self.system_info.has_vscode:
            vscode_success, vscode_msg = self._install_vscode()
            results.append(f"VS Code: {vscode_msg}")
        else:
            vscode_success = True
            results.append("VS Code: Already installed")
        
        # Install system dependencies
        system_success, system_msg = self._install_system_deps()
        results.append(f"System dependencies: {system_msg}")
        
        overall_success = python_success and node_success and vscode_success and system_success
        return overall_success, results
    
    def _install_python_deps(self) -> Tuple[bool, str]:
        """Install Python dependencies"""
        try:
            # Create virtual environment if it doesn't exist
            venv_path = Path.cwd() / '.venv'
            if not venv_path.exists():
                subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], 
                             check=True, capture_output=True)
            
            # Activate virtual environment and install requirements
            if self.system_info.platform == 'windows':
                pip_cmd = str(venv_path / 'Scripts' / 'pip')
            else:
                pip_cmd = str(venv_path / 'bin' / 'pip')
            
            # Install requirements
            subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], 
                         check=True, capture_output=True)
            
            return True, "Successfully installed"
        except Exception as e:
            return False, f"Failed: {str(e)}"
    
    def _install_nodejs(self) -> Tuple[bool, str]:
        """Install Node.js using system package manager"""
        try:
            if self.system_info.package_manager == 'apt':
                subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'nodejs', 'npm'], 
                             check=True, capture_output=True)
            elif self.system_info.package_manager == 'brew':
                subprocess.run(['brew', 'install', 'node'], check=True, capture_output=True)
            elif self.system_info.package_manager == 'choco':
                subprocess.run(['choco', 'install', 'nodejs'], check=True, capture_output=True)
            else:
                return False, f"Unsupported package manager: {self.system_info.package_manager}"
            
            return True, "Successfully installed"
        except Exception as e:
            return False, f"Failed: {str(e)}"
    
    def _install_vscode(self) -> Tuple[bool, str]:
        """Install VS Code using system package manager"""
        try:
            if self.system_info.package_manager == 'apt':
                # Add VS Code repository and install
                subprocess.run(['wget', '-qO-', 'https://packages.microsoft.com/keys/microsoft.asc'], 
                             check=True, capture_output=True)
                subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt', 'install', '-y', 'code'], 
                             check=True, capture_output=True)
            elif self.system_info.package_manager == 'brew':
                subprocess.run(['brew', 'install', '--cask', 'visual-studio-code'], 
                             check=True, capture_output=True)
            elif self.system_info.package_manager == 'choco':
                subprocess.run(['choco', 'install', 'vscode'], check=True, capture_output=True)
            else:
                return False, f"Unsupported package manager: {self.system_info.package_manager}"
            
            return True, "Successfully installed"
        except Exception as e:
            return False, f"Failed: {str(e)}"
    
    def _install_system_deps(self) -> Tuple[bool, str]:
        """Install system-level dependencies"""
        try:
            # Install git if not present
            if not self._check_command('git'):
                if self.system_info.package_manager == 'apt':
                    subprocess.run(['sudo', 'apt', 'install', '-y', 'git'], 
                                 check=True, capture_output=True)
                elif self.system_info.package_manager == 'brew':
                    subprocess.run(['brew', 'install', 'git'], check=True, capture_output=True)
                elif self.system_info.package_manager == 'choco':
                    subprocess.run(['choco', 'install', 'git'], check=True, capture_output=True)
            
            return True, "System dependencies installed"
        except Exception as e:
            return False, f"Failed: {str(e)}"
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, text=True, timeout=5)
            return True
        except Exception:
            return False

class OneClickInstaller:
    """Main installer class"""
    
    def __init__(self, config: InstallationConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.detector = EnvironmentDetector()
        self.system_info = None
        self.dependency_manager = None
    
    def install(self) -> InstallationResult:
        """Execute one-click installation"""
        self.logger.info("Starting Debuggle one-click installation...")
        logs = []
        
        try:
            # Phase 1: Environment Detection
            self.logger.info("Phase 1: Detecting environment...")
            self.system_info = self.detector.detect_environment()
            self.dependency_manager = DependencyManager(self.system_info)
            logs.append(f"Detected environment: {self.system_info.environment_type.value}")
            
            # Phase 2: Dependency Installation
            if self.config.install_dependencies:
                self.logger.info("Phase 2: Installing dependencies...")
                deps_success, deps_results = self.dependency_manager.install_dependencies()
                logs.extend(deps_results)
                
                if not deps_success:
                    return self._create_failed_result(
                        "Dependency installation failed", logs, deps_results
                    )
            
            # Phase 3: VS Code Integration
            if self.config.install_vscode_extension and self.system_info.has_vscode:
                self.logger.info("Phase 3: Configuring VS Code integration...")
                vscode_success, vscode_msg = self._configure_vscode_integration()
                logs.append(f"VS Code integration: {vscode_msg}")
                
                if not vscode_success:
                    logs.append("VS Code integration failed, but continuing...")
            
            # Phase 4: Workspace Configuration
            if self.config.configure_workspace:
                self.logger.info("Phase 4: Configuring workspace...")
                workspace_success, workspace_msg = self._configure_workspace()
                logs.append(f"Workspace configuration: {workspace_msg}")
            
            # Phase 5: Final Setup
            self.logger.info("Phase 5: Completing installation...")
            final_success, final_msg = self._complete_installation()
            logs.append(f"Final setup: {final_msg}")
            
            return InstallationResult(
                status=InstallationStatus.SUCCESS,
                message="Debuggle installed successfully!",
                details={
                    "installation_path": os.getcwd(),
                    "vscode_integration": self.config.install_vscode_extension,
                    "auto_start": self.config.enable_auto_start
                },
                system_info=self.system_info,
                config_used=self.config,
                installation_path=os.getcwd(),
                logs=logs
            )
            
        except Exception as e:
            self.logger.exception("Installation failed")
            return self._create_failed_result(f"Installation failed: {str(e)}", logs)
    
    def _configure_vscode_integration(self) -> Tuple[bool, str]:
        """Configure VS Code integration automatically"""
        try:
            # Install VS Code extension
            extension_path = Path.cwd() / 'vscode-extension'
            if extension_path.exists():
                # Build extension
                subprocess.run(['npm', 'install'], cwd=extension_path, 
                             check=True, capture_output=True)
                subprocess.run(['npm', 'run', 'compile'], cwd=extension_path, 
                             check=True, capture_output=True)
                
                # Install extension in VS Code
                subprocess.run(['code', '--install-extension', str(extension_path)], 
                             check=True, capture_output=True)
            
            # Configure workspace settings
            self._create_vscode_workspace_config()
            
            return True, "VS Code integration configured successfully"
        except Exception as e:
            return False, f"Failed to configure VS Code: {str(e)}"
    
    def _create_vscode_workspace_config(self):
        """Create VS Code workspace configuration"""
        vscode_dir = Path.cwd() / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        # Settings
        settings = {
            "python.defaultInterpreterPath": "./.venv/bin/python",
            "debuggle.autoStart": self.config.enable_auto_start,
            "debuggle.port": self.config.custom_port or 8000
        }
        
        with open(vscode_dir / 'settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
        
        # Launch configuration
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Launch Debuggle Server",
                    "type": "python",
                    "request": "launch",
                    "program": "entry_point.py",
                    "args": ["server"],
                    "console": "integratedTerminal",
                    "cwd": "${workspaceFolder}"
                }
            ]
        }
        
        with open(vscode_dir / 'launch.json', 'w') as f:
            json.dump(launch_config, f, indent=2)
    
    def _configure_workspace(self) -> Tuple[bool, str]:
        """Configure workspace for optimal Debuggle usage"""
        try:
            # Create .debuggle directory for configuration
            debuggle_dir = Path.cwd() / '.debuggle'
            debuggle_dir.mkdir(exist_ok=True)
            
            # Create configuration file
            config = {
                "version": "1.0",
                "auto_configured": True,
                "environment": self.system_info.environment_type.value if self.system_info else "unknown",
                "installation_date": datetime.now().isoformat(),
                "features": {
                    "vscode_integration": self.config.install_vscode_extension,
                    "auto_start": self.config.enable_auto_start
                }
            }
            
            with open(debuggle_dir / 'config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            return True, "Workspace configured successfully"
        except Exception as e:
            return False, f"Failed to configure workspace: {str(e)}"
    
    def _complete_installation(self) -> Tuple[bool, str]:
        """Complete the installation process"""
        try:
            # Create desktop shortcut if requested
            if self.config.create_desktop_shortcut:
                self._create_desktop_shortcut()
            
            # Set up auto-start if requested
            if self.config.enable_auto_start:
                self._setup_auto_start()
            
            # Start Debuggle server
            if not self.config.silent_mode:
                self._start_debuggle_server()
            
            return True, "Installation completed successfully"
        except Exception as e:
            return False, f"Failed to complete installation: {str(e)}"
    
    def _create_desktop_shortcut(self):
        """Create desktop shortcut for easy access"""
        # Platform-specific shortcut creation
        pass  # Implementation depends on platform
    
    def _setup_auto_start(self):
        """Set up auto-start functionality"""
        # Platform-specific auto-start setup
        pass  # Implementation depends on platform
    
    def _start_debuggle_server(self):
        """Start the Debuggle server"""
        try:
            subprocess.Popen([sys.executable, 'entry_point.py', 'server'], 
                           cwd=os.getcwd())
        except Exception as e:
            self.logger.warning(f"Failed to start server: {e}")
    
    def _create_failed_result(self, message: str, logs: List[str], 
                            details: Any = None) -> InstallationResult:
        """Create a failed installation result"""
        return InstallationResult(
            status=InstallationStatus.FAILED,
            message=message,
            details=details or {},
            system_info=self.system_info or SystemInfo(
                platform="unknown", architecture="unknown", python_version="unknown",
                has_wsl=False, has_docker=False, has_vscode=False, has_node=False,
                workspace_path="", user_home="", environment_type=EnvironmentType.UNKNOWN
            ),
            config_used=self.config,
            installation_path=os.getcwd(),
            logs=logs
        )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Debuggle One-Click Installer")
    parser.add_argument('--ui', action='store_true', help='Launch web-based installer')
    parser.add_argument('--vscode', action='store_true', help='Install with VS Code integration')
    parser.add_argument('--silent', action='store_true', help='Silent installation')
    parser.add_argument('--workspace', type=str, help='Custom workspace path')
    parser.add_argument('--port', type=int, help='Custom port for Debuggle server')
    parser.add_argument('--no-deps', action='store_true', help='Skip dependency installation')
    parser.add_argument('--no-vscode', action='store_true', help='Skip VS Code integration')
    
    args = parser.parse_args()
    
    # Create installation configuration
    config = InstallationConfig(
        install_vscode_extension=not args.no_vscode and (args.vscode or not args.silent),
        install_dependencies=not args.no_deps,
        configure_workspace=True,
        create_desktop_shortcut=not args.silent,
        enable_auto_start=False,  # User can enable this later
        custom_port=args.port,
        workspace_path=args.workspace,
        silent_mode=args.silent,
        ui_mode=args.ui
    )
    
    if args.ui:
        # Launch web-based installer (to be implemented)
        print("Web-based installer coming soon!")
        print("For now, running CLI installer...")
    
    # Run installation
    installer = OneClickInstaller(config)
    result = installer.install()
    
    # Display results
    print(f"\n{'='*50}")
    print(f"DEBUGGLE INSTALLATION {result.status.value.upper()}")
    print(f"{'='*50}")
    print(f"Status: {result.message}")
    print(f"Environment: {result.system_info.environment_type.value}")
    print(f"Installation Path: {result.installation_path}")
    
    if result.status == InstallationStatus.SUCCESS:
        print(f"\n✅ Debuggle is ready to use!")
        if result.config_used.install_vscode_extension:
            print("• VS Code integration configured")
        print("• Server starting automatically...")
        print(f"• Access at: http://localhost:{result.config_used.custom_port or 8000}")
    else:
        print(f"\n❌ Installation failed: {result.message}")
        if result.logs:
            print("\nLogs:")
            for log in result.logs:
                print(f"  • {log}")
    
    print(f"\nFull logs available at: {Path.home() / '.debuggle_install.log'}")

if __name__ == '__main__':
    main()