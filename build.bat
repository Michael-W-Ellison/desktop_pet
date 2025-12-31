@echo off
REM Desktop Pet - Automated Build Script
REM This script builds a standalone .exe with all dependencies included

echo.
echo ========================================
echo   Desktop Pet - Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo Running automated build script...
echo.

REM Run the Python build script
python build_exe.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the errors above.
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Your executable is in the dist\ folder
echo.
pause
