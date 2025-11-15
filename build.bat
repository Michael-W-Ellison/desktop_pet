@echo off
echo ========================================
echo Desktop Pet - Build Executable
echo ========================================
echo.

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller --name "DesktopPet" --windowed --onefile desktop_pet.py --add-data "src;src"

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo The executable can be found at:
echo   dist\DesktopPet.exe
echo.
pause
