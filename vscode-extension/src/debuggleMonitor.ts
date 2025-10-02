import * as vscode from 'vscode';
import WebSocket from 'ws';
import axios from 'axios';

export interface DebugglerError {
    id: string;
    timestamp: string;
    error_type: string;
    message: string;
    source: string;
    severity?: string;
    traceback?: string;
    context?: string;
    metadata?: any;
}

export class DebugglerMonitor {
    private context: vscode.ExtensionContext;
    private diagnosticCollection: vscode.DiagnosticCollection;
    private statusBarItem: vscode.StatusBarItem;
    private websocket: WebSocket | null = null;
    private isMonitoring: boolean = false;
    private errors: DebugglerError[] = [];
    private serverUrl: string;
    private websocketUrl: string;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('debuggle');
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        
        // Get configuration
        const config = vscode.workspace.getConfiguration('debuggle');
        this.serverUrl = config.get('serverUrl', 'http://localhost:8000');
        this.websocketUrl = config.get('websocketUrl', 'ws://localhost:8000/ws');

        // Initialize status bar
        this.updateStatusBar();
        this.statusBarItem.show();

        // Add to context subscriptions
        context.subscriptions.push(this.diagnosticCollection);
        context.subscriptions.push(this.statusBarItem);

        // Listen for configuration changes
        context.subscriptions.push(
            vscode.workspace.onDidChangeConfiguration((e: vscode.ConfigurationChangeEvent) => {
                if (e.affectsConfiguration('debuggle')) {
                    this.onConfigurationChanged();
                }
            })
        );
    }

    private onConfigurationChanged() {
        const config = vscode.workspace.getConfiguration('debuggle');
        const newServerUrl = config.get('serverUrl', 'http://localhost:8000');
        const newWebsocketUrl = config.get('websocketUrl', 'ws://localhost:8000/ws');

        if (newServerUrl !== this.serverUrl || newWebsocketUrl !== this.websocketUrl) {
            this.serverUrl = newServerUrl;
            this.websocketUrl = newWebsocketUrl;
            
            if (this.isMonitoring) {
                // Reconnect with new configuration
                this.stopMonitoring();
                this.startMonitoring();
            }
        }
    }

    public async startMonitoring(): Promise<void> {
        if (this.isMonitoring) {
            vscode.window.showInformationMessage('Debuggle monitoring is already active');
            return;
        }

        try {
            await this.connectWebSocket();
            await this.enableServerMonitoring();
            this.isMonitoring = true;
            this.updateStatusBar();
            
            vscode.commands.executeCommand('setContext', 'debuggle.monitoring.active', true);
            vscode.window.showInformationMessage('Debuggle monitoring started');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start monitoring: ${error}`);
        }
    }

    public async stopMonitoring(): Promise<void> {
        if (!this.isMonitoring) {
            return;
        }

        this.disconnectWebSocket();
        await this.disableServerMonitoring();
        this.isMonitoring = false;
        this.updateStatusBar();
        
        vscode.commands.executeCommand('setContext', 'debuggle.monitoring.active', false);
        vscode.window.showInformationMessage('Debuggle monitoring stopped');
    }

    public async connectToServer(): Promise<void> {
        try {
            const response = await axios.get(`${this.serverUrl}/api/v1/self-monitor/status`);
            vscode.window.showInformationMessage(`Connected to Debuggle server. Status: ${response.status}`);
            
            if (!this.isMonitoring) {
                this.startMonitoring();
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to connect to Debuggle server: ${error}`);
        }
    }

    public async testConnection(): Promise<void> {
        try {
            const response = await axios.get(`${this.serverUrl}/api/v1/self-monitor/status`);
            const data = response.data;
            
            vscode.window.showInformationMessage(
                `Connection successful! Errors: ${data.total_errors}, Monitoring: ${data.monitoring_enabled ? 'enabled' : 'disabled'}`
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Connection test failed: ${error}`);
        }
    }

    public async clearErrors(): Promise<void> {
        try {
            await axios.post(`${this.serverUrl}/api/v1/self-monitor/clear`);
            this.errors = [];
            this.diagnosticCollection.clear();
            this.updateStatusBar();
            vscode.window.showInformationMessage('Errors cleared');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to clear errors: ${error}`);
        }
    }

    private async connectWebSocket(): Promise<void> {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(this.websocketUrl);
                
                if (this.websocket) {
                    this.websocket.on('open', () => {
                        resolve();
                    });

                    this.websocket.on('message', (data: WebSocket.Data) => {
                        try {
                            const message = JSON.parse(data.toString());
                            this.handleWebSocketMessage(message);
                        } catch (error) {
                            console.error('Failed to parse WebSocket message:', error);
                        }
                    });

                    this.websocket.on('error', (error: any) => {
                        reject(error);
                    });

                    this.websocket.on('close', () => {
                        if (this.isMonitoring) {
                            // Attempt to reconnect after a delay
                            setTimeout(() => {
                                if (this.isMonitoring) {
                                    this.connectWebSocket().catch(console.error);
                                }
                            }, 5000);
                        }
                    });
                }

            } catch (error) {
                reject(error);
            }
        });
    }

    private disconnectWebSocket(): void {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }

    private async enableServerMonitoring(): Promise<void> {
        await axios.post(`${this.serverUrl}/api/v1/self-monitor/toggle`, {
            enabled: true
        });
    }

    private async disableServerMonitoring(): Promise<void> {
        try {
            await axios.post(`${this.serverUrl}/api/v1/self-monitor/toggle`, {
                enabled: false
            });
        } catch (error) {
            // Don't fail if we can't disable server monitoring
            console.error('Failed to disable server monitoring:', error);
        }
    }

    private handleWebSocketMessage(message: any): void {
        if (message.type === 'self_monitoring_error' && message.error) {
            const error: DebugglerError = message.error;
            this.addError(error);
            
            // Show notification for critical errors
            const config = vscode.workspace.getConfiguration('debuggle');
            if (config.get('enableNotifications', true) && error.severity === 'error') {
                vscode.window.showWarningMessage(`Debuggle Error: ${error.message}`);
            }
        }
    }

    private addError(error: DebugglerError): void {
        this.errors.push(error);
        
        const config = vscode.workspace.getConfiguration('debuggle');
        const maxDiagnostics = config.get('maxDiagnostics', 100);
        
        // Keep only the most recent errors
        if (this.errors.length > maxDiagnostics) {
            this.errors = this.errors.slice(-maxDiagnostics);
        }

        this.updateDiagnostics();
        this.updateStatusBar();
    }

    private updateDiagnostics(): void {
        // Create diagnostics for current workspace files
        const diagnosticMap = new Map<string, vscode.Diagnostic[]>();

        for (const error of this.errors) {
            // Try to map error to a file if possible
            let fileUri: vscode.Uri | null = null;
            
            if (error.metadata && error.metadata.file) {
                try {
                    fileUri = vscode.Uri.file(error.metadata.file);
                } catch (e) {
                    // Invalid file path
                }
            }

            // If no specific file, use a generic workspace file or create a virtual one
            if (!fileUri && vscode.workspace.workspaceFolders) {
                fileUri = vscode.Uri.joinPath(
                    vscode.workspace.workspaceFolders[0].uri, 
                    'debuggle-errors.log'
                );
            }

            if (fileUri) {
                const line = error.metadata?.line ? Math.max(0, error.metadata.line - 1) : 0;
                const range = new vscode.Range(line, 0, line, Number.MAX_SAFE_INTEGER);
                
                const severity = this.mapSeverity(error.severity || 'error');
                const diagnostic = new vscode.Diagnostic(
                    range,
                    `[${error.error_type}] ${error.message}`,
                    severity
                );
                
                diagnostic.source = 'debuggle';
                diagnostic.code = error.id;

                const key = fileUri.toString();
                if (!diagnosticMap.has(key)) {
                    diagnosticMap.set(key, []);
                }
                diagnosticMap.get(key)!.push(diagnostic);
            }
        }

        // Update diagnostics
        this.diagnosticCollection.clear();
        diagnosticMap.forEach((diagnostics, uri) => {
            this.diagnosticCollection.set(vscode.Uri.parse(uri), diagnostics);
        });
    }

    private mapSeverity(severity: string): vscode.DiagnosticSeverity {
        switch (severity.toLowerCase()) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Error;
        }
    }

    private updateStatusBar(): void {
        const config = vscode.workspace.getConfiguration('debuggle');
        if (!config.get('showInStatusBar', true)) {
            this.statusBarItem.hide();
            return;
        }

        const errorCount = this.errors.length;
        const status = this.isMonitoring ? 'monitoring' : 'inactive';
        
        this.statusBarItem.text = `$(debug-alt) Debuggle: ${errorCount} errors (${status})`;
        this.statusBarItem.tooltip = `Debuggle Monitor - ${errorCount} errors detected`;
        this.statusBarItem.command = 'debuggle.showDashboard';
        this.statusBarItem.show();
    }

    public getErrors(): DebugglerError[] {
        return [...this.errors];
    }

    public isActive(): boolean {
        return this.isMonitoring;
    }

    public dispose(): void {
        this.stopMonitoring();
        this.diagnosticCollection.dispose();
        this.statusBarItem.dispose();
        this.disconnectWebSocket();
    }
}