/**
 * 📡 DEBUGGLE RADAR SYSTEM - The Eyes and Ears of Mission Control
 * 
 * This file contains our sophisticated error-monitoring system that works like
 * a powerful radar array, constantly scanning for problems in your code and
 * reporting back to mission control (VS Code) with detailed intelligence.
 * 
 * 🏆 HIGH SCHOOL EXPLANATION:
 * Imagine you're running a air traffic control tower. You need several things:
 * 1. Radar screens to detect aircraft (VS Code integration)
 * 2. Radio communications to talk to pilots (WebSocket connections)  
 * 3. Internet access to check weather and flight plans (HTTP requests)
 * 4. A standard format for all the information you collect (DebugglerError)
 * 
 * This file sets up all those systems so our debugging "control tower" can
 * monitor, communicate, and help solve problems in real-time.
 */

// 🏗️ MISSION CONTROL TOOLKIT - importing our essential tools
import * as vscode from 'vscode';  // Like importing the control tower interface
import WebSocket from 'ws';        // Like setting up radio communications
import axios from 'axios';         // Like connecting to the internet for data

/**
 * 📋 ERROR INTELLIGENCE REPORT FORMAT - standardized data structure
 * 
 * This interface defines exactly what information we collect about each error,
 * like having a standardized form that air traffic controllers fill out for
 * every incident report.
 * 
 * 🏆 HIGH SCHOOL EXPLANATION:
 * Think of this like a police report form. Every time there's an incident
 * (an error in your code), we need to collect the same types of information:
 * - Who was involved? (source)
 * - When did it happen? (timestamp)  
 * - What exactly happened? (message)
 * - How serious was it? (severity)
 * - What were the circumstances? (context, traceback)
 * 
 * Having a standard format means everyone knows what to expect and where
 * to find specific information.
 */
export interface DebugglerError {
    // 🆔 UNIQUE IDENTIFIER - like a case number for this specific error
    id: string;
    
    // ⏰ TIMESTAMP - exactly when this error occurred  
    timestamp: string;
    
    // 🏷️ ERROR CLASSIFICATION - what category of problem this is
    error_type: string;
    
    // 💬 ERROR MESSAGE - the actual description of what went wrong
    message: string;
    
    // 📍 SOURCE LOCATION - which file or system reported this error
    source: string;
    
    // ⚠️ SEVERITY LEVEL - how serious this problem is (optional)
    severity?: string;
    
    // 🔍 TECHNICAL DETAILS - the full stack trace for debugging (optional)
    traceback?: string;
    
    // 🌟 SURROUNDING CONTEXT - additional information about the situation (optional)
    context?: string;
    
    // 📦 EXTRA DATA - any other relevant information (optional)
    metadata?: any;
}

/**
 * 🎯 DEBUGGLE RADAR CONTROL CENTER - The Master Monitoring System
 * 
 * This class is like the main control center for a sophisticated radar system.
 * It coordinates all the different monitoring equipment, manages communications,
 * and keeps track of everything that's happening across your codebase.
 * 
 * 🏆 HIGH SCHOOL EXPLANATION:
 * Think of this like the main computer system in a modern airport control tower.
 * It needs to manage:
 * 1. Multiple radar screens showing different information
 * 2. Radio communications with aircraft
 * 3. Status displays for air traffic controllers
 * 4. A log of all events and incidents
 * 5. Settings for how everything operates
 * 
 * This class brings all those pieces together into one coordinated system.
 */
export class DebugglerMonitor {
    // 🏗️ CONTROL CENTER INFRASTRUCTURE - all the equipment we need to operate
    
    // 🎮 MISSION CONTROL INTERFACE - connection to VS Code's systems
    private context: vscode.ExtensionContext;
    
    // 📊 ERROR DISPLAY SYSTEM - shows problems directly in your code editor
    // Like having red warnings appear on a radar screen when something's wrong
    private diagnosticCollection: vscode.DiagnosticCollection;
    
    // 📱 STATUS INDICATOR - the little notification area that shows our current status
    // Like the "ON AIR" light in a radio studio that tells everyone what's happening
    private statusBarItem: vscode.StatusBarItem;
    
    // 📡 REAL-TIME COMMUNICATION LINK - our connection to the Debuggle server
    // Like the radio system that keeps us in constant contact with headquarters
    private websocket: WebSocket | null = null;
    
    // 🚦 MONITORING STATE - whether we're actively scanning for errors or not
    // Like the master "RADAR ON/OFF" switch in the control room
    private isMonitoring: boolean = false;
    
    // 📚 ERROR DATABASE - our collection of all detected problems
    // Like the incident logbook where we record every problem we find
    private errors: DebugglerError[] = [];
    
    // 🌐 SERVER ADDRESSES - where to find the Debuggle intelligence services
    // Like having the phone numbers and addresses for different departments
    private serverUrl: string;        // Main headquarters (HTTP requests)
    private websocketUrl: string;     // Real-time communications (WebSocket)

