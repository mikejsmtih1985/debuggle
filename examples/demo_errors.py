#!/usr/bin/env python3
"""
Demo Error Generator - Your Personal Error Training Ground! 🎬🐛

Think of this as a "crash test dummy" program - it purposely creates different types
of errors so you can see how Debuggle analyzes them. It's like a driving school 
for error handling!

This is incredibly valuable for learning because:
- Shows you the MOST COMMON errors programmers encounter (like learning the most frequent driving mistakes)
- Demonstrates how Debuggle analyzes each error type with real context
- Proves why Debuggle is better than copy/pasting errors into ChatGPT
- Gives you safe examples to experiment with (no real harm if things break!)

Each demo represents a real-world scenario where these errors commonly occur:
- IndexError: Lists that don't match up (like trying to assign 4 people to 3 chairs)
- KeyError: Missing configuration values (like looking up a phone number that's not in the directory)
- AttributeError: Objects missing expected methods (like expecting a bicycle to have a steering wheel)
- ImportError: Missing Python packages (like trying to use a recipe ingredient you don't have)
- TypeError: Wrong data types (like trying to add numbers to text)
- FileNotFoundError: Missing files (like trying to read a book that doesn't exist)
- ZeroDivisionError: Division by zero (like trying to split 10 cookies among 0 people)

Perfect for students learning Python - see the error, understand the context, learn the fix!
"""

# Import the Python modules we need - like gathering tools before starting a project
import sys          # System utilities (command-line arguments, exit codes)
import os           # Operating system interface (file operations, paths)
import time         # Time-related functions (delays, timestamps)
from pathlib import Path    # Modern way to handle file and directory paths

def demo_index_error():
    """
    Demonstrate IndexError - The "Musical Chairs" Programming Error! 🪑👥
    
    IndexError happens when you try to access a position in a list that doesn't exist.
    It's like playing musical chairs - if you have 3 chairs but 4 people, someone's 
    going to be left standing (and your program will crash)!
    
    This is one of the MOST COMMON beginner errors in programming.
    Real-world scenario: You're building a user management system and accidentally
    assume that every user has a corresponding role, but the lists don't match up.
    """
    print("🎬 Demo 1: IndexError in user management system...")
    
    # Create our mismatched lists - this is the setup for our "musical chairs" problem
    users = ["alice", "bob", "charlie"]                    # 3 users (indices 0, 1, 2)
    user_roles = ["admin", "user", "guest", "moderator"]   # 4 roles (indices 0, 1, 2, 3)
    
    print(f"Loaded {len(users)} users and {len(user_roles)} roles")
    print("⚠️  Notice: We have more roles than users - this is about to cause problems!")
    
    # The fatal mistake: using the LONGER list to control the loop
    # This is like trying to seat 4 people in 3 chairs - the 4th person has no chair!
    for i in range(len(user_roles)):  # This goes 0, 1, 2, 3 (4 iterations)
        try:
            # When i=3, users[3] doesn't exist! users only has indices 0, 1, 2
            print(f"Assigning role {user_roles[i]} to user {users[i]}")
        except IndexError as e:
            print(f"💥 ERROR: {e}")
            print(f"🔍 What happened: Tried to access users[{i}] but users only has {len(users)} items!")
            print(f"🎯 Fix: Always check list lengths match, or use the shorter list for your loop")
            raise  # Re-raise so Debuggle can analyze the full error context

def demo_key_error():
    """
    Demonstrate KeyError - The "Lost Phone Number" Programming Error! 📞📋
    
    KeyError happens when you try to look up something in a dictionary (like a phone book)
    but that key doesn't exist. It's like trying to find "John Smith" in your contacts
    but you only saved him as "Johnny" - the exact name matters!
    
    This is EXTREMELY common in real applications, especially when:
    - Loading configuration files (some settings might be missing)
    - Processing API responses (fields might be optional)
    - Reading user input (users might skip required fields)
    
    Real-world scenario: Your app expects a database password in the config file,
    but someone forgot to add it. Instead of failing gracefully, your app crashes!
    """
    print("\n🎬 Demo 2: KeyError in configuration loading...")
    
    # Create a configuration dictionary that's missing a crucial piece
    # This is like a recipe that forgot to list one of the ingredients!
    config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "myapp"
            # 🚨 MISSING: "password" key - this will cause our error!
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000
        }
    }
    
    print("Loading database configuration...")
    print("🔍 Available database keys:", list(config["database"].keys()))
    print("⚠️  Notice: 'password' is missing from the configuration!")
    
    # Try to build our database connection - this will fail!
    # It's like trying to log into your email but forgetting your password
    try:
        db_config = {
            "host": config["database"]["host"],        # ✅ This exists
            "port": config["database"]["port"],        # ✅ This exists  
            "name": config["database"]["name"],        # ✅ This exists
            "password": config["database"]["password"] # 💥 This doesn't exist!
        }
    except KeyError as e:
        print(f"💥 ERROR: {e}")
        print(f"🔍 What happened: Tried to find key {e} in the database config, but it doesn't exist!")
        print(f"🎯 Fix: Check if the key exists first with 'in' or use .get() with a default value")
        print(f"    Example: config['database'].get('password', 'default_password')")
        raise  # Re-raise so Debuggle can analyze the full context

