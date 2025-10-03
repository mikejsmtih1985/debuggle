#!/usr/bin/env python3
"""
Test error file for demonstrating Debuggle analysis
"""

def divide_by_zero():
    """This function will create a division by zero error"""
    x = 10
    y = 0
    result = x / y  # This will cause ZeroDivisionError
    return result

def undefined_variable_error():
    """This function will create a NameError"""
    print(some_undefined_variable)  # This will cause NameError

def main():
    print("Creating test errors for Debuggle...")
    
    try:
        divide_by_zero()
    except Exception as e:
        print(f"Error 1: {e}")
    
    try:
        undefined_variable_error()
    except Exception as e:
        print(f"Error 2: {e}")

if __name__ == "__main__":
    main()