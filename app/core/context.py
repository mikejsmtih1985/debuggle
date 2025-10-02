"""
Development context extraction for enhanced error analysis.

This module provides the "ChatGPT killer" feature - extracting rich development
context that developers never include when copying errors to ChatGPT.
"""

import logging
import os
import re
import subprocess
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


logger = logging.getLogger(__name__)


@dataclass
class FileContext:
    """Context information for a specific file."""
    file_path: str
    line_number: Optional[int] = None
    surrounding_code: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class GitContext:
    """Git repository context."""
    is_git_repo: bool = False
    current_branch: Optional[str] = None
    recent_commits: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    last_commit_hash: Optional[str] = None


@dataclass
class ProjectContext:
    """Overall project context."""
    root_path: str
    project_type: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    config_files: List[str] = field(default_factory=list)
    has_tests: bool = False
    virtual_env: Optional[str] = None


@dataclass
class EnvironmentContext:
    """Runtime environment context."""
    python_version: Optional[str] = None
    node_version: Optional[str] = None
    java_version: Optional[str] = None
    working_directory: str = "."
    environment_variables: Dict[str, str] = field(default_factory=dict)


@dataclass
class DevelopmentContext:
    """Complete development context."""
    file_context: Optional[FileContext] = None
    git_context: Optional[GitContext] = None
    project_context: Optional[ProjectContext] = None
    environment_context: Optional[EnvironmentContext] = None
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)


