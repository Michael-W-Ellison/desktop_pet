"""
Helpers for converting PIL images to Qt image types.

PIL.ImageQt dropped PyQt5 support in Pillow 10, so the conversion is done here
directly from raw RGBA bytes.
"""
from PIL import Image
from PyQt5.QtGui import QImage


def pil_to_qimage(image: Image.Image) -> QImage:
    """Convert a PIL Image to a QImage that owns its own pixel data."""
    rgba = image.convert('RGBA')
    data = rgba.tobytes('raw', 'RGBA')
    qimage = QImage(data, rgba.width, rgba.height, rgba.width * 4, QImage.Format_RGBA8888)
    # copy() detaches the QImage from the Python bytes buffer
    return qimage.copy()
