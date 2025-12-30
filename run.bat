@echo off
echo Starting Desktop Pal...
python desktop_pet.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Desktop Pal
    echo Make sure you have run setup.bat first
    pause
)