def demo_attribute_error():
    """
    Demonstrate AttributeError - The "Wrong Tool for the Job" Programming Error! 🔧🪛
    
    AttributeError happens when you try to use a method or property that doesn't exist
    on an object. It's like trying to use a screwdriver as a hammer - the tool doesn't
    have that capability!
    
    This is SUPER common when:
    - Working with different types of objects that look similar but aren't the same
    - Expecting an object to have methods it doesn't actually have
    - Copying code from one context to another without checking compatibility
    
    Real-world scenario: You're used to working with requests.Response objects that
    have a .json() method, but you're working with a custom object that looks similar
    but doesn't have that method. It's like expecting every car to have a sunroof!
    """
    print("\n🎬 Demo 3: AttributeError in API response handling...")
    
    # Create a custom class that looks like a response but isn't quite the same
    # This is like making a toy car that looks real but doesn't have all the real car parts
    class MockResponse:
        """A fake response object that doesn't have all the methods of a real response."""
        def __init__(self, data):
            self.data = data            # Has data ✅
            self.status_code = 200      # Has status code ✅
            # Missing: .json() method ❌
    
    # Create our mock response - it looks like a real API response but isn't
    response = MockResponse({"users": ["alice", "bob"]})
    
    print("Processing API response...")
    print(f"📊 Response status: {response.status_code}")
    print(f"📦 Response data: {response.data}")
    print("🔍 Available methods:", [method for method in dir(response) if not method.startswith('_')])
    print("⚠️  Notice: .json() method is NOT in the available methods!")
    
    # Try to use it like a real API response - this will fail!
    # It's like trying to roll down the windows on a toy car
    try:
        data = response.json()  # 💥 MockResponse doesn't have a .json() method!
    except AttributeError as e:
        print(f"💥 ERROR: {e}")
        print(f"🔍 What happened: Tried to call .json() on MockResponse, but it doesn't exist!")
        print(f"🎯 Fix: Check what methods are available, or access .data directly")
        print(f"    Working solution: data = response.data  # Use the .data attribute instead")
        raise  # Re-raise so Debuggle can analyze the full context

def demo_import_error():
    """
    Demonstrate ImportError - The "Missing Ingredient" Programming Error! 📦🍽️
    
    ImportError happens when Python can't find a module you're trying to import.
    It's like trying to bake a cake but you're missing flour - you can't proceed
    until you get that essential ingredient!
    
    This is INCREDIBLY common in real projects because:
    - Someone forgot to install a required package (pip install missing_package)
    - You're trying to import from a file that doesn't exist
    - The package name changed or was spelled wrong
    - You're in the wrong directory or environment
    
    Real-world scenario: You copy code from a tutorial or Stack Overflow that uses
    a package you don't have installed. Instead of gracefully telling you what's
    missing, your program just crashes!
    """
    print("\n🎬 Demo 4: ImportError with missing dependency...")
    
    print("🔍 Attempting to import packages that don't exist...")
    print("💡 This is like trying to use a recipe ingredient you don't have in your kitchen!")
    
    try:
        # Try to import something that doesn't exist - like looking for unicorn flour
        print("📦 Trying: import nonexistent_package")
        import nonexistent_package
        
        print("📦 Trying: from missing_module import some_function")
        from missing_module import some_function
        
    except ImportError as e:
        print(f"💥 ERROR: {e}")
        print(f"🔍 What happened: Python searched everywhere but couldn't find this package!")
        print(f"🎯 Fix: Install the missing package with 'pip install package_name'")
        print(f"    Or check if the package name is spelled correctly")
        raise  # Re-raise so Debuggle can analyze the full context

