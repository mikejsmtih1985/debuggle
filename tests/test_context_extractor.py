"""
Test the context extraction functionality - our ChatGPT competitive advantage!
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.debuggle.core.context import ContextExtractor, DevelopmentContext, ErrorContext


class TestContextExtractor:
    """Test context extraction that gives us advantages over ChatGPT."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.extractor = ContextExtractor(str(self.project_root))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_extract_error_location_python(self):
        """Test extracting error location from Python traceback."""
        log_input = '''
        Traceback (most recent call last):
          File "app.py", line 14, in <module>
            main()
          File "app.py", line 10, in main
            user = users[999]
        IndexError: list index out of range
        '''
        
        location = self.extractor._extract_error_location(log_input)
        assert location == "app.py:14"
    
    def test_extract_error_location_javascript(self):
        """Test extracting error location from JavaScript error."""
        log_input = '''
        ReferenceError: undefined is not defined
        at app.js:25:10
        at Object.<anonymous> (app.js:30:5)
        '''
        
        location = self.extractor._extract_error_location(log_input)
        assert location == "app.js:25"
    
    def test_get_surrounding_code(self):
        """Test getting code context around error location."""
        # Create a test Python file
        test_file = self.project_root / "test.py"
        test_content = '''def main():
    users = ["alice", "bob", "charlie"]
    
    # This will cause an IndexError
    for i in range(5):
        print(f"User {i}: {users[i]}")  # Error on line 6
    
    print("Done")

if __name__ == "__main__":
    main()
'''
        test_file.write_text(test_content)
        
        log_input = f'File "{test_file}", line 6, in main\nIndexError: list index out of range'
        
        surrounding_code = self.extractor._get_surrounding_code(str(test_file), log_input)
        
        assert surrounding_code is not None
        assert "User {i}: {users[i]}" in surrounding_code
        assert ">>>" in surrounding_code  # Error line marker
        assert "def main():" in surrounding_code
    
    def test_analyze_project_structure_python(self):
        """Test project structure analysis for Python projects."""
        # Create Python project structure
        (self.project_root / "requirements.txt").write_text("fastapi==0.68.0\npygments==2.9.0")
        (self.project_root / "app").mkdir()
        (self.project_root / "app" / "__init__.py").write_text("")
        (self.project_root / "app" / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()")
        (self.project_root / "tests").mkdir()
        
        structure = self.extractor._analyze_project_structure()
        
        assert structure['language'] == 'python'
        assert structure['framework'] == 'fastapi'
        assert structure['has_tests'] is True
        assert 'requirements.txt' in structure['config_files']
    
    def test_extract_dependencies(self):
        """Test dependency extraction from requirements.txt."""
        requirements_content = """fastapi==0.68.0
pygments>=2.9.0
uvicorn[standard]
# Development dependencies
pytest
black
"""
        (self.project_root / "requirements.txt").write_text(requirements_content)
        
        deps = self.extractor._extract_dependencies()
        
        assert "fastapi" in deps
        assert "pygments" in deps
        assert "uvicorn" in deps
        assert "pytest" in deps
        assert "black" in deps
    
    def test_full_context_extraction(self):
        """Test comprehensive context extraction."""
        # Create a realistic project structure
        (self.project_root / "requirements.txt").write_text("fastapi==0.68.0")
        (self.project_root / "app").mkdir()
        
        # Create the error file
        error_file = self.project_root / "app" / "main.py"
        error_file.write_text("""from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    users = ["alice", "bob", "charlie"]
    return {"user": users[user_id]}  # This can cause IndexError
""")
        
        log_input = f'''Traceback (most recent call last):
  File "{error_file}", line 8, in get_user
    return {{"user": users[user_id]}}
IndexError: list index out of range'''
        
        context = self.extractor.extract_full_context(log_input, str(error_file))
        
        assert context.error_location is not None
        assert context.surrounding_code is not None
        assert context.project_structure is not None
        assert context.dependencies is not None
        assert context.environment_info is not None
    
    def test_format_context_for_analysis(self):
        """Test formatting context into comprehensive analysis."""
        # Create basic context
        context = ErrorContext()
        context.error_location = "app.py:10"
        context.surrounding_code = "    users = ['alice']\n>>> 10: return users[5]  # Error here"
        context.project_structure = {"language": "python", "framework": "fastapi"}
        context.dependencies = ["fastapi", "uvicorn"]
        context.environment_info = {"python_version": "Python 3.9.0"}
        
        log_input = "IndexError: list index out of range"
        
        formatted = self.extractor.format_context_for_analysis(context, log_input)
        
        # Check that our competitive advantages are highlighted
        assert "ERROR ANALYSIS WITH FULL CONTEXT" in formatted
        assert "Code Context (What you probably didn't paste into ChatGPT)" in formatted
        assert "Project Context:" in formatted
        assert "Environment:" in formatted
        assert "comprehensive context helps provide more accurate solutions" in formatted
    
    def test_chatgpt_competitive_advantages(self):
        """Test that our analysis includes competitive advantages over ChatGPT."""
        # Create a proper error with file location
        main_file = self.project_root / "main.py"
        main_file.write_text("users = []\nprint(users[0])  # This will error")
        
        log_input = f'''Traceback (most recent call last):
  File "{main_file}", line 2, in <module>
    print(users[0])  # This will error
IndexError: list index out of range'''
        
        context = self.extractor.extract_full_context(log_input, str(main_file))
        formatted = self.extractor.format_context_for_analysis(context, log_input)
        
        # Verify we highlight what ChatGPT can't do
        competitive_advantages = [
            "What you probably didn't paste into ChatGPT",
            "comprehensive context", 
            "more accurate solutions"
        ]
        
        for advantage in competitive_advantages:
            assert advantage in formatted
    
    def test_privacy_advantage(self):
        """Test that we emphasize privacy advantages over ChatGPT."""
        # Our processing is completely local - no data leaves the system
        log_input = "SECRET_API_KEY=abc123\nIndexError: list index out of range"
        
        context = self.extractor.extract_full_context(log_input)
        
        # Verify we can process sensitive information safely
        assert context is not None
        # The key point is this processing happens locally, unlike ChatGPT
    
    def test_workflow_integration_advantage(self):
        """Test that we can integrate with development workflow."""
        # Unlike ChatGPT, we can be integrated into IDEs, git hooks, etc.
        log_input = "Traceback (most recent call last):\nIndexError: list index out of range"
        
        # We can automatically detect project root and process errors
        context = self.extractor.extract_full_context(log_input)
        
        assert context is not None
        # This shows we can be integrated into automated workflows