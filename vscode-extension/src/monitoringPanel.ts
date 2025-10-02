import * as vscode from 'vscode';
import { DebugglerMonitor, DebugglerError } from './debuggleMonitor';

export class MonitoringPanel {
    public static readonly viewType = 'debuggleMonitoring';
    private panel: vscode.WebviewPanel;
    private disposables: vscode.Disposable[] = [];
    private monitor: DebugglerMonitor;

    constructor(extensionUri: vscode.Uri, monitor: DebugglerMonitor) {
        this.monitor = monitor;
        
        this.panel = vscode.window.createWebviewPanel(
            MonitoringPanel.viewType,
            'Debuggle Monitor Dashboard',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        this.panel.webview.html = this.getWebviewContent();
        
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);
        
        this.panel.webview.onDidReceiveMessage(
            (message: any) => {
                switch (message.command) {
                    case 'refresh':
                        this.updateContent();
                        break;
                    case 'clearErrors':
                        this.monitor.clearErrors();
                        this.updateContent();
                        break;
                    case 'startMonitoring':
                        this.monitor.startMonitoring();
                        break;
                    case 'stopMonitoring':
                        this.monitor.stopMonitoring();
                        break;
                }
            },
            null,
            this.disposables
        );

        // Update content periodically
        const updateInterval = setInterval(() => {
            this.updateContent();
        }, 2000);

        this.disposables.push({
            dispose: () => clearInterval(updateInterval)
        });

        // Initial content update
        this.updateContent();
    }

    public reveal() {
        this.panel.reveal(vscode.ViewColumn.One);
    }

    public onDidDispose(callback: () => void) {
        this.panel.onDidDispose(callback);
    }

    private updateContent() {
        const errors = this.monitor.getErrors();
        const isActive = this.monitor.isActive();
        
        this.panel.webview.postMessage({
            command: 'updateData',
            data: {
                errors: errors,
                isActive: isActive,
                timestamp: new Date().toISOString()
            }
        });
    }

    private getWebviewContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debuggle Monitor Dashboard</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            margin: 0;
            padding: 20px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: var(--vscode-errorForeground);
        }
        
        .status-indicator.active {
            background-color: var(--vscode-testing-iconPassed);
        }
        
        .controls {
            display: flex;
            gap: 10px;
        }
        
        button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background-color: var(--vscode-sideBar-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 15px;
        }
        
        .stat-title {
            font-size: 12px;
            text-transform: uppercase;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 5px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
        }
        
        .errors-container {
            background-color: var(--vscode-sideBar-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            padding: 15px;
        }
        
        .errors-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .error-item {
            border: 1px solid var(--vscode-panel-border);
            border-radius: 4px;
            margin-bottom: 10px;
            padding: 10px;
            background-color: var(--vscode-editor-background);
        }
        
        .error-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        
        .error-type {
            font-weight: bold;
            color: var(--vscode-errorForeground);
        }
        
        .error-timestamp {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        
        .error-message {
            margin-bottom: 5px;
            word-wrap: break-word;
        }
        
        .error-details {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        
        .no-errors {
            text-align: center;
            color: var(--vscode-descriptionForeground);
            padding: 40px;
        }
        
        .last-updated {
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="status">
            <div class="status-indicator" id="statusIndicator"></div>
            <span id="statusText">Initializing...</span>
        </div>
        <div class="controls">
            <button id="toggleMonitoring" onclick="toggleMonitoring()">Start Monitoring</button>
            <button onclick="refreshData()">Refresh</button>
            <button onclick="clearErrors()">Clear Errors</button>
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-title">Total Errors</div>
            <div class="stat-value" id="totalErrors">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Recent Errors</div>
            <div class="stat-value" id="recentErrors">0</div>
        </div>
        <div class="stat-card">
            <div class="stat-title">Monitoring Status</div>
            <div class="stat-value" id="monitoringStatus">Inactive</div>
        </div>
    </div>
    
    <div class="errors-container">
        <div class="errors-header">
            <h3>Recent Errors</h3>
        </div>
        <div id="errorsList">
            <div class="no-errors">No errors detected</div>
        </div>
    </div>
    
    <div class="last-updated" id="lastUpdated"></div>

    <script>
        const vscode = acquireVsCodeApi();
        let currentData = null;

        // Handle messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'updateData':
                    currentData = message.data;
                    updateUI();
                    break;
            }
        });

        function updateUI() {
            if (!currentData) return;
            
            const { errors, isActive, timestamp } = currentData;
            
            // Update status
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            const toggleButton = document.getElementById('toggleMonitoring');
            
            if (isActive) {
                statusIndicator.classList.add('active');
                statusText.textContent = 'Monitoring Active';
                toggleButton.textContent = 'Stop Monitoring';
            } else {
                statusIndicator.classList.remove('active');
                statusText.textContent = 'Monitoring Inactive';
                toggleButton.textContent = 'Start Monitoring';
            }
            
            // Update stats
            document.getElementById('totalErrors').textContent = errors.length;
            document.getElementById('recentErrors').textContent = errors.slice(-10).length;
            document.getElementById('monitoringStatus').textContent = isActive ? 'Active' : 'Inactive';
            
            // Update errors list
            const errorsList = document.getElementById('errorsList');
            
            if (errors.length === 0) {
                errorsList.innerHTML = '<div class="no-errors">No errors detected</div>';
            } else {
                const errorsHtml = errors.slice(-20).reverse().map(error => {
                    const timestamp = new Date(error.timestamp).toLocaleString();
                    return \`
                        <div class="error-item">
                            <div class="error-header">
                                <span class="error-type">\${error.error_type}</span>
                                <span class="error-timestamp">\${timestamp}</span>
                            </div>
                            <div class="error-message">\${error.message}</div>
                            <div class="error-details">
                                Source: \${error.source} | ID: \${error.id}
                            </div>
                        </div>
                    \`;
                }).join('');
                errorsList.innerHTML = errorsHtml;
            }
            
            // Update last updated time
            document.getElementById('lastUpdated').textContent = 
                'Last updated: ' + new Date(timestamp).toLocaleTimeString();
        }

        function toggleMonitoring() {
            if (currentData && currentData.isActive) {
                vscode.postMessage({ command: 'stopMonitoring' });
            } else {
                vscode.postMessage({ command: 'startMonitoring' });
            }
        }

        function refreshData() {
            vscode.postMessage({ command: 'refresh' });
        }

        function clearErrors() {
            vscode.postMessage({ command: 'clearErrors' });
        }

        // Initial refresh
        refreshData();
    </script>
</body>
</html>`;
    }

    public dispose() {
        this.panel.dispose();
        
        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}