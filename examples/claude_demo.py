#!/usr/bin/env python3
"""
🚀 CLAUDE INTEGRATION DEMONSTRATION - See AI Enhancement in Action!

This demo script shows how Debuggle's Claude integration works by generating
realistic error scenarios and showing how the analysis gets enhanced with
Claude AI insights (when available).
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def demo_index_error():
    """Generate a realistic IndexError for demonstration"""
    users = ["Alice", "Bob", "Charlie"]
    
    print("🎬 Demo: Generating IndexError for Claude integration test...")
    print("=" * 60)
    
    try:
        # This will cause an IndexError
        problem_user = users[999]
        print(f"User: {problem_user}")
    except Exception as e:
        # Re-raise with context for Debuggle to analyze
        raise IndexError(f"Attempted to access user index 999, but only {len(users)} users exist") from e

def demo_type_error():
    """Generate a realistic TypeError for demonstration"""
    print("🎬 Demo: Generating TypeError for Claude integration test...")
    print("=" * 60)
    
    user_data = {"name": "Alice", "age": 25}
    
    try:
        # This will cause a TypeError
        result = user_data + " - processed"
        print(result)
    except Exception as e:
        raise TypeError("Cannot concatenate dictionary and string - use string formatting instead") from e

def demo_attribute_error():
    """Generate a realistic AttributeError for demonstration"""
    print("🎬 Demo: Generating AttributeError for Claude integration test...")
    print("=" * 60)
    
    class User:
        def __init__(self, name):
            self.name = name
    
    user = User("Alice")
    
    try:
        # This will cause an AttributeError
        email = user.email_address
        print(f"Email: {email}")
    except Exception as e:
        raise AttributeError("User object has no attribute 'email_address' - did you mean 'email'?") from e

def main():
    """Run the demonstration"""
    print("🤖 Debuggle Claude Integration Demo")
    print("=" * 40)
    print()
    print("This script generates realistic errors to demonstrate")
    print("how Debuggle's Claude integration enhances error analysis.")
    print()
    print("💡 Try these commands:")
    print("   python examples/claude_demo.py 2>&1 | python cli/debuggle_cli.py")
    print("   python examples/claude_demo.py 2>&1 | python cli/debuggle_cli.py --claude")
    print()
    print("The first command shows standard Debuggle analysis.")
    print("The second shows AI-enhanced analysis (requires API key).")
    print()
    print("🎯 Starting error demonstration...")
    print()
    
    # Choose which error to demonstrate based on command line argument
    error_type = sys.argv[1] if len(sys.argv) > 1 else "index"
    
    if error_type == "index":
        demo_index_error()
    elif error_type == "type":
        demo_type_error()
    elif error_type == "attr":
        demo_attribute_error()
    else:
        print(f"Unknown error type: {error_type}")
        print("Available types: index, type, attr")
        demo_index_error()  # Default to IndexError

if __name__ == "__main__":
    main()