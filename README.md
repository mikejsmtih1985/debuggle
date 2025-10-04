# 🔧 Debuggle - ChatGPT for Debugging Without Leaving Your Terminal

**Debug errors instantly with AI-powered analysis and zero workflow friction.**

> **The Problem**: You hit an error → Copy to ChatGPT → Paste → Wait → Copy solution → Return to code  
> **The Solution**: You hit an error → `python app.py 2>&1 | debuggle` → Get instant analysis with full project context

## ⚡ Quick Start (Actually 30 seconds)

```bash
# 1. Install dependencies
cd debuggle && pip install -r requirements.txt

# 2. Try it immediately  
echo "NameError: name 'x' is not defined" | python cli/debuggle_cli.py

# 3. Use in your workflow
python your_script.py 2>&1 | python cli/debuggle_cli.py
```

**That's it.** No servers, no accounts, no configuration.

## 🎯 Why Use Debuggle Instead of ChatGPT?

| **ChatGPT Workflow** | **Debuggle Workflow** |
|---------------------|----------------------|
| 1. Error occurs | 1. Error occurs |
| 2. Copy error message | 2. Pipe to debuggle |
| 3. Open browser | 3. Get instant analysis |
| 4. Paste to ChatGPT | ✅ **Done** |
| 5. Wait for response | |
| 6. Copy solution back | |
| 7. Return to terminal | |

### 🚀 Core Benefits

- **🔥 Zero Friction**: No copy/paste, no browser switching
- **🔐 100% Private**: Your code never leaves your machine
- **🧠 Project Aware**: Understands your file structure and dependencies  
- **⚡ Terminal Native**: Integrates seamlessly with any development workflow
- **🎯 Context Rich**: Sees more than just the error message

## 🛠️ What It Actually Does

Debuggle analyzes programming errors with three key advantages over generic AI:

### 1. **Project Context Extraction**
```bash
# ChatGPT sees: "NameError: name 'x' is not defined"
# Debuggle sees: Your project structure, imports, recent changes, environment
```

### 2. **Specialized Error Analysis**  
- Detects error patterns across 7+ programming languages
- Provides specific fixes, not generic programming advice
- Educational explanations help you learn, not just fix

### 3. **Workflow Integration**
```bash
# Works with any command that produces errors
python script.py 2>&1 | debuggle
npm test 2>&1 | debuggle
go run main.go 2>&1 | debuggle
mvn compile 2>&1 | debuggle
```

## 🔍 Supported Error Types

### **Python**
IndexError, KeyError, AttributeError, TypeError, ValueError, ImportError, NameError, FileNotFoundError

### **JavaScript**  
ReferenceError, TypeError, SyntaxError, RangeError, and framework-specific errors

### **Java**
NullPointerException, ArrayIndexOutOfBoundsException, ClassNotFoundException

### **Other Languages**
C#, C++, Go, Rust with intelligent pattern recognition

## 🎬 See It In Action

```bash
# Generate a test error
python -c "print(undefined_variable)" 2>&1 | python cli/debuggle_cli.py
```

**Expected Output:**
```
🚨 **NameError Detected**

🔍 **What happened:** Python tried to use a variable that doesn't exist

📋 **Specific issue:** Variable 'undefined_variable' was referenced but never defined

🛠️ **Quick fixes:**
   1. Define the variable: `undefined_variable = "some_value"`
   2. Check for typos in the variable name
   3. Verify the variable is in the right scope

💡 **Prevention:** Always define variables before using them

📚 **Learn more:** Variable scoping and naming conventions
```

## 📦 Installation

### Option 1: From Source (Recommended)
```bash
git clone https://github.com/mikejsmtih1985/debuggle.git
cd debuggle
pip install -r requirements.txt
```

### Option 2: Direct Usage
```bash
# Download and use immediately
wget https://raw.githubusercontent.com/mikejsmtih1985/debuggle/main/cli/debuggle_cli.py
python debuggle_cli.py your_error.log
```

## 🔧 Usage Examples

### Basic Error Analysis
```bash
# Analyze any error output
python script.py 2>&1 | python cli/debuggle_cli.py

# Analyze log files
python cli/debuggle_cli.py error.log

# Chain with other commands
npm test 2>&1 | python cli/debuggle_cli.py
```

### Terminal Aliases (Recommended)
```bash
# Add to ~/.bashrc or ~/.zshrc
alias debug='2>&1 | python /path/to/debuggle/cli/debuggle_cli.py'

# Then use anywhere:
python script.py debug
npm test debug
go run main.go debug
```

## 🤖 Optional: AI Enhancement with Claude

For even deeper analysis, optionally integrate with Claude AI:

```bash
# Install AI dependencies
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Use AI-enhanced analysis
python script.py 2>&1 | python cli/debuggle_cli.py --claude
```

**Benefits of AI Enhancement:**
- Specific code fix suggestions
- Related error pattern insights  
- Prevention strategies
- Learning recommendations

**Privacy Note:** Only error messages are sent to Claude, never your full source code.

## 🧪 Testing

Run the test suite to verify everything works:

```bash
pytest tests/ -v
```

**198 tests covering:**
- Error pattern recognition
- Multi-language support  
- Context extraction
- Output formatting

## 📊 What Makes This Better Than "Just Use ChatGPT"

### **Workflow Integration**
- **Debuggle**: `python app.py 2>&1 | debuggle` (2 seconds)
- **ChatGPT**: Copy → Browser → Paste → Wait → Copy → Back (30+ seconds)

### **Project Context**
- **Debuggle**: Sees your imports, file structure, environment
- **ChatGPT**: Only sees what you manually paste

### **Privacy & Security**
- **Debuggle**: Everything stays on your machine
- **ChatGPT**: Your code goes to external servers

### **Specialized Analysis**
- **Debuggle**: Built specifically for programming errors
- **ChatGPT**: General AI that happens to know programming

## 🤝 Contributing

This is a focused tool with a clear mission. We welcome contributions that:

1. Improve error analysis accuracy
2. Add support for new programming languages
3. Enhance project context extraction
4. Fix bugs in core functionality

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/mikejsmtih1985/debuggle/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mikejsmtih1985/debuggle/discussions)

## 📈 Roadmap

**Current Focus**: Rock-solid CLI experience with perfect error analysis

**Future Possibilities** (after core is perfect):
- VS Code extension integration
- Web interface for teams
- Cloud sharing features
- Advanced analytics

**Philosophy**: Build something 100 developers use daily before building 100 features nobody uses.

---

**Made with ❤️ by developers who got tired of copy-pasting stack traces into ChatGPT.**

*Debuggle: Because debugging should enhance your workflow, not interrupt it.*