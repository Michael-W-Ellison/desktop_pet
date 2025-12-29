@echo off
echo ========================================
echo Desktop Pet - Build Executable
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
    echo ERROR: Build failed
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
echo ========================================
echo Build complete!
echo ========================================
echo.
echo The executable can be found at:
echo   dist\DesktopPet.exe
echo.
echo To create an installer, run build_installer.bat
echo (Requires Inno Setup to be installed)
echo.
pause
