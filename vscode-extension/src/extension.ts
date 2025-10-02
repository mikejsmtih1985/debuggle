/**
 * 🚀 VS CODE EXTENSION COMMAND CENTER - The Space Mission Control! 🚀
 * 
 * Think of this file as the main control room at NASA's mission control center!
 * Just like how mission control coordinates all aspects of a space mission,
 * this extension coordinates all the monitoring and debugging features for Debuggle.
 * 
 * 🎯 WHAT THIS MODULE DOES:
 * This is the "mission director" that starts up our VS Code extension and makes
 * sure all the different systems (monitoring, dashboard, commands) work together
 * smoothly to help developers debug their code.
 * 
 * 🏢 THE MISSION CONTROL ANALOGY:
 * - extension.ts: The mission control director who oversees everything
 * - debuggleMonitor: The radar system that tracks errors in real-time
 * - monitoringPanel: The main mission dashboard with all the displays
 * - Commands: Different mission procedures the crew can execute
 * 
 * 🔧 HOW VS CODE EXTENSIONS WORK:
 * 1. VS Code calls activate() when someone installs/enables our extension
 * 2. We register all our commands (like buttons the user can click)
 * 3. We start up our monitoring systems
 * 4. VS Code calls deactivate() when the extension shuts down
 * 
 * Real-world analogy: This is like the main electrical panel in your house that
 * controls all the different circuits and systems - lights, outlets, heating, etc.
 */

import * as vscode from 'vscode';
import { DebugglerMonitor } from './debuggleMonitor';
import { MonitoringPanel } from './monitoringPanel';

// 🎛️ GLOBAL MISSION CONTROL SYSTEMS - Our main operational equipment
// These variables store the key systems that run throughout the mission

// 📡 THE RADAR SYSTEM - monitors for errors and problems in real-time
// Like the radar dish that tracks spacecraft and incoming signals
let debuggleMonitor: DebugglerMonitor;

// 🖥️ THE MAIN DASHBOARD - the big screen where mission status is displayed
// Like the huge wall of monitors you see in NASA mission control
// This might be undefined if the dashboard isn't currently open
let monitoringPanel: MonitoringPanel | undefined;

