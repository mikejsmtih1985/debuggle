"""
Context Extraction - The "ChatGPT Killer" Intelligence System! 🕵️‍♂️🧠

This is Debuggle's SECRET WEAPON - the system that gathers all the context that
developers NEVER include when they copy/paste errors to ChatGPT. Think of it as
a super-detective that investigates the entire "crime scene" of your error.

When you paste an error to ChatGPT, you give it this:
❌ "My code has an error: NameError: name 'user_id' is not defined"

When Debuggle analyzes the same error, it automatically gathers:
✅ The exact line of code that failed (with surrounding context)
✅ What function and class the error occurred in
✅ Recent git commits that might have caused the issue
✅ Your project structure and dependencies
✅ What programming language and framework you're using  
✅ Your environment setup (Python version, virtual env, etc.)
✅ Related files and imports that might be involved

This is like the difference between:
- Calling 911 and saying "something bad happened" (ChatGPT approach)
- Having a full forensic investigation team with access to security cameras, 
  witness statements, and complete crime scene analysis (Debuggle approach)

The result? Solutions that are specific to YOUR actual codebase, not generic
advice that may or may not apply to your situation!
"""

# Import the Python tools we need - like getting detective equipment
import logging      # For recording our investigation process
import os          # For examining file system and environment  
import re          # For pattern matching in text (like finding clues)
import subprocess  # For running external commands (like git)
import ast         # For parsing Python code structure
from dataclasses import dataclass, field  # For organizing our findings
from pathlib import Path                   # For handling file paths cleanly
from typing import Dict, List, Optional, Any, Tuple, Union  # Type hints for clarity


logger = logging.getLogger(__name__)


@dataclass
class FileContext:
    """
    File Investigation Report - Like a CSI Analysis of the Crime Scene! 🔍📁
    
    This contains all the information we can gather about the specific file
    where the error occurred. It's like a detailed forensic report that includes:
    - The exact location of the incident (file path and line number)
    - Witness statements (surrounding code context)
    - The suspect's identity (function and class names)
    
    This is information that humans almost NEVER include when asking ChatGPT
    for help, but it's crucial for understanding what actually went wrong!
    """
    file_path: str                          # The exact file where the error happened
    line_number: Optional[int] = None       # The specific line that caused trouble
    surrounding_code: Optional[str] = None  # Code around the error (the "crime scene")
    function_name: Optional[str] = None     # Which function the error occurred in
    class_name: Optional[str] = None        # Which class the error occurred in


@dataclass
class GitContext:
    """
    Git Investigation Report - The "Recent History" Detective Work! 📚🔄
    
    This is like examining the "recent activity log" to see what changes might
    have caused the current problem. It's similar to checking security camera
    footage to see what happened in the days leading up to an incident.
    
    This is PURE GOLD for debugging because:
    - Most bugs are caused by recent changes
    - Knowing what branch you're on helps understand the context
    - Seeing modified files shows what you were working on
    
    ChatGPT will NEVER ask you "what did you change recently?" but we do it
    automatically - and this often points directly to the solution!
    """
    is_git_repo: bool = False                        # Are we even tracking changes?
    current_branch: Optional[str] = None             # Which branch are we working on?
    recent_commits: List[str] = field(default_factory=list)   # What changes were made recently?
    modified_files: List[str] = field(default_factory=list)   # What files have been changed?
    last_commit_hash: Optional[str] = None           # The ID of the most recent change


@dataclass
class ProjectContext:
    """
    Project Architecture Analysis - Like Studying the Building Plans! 🏗️📋
    
    This examines the overall structure and setup of your project to understand
    the "big picture" context. It's like an architect studying building plans
    to understand how everything fits together.
    
    This helps us provide solutions that:
    - Match your specific technology stack (Python? Node.js? React?)
    - Work with your framework (Django? Flask? Express?)
    - Consider your dependencies (what libraries you're using)
    - Respect your project structure (where files are organized)
    
    This is context that ChatGPT users almost never provide, but it's often
    essential for giving the right advice!
    """
    root_path: str                                    # Where is your project located?
    project_type: Optional[str] = None               # What kind of project? (web app, CLI tool, etc.)
    language: Optional[str] = None                   # Primary programming language
    framework: Optional[str] = None                  # Web framework or major library
    dependencies: List[str] = field(default_factory=list)     # What packages/libraries you use
    config_files: List[str] = field(default_factory=list)     # Configuration files we found
    has_tests: bool = False                          # Does this project have tests?
    virtual_env: Optional[str] = None                # Are you using a virtual environment?


