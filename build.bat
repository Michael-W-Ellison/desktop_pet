@echo off
REM Desktop Pet - Automated Build Script
REM This script builds a standalone .exe with all dependencies included

echo.
echo ========================================
echo Desktop Pal - Build Executable
echo ========================================
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://www.python.org/
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install pyinstaller pillow pyqt5 numpy pywin32

echo Running automated build script...
echo.
echo Building executable...

:: Build with PyInstaller
pyinstaller ^
    --name "DesktopPet" ^
    --windowed ^
    --onefile ^
    --icon "assets\icon.ico" ^
    --add-data "src;src" ^
    desktop_pet.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the errors above.
    pause
    exit /b 1
)

:: Create assets directory in dist if needed
if not exist "dist\assets" mkdir "dist\assets"

:: Copy assets if they exist
if exist "assets" (
    xcopy /E /Y "assets" "dist\assets\" >nul 2>&1
)

echo.
echo Build completed successfully!
echo Your executable is in the dist\ folder
echo.
echo To create an installer, run build_installer.bat
echo (Requires Inno Setup to be installed)
echo.
pause
