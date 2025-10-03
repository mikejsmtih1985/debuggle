"""
Test configuration and fixtures.
"""

import pytest
import sys
import os
from pathlib import Path

# Set testing environment BEFORE any imports that might cache settings
os.environ['DEBUGGLE_ENVIRONMENT'] = 'testing'

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))


@pytest.fixture
def sample_python_error():
    """Sample Python error log for testing."""
    return """Traceback (most recent call last):
  File "app.py", line 14, in <module>
    main()
  File "app.py", line 10, in main
    print(items[5])
IndexError: list index out of range"""


@pytest.fixture
def sample_javascript_error():
    """Sample JavaScript error log for testing."""
    return """ReferenceError: myVariable is not defined
    at Object.<anonymous> (app.js:5:13)
    at Module._compile (module.js:652:30)
    at Object.Module._extensions..js (module.js:663:10)"""


@pytest.fixture
def sample_java_error():
    """Sample Java error log for testing."""
    return """Exception in thread "main" java.lang.NullPointerException
    at com.example.MyClass.main(MyClass.java:15)
    at java.base/java.lang.reflect.Method.invoke(Method.java:568)"""


@pytest.fixture
def large_log_input():
    """Large log input for testing truncation."""
    lines = []
    for i in range(200):
        lines.append(f"Line {i}: Error occurred in processing step {i}")
    return "\n".join(lines)