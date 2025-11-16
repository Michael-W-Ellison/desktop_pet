# 🚀 Desktop Pet - 5-Minute Build Guide

Want to create a standalone executable that runs without Python? Follow these simple steps!

## For Windows Users

### Method 1: The Super Easy Way (Recommended)

1. **Download or clone** this repository
2. **Double-click:** `setup_and_build.bat`
3. **Wait 3-5 minutes** while it builds
4. **Done!** Find your executable at: `dist/DesktopPet.exe`

### Method 2: Command Line

1. Open Command Prompt in the project folder
2. Run: `setup_and_build.bat`
3. Done!

---

## For Linux/Mac Users

1. Open Terminal in the project folder
2. Make the script executable: `chmod +x build_exe.sh`
3. Run: `./build_exe.sh`
4. Done! Find your executable at: `dist/DesktopPet`

---

## What if I Don't Have Python?

### Windows
1. Download Python from: https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Restart your computer
4. Try again!

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Mac
```bash
brew install python3
```

---

## What Gets Built?

A **single executable file** that:
- ✅ Runs without Python installed
- ✅ Includes all dependencies
- ✅ Can be shared with anyone
- ✅ Works immediately when double-clicked

**File sizes:**
- Windows: ~100-150MB
- Linux: ~80-120MB
- Mac: ~90-130MB

---

## Sharing Your Build

Just send the file from the `dist/` folder:
- **Windows:** `dist/DesktopPet.exe`
- **Linux:** `dist/DesktopPet`
- **Mac:** `dist/DesktopPet.app`

No installation needed! Recipients can just run it.

---

## Troubleshooting

### "Python is not recognized"
- Reinstall Python with "Add to PATH" checked
- Or use absolute path: `C:\Python39\python.exe build_exe.py`

### "Permission denied" (Linux/Mac)
```bash
chmod +x build_exe.sh
./build_exe.sh
```

### Build fails
1. Check you have internet connection (downloads dependencies)
2. Try: `python build_exe.py` (shows detailed errors)
3. See [BUILD.md](BUILD.md) for detailed troubleshooting

---

## That's It!

Your standalone Desktop Pet executable is ready to use and share! 🎉

For more details, see [BUILD.md](BUILD.md)
