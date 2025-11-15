"""
Phase 15: Furniture Effects System

Manages furniture quality, bonuses, and special effects.
"""
from typing import Dict, Any, List, Optional
from enum import Enum


class FurnitureQuality(Enum):
    """Quality tiers for furniture."""
    BASIC = "basic"              # Basic quality (1.0x effects)
    STANDARD = "standard"        # Standard quality (1.2x effects)
    PREMIUM = "premium"          # Premium quality (1.5x effects)
    LUXURY = "luxury"            # Luxury quality (2.0x effects)
    LEGENDARY = "legendary"      # Legendary quality (3.0x effects)


class FurnitureCondition(Enum):
    """Furniture condition states."""
    BROKEN = "broken"            # 0-20% durability
    POOR = "poor"                # 20-40% durability
    FAIR = "fair"                # 40-60% durability
    GOOD = "good"                # 60-80% durability
    EXCELLENT = "excellent"      # 80-100% durability


class FurnitureEffect:
    """Represents a furniture's effects and bonuses."""

    def __init__(self, furniture_id: str, item_name: str):
        """
        Initialize furniture effect.

        Args:
            furniture_id: Unique furniture ID
            item_name: Furniture name
        """
        self.furniture_id = furniture_id
        self.item_name = item_name

        # Quality
        self.quality = FurnitureQuality.STANDARD
        self.quality_multiplier = 1.2

        # Durability
        self.max_durability = 100
        self.current_durability = 100
        self.durability_loss_per_use = 2

        # Base effects (stat -> value)
        self.base_effects: Dict[str, float] = {}

        # Bonus effects
        self.comfort_bonus = 0          # Extra happiness/stress relief
        self.speed_bonus = 0.0          # Interaction completes faster (0-1)
        self.efficiency_bonus = 0       # Effect multiplier bonus

        # Special effects
        self.special_effects: List[str] = []  # e.g., "sparkle", "heal_over_time"

        # Usage tracking
        self.times_used = 0
        self.total_effect_applied = 0.0
        self.favorite = False

    def set_quality(self, quality: FurnitureQuality):
        """Set furniture quality tier."""
        self.quality = quality

        # Set multiplier based on quality
        multipliers = {
            FurnitureQuality.BASIC: 1.0,
            FurnitureQuality.STANDARD: 1.2,
            FurnitureQuality.PREMIUM: 1.5,
            FurnitureQuality.LUXURY: 2.0,
            FurnitureQuality.LEGENDARY: 3.0
        }
        self.quality_multiplier = multipliers.get(quality, 1.0)

    def set_base_effects(self, effects: Dict[str, float]):
        """Set base effects for the furniture."""
        self.base_effects = effects.copy()

    def get_effective_effects(self) -> Dict[str, float]:
        """
        Get actual effects considering quality, durability, and bonuses.

        Returns:
            Effective effects dictionary
        """
        effects = {}

        # Start with base effects
        for stat, value in self.base_effects.items():
            effects[stat] = value

        # Apply quality multiplier
        for stat in effects:
            effects[stat] *= self.quality_multiplier

        # Apply efficiency bonus
        if self.efficiency_bonus > 0:
            for stat in effects:
                effects[stat] *= (1.0 + self.efficiency_bonus / 100)

        # Apply durability penalty
        durability_factor = self.get_durability_factor()
        for stat in effects:
            effects[stat] *= durability_factor

        # Add comfort bonus to happiness/stress
        if 'happiness' in effects:
            effects['happiness'] += self.comfort_bonus
        if 'stress' in effects and effects['stress'] < 0:
            effects['stress'] -= self.comfort_bonus * 0.5

        return effects

    def get_duration_modifier(self) -> float:
        """
        Get interaction duration modifier based on speed bonus.

        Returns:
            Duration multiplier (1.0 = normal, 0.5 = twice as fast)
        """
        return max(0.5, 1.0 - self.speed_bonus)

    def get_durability_factor(self) -> float:
        """
        Get effect multiplier based on durability.

        Returns:
            Multiplier (0.5-1.0)
        """
        percentage = self.current_durability / self.max_durability
        # Minimum 50% effectiveness even when broken
        return max(0.5, percentage)

    def get_condition(self) -> FurnitureCondition:
        """Get furniture condition based on durability."""
        percentage = (self.current_durability / self.max_durability) * 100

        if percentage <= 20:
            return FurnitureCondition.BROKEN
        elif percentage <= 40:
            return FurnitureCondition.POOR
        elif percentage <= 60:
            return FurnitureCondition.FAIR
        elif percentage <= 80:
            return FurnitureCondition.GOOD
        else:
            return FurnitureCondition.EXCELLENT

    def use(self):
        """Record furniture usage and apply durability loss."""
        self.times_used += 1

        # Reduce durability
        self.current_durability = max(0, self.current_durability - self.durability_loss_per_use)

        # Track total effects
        effects = self.get_effective_effects()
        total_effect = sum(abs(v) for v in effects.values())
        self.total_effect_applied += total_effect

    def repair(self, amount: int):
        """
        Repair furniture.

        Args:
            amount: Durability to restore
        """
        self.current_durability = min(self.max_durability, self.current_durability + amount)

    def upgrade_quality(self):
        """Upgrade furniture to next quality tier."""
        quality_order = [
            FurnitureQuality.BASIC,
            FurnitureQuality.STANDARD,
            FurnitureQuality.PREMIUM,
            FurnitureQuality.LUXURY,
            FurnitureQuality.LEGENDARY
        ]

        current_index = quality_order.index(self.quality)
        if current_index < len(quality_order) - 1:
            self.set_quality(quality_order[current_index + 1])
            return True
        return False

    def add_special_effect(self, effect: str):
        """Add special effect to furniture."""
        if effect not in self.special_effects:
            self.special_effects.append(effect)

    def remove_special_effect(self, effect: str):
        """Remove special effect from furniture."""
        if effect in self.special_effects:
            self.special_effects.remove(effect)

    def needs_repair(self, threshold: float = 0.5) -> bool:
        """Check if furniture needs repair."""
        return (self.current_durability / self.max_durability) < threshold

    def is_broken(self) -> bool:
        """Check if furniture is broken."""
        return self.get_condition() == FurnitureCondition.BROKEN

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'furniture_id': self.furniture_id,
            'item_name': self.item_name,
            'quality': self.quality.value,
            'quality_multiplier': self.quality_multiplier,
            'max_durability': self.max_durability,
            'current_durability': self.current_durability,
            'durability_loss_per_use': self.durability_loss_per_use,
            'base_effects': self.base_effects,
            'comfort_bonus': self.comfort_bonus,
            'speed_bonus': self.speed_bonus,
            'efficiency_bonus': self.efficiency_bonus,
            'special_effects': self.special_effects,
            'times_used': self.times_used,
            'total_effect_applied': self.total_effect_applied,
            'favorite': self.favorite
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FurnitureEffect':
        """Deserialize from dictionary."""
        effect = cls(
            furniture_id=data['furniture_id'],
            item_name=data['item_name']
        )
        effect.quality = FurnitureQuality(data.get('quality', 'standard'))
        effect.quality_multiplier = data.get('quality_multiplier', 1.2)
        effect.max_durability = data.get('max_durability', 100)
        effect.current_durability = data.get('current_durability', 100)
        effect.durability_loss_per_use = data.get('durability_loss_per_use', 2)
        effect.base_effects = data.get('base_effects', {})
        effect.comfort_bonus = data.get('comfort_bonus', 0)
        effect.speed_bonus = data.get('speed_bonus', 0.0)
        effect.efficiency_bonus = data.get('efficiency_bonus', 0)
        effect.special_effects = data.get('special_effects', [])
        effect.times_used = data.get('times_used', 0)
        effect.total_effect_applied = data.get('total_effect_applied', 0.0)
        effect.favorite = data.get('favorite', False)
        return effect