@dataclass 
class EnvironmentContext:
    """
    Environment Investigation - Like Checking the Weather and Air Quality! 🌡️💻
    
    This examines the "environmental conditions" where your code is running.
    Just like how a doctor needs to know about environmental factors (allergies,
    air quality, temperature) to diagnose an illness, we need to know about
    your computing environment to diagnose coding problems.
    
    Environmental factors that affect code behavior:
    - Python version (different versions behave differently)
    - Virtual environment setup (isolated package versions)
    - System PATH and other environment variables
    - Working directory (affects relative file paths)
    
    This is information that developers rarely think to mention when asking
    for help, but it's often the key to solving mysterious errors!
    """
    python_version: Optional[str] = None             # Which Python version you're running
    node_version: Optional[str] = None               # Which Node.js version (if applicable)
    java_version: Optional[str] = None               # Which Java version (if applicable)
    working_directory: str = "."                     # Where you ran the command from
    environment_variables: Dict[str, str] = field(default_factory=dict)  # System environment settings


@dataclass 
class ErrorContext:
    """Legacy error context for backward compatibility."""
    error_location: Optional[str] = None
    surrounding_code: Optional[str] = None
    recent_changes: List[str] = field(default_factory=list)
    project_structure: Dict[str, Any] = field(default_factory=dict)
    environment_info: Dict[str, Any] = field(default_factory=dict)
    similar_errors: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DevelopmentContext:
    """Complete development context."""
    file_context: Optional[FileContext] = None
    git_context: Optional[GitContext] = None
    project_context: Optional[ProjectContext] = None
    environment_context: Optional[EnvironmentContext] = None
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Add properties for backward compatibility
    @property
    def error_location(self) -> Optional[str]:
        if self.file_context and self.file_context.line_number:
            return f"{self.file_context.file_path}:{self.file_context.line_number}"
        return None
    
    @property
    def surrounding_code(self) -> Optional[str]:
        return self.file_context.surrounding_code if self.file_context else None
    
    @property
    def project_structure(self) -> Dict[str, Any]:
        if self.project_context:
            return {
                'language': self.project_context.language,
                'framework': self.project_context.framework,
                'has_tests': self.project_context.has_tests,
                'config_files': self.project_context.config_files
            }
        return {}
    
    @property
    def dependencies(self) -> List[str]:
        return self.project_context.dependencies if self.project_context else []
    
    @property
    def environment_info(self) -> Dict[str, Any]:
        if self.environment_context:
            return {
                'python_version': self.environment_context.python_version,
                'node_version': self.environment_context.node_version,
                'java_version': self.environment_context.java_version,
                'working_directory': self.environment_context.working_directory,
                **self.environment_context.environment_variables
            }
        return {}


