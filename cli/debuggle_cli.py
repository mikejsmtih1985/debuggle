#!/usr/bin/env python3
"""
Debuggle CLI - Command line interface for error analysis.

This demonstrates our competitive advantage over ChatGPT:
- No copy/paste required
- Automatic context extraction
- Privacy-preserving (local processing)
- Integrates with development workflow
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Import from app modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.processor import LogProcessor
from app.core.context import ContextExtractor


def analyze_error_from_file(log_file: str, project_root: Optional[str] = None):
    """Analyze error from log file with full context."""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        if not project_root:
            project_root = os.getcwd()
        
        processor = LogProcessor()
        
        print("🚀 Debuggle CLI - Better than copy/pasting into ChatGPT!")
        print("=" * 60)
        
        # Process with full context
        cleaned_log, summary, tags, metadata, rich_context = processor.process_log_with_context(
            log_input=log_content,
            project_root=project_root,
            highlight=False,  # Terminal friendly
            summarize=True,
            tags=True
        )
        
        print(rich_context)
        
        print("\n" + "=" * 60)
        print("🎯 Why this is better than ChatGPT:")
        print("  ✅ Analyzed your actual project context")
        print("  ✅ No data sent to external services") 
        print("  ✅ Integrated into your development workflow")
        print("  ✅ Automatic - no copy/paste required")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: Log file '{log_file}' not found")
        return False
    except Exception as e:
        print(f"❌ Error processing log: {e}")
        return False


def analyze_error_from_stdin():
    """Analyze error from stdin (pipe support)."""
    try:
        log_content = sys.stdin.read()
        
        if not log_content.strip():
            print("❌ No input provided")
            return False
        
        project_root = os.getcwd()
        processor = LogProcessor()
        
        print("🚀 Debuggle CLI - Analyzing piped error...")
        print("=" * 50)
        
        # Process with context
        cleaned_log, summary, tags, metadata, rich_context = processor.process_log_with_context(
            log_input=log_content,
            project_root=project_root,
            highlight=False,
            summarize=True,
            tags=True
        )
        
        print(rich_context)
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing input: {e}")
        return False


def watch_log_file(log_file: str, project_root: Optional[str] = None):
    """Watch a log file for new errors (basic implementation)."""
    print(f"👀 Watching {log_file} for new errors...")
    print("This demonstrates workflow integration - something ChatGPT can't do!")
    print("Press Ctrl+C to stop")
    
    try:
        import time
        last_size = 0
        
        while True:
            try:
                current_size = os.path.getsize(log_file)
                if current_size > last_size:
                    # New content added
                    with open(log_file, 'r') as f:
                        f.seek(last_size)
                        new_content = f.read()
                    
                    if 'error' in new_content.lower() or 'exception' in new_content.lower():
                        print(f"\n🚨 New error detected at {time.strftime('%H:%M:%S')}")
                        analyze_error_from_stdin_content(new_content, project_root)
                    
                    last_size = current_size
                
                time.sleep(1)
                
            except FileNotFoundError:
                print(f"⏳ Waiting for {log_file} to be created...")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n👋 Stopped watching log file")


def analyze_error_from_stdin_content(content: str, project_root: Optional[str] = None):
    """Helper to analyze content with context."""
    try:
        if not project_root:
            project_root = os.getcwd()
            
        processor = LogProcessor()
        
        cleaned_log, summary, tags, metadata, rich_context = processor.process_log_with_context(
            log_input=content,
            project_root=project_root,
            highlight=False,
            summarize=True,
            tags=True
        )
        
        print(rich_context)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Debuggle CLI - Better error analysis than copy/pasting into ChatGPT",
        epilog="""
Examples:
  debuggle error.log                    # Analyze log file
  debuggle -p /path/to/project error.log # Analyze with specific project root
  python app.py 2>&1 | debuggle         # Pipe errors directly
  debuggle --watch server.log           # Watch log file for new errors
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('logfile', nargs='?', help='Log file to analyze')
    parser.add_argument('-p', '--project-root', help='Project root directory for context')
    parser.add_argument('-w', '--watch', action='store_true', help='Watch log file for new errors')
    parser.add_argument('--version', action='version', version='Debuggle CLI 1.0.0')
    
    args = parser.parse_args()
    
    # Show help if no arguments
    if not args.logfile and sys.stdin.isatty():
        parser.print_help()
        return
    
    success = False
    
    if args.watch and args.logfile:
        # Watch mode
        watch_log_file(args.logfile, args.project_root)
        success = True
        
    elif args.logfile:
        # Analyze file
        success = analyze_error_from_file(args.logfile, args.project_root)
        
    elif not sys.stdin.isatty():
        # Analyze from stdin (piped input)
        success = analyze_error_from_stdin()
        
    else:
        parser.print_help()
        
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()