class FurnitureEffectsManager:
    """
    Manages effects for all furniture in the room.

    Features:
    - Track furniture quality and condition
    - Apply usage and durability
    - Manage bonuses and special effects
    - Repair and upgrade furniture
    """

    def __init__(self):
        """Initialize furniture effects manager."""
        # Furniture effects
        self.furniture_effects: Dict[str, FurnitureEffect] = {}

        # Preset effects by furniture type
        self.preset_effects = {
            'bed_basic': {'energy': 25, 'happiness': 5},
            'bed_premium': {'energy': 35, 'happiness': 10},
            'bed_luxury': {'energy': 50, 'happiness': 15, 'stress': -10},
            'food_bowl_basic': {'hunger': -30, 'happiness': 5},
            'food_bowl_premium': {'hunger': -45, 'happiness': 10},
            'toy_ball': {'happiness': 15, 'boredom': -20, 'energy': -5},
            'toy_premium': {'happiness': 25, 'boredom': -30, 'energy': -5, 'intelligence': 3},
            'scratching_post': {'stress': -15, 'happiness': 10, 'boredom': -10},
            'cat_tree': {'stress': -20, 'happiness': 15, 'boredom': -15, 'energy': -8},
        }

        # Statistics
        self.total_furniture_uses = 0
        self.total_repairs = 0
        self.total_upgrades = 0

    def register_furniture(self, furniture_id: str, item_name: str,
                          item_type: str, quality: FurnitureQuality = FurnitureQuality.STANDARD):
        """
        Register furniture and create effects.

        Args:
            furniture_id: Unique furniture ID
            item_name: Furniture name
            item_type: Type of furniture (for preset effects)
            quality: Quality tier
        """
        effect = FurnitureEffect(furniture_id, item_name)
        effect.set_quality(quality)

        # Apply preset effects if available
        if item_type in self.preset_effects:
            effect.set_base_effects(self.preset_effects[item_type])

        self.furniture_effects[furniture_id] = effect

    def use_furniture(self, furniture_id: str) -> Optional[Dict[str, float]]:
        """
        Use furniture and get effective effects.

        Args:
            furniture_id: Furniture to use

        Returns:
            Effective effects or None
        """
        effect = self.furniture_effects.get(furniture_id)
        if not effect:
            return None

        # Use furniture
        effect.use()
        self.total_furniture_uses += 1

        # Return effective effects
        return effect.get_effective_effects()

    def repair_furniture(self, furniture_id: str, amount: int = 50) -> bool:
        """
        Repair furniture.

        Args:
            furniture_id: Furniture to repair
            amount: Amount to repair

        Returns:
            True if successful
        """
        effect = self.furniture_effects.get(furniture_id)
        if not effect:
            return False

        effect.repair(amount)
        self.total_repairs += 1
        return True

    def upgrade_furniture(self, furniture_id: str) -> bool:
        """
        Upgrade furniture quality.

        Args:
            furniture_id: Furniture to upgrade

        Returns:
            True if successful
        """
        effect = self.furniture_effects.get(furniture_id)
        if not effect:
            return False

        if effect.upgrade_quality():
            self.total_upgrades += 1
            return True
        return False

    def get_furniture_effect(self, furniture_id: str) -> Optional[FurnitureEffect]:
        """Get furniture effect object."""
        return self.furniture_effects.get(furniture_id)

    def get_broken_furniture(self) -> List[FurnitureEffect]:
        """Get all broken furniture."""
        return [
            effect for effect in self.furniture_effects.values()
            if effect.is_broken()
        ]

    def get_furniture_needing_repair(self, threshold: float = 0.5) -> List[FurnitureEffect]:
        """Get furniture that needs repair."""
        return [
            effect for effect in self.furniture_effects.values()
            if effect.needs_repair(threshold)
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get furniture effects statistics."""
        total_durability = 0
        avg_quality_multiplier = 0

        if self.furniture_effects:
            for effect in self.furniture_effects.values():
                total_durability += effect.current_durability / effect.max_durability
                avg_quality_multiplier += effect.quality_multiplier

            avg_durability = total_durability / len(self.furniture_effects) * 100
            avg_quality_multiplier /= len(self.furniture_effects)
        else:
            avg_durability = 100
            avg_quality_multiplier = 1.0

        quality_distribution = {}
        for effect in self.furniture_effects.values():
            quality = effect.quality.value
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1

        return {
            'total_furniture': len(self.furniture_effects),
            'total_uses': self.total_furniture_uses,
            'total_repairs': self.total_repairs,
            'total_upgrades': self.total_upgrades,
            'average_durability': avg_durability,
            'average_quality_multiplier': avg_quality_multiplier,
            'broken_furniture': len(self.get_broken_furniture()),
            'furniture_needing_repair': len(self.get_furniture_needing_repair()),
            'quality_distribution': quality_distribution
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'furniture_effects': {
                furn_id: effect.to_dict()
                for furn_id, effect in self.furniture_effects.items()
            },
            'total_furniture_uses': self.total_furniture_uses,
            'total_repairs': self.total_repairs,
            'total_upgrades': self.total_upgrades
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FurnitureEffectsManager':
        """Deserialize from dictionary."""
        manager = cls()

        # Restore furniture effects
        effects_data = data.get('furniture_effects', {})
        for furn_id, effect_data in effects_data.items():
            manager.furniture_effects[furn_id] = FurnitureEffect.from_dict(effect_data)

        manager.total_furniture_uses = data.get('total_furniture_uses', 0)
        manager.total_repairs = data.get('total_repairs', 0)
        manager.total_upgrades = data.get('total_upgrades', 0)

        return manager
