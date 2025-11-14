"""
Procedural sprite generation for creatures, eggs, and items.
"""
from PIL import Image, ImageDraw
import random
from typing import List, Tuple


class SpriteGenerator:
    """Generates procedural sprites for creatures and items."""

    @staticmethod
    def generate_creature_sprite(creature_type: str, color_palette: List[str],
                                   size: Tuple[int, int] = (128, 128),
                                   facing_right: bool = True) -> Image.Image:
        """
        Generate a procedural sprite for a creature.

        Args:
            creature_type: Type of creature (e.g., 'dragon', 'cat')
            color_palette: List of color hex codes
            size: Size of the sprite (width, height)
            facing_right: Whether the creature is facing right

        Returns:
            PIL Image of the creature
        """
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        center_x, center_y = size[0] // 2, size[1] // 2
        primary_color = color_palette[0]
        secondary_color = color_palette[1] if len(color_palette) > 1 else color_palette[0]
        accent_color = color_palette[2] if len(color_palette) > 2 else primary_color

        # Generate different shapes based on creature type
        if creature_type == 'dragon':
            SpriteGenerator._draw_dragon(draw, center_x, center_y, primary_color,
                                         secondary_color, accent_color, facing_right)
        elif creature_type == 'cat':
            SpriteGenerator._draw_cat(draw, center_x, center_y, primary_color,
                                      secondary_color, accent_color, facing_right)
        elif creature_type == 'dog':
            SpriteGenerator._draw_dog(draw, center_x, center_y, primary_color,
                                      secondary_color, accent_color, facing_right)
        elif creature_type == 'bunny':
            SpriteGenerator._draw_bunny(draw, center_x, center_y, primary_color,
                                        secondary_color, accent_color, facing_right)
        elif creature_type == 'bird':
            SpriteGenerator._draw_bird(draw, center_x, center_y, primary_color,
                                       secondary_color, accent_color, facing_right)
        elif creature_type == 'fox':
            SpriteGenerator._draw_fox(draw, center_x, center_y, primary_color,
                                      secondary_color, accent_color, facing_right)
        else:
            # Default generic creature
            SpriteGenerator._draw_generic(draw, center_x, center_y, primary_color,
                                          secondary_color, accent_color, facing_right)

        # Flip if facing left
        if not facing_right:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

        return img

    @staticmethod
    def _draw_dragon(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a dragon-like creature."""
        # Body
        draw.ellipse([cx-30, cy-15, cx+30, cy+25], fill=primary, outline=accent, width=2)
        # Head
        draw.ellipse([cx+15, cy-25, cx+45, cy+5], fill=primary, outline=accent, width=2)
        # Wings
        draw.ellipse([cx-35, cy-10, cx-15, cy+15], fill=secondary, outline=accent, width=1)
        # Tail
        points = [(cx-30, cy+10), (cx-50, cy+5), (cx-55, cy+20)]
        draw.polygon(points, fill=secondary, outline=accent)
        # Eyes
        draw.ellipse([cx+25, cy-15, cx+30, cy-10], fill='white')
        draw.ellipse([cx+26, cy-14, cx+29, cy-11], fill='black')
        # Horns
        draw.polygon([(cx+35, cy-25), (cx+38, cy-35), (cx+40, cy-25)], fill=accent)

    @staticmethod
    def _draw_cat(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a cat-like creature."""
        # Body
        draw.ellipse([cx-25, cy-10, cx+25, cy+20], fill=primary, outline=accent, width=2)
        # Head
        draw.ellipse([cx+10, cy-20, cx+40, cy+10], fill=primary, outline=accent, width=2)
        # Ears
        draw.polygon([(cx+15, cy-20), (cx+12, cy-35), (cx+22, cy-20)], fill=primary, outline=accent)
        draw.polygon([(cx+30, cy-20), (cx+27, cy-35), (cx+37, cy-20)], fill=primary, outline=accent)
        # Tail
        draw.arc([cx-40, cy+5, cx-10, cy+35], 0, 180, fill=primary, width=5)
        # Eyes
        draw.ellipse([cx+18, cy-10, cx+23, cy-5], fill='yellow')
        draw.ellipse([cx+19, cy-9, cx+22, cy-6], fill='black')
        draw.ellipse([cx+28, cy-10, cx+33, cy-5], fill='yellow')
        draw.ellipse([cx+29, cy-9, cx+32, cy-6], fill='black')
        # Whiskers
        draw.line([(cx+15, cy), (cx+5, cy-2)], fill=accent, width=1)
        draw.line([(cx+15, cy+3), (cx+5, cy+5)], fill=accent, width=1)

    @staticmethod
    def _draw_dog(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a dog-like creature."""
        # Body
        draw.ellipse([cx-30, cy-10, cx+20, cy+20], fill=primary, outline=accent, width=2)
        # Head
        draw.ellipse([cx+5, cy-15, cx+35, cy+15], fill=primary, outline=accent, width=2)
        # Ears (floppy)
        draw.ellipse([cx+5, cy-10, cx+15, cy+10], fill=secondary, outline=accent, width=1)
        draw.ellipse([cx+25, cy-10, cx+35, cy+10], fill=secondary, outline=accent, width=1)
        # Tail (wagging up)
        draw.arc([cx-40, cy-20, cx-20, cy], 180, 90, fill=primary, width=6)
        # Eyes
        draw.ellipse([cx+13, cy-5, cx+17, cy-1], fill='brown')
        draw.ellipse([cx+23, cy-5, cx+27, cy-1], fill='brown')
        # Nose
        draw.ellipse([cx+18, cy+5, cx+22, cy+9], fill='black')

    @staticmethod
    def _draw_bunny(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a bunny-like creature."""
        # Body
        draw.ellipse([cx-25, cy-5, cx+25, cy+25], fill=primary, outline=accent, width=2)
        # Head
        draw.ellipse([cx+5, cy-20, cx+35, cy+10], fill=primary, outline=accent, width=2)
        # Long ears
        draw.ellipse([cx+10, cy-50, cx+18, cy-15], fill=primary, outline=accent, width=2)
        draw.ellipse([cx+12, cy-48, cx+16, cy-20], fill=secondary)
        draw.ellipse([cx+22, cy-50, cx+30, cy-15], fill=primary, outline=accent, width=2)
        draw.ellipse([cx+24, cy-48, cx+28, cy-20], fill=secondary)
        # Eyes
        draw.ellipse([cx+15, cy-10, cx+19, cy-6], fill='black')
        draw.ellipse([cx+25, cy-10, cx+29, cy-6], fill='black')
        # Nose
        draw.ellipse([cx+19, cy-2, cx+23, cy+2], fill='pink')
        # Fluffy tail
        draw.ellipse([cx-30, cy+15, cx-15, cy+30], fill='white', outline=accent)

    @staticmethod
    def _draw_bird(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a bird-like creature."""
        # Body
        draw.ellipse([cx-20, cy-10, cx+20, cy+20], fill=primary, outline=accent, width=2)
        # Head
        draw.ellipse([cx+10, cy-20, cx+35, cy+5], fill=primary, outline=accent, width=2)
        # Beak
        draw.polygon([(cx+35, cy-10), (cx+45, cy-8), (cx+35, cy-6)], fill='orange')
        # Wings
        draw.ellipse([cx-25, cy-5, cx-5, cy+15], fill=secondary, outline=accent, width=2)
        # Tail feathers
        draw.polygon([(cx-20, cy+10), (cx-35, cy+8), (cx-30, cy+20), (cx-20, cy+15)],
                     fill=secondary, outline=accent)
        # Eyes
        draw.ellipse([cx+20, cy-12, cx+25, cy-7], fill='white')
        draw.ellipse([cx+21, cy-11, cx+24, cy-8], fill='black')
        # Feet
        draw.line([(cx-5, cy+20), (cx-5, cy+28)], fill='orange', width=2)
        draw.line([(cx+5, cy+20), (cx+5, cy+28)], fill='orange', width=2)

    @staticmethod
    def _draw_fox(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a fox-like creature."""
        # Body
        draw.ellipse([cx-28, cy-8, cx+22, cy+18], fill=primary, outline=accent, width=2)
        # Head
        draw.ellipse([cx+8, cy-18, cx+38, cy+12], fill=primary, outline=accent, width=2)
        # Ears (pointed)
        draw.polygon([(cx+12, cy-18), (cx+10, cy-32), (cx+20, cy-18)], fill=primary, outline=accent)
        draw.polygon([(cx+13, cy-17), (cx+12, cy-28), (cx+18, cy-18)], fill='white')
        draw.polygon([(cx+26, cy-18), (cx+24, cy-32), (cx+34, cy-18)], fill=primary, outline=accent)
        draw.polygon([(cx+27, cy-17), (cx+26, cy-28), (cx+32, cy-18)], fill='white')
        # Bushy tail
        draw.ellipse([cx-45, cy, cx-15, cy+30], fill=secondary, outline=accent, width=2)
        # Eyes
        draw.ellipse([cx+16, cy-8, cx+21, cy-3], fill='yellow')
        draw.ellipse([cx+17, cy-7, cx+20, cy-4], fill='black')
        draw.ellipse([cx+26, cy-8, cx+31, cy-3], fill='yellow')
        draw.ellipse([cx+27, cy-7, cx+30, cy-4], fill='black')
        # Nose
        draw.ellipse([cx+21, cy+2, cx+25, cy+6], fill='black')

    @staticmethod
    def _draw_generic(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a generic blob creature."""
        # Body (blob shape)
        draw.ellipse([cx-30, cy-15, cx+30, cy+25], fill=primary, outline=accent, width=2)
        # Eyes
        draw.ellipse([cx-10, cy-5, cx-2, cy+3], fill='white')
        draw.ellipse([cx-8, cy-3, cx-4, cy+1], fill='black')
        draw.ellipse([cx+2, cy-5, cx+10, cy+3], fill='white')
        draw.ellipse([cx+4, cy-3, cx+8, cy+1], fill='black')
        # Mouth
        draw.arc([cx-8, cy+5, cx+8, cy+15], 0, 180, fill='black', width=2)
        # Little antenna or ears
        draw.ellipse([cx-15, cy-20, cx-10, cy-15], fill=secondary)
        draw.ellipse([cx+10, cy-20, cx+15, cy-15], fill=secondary)

    @staticmethod
    def generate_egg_sprite(size: Tuple[int, int] = (128, 128)) -> Image.Image:
        """Generate an egg sprite."""
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = size[0] // 2, size[1] // 2

        # Egg shape (oval)
        draw.ellipse([cx-35, cy-45, cx+35, cy+35], fill='#F0E68C', outline='#DAA520', width=3)

        # Spots/pattern
        draw.ellipse([cx-15, cy-20, cx-5, cy-10], fill='#DAA520')
        draw.ellipse([cx+5, cy-15, cx+15, cy-5], fill='#DAA520')
        draw.ellipse([cx-10, cy+5, cx+5, cy+20], fill='#DAA520')

        # Highlight
        draw.ellipse([cx-20, cy-35, cx-10, cy-25], fill='white', outline=None)

        return img

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
