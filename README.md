# 🐞 Debuggle Core

**Your AI-powered debugging companion that works locally, privately, and instantly**

Stop copying error messages into ChatGPT. Debuggle Core analyzes your errors with full project context, giving you smarter insights than any cloud service - all while keeping your code completely private.

---

## 🎯 **What Development Job Are You Hiring Debuggle For?**

### 😤 **"I hit an error and need to understand it quickly without breaking my flow"**
**→ Debuggle analyzes errors instantly in your terminal with full context**

```bash
# Instead of this workflow:
python app.py   # Error occurs
# Copy error message → Open ChatGPT → Paste → Wait → Get generic advice

# Do this instead:
python app.py 2>&1 | debuggle
# Get instant, contextual analysis with project-specific insights
```

### ⏰ **"I need to debug without context-switching or waiting for APIs"**
**→ Debuggle runs locally and integrates seamlessly into your development workflow**

- **Instant analysis** - no API calls or network delays
- **Terminal integration** - pipe any command's output directly
- **IDE-friendly** - works with any editor or development setup
- **Zero configuration** - works out of the box

### 🔒 **"I can't send my code/errors to external services due to privacy/security"**  
**→ Debuggle processes everything locally with no data transmission**

- **100% private** - your code never leaves your machine
- **Corporate-safe** - no compliance issues or firewall problems
- **Air-gap compatible** - works completely offline
- **No vendor lock-in** - open source and self-hosted

### 🧠 **"I want intelligent analysis, not just error monitoring"**
**→ Debuggle provides educational insights that make you a better developer**

- **Context-aware** - sees your project structure, recent changes, and environment
- **Educational explanations** - learn why errors happen and how to prevent them
- **Pattern recognition** - understand error categories and common fixes
- **Multi-language expertise** - Python, JavaScript, Java, C#, C++, Go, Rust

### � **"I need professional-quality error analysis without the enterprise price tag"**
**→ Debuggle is completely free with no usage limits or feature restrictions**

- **$0 forever** - no subscriptions, usage limits, or hidden costs
- **Full feature access** - get everything, not a limited "free tier"
- **Self-hosted** - no per-seat pricing or team limits
- **Open source** - modify and extend as needed

---

## ⚡ **Get Started in Your Development Workflow**

### 🛠️ **Option 1: CLI Integration (Recommended for Developers)**
```bash
# Install once
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle && pip install -r requirements.txt

# Use anywhere in your development workflow
python your_script.py 2>&1 | python cli/debuggle_cli.py
npm test 2>&1 | python cli/debuggle_cli.py
mvn compile 2>&1 | python cli/debuggle_cli.py
```

### 🌐 **Option 2: Web Interface (For Occasional Use)**
```bash
docker run -p 8000:8000 debuggle/core:latest
# Visit http://localhost:8000 and drag & drop your log file
```

### � **Option 3: Development Server (For Team Sharing)**
```bash
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
# Share http://your-dev-server:8000 with your team
```

---

## 🎬 **See It In Your Development Workflow**

### Real Development Scenario: 
**You're coding and hit an error...**

```bash
# Instead of copying to ChatGPT...
$ python app.py
Traceback (most recent call last):
  File "app.py", line 14, in <module>
    main()
  File "app.py", line 10, in main
    user = users[999]
IndexError: list index out of range

# Just pipe it to Debuggle:
$ python app.py 2>&1 | debuggle
```

**Debuggle gives you context ChatGPT never sees:**
```
🚨 **IndexError Detected**

🔍 **What happened:** You tried to access a position in a list/array that doesn't exist

📋 **Specific details:** Attempted to access index 999, but the list doesn't have that many items

🛠️ **Quick fixes:**
   1. Check list length: `if len(users) > 999: user = users[999]`
   2. Use safe indexing: `user = users[999] if 999 < len(users) else None`
   3. Try-catch approach: `try: user = users[999] except IndexError: user = None`

💡 **Prevention tip:** Always verify array/list bounds before accessing elements

📚 **Learn more:** https://docs.python.org/3/tutorial/errors.html#handling-exceptions
```

---

## 🔥 **Why Developers Choose Debuggle Over ChatGPT for Debugging**

### ✅ **Seamless Workflow Integration**
- **No context switching** - stays in your terminal/IDE
- **Instant results** - no waiting for API calls
- **Command chaining** - `npm test 2>&1 | debuggle` becomes muscle memory
- **Works offline** - debug on planes, trains, or restrictive networks

### ✅ **Superior Context Awareness**
- **Sees your project structure** - knows your framework and dependencies
- **Git integration** - shows recent changes that might have caused issues
- **Environment aware** - understands your Python version, virtual env, etc.
- **Code context** - analyzes surrounding code, not just the error message

### ✅ **Privacy & Security First**
- **Zero data transmission** - your proprietary code stays local
- **Corporate-compliant** - no external API dependencies
- **Audit-friendly** - open source and fully transparent
- **Works behind firewalls** - no network requirements

### ✅ **Developer-Optimized**
- **Fast startup** - ready in seconds, not minutes
- **Terminal-native** - designed for command-line workflows
- **Error pattern learning** - gets smarter with your specific codebase
- **Multi-language** - Python, JS, Java, C#, C++, Go, Rust

---

## 🚀 **Deployment Options: Choose Your Development Setup**

| **Local CLI** (Free) | **Team Server** (Free) | **Enterprise** (Custom) |
|----------------------|------------------------|-------------------------|
| ✅ Full error analysis | ✅ Everything in CLI | ✅ Everything in Team Server |
| ✅ Terminal integration | ✅ Shared team access | ✅ SSO integration |
| ✅ All 7 languages | ✅ Web interface | ✅ Custom deployment |
| ✅ Git context | ✅ API access | ✅ Compliance packages |
| ✅ Offline capable | ✅ Docker deployment | ✅ Priority support |
| ✅ Zero setup | ✅ Team collaboration | ✅ Custom integrations |

