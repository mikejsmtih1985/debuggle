# Debuggle Monitor VS Code Extension

A VS Code extension that integrates with Debuggle's self-monitoring system to provide real-time error monitoring and debugging assistance directly within your development environment.

## Features

- **Real-time Error Monitoring**: Connect to Debuggle server and receive live error updates
- **Integrated Diagnostics**: View Debuggle errors in VS Code's Problems panel
- **Status Bar Integration**: Monitor Debuggle status and error count at a glance
- **Rich Dashboard**: Comprehensive monitoring dashboard with error details and statistics
- **Command Palette Integration**: Full control via VS Code commands
- **Configurable Settings**: Customize server URLs, notifications, and display options

## Requirements

- VS Code 1.74.0 or higher
- Active Debuggle server instance (typically running on localhost:8000)
- Node.js for development

## Extension Settings

This extension contributes the following settings:

- `debuggle.serverUrl`: Debuggle server URL (default: `http://localhost:8000`)
- `debuggle.websocketUrl`: WebSocket URL for real-time updates (default: `ws://localhost:8000/ws`)
- `debuggle.autoConnect`: Automatically connect to server on startup (default: `true`)
- `debuggle.showInStatusBar`: Show monitoring status in status bar (default: `true`)
- `debuggle.maxDiagnostics`: Maximum number of diagnostics to show (default: `100`)
- `debuggle.enableNotifications`: Show notifications for critical errors (default: `true`)

## Commands

- `Debuggle: Start Monitoring` - Begin monitoring Debuggle server
- `Debuggle: Stop Monitoring` - Stop monitoring
- `Debuggle: Show Monitoring Dashboard` - Open the monitoring dashboard
- `Debuggle: Clear All Errors` - Clear all captured errors
- `Debuggle: Connect to Server` - Connect to Debuggle server
- `Debuggle: Test Connection` - Test connection to server

## Usage

1. Start your Debuggle server
2. Open VS Code and install the Debuggle Monitor extension
3. The extension will automatically attempt to connect to the default server (localhost:8000)
4. Use `Ctrl+Shift+P` and search for "Debuggle" commands to control monitoring
5. View errors in the Problems panel or open the monitoring dashboard

## Integration Features

### Problems Panel Integration
Debuggle errors appear directly in VS Code's Problems panel with:
- Error type and message
- Source file (when available)
- Line numbers (when available)
- Clickable navigation to error locations

### Status Bar Monitoring
The status bar shows:
- Current error count
- Monitoring status (active/inactive)
- Click to open dashboard

### Real-time Updates
- WebSocket connection for instant error notifications
- Automatic reconnection on connection loss
- Live dashboard updates

## Development

To set up for development:

\`\`\`bash
cd vscode-extension
npm install
npm run compile
\`\`\`

To test the extension:
1. Open VS Code
2. Go to Run and Debug (Ctrl+Shift+D)
3. Select "Run Extension" 
4. Press F5 to launch a new Extension Development Host

## Building

To build the extension:

\`\`\`bash
npm run compile
\`\`\`

To package for distribution:
\`\`\`bash
npm install -g vsce
vsce package
\`\`\`

## Architecture

- **DebugglerMonitor**: Core monitoring class that handles server communication
- **MonitoringPanel**: Webview-based dashboard for rich error visualization
- **Extension**: Main extension entry point and command registration

The extension uses:
- WebSocket connections for real-time updates
- REST API calls for control operations
- VS Code Diagnostic API for Problems panel integration
- Status Bar API for monitoring status display

## Known Issues

- WebSocket connection may require manual reconnection after server restarts
- Some error locations may not map perfectly to workspace files
- Large numbers of errors may impact performance

## Release Notes

### 1.0.0

Initial release of Debuggle Monitor extension with:
- Real-time error monitoring
- VS Code Problems panel integration
- Status bar integration
- Monitoring dashboard
- Command palette integration