    /**
     * 🚀 RADAR SYSTEM INITIALIZATION - Setting up our monitoring equipment
     * 
     * This constructor is called when we first power up our monitoring system.
     * It's like the startup sequence for a complex piece of equipment - we need
     * to initialize all the different components and make sure they're working together.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like setting up a new gaming setup. You need to:
     * 1. Connect all your monitors and peripherals
     * 2. Install the right software and drivers
     * 3. Configure your settings and preferences
     * 4. Test that everything is working properly
     * 
     * The 'context' parameter is like the main computer that everything else
     * connects to - it provides power, settings, and coordination for all components.
     */
    constructor(context: vscode.ExtensionContext) {
        // 🏗️ INFRASTRUCTURE SETUP - connect to our main systems
        this.context = context;
        
        // 📊 ERROR DISPLAY SETUP - create our visual warning system
        // Like setting up the red warning lights and alarms in the control room
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('debuggle');
        
        // 📱 STATUS DISPLAY SETUP - create our system status indicator
        // Like installing the status monitor that shows "SYSTEM OPERATIONAL" or "OFFLINE"
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        
        // ⚙️ CONFIGURATION LOADING - read our settings and preferences
        // Like loading the mission parameters and communication frequencies
        const config = vscode.workspace.getConfiguration('debuggle');
        this.serverUrl = config.get('serverUrl', 'http://localhost:8000');
        this.websocketUrl = config.get('websocketUrl', 'ws://localhost:8000/ws');

        // 🎬 SYSTEM ACTIVATION - power up our displays and indicators
        // Like turning on all the monitors and making sure they show the right information
        this.updateStatusBar();
        this.statusBarItem.show();

        // 📋 REGISTRATION WITH MISSION CONTROL - officially register our equipment
        // Like filling out the paperwork so headquarters knows what equipment we have
        // This ensures VS Code will properly clean up our systems when shutting down
        context.subscriptions.push(this.diagnosticCollection);
        context.subscriptions.push(this.statusBarItem);

        // 👂 SETTINGS MONITORING - watch for changes to our configuration
        // Like having a technician who watches for updates to mission parameters
        // If someone changes our settings, we need to know about it immediately
        context.subscriptions.push(
            vscode.workspace.onDidChangeConfiguration((e: vscode.ConfigurationChangeEvent) => {
                if (e.affectsConfiguration('debuggle')) {
                    // Something about our Debuggle settings changed - update accordingly
                    this.onConfigurationChanged();
                }
            })
        );
        
        /**
         * 🎯 RADAR SYSTEM READY FOR OPERATION!
         * 
         * At this point, our monitoring system is fully initialized and ready to:
         * - Display error information in VS Code
         * - Show status updates in the status bar
         * - Connect to the Debuggle server when requested
         * - Respond to configuration changes automatically
         * 
         * It's like having a fully operational radar system that's powered up,
         * calibrated, and ready to start scanning whenever we give the command.
         */
    }

    /**
     * ⚙️ CONFIGURATION UPDATE HANDLER - responding to settings changes
     * 
     * This method is called whenever someone changes our extension's settings.
     * It's like having a technician who immediately updates all the equipment
     * when mission control changes the communication frequencies or server addresses.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like updating your phone's WiFi settings. When you change
     * the WiFi network name or password in your settings, your phone needs to:
     * 1. Check what changed
     * 2. Update its internal records
     * 3. If you're currently connected, disconnect and reconnect with new settings
     * 
     * This ensures we're always using the most current configuration.
     */
    private onConfigurationChanged() {
        // 📋 SETTINGS INSPECTION - check what the new configuration looks like
        const config = vscode.workspace.getConfiguration('debuggle');
        const newServerUrl = config.get('serverUrl', 'http://localhost:8000');
        const newWebsocketUrl = config.get('websocketUrl', 'ws://localhost:8000/ws');

        // 🔍 CHANGE DETECTION - did any of our important settings actually change?
        if (newServerUrl !== this.serverUrl || newWebsocketUrl !== this.websocketUrl) {
            // 📝 SETTINGS UPDATE - record the new configuration
            this.serverUrl = newServerUrl;
            this.websocketUrl = newWebsocketUrl;
            
            // 🔄 RECONNECTION PROTOCOL - if we're actively monitoring, restart with new settings
            if (this.isMonitoring) {
                // Like hanging up the old phone call and dialing the new number
                this.stopMonitoring();
                this.startMonitoring();
            }
            
            // 🔔 STATUS UPDATE - let VS Code know about the configuration change
            this.updateStatusBar();
        }
    }

    /**
     * 🚀 RADAR ACTIVATION - powering up our error monitoring system
     * 
     * This method starts our active monitoring system, establishing real-time
     * communication with the Debuggle server and beginning the scanning process.
     * It's like turning on a radar system and starting to actively search for problems.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like starting up a security camera system:
     * 1. Turn on all the cameras (establish connection)
     * 2. Start recording and analyzing the video feed (monitor for errors)
     * 3. Set up alerts for when something unusual happens (error notifications)
     * 4. Update the security office display to show "MONITORING ACTIVE"
     * 
     * The 'async' keyword means this process might take some time (like waiting
     * for internet connection), so we don't freeze VS Code while it's working.
     */
    public async startMonitoring(): Promise<void> {
        // 🚦 SYSTEM STATUS CHECK - make sure we're not already running
        // Like checking if the security cameras are already on before trying to turn them on
        if (this.isMonitoring) {
            vscode.window.showInformationMessage('Debuggle monitoring is already active');
            return;
        }

        try {
            // 📡 COMMUNICATION SETUP - establish real-time connection to Debuggle server
            // Like dialing the security company to establish the monitoring connection
            await this.connectWebSocket();
            
            // 🔧 SERVER CONFIGURATION - tell the server to start sending us error data
            // Like programming the security system to send alerts to our monitoring station
            await this.enableServerMonitoring();
            
            // ✅ ACTIVATION CONFIRMATION - officially mark our system as active
            // Like flipping the "MONITORING ACTIVE" switch in the control room
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