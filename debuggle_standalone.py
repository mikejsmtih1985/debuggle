#!/usr/bin/env python3
"""
🤖 DEBUGGLE STANDALONE ENTRY POINT - One CLI to Rule Them All!

This is the unified entry point for standalone Debuggle executables.
It provides both CLI functionality and web server capabilities in a
single executable package.

🏆 HIGH SCHOOL EXPLANATION:
Think of this like a Swiss Army knife - one tool that can do multiple jobs:
- 🔧 Command line tool for piped error analysis  
- 🌐 Web server for drag-and-drop interface
- 🤖 AI-enhanced analysis with Claude integration
- 📊 Database management and error tracking

The user gets one executable that adapts to how they want to use it!
"""

import sys
import os
import argparse
from pathlib import Path

# Add the src directory to the path so we can import debuggle modules
project_root = Path(__file__).parent
if project_root.name == 'dist':  # PyInstaller bundle
    project_root = project_root.parent
sys.path.insert(0, str(project_root / 'src'))

# Now we can import our modules
try:
    from cli.debuggle_cli import main as cli_main
    CLI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ CLI import failed: {e}")
    CLI_AVAILABLE = False

try:
    # Try to import web server functionality
    import uvicorn
    from src.debuggle.main import app as debuggle_app
    WEB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Web server import failed: {e}")
    WEB_AVAILABLE = False

def show_help():
    """Show comprehensive help for all Debuggle functionality"""
    print("""
🤖 Debuggle - Advanced Error Analysis Tool

USAGE:
  debuggle [COMMAND] [OPTIONS]

COMMANDS:
  analyze     Analyze error from stdin or file
  serve       Start web server for drag-and-drop interface  
  help        Show this help message

ERROR ANALYSIS (CLI Mode):
  # Analyze errors from command output
  python your_app.py 2>&1 | debuggle analyze
  
  # With Claude AI enhancement (optional)
  python your_app.py 2>&1 | debuggle analyze --claude
  
  # Analyze from log file
  debuggle analyze --file error.log
  
  # Analyze with project context
  debuggle analyze --file error.log --project-root /path/to/project

WEB INTERFACE (Server Mode):
  # Start web server on default port (8000)
  debuggle serve
  
  # Start on custom port
  debuggle serve --port 8080
  
  # Start with custom host
  debuggle serve --host 0.0.0.0 --port 8000

CLAUDE AI INTEGRATION:
  # Enable Claude AI for enhanced analysis
  export ANTHROPIC_API_KEY=your_key_here
  python your_app.py 2>&1 | debuggle analyze --claude
  
  # Check Claude availability
  debuggle analyze --claude --help

OPTIONS:
  --claude              Enable Claude AI enhanced analysis
  --file FILE          Analyze specific log file
  --project-root PATH  Set project root for context
  --port PORT          Web server port (default: 8000)
  --host HOST          Web server host (default: 127.0.0.1)
  --help               Show help message
  --version            Show version information

EXAMPLES:
  # Basic error analysis
  python app.py 2>&1 | debuggle analyze
  
  # AI-enhanced analysis  
  python app.py 2>&1 | debuggle analyze --claude
  
  # Web interface for multiple files
  debuggle serve
  # Then open http://localhost:8000 and drag-drop files
  
  # Analyze specific file with context
  debuggle analyze --file app.log --project-root .

FEATURES:
  🎯 Smart Error Detection    - Pattern-based error recognition
  🤖 Claude AI Integration   - Optional AI-enhanced analysis  
  🔍 Context Extraction      - Full project context awareness
  📊 SQLite Database         - Persistent error tracking
  🎨 Rich Output            - Beautiful terminal formatting
  🛡️ Privacy First          - Local processing, optional AI
  🌐 Web Interface          - Drag-and-drop file analysis
  ⚡ Fast Performance       - Optimized for real-time analysis

For more information: https://github.com/mikejsmtih1985/debuggle
""")

def main():
    """Main entry point for standalone Debuggle executable"""
    
    # Handle empty arguments
    if len(sys.argv) == 1:
        show_help()
        return 0
    
    # Parse the first argument to determine mode
    command = sys.argv[1].lower()
    
    if command in ['help', '--help', '-h']:
        show_help()
        return 0
        
    elif command == 'version' or command == '--version':
        print("🤖 Debuggle Standalone v1.0.0 (with Claude AI)")
        print("🔗 https://github.com/mikejsmtih1985/debuggle")
        return 0
        
    elif command == 'analyze' or command in ['--claude']:
        # CLI mode - error analysis
        if not CLI_AVAILABLE:
            print("❌ CLI functionality not available in this build")
            return 1
            
        # Remove 'analyze' from args and call CLI main
        if command == 'analyze':
            sys.argv = [sys.argv[0]] + sys.argv[2:]
        
        return cli_main()
        
    elif command == 'serve':
        # Web server mode
        if not WEB_AVAILABLE:
            print("❌ Web server functionality not available in this build")
            return 1
            
        # Parse server arguments
        parser = argparse.ArgumentParser(description='Debuggle Web Server')
        parser.add_argument('--port', type=int, default=8000, help='Port to serve on')
        parser.add_argument('--host', default='127.0.0.1', help='Host to serve on')
        
        # Parse only the server args
        server_args = parser.parse_args(sys.argv[2:])
        
        print(f"🌐 Starting Debuggle web server...")
        print(f"📍 Server: http://{server_args.host}:{server_args.port}")
        print(f"🎯 Open your browser and drag-drop log files to analyze!")
        print(f"⏹️  Press Ctrl+C to stop")
        
        try:
            import uvicorn
            uvicorn.run(debuggle_app, host=server_args.host, port=server_args.port)
        except KeyboardInterrupt:
            print("\n👋 Debuggle server stopped")
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            return 1
            
        return 0
        
    else:
        # Default to CLI analysis for backward compatibility
        if not CLI_AVAILABLE:
            print("❌ CLI functionality not available in this build")
            show_help()
            return 1
            
        # Treat unknown command as potential CLI flag
        return cli_main()

if __name__ == '__main__':
    sys.exit(main())