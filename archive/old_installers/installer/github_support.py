#!/usr/bin/env python3
"""
GitHub Issue Auto-Creation System
=================================

Automatically creates GitHub issues when unsupported environments or 
configurations are detected during installation.
"""

import os
import json
import requests
import hashlib
from typing import Dict, Any, Optional
from dataclasses import asdict
from datetime import datetime
import logging

from one_click_install import SystemInfo, InstallationConfig, EnvironmentType

logger = logging.getLogger(__name__)

class GitHubIssueCreator:
    """Creates GitHub issues for unsupported configurations"""
    
    def __init__(self, repo_owner: str = "mikejsmtih1985", repo_name: str = "debuggle"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_base = "https://api.github.com"
        self.repo_url = f"{self.api_base}/repos/{repo_owner}/{repo_name}"
        
        # Try to get GitHub token from environment
        self.token = os.getenv('GITHUB_TOKEN')
        if not self.token:
            logger.warning("No GITHUB_TOKEN found - issues will be created as anonymous")
    
    def create_support_issue(self, system_info: SystemInfo, config: InstallationConfig, 
                           error_details: Dict[str, Any]) -> Optional[str]:
        """Create a GitHub issue for unsupported environment"""
        
        # Generate unique identifier for this configuration
        config_hash = self._generate_config_hash(system_info, config)
        
        # Check if issue already exists
        existing_issue = self._find_existing_issue(config_hash)
        if existing_issue:
            logger.info(f"Issue already exists: {existing_issue}")
            return existing_issue
        
        # Create new issue
        issue_data = self._prepare_issue_data(system_info, config, error_details, config_hash)
        
        try:
            headers = {'Accept': 'application/vnd.github+json'}
            if self.token:
                headers['Authorization'] = f'token {self.token}'
            
            response = requests.post(
                f"{self.repo_url}/issues",
                headers=headers,
                json=issue_data,
                timeout=30
            )
            
            if response.status_code == 201:
                issue_url = response.json()['html_url']
                logger.info(f"Created GitHub issue: {issue_url}")
                return issue_url
            else:
                logger.error(f"Failed to create issue: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.exception(f"Failed to create GitHub issue: {e}")
            return None
    
    def _generate_config_hash(self, system_info: SystemInfo, config: InstallationConfig) -> str:
        """Generate unique hash for this configuration"""
        config_str = json.dumps({
            'platform': system_info.platform,
            'environment_type': system_info.environment_type.value,
            'has_wsl': system_info.has_wsl,
            'has_docker': system_info.has_docker,
            'package_manager': system_info.package_manager,
            'shell': system_info.shell
        }, sort_keys=True)
        
        return hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    def _find_existing_issue(self, config_hash: str) -> Optional[str]:
        """Check if an issue already exists for this configuration"""
        try:
            headers = {'Accept': 'application/vnd.github+json'}
            if self.token:
                headers['Authorization'] = f'token {self.token}'
            
            # Search for issues with the config hash
            search_query = f"repo:{self.repo_owner}/{self.repo_name} is:issue label:auto-install-support {config_hash}"
            
            response = requests.get(
                f"{self.api_base}/search/issues",
                headers=headers,
                params={'q': search_query},
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                if results['total_count'] > 0:
                    return results['items'][0]['html_url']
            
            return None
            
        except Exception as e:
            logger.exception(f"Failed to search for existing issues: {e}")
            return None
    
    def _prepare_issue_data(self, system_info: SystemInfo, config: InstallationConfig, 
                           error_details: Dict[str, Any], config_hash: str) -> Dict[str, Any]:
        """Prepare GitHub issue data"""
        
        title = f"[Auto-Install Support] {system_info.environment_type.value} - {system_info.platform}"
        
        # Create detailed issue body
        body_parts = [
            "## Auto-Generated Installation Support Request",
            "",
            "This issue was automatically created when the Debuggle one-click installer",
            "encountered an unsupported environment or configuration.",
            "",
            f"**Configuration Hash:** `{config_hash}`",
            f"**Timestamp:** {datetime.now().isoformat()}",
            "",
            "## System Information",
            "",
            f"- **Platform:** {system_info.platform}",
            f"- **Architecture:** {system_info.architecture}",
            f"- **Python Version:** {system_info.python_version}",
            f"- **Environment Type:** {system_info.environment_type.value}",
            f"- **Package Manager:** {system_info.package_manager or 'None detected'}",
            f"- **Shell:** {system_info.shell or 'Unknown'}",
            f"- **Terminal:** {system_info.terminal or 'Unknown'}",
            "",
            "## Environment Detection Results",
            "",
            f"- **WSL:** {'✅' if system_info.has_wsl else '❌'}",
            f"- **Docker:** {'✅' if system_info.has_docker else '❌'}",
            f"- **VS Code:** {'✅' if system_info.has_vscode else '❌'}",
            f"- **Node.js:** {'✅' if system_info.has_node else '❌'}",
            "",
            "## Installation Configuration",
            "",
            f"- **VS Code Extension:** {config.install_vscode_extension}",
            f"- **Install Dependencies:** {config.install_dependencies}",
            f"- **Configure Workspace:** {config.configure_workspace}",
            f"- **Silent Mode:** {config.silent_mode}",
            "",
            "## Error Details",
            "",
            "```json"
        ]
        
        # Add error details
        body_parts.append(json.dumps(error_details, indent=2))
        body_parts.extend([
            "```",
            "",
            "## IDE Integrations Available",
            ""
        ])
        
        if system_info.ide_integrations:
            for ide in system_info.ide_integrations:
                body_parts.append(f"- {ide}")
        else:
            body_parts.append("- None detected")
        
        body_parts.extend([
            "",
            "## Paths",
            "",
            f"- **Workspace:** `{system_info.workspace_path}`",
            f"- **User Home:** `{system_info.user_home}`",
            "",
            "## Suggested Implementation Priority",
            "",
            self._get_priority_suggestion(system_info),
            "",
            "## Implementation Checklist",
            "",
            "- [ ] Analyze environment configuration",
            "- [ ] Implement detection logic",
            "- [ ] Create installation strategy",
            "- [ ] Add dependency management",
            "- [ ] Test on similar systems",
            "- [ ] Update documentation",
            "- [ ] Add to CI/CD testing matrix",
            "",
            "---",
            "*This issue was automatically generated by the Debuggle One-Click Installer*"
        ])
        
        return {
            'title': title,
            'body': '\n'.join(body_parts),
            'labels': [
                'auto-install-support',
                'enhancement',
                f'platform-{system_info.platform}',
                f'env-{system_info.environment_type.value}',
                'installer'
            ]
        }
    
    def _get_priority_suggestion(self, system_info: SystemInfo) -> str:
        """Get priority suggestion based on environment popularity"""
        
        # Common environments get higher priority
        high_priority_envs = [
            EnvironmentType.WSL,
            EnvironmentType.WINDOWS_LOCAL,
            EnvironmentType.MACOS_LOCAL,
            EnvironmentType.LINUX_LOCAL,
            EnvironmentType.CODESPACES
        ]
        
        medium_priority_envs = [
            EnvironmentType.DOCKER,
            EnvironmentType.CLOUD_AWS,
            EnvironmentType.GITPOD
        ]
        
        if system_info.environment_type in high_priority_envs:
            return "**🔥 HIGH PRIORITY** - Common development environment"
        elif system_info.environment_type in medium_priority_envs:
            return "**🟡 MEDIUM PRIORITY** - Popular in certain workflows"
        else:
            return "**🔵 LOW PRIORITY** - Specialized or uncommon environment"

class SmartTroubleshooter:
    """AI-powered troubleshooting assistance"""
    
    def __init__(self):
        self.known_solutions = self._load_known_solutions()
    
    def get_troubleshooting_steps(self, system_info: SystemInfo, 
                                error_details: Dict[str, Any]) -> list[str]:
        """Get AI-powered troubleshooting steps"""
        
        steps = []
        
        # Environment-specific troubleshooting
        if system_info.environment_type == EnvironmentType.WSL:
            steps.extend(self._get_wsl_troubleshooting())
        elif system_info.environment_type == EnvironmentType.DOCKER:
            steps.extend(self._get_docker_troubleshooting())
        elif system_info.environment_type == EnvironmentType.CODESPACES:
            steps.extend(self._get_codespaces_troubleshooting())
        
        # Dependency-specific troubleshooting
        if not system_info.has_node:
            steps.extend(self._get_nodejs_troubleshooting(system_info))
        
        if not system_info.has_vscode:
            steps.extend(self._get_vscode_troubleshooting(system_info))
        
        # Generic fallback steps
        steps.extend(self._get_general_troubleshooting())
        
        return steps
    
    def _load_known_solutions(self) -> Dict[str, Any]:
        """Load known solutions database"""
        # This would typically load from a JSON file or database
        return {
            "wsl_node_issue": {
                "description": "Node.js not found in WSL",
                "solution": [
                    "Install Node.js using NodeSource repository",
                    "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -",
                    "sudo apt-get install -y nodejs"
                ]
            },
            "permission_denied": {
                "description": "Permission denied during installation",
                "solution": [
                    "Check file permissions in workspace",
                    "Ensure user has write access to installation directory",
                    "Consider running with appropriate privileges"
                ]
            }
        }
    
    def _get_wsl_troubleshooting(self) -> list[str]:
        """WSL-specific troubleshooting steps"""
        return [
            "🔧 **WSL Environment Detected**",
            "• Ensure you're running in WSL 2 (not WSL 1)",
            "• Install dependencies in WSL, not Windows",
            "• Use VS Code Remote-WSL extension",
            "• Check Windows Defender real-time protection settings"
        ]
    
    def _get_docker_troubleshooting(self) -> list[str]:
        """Docker-specific troubleshooting steps"""
        return [
            "🐳 **Docker Environment Detected**",
            "• Ensure Docker daemon is running",
            "• Check port bindings and networking",
            "• Verify volume mounts for persistence",
            "• Consider using docker-compose for easier setup"
        ]
    
    def _get_codespaces_troubleshooting(self) -> list[str]:
        """GitHub Codespaces-specific troubleshooting steps"""
        return [
            "☁️ **GitHub Codespaces Detected**",
            "• Use pre-built devcontainer configuration",
            "• Check port forwarding settings",
            "• Verify persistent storage setup",
            "• Consider using Codespaces secrets for configuration"
        ]
    
    def _get_nodejs_troubleshooting(self, system_info: SystemInfo) -> list[str]:
        """Node.js installation troubleshooting"""
        if system_info.package_manager == 'apt':
            return [
                "📦 **Installing Node.js on Ubuntu/Debian:**",
                "• `curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -`",
                "• `sudo apt-get install -y nodejs`",
                "• Verify with `node --version`"
            ]
        elif system_info.package_manager == 'brew':
            return [
                "🍺 **Installing Node.js on macOS:**",
                "• `brew install node`",
                "• Or use Node Version Manager: `brew install nvm`",
                "• Verify with `node --version`"
            ]
        else:
            return [
                "📦 **Installing Node.js:**",
                "• Download from https://nodejs.org/",
                "• Use Node Version Manager (nvm) for version control",
                "• Verify installation with `node --version`"
            ]
    
    def _get_vscode_troubleshooting(self, system_info: SystemInfo) -> list[str]:
        """VS Code installation troubleshooting"""
        if system_info.environment_type == EnvironmentType.WSL:
            return [
                "💻 **Installing VS Code for WSL:**",
                "• Install VS Code on Windows (not in WSL)",
                "• Install Remote-WSL extension",
                "• Open WSL project with `code .` from WSL terminal"
            ]
        else:
            return [
                "💻 **Installing VS Code:**",
                "• Download from https://code.visualstudio.com/",
                "• Or use package manager if available",
                "• Verify with `code --version`"
            ]
    
    def _get_general_troubleshooting(self) -> list[str]:
        """General troubleshooting steps"""
        return [
            "🔍 **General Troubleshooting:**",
            "• Check internet connectivity",
            "• Verify disk space availability",
            "• Ensure all ports are available",
            "• Review system logs for errors",
            "• Try installation in clean environment",
            "",
            "📝 **Get Help:**",
            "• Check Debuggle documentation",
            "• Join our Discord community",
            "• Create manual GitHub issue with full logs"
        ]

# Example usage
if __name__ == '__main__':
    # This would be used by the installer when it encounters issues
    issue_creator = GitHubIssueCreator()
    troubleshooter = SmartTroubleshooter()
    
    print("GitHub Issue Auto-Creation System ready!")
    print("This will be integrated into the one-click installer.")