#!/usr/bin/env python3
"""
Web-Based Installer UI
======================

Beautiful, interactive web interface for the Debuggle one-click installer.
Provides real-time progress updates and handles all complexity behind the scenes.
"""

import os
import json
import asyncio
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

try:
    from fastapi import FastAPI, WebSocket, Request, BackgroundTasks
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from one_click_install import OneClickInstaller, InstallationConfig, EnvironmentDetector, InstallationStatus
from github_support import GitHubIssueCreator, SmartTroubleshooter

logger = logging.getLogger(__name__)

class WebInstallerUI:
    """Web-based installer interface"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = None
        self.active_installations = {}
        self.templates_dir = Path(__file__).parent / "templates"
        self.static_dir = Path(__file__).parent / "static"
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(exist_ok=True)
        self.static_dir.mkdir(exist_ok=True)
        
        self.issue_creator = GitHubIssueCreator()
        self.troubleshooter = SmartTroubleshooter()
        
        if FASTAPI_AVAILABLE:
            self._setup_fastapi()
        else:
            logger.warning("FastAPI not available - falling back to simple HTTP server")
    
    def _setup_fastapi(self):
        """Set up FastAPI application"""
        self.app = FastAPI(title="Debuggle Installer", version="1.0.0")
        
        # Mount static files
        if self.static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(self.static_dir)), name="static")
        
        # Set up templates
        self.templates = Jinja2Templates(directory=str(self.templates_dir))
        
        # Routes
        self.app.get("/")(self.home)
        self.app.get("/install")(self.install_page)
        self.app.post("/api/start-install")(self.start_installation)
        self.app.get("/api/install-status/{install_id}")(self.get_install_status)
        self.app.websocket("/ws/{install_id}")(self.websocket_endpoint)
        self.app.get("/api/system-info")(self.get_system_info)
        self.app.post("/api/create-support-issue")(self.create_support_issue)
    
    async def home(self, request: Request):
        """Home page"""
        return self.templates.TemplateResponse("index.html", {"request": request})
    
    async def install_page(self, request: Request):
        """Installation page"""
        return self.templates.TemplateResponse("install.html", {"request": request})
    
    async def get_system_info(self):
        """Get system information for display"""
        detector = EnvironmentDetector()
        system_info = detector.detect_environment()
        
        return {
            "platform": system_info.platform,
            "environment": system_info.environment_type.value,
            "python_version": system_info.python_version,
            "has_vscode": system_info.has_vscode,
            "has_node": system_info.has_node,
            "has_docker": system_info.has_docker,
            "package_manager": system_info.package_manager,
            "ide_integrations": system_info.ide_integrations or []
        }
    
    async def start_installation(self, request: Request):
        """Start installation process"""
        data = await request.json()
        
        # Generate installation ID
        install_id = f"install_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create configuration from request
        config = InstallationConfig(
            install_vscode_extension=data.get('vscode_integration', True),
            install_dependencies=data.get('install_dependencies', True),
            configure_workspace=data.get('configure_workspace', True),
            create_desktop_shortcut=data.get('desktop_shortcut', False),
            enable_auto_start=data.get('auto_start', False),
            custom_port=data.get('custom_port'),
            workspace_path=data.get('workspace_path'),
            silent_mode=False,
            ui_mode=True
        )
        
        # Store installation info
        self.active_installations[install_id] = {
            "status": "starting",
            "config": config,
            "progress": 0,
            "current_step": "Initializing...",
            "logs": [],
            "result": None
        }
        
        # Start installation in background
        asyncio.create_task(self._run_installation(install_id, config))
        
        return {"install_id": install_id, "status": "started"}
    
    async def get_install_status(self, install_id: str):
        """Get installation status"""
        if install_id not in self.active_installations:
            return JSONResponse({"error": "Installation not found"}, status_code=404)
        
        return self.active_installations[install_id]
    
    async def websocket_endpoint(self, websocket: WebSocket, install_id: str):
        """WebSocket endpoint for real-time updates"""
        await websocket.accept()
        
        try:
            while True:
                if install_id in self.active_installations:
                    status = self.active_installations[install_id]
                    await websocket.send_json(status)
                    
                    # Stop sending updates if installation is complete
                    if status.get("status") in ["success", "failed"]:
                        break
                
                await asyncio.sleep(1)
        except Exception as e:
            logger.exception(f"WebSocket error: {e}")
        finally:
            await websocket.close()
    
    async def create_support_issue(self, request: Request):
        """Create GitHub support issue"""
        data = await request.json()
        install_id = data.get('install_id')
        
        if install_id not in self.active_installations:
            return JSONResponse({"error": "Installation not found"}, status_code=404)
        
        installation = self.active_installations[install_id]
        
        # This would use the actual system info and error details
        # For now, we'll create a placeholder response
        issue_url = "https://github.com/mikejsmtih1985/debuggle/issues/new"
        
        return {"issue_url": issue_url, "status": "created"}
    
    async def _run_installation(self, install_id: str, config: InstallationConfig):
        """Run installation in background"""
        installation = self.active_installations[install_id]
        
        try:
            installation["status"] = "running"
            installation["current_step"] = "Detecting environment..."
            installation["progress"] = 10
            
            # Create installer
            installer = OneClickInstaller(config)
            
            # Run installation
            installation["current_step"] = "Installing dependencies..."
            installation["progress"] = 30
            await asyncio.sleep(1)  # Simulate work
            
            installation["current_step"] = "Configuring VS Code..."
            installation["progress"] = 60
            await asyncio.sleep(1)  # Simulate work
            
            installation["current_step"] = "Finalizing setup..."
            installation["progress"] = 90
            await asyncio.sleep(1)  # Simulate work
            
            # Actually run the installer
            result = installer.install()
            
            installation["result"] = {
                "status": result.status.value,
                "message": result.message,
                "installation_path": result.installation_path
            }
            installation["status"] = "success" if result.status == InstallationStatus.SUCCESS else "failed"
            installation["progress"] = 100
            installation["current_step"] = "Complete!"
            
        except Exception as e:
            logger.exception(f"Installation failed: {e}")
            installation["status"] = "failed"
            installation["result"] = {"error": str(e)}
            installation["current_step"] = f"Failed: {str(e)}"
    
    def run(self, open_browser: bool = True):
        """Run the web installer"""
        if not FASTAPI_AVAILABLE:
            print("❌ FastAPI not available. Please install with:")
            print("   pip install fastapi uvicorn jinja2")
            return
        
        # Create HTML templates
        self._create_templates()
        self._create_static_files()
        
        print(f"🚀 Starting Debuggle Web Installer on http://localhost:{self.port}")
        
        if open_browser:
            webbrowser.open(f"http://localhost:{self.port}")
        
        # Run server
        if self.app:
            uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")
    
    def _create_templates(self):
        """Create HTML templates"""
        
        # Main page template
        index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debuggle One-Click Installer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-hover:hover { transform: translateY(-4px); transition: all 0.3s ease; }
    </style>
</head>
<body class="bg-gray-100">
    <div class="gradient-bg min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl w-full">
            <div class="text-center mb-8">
                <i class="fas fa-bug text-6xl text-purple-600 mb-4"></i>
                <h1 class="text-4xl font-bold text-gray-800 mb-2">Debuggle</h1>
                <p class="text-xl text-gray-600">One-Click Installation</p>
                <p class="text-gray-500 mt-2">The easiest way to set up intelligent error analysis</p>
            </div>
            
            <div class="grid md:grid-cols-2 gap-6 mb-8">
                <div class="card-hover bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-xl border border-blue-200">
                    <i class="fas fa-magic text-3xl text-blue-600 mb-4"></i>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">Auto-Detection</h3>
                    <p class="text-gray-600">Automatically detects your environment (WSL, Docker, Cloud) and configures everything perfectly.</p>
                </div>
                
                <div class="card-hover bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-xl border border-green-200">
                    <i class="fab fa-microsoft text-3xl text-green-600 mb-4"></i>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">VS Code Integration</h3>
                    <p class="text-gray-600">Seamless integration with VS Code for real-time error monitoring and analysis.</p>
                </div>
                
                <div class="card-hover bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-xl border border-purple-200">
                    <i class="fas fa-cog text-3xl text-purple-600 mb-4"></i>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">Zero Configuration</h3>
                    <p class="text-gray-600">No manual setup required. Just click install and start debugging smarter.</p>
                </div>
                
                <div class="card-hover bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-xl border border-red-200">
                    <i class="fas fa-life-ring text-3xl text-red-600 mb-4"></i>
                    <h3 class="text-xl font-semibold text-gray-800 mb-2">Smart Support</h3>
                    <p class="text-gray-600">AI-powered troubleshooting and automatic GitHub issue creation for edge cases.</p>
                </div>
            </div>
            
            <div class="text-center">
                <button onclick="location.href='/install'" class="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-4 px-8 rounded-xl text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200">
                    <i class="fas fa-rocket mr-2"></i>
                    Start Installation
                </button>
                
                <div class="mt-6 text-sm text-gray-500">
                    <p>✅ Works on Windows, macOS, Linux, WSL, Docker, and Cloud environments</p>
                    <p>⚡ Installation typically takes 2-3 minutes</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>'''
        
        # Installation page template
        install_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Installing Debuggle</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .progress-bar { transition: width 0.5s ease-in-out; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .spinner { animation: spin 1s linear infinite; }
    </style>
</head>
<body class="bg-gray-100">
    <div class="gradient-bg min-h-screen flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full">
            <div class="text-center mb-8">
                <i class="fas fa-bug text-4xl text-purple-600 mb-4"></i>
                <h1 class="text-3xl font-bold text-gray-800">Installing Debuggle</h1>
            </div>
            
            <!-- System Info -->
            <div id="system-info" class="bg-gray-50 rounded-xl p-6 mb-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">System Information</h3>
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>Platform: <span id="platform" class="font-mono">Detecting...</span></div>
                    <div>Environment: <span id="environment" class="font-mono">Detecting...</span></div>
                    <div>Python: <span id="python" class="font-mono">Detecting...</span></div>
                    <div>VS Code: <span id="vscode" class="font-mono">Detecting...</span></div>
                </div>
            </div>
            
            <!-- Progress Bar -->
            <div class="mb-6">
                <div class="flex justify-between mb-2">
                    <span id="current-step" class="text-sm font-medium text-gray-700">Preparing installation...</span>
                    <span id="progress-percent" class="text-sm font-medium text-gray-700">0%</span>
                </div>
                <div class="bg-gray-200 rounded-full h-3">
                    <div id="progress-bar" class="bg-gradient-to-r from-purple-600 to-blue-600 h-3 rounded-full progress-bar" style="width: 0%"></div>
                </div>
            </div>
            
            <!-- Status -->
            <div id="status-section" class="text-center mb-6">
                <div id="loading-spinner" class="inline-block">
                    <i class="fas fa-spinner text-2xl text-purple-600 spinner"></i>
                </div>
                <p id="status-message" class="text-gray-600 mt-2">Initializing installation process...</p>
            </div>
            
            <!-- Options -->
            <div class="bg-blue-50 rounded-xl p-4 mb-6">
                <h4 class="font-semibold text-gray-800 mb-3">Installation Options</h4>
                <div class="space-y-2">
                    <label class="flex items-center">
                        <input type="checkbox" id="vscode-integration" checked class="mr-2">
                        <span class="text-sm">Install VS Code integration</span>
                    </label>
                    <label class="flex items-center">
                        <input type="checkbox" id="install-dependencies" checked class="mr-2">
                        <span class="text-sm">Install missing dependencies</span>
                    </label>
                    <label class="flex items-center">
                        <input type="checkbox" id="configure-workspace" checked class="mr-2">
                        <span class="text-sm">Configure current workspace</span>
                    </label>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="text-center space-x-4">
                <button id="install-btn" onclick="startInstallation()" class="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-lg">
                    <i class="fas fa-play mr-2"></i>
                    Start Installation
                </button>
                
                <button id="cancel-btn" onclick="history.back()" class="bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg">
                    <i class="fas fa-arrow-left mr-2"></i>
                    Back
                </button>
            </div>
            
            <!-- Results Section (hidden initially) -->
            <div id="results-section" class="hidden mt-8 p-6 rounded-xl">
                <h3 class="text-xl font-bold mb-4">Installation Complete!</h3>
                <div id="results-content"></div>
            </div>
            
            <!-- Error Section (hidden initially) -->
            <div id="error-section" class="hidden mt-8 p-6 bg-red-50 rounded-xl border border-red-200">
                <h3 class="text-xl font-bold text-red-800 mb-4">Installation Failed</h3>
                <div id="error-content" class="text-red-700"></div>
                <button onclick="createSupportIssue()" class="mt-4 bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">
                    <i class="fab fa-github mr-2"></i>
                    Create Support Issue
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let installId = null;
        let socket = null;
        
        // Load system info
        fetch('/api/system-info')
            .then(response => response.json())
            .then(data => {
                document.getElementById('platform').textContent = data.platform;
                document.getElementById('environment').textContent = data.environment;
                document.getElementById('python').textContent = data.python_version;
                document.getElementById('vscode').textContent = data.has_vscode ? 'Available' : 'Not found';
            });
        
        function startInstallation() {
            const config = {
                vscode_integration: document.getElementById('vscode-integration').checked,
                install_dependencies: document.getElementById('install-dependencies').checked,
                configure_workspace: document.getElementById('configure-workspace').checked
            };
            
            fetch('/api/start-install', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            })
            .then(response => response.json())
            .then(data => {
                installId = data.install_id;
                connectWebSocket();
                
                // Hide install button, show progress
                document.getElementById('install-btn').style.display = 'none';
                document.getElementById('cancel-btn').style.display = 'none';
            });
        }
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(`${protocol}//${window.location.host}/ws/${installId}`);
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateProgress(data);
            };
        }
        
        function updateProgress(data) {
            document.getElementById('current-step').textContent = data.current_step;
            document.getElementById('progress-percent').textContent = data.progress + '%';
            document.getElementById('progress-bar').style.width = data.progress + '%';
            
            if (data.status === 'success') {
                showSuccess(data.result);
            } else if (data.status === 'failed') {
                showError(data.result);
            }
        }
        
        function showSuccess(result) {
            document.getElementById('loading-spinner').innerHTML = '<i class="fas fa-check-circle text-3xl text-green-600"></i>';
            document.getElementById('status-message').textContent = 'Installation completed successfully!';
            document.getElementById('results-section').classList.remove('hidden');
            document.getElementById('results-section').className += ' bg-green-50 border border-green-200';
            document.getElementById('results-content').innerHTML = `
                <p class="text-green-800 mb-2">✅ ${result.message}</p>
                <p class="text-sm text-gray-600">Installation path: ${result.installation_path}</p>
                <a href="http://localhost:8000" target="_blank" class="inline-block mt-4 bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                    <i class="fas fa-external-link-alt mr-2"></i>
                    Open Debuggle
                </a>
            `;
        }
        
        function showError(result) {
            document.getElementById('loading-spinner').innerHTML = '<i class="fas fa-times-circle text-3xl text-red-600"></i>';
            document.getElementById('status-message').textContent = 'Installation failed';
            document.getElementById('error-section').classList.remove('hidden');
            document.getElementById('error-content').textContent = result.error || result.message;
        }
        
        function createSupportIssue() {
            fetch('/api/create-support-issue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ install_id: installId })
            })
            .then(response => response.json())
            .then(data => {
                window.open(data.issue_url, '_blank');
            });
        }
    </script>
</body>
</html>'''
        
        # Write templates
        with open(self.templates_dir / "index.html", "w") as f:
            f.write(index_html)
        
        with open(self.templates_dir / "install.html", "w") as f:
            f.write(install_html)
    
    def _create_static_files(self):
        """Create static CSS and JS files"""
        # For now, we're using CDNs, so no static files needed
        pass

def run_web_installer(port: int = 8080, open_browser: bool = True):
    """Run the web-based installer"""
    installer = WebInstallerUI(port)
    installer.run(open_browser)

if __name__ == '__main__':
    run_web_installer()