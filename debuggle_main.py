#!/usr/bin/env python3
"""
Debuggle Entry Point - Unified entry point for both CLI and web server modes
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path so we can import our modules
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

def main():
    """Main entry point that handles both CLI and server modes"""
    parser = argparse.ArgumentParser(
        description="🐞 Debuggle - Intelligent Log Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s serve                    # Start web server (default)
  %(prog)s serve --port 8080       # Start on custom port
  %(prog)s analyze mylog.txt       # Analyze file via CLI
  %(prog)s --help                  # Show this help
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Serve command (web server)
    serve_parser = subparsers.add_parser('serve', help='Start web server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    serve_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    # Analyze command (CLI mode)
    analyze_parser = subparsers.add_parser('analyze', help='Analyze log file via CLI')
    analyze_parser.add_argument('file', help='Log file to analyze')
    analyze_parser.add_argument('--project-root', help='Project root directory')
    analyze_parser.add_argument('--no-summary', action='store_true', help='Skip summary generation')
    analyze_parser.add_argument('--no-tags', action='store_true', help='Skip tag generation')
    
    args = parser.parse_args()
    
    # Default to serve if no command specified
    if not args.command:
        args.command = 'serve'
        args.host = '0.0.0.0'
        args.port = 8000
        args.reload = False
    
    if args.command == 'serve':
        start_server(args.host, args.port, args.reload)
    elif args.command == 'analyze':
        analyze_file(args.file, args.project_root, not args.no_summary, not args.no_tags)
    else:
        parser.print_help()

def start_server(host='0.0.0.0', port=8000, reload=False):
    """Start the FastAPI web server"""
    try:
        import uvicorn
        from app.main import app
        
        print(f"🚀 Starting Debuggle web server...")
        print(f"📍 URL: http://localhost:{port}")
        print(f"🖥️  Host: {host}")
        print(f"🔄  Reload: {reload}")
        print(f"📁  Static files: Drag & drop interface ready!")
        print()
        print("Press Ctrl+C to stop the server")
        
        print(f"🌐  Static files and UI will be served by the main app")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("Make sure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def analyze_file(file_path, project_root=None, summarize=True, tags=True):
    """Analyze a log file via CLI"""
    try:
        from cli.debuggle_cli import analyze_error_from_file
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        
        print(f"🔍 Analyzing: {file_path}")
        if project_root:
            print(f"📁 Project root: {project_root}")
        
        analyze_error_from_file(file_path, project_root)
        
    except ImportError as e:
        print(f"❌ Failed to import CLI modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()