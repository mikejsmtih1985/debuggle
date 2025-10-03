# 🛠️ Debuggle Installation Troubleshooting Guide

This document addresses common installation issues encountered across different systems.

## 🔧 VS Code Extension Issues

### Node.js Version Compatibility
**Problem**: Extension packaging fails with "Unsupported engine" errors
```
npm WARN EBADENGINE Unsupported engine {
npm WARN EBADENGINE   package: 'cheerio@1.1.2',
npm WARN EBADENGINE   required: { node: '>=20.18.1' },
```

**Solutions**:
1. **Development Mode (Recommended)**: Skip packaging, use F5 directly
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   # Then: Open folder in VS Code, press F5
   ```

2. **Update Node.js**: Install Node.js 20.18.1+ for packaging
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # Or use nvm
   nvm install 20
   nvm use 20
   ```

3. **Use Modern Packaging**: 
   ```bash
   npm install @vscode/vsce --save-dev
   npm run package
   ```

### Extension Loading Issues
**Problem**: Extension doesn't load in VS Code

**Solutions**:
1. **Verify Compilation**: Ensure TypeScript compiled successfully
   ```bash
   cd vscode-extension
   npm run compile
   # Should complete without errors
   ```

2. **Check Output Directory**: Verify `out/` directory exists with compiled JS files

3. **Reload Extension Host**: In Extension Development Host window
   - Ctrl+Shift+P → "Developer: Reload Window"

## 🐍 Python Environment Issues

### Missing Dependencies
**Problem**: Import errors when starting Debuggle

**Solutions**:
1. **Use Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or .venv\Scripts\activate  # Windows
   ```

2. **Install All Dependencies**:
   ```bash
   python install.py
   # or
   pip install -r requirements.txt
   ```

3. **Verify Installation**:
   ```bash
   python -c "import fastapi, uvicorn; print('Core dependencies OK')"
   ```

### Context Extraction Warnings
**Problem**: "No such file or directory: 'java'" warnings

**Impact**: Non-critical - context extraction continues without Java version detection

**Solutions**:
1. **Install Java** (optional):
   ```bash
   # Ubuntu/Debian
   sudo apt install default-jdk
   
   # macOS
   brew install java
   
   # Windows
   # Download from Oracle or OpenJDK
   ```

2. **Ignore Warning**: Java detection is optional, doesn't affect core functionality

## 🌐 Server Connection Issues

### Port Already in Use
**Problem**: "Address already in use" on port 8000

**Solutions**:
1. **Kill Existing Process**:
   ```bash
   lsof -ti:8000 | xargs kill -9
   # or
   pkill -f "python.*debuggle"
   ```

2. **Use Different Port**:
   ```bash
   python entry_point.py serve --port 8080
   ```

3. **Update Extension Config**: In VS Code settings
   ```json
   "debuggle.serverUrl": "http://localhost:8080"
   ```

### WebSocket Connection Failures
**Problem**: Extension can't connect to server WebSocket

**Solutions**:
1. **Verify Server Running**: Visit http://localhost:8000 in browser

2. **Check Firewall**: Ensure port 8000 accessible

3. **Manual Reconnection**: Use "Debuggle: Connect to Server" command

## 📦 Packaging and Distribution Issues

### VSIX Creation Fails
**Problem**: Cannot create .vsix package for distribution

**Solutions**:
1. **Use Development Mode**: Skip packaging for local development
   
2. **Fix Dependencies**: Update to compatible versions
   ```bash
   npm update
   npm audit fix
   ```

3. **Alternative Packaging**:
   ```bash
   npm install -g @vscode/vsce
   vsce package --allow-star-activation
   ```

## 🖥️ Platform-Specific Issues

### Windows
- Use PowerShell or Git Bash instead of CMD
- Path separators: Use forward slashes or double backslashes
- Virtual environment activation: `.venv\Scripts\activate`

### macOS
- May need Xcode command line tools: `xcode-select --install`
- Permission issues: Use `sudo` sparingly, prefer user-level installs

### Linux/WSL
- Ensure Python dev headers: `sudo apt install python3-dev`
- Node.js from NodeSource for latest versions
- File permissions: Make shell scripts executable with `chmod +x`

## 🔍 Diagnostic Commands

Run these to diagnose issues:

```bash
# Python environment
python --version
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# Node.js environment  
node --version
npm --version

# Debuggle specific
cd /path/to/debuggle
python entry_point.py --help

# VS Code extension
cd vscode-extension
npm list
ls -la out/
```

## 🆘 Getting Help

If issues persist:

1. **Check Logs**: Look at VS Code Developer Tools console
2. **Minimal Reproduction**: Try with fresh virtual environment
3. **Report Issues**: Include diagnostic command outputs
4. **Development Mode**: Use F5 method as fallback for packaging issues

## ✅ Success Indicators

Everything is working when:
- ✅ `python entry_point.py serve` starts without errors
- ✅ http://localhost:8000 shows Debuggle interface
- ✅ VS Code Extension Development Host loads extension
- ✅ Status bar shows Debuggle icon
- ✅ "Debuggle: Start Monitoring" command available
- ✅ Problems panel shows "Debuggle" as source for errors