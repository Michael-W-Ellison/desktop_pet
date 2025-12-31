#!/bin/bash
# Desktop Pet - Build Script for Linux/Mac
# This script builds a standalone executable with all dependencies included

echo ""
echo "========================================"
echo "  Desktop Pet - Build Script"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from your package manager"
    exit 1
fi

echo "Running automated build script..."
echo ""

# Run the Python build script
python3 build_exe.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Build failed! Check the errors above."
    exit 1
fi

echo ""
echo "Build completed successfully!"
echo "Your executable is in the dist/ folder"
echo ""