class ContextExtractor:
    """
    The Master Detective - Coordinator of All Context Investigation! 🕵️‍♂️👮‍♀️
    
    This is the \"Chief Detective\" who coordinates multiple investigation units
    to build a complete picture of what went wrong. While ChatGPT only sees the
    error message you copy/paste, this system automatically investigates:
    
    🔍 Crime Scene Unit (FileContext): Examines the exact location of the error
    📚 Historical Unit (GitContext): Investigates recent changes and patterns  
    🏗️ Architecture Unit (ProjectContext): Studies the overall project structure
    🌡️ Environmental Unit (EnvironmentContext): Checks system conditions
    
    This multi-angle investigation approach is what makes Debuggle's solutions
    so much more accurate and specific than generic ChatGPT responses!
    
    The workflow is like a professional investigation:
    1. Set up investigation headquarters (initialize with project root)
    2. Deploy specialized units to gather different types of evidence
    3. Compile comprehensive case file with all findings  
    4. Format the results for easy human understanding
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Set Up Investigation Headquarters - Establish Base of Operations! 🏢🗂️
        
        This is like setting up a detective's command center where all the
        evidence will be collected and analyzed. We establish:
        - The geographical scope of our investigation (project_root)
        - Our case documentation system (logger)
        - Access to all investigation tools and databases
        
        Args:
            project_root: The "jurisdiction" of our investigation - which folder
                         contains the project we're investigating. If not specified,
                         we investigate the current directory (where the user ran the command)
        """
        # Establish our investigation jurisdiction - the project folder we'll examine
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # Set up our case documentation system - like a detective's notebook
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def extract_full_context(self, error_text: str, file_path: Optional[str] = None) -> DevelopmentContext:
        """
        🚀 The Full Investigation - Our ChatGPT-Crushing Comprehensive Analysis! 🔍📊
        
        This is the main event - where we conduct a COMPLETE investigation that gathers
        all the context that developers NEVER include when they ask ChatGPT for help.
        
        Imagine the difference between:
        📋 ChatGPT user: "My code has an error: NameError: name 'user_id' is not defined"
        🕵️ Debuggle investigation: 
          - Exact file and line where error occurred
          - Code surrounding the error (function, class context)
          - Recent git commits that might have caused this
          - Project structure and dependencies
          - Environment setup and configuration
          - Similar patterns from other files
        
        This comprehensive approach is why our solutions are so much more accurate
        and specific than generic ChatGPT responses!
        
        Args:
            error_text: The "initial crime report" - raw error logs or stack traces
            file_path: Optional "crime scene address" - specific file if already known
            
        Returns:
            Complete investigation file with all findings organized and ready for analysis
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
                surrounding_code = self._get_surrounding_code_internal(full_path, line_number)
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
            
            # Get Java version (if available)
            try:
                result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    context.java_version = result.stderr.split('\n')[0] if result.stderr else result.stdout.split('\n')[0]
            except FileNotFoundError:
                # Java not installed - this is optional, so continue gracefully
                context.java_version = None
            
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
            r'at ([^:]+):(\d+):\d+',  # Direct file:line pattern (prioritize this)
            r'at .* \(([^:]+):(\d+):\d+\)',  # Function call pattern
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
    
    def _get_surrounding_code_internal(self, file_path: Path, line_number: int, context_lines: int = 5) -> Optional[str]:
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
            '.gitignore', 'Dockerfile', 'Makefile', 'requirements.txt',
            'requirements-dev.txt', 'pyproject.toml', 'package.json'
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
                                # Extract package name (before == or >= and handle extras like [standard])
                                pkg = re.split(r'[>=<]', line)[0].strip()
                                # Remove extras like [standard] from uvicorn[standard]
                                pkg = re.split(r'\[', pkg)[0].strip()
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
    
    # Backward compatibility methods for existing tests
    def _extract_error_location(self, log_input: str) -> Optional[str]:
        """Extract error location (backward compatibility)."""
        file_path, line_number = self._parse_file_location_from_error(log_input)
        if file_path and line_number:
            return f"{file_path}:{line_number}"
        return None
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure (backward compatibility)."""
        context = self._extract_project_context()
        return {
            'language': context.language or 'unknown',
            'framework': context.framework or 'unknown', 
            'has_tests': context.has_tests,
            'config_files': context.config_files
        }
    
    def _get_dependencies_list(self) -> List[str]:
        """Get dependencies list (backward compatibility).""" 
        context = self._extract_project_context()
        return context.dependencies
    
    def _get_surrounding_code(self, file_path: str, log_input: str) -> Optional[str]:
        """Get surrounding code (backward compatibility method matching test expectations)."""
        try:
            line_number = self._parse_line_number_from_error(log_input)
            if not line_number:
                return None
            return self._get_surrounding_code_internal(Path(file_path), line_number)
        except Exception as e:
            self.logger.error(f"Error getting surrounding code: {e}")
            return None
    
    def format_context_for_analysis(self, context: Union[ErrorContext, DevelopmentContext], log_input: str) -> str:
        """Format context for analysis (backward compatibility)."""
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
        
        # Handle different context types
        if isinstance(context, ErrorContext):
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
        
        elif isinstance(context, DevelopmentContext):
            # Git context
            if context.git_context and context.git_context.recent_commits:
                sections.append("\n🔄 **Recent Changes (Git History):**")
                for change in context.git_context.recent_commits:
                    sections.append(f"  • {change}")
            
            # Project context
            if context.project_context:
                sections.append("\n🏗️ **Project Context:**")
                sections.append(f"  • Language: {context.project_context.language or 'unknown'}")
                sections.append(f"  • Framework: {context.project_context.framework or 'none detected'}")
                sections.append(f"  • Has Tests: {'Yes' if context.project_context.has_tests else 'No'}")
                if context.project_context.config_files:
                    sections.append(f"  • Config Files: {', '.join(context.project_context.config_files)}")
            
            # Dependencies
            if context.project_context and context.project_context.dependencies:
                sections.append("\n📦 **Key Dependencies:**")
                sections.append(f"  {', '.join(context.project_context.dependencies[:10])}")  # Limit to first 10
            
            # Environment
            if context.environment_context:
                sections.append("\n💻 **Environment:**")
                if context.environment_context.python_version:
                    sections.append(f"  • {context.environment_context.python_version}")
                if context.environment_context.node_version:
                    sections.append(f"  • Node: {context.environment_context.node_version}")
                if context.environment_context.java_version:
                    sections.append(f"  • Java: {context.environment_context.java_version}")
        
        sections.append("\n" + "=" * 50)
        sections.append("🎯 **This comprehensive context helps provide more accurate solutions than generic error explanations!**")
        
        return "\n".join(sections)