class ContextExtractor:
    """
    Extracts rich development context for error analysis.
    
    This provides the key differentiator over ChatGPT - we can see the actual
    development environment, recent changes, project structure, etc.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize context extractor.
        
        Args:
            project_root: Root directory of the project, defaults to current directory
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def extract_full_context(self, error_text: str, file_path: Optional[str] = None) -> DevelopmentContext:
        """
        Extract comprehensive development context.
        
        This is our "secret sauce" - the context that ChatGPT never sees!
        
        Args:
            error_text: The error log or stack trace  
            file_path: Optional specific file path if known
            
        Returns:
            Complete development context
        """
        context = DevelopmentContext()
        
        try:
            # Extract file context from error
            context.file_context = self._extract_file_context(error_text, file_path)
            
            # Extract git context
            context.git_context = self._extract_git_context()
            
            # Extract project context
            context.project_context = self._extract_project_context()
            
            # Extract environment context
            context.environment_context = self._extract_environment_context()
            
            # Add extraction metadata
            context.extraction_metadata = {
                'project_root': str(self.project_root),
                'context_sources': [
                    'file_analysis' if context.file_context else None,
                    'git_analysis' if context.git_context and context.git_context.is_git_repo else None,
                    'project_analysis' if context.project_context else None,
                    'environment_analysis' if context.environment_context else None
                ],
                'extraction_successful': True
            }
            
        except Exception as e:
            self.logger.error(f"Context extraction failed: {e}", exc_info=True)
            context.extraction_metadata = {
                'extraction_successful': False,
                'error': str(e)
            }
        
        return context
    
    def _extract_file_context(self, error_text: str, file_path: Optional[str] = None) -> Optional[FileContext]:
        """Extract context about the specific file where the error occurred."""
        try:
            # Try to extract file path and line number from error text
            if not file_path:
                file_path, line_number = self._parse_file_location_from_error(error_text)
            else:
                line_number = self._parse_line_number_from_error(error_text)
            
            if not file_path:
                return None
            
            # Convert to absolute path
            full_path = self.project_root / file_path if not os.path.isabs(file_path) else Path(file_path)
            
            if not full_path.exists():
                self.logger.warning(f"File not found: {full_path}")
                return None
            
            # Read file and extract surrounding code
            surrounding_code = None
            function_name = None
            class_name = None
            
            if line_number:
                surrounding_code = self._get_surrounding_code(full_path, line_number)
                function_name, class_name = self._get_function_and_class_context(full_path, line_number)
            
            return FileContext(
                file_path=str(full_path),
                line_number=line_number,
                surrounding_code=surrounding_code,
                function_name=function_name,
                class_name=class_name
            )
            
        except Exception as e:
            self.logger.error(f"File context extraction failed: {e}")
            return None
    
    def _extract_git_context(self) -> GitContext:
        """Extract git repository context."""
        context = GitContext()
        
        try:
            # Check if this is a git repository
            result = self._run_git_command(['status'], check=False)
            if result.returncode != 0:
                return context
            
            context.is_git_repo = True
            
            # Get current branch
            result = self._run_git_command(['branch', '--show-current'])
            if result.returncode == 0:
                context.current_branch = result.stdout.strip()
            
            # Get recent commits
            result = self._run_git_command(['log', '--oneline', '-5'])
            if result.returncode == 0:
                context.recent_commits = result.stdout.strip().split('\n')
                if context.recent_commits:
                    context.last_commit_hash = context.recent_commits[0].split()[0]
            
            # Get modified files
            result = self._run_git_command(['diff', '--name-only', 'HEAD'])
            if result.returncode == 0:
                context.modified_files = [f for f in result.stdout.strip().split('\n') if f]
            
        except Exception as e:
            self.logger.error(f"Git context extraction failed: {e}")
        
        return context
    
    def _extract_project_context(self) -> ProjectContext:
        """Extract project structure and configuration context."""
        context = ProjectContext(root_path=str(self.project_root))
        
        try:
            # Detect project type and language
            context.project_type, context.language = self._detect_project_type()
            
            # Detect framework
            context.framework = self._detect_framework()
            
            # Find configuration files
            context.config_files = self._find_config_files()
            
            # Check for tests
            context.has_tests = self._has_tests()
            
            # Detect virtual environment
            context.virtual_env = self._detect_virtual_env()
            
            # Extract dependencies
            context.dependencies = self._extract_dependencies()
            
        except Exception as e:
            self.logger.error(f"Project context extraction failed: {e}")
        
        return context
    
    def _extract_environment_context(self) -> EnvironmentContext:
        """Extract runtime environment context."""
        context = EnvironmentContext(working_directory=os.getcwd())
        
        try:
            # Get Python version
            result = subprocess.run(['python', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                context.python_version = result.stdout.strip()
            
            # Get Node version
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                context.node_version = result.stdout.strip()
            
            # Get Java version
            result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                context.java_version = result.stderr.split('\n')[0] if result.stderr else result.stdout.split('\n')[0]
            
            # Get relevant environment variables
            env_vars_of_interest = ['VIRTUAL_ENV', 'NODE_ENV', 'PYTHONPATH', 'PATH']
            for var in env_vars_of_interest:
                if var in os.environ:
                    context.environment_variables[var] = os.environ[var]
            
        except Exception as e:
            self.logger.error(f"Environment context extraction failed: {e}")
        
        return context
    
    def _parse_file_location_from_error(self, error_text: str) -> Tuple[Optional[str], Optional[int]]:
        """Parse file path and line number from error text."""
        # Python traceback patterns
        python_patterns = [
            r'File "([^"]+)", line (\d+)',
            r'File "([^"]+)".*line (\d+)',
        ]
        
        # JavaScript error patterns
        js_patterns = [
            r'at .* \(([^:]+):(\d+):\d+\)',
            r'at ([^:]+):(\d+):\d+',
        ]
        
        # Java error patterns
        java_patterns = [
            r'at .+\(([^:]+):(\d+)\)',
        ]
        
        all_patterns = python_patterns + js_patterns + java_patterns
        
        for pattern in all_patterns:
            match = re.search(pattern, error_text)
            if match:
                file_path = match.group(1)
                line_number = int(match.group(2))
                return file_path, line_number
        
        return None, None
    
    def _parse_line_number_from_error(self, error_text: str) -> Optional[int]:
        """Parse line number from error text."""
        # Look for line number patterns
        patterns = [
            r'line (\d+)',
            r':(\d+):',
            r':(\d+)\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_text)
            if match:
                return int(match.group(1))
        
        return None
    
    def _get_surrounding_code(self, file_path: Path, line_number: int, context_lines: int = 5) -> Optional[str]:
        """Get code surrounding the error line."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_number - context_lines - 1)
            end = min(len(lines), line_number + context_lines)
            
            context_lines_list = []
            for i in range(start, end):
                line_num = i + 1
                marker = ">>> " if line_num == line_number else "    "
                context_lines_list.append(f"{marker}{line_num:3d}: {lines[i].rstrip()}")
            
            return '\n'.join(context_lines_list)
            
        except Exception as e:
            self.logger.error(f"Error reading surrounding code: {e}")
            return None
    
    def _get_function_and_class_context(self, file_path: Path, line_number: int) -> Tuple[Optional[str], Optional[str]]:
        """Get the function and class context for the error line."""
        try:
            if not file_path.suffix == '.py':
                return None, None  # Only support Python for now
            
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            function_name = None
            class_name = None
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if hasattr(node, 'lineno') and node.lineno <= line_number <= getattr(node, 'end_lineno', node.lineno):
                        function_name = node.name
                
                elif isinstance(node, ast.ClassDef):
                    if hasattr(node, 'lineno') and node.lineno <= line_number <= getattr(node, 'end_lineno', node.lineno):
                        class_name = node.name
            
            return function_name, class_name
            
        except Exception as e:
            self.logger.error(f"Error parsing function/class context: {e}")
            return None, None
    
    def _run_git_command(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command safely."""
        try:
            return subprocess.run(
                ['git'] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
                check=check
            )
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Git command timed out: {args}")
            raise
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"Git command failed: {args}, error: {e}")
            raise
    
    def _detect_project_type(self) -> Tuple[Optional[str], Optional[str]]:
        """Detect project type and primary language."""
        # Check for common project files
        indicators = {
            'python': ['setup.py', 'pyproject.toml', 'requirements.txt', 'Pipfile'],
            'javascript': ['package.json', 'yarn.lock', 'npm-shrinkwrap.json'],
            'java': ['pom.xml', 'build.gradle', 'build.xml'],
            'csharp': ['*.csproj', '*.sln'],
            'go': ['go.mod', 'go.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
        }
        
        for language, files in indicators.items():
            for file_pattern in files:
                if any(self.project_root.glob(file_pattern)):
                    return language, language
        
        return None, None
    
    def _detect_framework(self) -> Optional[str]:
        """Detect web framework or major libraries."""
        frameworks = {
            'django': ['manage.py', 'django'],
            'flask': ['app.py', 'flask'],
            'fastapi': ['main.py', 'fastapi'],
            'react': ['package.json', 'react'],
            'vue': ['package.json', 'vue'],
            'spring': ['pom.xml', 'springframework'],
        }
        
        # Check package.json for JS frameworks
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    for framework, patterns in frameworks.items():
                        if any(pattern in dependencies for pattern in patterns[1:]):
                            return framework
            except Exception:
                pass
        
        # Check requirements.txt for Python frameworks
        requirements = self.project_root / 'requirements.txt'
        if requirements.exists():
            try:
                with open(requirements) as f:
                    content = f.read().lower()
                    for framework, patterns in frameworks.items():
                        if any(pattern in content for pattern in patterns[1:]):
                            return framework
            except Exception:
                pass
        
        return None
    
    def _find_config_files(self) -> List[str]:
        """Find common configuration files."""
        config_patterns = [
            '.env', '.env.*', 'config.json', 'config.yml', 'config.yaml',
            'settings.py', 'settings.json', 'docker-compose.yml',
            '.gitignore', 'Dockerfile', 'Makefile'
        ]
        
        config_files = []
        for pattern in config_patterns:
            config_files.extend([str(p.relative_to(self.project_root)) for p in self.project_root.glob(pattern)])
        
        return config_files
    
    def _has_tests(self) -> bool:
        """Check if the project has tests."""
        test_indicators = [
            'test_*.py', '*_test.py', 'tests/', 'test/',
            '*.test.js', '*.spec.js', '__tests__/',
            'src/test/', 'spec/'
        ]
        
        for pattern in test_indicators:
            if any(self.project_root.glob(f"**/{pattern}")):
                return True
        
        return False
    
    def _detect_virtual_env(self) -> Optional[str]:
        """Detect if running in a virtual environment."""
        # Check for common virtual environment indicators
        if 'VIRTUAL_ENV' in os.environ:
            return os.environ['VIRTUAL_ENV']
        
        # Check for venv/env directories
        for env_dir in ['venv', 'env', '.venv', '.env']:
            env_path = self.project_root / env_dir
            if env_path.exists() and env_path.is_dir():
                return str(env_path)
        
        return None
    
    def _extract_dependencies(self) -> List[str]:
        """Extract project dependencies."""
        dependencies = []
        
        # Python dependencies
        requirements_files = ['requirements.txt', 'requirements-dev.txt', 'Pipfile']
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    with open(req_path) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Extract package name (before == or >=)
                                pkg = re.split(r'[>=<]', line)[0].strip()
                                if pkg:
                                    dependencies.append(pkg)
                except Exception:
                    pass
        
        # JavaScript dependencies
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    dependencies.extend(deps.keys())
            except Exception:
                pass
        
        return dependencies[:20]  # Limit to avoid too much noise
    
    def format_context_for_display(self, context: DevelopmentContext) -> str:
        """Format the development context for human-readable display."""
        sections = []
        
        sections.append("🚨 **FULL DEVELOPMENT CONTEXT ANALYSIS**")
        sections.append("=" * 50)
        sections.append("*(This is the context ChatGPT never sees!)*\n")
        
        # File context
        if context.file_context:
            sections.append("📁 **File Context:**")
            sections.append(f"  • File: {context.file_context.file_path}")
            if context.file_context.line_number:
                sections.append(f"  • Line: {context.file_context.line_number}")
            if context.file_context.function_name:
                sections.append(f"  • Function: {context.file_context.function_name}()")
            if context.file_context.class_name:
                sections.append(f"  • Class: {context.file_context.class_name}")
            
            if context.file_context.surrounding_code:
                sections.append(f"\n📋 **Code Context:**")
                sections.append("```")
                sections.append(context.file_context.surrounding_code)
                sections.append("```")
            sections.append("")
        
        # Git context
        if context.git_context and context.git_context.is_git_repo:
            sections.append("🔄 **Git Context:**")
            if context.git_context.current_branch:
                sections.append(f"  • Branch: {context.git_context.current_branch}")
            
            if context.git_context.recent_commits:
                sections.append("  • Recent commits:")
                for commit in context.git_context.recent_commits[:3]:
                    sections.append(f"    - {commit}")
            
            if context.git_context.modified_files:
                sections.append("  • Modified files:")
                for file in context.git_context.modified_files[:5]:
                    sections.append(f"    - {file}")
            sections.append("")
        
        # Project context
        if context.project_context:
            sections.append("🏗️ **Project Context:**")
            if context.project_context.language:
                sections.append(f"  • Language: {context.project_context.language}")
            if context.project_context.framework:
                sections.append(f"  • Framework: {context.project_context.framework}")
            if context.project_context.dependencies:
                sections.append(f"  • Key dependencies: {', '.join(context.project_context.dependencies[:5])}")
            if context.project_context.has_tests:
                sections.append("  • Has tests: Yes")
            if context.project_context.virtual_env:
                sections.append(f"  • Virtual env: {context.project_context.virtual_env}")
            sections.append("")
        
        # Environment context
        if context.environment_context:
            sections.append("💻 **Environment:**")
            if context.environment_context.python_version:
                sections.append(f"  • {context.environment_context.python_version}")
            if context.environment_context.node_version:
                sections.append(f"  • Node: {context.environment_context.node_version}")
            if context.environment_context.java_version:
                sections.append(f"  • Java: {context.environment_context.java_version}")
            sections.append("")
        
        sections.append("💡 **Why This Matters:**")
        sections.append("  ✅ ChatGPT only sees the error message you copy")
        sections.append("  ✅ Debuggle sees your entire development context")
        sections.append("  ✅ This leads to more accurate and specific solutions")
        sections.append("  ✅ All analysis happens locally - your code stays private")
        
        return "\n".join(sections)