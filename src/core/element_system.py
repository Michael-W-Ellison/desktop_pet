"""
Element System for Desktop Pet

Handles elemental types, type advantages/disadvantages, and elemental interactions.
Similar to Pokemon type effectiveness but adapted for desktop pet interactions.
"""
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import random
from core.config import (
    ElementType,
    ELEMENT_ADVANTAGES,
    SPECIES_ELEMENTS
)


class ElementalInteraction(Enum):
    """Types of elemental interactions."""
    SUPER_EFFECTIVE = "super_effective"  # 2x effectiveness
    EFFECTIVE = "effective"              # 1x effectiveness
    NOT_EFFECTIVE = "not_effective"      # 0.5x effectiveness
    IMMUNE = "immune"                    # 0x effectiveness


class ElementSystem:
    """
    Manages elemental types and their interactions.

    Elements can affect:
    - Learning rates for certain tricks
    - Personality trait modifiers
    - Visual effects (particle systems)
    - Interactions with other creatures
    - Environmental preferences
    """

    def __init__(self, primary_element: ElementType, secondary_element: Optional[ElementType] = None):
        """
        Initialize element system.

        Args:
            primary_element: Primary element type
            secondary_element: Optional secondary element (for dual-type creatures)
        """
        self.primary_element = primary_element
        self.secondary_element = secondary_element
        self.elemental_power = 1.0  # Can be boosted through interactions
        self.elemental_affinity_bonus = 0.0  # Bonus from experience with element

    def get_effectiveness(self, target_element: ElementType) -> Tuple[float, ElementalInteraction]:
        """
        Calculate type effectiveness against another element.

        Args:
            target_element: The target's element type

        Returns:
            Tuple of (multiplier, interaction_type)
        """
        # Check primary element advantage
        multiplier = 1.0
        interaction = ElementalInteraction.EFFECTIVE

        if target_element in ELEMENT_ADVANTAGES.get(self.primary_element, []):
            multiplier *= 2.0
            interaction = ElementalInteraction.SUPER_EFFECTIVE
        elif self.primary_element in ELEMENT_ADVANTAGES.get(target_element, []):
            multiplier *= 0.5
            interaction = ElementalInteraction.NOT_EFFECTIVE

        # Check secondary element if present
        if self.secondary_element:
            if target_element in ELEMENT_ADVANTAGES.get(self.secondary_element, []):
                multiplier *= 1.5  # Secondary element gives smaller bonus
            elif self.secondary_element in ELEMENT_ADVANTAGES.get(target_element, []):
                multiplier *= 0.75  # Secondary element gives smaller penalty

        return multiplier, interaction

    def get_element_modifiers(self) -> Dict[str, float]:
        """
        Get behavioral modifiers based on element type.

        Returns:
            Dictionary of modifier names to multipliers
        """
        # Element-specific behavioral modifiers
        element_behaviors = {
            ElementType.FIRE: {
                "energy_level": 1.3,
                "aggression": 1.2,
                "movement_speed": 1.2,
                "patience": 0.7,
                "warmth_preference": 1.5
            },
            ElementType.WATER: {
                "emotional_stability": 1.3,
                "adaptability": 1.4,
                "calm_behavior": 1.3,
                "flow_movement": 1.2,
                "moisture_preference": 1.5
            },
            ElementType.EARTH: {
                "stubbornness": 1.2,
                "patience": 1.4,
                "stability": 1.5,
                "grounded_behavior": 1.3,
                "solid_stance": 1.4
            },
            ElementType.AIR: {
                "movement_speed": 1.4,
                "curiosity": 1.3,
                "lightness": 1.5,
                "attention_span": 0.8,
                "height_preference": 1.4
            },
            ElementType.LIGHT: {
                "happiness_gain": 1.3,
                "trust": 1.3,
                "brightness": 1.5,
                "optimism": 1.4,
                "day_activity": 1.3
            },
            ElementType.DARK: {
                "stealth": 1.5,
                "independence": 1.3,
                "night_activity": 1.4,
                "mystery": 1.4,
                "shadow_affinity": 1.5
            },
            ElementType.ELECTRIC: {
                "energy_level": 1.5,
                "reaction_speed": 1.4,
                "unpredictability": 1.2,
                "spark": 1.3,
                "charged_behavior": 1.3
            },
            ElementType.ICE: {
                "calm_behavior": 1.4,
                "precision": 1.3,
                "cold_resistance": 1.5,
                "calculated_moves": 1.3,
                "frost_affinity": 1.4
            },
            ElementType.NATURE: {
                "growth_rate": 1.2,
                "healing_factor": 1.3,
                "natural_affinity": 1.5,
                "outdoor_preference": 1.4,
                "vitality": 1.3
            },
            ElementType.PSYCHIC: {
                "intelligence": 1.4,
                "learning_speed": 1.3,
                "intuition": 1.5,
                "mental_focus": 1.4,
                "perception": 1.3
            },
            ElementType.NEUTRAL: {
                "balance": 1.2,
                "adaptability": 1.3,
                "versatility": 1.4
            }
        }

        modifiers = element_behaviors.get(self.primary_element, {}).copy()

        # Add secondary element influence (at 50% strength)
        if self.secondary_element:
            secondary_mods = element_behaviors.get(self.secondary_element, {})
            for key, value in secondary_mods.items():
                if key in modifiers:
                    # Average the two modifiers
                    modifiers[key] = (modifiers[key] + value) / 2
                else:
                    # Add at reduced strength
                    modifiers[key] = 1.0 + (value - 1.0) * 0.5

        # Apply elemental power multiplier
        for key in modifiers:
            modifiers[key] *= self.elemental_power

        return modifiers

    def get_preferred_tricks(self) -> List[str]:
        """
        Get list of tricks this element learns faster.

        Returns:
            List of trick names with affinity bonus
        """
        element_trick_affinities = {
            ElementType.FIRE: ["dance", "jump", "spin"],
            ElementType.WATER: ["fetch", "swim", "flow"],
            ElementType.EARTH: ["sit", "stay", "guard"],
            ElementType.AIR: ["jump", "fly", "spin"],
            ElementType.LIGHT: ["shine", "dance", "greet"],
            ElementType.DARK: ["hide", "stealth", "shadow"],
            ElementType.ELECTRIC: ["zap", "quick", "spark"],
            ElementType.ICE: ["freeze", "slide", "chill"],
            ElementType.NATURE: ["grow", "heal", "bloom"],
            ElementType.PSYCHIC: ["think", "predict", "sense"],
            ElementType.NEUTRAL: []  # No specific preferences
        }

        preferred = element_trick_affinities.get(self.primary_element, []).copy()

        if self.secondary_element:
            preferred.extend(element_trick_affinities.get(self.secondary_element, []))

        return list(set(preferred))  # Remove duplicates

    def boost_elemental_power(self, amount: float = 0.1):
        """
        Increase elemental power through practice or experience.

        Args:
            amount: How much to boost power by
        """
        self.elemental_power = min(2.0, self.elemental_power + amount)  # Cap at 2.0x

    def get_particle_effect_type(self) -> str:
        """
        Get the particle effect type for this element.

        Returns:
            Particle effect identifier
        """
        element_particles = {
            ElementType.FIRE: "flames",
            ElementType.WATER: "water_drops",
            ElementType.EARTH: "rocks",
            ElementType.AIR: "wind_swirls",
            ElementType.LIGHT: "sparkles",
            ElementType.DARK: "shadows",
            ElementType.ELECTRIC: "lightning",
            ElementType.ICE: "snowflakes",
            ElementType.NATURE: "leaves",
            ElementType.PSYCHIC: "energy_rings",
            ElementType.NEUTRAL: "stars"
        }

        return element_particles.get(self.primary_element, "stars")

    def get_element_color(self) -> str:
        """
        Get the primary color associated with this element.

        Returns:
            Hex color code
        """
        element_colors = {
            ElementType.FIRE: "#FF4500",      # Orange-red
            ElementType.WATER: "#1E90FF",     # Dodger blue
            ElementType.EARTH: "#8B4513",     # Saddle brown
            ElementType.AIR: "#87CEEB",       # Sky blue
            ElementType.LIGHT: "#FFD700",     # Gold
            ElementType.DARK: "#4B0082",      # Indigo
            ElementType.ELECTRIC: "#FFFF00",  # Yellow
            ElementType.ICE: "#00FFFF",       # Cyan
            ElementType.NATURE: "#228B22",    # Forest green
            ElementType.PSYCHIC: "#FF00FF",   # Magenta
            ElementType.NEUTRAL: "#808080"    # Gray
        }

        return element_colors.get(self.primary_element, "#808080")

    def get_element_description(self) -> str:
        """Get a description of the creature's element."""
        descriptions = {
            ElementType.FIRE: "Burns with inner flame and passionate energy",
            ElementType.WATER: "Flows gracefully with calm, adaptive nature",
            ElementType.EARTH: "Stands firm with grounded, steady strength",
            ElementType.AIR: "Dances on the wind with light, free spirit",
            ElementType.LIGHT: "Radiates warmth and positive energy",
            ElementType.DARK: "Moves through shadows with mysterious grace",
            ElementType.ELECTRIC: "Crackles with energetic, unpredictable power",
            ElementType.ICE: "Cool and calculated with crystalline beauty",
            ElementType.NATURE: "Thrives with natural vitality and growth",
            ElementType.PSYCHIC: "Thinks deeply with enhanced perception",
            ElementType.NEUTRAL: "Balanced and adaptable to any situation"
        }

        primary_desc = descriptions.get(self.primary_element, "Has a unique elemental nature")

        if self.secondary_element:
            secondary_desc = descriptions.get(self.secondary_element, "")
            return f"{primary_desc}, with hints of {self.secondary_element.value} energy"

        return primary_desc

    def interact_with_element(self, other_element: ElementType) -> Dict[str, Any]:
        """
        Handle interaction with another elemental creature or object.

        Args:
            other_element: The other element involved

        Returns:
            Dictionary describing the interaction outcome
        """
        multiplier, interaction_type = self.get_effectiveness(other_element)

        # Generate interaction message
        messages = {
            ElementalInteraction.SUPER_EFFECTIVE: [
                "The elements resonate powerfully!",
                "A surge of elemental energy!",
                "The reaction is incredibly effective!"
            ],
            ElementalInteraction.EFFECTIVE: [
                "The elements interact normally.",
                "A balanced elemental exchange.",
                "The elements coexist peacefully."
            ],
            ElementalInteraction.NOT_EFFECTIVE: [
                "The elements clash weakly...",
                "The reaction is subdued.",
                "Not much happened..."
            ]
        }

        message = random.choice(messages.get(interaction_type, ["The elements interact."]))

        # Calculate effects
        happiness_change = (multiplier - 1.0) * 10  # -5 to +10 happiness
        bond_change = abs(multiplier - 1.0) * 5     # 0 to 5 bond (any interaction builds bond)

        return {
            'interaction_type': interaction_type.value,
            'multiplier': multiplier,
            'message': message,
            'happiness_change': happiness_change,
            'bond_change': bond_change,
            'visual_effect': interaction_type == ElementalInteraction.SUPER_EFFECTIVE
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize element system state."""
        return {
            'primary_element': self.primary_element.value,
            'secondary_element': self.secondary_element.value if self.secondary_element else None,
            'elemental_power': self.elemental_power,
            'elemental_affinity_bonus': self.elemental_affinity_bonus
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ElementSystem':
        """Deserialize element system state."""
        primary = ElementType(data.get('primary_element', 'neutral'))
        secondary = ElementType(data['secondary_element']) if data.get('secondary_element') else None

        system = cls(primary_element=primary, secondary_element=secondary)
        system.elemental_power = data.get('elemental_power', 1.0)
        system.elemental_affinity_bonus = data.get('elemental_affinity_bonus', 0.0)

        return system

    @staticmethod
    def get_species_element(species: str) -> ElementType:
        """
        Get the default element for a species.

        Args:
            species: Species name

        Returns:
            Element type for that species
        """
        return SPECIES_ELEMENTS.get(species, ElementType.NEUTRAL)


def create_element_system_for_species(species: str) -> ElementSystem:
    """
    Create an element system with the appropriate element for a species.

    Args:
        species: The creature species

    Returns:
        Configured ElementSystem
    """
    element = ElementSystem.get_species_element(species)
    return ElementSystem(primary_element=element)
