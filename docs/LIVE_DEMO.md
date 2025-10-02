# 🎬 **Live Demo: See Debuggle Core Beat ChatGPT**

## 🚀 **Quick Start - See It In Action (2 minutes)**

### **1. Generate a Realistic Error**
```bash
cd /home/mikej/debuggle

# Run a demo that creates a realistic IndexError
python demo_errors.py 1
```

### **2. Analyze with Debuggle Core (Our Way)**
```bash
# Get comprehensive analysis with full context:
python demo_errors.py 1 2>&1 | python debuggle_cli.py

# Or save to file and analyze:
python demo_errors.py 1 > demo_error.log 2>&1
python debuggle_cli.py demo_error.log
```

### **3. Compare to ChatGPT (Traditional Way)**
```bash
# What you'd normally copy to ChatGPT:
python demo_errors.py 1

# Just the basic error message - no context!
```

---

## 🎯 **Interactive Demo Scenarios**

### **Demo 1: IndexError in User Management**
```bash
python demo_errors.py 1 2>&1 | python debuggle_cli.py
```
**What You'll See:**
- ✅ **Debuggle Core:** Shows exact code location, surrounding context, project structure
- ❌ **ChatGPT equivalent:** Just "IndexError: list index out of range"

### **Demo 2: KeyError in Configuration**
```bash
python demo_errors.py 2 2>&1 | python debuggle_cli.py
```
**What You'll See:**
- ✅ **Debuggle Core:** Shows missing config key, environment context, recent changes
- ❌ **ChatGPT equivalent:** Just "KeyError: 'password'"

### **Demo 3: AttributeError in API Handling**
```bash
python demo_errors.py 3 2>&1 | python debuggle_cli.py
```

### **Demo 4: ImportError with Dependencies**
```bash
python demo_errors.py 4 2>&1 | python debuggle_cli.py
```

### **Demo 5: TypeError in Data Processing**
```bash
python demo_errors.py 5 2>&1 | python debuggle_cli.py
```

### **Demo 6: FileNotFoundError**
```bash
python demo_errors.py 6 2>&1 | python debuggle_cli.py
```

### **Demo 7: ZeroDivisionError in Metrics**
```bash
python demo_errors.py 7 2>&1 | python debuggle_cli.py
```

---

## 🔥 **Web App Demo (Flask Application)**

### **Start the Demo Flask App**
```bash
# First install Flask (demo dependency)
pip install flask

# Start the buggy demo web app
cd demo_app
python app.py
```

### **Trigger Realistic Web Errors**
```bash
# In another terminal, test the endpoints:

# IndexError demo:
curl http://localhost:5000/users/5 2>&1 | python ../debuggle_cli.py

# KeyError demo:
curl http://localhost:5000/users/1/profile 2>&1 | python ../debuggle_cli.py

# ZeroDivisionError demo:
curl http://localhost:5000/calculate/conversion 2>&1 | python ../debuggle_cli.py

# TypeError demo:
curl http://localhost:5000/process_data 2>&1 | python ../debuggle_cli.py

# AttributeError demo:
curl http://localhost:5000/load_config 2>&1 | python ../debuggle_cli.py
```

---

## 📊 **Side-by-Side Comparison**

### **Run This Command:**
```bash
python demo_errors.py 1 2>&1 | python debuggle_cli.py
```

### **Debuggle Core Output:**
```
🚀 Debuggle CLI - Better than copy/pasting into ChatGPT!
============================================================
🚨 **ERROR ANALYSIS WITH FULL CONTEXT**
==================================================

📋 **Original Error:**
```
IndexError: list index out of range
```

🎯 **Code Context (What you probably didn't paste into ChatGPT):**
```python
    users = ["alice", "bob", "charlie"]
    user_roles = ["admin", "user", "guest", "moderator"] 
    
    for i in range(len(user_roles)):  # This goes 0,1,2,3 but users only has 0,1,2
