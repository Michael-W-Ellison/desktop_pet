"""
Generate application icon for Desktop Pet.

This script creates an .ico file for the application using PIL/Pillow.
Run this script before building the installer.
"""
import os
from PIL import Image, ImageDraw

def create_pet_icon(size=256):
    """
    Create a simple pet icon.

    Args:
        size: Icon size in pixels

    Returns:
        PIL Image object
    """
    # Create a new image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    body_color = (255, 180, 120)  # Peachy/orange
    eye_color = (50, 50, 50)       # Dark gray
    nose_color = (200, 100, 80)    # Pink/red
    highlight = (255, 220, 180)    # Light highlight

    # Calculate proportions
    center_x = size // 2
    center_y = size // 2
    body_radius = int(size * 0.4)
    ear_size = int(size * 0.15)
    eye_size = int(size * 0.08)
    nose_size = int(size * 0.06)

    # Draw ears (behind body)
    # Left ear
    ear_left_x = center_x - int(body_radius * 0.7)
    ear_top_y = center_y - int(body_radius * 0.8)
    draw.polygon([
        (ear_left_x, ear_top_y),
        (ear_left_x - ear_size, center_y - body_radius + ear_size),
        (ear_left_x + ear_size, center_y - body_radius + ear_size)
    ], fill=body_color)

    # Right ear
    ear_right_x = center_x + int(body_radius * 0.7)
    draw.polygon([
        (ear_right_x, ear_top_y),
        (ear_right_x - ear_size, center_y - body_radius + ear_size),
        (ear_right_x + ear_size, center_y - body_radius + ear_size)
    ], fill=body_color)

    # Draw body (circle)
    draw.ellipse([
        center_x - body_radius,
        center_y - body_radius,
        center_x + body_radius,
        center_y + body_radius
    ], fill=body_color)

    # Draw highlight (smaller ellipse offset up-left)
    highlight_offset = int(size * 0.05)
    highlight_radius = int(body_radius * 0.7)
    draw.ellipse([
        center_x - highlight_radius - highlight_offset,
        center_y - highlight_radius - highlight_offset,
        center_x + highlight_radius - highlight_offset,
        center_y + highlight_radius - highlight_offset
    ], fill=highlight)

    # Blend the highlight by drawing the body color again with transparency
    # (Simple approach - draw a semi-transparent body on top)

    # Draw eyes
    eye_offset_x = int(size * 0.15)
    eye_offset_y = int(size * 0.05)

    # Left eye
    draw.ellipse([
        center_x - eye_offset_x - eye_size,
        center_y - eye_offset_y - eye_size,
        center_x - eye_offset_x + eye_size,
        center_y - eye_offset_y + eye_size
    ], fill=eye_color)

    # Right eye
    draw.ellipse([
        center_x + eye_offset_x - eye_size,
        center_y - eye_offset_y - eye_size,
        center_x + eye_offset_x + eye_size,
        center_y - eye_offset_y + eye_size
    ], fill=eye_color)

    # Eye highlights (small white circles)
    eye_highlight_size = int(eye_size * 0.4)
    highlight_color = (255, 255, 255)

    draw.ellipse([
        center_x - eye_offset_x - eye_highlight_size,
        center_y - eye_offset_y - eye_size + eye_highlight_size,
        center_x - eye_offset_x + eye_highlight_size,
        center_y - eye_offset_y - eye_size + eye_highlight_size * 3
    ], fill=highlight_color)

    draw.ellipse([
        center_x + eye_offset_x - eye_highlight_size,
        center_y - eye_offset_y - eye_size + eye_highlight_size,
        center_x + eye_offset_x + eye_highlight_size,
        center_y - eye_offset_y - eye_size + eye_highlight_size * 3
    ], fill=highlight_color)

    # Draw nose
    nose_y = center_y + int(size * 0.08)
    draw.ellipse([
        center_x - nose_size,
        nose_y - nose_size // 2,
        center_x + nose_size,
        nose_y + nose_size // 2
    ], fill=nose_color)

    # Draw smile (arc)
    smile_width = int(size * 0.15)
    smile_y = nose_y + int(size * 0.05)
    draw.arc([
        center_x - smile_width,
        smile_y - smile_width // 2,
        center_x + smile_width,
        smile_y + smile_width
    ], start=0, end=180, fill=eye_color, width=max(2, size // 64))

    return img


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

    # Save as .ico with multiple sizes
    # The first image is the main one, save with append_images for multi-resolution
    icons[0].save(
        output_path,
        format='ICO',
        append_images=icons[1:],
        sizes=[(s, s) for s in sizes]
    )

    print(f"Icon saved to: {output_path}")

    # Also save a PNG version for other uses
    png_path = output_path.replace('.ico', '.png')
    icons[-1].save(png_path, format='PNG')
    print(f"PNG version saved to: {png_path}")


def main():
    """Generate the application icons."""
    print("Generating Desktop Pet icons...")
    print()

    generate_ico_file('assets/icon.ico')

    print()
    print("Done! Icons have been generated in the assets folder.")


if __name__ == '__main__':
    main()
