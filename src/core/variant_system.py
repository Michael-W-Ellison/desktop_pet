"""
Variant System for Desktop Pal

Handles rare creature variants (shiny, mystic, shadow, crystal).
Similar to shiny Pokemon but with unique stat modifiers and visual effects.
"""
from typing import Dict, Any, Optional, List
import random
import numpy as np
from core.config import (
    VariantType,
    VARIANT_RARITY,
    VARIANT_MODIFIERS
)


class VariantSystem:
    """
    Manages creature variants and their special properties.

    Variants:
    - NORMAL (70%): Standard creature
    - SHINY (15%): Rare color variant with sparkle effects
    - MYSTIC (8%): Magical aura, enhanced learning
    - SHADOW (5%): Dark powers, stronger but less happy
    - CRYSTAL (2%): Ultra-rare, legendary status, best stats
    """

    def __init__(self, variant: VariantType = VariantType.NORMAL):
        """
        Initialize variant system.

        Args:
            variant: The variant type
        """
        self.variant = variant
        self.variant_discovered_time = None
        self.special_effects_active = True

    @staticmethod
    def roll_random_variant() -> VariantType:
        """
        Randomly determine a variant based on rarity rates.

        Returns:
            A variant type based on probability distribution
        """
        # Create weighted random selection
        variants = list(VARIANT_RARITY.keys())
        probabilities = [VARIANT_RARITY[v] for v in variants]

        # Normalize probabilities to sum to 1.0
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]

        return np.random.choice(variants, p=probabilities)

    def get_rarity_tier(self) -> str:
        """
        Get the rarity tier description.

        Returns:
            Rarity tier string
        """
        rarity_tiers = {
            VariantType.NORMAL: "Common",
            VariantType.SHINY: "Rare",
            VariantType.MYSTIC: "Epic",
            VariantType.SHADOW: "Legendary",
            VariantType.CRYSTAL: "Mythical"
        }
        return rarity_tiers.get(self.variant, "Common")

    def get_variant_modifiers(self) -> Dict[str, Any]:
        """
        Get stat modifiers for this variant.

        Returns:
            Dictionary of modifiers
        """
        return VARIANT_MODIFIERS.get(self.variant, VARIANT_MODIFIERS[VariantType.NORMAL]).copy()

    def get_learning_rate_multiplier(self) -> float:
        """Get learning rate multiplier for this variant."""
        mods = self.get_variant_modifiers()
        return mods.get('learning_rate', 1.0)

    def get_happiness_multiplier(self) -> float:
        """Get happiness gain multiplier for this variant."""
        mods = self.get_variant_modifiers()
        return mods.get('happiness_gain', 1.0)

    def get_bond_multiplier(self) -> float:
        """Get bond gain multiplier for this variant."""
        mods = self.get_variant_modifiers()
        return mods.get('bond_gain', 1.0)

    def has_visual_effect(self, effect_type: str) -> bool:
        """
        Check if variant has a specific visual effect.

        Args:
            effect_type: Type of effect to check for

        Returns:
            True if variant has this effect
        """
        mods = self.get_variant_modifiers()
        return mods.get(effect_type, False)

    def get_color_adjustment(self, base_colors: List[str]) -> List[str]:
        """
        Adjust colors based on variant type.

        Args:
            base_colors: Original color palette

        Returns:
            Modified color palette
        """
        if self.variant == VariantType.NORMAL:
            return base_colors

        elif self.variant == VariantType.SHINY:
            # Shiny: Shift hue and increase saturation
            return self._shift_colors_shiny(base_colors)

        elif self.variant == VariantType.MYSTIC:
            # Mystic: Add purple/blue mystical tones
            return self._add_mystical_tones(base_colors)

        elif self.variant == VariantType.SHADOW:
            # Shadow: Darken colors, add dark purple/black
            return self._darken_colors(base_colors)

        elif self.variant == VariantType.CRYSTAL:
            # Crystal: Brighten, add translucent/crystalline effect
            return self._crystallize_colors(base_colors)

        return base_colors

    def _shift_colors_shiny(self, colors: List[str]) -> List[str]:
        """Shift colors for shiny variant."""
        # For shiny, we rotate the hue by 60-120 degrees and boost saturation
        shiny_colors = []
        for color in colors:
            # Convert hex to RGB
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

            # Simple hue shift (rotate colors)
            # This is a simplified version - full HSV conversion would be better
            shiny_r = min(255, int(r * 0.7 + g * 0.3))
            shiny_g = min(255, int(g * 0.7 + b * 0.3))
            shiny_b = min(255, int(b * 0.7 + r * 0.3))

            shiny_colors.append(f"#{shiny_r:02X}{shiny_g:02X}{shiny_b:02X}")

        return shiny_colors

    def _add_mystical_tones(self, colors: List[str]) -> List[str]:
        """Add mystical purple/blue tones."""
        mystical_colors = []
        for color in colors:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

            # Boost blue and add purple
            mystic_r = min(255, int(r * 0.8 + 100 * 0.2))
            mystic_g = min(255, int(g * 0.9 + 80 * 0.1))
            mystic_b = min(255, int(b * 1.2))

            mystical_colors.append(f"#{mystic_r:02X}{mystic_g:02X}{mystic_b:02X}")

        return mystical_colors

    def _darken_colors(self, colors: List[str]) -> List[str]:
        """Darken colors for shadow variant."""
        shadow_colors = []
        for color in colors:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

            # Darken significantly, add purple tint
            shadow_r = int(r * 0.4 + 40 * 0.1)
            shadow_g = int(g * 0.4)
            shadow_b = int(b * 0.5 + 60 * 0.1)

            shadow_colors.append(f"#{shadow_r:02X}{shadow_g:02X}{shadow_b:02X}")

        return shadow_colors

    def _crystallize_colors(self, colors: List[str]) -> List[str]:
        """Brighten and add crystalline quality."""
        crystal_colors = []
        for color in colors:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)

            # Brighten and add cyan/white tint
            crystal_r = min(255, int(r * 1.3 + 200 * 0.2))
            crystal_g = min(255, int(g * 1.3 + 230 * 0.2))
            crystal_b = min(255, int(b * 1.4 + 255 * 0.1))

            crystal_colors.append(f"#{crystal_r:02X}{crystal_g:02X}{crystal_b:02X}")

        return crystal_colors

    def get_variant_description(self) -> str:
        """Get a description of the variant."""
        descriptions = {
            VariantType.NORMAL: "A typical member of its species",
            VariantType.SHINY: "✨ A rare shimmering variant with unusual coloring!",
            VariantType.MYSTIC: "🔮 A mystical variant radiating magical energy!",
            VariantType.SHADOW: "🌑 A shadowy variant with dark, mysterious powers!",
            VariantType.CRYSTAL: "💎 An ultra-rare crystalline variant of legendary status!"
        }
        return descriptions.get(self.variant, "A unique creature")

    def get_variant_emoji(self) -> str:
        """Get emoji representing the variant."""
        emojis = {
            VariantType.NORMAL: "",
            VariantType.SHINY: "✨",
            VariantType.MYSTIC: "🔮",
            VariantType.SHADOW: "🌑",
            VariantType.CRYSTAL: "💎"
        }
        return emojis.get(self.variant, "")

    def get_special_abilities(self) -> List[str]:
        """Get list of special abilities this variant has."""
        abilities = {
            VariantType.NORMAL: [],
            VariantType.SHINY: [
                "Sparkle Trail",
                "Enhanced Charm",
                "Luck Boost"
            ],
            VariantType.MYSTIC: [
                "Magical Aura",
                "Enhanced Learning",
                "Trick Mastery",
                "Mystical Presence"
            ],
            VariantType.SHADOW: [
                "Shadow Cloak",
                "Intimidating Presence",
                "Night Affinity",
                "Dark Resilience"
            ],
            VariantType.CRYSTAL: [
                "Crystalline Barrier",
                "Perfect Learning",
                "Legendary Aura",
                "Maximum Bond",
                "Eternal Beauty"
            ]
        }
        return abilities.get(self.variant, [])

    def get_particle_effects(self) -> List[str]:
        """Get list of particle effects for this variant."""
        effects = []

        mods = self.get_variant_modifiers()

        if mods.get('sparkle_effect'):
            effects.append('sparkles')

        if mods.get('aura_effect'):
            effects.append('mystical_aura')

        if mods.get('dark_aura'):
            effects.append('shadow_aura')

        if mods.get('crystal_effect'):
            effects.append('crystal_gleam')

        return effects

    def is_rare(self) -> bool:
        """Check if this is a rare variant (anything other than normal)."""
        return self.variant != VariantType.NORMAL

    def get_encounter_message(self) -> Optional[str]:
        """Get special message when first encountering this variant."""
        if self.variant == VariantType.NORMAL:
            return None

        messages = {
            VariantType.SHINY: "✨ WOW! You've encountered a rare SHINY variant! ✨",
            VariantType.MYSTIC: "🔮 INCREDIBLE! This is a MYSTIC variant with magical powers! 🔮",
            VariantType.SHADOW: "🌑 AMAZING! A SHADOW variant has appeared from the darkness! 🌑",
            VariantType.CRYSTAL: "💎 LEGENDARY! You've found an ultra-rare CRYSTAL variant! 💎"
        }

        return messages.get(self.variant)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize variant system state."""
        return {
            'variant': self.variant.value,
            'variant_discovered_time': self.variant_discovered_time,
            'special_effects_active': self.special_effects_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VariantSystem':
        """Deserialize variant system state."""
        variant = VariantType(data.get('variant', 'normal'))
        system = cls(variant=variant)

        system.variant_discovered_time = data.get('variant_discovered_time')
        system.special_effects_active = data.get('special_effects_active', True)

        return system


def generate_random_variant() -> VariantSystem:
    """
    Generate a random variant based on rarity probabilities.

    Returns:
        A new VariantSystem with randomly determined variant
    """
    variant = VariantSystem.roll_random_variant()
    return VariantSystem(variant=variant)
