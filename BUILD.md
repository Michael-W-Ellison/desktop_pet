# Building Desktop Pet - Standalone Executable Guide

This guide explains how to build a standalone executable (.exe) that includes all dependencies and can run without Python installed.

## 🚀 Quick Start (Easiest Method)

### Windows

**Double-click:** `setup_and_build.bat`

That's it! This one script does everything:
- Checks Python installation
- Installs all dependencies automatically
- Builds the standalone .exe file

The executable will be in the `dist/` folder.

### Linux/Mac

```bash
chmod +x build_exe.sh
./build_exe.sh
```

---

## 📋 Requirements

- **Python 3.7 or higher** (must be in PATH)
- **Internet connection** (for downloading dependencies)
- **~500MB free disk space** (for build process and dependencies)

### How to Check if Python is Installed

**Windows:** Open Command Prompt and type:
```cmd
python --version
```

**Linux/Mac:** Open Terminal and type:
```bash
python3 --version
```

If Python is not installed, download from: https://www.python.org/downloads/

**Important for Windows:** During installation, check "Add Python to PATH"!

---

## 🔧 Manual Build Process

If you prefer more control, follow these steps:

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller>=5.0.0
```

### Step 2: Run Build Script

**Windows:**
```cmd
python build_exe.py
```

**Linux/Mac:**
```bash
python3 build_exe.py
```

### Step 3: Find Your Executable

The standalone executable will be in:
- **Windows:** `dist/DesktopPet.exe`
- **Linux:** `dist/DesktopPet`
- **Mac:** `dist/DesktopPet.app`

---

## 🎯 What the Build Script Does

The `build_exe.py` script automatically:

1. ✅ **Checks Python version** (ensures 3.7+)
2. 📦 **Installs missing dependencies**
   - PyQt5 (GUI framework)
   - Pillow (image generation)
   - numpy (neural networks)
   - PyInstaller (packaging tool)
3. 🎨 **Creates placeholder icon** (if none exists)
4. 🧹 **Cleans old build files**
5. 🔨 **Builds the executable** (using PyInstaller)
6. ✔️ **Verifies the build** (checks file exists)

The entire process takes 3-5 minutes on average.

---

## 📦 Build Configuration

The build is configured using `desktop_pet.spec` which:

- **Bundles all Python modules** (src/core and src/ui)
- **Includes all dependencies** (PyQt5, Pillow, numpy)
- **Creates single-file executable** (no external files needed)
- **Optimizes size** (excludes unused modules like matplotlib, pandas)
- **Sets GUI mode** (no console window appears)
- **Adds application icon** (if available)

### Customizing the Build

Edit `desktop_pet.spec` to:
- Change the executable name (`name='DesktopPet'`)
- Add custom icon (`icon='path/to/icon.ico'`)
- Include additional files (`datas=[...]`)
- Exclude more modules (`excludes=[...]`)

After editing the spec file, rebuild with:
```bash
pyinstaller desktop_pet.spec --clean
```

---

## 🐛 Troubleshooting

### Build Fails with "Module not found"

**Solution:** Install the missing module:
```bash
pip install <module-name>
```

### Build Succeeds but Executable Won't Run

**Common causes:**

1. **Antivirus blocking**: Add exception for the executable
2. **Missing DLL files**: Rebuild with `--clean` flag
3. **PyQt5 issues**: Reinstall PyQt5:
   ```bash
   pip uninstall PyQt5
   pip install PyQt5>=5.15.0
   ```

### Executable is Too Large (>100MB)

This is normal! The executable includes:
- Python runtime
- PyQt5 GUI framework
- All application modules
- Neural network libraries

To reduce size, you can use UPX compression (already enabled in spec file).

### "Python not found" Error

**Windows:**
1. Reinstall Python from python.org
2. Check "Add Python to PATH" during installation
3. Restart Command Prompt

**Linux/Mac:**
```bash
# Install Python 3
sudo apt install python3 python3-pip  # Ubuntu/Debian
brew install python3                   # Mac
```

---

## 🎁 Distributing the Executable

The built executable is **completely standalone**:

- ✅ No Python installation needed
- ✅ No pip packages required
- ✅ All dependencies included
- ✅ Works on any compatible system

### What to Share

**Just send:** `dist/DesktopPet.exe` (Windows) or `dist/DesktopPet` (Linux/Mac)

**Recipients can:**
1. Download the file
2. Double-click to run
3. Enjoy their desktop pet!

**Note:** On first run, the application will:
- Create a `pet_data.json` file (for saving pet state)
- Generate procedural sprites (no external images needed)

---

## 🔍 Build Output Files

After building, you'll see:

```
desktop_pet/
├── dist/
│   └── DesktopPet.exe          ← YOUR EXECUTABLE (share this!)
├── build/                       ← Temporary build files (can delete)
│   └── DesktopPet/
└── desktop_pet.spec             ← Build configuration
```

**Safe to delete:**
- `build/` folder (temporary files)
- `__pycache__/` folders (cached Python files)

**Keep:**
- `dist/DesktopPet.exe` (your executable)
- `desktop_pet.spec` (for rebuilding)

---

## ⚡ Quick Reference

| Task | Windows | Linux/Mac |
|------|---------|-----------|
| **One-click build** | `setup_and_build.bat` | `./build_exe.sh` |
| **Manual build** | `python build_exe.py` | `python3 build_exe.py` |
| **Custom build** | `pyinstaller desktop_pet.spec` | `pyinstaller desktop_pet.spec` |
| **Clean rebuild** | `pyinstaller desktop_pet.spec --clean` | `pyinstaller desktop_pet.spec --clean` |

---

## 📝 Notes

- **First build** takes longer (downloads dependencies)
- **Subsequent builds** are faster (uses cache)
- **Executable size** is typically 80-150MB
- **Build time** is 3-5 minutes on average
- **Antivirus** may scan the new executable (this is normal)

---

## 🤝 Need Help?

If you encounter issues:

1. Check the error messages carefully
2. Ensure Python 3.7+ is installed and in PATH
3. Try a clean rebuild: `pyinstaller desktop_pet.spec --clean`
4. Check that all dependencies installed: `pip list`
5. Report issues with the full error output

---

**Happy building! 🎉**
