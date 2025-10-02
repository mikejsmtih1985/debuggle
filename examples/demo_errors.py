#!/usr/bin/env python3
"""
Demo script that generates realistic errors for testing Debuggle Core.
This shows how our tool works better than ChatGPT for error analysis.
"""

import sys
import os
import time
from pathlib import Path

def demo_index_error():
    """Generate a realistic IndexError scenario."""
    print("🎬 Demo 1: IndexError in user management system...")
    
    # This will cause an IndexError
    users = ["alice", "bob", "charlie"]
    user_roles = ["admin", "user", "guest", "moderator"] 
    
    print(f"Loaded {len(users)} users and {len(user_roles)} roles")
    
    # Simulate accessing user by role index (common mistake)
    for i in range(len(user_roles)):  # This goes 0,1,2,3 but users only has 0,1,2
        try:
            print(f"Assigning role {user_roles[i]} to user {users[i]}")
        except IndexError as e:
            print(f"ERROR: {e}")
            raise  # Re-raise to see full traceback

def demo_key_error():
    """Generate a realistic KeyError scenario."""
    print("\n🎬 Demo 2: KeyError in configuration loading...")
    
    # Simulate loading config with missing keys
    config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp"
            # Missing "password" key
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000
        }
    }
    
    print("Loading database configuration...")
    
    # This will cause KeyError
    db_config = {
        "host": config["database"]["host"],
        "port": config["database"]["port"], 
        "name": config["database"]["name"],
        "password": config["database"]["password"]  # KeyError here!
    }

def demo_attribute_error():
    """Generate a realistic AttributeError scenario."""
    print("\n🎬 Demo 3: AttributeError in API response handling...")
    
    class MockResponse:
        def __init__(self, data):
            self.data = data
            self.status_code = 200
    
    # Simulate API response without expected attribute
    response = MockResponse({"users": ["alice", "bob"]})
    
    print("Processing API response...")
    
    # Common mistake - expecting .json() method on custom object
    try:
        data = response.json()  # AttributeError - MockResponse has no json() method
    except AttributeError as e:
        print(f"ERROR: {e}")
        raise

def demo_import_error():
    """Generate a realistic ImportError scenario."""
    print("\n🎬 Demo 4: ImportError with missing dependency...")
    
    try:
        # Try to import something that doesn't exist
        import nonexistent_package
        from missing_module import some_function
    except ImportError as e:
        print(f"ERROR: {e}")
        raise

def demo_type_error():
    """Generate a realistic TypeError scenario."""
    print("\n🎬 Demo 5: TypeError in data processing...")
    
    # Simulate processing mixed data types
    user_ids = [1, 2, 3, "invalid", 5]
    
    print("Processing user IDs...")
    
    total = 0
    for user_id in user_ids:
        print(f"Processing user ID: {user_id}")
        total += user_id * 2  # TypeError when user_id is string

def demo_file_not_found():
    """Generate a realistic FileNotFoundError scenario."""
    print("\n🎬 Demo 6: FileNotFoundError in log processing...")
    
    log_files = ["app.log", "error.log", "missing.log", "debug.log"]
    
    for log_file in log_files:
        print(f"Processing {log_file}...")
        with open(log_file, 'r') as f:  # FileNotFoundError on missing.log
            content = f.read()
            print(f"Read {len(content)} characters")

def demo_zero_division():
    """Generate a realistic ZeroDivisionError scenario."""
    print("\n🎬 Demo 7: ZeroDivisionError in metrics calculation...")
    
    metrics = [
        {"requests": 100, "errors": 5},
        {"requests": 250, "errors": 12}, 
        {"requests": 0, "errors": 0},    # This will cause division by zero
        {"requests": 75, "errors": 2}
    ]
    
    print("Calculating success rates...")
    
    for i, metric in enumerate(metrics):
        success_rate = (metric["requests"] - metric["errors"]) / metric["requests"] * 100
        print(f"Server {i+1}: {success_rate:.1f}% success rate")

def main():
    """Run demo scenarios."""
    demos = [
        ("IndexError Demo", demo_index_error),
        ("KeyError Demo", demo_key_error), 
        ("AttributeError Demo", demo_attribute_error),
        ("ImportError Demo", demo_import_error),
        ("TypeError Demo", demo_type_error),
        ("FileNotFoundError Demo", demo_file_not_found),
        ("ZeroDivisionError Demo", demo_zero_division)
    ]
    
    if len(sys.argv) > 1:
        # Run specific demo by number
        try:
            demo_num = int(sys.argv[1]) - 1
            if 0 <= demo_num < len(demos):
                name, demo_func = demos[demo_num]
                print(f"🚀 Running {name}")
                demo_func()
            else:
                print(f"Demo number must be 1-{len(demos)}")
        except ValueError:
            print("Please provide a valid demo number")
    else:
        # Show available demos
        print("🎬 Available Error Demos for Testing Debuggle Core:")
        print("=" * 50)
        for i, (name, _) in enumerate(demos, 1):
            print(f"{i}. {name}")
        
        print(f"\n💡 Usage:")
        print(f"  python {sys.argv[0]} <demo_number>")
        print(f"\n🔧 Test with Debuggle Core:")
        print(f"  python {sys.argv[0]} 1 2>&1 | python debuggle_cli.py")
        print(f"  python {sys.argv[0]} 2 > error.log && python debuggle_cli.py error.log")

if __name__ == "__main__":
    main()