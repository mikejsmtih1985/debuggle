# 🚀 Debuggle VS Code Integration - Complete Setup Guide

## 📋 Prerequisites Checklist
- ✅ **Python 3.8+** (you have 3.12.3)
- ✅ **Node.js** (you have v18.19.1) 
- ✅ **VS Code** (latest version recommended)
- ✅ **Git** (for project context)

## 🎯 Quick Start (5 Minutes)

### 1. Install Debuggle Core
```bash
cd /home/mikej/debuggle
source .venv/bin/activate
python install.py
```
✅ **Status: COMPLETED** - All dependencies installed!

### 2. Start Debuggle Server
```bash
cd /home/mikej/debuggle
source .venv/bin/activate
python entry_point.py serve
```
🌐 **Server will be available at: http://localhost:8000**

### 3. Install VS Code Extension (Development Mode)

**WSL Users (Recommended Approach):**
```bash
cd /home/mikej/debuggle/vscode-extension
code .  # Opens VS Code connected to WSL
```
Then press **F5** to launch Extension Development Host

**Option A: Direct Loading (WSL or Local)**
1. Open VS Code
2. File → Open Folder → Select `/home/mikej/debuggle/vscode-extension/`
   - **WSL Path**: `/home/mikej/debuggle/vscode-extension/`
   - **Windows Path**: `\\wsl$\Ubuntu\home\mikej\debuggle\vscode-extension\`
3. Press **F5** to launch Extension Development Host  
4. New VS Code window opens with Debuggle extension loaded

**Option B: Command Palette**
1. Open VS Code
2. **Ctrl+Shift+P** → Type "Extensions: Install from VSIX"
3. Navigate to extension directory
4. Select the extension (once packaged)

## 🎮 Using Debuggle + VS Code Integration

### Real-Time Error Monitoring
1. **Start Debuggle server** (if not running):
   ```bash
   cd /home/mikej/debuggle && python entry_point.py serve
   ```

2. **Open VS Code with extension loaded** (F5 from vscode-extension folder)

3. **Activate monitoring**:
   - **Ctrl+Shift+P** → "Debuggle: Start Monitoring"
   - OR click Debuggle icon in status bar

### Testing the Integration

**Test with CLI Analysis:**
```bash
cd /home/mikej/debuggle
source .venv/bin/activate
python test_errors.py 2>&1 | python cli/debuggle_cli.py
```

**Test with Web Interface:**
1. Visit http://localhost:8000 in browser
2. Drag & drop your error log files
3. See real-time analysis

**Test with VS Code Integration:**
1. Generate errors in your code
2. Watch them appear in VS Code Problems panel
3. Use Debuggle dashboard for detailed analysis

## 🔧 Extension Features

### Status Bar Integration
- 📊 **Error count display** - See total errors at a glance  
- 🔴/🟢 **Connection status** - Know if Debuggle server is running
- 👆 **Click to open dashboard** - Quick access to details

### Problems Panel Integration  
- 🚨 **Real-time error display** - Errors appear as VS Code diagnostics
- 📍 **File locations** - Click to jump to error source
- 🏷️ **Error categorization** - Tags and severity levels
- 🔍 **Searchable/filterable** - Use VS Code's built-in problem filtering

### Command Palette Integration
Available commands (**Ctrl+Shift+P**):
- `Debuggle: Start Monitoring` - Begin real-time monitoring
- `Debuggle: Stop Monitoring` - Stop monitoring  
- `Debuggle: Show Monitoring Dashboard` - Open rich dashboard
- `Debuggle: Clear All Errors` - Reset error list
- `Debuggle: Connect to Server` - Manually connect to server
- `Debuggle: Test Connection` - Verify server connectivity

### Configuration Settings
Access via **File → Preferences → Settings → Search "Debuggle"**:
- `debuggle.serverUrl` - Server URL (default: http://localhost:8000)
- `debuggle.websocketUrl` - WebSocket URL for real-time updates
- `debuggle.autoConnect` - Auto-connect on startup
- `debuggle.showInStatusBar` - Show status bar integration
- `debuggle.maxDiagnostics` - Maximum problems to display
- `debuggle.enableNotifications` - Show error notifications

## 🚀 Development Workflow Integration

### For Code Coverage Testing (Current Project)
1. **Start Debuggle server**: `python entry_point.py serve`
2. **Load VS Code extension**: Open vscode-extension folder, press F5
3. **Run our test suites**: 
   ```bash
   python -m pytest tests/test_core_*_comprehensive.py --cov
   ```
4. **See real-time feedback** in VS Code as tests run
5. **Analyze any test failures** immediately with full context

### For General Development
1. **Always have Debuggle running** in background
2. **VS Code shows live errors** in Problems panel  
3. **Click error → See full analysis** with project context
4. **Get suggestions** better than ChatGPT because we see your actual code

## 🎯 Next Steps for Your Use Case

Since you're working on improving code coverage, here's the optimal workflow:

1. **Keep Debuggle server running**: 
   ```bash
   cd /home/mikej/debuggle && python entry_point.py serve
   ```

2. **Open VS Code with extension**: Load extension development host (F5)

3. **Continue our coverage work** with real-time monitoring:
   - Any import errors → Instantly visible in Problems panel
   - Test failures → Full context analysis available
   - Code issues → Debuggle provides solutions with project awareness

4. **Monitor our progress**: Dashboard shows error trends as we improve coverage

## 🔍 Troubleshooting

### Server Won't Start
- Check virtual environment: `source .venv/bin/activate`
- Verify dependencies: `python install.py`
- Check port availability: `lsof -ti:8000`

### Extension Not Loading  
- Ensure TypeScript compiled: `cd vscode-extension && npm run compile`
- Try reloading: Close Extension Development Host, press F5 again
- Check VS Code logs: Help → Toggle Developer Tools → Console

### Connection Issues
- Verify server is running: Visit http://localhost:8000
- Check WebSocket: Should see connection in server logs
- Test connection: Use "Debuggle: Test Connection" command

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ **Debuggle server shows**: "Uvicorn running on http://0.0.0.0:8000"
- ✅ **VS Code status bar shows**: Debuggle icon with error count
- ✅ **Problems panel shows**: "Debuggle" as error source
- ✅ **Dashboard opens**: Rich monitoring interface available
- ✅ **Real-time updates**: Errors appear immediately when generated

**You're now ready to continue our code coverage work with full VS Code integration!** 🚀

The next time we run our comprehensive test suites, you'll see everything in real-time through VS Code's interface, making development much more efficient.