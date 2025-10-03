#!/usr/bin/env python3
"""
🔧 DEBUGGLE SWISS ARMY KNIFE - The Professional's Portable Debugging Toolkit
============================================================================

This CLI (Command Line Interface) tool is like having a Swiss Army knife for
debugging - a compact, powerful, multi-tool that fits in your pocket and
handles most common debugging tasks without needing a full workshop setup.

🏆 HIGH SCHOOL EXPLANATION:
Think of this like the difference between:
- 🏪 FULL STORE EXPERIENCE: Going to a big department store (web interface)
  - Beautiful displays, helpful staff, comfortable environment
  - Great for browsing and complex tasks
  - Requires time to travel there and navigate

- 🔧 PORTABLE TOOLKIT: Using a Swiss Army knife (this CLI tool)
  - Instant access, no setup required
  - Perfect for quick fixes and emergencies
  - Works anywhere, anytime, in any environment
  - Integrates seamlessly with your existing workflow

🎯 WHY DEBUGGLE CLI BEATS COPY/PASTING TO CHATGPT:

🚫 OLD WORKFLOW (Copy/Paste to ChatGPT):
   1. Error occurs → 2. Copy error text → 3. Open browser → 4. Paste to ChatGPT 
   5. Wait for response → 6. Copy suggestion → 7. Go back to code

✅ NEW WORKFLOW (Debuggle CLI):
   1. Error occurs → 2. Pipe directly: `python app.py 2>&1 | debuggle` → 3. Get instant analysis

🔥 PROFESSIONAL ADVANTAGES:
- 🚀 ZERO FRICTION: No copy/paste, no browser switching, no context loss
- 🔐 PRIVACY FORTRESS: Your code never leaves your computer - enterprise safe
- 🧠 CONTEXT AWARENESS: Sees your entire project structure and files
- ⚡ WORKFLOW INTEGRATION: Works with any terminal, script, or automation
- 🎯 PRECISION ANALYSIS: Understands your specific codebase and patterns

🛠️ SWISS ARMY KNIFE TOOLS:
    debuggle error.log                    # 🔍 File analyzer tool
    python app.py 2>&1 | debuggle         # ⚡ Live error interceptor (the magic!)
    debuggle --watch server.log           # 👁️ Continuous monitoring tool
    debuggle --project /path/to/code      # 🗂️ Project context analyzer
    
EDUCATIONAL METAPHORS USED IN THIS FILE:
🔧 Swiss Army Knife - Multi-purpose tool with many specialized functions
👨‍🔧 Professional Toolkit - Organized collection of specialized instruments  
⚡ Emergency Response - Quick response tools for urgent situations
🔍 Detective Kit - Investigation tools for analyzing evidence
📡 Communication Hub - Connecting different systems and workflows
"""

#
# 🧰 TOOLKIT INVENTORY - Essential instruments for our debugging Swiss Army knife
# ===============================================================================
#
# Like a well-organized professional's toolkit, we need specific instruments
# for different aspects of command-line debugging and error analysis.
#
import argparse     # 🎛️ Command interface controller (handles --help, --version, etc.)
import sys          # 🔧 System integration tools (stdin/stdout pipes, exit codes)
import os           # 🗂️ File system navigator (paths, directories, file operations)
from pathlib import Path        # 🗺️ Modern GPS for file and directory navigation
from typing import Optional     # 📋 Code clarity enhancer (documents what might be None)

#
# 📍 TOOLKIT LOCATION SETUP - Connecting to our main debugging arsenal
# ====================================================================
#
# This is like telling our Swiss Army knife where to find the main toolbox
# so it can access all the specialized debugging instruments and analysis engines.
#
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#
# 🔬 SPECIALIZED ANALYSIS INSTRUMENTS - The core debugging engines
# ================================================================
#
# These are like importing the high-precision instruments from our main
# laboratory - the sophisticated analysis engines that do the actual
# error investigation and context extraction work.
#
from src.debuggle.core.processor import LogProcessor    # 🧠 Master error analysis engine
from src.debuggle.core.context import ContextExtractor  # 🔍 Project context detective


def analyze_error_from_file(log_file: str, project_root: Optional[str] = None):
    """
    🔍 FILE FORENSICS ANALYZER - Professional error investigation from saved evidence
    
    This function is like a crime scene investigator who can analyze evidence
    (log files) to reconstruct what happened and provide expert analysis
    of the situation, complete with context and recommendations.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like being a detective investigating a case:
    1. 📂 Open evidence file (log file) and read all the details
    2. 🗂️ Establish crime scene location (project directory context)
    3. 🔬 Deploy forensic analysis tools (LogProcessor)
    4. 📊 Generate comprehensive investigation report
    5. 💡 Provide actionable recommendations for resolution
    
    Args:
        log_file: Path to the evidence file (error log) to analyze
        project_root: The "crime scene" directory (defaults to current location)
    """
    try:
        # 📂 EVIDENCE COLLECTION - Reading the case file
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 🗺️ CRIME SCENE ESTABLISHMENT - Setting investigation boundaries  
        if not project_root:
            project_root = os.getcwd()  # Use current directory as investigation zone
        
        # 🔬 FORENSIC LAB SETUP - Initialize analysis instruments
        processor = LogProcessor()
        
        # 📢 INVESTIGATION ANNOUNCEMENT - Professional toolkit activation
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