# 🎬 **Debuggle Core Examples**

This directory contains demonstrations showing how Debuggle Core beats ChatGPT for error analysis.

## 📁 **Contents**

### **Demo Scripts**
- **`demo_errors.py`** - 7 realistic error scenarios for testing
- **`compare_chatgpt.py`** - Side-by-side comparison with ChatGPT
- **`demo_app/`** - Flask web application with intentional bugs

### **Requirements**
- **`requirements.demo.txt`** - Additional dependencies for examples (Flask, etc.)

### **Sample Data**
- **`sample_logs/`** - Example log files for testing

## � **Quick Start**

### **🚀 Easy Way (Recommended): Use Demo Wrapper**
```bash
# From anywhere in the project:
./scripts/demo.sh health              # Check if everything works
./scripts/demo.sh demo 1              # Run IndexError demo  
./scripts/demo.sh compare 2           # Compare KeyError with ChatGPT
./scripts/demo.sh flask-demo          # Start Flask app with bugs
```

### **📋 Available Demo Commands**
```bash
./scripts/demo.sh demo 1        # IndexError Demo
./scripts/demo.sh demo 2        # KeyError Demo  
./scripts/demo.sh demo 3        # AttributeError Demo
./scripts/demo.sh demo 4        # ImportError Demo
./scripts/demo.sh demo 5        # TypeError Demo
./scripts/demo.sh demo 6        # FileNotFoundError Demo
./scripts/demo.sh demo 7        # ZeroDivisionError Demo
```

### **🔍 ChatGPT Comparisons**
```bash
./scripts/demo.sh compare 1     # See what ChatGPT misses vs Debuggle
./scripts/demo.sh compare 2     # KeyError comparison
./scripts/demo.sh compare 3     # AttributeError comparison
# ... etc for all 7 demos
```

### **🌐 Web Application Demo**
```bash
# Start the buggy Flask app:
./scripts/demo.sh flask-demo

# In another terminal, trigger errors:
curl http://localhost:5000/users/5                  # IndexError
curl http://localhost:5000/users/1/profile          # KeyError  
curl http://localhost:5000/calculate/conversion     # ZeroDivisionError
curl http://localhost:5000/process_data             # TypeError
curl http://localhost:5000/load_config              # AttributeError
```

### **🔧 Manual Usage (Advanced)**
```bash
# Activate environment first:
cd /path/to/debuggle && source .venv/bin/activate

# Then run demos:
cd examples
python3 demo_errors.py 1 2>&1 | python3 ../cli/debuggle_cli.py
python3 compare_chatgpt.py 2

# Test with log files:
python3 ../cli/debuggle_cli.py sample_logs/application.log
```

## 🎯 **What You'll See**

### **ChatGPT Input (Limited Context):**
```
IndexError: list index out of range
```

### **Debuggle Core Analysis (Rich Context):**
```
🚨 ERROR ANALYSIS WITH FULL CONTEXT
• Code Context: Shows actual error location with surrounding code
• Recent Changes: Git history that might have caused the issue  
• Project Context: Language, framework, dependencies
• Environment: Python version, virtual env details
• Privacy: 100% local processing
```

## 💡 **Key Demonstrations**

### **🔒 Privacy Advantage**
- All processing happens locally
- No data sent to external APIs
- Corporate/enterprise safe

### **🎯 Context Advantage** 
- Sees surrounding code (ChatGPT doesn't)
- Understands project structure
- Knows your environment details
- Shows recent changes that might be relevant

### **⚡ Workflow Advantage**
- No copy/paste required
- Pipe errors directly from any command
- Integrates into development workflow
- Faster than API calls

## 🔧 **Integration Examples**

### **Terminal Integration**
```bash
# From project root with environment activated:
cd /path/to/debuggle && source .venv/bin/activate

# Any command that might error:
python your_script.py 2>&1 | python cli/debuggle_cli.py

# Process log files:
python cli/debuggle_cli.py server.log
python cli/debuggle_cli.py error.log
```

### **Development Workflow**
```bash
# Pre-commit hook example:
cd /path/to/debuggle && source .venv/bin/activate
python -m pytest 2>&1 | python cli/debuggle_cli.py
```

### **CI/CD Pipeline**
```bash
# GitHub Actions example:
run: |
  cd debuggle && source .venv/bin/activate
  pytest 2>&1 | tee test_output.log
  if [ $? -ne 0 ]; then
    python cli/debuggle_cli.py test_output.log > analysis.md
  fi
```

## � **Comparison Results**

When you run these examples, you'll see:

| **Aspect** | **ChatGPT** | **Debuggle Core** |
|------------|-------------|-------------------|
| **Context** | Basic error only | Full development context |
| **Privacy** | Data sent to OpenAI | 100% local processing |
| **Speed** | 3-10 second API calls | <1 second local analysis |
| **Integration** | Manual copy/paste | Automated workflow |
| **Learning** | Generic responses | Project-aware analysis |

Try the examples and see the difference for yourself!