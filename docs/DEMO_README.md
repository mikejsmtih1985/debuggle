# 🎬 **See Debuggle Core Beat ChatGPT in Action**

## 🎯 **Quick Demo (30 seconds)**

### **1. Basic Comparison**
```bash
# See the difference side-by-side:
python3 compare_chatgpt.py 1
```

### **2. Try Different Error Types**
```bash
python3 compare_chatgpt.py 2    # KeyError demo
python3 compare_chatgpt.py 3    # AttributeError demo  
python3 compare_chatgpt.py 4    # ImportError demo
python3 compare_chatgpt.py 5    # TypeError demo
python3 compare_chatgpt.py 6    # FileNotFoundError demo
python3 compare_chatgpt.py 7    # ZeroDivisionError demo
```

### **3. Direct CLI Usage**
```bash
# Pipe any error directly:
python3 demo_errors.py 1 2>&1 | .venv/bin/python debuggle_cli.py

# Analyze log files:
python3 demo_errors.py 2 > error.log 2>&1
.venv/bin/python debuggle_cli.py error.log
```

## 🚀 **API Demo**

### **Start the Server**
```bash
.venv/bin/uvicorn app.main:app --reload
```

### **Try the ChatGPT-Killer Endpoint**
```bash
# Visit: http://localhost:8000/docs
# Try: POST /api/v1/analyze-with-context
# Compare output to what ChatGPT would see
```

## 💡 **What You'll See**

### **ChatGPT Input:**
```
IndexError: list index out of range
```

### **Debuggle Core Analysis:**
- 🎯 **Code Context:** Actual error location with surrounding code
- 🔄 **Recent Changes:** Git history that might have caused the issue
- 🏗️ **Project Context:** Language, framework, dependencies
- 💻 **Environment:** Python version, virtual env details
- 📦 **Dependencies:** What packages are actually installed
- 🔒 **Privacy:** All processed locally, no data sent anywhere

## 🎯 **The Key Insight**

**ChatGPT sees:** What you remember to copy
**Debuggle Core sees:** Your entire development context

**Result:** Better analysis, faster fixes, complete privacy!