def demo_type_error():
    """
    Demonstrate TypeError - The "Mixing Oil and Water" Programming Error! 🛢️💧
    
    TypeError happens when you try to perform an operation on the wrong type of data.
    It's like trying to multiply a word by a number - Python doesn't know how to do that!
    
    This is EXTREMELY common because:
    - User input is always text (strings), but you need numbers
    - Data from files or databases might come in unexpected formats
    - APIs sometimes return different types than you expect
    - You forget to convert between types (string ↔ number)
    
    Real-world scenario: You're processing user IDs from a form. Most are numbers,
    but some users typed "N/A" or "unknown". Your math operations crash when they
    hit the text values!
    """
    print("\n🎬 Demo 5: TypeError in data processing...")
    
    # Create a list with mixed data types - like having numbers and text in the same box
    user_ids = [1, 2, 3, "invalid", 5]  # First 3 are numbers, 4th is text, 5th is number
    
    print("Processing user IDs...")
    print(f"🔍 Our data: {user_ids}")
    print(f"📊 Data types: {[type(x).__name__ for x in user_ids]}")
    print("⚠️  Notice: Most are 'int' (numbers) but one is 'str' (text)!")
    
    total = 0
    try:
        for user_id in user_ids:
            print(f"Processing user ID: {user_id} (type: {type(user_id).__name__})")
            # This works fine for numbers: 1*2=2, 2*2=4, 3*2=6
            # But crashes on "invalid" * 2 - you can't multiply text by a number!
            total += user_id * 2  # 💥 TypeError when user_id is "invalid"
    except TypeError as e:
        print(f"💥 ERROR: {e}")
        print(f"🔍 What happened: Tried to multiply '{user_id}' (text) by 2 (number)")
        print(f"🎯 Fix: Check data types first, or convert text to numbers")
        print(f"    Example: user_id = int(user_id) if str(user_id).isdigit() else 0")
        raise  # Re-raise so Debuggle can analyze the full context

def demo_file_not_found():
    """
    Demonstrate FileNotFoundError - The "Looking for a Book That's Not There" Error! 📚🔍
    
    FileNotFoundError happens when you try to open a file that doesn't exist.
    It's like going to the library to check out a specific book, but when you get
    to the shelf, that book isn't there!
    
    This is SUPER common in real applications because:
    - Configuration files get moved or deleted
    - Log files haven't been created yet
    - File paths change between different computers (Windows vs. Mac vs. Linux)
    - Users delete files your program expects
    - Typos in file names ("config.txt" vs. "confg.txt")
    
    Real-world scenario: Your app tries to read several log files to generate a report.
    Most files exist, but one is missing. Instead of skipping it or handling it gracefully,
    your entire report generation crashes!
    """
    print("\n🎬 Demo 6: FileNotFoundError in log processing...")
    
    # Create a list of files we want to process - some exist, some don't
    log_files = ["app.log", "error.log", "missing.log", "debug.log"]
    
    print(f"📂 Files to process: {log_files}")
    print("💡 Some of these files don't actually exist - let's see what happens!")
    
    try:
        for log_file in log_files:
            print(f"\n📖 Processing {log_file}...")
            # Try to open each file - this will crash when we hit the missing one
            # It's like trying to open a door that isn't there!
            with open(log_file, 'r') as f:  # 💥 FileNotFoundError on missing.log
                content = f.read()
                print(f"✅ Success! Read {len(content)} characters from {log_file}")
    except FileNotFoundError as e:
        print(f"💥 ERROR: {e}")
        print(f"🔍 What happened: Tried to open '{log_file}' but it doesn't exist!")
        print(f"🎯 Fix: Check if file exists first with os.path.exists() or use try/except")
        print(f"    Example: if os.path.exists(log_file): # only process if file exists")
        raise  # Re-raise so Debuggle can analyze the full context

def demo_zero_division():
    """
    Demonstrate ZeroDivisionError - The "Dividing Pizza Among Zero People" Error! 🍕➡️😵
    
    ZeroDivisionError happens when you try to divide by zero, which is mathematically
    impossible. It's like trying to split 10 cookies among 0 people - how many cookies
    does each person get? The math just doesn't work!
    
    This is VERY common in data analysis and statistics because:
    - Calculating percentages when the total is zero
    - Computing averages when there are no data points
    - Division in loops where the denominator might be zero
    - Edge cases in mathematical formulas
    
    Real-world scenario: You're calculating success rates for your servers. Most servers
    handled requests normally, but one server was down (0 requests). When you try to
    calculate its success rate, you divide by zero and everything crashes!
    """
    print("\n🎬 Demo 7: ZeroDivisionError in metrics calculation...")
    
    # Create server metrics - notice one server has 0 requests (it was down!)
    metrics = [
        {"requests": 100, "errors": 5},    # Normal server: 95% success rate
        {"requests": 250, "errors": 12},   # Busy server: ~95% success rate
        {"requests": 0, "errors": 0},      # 💥 Down server: Can't divide by 0!
        {"requests": 75, "errors": 2}      # Small server: ~97% success rate
    ]
    
    print("📈 Calculating success rates for our servers...")
    print(f"📊 Server metrics: {metrics}")
    print("⚠️  Notice: Server 3 has 0 requests - this will cause division by zero!")
    
    try:
        for i, metric in enumerate(metrics):
            print(f"\n💻 Processing Server {i+1}:")
            print(f"  📊 Requests: {metric['requests']}, Errors: {metric['errors']}")
            
            # This formula works fine when requests > 0
            # But crashes when requests = 0 (you can't divide by zero!)
            success_rate = (metric["requests"] - metric["errors"]) / metric["requests"] * 100
            print(f"  ✅ Server {i+1}: {success_rate:.1f}% success rate")
            
    except ZeroDivisionError as e:
        print(f"💥 ERROR: {e}")
        print(f"🔍 What happened: Tried to divide by {metric['requests']} (which is zero!)")
        print(f"🎯 Fix: Check for zero before dividing, or handle the special case")
        print(f"    Example: success_rate = 0 if requests == 0 else (requests - errors) / requests * 100")
        raise  # Re-raise so Debuggle can analyze the full context