**All deployment options are completely free and open source**

---

## 🤝 **Development Workflow Integration**

### 👨‍💻 **Solo Developer Workflow**
*"I need instant error analysis without leaving my terminal"*
```bash
# Add to your .bashrc/.zshrc
alias debug='2>&1 | debuggle'

# Then use anywhere:
python script.py debug
npm test debug  
go run main.go debug
```

### 🏢 **Development Team Setup**  
*"We want consistent error analysis across our team"*
```bash
# One-time team setup
docker run -d -p 8000:8000 debuggle/core:latest
# Everyone uses: curl -X POST team-server:8000/api/v1/beautify

# Or shared CLI setup
git clone https://github.com/mikejsmtih1985/debuggle.git /shared/debuggle
# Add /shared/debuggle/cli to everyone's PATH
```

### 🔧 **CI/CD Integration**
*"We want automatic error analysis in our build pipeline"*
```yaml
# GitHub Actions example
- name: Test with error analysis
  run: |
    npm test 2>&1 | tee test_output.log
    if [ $? -ne 0 ]; then
      python /path/to/debuggle/cli/debuggle_cli.py test_output.log > analysis.md
      # Attach analysis.md to PR or notification
    fi
```

---

## 📊 **Technical Excellence**

### 🧪 **Battle-Tested Quality**
- **Industry-Leading Test Coverage** - Comprehensive testing exceeding industry standards (89%+)
- **400+ Passing Tests** - Thorough edge case handling and quality validation
- **Zero Known Bugs** - Production-ready reliability

*See our [Testing Standards](docs/TESTING_STANDARDS.md) for detailed quality metrics*

### ⚡ **Performance Optimized**
- **FastAPI Backend** - High-performance async processing
- **Smart Caching** - Avoid reprocessing similar errors
- **Rate Limited** - Production-safe usage limits

### 🔒 **Security First**
- **Input Validation** - Prevent malicious log injection
- **No Data Storage** - Your logs stay private
- **Configurable Limits** - Prevent resource exhaustion

---

## 🛠️ **Development Integration Examples**

### Terminal Aliases (Recommended)
```bash
# Add to ~/.bashrc or ~/.zshrc
alias debug-py='python 2>&1 | debuggle'
alias debug-npm='npm 2>&1 | debuggle'  
alias debug-mvn='mvn 2>&1 | debuggle'
alias debug='2>&1 | debuggle'  # Universal

# Usage:
python app.py debug
npm test debug
mvn compile debug
```

### Real-Time Error Monitoring ⚡ NEW!
```bash
# Start the web server
python entry_point.py server

# Open http://localhost:8000 in your browser
# Real-time error notifications appear automatically!

# WebSocket endpoint for custom integrations
ws://localhost:8000/ws/errors

# Check error monitoring status
curl http://localhost:8000/api/v1/errors/stats
```

**Features:**
- **Live error streaming** - See errors as they happen
- **WebSocket notifications** - Real-time updates in the browser
- **Error statistics** - Track error patterns and frequency  
- **Connection monitoring** - Automatic reconnection handling
- **Multi-client support** - Multiple browsers can monitor simultaneously

### API Integration (For Tools/IDEs)
```bash
# Health check
curl http://localhost:8000/health

# Analyze any error output
curl -X POST "http://localhost:8000/api/v1/beautify" \
  -H "Content-Type: application/json" \
  -d '{"log_input": "Your error here", "language": "auto"}'

# Upload log files
curl -X POST "http://localhost:8000/api/v1/upload-log" \
  -F "file=@build.log"
```

**Full API Docs:** Visit `/docs` for interactive Swagger documentation

---

## 🐛 **Supported Error Types**

### **Python**
IndexError, KeyError, AttributeError, TypeError, ValueError, FileNotFoundError, ImportError, ZeroDivisionError, and more

### **JavaScript**  
ReferenceError, TypeError, SyntaxError, RangeError, and framework-specific errors

### **Java**
NullPointerException, ArrayIndexOutOfBoundsException, ClassNotFoundException, ConcurrentModificationException

### **C#**
NullReferenceException, ArgumentException, InvalidOperationException

### **Other Languages**
C++, Go, Rust with intelligent pattern recognition

---

## 🚀 **Development Environment Setup**

### **Local CLI (Individual Developer)**
```bash
# One-time setup
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle && pip install -r requirements.txt

# Add to PATH or create alias
echo 'alias debuggle="python /path/to/debuggle/cli/debuggle_cli.py"' >> ~/.bashrc

# Use immediately
python your_script.py 2>&1 | debuggle
```

### **Team Development Server**
```bash
# Shared team server
docker run -d -p 8000:8000 --name debuggle-team debuggle/core:latest

# Or local development mode
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle && pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```

### **CI/CD Integration**
Perfect for GitHub Actions, GitLab CI, Jenkins, Azure DevOps - any build system that can pipe output to a command

---

## 📞 **Get Help**

- **📖 Documentation:** http://localhost:8000/docs
- **🐛 Bug Reports:** [GitHub Issues](https://github.com/mikejsmtih1985/debuggle/issues)
- **💬 Discussions:** [GitHub Discussions](https://github.com/mikejsmtih1985/debuggle/discussions)
- **📧 Support:** hello@debuggle.com

---

## 🤝 **Contributing**

We welcome contributions! See our [Contributing Guide](docs/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Maintain comprehensive test coverage above industry standards
5. Submit a pull request

---

**Made with ❤️ by developers who got tired of copy-pasting stack traces into ChatGPT**

*Your AI debugging companion that works locally, privately, and instantly - right in your development workflow.*