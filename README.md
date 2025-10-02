# 🐞 Debuggle Core

**Turn "What the hell happened?" into "Ah, I know exactly how to fix this!"**

When you're staring at a cryptic error message at 2 AM, Debuggle Core transforms confusing stack traces into clear, actionable solutions. Get unstuck faster with intelligent error analysis that actually helps you fix bugs instead of just showing you what broke.

---

## 🎯 **What Job Are You Hiring Debuggle For?**

### 😤 **"I'm stuck on this error and don't know what it means"**
**→ Debuggle gives you plain-English explanations + specific fix suggestions**

```
Before: "IndexError: list index out of range" 😕
After:  "🚨 You tried to access position 5 in a list that only has 3 items
         🛠️ Quick fixes:
         1. Check list length: if len(my_list) > index: item = my_list[index]
         2. Use safe indexing: item = my_list[index] if index < len(my_list) else None
         💡 Prevention: Always verify array bounds before accessing elements"
```

### ⏰ **"I'm wasting hours trying to parse this stack trace"**
**→ Debuggle highlights what matters and filters out the noise**

- **Smart cleanup** removes repetitive lines and focuses on your code
- **Key locations highlighted** so you know exactly where to look
- **Exception chain analysis** shows you the root cause, not just symptoms

### 🤯 **"This error spans multiple languages/frameworks"**  
**→ Debuggle speaks Python, JavaScript, Java, C#, C++, Go, and Rust**

- **Auto-detects language** from your logs
- **Cross-language expertise** handles complex polyglot applications
- **Framework-aware** understands Spring, React, Django patterns

### 📚 **"I want to learn from my mistakes"**
**→ Debuggle teaches you patterns to prevent future errors**

- **Prevention tips** for each error type
- **Best practices** linked to official documentation  
- **Pattern recognition** helps you spot similar issues early

### 🚀 **"I need this to work in production"**
**→ Debuggle is battle-tested and production-ready**

- **95% test coverage** with 198 passing tests
- **Rate limiting** and input validation
- **Docker deployment** ready
- **FastAPI performance** handles high throughput

---

## ⚡ **Get Started in 30 Seconds**

### 🌐 **Option 1: Web Interface (Easiest)**
```bash
docker run -p 8000:8000 debuggle/core:latest
# Visit http://localhost:8000 and drag & drop your log file
```

### 🛠️ **Option 2: API Integration**
```bash
curl -X POST "http://localhost:8000/api/v1/beautify" \
  -H "Content-Type: application/json" \
  -d '{"log_input": "Your error message here"}'
```

### 💻 **Option 3: Local Development**
```bash
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle && pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 🎬 **See It In Action**

### Real Example: Python IndexError
**Input:** Messy stack trace
```
Traceback (most recent call last):
  File "app.py", line 14, in <module>
    main()
  File "app.py", line 10, in main
    user = users[999]
IndexError: list index out of range
```

**Debuggle Output:** Actionable insights
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

## 🔥 **Why Developers Choose Debuggle**

### ✅ **Instant Clarity**
- Transform cryptic errors into clear explanations
- Get specific fix suggestions, not just descriptions
- Learn the "why" behind each error

### ✅ **Time Saver**
- Skip the "copy error into Google" step
- Get context-aware solutions immediately
- Focus on fixing, not investigating

### ✅ **Production Ready**
- 95% test coverage ensures reliability
- Docker containerized for easy deployment
- Rate limited and validated for production use

### ✅ **Multi-Language Expert**
- Handles Python, JavaScript, Java, C#, C++, Go, Rust
- Understands framework-specific patterns
- Auto-detects language from log content

---

## 🚀 **Service Tiers: Grow With Your Needs**

| **Core** (Free) | **Pro** ($19/mo) | **Team** ($49/mo) | **Enterprise** (Custom) |
|------------------|-------------------|-------------------|-------------------------|
| ✅ Error analysis | ✅ Everything in Core | ✅ Everything in Pro | ✅ Everything in Team |
| ✅ 15+ error types | ✅ Log grouping | ✅ Persistent storage | ✅ SSO integration |
| ✅ Web + API access | ✅ Pattern detection | ✅ Team dashboards | ✅ Custom integrations |
| ✅ File upload | ✅ Basic storage | ✅ Advanced search | ✅ Compliance features |
| | ✅ Slack alerts | ✅ User management | ✅ Priority support |

---

## 🤝 **Common Use Cases**

### 👨‍💻 **Solo Developer**
*"I'm debugging alone and need quick answers"*
- Use the web interface for one-off error analysis
- Get unstuck on tricky stack traces
- Learn better error handling patterns

### 🏢 **Development Team**  
*"We need to triage errors efficiently"*
- API integration with your monitoring stack
- Consistent error analysis across team members
- Share insights through clear, formatted output

### 🏭 **Production Support**
*"We need to diagnose customer issues fast"*
- Process production logs safely and securely
- Get actionable insights for customer support
- Reduce mean time to resolution (MTTR)

---

## 📊 **Technical Excellence**

### 🧪 **Battle-Tested Quality**
- **95% Code Coverage** - Every feature thoroughly tested
- **198 Passing Tests** - Comprehensive edge case handling
- **Zero Known Bugs** - Production-ready reliability

### ⚡ **Performance Optimized**
- **FastAPI Backend** - High-performance async processing
- **Smart Caching** - Avoid reprocessing similar errors
- **Rate Limited** - Production-safe usage limits

### 🔒 **Security First**
- **Input Validation** - Prevent malicious log injection
- **No Data Storage** - Your logs stay private
- **Configurable Limits** - Prevent resource exhaustion

---

## 🛠️ **API Documentation**

### Quick Integration
```bash
# Health check
curl http://localhost:8000/health

# Analyze error
curl -X POST "http://localhost:8000/api/v1/beautify" \
  -H "Content-Type: application/json" \
  -d '{
    "log_input": "Your error here",
    "language": "auto",
    "options": {"summarize": true, "tags": true}
  }'

# Upload file
curl -X POST "http://localhost:8000/api/v1/upload-log" \
  -F "file=@error.log"
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

## 🚀 **Deployment Options**

### **Docker (Recommended)**
```bash
# Pull and run
docker run -p 8000:8000 debuggle/core:latest

# Docker Compose
docker-compose up
```

### **Local Development**
```bash
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### **Cloud Platforms**
Works seamlessly with AWS Lambda, Google Cloud Run, Azure Container Instances, Fly.io, Railway, Heroku

---

## 📞 **Get Help**

- **📖 Documentation:** http://localhost:8000/docs
- **🐛 Bug Reports:** [GitHub Issues](https://github.com/mikejsmtih1985/debuggle/issues)
- **💬 Discussions:** [GitHub Discussions](https://github.com/mikejsmtih1985/debuggle/discussions)
- **📧 Support:** hello@debuggle.com

---

## 🤝 **Contributing**

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure 95%+ test coverage
5. Submit a pull request

---

**Made with ❤️ by developers who hate cryptic error messages**

*Stop googling error messages. Start fixing them.*