@echo off
REM Desktop Pet - Complete Setup and Build Script
REM This script does EVERYTHING needed to create the standalone executable

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  Desktop Pet - One-Click Build                ║
echo ║                                                                ║
echo ║  This script will:                                            ║
echo ║    1. Check Python installation                               ║
echo ║    2. Install all required dependencies                       ║
echo ║    3. Build a standalone .exe file                            ║
echo ║                                                                ║
echo ║  The resulting .exe can run without Python installed!         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
python --version
echo.

echo Starting automated setup and build...
echo.

REM Run the Python build script (which handles dependency installation)
python build_exe.py

if errorlevel 1 (
    echo.
    echo ❌ Build failed! Check the errors above.
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                     BUILD SUCCESSFUL!                          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Your standalone executable is ready in the dist\ folder!
echo You can now run DesktopPet.exe without needing Python installed.
echo.
pause
