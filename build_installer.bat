@echo off
echo ========================================
echo Desktop Pal - Build Installer
echo ========================================
echo.

:: Check if executable exists
if not exist "dist\DesktopPet.exe" (
    echo ERROR: DesktopPet.exe not found in dist folder
    echo Please run build.bat first to create the executable
    echo.
    pause
    exit /b 1
)

:: Try to find Inno Setup
set ISCC_PATH=

:: Check common installation paths
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe
) else if exist "%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe" (
    set ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe
) else if exist "%ProgramFiles%\Inno Setup 5\ISCC.exe" (
    set ISCC_PATH=%ProgramFiles%\Inno Setup 5\ISCC.exe
)

:: Check if Inno Setup was found
if "%ISCC_PATH%"=="" (
    echo ERROR: Inno Setup not found
    echo.
    echo Please install Inno Setup from:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo Found Inno Setup at: %ISCC_PATH%
echo.

:: Create installer output directory
if not exist "dist\installer" mkdir "dist\installer"

:: Build the installer
echo Building installer...
"%ISCC_PATH%" "installer\desktop_pet.iss"

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installer build complete!
echo ========================================
echo.
echo The installer can be found at:
echo   dist\installer\DesktopPetSetup.exe
echo.
pause
