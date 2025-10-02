#!/bin/bash
# Demo wrapper script - ensures proper environment and paths for running Debuggle demos

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check if we're in the right directory structure
if [[ ! -f "$PROJECT_ROOT/cli/debuggle_cli.py" ]]; then
    echo "❌ Error: Cannot find debuggle_cli.py. Please run this script from the debuggle project."
    exit 1
fi

# Activate virtual environment if it exists
if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
    echo "🔧 Activating virtual environment..."
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo "⚠️  Warning: No virtual environment found at $PROJECT_ROOT/.venv"
fi

# Function to show usage
show_usage() {
    echo "🎬 Debuggle Demo Wrapper"
    echo "========================"
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Available commands:"
    echo "  demo <num>           - Run demo error #num (1-7)"
    echo "  compare <num>        - Run ChatGPT comparison for demo #num"  
    echo "  flask-demo           - Start Flask demo app with bugs"
    echo "  test-cli <logfile>   - Test CLI with log file"
    echo "  health               - Check if everything is working"
    echo ""
    echo "Examples:"
    echo "  $0 demo 1            # Run IndexError demo"
    echo "  $0 compare 2         # Compare KeyError demo with ChatGPT"
    echo "  $0 flask-demo        # Start Flask app for testing"
    echo "  $0 health            # Verify setup"
}

# Function to run demo with proper error handling
run_demo() {
    local demo_num="$1"
    
    if [[ -z "$demo_num" ]]; then
        echo "❌ Error: Please specify demo number (1-7)"
        exit 1
    fi
    
    echo "🚀 Running Demo #$demo_num with full Debuggle analysis..."
    echo "========================================================="
    
    cd "$PROJECT_ROOT/examples"
    
    # Run demo and pipe to debuggle CLI
    if python3 demo_errors.py "$demo_num" 2>&1 | python3 "$PROJECT_ROOT/cli/debuggle_cli.py"; then
        echo ""
        echo "✅ Demo #$demo_num completed successfully!"
    else
        echo "❌ Demo #$demo_num failed. Check the error output above."
        exit 1
    fi
}

# Function to run comparison
run_comparison() {
    local demo_num="$1"
    
    if [[ -z "$demo_num" ]]; then
        echo "❌ Error: Please specify demo number (1-7)"
        exit 1
    fi
    
    echo "🔥 Running ChatGPT vs Debuggle Comparison for Demo #$demo_num"
    echo "=============================================================="
    
    cd "$PROJECT_ROOT/examples"
    
    if python3 compare_chatgpt.py "$demo_num"; then
        echo ""
        echo "✅ Comparison completed successfully!"
    else
        echo "❌ Comparison failed. Check the error output above."
        exit 1
    fi
}

# Function to start Flask demo
run_flask_demo() {
    echo "🌐 Starting Flask Demo App with Intentional Bugs..."
    echo "===================================================="
    echo "The app will start on http://localhost:5000"
    echo "Try these URLs to trigger errors:"
    echo "  http://localhost:5000/users/5           (IndexError)"
    echo "  http://localhost:5000/users/1/profile   (KeyError)"
    echo "  http://localhost:5000/calculate/conversion (ZeroDivisionError)"
    echo "  http://localhost:5000/process_data       (TypeError)"
    echo "  http://localhost:5000/load_config        (AttributeError)"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    cd "$PROJECT_ROOT/examples/demo_app"
    python3 app.py
}

# Function to test CLI with a log file
test_cli() {
    local logfile="$1"
    
    if [[ -z "$logfile" ]]; then
        echo "❌ Error: Please specify a log file"
        exit 1
    fi
    
    if [[ ! -f "$logfile" ]]; then
        echo "❌ Error: Log file '$logfile' not found"
        exit 1
    fi
    
    echo "🔍 Testing Debuggle CLI with log file: $logfile"
    echo "================================================"
    
    python3 "$PROJECT_ROOT/cli/debuggle_cli.py" "$logfile"
}

# Function to check health
check_health() {
    echo "🏥 Debuggle Health Check"
    echo "========================"
    
    local all_good=true
    
    # Check Python
    if python3 --version &>/dev/null; then
        echo "✅ Python 3: $(python3 --version)"
    else
        echo "❌ Python 3 not found"
        all_good=false
    fi
    
    # Check virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo "✅ Virtual Environment: $VIRTUAL_ENV"
    else
        echo "⚠️  No virtual environment active"
    fi
    
    # Check core dependencies
    echo -n "✅ FastAPI: "
    python3 -c "import fastapi; print(fastapi.__version__)" 2>/dev/null || echo "❌ Not found"
    
    echo -n "✅ Flask: "
    python3 -c "import flask; print(flask.__version__)" 2>/dev/null || echo "❌ Not found"
    
    # Check if CLI can import
    echo -n "✅ Debuggle CLI: "
    if python3 -c "import sys; sys.path.append('$PROJECT_ROOT'); from src.debuggle.core.processor import LogProcessor; print('OK')" 2>/dev/null; then
        echo "Imports OK"
    else
        echo "❌ Import failed"
        all_good=false
    fi
    
    # Check project structure
    local required_files=("cli/debuggle_cli.py" "app/main.py" "examples/demo_errors.py")
    for file in "${required_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            echo "✅ $file"
        else
            echo "❌ Missing: $file"
            all_good=false
        fi
    done
    
    echo ""
    if [[ "$all_good" == true ]]; then
        echo "🎉 All systems operational! Ready to run demos."
    else
        echo "⚠️  Some issues detected. See above for details."
    fi
}

# Main command dispatch
case "${1:-}" in
    "demo")
        run_demo "$2"
        ;;
    "compare")
        run_comparison "$2"
        ;;
    "flask-demo")
        run_flask_demo
        ;;
    "test-cli")
        test_cli "$2"
        ;;
    "health")
        check_health
        ;;
    "help"|"-h"|"--help"|"")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac