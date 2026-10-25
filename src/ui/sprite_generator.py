"""
Sprite generation for creatures, eggs, and items.

Creatures are shaded illustrations from creature_art, one design per species,
rendered once per species and palette and cached; facing and evolution-stage
size are applied to the cached picture.
"""
from functools import lru_cache
from PIL import Image, ImageDraw
from typing import List, Tuple, Optional

from core.config import COLOR_PALETTES
from ui import creature_art


@lru_cache(maxsize=32)
def _creature_picture(creature_type: str, colors: Tuple[str, ...], size: Tuple[int, int]) -> Image.Image:
    palette = list(colors)
    index = COLOR_PALETTES.index(palette) if palette in COLOR_PALETTES else None
    return creature_art.render_creature(creature_type, palette, min(size), index).resize(size)


@lru_cache(maxsize=4)
def _egg_picture(size: Tuple[int, int]) -> Image.Image:
    return creature_art.render_egg(min(size)).resize(size)


class SpriteGenerator:
    """Generates sprites for creatures and items."""

    @staticmethod
    def generate_creature_sprite(creature_type: str, color_palette: List[str],
                                 size: Tuple[int, int] = (128, 128),
                                 facing_right: bool = True,
                                 stage_multiplier: float = 1.0,
                                 variant_colors: Optional[List[str]] = None) -> Image.Image:
        """
        Picture of a creature.

        Args:
            creature_type: Species (e.g., 'dragon', 'phoenix', 'sprite')
            color_palette: Palette colour hex codes
            size: Size of the full-grown picture (width, height)
            facing_right: Whether the creature is facing right
            stage_multiplier: Size multiplier for the evolution stage; the returned
                image is size scaled by this
            variant_colors: Optional colours in place of the palette

        Returns:
            PIL Image of the creature
        """
        colors = tuple(variant_colors if variant_colors else color_palette)
        img = _creature_picture(creature_type, colors, tuple(size))
        if not facing_right:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        scaled_size = (max(1, int(size[0] * stage_multiplier)), max(1, int(size[1] * stage_multiplier)))
        if scaled_size != tuple(size):
            img = img.resize(scaled_size, Image.Resampling.LANCZOS)
        return img.copy()

    @staticmethod
    def generate_egg_sprite(size: Tuple[int, int] = (128, 128)) -> Image.Image:
        """Generate an egg sprite."""
        return _egg_picture(tuple(size)).copy()

    @staticmethod
    def generate_shelter_sprite(size: Tuple[int, int] = (128, 128)) -> Image.Image:
        """Generate a shelter/house sprite."""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = size[0] // 2, size[1] // 2

        # House base
        draw.rectangle([cx-40, cy-10, cx+40, cy+40], fill='#8B4513', outline='#654321', width=2)

        # Roof
        draw.polygon([(cx-45, cy-10), (cx, cy-45), (cx+45, cy-10)], fill='#CD5C5C', outline='#8B0000', width=2)

        # Door
        draw.rectangle([cx-12, cy+10, cx+12, cy+40], fill='#654321', outline='#4a3219', width=2)

        # Window
        draw.rectangle([cx-30, cy, cx-15, cy+15], fill='#87CEEB', outline='#4682B4', width=2)
        draw.rectangle([cx+15, cy, cx+30, cy+15], fill='#87CEEB', outline='#4682B4', width=2)

        # Window panes
        draw.line([(cx-22, cy), (cx-22, cy+15)], fill='#4682B4', width=1)
        draw.line([(cx-30, cy+7), (cx-15, cy+7)], fill='#4682B4', width=1)
        draw.line([(cx+22, cy), (cx+22, cy+15)], fill='#4682B4', width=1)
        draw.line([(cx+15, cy+7), (cx+30, cy+7)], fill='#4682B4', width=1)

        return img

    @staticmethod
    def generate_ball_sprite(size: Tuple[int, int] = (64, 64)) -> Image.Image:
        """Generate a ball toy sprite."""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = size[0] // 2, size[1] // 2
        radius = 25

        # Ball
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                     fill='#FF6B6B', outline='#C92A2A', width=2)

        # Pattern (stripes)
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 45, 135, fill='white', width=8)
        draw.arc([cx-radius, cy-radius, cx+radius, cy+radius], 225, 315, fill='white', width=8)

        # Highlight
        draw.ellipse([cx-15, cy-15, cx-5, cy-5], fill='white', outline=None)

        return img

    @staticmethod
    def generate_food_sprite(size: Tuple[int, int] = (64, 64)) -> Image.Image:
        """Generate a food bowl sprite."""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = size[0] // 2, size[1] // 2

        # Bowl
        draw.arc([cx-25, cy-10, cx+25, cy+30], 0, 180, fill='#FFB6C1', width=8)
        draw.line([(cx-25, cy+10), (cx+25, cy+10)], fill='#FFB6C1', width=8)

        # Food (little mound)
        draw.ellipse([cx-15, cy-5, cx+15, cy+15], fill='#8B4513', outline='#654321', width=1)

        return img
