"""
Phase 14: Pet Customization System

Allows customization of pet appearance, colors, and accessories.
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class ColorPalette(Enum):
    """Available color palettes for pets."""
    NATURAL = "natural"          # Natural animal colors
    PASTEL = "pastel"            # Soft pastel colors
    VIBRANT = "vibrant"          # Bright, vivid colors
    MONOCHROME = "monochrome"    # Black/white/gray
    RAINBOW = "rainbow"          # Rainbow colors
    NEON = "neon"                # Neon/glowing colors
    EARTH = "earth"              # Earth tones
    OCEAN = "ocean"              # Blue/aqua tones
    SUNSET = "sunset"            # Orange/pink/purple
    GALAXY = "galaxy"            # Purple/blue/stars


class PetPattern(Enum):
    """Pet coat/fur patterns."""
    SOLID = "solid"              # Single solid color
    SPOTS = "spots"              # Spots (dalmatian-style)
    STRIPES = "stripes"          # Stripes (tiger/tabby)
    PATCHES = "patches"          # Color patches
    GRADIENT = "gradient"        # Color gradient
    TUXEDO = "tuxedo"           # Tuxedo pattern
    CALICO = "calico"           # Three-color patches
    MERLE = "merle"             # Mottled/marbled
    BRINDLE = "brindle"         # Streaked pattern
    BICOLOR = "bicolor"         # Two distinct colors


class AccessorySlot(Enum):
    """Slots where accessories can be equipped."""
    HEAD = "head"                # Hats, bows, headbands
    NECK = "neck"                # Collars, bandanas, necklaces
    BODY = "body"                # Shirts, jackets, capes
    FEET = "feet"                # Shoes, socks
    TAIL = "tail"                # Tail accessories
    FACE = "face"                # Glasses, masks
    BACK = "back"                # Wings, backpacks


class PetAccessory:
    """Represents a wearable accessory."""

    def __init__(self, accessory_id: str, name: str, slot: AccessorySlot,
                 description: str = ""):
        """
        Initialize accessory.

        Args:
            accessory_id: Unique accessory ID
            name: Accessory name
            slot: Equipment slot
            description: Accessory description
        """
        self.accessory_id = accessory_id
        self.name = name
        self.slot = slot
        self.description = description

        # Visual properties
        self.color: Optional[str] = None
        self.sparkle = False
        self.glow = False

        # Unlock requirements
        self.unlocked = True
        self.unlock_level = 1
        self.unlock_cost = 0

        # Metadata
        self.times_worn = 0
        self.favorite = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'accessory_id': self.accessory_id,
            'name': self.name,
            'slot': self.slot.value,
            'description': self.description,
            'color': self.color,
            'sparkle': self.sparkle,
            'glow': self.glow,
            'unlocked': self.unlocked,
            'unlock_level': self.unlock_level,
            'unlock_cost': self.unlock_cost,
            'times_worn': self.times_worn,
            'favorite': self.favorite
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PetAccessory':
        """Deserialize from dictionary."""
        accessory = cls(
            accessory_id=data['accessory_id'],
            name=data['name'],
            slot=AccessorySlot(data['slot']),
            description=data.get('description', '')
        )
        accessory.color = data.get('color')
        accessory.sparkle = data.get('sparkle', False)
        accessory.glow = data.get('glow', False)
        accessory.unlocked = data.get('unlocked', True)
        accessory.unlock_level = data.get('unlock_level', 1)
        accessory.unlock_cost = data.get('unlock_cost', 0)
        accessory.times_worn = data.get('times_worn', 0)
        accessory.favorite = data.get('favorite', False)
        return accessory


class PetCustomization:
    """
    Manages pet appearance customization.

    Features:
    - Body colors (primary, secondary, accent)
    - Fur/coat patterns
    - Eye color and style
    - Accessory equipment
    - Color palettes
    - Appearance presets
    """

    def __init__(self):
        """Initialize pet customization."""
        # Body colors (RGB tuples as strings for serialization)
        self.primary_color = "150,100,50"      # Main body color
        self.secondary_color = "200,150,100"   # Secondary markings
        self.accent_color = "255,200,150"      # Accent details
        self.eye_color = "50,100,200"          # Eye color

        # Patterns
        self.pattern = PetPattern.SOLID
        self.pattern_color = "100,50,25"       # Pattern overlay color
        self.pattern_opacity = 1.0             # 0-1

        # Physical features
        self.body_size = 1.0                   # Scale 0.5-2.0
        self.ear_style = "default"             # Ear shape
        self.tail_style = "default"            # Tail shape
        self.eye_style = "normal"              # Eye shape

        # Accessories (slot: accessory_id)
        self.equipped_accessories: Dict[AccessorySlot, str] = {}
        self.available_accessories: Dict[str, PetAccessory] = {}

        # Active palette
        self.active_palette = ColorPalette.NATURAL

        # Effects
        self.sparkle_effect = False
        self.glow_effect = False
        self.shadow_effect = True

        # Statistics
        self.customization_changes = 0
        self.total_accessories_worn = 0
        self.favorite_pattern = PetPattern.SOLID

        # Create default accessories
        self._create_default_accessories()

    def _create_default_accessories(self):
        """Create default available accessories."""
        accessories = [
            # Head
            ('hat_basic', 'Basic Hat', AccessorySlot.HEAD, 'Simple hat'),
            ('hat_party', 'Party Hat', AccessorySlot.HEAD, 'Festive party hat'),
            ('bow_ribbon', 'Ribbon Bow', AccessorySlot.HEAD, 'Cute ribbon bow'),
            ('crown', 'Crown', AccessorySlot.HEAD, 'Royal crown'),

            # Neck
            ('collar_basic', 'Basic Collar', AccessorySlot.NECK, 'Simple collar'),
            ('collar_bell', 'Bell Collar', AccessorySlot.NECK, 'Collar with bell'),
            ('bandana_red', 'Red Bandana', AccessorySlot.NECK, 'Red bandana'),
            ('scarf', 'Scarf', AccessorySlot.NECK, 'Warm scarf'),

            # Body
            ('shirt_plain', 'Plain Shirt', AccessorySlot.BODY, 'Simple shirt'),
            ('sweater', 'Sweater', AccessorySlot.BODY, 'Cozy sweater'),
            ('cape', 'Cape', AccessorySlot.BODY, 'Superhero cape'),

            # Face
            ('glasses_round', 'Round Glasses', AccessorySlot.FACE, 'Round glasses'),
            ('glasses_cool', 'Cool Glasses', AccessorySlot.FACE, 'Sunglasses'),
            ('mask_hero', 'Hero Mask', AccessorySlot.FACE, 'Superhero mask'),

            # Back
            ('wings_angel', 'Angel Wings', AccessorySlot.BACK, 'White angel wings'),
            ('wings_fairy', 'Fairy Wings', AccessorySlot.BACK, 'Magical fairy wings'),
            ('backpack', 'Backpack', AccessorySlot.BACK, 'Small backpack'),
        ]

        for acc_id, name, slot, desc in accessories:
            accessory = PetAccessory(acc_id, name, slot, desc)
            self.available_accessories[acc_id] = accessory

    def set_primary_color(self, r: int, g: int, b: int):
        """Set primary body color (RGB)."""
        self.primary_color = f"{r},{g},{b}"
        self.customization_changes += 1

    def set_secondary_color(self, r: int, g: int, b: int):
        """Set secondary color (RGB)."""
        self.secondary_color = f"{r},{g},{b}"
        self.customization_changes += 1

    def set_accent_color(self, r: int, g: int, b: int):
        """Set accent color (RGB)."""
        self.accent_color = f"{r},{g},{b}"
        self.customization_changes += 1

    def set_eye_color(self, r: int, g: int, b: int):
        """Set eye color (RGB)."""
        self.eye_color = f"{r},{g},{b}"
        self.customization_changes += 1

    def set_pattern(self, pattern: PetPattern):
        """Set fur/coat pattern."""
        self.pattern = pattern
        self.favorite_pattern = pattern
        self.customization_changes += 1

    def set_pattern_color(self, r: int, g: int, b: int):
        """Set pattern overlay color."""
        self.pattern_color = f"{r},{g},{b}"
        self.customization_changes += 1

    def apply_color_palette(self, palette: ColorPalette):
        """
        Apply a pre-defined color palette.

        Args:
            palette: Color palette to apply
        """
        self.active_palette = palette

        # Define palette colors
        palettes = {
            ColorPalette.NATURAL: {
                'primary': "150,100,50",
                'secondary': "200,150,100",
                'accent': "255,200,150",
                'eye': "50,100,200"
            },
            ColorPalette.PASTEL: {
                'primary': "255,200,220",
                'secondary': "200,220,255",
                'accent': "220,255,200",
                'eye': "150,180,255"
            },
            ColorPalette.VIBRANT: {
                'primary': "255,50,100",
                'secondary': "50,200,255",
                'accent': "255,200,50",
                'eye': "255,100,200"
            },
            ColorPalette.MONOCHROME: {
                'primary': "100,100,100",
                'secondary': "200,200,200",
                'accent': "255,255,255",
                'eye': "50,50,50"
            },
            ColorPalette.RAINBOW: {
                'primary': "255,100,100",
                'secondary': "100,255,100",
                'accent': "100,100,255",
                'eye': "255,200,255"
            },
            ColorPalette.NEON: {
                'primary': "0,255,200",
                'secondary': "255,0,255",
                'accent': "255,255,0",
                'eye': "0,255,255"
            },
            ColorPalette.EARTH: {
                'primary': "139,90,43",
                'secondary': "101,67,33",
                'accent': "205,133,63",
                'eye': "85,107,47"
            },
            ColorPalette.OCEAN: {
                'primary': "0,105,148",
                'secondary': "72,209,204",
                'accent': "135,206,250",
                'eye': "0,191,255"
            },
            ColorPalette.SUNSET: {
                'primary': "255,140,0",
                'secondary': "255,105,180",
                'accent': "186,85,211",
                'eye': "255,160,122"
            },
            ColorPalette.GALAXY: {
                'primary': "75,0,130",
                'secondary': "138,43,226",
                'accent': "147,112,219",
                'eye': "186,85,211"
            }
        }

        colors = palettes.get(palette)
        if colors:
            self.primary_color = colors['primary']
            self.secondary_color = colors['secondary']
            self.accent_color = colors['accent']
            self.eye_color = colors['eye']
            self.customization_changes += 1

    def equip_accessory(self, accessory_id: str) -> bool:
        """
        Equip an accessory.

        Args:
            accessory_id: Accessory to equip

        Returns:
            True if successful
        """
        accessory = self.available_accessories.get(accessory_id)
        if not accessory or not accessory.unlocked:
            return False

        # Unequip current accessory in slot
        if accessory.slot in self.equipped_accessories:
            old_id = self.equipped_accessories[accessory.slot]
            old_accessory = self.available_accessories.get(old_id)
            if old_accessory:
                old_accessory.times_worn += 1

        # Equip new accessory
        self.equipped_accessories[accessory.slot] = accessory_id
        accessory.times_worn += 1
        self.total_accessories_worn += 1
        self.customization_changes += 1

        return True

    def unequip_accessory(self, slot: AccessorySlot) -> bool:
        """Unequip accessory from slot."""
        if slot in self.equipped_accessories:
            del self.equipped_accessories[slot]
            self.customization_changes += 1
            return True
        return False

    def unequip_all_accessories(self):
        """Remove all accessories."""
        self.equipped_accessories.clear()
        self.customization_changes += 1

    def unlock_accessory(self, accessory_id: str) -> bool:
        """Unlock an accessory."""
        accessory = self.available_accessories.get(accessory_id)
        if not accessory:
            return False

        accessory.unlocked = True
        return True

    def get_equipped_accessories(self) -> List[PetAccessory]:
        """Get all currently equipped accessories."""
        return [
            self.available_accessories[acc_id]
            for acc_id in self.equipped_accessories.values()
            if acc_id in self.available_accessories
        ]

    def get_accessories_by_slot(self, slot: AccessorySlot) -> List[PetAccessory]:
        """Get all available accessories for a slot."""
        return [
            acc for acc in self.available_accessories.values()
            if acc.slot == slot
        ]

    def get_unlocked_accessories(self) -> List[PetAccessory]:
        """Get all unlocked accessories."""
        return [
            acc for acc in self.available_accessories.values()
            if acc.unlocked
        ]

    def set_body_size(self, size: float):
        """Set pet body size (0.5 - 2.0)."""
        self.body_size = max(0.5, min(2.0, size))
        self.customization_changes += 1

    def set_effects(self, sparkle: bool = False, glow: bool = False, shadow: bool = True):
        """Set visual effects."""
        self.sparkle_effect = sparkle
        self.glow_effect = glow
        self.shadow_effect = shadow
        self.customization_changes += 1

    def randomize_colors(self):
        """Randomize all colors."""
        import random
        palettes = list(ColorPalette)
        random_palette = random.choice(palettes)
        self.apply_color_palette(random_palette)

    def randomize_pattern(self):
        """Randomize pattern."""
        import random
        patterns = list(PetPattern)
        self.set_pattern(random.choice(patterns))

    def get_appearance_summary(self) -> Dict[str, Any]:
        """Get summary of current appearance."""
        return {
            'colors': {
                'primary': self.primary_color,
                'secondary': self.secondary_color,
                'accent': self.accent_color,
                'eye': self.eye_color
            },
            'pattern': self.pattern.value,
            'pattern_color': self.pattern_color,
            'palette': self.active_palette.value,
            'body_size': self.body_size,
            'effects': {
                'sparkle': self.sparkle_effect,
                'glow': self.glow_effect,
                'shadow': self.shadow_effect
            },
            'equipped_accessories': {
                slot.value: acc_id
                for slot, acc_id in self.equipped_accessories.items()
            },
            'num_accessories': len(self.equipped_accessories)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get customization statistics."""
        return {
            'customization_changes': self.customization_changes,
            'total_accessories_worn': self.total_accessories_worn,
            'accessories_equipped': len(self.equipped_accessories),
            'unlocked_accessories': len(self.get_unlocked_accessories()),
            'total_accessories': len(self.available_accessories),
            'favorite_pattern': self.favorite_pattern.value,
            'active_palette': self.active_palette.value
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'accent_color': self.accent_color,
            'eye_color': self.eye_color,
            'pattern': self.pattern.value,
            'pattern_color': self.pattern_color,
            'pattern_opacity': self.pattern_opacity,
            'body_size': self.body_size,
            'ear_style': self.ear_style,
            'tail_style': self.tail_style,
            'eye_style': self.eye_style,
            'equipped_accessories': {
                slot.value: acc_id
                for slot, acc_id in self.equipped_accessories.items()
            },
            'available_accessories': {
                acc_id: acc.to_dict()
                for acc_id, acc in self.available_accessories.items()
            },
            'active_palette': self.active_palette.value,
            'sparkle_effect': self.sparkle_effect,
            'glow_effect': self.glow_effect,
            'shadow_effect': self.shadow_effect,
            'customization_changes': self.customization_changes,
            'total_accessories_worn': self.total_accessories_worn,
            'favorite_pattern': self.favorite_pattern.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PetCustomization':
        """Deserialize from dictionary."""
        customization = cls()

        customization.primary_color = data.get('primary_color', "150,100,50")
        customization.secondary_color = data.get('secondary_color', "200,150,100")
        customization.accent_color = data.get('accent_color', "255,200,150")
        customization.eye_color = data.get('eye_color', "50,100,200")
        customization.pattern = PetPattern(data.get('pattern', 'solid'))
        customization.pattern_color = data.get('pattern_color', "100,50,25")
        customization.pattern_opacity = data.get('pattern_opacity', 1.0)
        customization.body_size = data.get('body_size', 1.0)
        customization.ear_style = data.get('ear_style', 'default')
        customization.tail_style = data.get('tail_style', 'default')
        customization.eye_style = data.get('eye_style', 'normal')

        # Restore equipped accessories
        equipped_data = data.get('equipped_accessories', {})
        customization.equipped_accessories = {
            AccessorySlot(slot): acc_id
            for slot, acc_id in equipped_data.items()
        }

        # Restore available accessories
        accessories_data = data.get('available_accessories', {})
        for acc_id, acc_data in accessories_data.items():
            customization.available_accessories[acc_id] = PetAccessory.from_dict(acc_data)

        customization.active_palette = ColorPalette(data.get('active_palette', 'natural'))
        customization.sparkle_effect = data.get('sparkle_effect', False)
        customization.glow_effect = data.get('glow_effect', False)
        customization.shadow_effect = data.get('shadow_effect', True)
        customization.customization_changes = data.get('customization_changes', 0)
        customization.total_accessories_worn = data.get('total_accessories_worn', 0)
        customization.favorite_pattern = PetPattern(data.get('favorite_pattern', 'solid'))

        return customization
