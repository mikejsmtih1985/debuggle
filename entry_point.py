#!/usr/bin/env python3
"""
Debuggle Entry Point - The main door into the Debuggle application

Think of this file like the front door of a building - it's where everyone enters
and it decides which room (feature) they should go to.

This file provides two main ways to use Debuggle:
1. CLI mode: Type commands in terminal to analyze error logs directly
2. Server mode: Open a web browser to use Debuggle with a nice interface

Default behavior: If you just run "python entry_point.py", it starts a web server
that you can visit at http://localhost:8000 in your browser

Usage examples:
    python entry_point.py                    # Start web server (easiest way)
    python entry_point.py serve --port 8080  # Start server on different port
    python entry_point.py analyze file.log   # Analyze a log file in terminal
"""

# Import the tools we need - like getting ingredients before cooking
import sys        # System tools (like command line arguments)
import os         # Operating system tools (like checking if files exist)
import argparse   # Command line argument parser (handles --port, --help, etc.)
from pathlib import Path  # Modern way to work with file paths

# IMPORTANT: Tell Python where to find our Debuggle code
# This is like telling someone "the kitchen is down the hall" - we're giving
# directions to Python so it knows where to find our Debuggle modules
current_dir = Path(__file__).parent.absolute()  # Get the folder this file is in
sys.path.insert(0, str(current_dir))  # Add it to Python's search path

def main():
    """
    The main function - like the receptionist at a hotel front desk
    
    This function figures out what the user wants to do based on what they typed
    in the command line, then directs them to the right place (serve or analyze).
    """
    # Create an argument parser - think of this like a smart assistant that
    # understands what users type after "python entry_point.py"
    # For example: "python entry_point.py serve --port 8080"
    parser = argparse.ArgumentParser(
        description="🐞 Debuggle - Intelligent Log Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,  # Keeps our formatting nice
        epilog="""
Examples:
  %(prog)s serve                    # Start web server (default)
  %(prog)s serve --port 8080       # Start on custom port
  %(prog)s analyze mylog.txt       # Analyze file via CLI
  %(prog)s --help                  # Show this help
        """
    )
    
    # Create subparsers - these handle different "commands" like "serve" and "analyze"
    # Think of this like having different departments in a store (electronics, clothing, etc.)
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Set up the "serve" command (starts the web server)
    # This is like setting up the "web interface department"
    serve_parser = subparsers.add_parser('serve', help='Start web server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (0.0.0.0 means any computer can connect)')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port number (like apartment number for network connections)')
    serve_parser.add_argument('--reload', action='store_true', help='Restart server when code changes (useful for development)')
    
    # Set up the "analyze" command (command-line analysis)
    # This is like setting up the "quick service department" for direct analysis
    analyze_parser = subparsers.add_parser('analyze', help='Analyze log file via CLI')
    analyze_parser.add_argument('file', help='Path to the log file you want to analyze')
    analyze_parser.add_argument('--project-root', help='Root folder of your project (helps with context)')
    analyze_parser.add_argument('--no-summary', action='store_true', help='Skip creating a summary (faster but less helpful)')
    analyze_parser.add_argument('--no-tags', action='store_true', help='Skip adding tags to errors (faster but less organized)')
    
    # Parse the arguments - this reads what the user typed and organizes it
    # Like a waiter taking your order and writing it down neatly
    args = parser.parse_args()
    
    # If the user didn't specify a command, default to starting the web server
    # This is like saying "if someone walks into a restaurant and doesn't say anything,
    # assume they want to be seated at a table" (rather than takeout)
    if not args.command:
        args.command = 'serve'      # Default action: start web server
        args.host = '0.0.0.0'       # Allow connections from any computer
        args.port = 8000            # Use the standard port
        args.reload = False         # Don't auto-restart (stable mode)
    
    # Now that we know what the user wants, do it!
    # This is like the receptionist directing you to the right department
    if args.command == 'serve':
        # User wants to start the web server
        start_server(args.host, args.port, args.reload)
    elif args.command == 'analyze':
        # User wants to analyze a file directly in the terminal
        # Note: "not args.no_summary" converts --no-summary flag to True/False for summary
        analyze_file(args.file, args.project_root, not args.no_summary, not args.no_tags)
    else:
        # Something went wrong, show help
        parser.print_help()

