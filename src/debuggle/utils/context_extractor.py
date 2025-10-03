"""
🕵️ SUPER DETECTIVE CONTEXT INVESTIGATOR - The CSI of Error Analysis! 🕵️

Think of this file as the ultimate crime scene investigation unit that gathers
EVERY possible clue about an error, not just the obvious stuff! While most people
just copy-paste error messages into ChatGPT, this module is like having a forensic
expert who examines fingerprints, DNA, security footage, and witness statements.

🎯 WHAT THIS MODULE DOES:
This is the "CSI: Code Scene Investigation" department of Debuggle! It doesn't just
look at the error message - it investigates the entire "crime scene" to understand
the full story of what went wrong and why.

🔍 THE FORENSIC INVESTIGATION ANALOGY:
- ErrorContext: The complete case file with all evidence
- ContextExtractor: The lead forensic investigator
- extract_full_context(): The comprehensive crime scene analysis
- Git history: Security camera footage showing what happened before
- Surrounding code: Physical evidence at the crime scene
- Dependencies: List of all "suspects" (libraries) that might be involved
- Environment info: The "location details" where the crime occurred

🚀 HOW WE'RE BETTER THAN CHATGPT COPY-PASTE:
1. We examine the actual code around the error (ChatGPT users rarely include this)
2. We check what changed recently (git history - almost never included)
3. We analyze the project structure and dependencies (usually missing)
4. We gather environment details (operating system, Python version, etc.)
5. We create a comprehensive report with ALL the context

Real-world analogy: This is like the difference between calling the police and
saying "someone stole my bike" vs. having a full forensic team investigate with
fingerprints, security footage, witness interviews, and a complete crime scene report!
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
    """
    📁 COMPLETE CASE FILE - All Evidence About the Error!
    
    Think of this as the master case file that a detective assembles with
    ALL the evidence about a crime. Instead of just having the victim's
    statement, we have fingerprints, DNA, security footage, witness
    statements, and background information!
    
    🏆 HIGH SCHOOL EXPLANATION:
    Like a comprehensive school incident report that includes:
    - Where it happened (error_location)
    - What was going on around it (surrounding_code)
    - What happened recently that might be related (recent_changes)
    - What kind of place this is (project_structure)
    - Environmental factors (environment_info)
    - If similar things happened before (similar_errors)
    - Who else was involved (dependencies)
    """
    
    # 📍 CRIME SCENE LOCATION - where exactly did the error occur?
    # Like "Room 205, 3rd floor, near the water fountain"
    error_location: Optional[str] = None
    
    # 📄 EVIDENCE AT THE SCENE - the actual code around the error
    # Like photographing everything within 10 feet of where the incident happened
    surrounding_code: Optional[str] = None
    
    # 📹 SECURITY FOOTAGE - what changed recently in version control
    # Like checking security cameras to see what happened before the incident
    recent_changes: List[str] = None
    
    # 🏗️ BUILDING BLUEPRINT - what kind of project/system is this?
    # Like knowing if the incident happened in a school, hospital, or office building
    project_structure: Dict[str, Any] = None
    
    # 🌡️ ENVIRONMENTAL CONDITIONS - technical environment details
    # Like noting "it was raining, temperature was 75°F, lights were on"
    environment_info: Dict[str, Any] = None
    
    # 📚 SIMILAR CASES - have we seen this type of error before?
    # Like checking police records for similar incidents in the area
    similar_errors: List[str] = None
    
    # 👥 SUSPECTS AND WITNESSES - what libraries and tools are involved?
    # Like listing everyone who was in the building at the time
    dependencies: List[str] = None


class ContextExtractor:
    """
    🔍 MASTER DETECTIVE - The Sherlock Holmes of Error Investigation!
    
    This class is like hiring the world's best detective to investigate your
    programming errors. While most people just look at the error message,
    this detective examines EVERYTHING: the crime scene, the history, the
    environment, the suspects, and builds a complete picture.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like a super-thorough detective who, when investigating
    a bike theft, doesn't just ask "what happened?" but also:
    - Examines the exact location where it was stolen
    - Checks security cameras for recent activity
    - Interviews witnesses and neighbors
    - Studies the neighborhood crime patterns
    - Analyzes the environment and conditions
    - Creates a comprehensive report with all findings
    """
    
    def __init__(self, project_root: Optional[str] = None):
        """
        🏢 SETTING UP THE DETECTIVE OFFICE
        
        When we create a new ContextExtractor, it's like a detective setting up
        their office in a new city - they need to know what area they're
        responsible for investigating.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Like a security guard starting a new job - they need to know which
        building or area they're supposed to watch and protect.
        """
        # 🏠 ESTABLISH OUR INVESTIGATION TERRITORY - what project are we examining?
        # Like a detective being assigned to investigate crimes in a specific district
        # If no specific area is given, we assume it's the current directory
        self.project_root = Path(project_root) if project_root else Path.cwd()
    
    def extract_full_context(self, log_input: str, file_path: Optional[str] = None) -> ErrorContext:
        """
        🔬 THE COMPLETE FORENSIC INVESTIGATION - CSI: Code Scene Investigation!
        
        This is our main investigation method - like a forensic team that conducts
        a complete crime scene analysis. While most people just copy-paste error
        messages into ChatGPT, we conduct a FULL investigation to understand
        the complete story of what went wrong.
        
        🏆 HIGH SCHOOL EXPLANATION:
        Think of this like being a detective investigating a school incident.
        Instead of just asking "what happened?", you:
        1. Find out exactly WHERE it happened
        2. Look at what was going on around that location
        3. Check what happened recently that might be related
        4. Understand what kind of place this is (library? gym? cafeteria?)
        5. Note environmental factors (time of day, weather, etc.)
        6. List who else was involved or nearby
        
        This gives us MORE information than developers typically paste into ChatGPT!
        """
        # 📁 CREATE THE CASE FILE - start with an empty investigation folder
        # Like a detective opening a new case file and preparing to fill it with evidence
        context = ErrorContext()
        
        # 🎯 STEP 1: FIND THE CRIME SCENE - where exactly did this error occur?
        # Like determining the exact room and location where an incident happened
        context.error_location = self._extract_error_location(log_input)
        
        # 🔍 STEP 2: EXAMINE THE IMMEDIATE AREA - what code is around the error?
        # Like photographing everything within 10 feet of where the incident occurred
        if file_path or context.error_location:
            target_file = file_path or self._extract_file_from_location(context.error_location)
            if target_file:
                context.surrounding_code = self._get_surrounding_code(target_file, log_input)
        
        # 📹 STEP 3: CHECK THE SECURITY FOOTAGE - what changed recently?
        # Like reviewing security camera footage from the past few days
        # This is something developers RARELY include when asking ChatGPT!
        context.recent_changes = self._get_recent_changes()
        
        # 🏗️ STEP 4: UNDERSTAND THE BUILDING - what kind of project is this?
        # Like knowing if the incident happened in a school, hospital, or office
        context.project_structure = self._analyze_project_structure()
        
        # 🌡️ STEP 5: RECORD ENVIRONMENTAL CONDITIONS - technical environment details
        # Like noting weather, lighting, temperature, and other conditions
        context.environment_info = self._get_environment_info()
        
        # 👥 STEP 6: LIST ALL SUSPECTS AND WITNESSES - what libraries are involved?
        # Like identifying everyone who was in the building at the time
        context.dependencies = self._extract_dependencies()
        
        # 📋 CASE COMPLETE - return the comprehensive investigation file
        # Like handing over a complete forensic report with all findings
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
        📄 THE COMPREHENSIVE INVESTIGATION REPORT - Our Secret Weapon!
        
        This method takes all our detective work and formats it into a beautiful,
        comprehensive report that contains WAY more information than what people
        typically paste into ChatGPT. This is what makes Debuggle superior!
        
        🏆 HIGH SCHOOL EXPLANATION:
        Think of this like writing the final report for a science project where you:
        1. State the problem clearly
        2. Show all your experimental data
        3. Include background research
        4. Document your methodology
        5. Present your findings with evidence
        6. Draw conclusions based on ALL the information
        
        This is what makes us BETTER than ChatGPT copy/paste - we provide CONTEXT!
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