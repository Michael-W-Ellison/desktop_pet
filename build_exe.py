#!/usr/bin/env python3
"""
Automated build script for Desktop Pet executable.

This script:
1. Checks and installs required dependencies
2. Verifies PyInstaller is available
3. Creates a placeholder icon if needed
4. Builds the standalone executable
5. Cleans up build artifacts
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path


def print_header(message):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70 + "\n")


def check_python_version():
    """Ensure Python version is compatible."""
    print_header("Checking Python Version")

    if sys.version_info < (3, 7):
        print("❌ ERROR: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_and_install_dependencies():
    """Check if required packages are installed, install if missing."""
    print_header("Checking Dependencies")

    required_packages = {
        'PyQt5': 'PyQt5>=5.15.0',
        'PIL': 'Pillow>=9.0.0',
        'numpy': 'numpy>=1.21.0',
        'PyInstaller': 'pyinstaller>=5.0.0',
    }

    missing_packages = []

    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing package(s)...")

        # Install from requirements.txt
        if os.path.exists('requirements.txt'):
            print("   Using requirements.txt...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Error installing from requirements.txt:\n{result.stderr}")
                return False

        # Install PyInstaller separately
        if 'pyinstaller>=5.0.0' in missing_packages:
            print("   Installing PyInstaller...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'pyinstaller>=5.0.0'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"❌ Error installing PyInstaller:\n{result.stderr}")
                return False

        print("✓ All dependencies installed successfully")

    return True


def create_placeholder_icon():
    """Create a placeholder icon if one doesn't exist."""
    print_header("Checking Icon File")

    icon_dir = Path('assets')
    icon_path = icon_dir / 'icon.ico'

    if icon_path.exists():
        print(f"✓ Icon file exists: {icon_path}")
        return True

    print("⚠ No icon file found, creating placeholder...")

    # Create assets directory
    icon_dir.mkdir(exist_ok=True)

    # Create a simple icon using PIL
    try:
        from PIL import Image, ImageDraw

        # Create a 256x256 image
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw a simple egg shape
        draw.ellipse([40, 30, 216, 226], fill='#FFE66D', outline='#FF6B6B', width=4)

        # Save as ICO (Windows icon format)
        img.save(str(icon_path), format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"✓ Created placeholder icon: {icon_path}")
        return True

    except Exception as e:
        print(f"⚠ Could not create icon: {e}")
        print("  (Build will continue without icon)")
        return True  # Don't fail the build


def clean_build_artifacts():
    """Remove old build artifacts."""
    print_header("Cleaning Old Build Artifacts")

    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec~']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"  Removing {dir_name}/")
            shutil.rmtree(dir_name)

    print("✓ Build directories cleaned")


def build_executable():
    """Build the executable using PyInstaller."""
    print_header("Building Executable")

    spec_file = 'desktop_pet.spec'

    if not os.path.exists(spec_file):
        print(f"❌ ERROR: {spec_file} not found")
        return False

    print(f"📦 Running PyInstaller with {spec_file}...")
    print("   This may take a few minutes...\n")

    result = subprocess.run(
        [sys.executable, '-m', 'PyInstaller', spec_file, '--clean'],
        capture_output=False,  # Show output in real-time
        text=True
    )

    if result.returncode != 0:
        print("\n❌ Build failed!")
        return False

    print("\n✓ Build completed successfully!")
    return True


def verify_executable():
    """Verify the executable was created."""
    print_header("Verifying Executable")

    exe_name = 'DesktopPet.exe' if sys.platform == 'win32' else 'DesktopPet'
    exe_path = Path('dist') / exe_name

    if not exe_path.exists():
        print(f"❌ ERROR: Executable not found at {exe_path}")
        return False

    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✓ Executable created: {exe_path}")
    print(f"  Size: {size_mb:.2f} MB")

    return True


def print_success_message():
    """Print final success message with instructions."""
    print_header("BUILD SUCCESSFUL!")

    exe_name = 'DesktopPet.exe' if sys.platform == 'win32' else 'DesktopPet'

    print("Your standalone executable is ready!")
    print(f"\n📁 Location: dist/{exe_name}\n")
    print("What you can do now:")
    print(f"  1. Run the executable: .\\dist\\{exe_name}")
    print(f"  2. Move it anywhere on your computer")
    print(f"  3. Share it with others (no Python installation needed!)")
    print("\nNote: The executable includes all dependencies and can run")
    print("      on any compatible system without requiring Python.")
    print("\n" + "=" * 70 + "\n")


def main():
    """Main build process."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                 Desktop Pet - Build Script                        ║")
    print("║              Creating Standalone Executable                       ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", check_and_install_dependencies),
        ("Creating icon", create_placeholder_icon),
        ("Cleaning old builds", lambda: (clean_build_artifacts(), True)[1]),
        ("Building executable", build_executable),
        ("Verifying build", verify_executable),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Build failed at step: {step_name}")
            print("\nPlease fix the errors above and try again.")
            sys.exit(1)

    print_success_message()
    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
