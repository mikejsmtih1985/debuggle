"""
Test configuration and fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))


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