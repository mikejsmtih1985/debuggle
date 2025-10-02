# VS Code Integration

Debuggle now includes a VS Code extension that provides real-time error monitoring and debugging assistance directly within your development environment.

## Features

The VS Code extension provides:

- **Real-time Error Monitoring**: Live updates from Debuggle's self-monitoring system
- **Problems Panel Integration**: Debuggle errors appear in VS Code's Problems panel
- **Status Bar Monitoring**: Error count and monitoring status in the status bar
- **Rich Dashboard**: Comprehensive monitoring dashboard with error details
- **Command Palette Integration**: Full control via VS Code commands
- **WebSocket Connection**: Real-time updates with automatic reconnection

## Installation

### From Source

1. Navigate to the extension directory:
   ```bash
   cd vscode-extension
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Compile the extension:
   ```bash
   npm run compile
   ```

4. Open VS Code in the extension directory and press F5 to launch the Extension Development Host

### Extension Commands

Available commands (accessible via Ctrl+Shift+P):

- `Debuggle: Start Monitoring` - Begin monitoring Debuggle server
- `Debuggle: Stop Monitoring` - Stop monitoring
- `Debuggle: Show Monitoring Dashboard` - Open the monitoring dashboard
- `Debuggle: Clear All Errors` - Clear all captured errors
- `Debuggle: Connect to Server` - Connect to Debuggle server
- `Debuggle: Test Connection` - Test connection to server

## Configuration

Configure the extension via VS Code settings:

```json
{
  "debuggle.serverUrl": "http://localhost:8000",
  "debuggle.websocketUrl": "ws://localhost:8000/ws",
  "debuggle.autoConnect": true,
  "debuggle.showInStatusBar": true,
  "debuggle.maxDiagnostics": 100,
  "debuggle.enableNotifications": true
}
```

## Usage Workflow

1. **Start Debuggle Server**:
   ```bash
   python entry_point.py serve
   ```

2. **Install and Activate Extension** in VS Code

3. **Automatic Connection**: The extension will automatically connect to the server

4. **Monitor Errors**: 
   - View errors in the Problems panel
   - Check status in the status bar
   - Open the dashboard for detailed analysis

5. **Development Integration**:
   - Errors appear with file locations when available
   - Click to navigate directly to error locations
   - Real-time updates as errors occur

## Integration Architecture

### Communication Flow

```
Debuggle Server ←→ WebSocket ←→ VS Code Extension
      ↓                              ↓
  Self Monitor              Problems Panel
      ↓                              ↓
  Error Events              Status Bar Updates
      ↓                              ↓
   REST API                    Dashboard UI
```

### Key Components

1. **DebugglerMonitor**: Core monitoring class handling server communication
2. **MonitoringPanel**: Webview-based dashboard for rich visualization
3. **Diagnostic Collection**: Maps errors to VS Code's Problems panel
4. **Status Bar Integration**: Real-time status updates
5. **WebSocket Client**: Real-time error streaming

### Error Mapping

The extension maps Debuggle errors to VS Code diagnostics:

- **Error Type**: Shown as diagnostic message prefix
- **Message**: Main diagnostic message
- **File Location**: Maps to workspace files when available
- **Line Number**: Precise error location when available
- **Severity**: Error/Warning/Info levels

## Testing Integration

Use the included test script to verify server connectivity:

```bash
python vscode-extension/test_integration.py
```

This tests:
- REST API endpoints
- Self-monitoring controls
- Error generation and clearing
- WebSocket connectivity

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure Debuggle server is running on port 8000
2. **WebSocket Errors**: Check firewall settings and server configuration
3. **No Errors Showing**: Verify monitoring is enabled and errors are being generated
4. **Extension Not Loading**: Check VS Code version compatibility (≥1.74.0)

### Debug Mode

1. Open VS Code Developer Tools (Help → Toggle Developer Tools)
2. Check console for extension logs
3. Use Extension Development Host for debugging
4. Enable verbose logging in extension settings

## Development

### Building the Extension

```bash
cd vscode-extension
npm install
npm run compile
```

### Packaging for Distribution

```bash
npm install -g vsce
vsce package
```

### Testing Changes

1. Make changes to TypeScript files in `src/`
2. Run `npm run compile`
3. Reload the Extension Development Host (Ctrl+R)

## API Integration

The extension integrates with these Debuggle API endpoints:

- `GET /api/v1/self-monitor/status` - Get monitoring status
- `POST /api/v1/self-monitor/toggle` - Enable/disable monitoring
- `POST /api/v1/self-monitor/clear` - Clear all errors
- `POST /api/v1/self-monitor/test-error` - Generate test error
- `WebSocket /ws` - Real-time error streaming

## Future Enhancements

Planned improvements:

- Language server protocol integration
- Code action providers for quick fixes
- Error pattern analysis and suggestions
- Integration with VS Code debugging features
- Custom error filtering and categorization