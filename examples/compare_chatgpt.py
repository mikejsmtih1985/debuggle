#!/usr/bin/env python3
"""
Comparison script: Shows what you'd paste to ChatGPT vs. what Debuggle Core analyzes.
"""

import subprocess
import sys
import os

def show_chatgpt_vs_debuggle(demo_num):
    """Show side-by-side comparison."""
    
    print("🔥 CHATGPT vs DEBUGGLE CORE COMPARISON")
    print("=" * 60)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Run the demo and capture output
    result = subprocess.run([
        sys.executable, "demo_errors.py", str(demo_num)
    ], capture_output=True, text=True, cwd=script_dir)
    
    error_output = result.stderr + result.stdout
    
    # Extract just the error message (what users typically paste to ChatGPT)
    lines = error_output.split('\n')
    error_lines = []
    in_traceback = False
    
    for line in lines:
        if "Traceback" in line:
            in_traceback = True
        if in_traceback:
            error_lines.append(line)
    
    chatgpt_input = '\n'.join(error_lines).strip()
    
    print("❌ WHAT YOU'D PASTE TO CHATGPT:")
    print("-" * 40)
    print(chatgpt_input)
    print()
    
    print("✅ WHAT DEBUGGLE CORE ANALYZES:")
    print("-" * 40)
    
    # Run through Debuggle Core
    venv_python = os.path.join(project_root, ".venv", "bin", "python")
    cli_path = os.path.join(project_root, "cli", "debuggle_cli.py")
    
    debuggle_result = subprocess.run([
        venv_python, cli_path
    ], input=error_output, capture_output=True, text=True, cwd=project_root)
    
    print(debuggle_result.stdout)
    
    print("🎯 THE DIFFERENCE:")
    print("-" * 40)
    print("• ChatGPT: Just the basic error message")
    print("• Debuggle: Full context including:")
    print("  - Surrounding code")
    print("  - Project structure") 
    print("  - Recent git changes")
    print("  - Environment details")
    print("  - Dependencies")
    print("  - All processed locally (private)")

def main():
    """Main comparison script."""
    if len(sys.argv) != 2:
        print("Usage: python compare_chatgpt.py <demo_number>")
        print("Available demos: 1-7")
        sys.exit(1)
    
    try:
        demo_num = int(sys.argv[1])
        if not 1 <= demo_num <= 7:
            print("Demo number must be 1-7")
            sys.exit(1)
        
        show_chatgpt_vs_debuggle(demo_num)
        
    except ValueError:
        print("Please provide a valid demo number (1-7)")
        sys.exit(1)

if __name__ == "__main__":
    main()