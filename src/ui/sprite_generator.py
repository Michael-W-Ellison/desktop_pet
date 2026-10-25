"""
Sprite generation for creatures, eggs, and items.

Sprites are pixel art from creature_art, drawn on a small grid (64x64 for a
full-grown pet) and scaled up with nearest-neighbour resampling so pixels stay
crisp. Each evolution stage is drawn on its own grid (a Baby on 32x32) rather
than shrinking a larger picture, so every stage has the same pixel size.
Pictures are cached per species, palette and grid.
"""
from functools import lru_cache
from PIL import Image
from typing import List, Optional, Tuple

from core.config import COLOR_PALETTES
from ui import creature_art


# Pixels of the full-grown creature grid; the window shows each pixel as a square block
CREATURE_GRID = 64


def _pixel_scale(size: Tuple[int, int], grid: int) -> int:
    return max(1, min(size) // grid)


# Animation frames, by animation (keys of creature_art.FRAMES)
ANIMATIONS = {
    'idle': ['idle_0', 'idle_1'],
    'blink': ['blink'],
    'walk': ['walk_0', 'walk_1', 'walk_2', 'walk_3'],
    'sleep': ['sleep_0', 'sleep_1'],
    'wobble': ['wobble_l', 'idle_0', 'wobble_r', 'idle_0'],
}


@lru_cache(maxsize=256)
def _creature_picture(creature_type: str, colors: Tuple[str, ...], grid: int, frame: str) -> Image.Image:
    palette = list(colors)
    index = COLOR_PALETTES.index(palette) if palette in COLOR_PALETTES else None
    return creature_art.render_creature(creature_type, palette, grid, index, frame)


@lru_cache(maxsize=32)
def _item_picture(name: str, size: Tuple[int, int], frame: str = 'idle_0') -> Image.Image:
    # Items use the same pixel size as creatures where the size allows (3x), else 2x
    scale = 3 if min(size) >= 96 else 2 if min(size) >= 48 else 1
    grid = max(8, min(size) // scale)
    return creature_art.render_item(name, grid, frame).resize(size, Image.Resampling.NEAREST)


class SpriteGenerator:
    """Generates sprites for creatures and items."""

    @staticmethod
    def generate_creature_sprite(creature_type: str, color_palette: List[str],
                                 size: Tuple[int, int] = (128, 128),
                                 facing_right: bool = True,
                                 stage_multiplier: float = 1.0,
                                 variant_colors: Optional[List[str]] = None,
                                 frame: str = 'idle_0') -> Image.Image:
        """
        Picture of a creature.

        Args:
            creature_type: Species (e.g., 'dragon', 'phoenix', 'sprite')
            color_palette: Palette colour hex codes
            size: Size of the full-grown picture (width, height)
            facing_right: Whether the creature is facing right
            stage_multiplier: Size multiplier for the evolution stage; the creature is
                drawn on a grid this much smaller, so the image is about size scaled by this
            variant_colors: Optional colours in place of the palette
            frame: Animation frame (see ANIMATIONS)

        Returns:
            PIL Image of the creature
        """
        colors = tuple(variant_colors if variant_colors else color_palette)
        scale = _pixel_scale(size, CREATURE_GRID)
        grid = max(8, int(round(CREATURE_GRID * stage_multiplier)))
        img = _creature_picture(creature_type, colors, grid, frame)
        if not facing_right:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        return img.resize((grid * scale, grid * scale), Image.Resampling.NEAREST)

    @staticmethod
    def generate_egg_sprite(size: Tuple[int, int] = (128, 128), frame: str = 'idle_0') -> Image.Image:
        """Generate an egg sprite (frame: 'idle_0', or 'wobble_l'/'wobble_r' while it rocks)."""
        return _item_picture('egg', tuple(size), frame).copy()

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
