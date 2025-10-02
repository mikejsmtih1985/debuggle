import * as vscode from 'vscode';
import { DebugglerMonitor } from './debuggleMonitor';
import { MonitoringPanel } from './monitoringPanel';

let debuggleMonitor: DebugglerMonitor;
let monitoringPanel: MonitoringPanel | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('Debuggle Monitor extension is now active!');

    // Initialize the monitor
    debuggleMonitor = new DebugglerMonitor(context);

    // Register commands
    const commands = [
        vscode.commands.registerCommand('debuggle.startMonitoring', () => {
            debuggleMonitor.startMonitoring();
        }),

        vscode.commands.registerCommand('debuggle.stopMonitoring', () => {
            debuggleMonitor.stopMonitoring();
        }),

        vscode.commands.registerCommand('debuggle.showDashboard', () => {
            if (monitoringPanel) {
                monitoringPanel.reveal();
            } else {
                monitoringPanel = new MonitoringPanel(context.extensionUri, debuggleMonitor);
                monitoringPanel.onDidDispose(() => {
                    monitoringPanel = undefined;
                });
            }
        }),

        vscode.commands.registerCommand('debuggle.clearErrors', () => {
            debuggleMonitor.clearErrors();
        }),

        vscode.commands.registerCommand('debuggle.connectToServer', () => {
            debuggleMonitor.connectToServer();
        }),

        vscode.commands.registerCommand('debuggle.testConnection', () => {
            debuggleMonitor.testConnection();
        })
    ];

    // Add all commands to subscriptions
    commands.forEach(command => context.subscriptions.push(command));

    // Auto-connect if configured
    const config = vscode.workspace.getConfiguration('debuggle');
    if (config.get('autoConnect', true)) {
        debuggleMonitor.connectToServer();
    }

    // Set context for views
    vscode.commands.executeCommand('setContext', 'debuggle.monitoring.active', false);
}

export function deactivate() {
    if (debuggleMonitor) {
        debuggleMonitor.dispose();
    }
    if (monitoringPanel) {
        monitoringPanel.dispose();
    }
}