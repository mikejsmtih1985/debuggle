#!/bin/bash

#
# 🏭 DEBUGGLE MULTI-PLATFORM FACTORY - The Universal Assembly Line
# =================================================================
#
# This shell script is like having a sophisticated manufacturing facility
# that can produce the same product (Debuggle) for different markets
# (Windows, Linux, macOS) using automated assembly lines.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like a car factory that can build the same car model
# but configure it for different countries:
# - Left-hand drive vs right-hand drive
# - Different electrical systems (110V vs 220V) 
# - Different safety standards and regulations
# - Different languages for the dashboard
#
# This script automates the entire "manufacturing process" so that with
# one command, we can produce ready-to-ship software packages for
# customers using Windows, Mac, or Linux computers.
#
# EDUCATIONAL METAPHORS USED:
# 🏭 Manufacturing & Factory Automation - Build processes like assembly lines
# 🔧 Industrial Engineering - Optimization and quality control
# 📦 Shipping & Logistics - Packaging and distribution
# 🏗️ Construction Management - Project coordination and sequencing
#

# 📢 FACTORY STARTUP ANNOUNCEMENT - Welcome message for operators
echo "🚀 Debuggle Multi-Platform Build System"
echo "======================================"

#
# 🎯 SPECIALIZED ASSEMBLY LINE FUNCTION - Platform-specific manufacturing
# =======================================================================
#
# This function is like having a flexible manufacturing station that can
# reconfigure itself to produce the same product for different markets.
# It's the core "assembly line worker" that knows how to build our software
# for specific operating systems.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like a skilled technician at a electronics factory who can
# assemble the same smartphone but configure it for different regions:
# - Different power adapters (US vs EU vs UK plugs)
# - Different cellular radio bands for local carriers  
# - Different languages pre-installed
# - Different safety certifications and stickers
#
# The technician follows different procedures depending on which market
# the product is destined for, but the core device is the same.
#
build_for_platform() {
    # 📋 WORK ORDER PARAMETERS - receiving instructions for this build job
    local platform=$1    # 🌍 Target operating system (windows, linux, macos)
    local arch=$2        # 🏗️ Processor architecture (x64, arm64, etc.)
    
    echo ""
    echo "🔨 Building for $platform-$arch..."
    
    # 🔀 PRODUCTION LINE ROUTING - choosing the right assembly process
    if [ "$platform" = "windows" ]; then
        #
        # 🍷 CROSS-PLATFORM MANUFACTURING - Building Windows software on non-Windows
        # ========================================================================
        #
        # This is like having a specialized workstation that can manufacture
        # products for a different market than where the factory is located.
        # Wine is a compatibility layer that lets Linux/Mac systems run
        # Windows programs, like having translation equipment in the factory.
        #
        if command -v wine &> /dev/null; then
            echo "🍷 Using Wine for Windows cross-compilation"
            # 🏭 Execute the build process through the compatibility layer
            wine python scripts/build_standalone.py
        else
            # 🚨 MISSING EQUIPMENT ALERT - can't complete this type of build
            echo "⚠️  Wine not found - skipping Windows build"
            echo "   Install wine to enable Windows cross-compilation"
        fi
    else
        # 🏠 NATIVE MANUFACTURING - building for the same system we're running on
        # Like having a local factory that produces goods for the local market
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