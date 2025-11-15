"""
Procedural sprite generation for creatures, eggs, and items.

Phase 4 Enhanced:
- Supports 25+ creature species
- Evolution stage scaling (baby/juvenile/adult/elder)
- Variant color modifications (shiny, mystic, shadow, crystal)
"""
from PIL import Image, ImageDraw, ImageEnhance
import random
from typing import List, Tuple, Optional


class SpriteGenerator:
    """Generates procedural sprites for creatures and items."""

    @staticmethod
    def generate_creature_sprite(creature_type: str, color_palette: List[str],
                                   size: Tuple[int, int] = (128, 128),
                                   facing_right: bool = True,
                                   stage_multiplier: float = 1.0,
                                   variant_colors: Optional[List[str]] = None) -> Image.Image:
        """
        Generate a procedural sprite for a creature (Phase 4 enhanced).

        Args:
            creature_type: Type of creature (e.g., 'dragon', 'phoenix', 'sprite')
            color_palette: List of color hex codes
            size: Size of the sprite (width, height)
            facing_right: Whether the creature is facing right
            stage_multiplier: Size multiplier for evolution stage (0.6-1.2)
            variant_colors: Optional color overrides for variants

        Returns:
            PIL Image of the creature
        """
        # Use variant colors if provided
        colors = variant_colors if variant_colors else color_palette

        # Scale size based on evolution stage
        scaled_size = (int(size[0] * stage_multiplier), int(size[1] * stage_multiplier))

        img = Image.new('RGBA', scaled_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        center_x, center_y = scaled_size[0] // 2, scaled_size[1] // 2
        primary_color = colors[0]
        secondary_color = colors[1] if len(colors) > 1 else colors[0]
        accent_color = colors[2] if len(colors) > 2 else primary_color

        # Dictionary mapping creature types to drawing functions
        creature_drawers = {
            'dragon': SpriteGenerator._draw_dragon,
            'cat': SpriteGenerator._draw_cat,
            'dog': SpriteGenerator._draw_dog,
            'bunny': SpriteGenerator._draw_bunny,
            'bird': SpriteGenerator._draw_bird,
            'fox': SpriteGenerator._draw_fox,
            'hamster': SpriteGenerator._draw_generic,
            'owl': SpriteGenerator._draw_bird,
            'penguin': SpriteGenerator._draw_bird,
            'turtle': SpriteGenerator._draw_generic,
            # Phase 4: Fantastical creatures
            'phoenix': SpriteGenerator._draw_phoenix,
            'sprite': SpriteGenerator._draw_sprite,
            'golem': SpriteGenerator._draw_golem,
            'griffin': SpriteGenerator._draw_griffin,
            'unicorn': SpriteGenerator._draw_unicorn,
            'chimera': SpriteGenerator._draw_dragon,  # Similar to dragon
            'wisp': SpriteGenerator._draw_wisp,
            'kraken': SpriteGenerator._draw_generic,
            'hydra': SpriteGenerator._draw_dragon,  # Similar to dragon
            'basilisk': SpriteGenerator._draw_generic,
            'manticore': SpriteGenerator._draw_generic,
            'salamander': SpriteGenerator._draw_generic,
            'sylph': SpriteGenerator._draw_sprite,  # Similar to sprite
            'undine': SpriteGenerator._draw_sprite,  # Similar to sprite
            'gnome': SpriteGenerator._draw_generic
        }

        # Get drawer function or default to generic
        drawer = creature_drawers.get(creature_type, SpriteGenerator._draw_generic)
        drawer(draw, center_x, center_y, primary_color, secondary_color, accent_color, facing_right)

        # Flip if facing left
        if not facing_right:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

        # Resize back to target size if needed
        if scaled_size != size:
            # Resize with high-quality resampling
            img = img.resize(size, Image.Resampling.LANCZOS)

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

    # ========== Phase 4: Fantastical Creature Sprites ==========

    @staticmethod
    def _draw_phoenix(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a phoenix (majestic fire bird)."""
        # Body (elegant bird shape)
        draw.ellipse([cx-25, cy-15, cx+25, cy+20], fill=primary, outline=accent, width=2)
        # Head with crest
        draw.ellipse([cx+10, cy-25, cx+40, cy+5], fill=primary, outline=accent, width=2)
        # Flame crest
        draw.polygon([(cx+20, cy-25), (cx+18, cy-40), (cx+25, cy-30)], fill='#FF4500')
        draw.polygon([(cx+25, cy-25), (cx+23, cy-42), (cx+32, cy-30)], fill='#FFD700')
        draw.polygon([(cx+30, cy-25), (cx+28, cy-38), (cx+37, cy-30)], fill='#FF4500')
        # Large wings
        draw.ellipse([cx-35, cy-10, cx-5, cy+20], fill=secondary, outline=accent, width=2)
        draw.ellipse([cx-45, cy-5, cx-25, cy+25], fill='#FFD700', outline=accent, width=1)
        # Tail feathers (flame-like)
        points = [(cx-25, cy+10), (cx-50, cy+5), (cx-55, cy+25), (cx-25, cy+18)]
        draw.polygon(points, fill='#FF4500', outline=accent)
        points = [(cx-25, cy+14), (cx-45, cy+18), (cx-50, cy+30), (cx-25, cy+20)]
        draw.polygon(points, fill='#FFD700', outline=accent)
        # Eyes (fierce)
        draw.ellipse([cx+20, cy-15, cx+26, cy-9], fill='#FFD700')
        draw.ellipse([cx+22, cy-13, cx+24, cy-11], fill='#FF4500')

    @staticmethod
    def _draw_sprite(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a magical sprite/fairy."""
        # Small body
        draw.ellipse([cx-15, cy-5, cx+15, cy+20], fill=primary, outline=accent, width=2)
        # Head
        draw.ellipse([cx-5, cy-20, cx+20, cy+5], fill=primary, outline=accent, width=2)
        # Wings (butterfly-like)
        draw.ellipse([cx-30, cy-10, cx-10, cy+10], fill=secondary, outline=accent, width=2)
        draw.ellipse([cx-25, cy+5, cx-5, cy+22], fill=secondary, outline=accent, width=1)
        # Wing patterns
        draw.ellipse([cx-23, cy-5, cx-17, cy+1], fill='white')
        draw.ellipse([cx-20, cy+10, cx-14, cy+16], fill='white')
        # Antenna
        draw.line([(cx+5, cy-20), (cx+2, cy-30)], fill=accent, width=2)
        draw.ellipse([cx, cy-33, cx+4, cy-29], fill='#FFD700')
        draw.line([(cx+12, cy-20), (cx+15, cy-30)], fill=accent, width=2)
        draw.ellipse([cx+13, cy-33, cx+17, cy-29], fill='#FFD700')
        # Eyes (large and magical)
        draw.ellipse([cx+2, cy-10, cx+8, cy-4], fill='#E0BBE4')
        draw.ellipse([cx+3, cy-9, cx+7, cy-5], fill='black')
        draw.ellipse([cx+10, cy-10, cx+16, cy-4], fill='#E0BBE4')
        draw.ellipse([cx+11, cy-9, cx+15, cy-5], fill='black')

    @staticmethod
    def _draw_golem(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a stone/earth golem."""
        # Blocky body
        draw.rectangle([cx-28, cy-8, cx+28, cy+25], fill=primary, outline=accent, width=3)
        # Head (blocky)
        draw.rectangle([cx-20, cy-28, cx+20, cy-8], fill=primary, outline=accent, width=3)
        # Rock texture (cracks)
        draw.line([(cx-15, cy-25), (cx-10, cy-15)], fill=accent, width=2)
        draw.line([(cx+10, cy-20), (cx+15, cy-10)], fill=accent, width=2)
        draw.line([(cx-20, cy), (cx-10, cy+10)], fill=accent, width=2)
        draw.line([(cx+15, cy+5), (cx+25, cy+15)], fill=accent, width=2)
        # Glowing eyes
        draw.rectangle([cx-12, cy-20, cx-6, cy-14], fill='#FFD700')
        draw.rectangle([cx+6, cy-20, cx+12, cy-14], fill='#FFD700')
        # Arms (thick)
        draw.rectangle([cx-35, cy, cx-28, cy+20], fill=secondary, outline=accent, width=2)
        # Gem in chest
        draw.polygon([(cx-5, cy+5), (cx, cy), (cx+5, cy+5), (cx, cy+10)], fill='#00BFFF')

    @staticmethod
    def _draw_griffin(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a griffin (lion-eagle hybrid)."""
        # Lion body
        draw.ellipse([cx-30, cy-5, cx+20, cy+20], fill=secondary, outline=accent, width=2)
        # Eagle head
        draw.ellipse([cx+8, cy-20, cx+38, cy+10], fill=primary, outline=accent, width=2)
        # Beak
        draw.polygon([(cx+38, cy-8), (cx+48, cy-5), (cx+38, cy-2)], fill='#FFD700')
        # Eagle wings
        draw.ellipse([cx-35, cy-8, cx-10, cy+15], fill=primary, outline=accent, width=2)
        draw.polygon([(cx-35, cy), (cx-50, cy-10), (cx-45, cy+10)], fill=primary, outline=accent)
        # Feathered tail
        draw.polygon([(cx-30, cy+10), (cx-45, cy+8), (cx-40, cy+22)], fill=secondary, outline=accent)
        # Eyes (fierce eagle eyes)
        draw.ellipse([cx+18, cy-10, cx+24, cy-4], fill='#FFD700')
        draw.ellipse([cx+20, cy-8, cx+22, cy-6], fill='black')
        # Ears/feather tufts
        draw.polygon([(cx+15, cy-20), (cx+12, cy-30), (cx+18, cy-22)], fill=primary, outline=accent)
        draw.polygon([(cx+28, cy-20), (cx+25, cy-30), (cx+31, cy-22)], fill=primary, outline=accent)

    @staticmethod
    def _draw_unicorn(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a magical unicorn."""
        # Horse body
        draw.ellipse([cx-30, cy-8, cx+20, cy+20], fill=primary, outline=accent, width=2)
        # Horse head/neck
        draw.ellipse([cx+5, cy-20, cx+35, cy+10], fill=primary, outline=accent, width=2)
        # Mane (flowing)
        draw.ellipse([cx+8, cy-25, cx+20, cy-10], fill=secondary, outline=accent, width=1)
        draw.ellipse([cx+5, cy-18, cx+15, cy-5], fill=secondary)
        draw.ellipse([cx-5, cy-10, cx+5, cy+5], fill=secondary)
        # Magical horn
        draw.polygon([(cx+22, cy-20), (cx+20, cy-40), (cx+24, cy-20)], fill='#FFD700', outline=accent, width=2)
        # Spiral on horn
        draw.line([(cx+21, cy-35), (cx+23, cy-30)], fill='white', width=1)
        draw.line([(cx+21, cy-30), (cx+23, cy-25)], fill='white', width=1)
        # Ears
        draw.polygon([(cx+20, cy-20), (cx+18, cy-27), (cx+23, cy-22)], fill=primary, outline=accent)
        # Eyes (gentle)
        draw.ellipse([cx+18, cy-10, cx+23, cy-5], fill='white')
        draw.ellipse([cx+19, cy-9, cx+22, cy-6], fill='#8B008B')  # Purple eye
        # Tail (flowing)
        draw.arc([cx-40, cy, cx-15, cy+30], 180, 90, fill=secondary, width=6)
        # Hooves
        draw.rectangle([cx+10, cy+20, cx+15, cy+28], fill=accent)

    @staticmethod
    def _draw_wisp(draw, cx, cy, primary, secondary, accent, facing_right):
        """Draw a floating wisp/spirit orb."""
        # Main orb (glowing)
        draw.ellipse([cx-25, cy-25, cx+25, cy+25], fill=primary, outline=accent, width=2)
        # Inner glow
        draw.ellipse([cx-18, cy-18, cx+18, cy+18], fill=secondary)
        draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill='white')
        # Energy trails
        trail1 = [(cx-15, cy+20), (cx-25, cy+35), (cx-20, cy+40)]
        draw.line(trail1, fill=secondary, width=4)
        trail2 = [(cx+15, cy+20), (cx+25, cy+35), (cx+20, cy+40)]
        draw.line(trail2, fill=secondary, width=4)
        trail3 = [(cx, cy+22), (cx-5, cy+38), (cx, cy+45)]
        draw.line(trail3, fill=primary, width=3)
        # Energy wisps around it
        draw.ellipse([cx-35, cy-10, cx-28, cy-3], fill=secondary)
        draw.ellipse([cx+28, cy-15, cx+35, cy-8], fill=secondary)
        draw.ellipse([cx-5, cy-35, cx+2, cy-28], fill=primary)
        # Simple face (optional, mystical eyes)
        draw.ellipse([cx-8, cy-5, cx-3, cy], fill='#FFD700')
        draw.ellipse([cx+3, cy-5, cx+8, cy], fill='#FFD700')

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
