#!/bin/bash

# Cross-platform build script for Debuggle
# Builds standalone executables for Windows, Linux, and macOS

echo "🚀 Debuggle Multi-Platform Build System"
echo "======================================"

# Function to build for a specific platform
build_for_platform() {
    local platform=$1
    local arch=$2
    
    echo ""
    echo "🔨 Building for $platform-$arch..."
    
    if [ "$platform" = "windows" ]; then
        # Cross-compile for Windows (requires wine on Linux/Mac)
        if command -v wine &> /dev/null; then
            echo "🍷 Using Wine for Windows cross-compilation"
            wine python scripts/build_standalone.py
        else
            echo "⚠️  Wine not found - skipping Windows build"
            echo "   Install wine to enable Windows cross-compilation"
        fi
    else
        # Native build
        python3 scripts/build_standalone.py
    fi
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install build dependencies
echo "📦 Installing build dependencies..."
python3 -m pip install -r requirements-build.txt

# Detect current platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $OS in
    linux*)
        PLATFORM="linux"
        ;;
    darwin*)
        PLATFORM="macos"
        ;;
    mingw*|cygwin*|msys*)
        PLATFORM="windows"
        ;;
    *)
        echo "❌ Unsupported operating system: $OS"
        exit 1
        ;;
esac

# Normalize architecture
case $ARCH in
    x86_64|amd64)
        ARCH="x64"
        ;;
    i386|i686)
        ARCH="x86"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    *)
        echo "⚠️  Unknown architecture: $ARCH, using as-is"
        ;;
esac

echo "🖥️  Detected platform: $PLATFORM-$ARCH"

# Build for current platform
build_for_platform $PLATFORM $ARCH

# Ask if user wants to build for other platforms
echo ""
echo "🤔 Would you like to build for other platforms?"
echo "   (Requires appropriate cross-compilation tools)"
echo ""

read -p "Build all platforms? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌍 Building for all supported platforms..."
    
    # Build for common platforms
    case $PLATFORM in
        linux)
            echo "Building additional Linux variants..."
            # Could add ARM builds here
            ;;
        macos)
            echo "Building additional macOS variants..."
            # Could add Intel/Apple Silicon specific builds
            ;;
        windows)
            echo "Building additional Windows variants..."
            # Could add 32-bit builds
            ;;
    esac
fi

echo ""
echo "✅ Build process completed!"
echo "📦 Check the build_standalone directory for your executables"
echo ""
echo "💡 Distribution files are ready to share:"
echo "   - No Python installation required on target systems"
echo "   - No admin privileges needed to run"
echo "   - Self-contained with all dependencies"
echo ""
echo "🚀 To distribute:"
echo "   1. Share the .zip/.tar.gz file"
echo "   2. Users extract and run the launcher script"
echo "   3. Browser opens to http://localhost:8000"
echo "   4. Drag & drop logs to analyze!"