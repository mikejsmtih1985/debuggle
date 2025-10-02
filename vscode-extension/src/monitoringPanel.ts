/**
 * 📺 DEBUGGLE MISSION CONTROL DASHBOARD - The Visual Command Center
 * 
 * This file creates the beautiful, interactive dashboard that displays all our
 * error monitoring information in an easy-to-understand visual format.
 * Think of it as the main screen in mission control where all the important
 * information is displayed with charts, graphs, and real-time updates.
 * 
 * 🏆 HIGH SCHOOL EXPLANATION:
 * Imagine you're building the main dashboard for a space mission control room.
 * You need:
 * 1. Large displays showing current status and data (the webview panel)
 * 2. Interactive controls and buttons (message handling)
 * 3. Connection to all the monitoring equipment (DebugglerMonitor integration)
 * 4. Automatic updates so the information stays current (periodic refreshes)
 * 
 * This file handles all of that, creating a professional-looking interface
 * that makes complex debugging information easy to understand and act on.
 */

// 🏗️ MISSION CONTROL TOOLKIT - importing our essential dashboard tools
import * as vscode from 'vscode';                                    // Like importing the display system framework
import { DebugglerMonitor, DebugglerError } from './debuggleMonitor'; // Like connecting to our radar and monitoring systems

/**
 * 🎯 MISSION CONTROL DASHBOARD - The Visual Command Center
 * 
 * This class creates and manages the interactive dashboard panel where users
 * can see all their error information, monitoring status, and control the
 * debugging system. It's like the main control panel in a spaceship cockpit.
 * 
 * 🏆 HIGH SCHOOL EXPLANATION:
 * Think of this like creating a custom app interface on a tablet that shows:
 * - Real-time charts and graphs of system performance
 * - Big, colorful buttons to control different functions
 * - Status indicators showing whether systems are online or offline
 * - Automatic updates so the information is always current
 * 
 * The panel is like a window within VS Code that displays our custom web page
 * with all the debugging information formatted in a beautiful, easy-to-read way.
 */
export class MonitoringPanel {
    // 🏷️ PANEL IDENTIFICATION - unique identifier for our dashboard type
    // Like having a model number that VS Code uses to recognize our specific dashboard
    public static readonly viewType = 'debuggleMonitoring';
    
    // 📺 MAIN DISPLAY SCREEN - the actual panel that shows our dashboard
    // Like the main monitor in mission control that displays all the important information
    private panel: vscode.WebviewPanel;
    
    // 🗑️ CLEANUP CREW - list of things to clean up when we shut down
    // Like having a checklist of equipment to power down when the mission ends
    private disposables: vscode.Disposable[] = [];
    
    // 📡 RADAR CONNECTION - our link to the error monitoring system
    // Like having a direct line to the radar operators who report what they see
    private monitor: DebugglerMonitor;

    /**
     * 🚀 DASHBOARD CONSTRUCTION - building our mission control interface
     * 
     * This constructor creates and sets up our interactive dashboard panel.
     * It's like setting up a new control room with all the screens, buttons,
     * and communication systems needed to monitor and control operations.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like setting up a streaming setup with multiple monitors:
     * 1. Create the main display window (webview panel)
     * 2. Connect it to your data sources (monitor connection)
     * 3. Set up interactive controls (message handling)
     * 4. Configure automatic updates (event listeners)
     * 5. Plan for proper cleanup when you're done (disposal management)
     * 
     * The extensionUri parameter tells us where our extension's files are stored,
     * and the monitor parameter connects us to our error detection system.
     */
    constructor(extensionUri: vscode.Uri, monitor: DebugglerMonitor) {
        // 📡 RADAR CONNECTION - establish link to our monitoring system
        this.monitor = monitor;
        
        // 📺 MAIN DASHBOARD CREATION - build the visual interface panel
        // Like setting up a new monitor and configuring it for our mission control room
        this.panel = vscode.window.createWebviewPanel(
            MonitoringPanel.viewType,           // 🏷️ Panel type identifier
            'Debuggle Monitor Dashboard',       // 📋 Title shown in VS Code tab
            vscode.ViewColumn.One,              // 📍 Where to position the panel
            {
                enableScripts: true,            // 🔧 Allow JavaScript for interactivity
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')] // 📁 Where to find our assets
            }
        );

        // 🎨 DASHBOARD CONTENT - load the HTML/CSS/JavaScript for our interface
        // Like loading the software that creates all the charts, graphs, and buttons
        this.panel.webview.html = this.getWebviewContent();
        
        // 🗑️ CLEANUP SCHEDULING - plan for proper shutdown when panel is closed
        // Like programming the automatic shutdown sequence when mission control closes
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);
        
