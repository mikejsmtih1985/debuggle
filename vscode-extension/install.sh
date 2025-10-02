#!/bin/bash

# Debuggle VS Code Extension Installation Script

set -e

echo "🚀 Installing Debuggle Monitor VS Code Extension"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: This script must be run from the vscode-extension directory"
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is required but not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is required but not installed"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo "🔨 Compiling TypeScript..."
npm run compile

echo "📋 Extension compiled successfully!"
echo ""
echo "🎯 Next Steps:"
echo "1. Open VS Code"
echo "2. Press F1 and type 'Extensions: Install from VSIX'"
echo "3. Or run: code --install-extension debuggle-monitor-1.0.0.vsix"
echo ""
echo "🔧 For Development:"
echo "1. Open VS Code in this directory"
echo "2. Press F5 to launch Extension Development Host"
echo "3. The extension will be loaded for testing"
echo ""
echo "📚 Documentation: ../docs/VSCODE_INTEGRATION.md"
echo ""
echo "✅ Installation complete!"