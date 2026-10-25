"""
Generate application icon for Desktop Pal.

This script creates an .ico file for the application using PIL/Pillow.
Run this script before building the installer.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from ui.creature_art import render_icon  # noqa: E402


def create_pet_icon(size=256):
    """
    Create the pet icon: a shaded cat portrait in a round badge.

    Args:
        size: Icon size in pixels

    Returns:
        PIL Image object
    """
    return render_icon(size)


def generate_ico_file(output_path='assets/icon.ico'):
    """
    Generate a Windows .ico file with multiple sizes.

    Args:
        output_path: Path to save the .ico file
    """
    # Create directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Generate icons at standard Windows sizes
    sizes = [16, 24, 32, 48, 64, 128, 256]
    icons = []

    for size in sizes:
        icon = create_pet_icon(size)
        icons.append(icon)

    # Save as .ico with multiple sizes: Pillow writes each size from the largest
    # image, or from an appended image of exactly that size when there is one
    icons[-1].save(
        output_path,
        format='ICO',
        append_images=icons[:-1],
        sizes=[(s, s) for s in sizes]
    )

    print(f"Icon saved to: {output_path}")

    # Also save a PNG version for other uses
    png_path = output_path.replace('.ico', '.png')
    icons[-1].save(png_path, format='PNG')
    print(f"PNG version saved to: {png_path}")


def main():
    """Generate the application icons."""
    print("Generating Desktop Pal icons...")
    print()

    generate_ico_file('assets/icon.ico')

    print()
    print("Done! Icons have been generated in the assets folder.")


if __name__ == '__main__':
    main()