        // 🎛️ CONTROL SYSTEM - set up interactive button handling
        // Like programming what happens when operators press different control buttons
        this.panel.webview.onDidReceiveMessage(
            (message: any) => {
                // 📨 MESSAGE PROCESSING - handle commands from the dashboard interface
                switch (message.command) {
                    case 'refresh':
                        // 🔄 REFRESH BUTTON - update the display with latest information
                        this.updateContent();
                        break;
                    case 'clearErrors':
                        // 🧹 CLEAR BUTTON - reset the error log and update display
                        this.monitor.clearErrors();
                        this.updateContent();
                        break;
                    case 'startMonitoring':
                        // 🚀 START BUTTON - begin error monitoring operations
                        this.monitor.startMonitoring();
                        break;
                    case 'stopMonitoring':
                        // 🛑 STOP BUTTON - pause error monitoring operations
                        this.monitor.stopMonitoring();
                        break;
                }
            },
            null,
            this.disposables
        );

        // ⏰ AUTOMATIC UPDATES - set up periodic refresh of dashboard information
        // Like having a digital clock that updates every second, we refresh our
        // error information every 2 seconds to keep everything current
        const updateInterval = setInterval(() => {
            this.updateContent();
        }, 2000);

        // 📋 CLEANUP REGISTRATION - add the update timer to our cleanup list
        // When we shut down the dashboard, we need to stop the automatic updates
        // to prevent memory leaks and unnecessary processing
        this.disposables.push({
            dispose: () => clearInterval(updateInterval)
        });

        // 🎬 INITIAL DISPLAY - show the first version of our dashboard
        // Like turning on the monitors and displaying the starting information
        this.updateContent();
        
        /**
         * 🎯 MISSION CONTROL DASHBOARD READY!
         * 
         * At this point, our interactive dashboard is fully operational and ready to:
         * - Display real-time error information with beautiful formatting
         * - Respond to user button clicks and commands
         * - Update automatically every 2 seconds with fresh data
         * - Handle proper cleanup when the user closes the panel
         * 
         * It's like having a fully functional mission control center that's
         * staffed, powered up, and ready to monitor and control operations!
         */
    }

    public reveal() {
        this.panel.reveal(vscode.ViewColumn.One);
    }

    public onDidDispose(callback: () => void) {
        this.panel.onDidDispose(callback);
    }

    /**
     * 🔄 DASHBOARD REFRESH - updating the display with latest information
     * 
     * This method fetches the latest error data from our monitoring system and
     * sends it to the dashboard display for visual presentation. It's like a
     * mission control operator updating all the screens with the newest data.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like refreshing a social media app:
     * 1. Ask the server for the latest posts (get errors from monitor)
     * 2. Check if you're currently online (get monitoring status)
     * 3. Package all the information together (create data object)
     * 4. Send it to your app's display system (post message to webview)
     * 
     * This happens automatically every 2 seconds to keep the dashboard current.
     */
    private updateContent() {
        // 📊 DATA COLLECTION - gather the latest information from our monitoring system
        const errors = this.monitor.getErrors();    // 🚨 Get all detected errors
        const isActive = this.monitor.isActive();   // 🚦 Check if monitoring is currently running
        
        // 📤 DATA TRANSMISSION - send the fresh information to our dashboard display
        // Like mission control updating all the wall displays with new data
        this.panel.webview.postMessage({
            command: 'updateData',              // 📋 Tell the dashboard this is a data update
            data: {
                errors: errors,                 // 🚨 The list of all current errors
                isActive: isActive,             // 🚦 Whether monitoring is currently active
                timestamp: new Date().toISOString() // ⏰ When this update was created
            }
        });
    }

    /**
     * 🎨 DASHBOARD DESIGN - creating the visual interface HTML
     * 
     * This method generates the HTML code that creates our beautiful dashboard
     * interface. It's like being a web designer who creates the layout, styling,
     * and interactive elements for our mission control display.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like creating a custom website that will be displayed
     * inside VS Code. This method writes all the HTML, CSS, and JavaScript
     * needed to create:
     * - Beautiful charts and graphs showing error data
     * - Colorful buttons for controlling the monitoring system
     * - Status indicators showing whether systems are online
     * - Professional styling that looks like a real control center
     * 
     * The returned string contains a complete web page that VS Code will
     * display in our panel, just like opening a website in a browser.
     */
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