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

### **1. Basic Comparison**
```bash
# See what ChatGPT gets vs. what Debuggle Core analyzes:
python compare_chatgpt.py 1
```

### **2. Try Different Error Types**
```bash
python compare_chatgpt.py 2    # KeyError
python compare_chatgpt.py 3    # AttributeError  
python compare_chatgpt.py 4    # ImportError
python compare_chatgpt.py 5    # TypeError
python compare_chatgpt.py 6    # FileNotFoundError
python compare_chatgpt.py 7    # ZeroDivisionError
```

### **3. Direct CLI Usage**
```bash
# Generate error and pipe to Debuggle Core:
python demo_errors.py 1 2>&1 | ../cli/debuggle_cli.py

# Or save to file first:
python demo_errors.py 2 > error.log 2>&1
../cli/debuggle_cli.py error.log
```

### **4. Web Application Demo**
```bash
# Install demo dependencies:
pip install -r requirements.demo.txt

# Start the buggy Flask app:
cd demo_app && python app.py

# In another terminal, trigger errors:
curl http://localhost:5000/users/5  # IndexError
curl http://localhost:5000/calculate/conversion  # ZeroDivisionError
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
# Any command that might error:
python your_script.py 2>&1 | debuggle

# Watch log files:
debuggle --watch server.log
```

### **Development Workflow**
```bash
# Pre-commit hook example:
python -m pytest 2>&1 | debuggle
```

### **CI/CD Pipeline**
```bash
# GitHub Actions example:
run: |
  pytest 2>&1 | tee test_output.log
  if [ $? -ne 0 ]; then
    debuggle test_output.log > analysis.md
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