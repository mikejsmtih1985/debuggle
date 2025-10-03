#!/usr/bin/env python3
"""
Real-time error generator for testing VS Code integration
"""
import time
import sys

def create_division_error():
    """Generate a division by zero error"""
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(f"Traceback: Division by zero in line 12")

def create_name_error():
    """Generate a name error"""
    try:
        print(undefined_variable)
    except NameError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(f"Traceback: undefined_variable is not defined")

def create_type_error():
    """Generate a type error"""
    try:
        result = "string" + 42
    except TypeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(f"Traceback: cannot concatenate str and int")

def main():
    print("🧪 Testing VS Code Integration - Generating Errors...")
    print("Watch your VS Code Problems panel for real-time updates!")
    print()
    
    print("1. Generating Division Error...")
    create_division_error()
    time.sleep(2)
    
    print("2. Generating Name Error...")  
    create_name_error()
    time.sleep(2)
    
    print("3. Generating Type Error...")
    create_type_error()
    time.sleep(2)
    
    print("✅ Done! Check VS Code Problems panel for all errors.")

if __name__ == "__main__":
    main()