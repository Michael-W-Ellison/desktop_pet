"""
Phase 8: Aging and Lifespan System

Manages pet aging from baby to elder and natural end of life.
"""
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum


class LifeStage(Enum):
    """Life stages of a pet."""
    EGG = "egg"              # 0-3 days
    BABY = "baby"            # 3-30 days
    CHILD = "child"          # 30-90 days
    TEEN = "teen"            # 90-180 days
    ADULT = "adult"          # 180-2555 days (7 years)
    SENIOR = "senior"        # 2555-3650 days (7-10 years)
    ELDER = "elder"          # 3650+ days (10+ years)


class AgingSystem:
    """
    Manages pet aging and lifespan.

    Features:
    - Aging from baby to elder
    - Life stage transitions
    - Natural lifespan
    - Death from old age
    - Age-based stat modifiers
    """

    def __init__(self, birth_time: float = None, lifespan_days: float = 3650):
        """
        Initialize aging system.

        Args:
            birth_time: When pet was born (timestamp)
            lifespan_days: Expected lifespan in days (default ~10 years)
        """
        self.birth_time = birth_time or time.time()
        self.lifespan_days = lifespan_days  # Natural lifespan

        # Current age
        self.age_seconds = 0.0
        self.age_days = 0.0

        # Life stage
        self.current_stage = LifeStage.EGG
        self.stage_history = []  # List of stage transitions

        # Mortality
        self.is_alive = True
        self.death_time = None
        self.cause_of_death = None

        # Aging rate (can be modified)
        self.aging_rate = 1.0  # 1.0 = normal, 2.0 = twice as fast

        # Health effects of aging
        self.age_related_health_decay = 0.0

    def update(self, hours_elapsed: float):
        """
        Update age.

        Args:
            hours_elapsed: Hours since last update
        """
        if not self.is_alive:
            return

        # Age the pet
        seconds_elapsed = hours_elapsed * 3600.0
        self.age_seconds += seconds_elapsed * self.aging_rate
        self.age_days = self.age_seconds / 86400.0

        # Check for life stage transition
        new_stage = self._calculate_life_stage()
        if new_stage != self.current_stage:
            self._transition_to_stage(new_stage)

        # Check for natural death
        if self.age_days >= self.lifespan_days:
            self._check_natural_death()

    def _calculate_life_stage(self) -> LifeStage:
        """Calculate current life stage based on age."""
        if self.age_days < 3:
            return LifeStage.EGG
        elif self.age_days < 30:
            return LifeStage.BABY
        elif self.age_days < 90:
            return LifeStage.CHILD
        elif self.age_days < 180:
            return LifeStage.TEEN
        elif self.age_days < 2555:  # ~7 years
            return LifeStage.ADULT
        elif self.age_days < 3650:  # ~10 years
            return LifeStage.SENIOR
        else:
            return LifeStage.ELDER

    def _transition_to_stage(self, new_stage: LifeStage):
        """Transition to a new life stage."""
        old_stage = self.current_stage

        transition = {
            'from_stage': old_stage.value,
            'to_stage': new_stage.value,
            'age_days': self.age_days,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat()
        }

        self.stage_history.append(transition)
        self.current_stage = new_stage

    def _check_natural_death(self):
        """Check if pet dies from old age."""
        import random

        # Past lifespan, increasing chance of death
        days_over = self.age_days - self.lifespan_days

        # Death probability increases with age
        death_chance = min(0.95, days_over / 365.0)  # Max 95% chance

        if random.random() < death_chance:
            self.die("old_age")

    def die(self, cause: str):
        """
        Pet dies.

        Args:
            cause: Cause of death
        """
        if not self.is_alive:
            return

        self.is_alive = False
        self.death_time = time.time()
        self.cause_of_death = cause

    def get_age_modifiers(self) -> Dict[str, float]:
        """
        Get stat modifiers based on age.

        Returns:
            Dictionary of stat multipliers
        """
        stage = self.current_stage

        # Different stages have different capabilities
        if stage == LifeStage.EGG:
            return {
                'energy_max': 0.5,
                'hunger_rate': 0.3,
                'learning_rate': 0.0,
                'bond_rate': 0.0,
                'activity_level': 0.0
            }
        elif stage == LifeStage.BABY:
            return {
                'energy_max': 0.6,
                'hunger_rate': 1.5,  # Babies eat more frequently
                'learning_rate': 1.2,  # Learn quickly
                'bond_rate': 1.5,  # Bond easily
                'activity_level': 0.7
            }
        elif stage == LifeStage.CHILD:
            return {
                'energy_max': 0.8,
                'hunger_rate': 1.3,
                'learning_rate': 1.5,  # Peak learning
                'bond_rate': 1.3,
                'activity_level': 1.2  # Very active
            }
        elif stage == LifeStage.TEEN:
            return {
                'energy_max': 1.0,
                'hunger_rate': 1.4,  # Growth spurt
                'learning_rate': 1.3,
                'bond_rate': 0.9,  # Slightly rebellious
                'activity_level': 1.3  # Most active
            }
        elif stage == LifeStage.ADULT:
            return {
                'energy_max': 1.0,
                'hunger_rate': 1.0,
                'learning_rate': 1.0,
                'bond_rate': 1.0,
                'activity_level': 1.0
            }
        elif stage == LifeStage.SENIOR:
            return {
                'energy_max': 0.8,
                'hunger_rate': 0.8,
                'learning_rate': 0.7,
                'bond_rate': 1.1,  # More affectionate
                'activity_level': 0.7
            }
        else:  # ELDER
            return {
                'energy_max': 0.6,
                'hunger_rate': 0.6,
                'learning_rate': 0.5,
                'bond_rate': 1.2,  # Very affectionate
                'activity_level': 0.5
            }

    def get_remaining_lifespan(self) -> Dict[str, Any]:
        """Get information about remaining lifespan."""
        if not self.is_alive:
            return {
                'is_alive': False,
                'death_time': self.death_time,
                'cause_of_death': self.cause_of_death
            }

        remaining_days = max(0, self.lifespan_days - self.age_days)
        life_percentage = (self.age_days / self.lifespan_days) * 100.0

        return {
            'is_alive': True,
            'remaining_days': remaining_days,
            'remaining_years': remaining_days / 365.0,
            'life_percentage': life_percentage,
            'expected_death_date': self.birth_time + (self.lifespan_days * 86400.0)
        }

    def extend_lifespan(self, days: float, reason: str):
        """
        Extend pet's lifespan.

        Args:
            days: Days to add to lifespan
            reason: Reason for extension (good care, medicine, etc.)
        """
        self.lifespan_days += days

    def get_life_stage_description(self) -> str:
        """Get human-readable description of life stage."""
        descriptions = {
            LifeStage.EGG: "Still developing in egg",
            LifeStage.BABY: "Young baby, learning about the world",
            LifeStage.CHILD: "Playful child, full of energy",
            LifeStage.TEEN: "Energetic teenager, testing boundaries",
            LifeStage.ADULT: "Mature adult in their prime",
            LifeStage.SENIOR: "Wise senior, slowing down",
            LifeStage.ELDER: "Elderly, deserves comfort and care"
        }
        return descriptions.get(self.current_stage, "Unknown")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive aging status."""
        lifespan_info = self.get_remaining_lifespan()

        return {
            'is_alive': self.is_alive,
            'age_days': self.age_days,
            'age_years': self.age_days / 365.0,
            'life_stage': self.current_stage.value,
            'stage_description': self.get_life_stage_description(),
            'lifespan_days': self.lifespan_days,
            'lifespan_years': self.lifespan_days / 365.0,
            'life_percentage': lifespan_info.get('life_percentage', 0.0),
            'remaining_days': lifespan_info.get('remaining_days', 0),
            'stage_transitions': len(self.stage_history),
            'aging_rate': self.aging_rate,
            'death_time': self.death_time,
            'cause_of_death': self.cause_of_death
        }

    def get_age_in_human_years(self, species: str = 'cat') -> float:
        """
        Convert pet age to approximate human years.

        Args:
            species: Species type (affects conversion)

        Returns:
            Approximate age in human years
        """
        # Simplified conversion
        # First year = 15 human years
        # Second year = 9 human years
        # Each year after = 4 human years

        if self.age_days < 365:
            return (self.age_days / 365.0) * 15.0
        elif self.age_days < 730:
            return 15.0 + ((self.age_days - 365.0) / 365.0) * 9.0
        else:
            years_after_2 = (self.age_days - 730.0) / 365.0
            return 15.0 + 9.0 + (years_after_2 * 4.0)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'birth_time': self.birth_time,
            'lifespan_days': self.lifespan_days,
            'age_seconds': self.age_seconds,
            'age_days': self.age_days,
            'current_stage': self.current_stage.value,
            'stage_history': self.stage_history.copy(),
            'is_alive': self.is_alive,
            'death_time': self.death_time,
            'cause_of_death': self.cause_of_death,
            'aging_rate': self.aging_rate,
            'age_related_health_decay': self.age_related_health_decay
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgingSystem':
        """Deserialize from dictionary."""
        system = cls(
            birth_time=data.get('birth_time', time.time()),
            lifespan_days=data.get('lifespan_days', 3650)
        )
        system.age_seconds = data.get('age_seconds', 0.0)
        system.age_days = data.get('age_days', 0.0)
        system.current_stage = LifeStage(data.get('current_stage', 'egg'))
        system.stage_history = data.get('stage_history', [])
        system.is_alive = data.get('is_alive', True)
        system.death_time = data.get('death_time')
        system.cause_of_death = data.get('cause_of_death')
        system.aging_rate = data.get('aging_rate', 1.0)
        system.age_related_health_decay = data.get('age_related_health_decay', 0.0)
        return system