>>>     print(f"Assigning role {user_roles[i]} to user {users[i]}")
```

🏗️ **Project Context:**
  • Language: python
  • Framework: fastapi
  • Has Tests: Yes
  • Dependencies: fastapi, uvicorn, pydantic, pytest...

🔄 **Recent Changes (Git History):**
  • fa9d5e1 ✨ Implement Jobs-to-Be-Done focused README + coverage boost
  • eb25849 feat: Add enhanced error suggestions

💻 **Environment:**
  • Python 3.12.3
  • Virtual environment: /home/mikej/debuggle/.venv
```

### **What You'd Paste to ChatGPT:**
```
IndexError: list index out of range
```

**See the difference?** Debuggle Core provides 10x more context automatically!

---

## 🎯 **API Demo (Test Our ChatGPT-Killer Endpoint)**

### **Start Debuggle Core Server**
```bash
uvicorn app.main:app --reload
```

### **Test the Enhanced Context Endpoint**
```bash
# Generate an error and analyze it via API:
python demo_errors.py 1 > demo_error.log 2>&1

curl -X POST "http://localhost:8000/api/v1/analyze-with-context" \
  -F "log_input=$(cat demo_error.log)" \
  -F "project_root=$(pwd)"
```

### **Visit the Interactive Docs**
```bash
# Open browser to:
http://localhost:8000/docs

# Try the POST /api/v1/analyze-with-context endpoint
# Paste any error from the demos above
# See the comprehensive analysis vs. what ChatGPT would see
```

---

## 🚀 **Workflow Integration Demo**

### **1. Pipeline Integration**
```bash
# Create a failing test scenario:
echo "def test_broken(): assert 1/0 == 1" > demo_test.py

# Run test and analyze failure:
python -m pytest demo_test.py -v 2>&1 | python debuggle_cli.py

# Clean up:
rm demo_test.py
```

### **2. Log Monitoring Demo**
```bash
# Create a log file with errors:
echo "2025-10-02 14:30:15 ERROR: Database connection failed" > demo.log
echo "2025-10-02 14:30:16 ERROR: KeyError: 'user_id' in session data" >> demo.log

# Watch for new errors (simulate in another terminal):
python debuggle_cli.py --watch demo.log

# In another terminal, add new errors:
echo "2025-10-02 14:31:00 ERROR: IndexError: list index out of range in get_user()" >> demo.log
```

### **3. Git Hook Simulation**
```bash
# Simulate a pre-commit hook:
echo "#!/bin/bash
python demo_errors.py 1 2>&1 | python debuggle_cli.py
echo 'This would prevent commits with unanalyzed errors!'" > demo_hook.sh

chmod +x demo_hook.sh
./demo_hook.sh
```

---

## 💡 **Key Takeaways You'll See**

### **🎯 Context ChatGPT Never Gets:**
- **Surrounding Code:** See exactly where the error occurs
- **Project Structure:** Understand the tech stack and dependencies
- **Environment Details:** Python version, virtual env, OS info
- **Recent Changes:** Git history that might have caused the issue

### **🔒 Privacy Advantages:**
- **Local Processing:** Your code never leaves your machine
- **No API Calls:** No data sent to external services
- **Corporate Safe:** Works behind firewalls and air-gapped environments

### **⚡ Speed & Integration:**
- **Instant Analysis:** No waiting for API responses
- **Workflow Native:** Pipe errors directly from any command
- **Automation Ready:** Can be integrated into any development process

---

## 🎬 **Try It Right Now!**

### **1-Minute Quick Test:**
```bash
# Just run this:
cd /home/mikej/debuggle
python demo_errors.py 1 2>&1 | python debuggle_cli.py
```

### **5-Minute Deep Dive:**
```bash
# Try multiple scenarios:
for i in {1..7}; do
  echo "=== Demo $i ==="
  python demo_errors.py $i 2>&1 | python debuggle_cli.py
  echo ""
done
```

### **10-Minute Full Experience:**
```bash
# Start the API server:
uvicorn app.main:app --reload &

# Try the web interface:
open http://localhost:8000/docs

# Test various endpoints with demo errors
```

**You'll immediately see why this beats copy/pasting into ChatGPT!**