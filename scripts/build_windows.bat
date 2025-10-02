@echo off
REM Windows build script for Debuggle
REM Builds standalone executable for Windows

echo 🚀 Debuggle Windows Build System
echo ===================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install build dependencies
echo 📦 Installing build dependencies...
python -m pip install -r requirements-build.txt

REM Run the build script
echo 🔨 Building Windows executable...
python scripts\build_standalone.py

echo.
echo ✅ Build process completed!
echo 📦 Check the build_standalone directory for your executable
echo.
echo 💡 Distribution files are ready to share:
echo    - No Python installation required on target systems
echo    - No admin privileges needed to run
echo    - Self-contained with all dependencies
echo.
echo 🚀 To distribute:
echo    1. Share the .zip file
echo    2. Users extract and run start_debuggle.bat
echo    3. Browser opens to http://localhost:8000
echo    4. Drag ^& drop logs to analyze!

pause