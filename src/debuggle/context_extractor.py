"""
Advanced context extraction for error analysis.
Goes beyond basic error messages to capture development context.
"""

import os
import re
import ast
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ErrorContext:
    """Rich context information for error analysis."""
    error_location: Optional[str] = None
    surrounding_code: Optional[str] = None
    recent_changes: List[str] = None
    project_structure: Dict[str, Any] = None
    environment_info: Dict[str, Any] = None
    similar_errors: List[str] = None
    dependencies: List[str] = None


class ContextExtractor:
    """Extracts rich context from error logs and development environment."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
    
    def extract_full_context(self, log_input: str, file_path: Optional[str] = None) -> ErrorContext:
        """
        Extract comprehensive context from error log.
        This gives us MORE information than developers typically paste into ChatGPT.
        """
        context = ErrorContext()
        
        # Extract basic error location
        context.error_location = self._extract_error_location(log_input)
        
        # If we have a file path, get surrounding code
        if file_path or context.error_location:
            target_file = file_path or self._extract_file_from_location(context.error_location)
            if target_file:
                context.surrounding_code = self._get_surrounding_code(target_file, log_input)
        
        # Get recent git changes (what developers rarely include)
        context.recent_changes = self._get_recent_changes()
        
        # Analyze project structure
        context.project_structure = self._analyze_project_structure()
        
        # Get environment information
        context.environment_info = self._get_environment_info()
        
        # Extract dependencies
        context.dependencies = self._extract_dependencies()
        
        return context
    
    def _extract_error_location(self, log_input: str) -> Optional[str]:
        """Extract file path and line number from error log."""
        patterns = [
            r'File "([^"]+)", line (\d+)',  # Python
            r'at ([^:]+):(\d+)',  # JavaScript/Java
            r'in ([^:]+):(\d+)',  # General
            r'([^\s]+\.py):(\d+)',  # Python simple
        ]
        
        for pattern in patterns:
            match = re.search(pattern, log_input)
            if match:
                return f"{match.group(1)}:{match.group(2)}"
        
        return None
    
    def _extract_file_from_location(self, location: str) -> Optional[str]:
        """Extract file path from location string."""
        if not location:
            return None
        
        file_path = location.split(':')[0]
        full_path = self.project_root / file_path
        
        return str(full_path) if full_path.exists() else None
    
    def _get_surrounding_code(self, file_path: str, log_input: str) -> Optional[str]:
        """
        Get code context around the error location.
        ChatGPT users rarely include this!
        """
        try:
            # Extract line number from log
            line_match = re.search(r'line (\d+)', log_input)
            if not line_match:
                return None
            
            error_line = int(line_match.group(1))
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get 5 lines before and after the error
            start = max(0, error_line - 6)
            end = min(len(lines), error_line + 5)
            
            context_lines = []
            for i in range(start, end):
                marker = ">>> " if i == error_line - 1 else "    "
                context_lines.append(f"{marker}{i+1:3d}: {lines[i].rstrip()}")
            
            return "\n".join(context_lines)
        
        except Exception:
            return None
    
    def _get_recent_changes(self) -> List[str]:
        """
        Get recent git changes - something developers almost never include in ChatGPT!
        """
        try:
            # Get last 3 commits
            result = subprocess.run(
                ['git', 'log', '--oneline', '-3'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        
        except Exception:
            pass
        
        return []
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure to understand context."""
        structure = {
            'language': 'unknown',
            'framework': 'unknown',
            'has_tests': False,
            'config_files': []
        }
        
        # Check for Python
        if (self.project_root / 'requirements.txt').exists():
            structure['language'] = 'python'
            structure['config_files'].append('requirements.txt')
        
        if (self.project_root / 'pyproject.toml').exists():
            structure['language'] = 'python'
            structure['config_files'].append('pyproject.toml')
        
        # Check for JavaScript
        if (self.project_root / 'package.json').exists():
            structure['language'] = 'javascript'
            structure['config_files'].append('package.json')
        
        # Check for frameworks
        if (self.project_root / 'app').exists() and structure['language'] == 'python':
            # Look for FastAPI/Flask patterns
            app_files = list((self.project_root / 'app').glob('*.py'))
            for app_file in app_files:
                content = app_file.read_text(encoding='utf-8', errors='ignore')
                if 'fastapi' in content.lower():
                    structure['framework'] = 'fastapi'
                elif 'flask' in content.lower():
                    structure['framework'] = 'flask'
        
        # Check for tests
        test_dirs = ['tests', 'test', 'spec']
        for test_dir in test_dirs:
            if (self.project_root / test_dir).exists():
                structure['has_tests'] = True
                break
        
        return structure
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information that affects error context."""
        env_info = {}
        
        # Python version
        try:
            result = subprocess.run(
                ['python', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                env_info['python_version'] = result.stdout.strip()
        except Exception:
            pass
        
        # Operating system
        env_info['os'] = os.name
        
        # Virtual environment
        if 'VIRTUAL_ENV' in os.environ:
            env_info['virtual_env'] = os.environ['VIRTUAL_ENV']
        
        return env_info
    
    def _extract_dependencies(self) -> List[str]:
        """Extract project dependencies."""
        deps = []
        
        # Python requirements
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            try:
                content = req_file.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before version specifiers)
                        pkg_match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                        if pkg_match:
                            deps.append(pkg_match.group(1))
            except Exception:
                pass
        
        return deps
    
    def format_context_for_analysis(self, context: ErrorContext, log_input: str) -> str:
        """
        Format rich context into a comprehensive analysis.
        This is what makes us BETTER than ChatGPT copy/paste!
        """
        sections = []
        
        sections.append("🚨 **ERROR ANALYSIS WITH FULL CONTEXT**")
        sections.append("=" * 50)
        
        # Original error
        sections.append("\n📋 **Original Error:**")
        sections.append(f"```\n{log_input}\n```")
        
        # Error location with surrounding code
        if context.surrounding_code:
            sections.append("\n🎯 **Code Context (What you probably didn't paste into ChatGPT):**")
            sections.append(f"```python\n{context.surrounding_code}\n```")
        
        # Recent changes
        if context.recent_changes:
            sections.append("\n🔄 **Recent Changes (Git History):**")
            for change in context.recent_changes:
                sections.append(f"  • {change}")
        
        # Project context
        if context.project_structure:
            sections.append("\n🏗️ **Project Context:**")
            proj = context.project_structure
            sections.append(f"  • Language: {proj.get('language', 'unknown')}")
            sections.append(f"  • Framework: {proj.get('framework', 'none detected')}")
            sections.append(f"  • Has Tests: {'Yes' if proj.get('has_tests') else 'No'}")
            if proj.get('config_files'):
                sections.append(f"  • Config Files: {', '.join(proj['config_files'])}")
        
        # Dependencies
        if context.dependencies:
            sections.append("\n📦 **Key Dependencies:**")
            sections.append(f"  {', '.join(context.dependencies[:10])}")  # Limit to first 10
        
        # Environment
        if context.environment_info:
            sections.append("\n💻 **Environment:**")
            for key, value in context.environment_info.items():
                sections.append(f"  • {key}: {value}")
        
        sections.append("\n" + "=" * 50)
        sections.append("🎯 **This comprehensive context helps provide more accurate solutions than generic error explanations!**")
        
        return "\n".join(sections)