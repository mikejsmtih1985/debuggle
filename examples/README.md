# Examples Directory

This directory contains sample log files, code examples, and usage demonstrations for Debuggle.

## 📁 Contents

### 📋 Sample Log Files (`logs/`)
Real-world log file examples for testing and demonstration:
- **application.log** - Standard application logs
- **error.log** - Error-focused log entries  
- **nginx-access.log** - Web server access logs
- **database.log** - Database query and error logs
- **json-logs.log** - Structured JSON log entries

### 💻 Code Examples (`integrations/`)
Code snippets showing how to integrate Debuggle:
- **python/** - Python integration examples
- **javascript/** - JavaScript/Node.js examples  
- **bash/** - Shell script examples
- **curl/** - cURL command examples

### 🎯 Use Cases (`use-cases/`)
Complete scenarios demonstrating Debuggle features:
- **monitoring/** - System monitoring setups
- **debugging/** - Application debugging workflows
- **analytics/** - Log analysis examples

## 🚀 Quick Start Examples

### Process a Sample Log File
```bash
# Upload sample application log
curl -X POST http://localhost:8000/upload-file \
  -F "file=@examples/logs/application.log" \
  -F "tier=core"
```

### Test Different Service Tiers
```bash
# Core tier example
curl -X POST http://localhost:8000/debuggle-log \
  -H "Content-Type: application/json" \
  -d @examples/requests/core-tier.json

# Pro tier example  
curl -X POST http://localhost:8000/debuggle-log \
  -H "Content-Type: application/json" \
  -d @examples/requests/pro-tier.json
```

### Run Integration Examples
```bash
# Python example
cd examples/integrations/python
python basic_integration.py

# JavaScript example
cd examples/integrations/javascript  
node basic_integration.js
```

## 📊 Sample Data

All sample log files contain realistic but anonymized data. No real user information, credentials, or sensitive data is included.

## 🔧 Using Examples

1. **Copy and modify** examples for your specific use case
2. **Test features** using provided sample data
3. **Learn patterns** from real-world scenarios
4. **Validate integrations** with working code

## 📚 Related Documentation

- [Getting Started Guide](../docs/user-guide/getting-started.md)
- [API Reference](../docs/api/README.md)
- [Integration Patterns](../docs/user-guide/features.md)