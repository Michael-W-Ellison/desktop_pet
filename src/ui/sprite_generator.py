"""
Sprite generation for creatures, eggs, and items.

Creatures and items are shaded illustrations from creature_art: creatures have
one design per species, rendered once per species and palette and cached, with
facing and evolution-stage size applied to the cached picture.
"""
from functools import lru_cache
from PIL import Image
from typing import List, Optional, Tuple

from core.config import COLOR_PALETTES
from ui import creature_art


@lru_cache(maxsize=32)
def _creature_picture(creature_type: str, colors: Tuple[str, ...], size: Tuple[int, int]) -> Image.Image:
    palette = list(colors)
    index = COLOR_PALETTES.index(palette) if palette in COLOR_PALETTES else None
    return creature_art.render_creature(creature_type, palette, min(size), index).resize(size)


@lru_cache(maxsize=16)
def _item_picture(name: str, size: Tuple[int, int]) -> Image.Image:
    return creature_art.render_item(name, min(size)).resize(size)


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
        return _item_picture('egg', tuple(size)).copy()

    @staticmethod
    def generate_shelter_sprite(size: Tuple[int, int] = (128, 128)) -> Image.Image:
        """Generate a shelter/house sprite."""
        return _item_picture('shelter', tuple(size)).copy()

    @staticmethod
    def generate_ball_sprite(size: Tuple[int, int] = (64, 64)) -> Image.Image:
        """Generate a ball toy sprite."""
        return _item_picture('ball', tuple(size)).copy()

    @staticmethod
    def generate_food_sprite(size: Tuple[int, int] = (64, 64)) -> Image.Image:
        """Generate a food bowl sprite."""
        return _item_picture('food', tuple(size)).copy()