export function activate(context: vscode.ExtensionContext) {
    /**
     * 🚀 MISSION LAUNCH SEQUENCE - Starting Up Our Space Program!
     * 
     * This function is called when VS Code starts our extension - like the moment
     * when mission control comes online and all the systems boot up for a space mission.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like starting up a complex video game or launching a sophisticated
     * app on your phone. The system needs to:
     * 1. Initialize all the different components
     * 2. Set up all the buttons and menus
     * 3. Connect to external services
     * 4. Be ready for user interaction
     * 
     * The 'context' parameter is like the game's save file - it contains all the
     * settings and resources our extension needs to operate properly.
     */
    
    // 📢 MISSION STATUS ANNOUNCEMENT - let everyone know we're online!
    // Like the mission director announcing "Mission Control is go for launch!"
    console.log('Debuggle Monitor extension is now active!');

    // 🏗️ SYSTEM INITIALIZATION - set up our main radar/monitoring system
    // Like powering up the main radar dish and calibrating all the sensors
    debuggleMonitor = new DebugglerMonitor(context);

    // 🎛️ MISSION COMMAND REGISTRATION - set up all the buttons mission control can press
    // Like programming all the different procedures and emergency protocols
    // Each command is like a different button on the mission control panel
    const commands = [
        // 🟢 "START MONITORING" BUTTON - begin tracking errors in real-time
        // Like turning on the radar to start tracking spacecraft
        vscode.commands.registerCommand('debuggle.startMonitoring', () => {
            debuggleMonitor.startMonitoring();
        }),

        // 🔴 "STOP MONITORING" BUTTON - pause error tracking
        // Like putting the radar on standby mode
        vscode.commands.registerCommand('debuggle.stopMonitoring', () => {
            debuggleMonitor.stopMonitoring();
        }),

        // 📊 "SHOW DASHBOARD" BUTTON - open the main mission control screen
        // Like bringing up the big wall of monitors with all the mission data
        vscode.commands.registerCommand('debuggle.showDashboard', () => {
            if (monitoringPanel) {
                // Dashboard already exists - just bring it to the front
                // Like switching to a screen that's already on
                monitoringPanel.reveal();
            } else {
                // Create a new dashboard from scratch
                // Like powering up a new monitor and loading the mission display
                monitoringPanel = new MonitoringPanel(context.extensionUri, debuggleMonitor);
                
                // Set up cleanup when the dashboard is closed
                // Like scheduling automatic shutdown when mission control closes a screen
                monitoringPanel.onDidDispose(() => {
                    monitoringPanel = undefined;
                });
            }
        }),

        // 🧹 "CLEAR ERRORS" BUTTON - reset the error log
        // Like clearing the mission log to start fresh
        vscode.commands.registerCommand('debuggle.clearErrors', () => {
            debuggleMonitor.clearErrors();
        }),

        // 🔗 "CONNECT TO SERVER" BUTTON - establish communication with Debuggle server
        // Like establishing radio contact with the spacecraft
        vscode.commands.registerCommand('debuggle.connectToServer', () => {
            debuggleMonitor.connectToServer();
        }),

        // 🧪 "TEST CONNECTION" BUTTON - verify our communication link is working
        // Like doing a radio check: "Houston, do you copy?"
        vscode.commands.registerCommand('debuggle.testConnection', () => {
            debuggleMonitor.testConnection();
        })
    ];

    // 📝 MISSION PROTOCOL REGISTRATION - officially register all our procedures
    // Like filing all the emergency protocols with mission headquarters so they
    // know what buttons do what. The 'context.subscriptions' is like the official
    // mission manual where all procedures get recorded.
    commands.forEach(command => context.subscriptions.push(command));

    // 🚀 AUTO-CONNECT SEQUENCE - establish communication automatically if configured
    // Like having an automatic "phone home" protocol when mission control starts up
    const config = vscode.workspace.getConfiguration('debuggle');
    if (config.get('autoConnect', true)) {
        // The user has enabled auto-connect in their settings
        // Like having "establish radio contact" checked in the startup checklist
        debuggleMonitor.connectToServer();
    }

    // 🏷️ MISSION STATUS INDICATOR - tell VS Code what our current state is
    // Like updating the mission status board so other systems know we're not
    // actively monitoring yet (we're ready, but haven't started scanning)
    vscode.commands.executeCommand('setContext', 'debuggle.monitoring.active', false);
    
    /**
     * 🎯 MISSION ACTIVATION COMPLETE!
     * 
     * At this point, our extension is fully operational and ready to:
     * - Monitor for errors in real-time
     * - Display beautiful dashboards with error information
     * - Connect to the Debuggle server for enhanced debugging
     * - Respond to all user commands through VS Code's interface
     * 
     * It's like mission control is now fully staffed, all systems are green,
     * and we're ready for whatever debugging challenges come our way!
     */
}

export function deactivate() {
    /**
     * 🛑 MISSION SHUTDOWN SEQUENCE - safely powering down our space program
     * 
     * This function is called when VS Code shuts down our extension - like the
     * end-of-mission protocol where we need to safely power down all systems.
     * 
     * 🏆 HIGH SCHOOL EXPLANATION:
     * Think of this like properly shutting down a computer or closing a complex
     * video game. We can't just pull the plug - we need to:
     * 1. Save any important data
     * 2. Close all open connections
     * 3. Clean up temporary files
     * 4. Let other systems know we're going offline
     * 
     * This prevents crashes and ensures everything is ready for the next time
     * we start up the extension.
     */
    
    if (debuggleMonitor) {
        // 📡 RADAR SHUTDOWN - turn off our error monitoring system
        // Like powering down the radar dish and stopping all scanning operations
        debuggleMonitor.dispose();
    }
    
    if (monitoringPanel) {
        // 📺 DASHBOARD SHUTDOWN - close the mission control screens
        // Like turning off all the monitors and control panels
        monitoringPanel.dispose();
    }
    
    /**
     * 👋 MISSION CONTROL SIGNING OFF
     * 
     * All systems are now safely powered down. The extension has been cleanly
     * deactivated and VS Code can shut down without any issues.
     * 
     * Until next time, this is Debuggle Mission Control - over and out! 🚀
     */
}