def main():
    """
    Main Menu - Your Error Learning Command Center! 🎮🎯
    
    This function is like a restaurant menu - it shows you all the available "error dishes"
    you can order, and lets you choose which one you want to experience. Each error type
    teaches you something different about programming!
    
    How it works:
    1. If you provide a number (like 'python demo_errors.py 3'), it runs that specific demo
    2. If you don't provide a number, it shows you the menu of all available demos
    3. Each demo crashes on purpose so you can see how Debuggle analyzes real errors!
    
    This is educational gold because you get to:
    - See exactly what each error looks like when it happens
    - Understand the real-world context where these errors occur
    - Practice using Debuggle to analyze and fix the problems
    - Learn without fear (these crashes are intentional and safe!)
    """
    # Create our "menu" of error demonstrations - like a buffet of learning opportunities!
    demos = [
        ("IndexError Demo", demo_index_error),           # The "musical chairs" error
        ("KeyError Demo", demo_key_error),               # The "lost phone number" error 
        ("AttributeError Demo", demo_attribute_error),   # The "wrong tool" error
        ("ImportError Demo", demo_import_error),         # The "missing ingredient" error
        ("TypeError Demo", demo_type_error),            # The "oil and water" error
        ("FileNotFoundError Demo", demo_file_not_found), # The "missing book" error
        ("ZeroDivisionError Demo", demo_zero_division)   # The "dividing by zero" error
    ]
    
    # Check if the user chose a specific demo to run
    if len(sys.argv) > 1:
        # User said "I want demo number X" - let's give it to them!
        try:
            demo_num = int(sys.argv[1]) - 1  # Convert to 0-based index (humans count from 1, computers from 0)
            
            # Make sure they picked a valid demo number
            if 0 <= demo_num < len(demos):
                name, demo_func = demos[demo_num]  # Get the demo name and function
                print(f"🚀 Running {name}")
                print(f"🎭 Get ready to see a realistic {name.split()[0]} in action!")
                print(f"🔮 This will crash on purpose - that's the whole point!")
                demo_func()  # Run the chosen demo function
            else:
                print(f"❌ Demo number must be between 1 and {len(demos)}")
                print(f"📊 Available demos: 1-{len(demos)}")
        except ValueError:
            print("❌ Please provide a valid demo number (like: python demo_errors.py 3)")
            print("🔢 Demo numbers should be integers, not text!")
    else:
        # No specific demo chosen - show the user their options (like a menu)
        print("🎬 Available Error Demos for Testing Debuggle Core:")
        print("🎓 Perfect for learning the most common Python errors!")
        print("=" * 60)
        
        # List all available demos with descriptions
        for i, (name, _) in enumerate(demos, 1):
            print(f"{i}. {name} - Learn about {name.split()[0].lower()}s")
        
        # Show usage instructions - teach users how to use this learning tool
        print(f"\n💡 How to Use This Learning Tool:")
        print(f"  python {sys.argv[0]} <demo_number>")
        print(f"  Example: python {sys.argv[0]} 1  # Run the IndexError demo")
        
        print(f"\n🔧 Advanced: Test with Debuggle Analysis:")
        print(f"  python {sys.argv[0]} 1 2>&1 | python ../cli/debuggle_cli.py")
        print(f"  python {sys.argv[0]} 2 > error.log && python ../cli/debuggle_cli.py error.log")
        print(f"\n🌟 Pro tip: Try each demo, then analyze it with Debuggle to see the magic!")
        print(f"🎯 This shows you why Debuggle is better than copying errors to ChatGPT!")

if __name__ == "__main__":
    main()