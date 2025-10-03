#!/usr/bin/env python3
"""
🚉 DEBUGGLE CENTRAL STATION - The Main Transportation Hub
========================================================

This entry_point.py file is like the main terminal at a major airport or train station -
it's the central hub where all passengers (users) arrive and get directed to their
correct destination (web interface or command-line tools).

🏆 HIGH SCHOOL EXPLANATION:
Think of this like the main information desk at a large airport:
- Passengers arrive with different needs (analyze files, start server, get help)
- The information agent (this script) asks what they want to do
- Based on their answer, they get directed to the right terminal/gate
- Some want the full-service experience (web browser interface)
- Others prefer the express route (command-line analysis)

This file provides multiple transportation methods to reach your debugging destination:

🌐 LUXURY EXPRESS SERVICE (Web Interface):
    python entry_point.py                    # First-class web experience
    python entry_point.py serve --port 8080  # Custom departure gate

⚡ RAPID TRANSIT (Command Line):
    python entry_point.py analyze file.log   # Direct express route to results

🆘 INFORMATION SERVICES:
    python entry_point.py --help            # Station directory and schedules

EDUCATIONAL METAPHORS USED IN THIS FILE:
🚉 Transportation Hub - Central station directing traffic to destinations
🎫 Ticket Counter - Command-line argument processing and validation
🚌 Route Planning - Deciding which service (web/CLI) to launch
📢 Station Announcements - User feedback and status messages
🧳 Baggage Handling - File processing and path management
"""

#
# 🧳 STATION EQUIPMENT AND SUPPLIES - Essential tools for running our transportation hub
# ====================================================================================
#
# Like a well-equipped train station needs ticketing systems, announcement boards,
# and navigation tools, our entry point needs these Python modules to operate.
#
import sys        # 🎛️ System control panel (command line arguments, Python paths)
import os         # 🗂️ File system navigator (checking files, directories, permissions)
import argparse   # 🎫 Ticket booth system (processes user commands and options)
from pathlib import Path  # 🗺️ Modern GPS navigation for file paths and directories

#
# 📍 STATION DIRECTORY SETUP - Telling Python where to find our services
# ======================================================================
#
# This is like posting clear directional signs throughout the station so
# passengers (and Python) can find the right departments and services.
# Without these directions, Python wouldn't know where our Debuggle
# modules are located.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like setting up GPS navigation in a car:
# 1. Figure out where we are now (current_dir = where this file lives)
# 2. Add our location to the "places Python knows about" (sys.path)
# 3. Now Python can find and import our custom Debuggle modules
#
current_dir = Path(__file__).parent.absolute()  # 📍 Determine our station's location
sys.path.insert(0, str(current_dir))           # 🗺️ Add to Python's navigation system

def main():
    """
    🎫 CENTRAL DISPATCH CENTER - The main traffic controller for all Debuggle services
    
    This function is like the master control room at a major transportation hub
    that coordinates all incoming requests and routes them to the appropriate
    service departments based on what passengers (users) need.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like the main operator at a large company who answers the phone:
    - Customer calls and says what they want
    - Operator asks clarifying questions if needed  
    - Based on the request, transfers them to the right department
    - Web interface department: "I want the full graphical experience"
    - Command-line department: "Just analyze this file quickly"
    - Help desk: "I'm not sure what I can do"
    
    The function processes command-line arguments (what the user typed) and
    routes them to the correct service handler.
    """
    
    # 🎫 SMART TICKETING SYSTEM - Understanding what users want
    # ========================================================
    #
    # This argument parser is like having an intelligent ticket machine that
    # can understand different requests and provide appropriate options.
    # It handles complex commands like "python entry_point.py serve --port 8080"
    #
    parser = argparse.ArgumentParser(
        description="🐞 Debuggle - Intelligent Log Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,  # 📋 Preserve formatting for help text
        epilog="""
🚀 TRANSPORTATION OPTIONS:

  %(prog)s serve                    # 🌐 Launch luxury web interface (most popular)
  %(prog)s serve --port 8080       # 🚪 Custom departure gate (different port)
  %(prog)s analyze mylog.txt       # ⚡ Express command-line service  
  %(prog)s --help                  # 📚 Station information and schedules
        """
    )
    
    # 🏢 DEPARTMENT DIRECTORY - Setting up specialized service counters
    # ================================================================
    #
    # Subparsers are like having different service counters in a large facility:
    # - Counter #1: Web Interface Services ("serve" command)
    # - Counter #2: Express Analysis Services ("analyze" command)  
    # - Counter #3: Information Services ("help" command)
    #
    # Each counter has its own specialists who understand specific types of requests.
    #
    subparsers = parser.add_subparsers(dest='command', help='Available service departments')
    
    # 🌐 WEB INTERFACE SERVICE COUNTER - Full-featured graphical experience
    # ====================================================================
    #
    # This sets up the "luxury service" counter where users can request
    # the full web interface experience with all visual features and
    # interactive capabilities.
    #
    serve_parser = subparsers.add_parser('serve', help='🌐 Start web interface server')
    
    # 🏠 HOST CONFIGURATION - Which address to broadcast from
    serve_parser.add_argument('--host', default='0.0.0.0', 
                             help='🌍 Network address (0.0.0.0 = accept connections from anywhere)')
    
    # 🚪 PORT CONFIGURATION - Which "doorway" to use for connections  
    serve_parser.add_argument('--port', type=int, default=8000,
                             help='🔢 Network port number (like apartment number for internet connections)')
    
    # 🔄 DEVELOPMENT MODE - Auto-restart when files change
    serve_parser.add_argument('--reload', action='store_true',
                             help='🔧 Development mode (restart when code changes - like hot reload)')
    
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
        from src.debuggle.app_factory import create_app
        app = create_app()
        
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