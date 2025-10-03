#!/usr/bin/env python3
"""
Standalone coverage checker with graceful failure handling.

Usage: python check_coverage.py [required_coverage] [actual_coverage] 
Example: python check_coverage.py 40 25.15
"""

import sys
from pathlib import Path

# Add tests directory to path to import our coverage plugin
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

from pytest_coverage_plugin import graceful_coverage_check


def main():
    """Main coverage checking function."""
    
    if len(sys.argv) != 3:
        print("Usage: python check_coverage.py <required_coverage> <actual_coverage>")
        print("Example: python check_coverage.py 40 25.15")
        sys.exit(1)
    
    try:
        required = float(sys.argv[1])
        actual = float(sys.argv[2])
    except ValueError:
        print("Error: Both arguments must be numbers")
        sys.exit(1)
    
    # Use our graceful coverage checker
    success = graceful_coverage_check(required, actual)
    
    if success:
        print("\n🎉 Coverage check passed!")
        sys.exit(0)
    else:
        print("\n💡 Coverage check failed, but handled gracefully.")
        print("Continue working on improving test coverage! 🚀")
        sys.exit(1)


if __name__ == "__main__":
    main()