def start_server(host='0.0.0.0', port=8000, reload=False):
    """
    Start the web server - like opening a restaurant for business
    
    This function starts up a web server that people can visit in their browser
    to use Debuggle's graphical interface. Think of it like opening a restaurant:
    - We set up the kitchen (import the app)
    - We unlock the doors (start the server)
    - We put up a sign saying we're open (print the URL)
    """
    try:
        # Import the tools we need to run the web server
        # uvicorn = the web server engine (like the restaurant's oven and stove)
        # app = our Debuggle application (like the restaurant's menu and recipes)
        import uvicorn
        from src.debuggle.main import app
        
        # Tell the user what's happening - like putting up an "OPEN" sign
        print(f"🚀 Starting Debuggle web server...")
        print(f"📍 URL: http://localhost:{port}")  # Where to visit in browser
        print(f"🖥️  Host: {host}")                  # Which network address we're using
        print(f"🔄  Reload: {reload}")              # Whether we restart when code changes
        print(f"📁  Static files: Drag & drop interface ready!")  # UI features available
        print()
        print("Press Ctrl+C to stop the server")   # How to stop it later
        
        print(f"🌐  Static files and UI will be served by the main app")
        
        # Actually start the server - this is like flipping the "OPEN" switch
        # The server will keep running until the user presses Ctrl+C
        uvicorn.run(
            app,                    # Our Debuggle application
            host=host,              # Network address to listen on
            port=port,              # Port number to listen on
            reload=reload,          # Whether to restart when files change
            access_log=True         # Log who visits the server (for debugging)
        )
        
    except ImportError as e:
        # This happens if we're missing required software (like trying to cook without an oven)
        print(f"❌ Failed to import required modules: {e}")
        print("Make sure all dependencies are installed.")
        sys.exit(1)  # Exit with error code 1 (tells the system something went wrong)
    except Exception as e:
        # This catches any other unexpected problems
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def analyze_file(file_path, project_root=None, summarize=True, tags=True):
    """
    Analyze a log file directly in the terminal - like a doctor examining a patient
    
    This function takes an error log file and analyzes it to figure out what went wrong.
    It's like having a detective look at clues to solve a mystery, but the mystery is
    "why did my code break?"
    
    Parameters:
        file_path: Path to the log file we want to analyze (like a patient file)
        project_root: Folder containing your project (gives context, like patient history)
        summarize: Whether to create a summary (True = yes, False = just raw analysis)
        tags: Whether to add category tags (True = organize findings, False = raw results)
    """
    try:
        # Import the actual analysis function - like calling in a specialist doctor
        from cli.debuggle_cli import analyze_error_from_file
        
        # First, check if the file actually exists - like making sure the patient showed up
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            print("Make sure you typed the file path correctly!")
            sys.exit(1)  # Exit with error - can't analyze a file that doesn't exist
        
        # Tell the user what we're doing - like a doctor explaining the procedure
        print(f"🔍 Analyzing: {file_path}")
        if project_root:
            print(f"📁 Project root: {project_root}")  # Extra context helps with diagnosis
        
        # Do the actual analysis - this is where the magic happens!
        # Like the doctor examining the patient and making a diagnosis
        analyze_error_from_file(file_path, project_root)
        
    except ImportError as e:
        # This happens if we can't find the analysis tools (like a hospital missing equipment)
        print(f"❌ Failed to import CLI modules: {e}")
        print("Make sure all Debuggle components are properly installed.")
        sys.exit(1)
    except Exception as e:
        # This catches any other problems during analysis (like unexpected complications)
        print(f"❌ Analysis failed: {e}")
        print("The log file might be corrupted or in an unexpected format.")
        sys.exit(1)

# This is Python's way of saying "only run this code if someone runs this file directly"
# It's like having a sign on a door that says "Only enter if this is your destination"
# If someone imports this file from another Python script, this part won't run
if __name__ == '__main__':
    main()  # Start the program!