@echo off
echo Starting Desktop Pet...
python desktop_pet.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start Desktop Pet
    echo Make sure you have run setup.bat first
    pause
)
