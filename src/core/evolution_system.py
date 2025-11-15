"""
Evolution System for Desktop Pet

Handles creature evolution through different life stages (baby -> juvenile -> adult -> elder).
Evolution is based on age, care quality, bond strength, and interactions.
"""
from typing import Dict, Any, Optional, Tuple
import time
from enum import Enum
from core.config import (
    EvolutionStage,
    EVOLUTION_REQUIREMENTS,
    STAGE_SIZE_MULTIPLIERS
)


class EvolutionTrigger(Enum):
    """Events that can trigger evolution checks."""
    TIME_PASSED = "time_passed"
    INTERACTION = "interaction"
    HAPPINESS_GAIN = "happiness_gain"
    BOND_INCREASE = "bond_increase"
    TRICK_LEARNED = "trick_learned"
    MANUAL_CHECK = "manual_check"


class EvolutionSystem:
    """
    Manages creature evolution through life stages.

    Evolution progression:
    - BABY: 0-2 hours, no requirements
    - JUVENILE: 2+ hours, needs happiness 40+, bond 30+
    - ADULT: 6+ hours, needs happiness 60+, bond 60+, 50+ interactions
    - ELDER: 12+ hours, needs happiness 70+, bond 80+, 100+ interactions, 3+ tricks

    Creatures can evolve automatically when requirements are met, or evolution
    can be checked manually. Poor care can delay evolution.
    """

    def __init__(self, current_stage: EvolutionStage = EvolutionStage.BABY):
        """
        Initialize the evolution system.

        Args:
            current_stage: Starting evolution stage
        """
        self.current_stage = current_stage
        self.evolution_history = []  # Track evolution events
        self.next_evolution_time = None  # When next evolution is possible
        self.evolution_ready = False  # Whether creature can evolve now
        self.evolution_delayed = False  # Whether evolution was delayed due to poor care

    def check_evolution_eligibility(self, creature_stats: Dict[str, Any]) -> Tuple[bool, Optional[EvolutionStage], str]:
        """
        Check if creature is eligible to evolve to next stage.

        Args:
            creature_stats: Dictionary containing:
                - age_hours: Creature age in hours
                - happiness: Current happiness (0-100)
                - bond: Bond level (0-100)
                - total_interactions: Total number of interactions
                - tricks_learned: Number of tricks learned

        Returns:
            Tuple of (can_evolve, next_stage, reason)
        """
        # Already at max stage
        if self.current_stage == EvolutionStage.ELDER:
            return False, None, "Already at maximum evolution stage (Elder)"

        # Determine next stage
        stage_progression = {
            EvolutionStage.BABY: EvolutionStage.JUVENILE,
            EvolutionStage.JUVENILE: EvolutionStage.ADULT,
            EvolutionStage.ADULT: EvolutionStage.ELDER
        }
        next_stage = stage_progression[self.current_stage]

        # Get requirements for next stage
        requirements = EVOLUTION_REQUIREMENTS[next_stage]

        # Check each requirement
        age_hours = creature_stats.get('age_hours', 0)
        happiness = creature_stats.get('happiness', 0)
        bond = creature_stats.get('bond', 0)
        interactions = creature_stats.get('total_interactions', 0)
        tricks = creature_stats.get('tricks_learned', 0)

        # Age check
        if age_hours < requirements['min_age_hours']:
            hours_needed = requirements['min_age_hours'] - age_hours
            return False, None, f"Too young - needs {hours_needed:.1f} more hours"

        # Happiness check
        if happiness < requirements['min_happiness']:
            needed = requirements['min_happiness'] - happiness
            return False, None, f"Not happy enough - needs {needed:.0f} more happiness"

        # Bond check
        if bond < requirements['min_bond']:
            needed = requirements['min_bond'] - bond
            return False, None, f"Bond not strong enough - needs {needed:.0f} more bond"

        # Interaction check (for adult and elder)
        if 'min_interactions' in requirements:
            if interactions < requirements['min_interactions']:
                needed = requirements['min_interactions'] - interactions
                return False, None, f"Not enough interactions - needs {needed} more"

        # Tricks check (for elder)
        if 'min_tricks_learned' in requirements:
            if tricks < requirements['min_tricks_learned']:
                needed = requirements['min_tricks_learned'] - tricks
                return False, None, f"Not enough tricks learned - needs {needed} more"

        # All requirements met!
        return True, next_stage, f"Ready to evolve to {next_stage.value.title()}!"

    def evolve(self, creature_stats: Dict[str, Any]) -> Tuple[bool, Optional[EvolutionStage], str]:
        """
        Attempt to evolve the creature to the next stage.

        Args:
            creature_stats: Current creature statistics

        Returns:
            Tuple of (success, new_stage, message)
        """
        can_evolve, next_stage, reason = self.check_evolution_eligibility(creature_stats)

        if not can_evolve:
            return False, self.current_stage, f"Cannot evolve: {reason}"

        # Evolution successful!
        old_stage = self.current_stage
        self.current_stage = next_stage
        self.evolution_ready = False
        self.evolution_delayed = False

        # Record evolution event
        evolution_event = {
            'timestamp': time.time(),
            'from_stage': old_stage,
            'to_stage': next_stage,
            'age_hours': creature_stats.get('age_hours', 0),
            'happiness': creature_stats.get('happiness', 0),
            'bond': creature_stats.get('bond', 0)
        }
        self.evolution_history.append(evolution_event)

        message = f"🎉 Evolved from {old_stage.value.title()} to {next_stage.value.title()}!"
        return True, next_stage, message

    def get_stage_multiplier(self) -> float:
        """
        Get the size multiplier for the current evolution stage.

        Returns:
            Size multiplier (0.6 for baby, 1.2 for elder)
        """
        return STAGE_SIZE_MULTIPLIERS[self.current_stage]

    def get_evolution_progress(self, creature_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information about evolution progress.

        Args:
            creature_stats: Current creature statistics

        Returns:
            Dictionary with progress information
        """
        if self.current_stage == EvolutionStage.ELDER:
            return {
                'current_stage': self.current_stage,
                'can_evolve': False,
                'progress_percent': 100,
                'message': "Maximum evolution stage reached!"
            }

        # Determine next stage
        stage_progression = {
            EvolutionStage.BABY: EvolutionStage.JUVENILE,
            EvolutionStage.JUVENILE: EvolutionStage.ADULT,
            EvolutionStage.ADULT: EvolutionStage.ELDER
        }
        next_stage = stage_progression[self.current_stage]
        requirements = EVOLUTION_REQUIREMENTS[next_stage]

        # Calculate progress for each requirement
        age_hours = creature_stats.get('age_hours', 0)
        happiness = creature_stats.get('happiness', 0)
        bond = creature_stats.get('bond', 0)
        interactions = creature_stats.get('total_interactions', 0)
        tricks = creature_stats.get('tricks_learned', 0)

        progress_items = []
        total_progress = 0
        num_requirements = 0

        # Age progress
        age_progress = min(100, (age_hours / requirements['min_age_hours']) * 100)
        progress_items.append({
            'name': 'Age',
            'current': age_hours,
            'required': requirements['min_age_hours'],
            'progress': age_progress,
            'met': age_hours >= requirements['min_age_hours']
        })
        total_progress += age_progress
        num_requirements += 1

        # Happiness progress
        happiness_progress = min(100, (happiness / requirements['min_happiness']) * 100)
        progress_items.append({
            'name': 'Happiness',
            'current': happiness,
            'required': requirements['min_happiness'],
            'progress': happiness_progress,
            'met': happiness >= requirements['min_happiness']
        })
        total_progress += happiness_progress
        num_requirements += 1

        # Bond progress
        bond_progress = min(100, (bond / requirements['min_bond']) * 100)
        progress_items.append({
            'name': 'Bond',
            'current': bond,
            'required': requirements['min_bond'],
            'progress': bond_progress,
            'met': bond >= requirements['min_bond']
        })
        total_progress += bond_progress
        num_requirements += 1

        # Interactions (if required)
        if 'min_interactions' in requirements:
            interaction_progress = min(100, (interactions / requirements['min_interactions']) * 100)
            progress_items.append({
                'name': 'Interactions',
                'current': interactions,
                'required': requirements['min_interactions'],
                'progress': interaction_progress,
                'met': interactions >= requirements['min_interactions']
            })
            total_progress += interaction_progress
            num_requirements += 1

        # Tricks (if required)
        if 'min_tricks_learned' in requirements:
            trick_progress = min(100, (tricks / requirements['min_tricks_learned']) * 100)
            progress_items.append({
                'name': 'Tricks Learned',
                'current': tricks,
                'required': requirements['min_tricks_learned'],
                'progress': trick_progress,
                'met': tricks >= requirements['min_tricks_learned']
            })
            total_progress += trick_progress
            num_requirements += 1

        # Calculate overall progress
        overall_progress = total_progress / num_requirements if num_requirements > 0 else 0

        can_evolve, _, reason = self.check_evolution_eligibility(creature_stats)

        return {
            'current_stage': self.current_stage,
            'next_stage': next_stage,
            'can_evolve': can_evolve,
            'progress_percent': overall_progress,
            'requirements': progress_items,
            'message': reason
        }

    def auto_check_evolution(self, creature_stats: Dict[str, Any], trigger: EvolutionTrigger) -> Optional[Dict[str, Any]]:
        """
        Automatically check if evolution should occur based on a trigger event.

        Args:
            creature_stats: Current creature statistics
            trigger: What triggered this check

        Returns:
            Evolution result if evolution occurred, None otherwise
        """
        # Don't auto-evolve if already at max stage
        if self.current_stage == EvolutionStage.ELDER:
            return None

        # Check eligibility
        can_evolve, next_stage, reason = self.check_evolution_eligibility(creature_stats)

        if can_evolve and not self.evolution_ready:
            # Mark as ready but don't auto-evolve yet
            # This gives the user a chance to see the evolution animation
            self.evolution_ready = True
            return {
                'ready': True,
                'next_stage': next_stage,
                'evolved': False,
                'message': f"Your pet is ready to evolve to {next_stage.value.title()}!"
            }

        return None

    def force_evolve(self) -> Tuple[bool, str]:
        """
        Force evolution if ready (for manual evolution triggers).

        Returns:
            Tuple of (success, message)
        """
        if not self.evolution_ready:
            return False, "Evolution not ready yet"

        if self.current_stage == EvolutionStage.ELDER:
            return False, "Already at maximum stage"

        # Determine next stage
        stage_progression = {
            EvolutionStage.BABY: EvolutionStage.JUVENILE,
            EvolutionStage.JUVENILE: EvolutionStage.ADULT,
            EvolutionStage.ADULT: EvolutionStage.ELDER
        }
        next_stage = stage_progression[self.current_stage]

        old_stage = self.current_stage
        self.current_stage = next_stage
        self.evolution_ready = False

        # Record evolution
        evolution_event = {
            'timestamp': time.time(),
            'from_stage': old_stage,
            'to_stage': next_stage,
            'forced': True
        }
        self.evolution_history.append(evolution_event)

        return True, f"Evolved from {old_stage.value.title()} to {next_stage.value.title()}!"

    def get_stage_name(self) -> str:
        """Get the display name of the current stage."""
        return self.current_stage.value.title()

    def get_evolution_history(self) -> list:
        """Get the complete evolution history."""
        return self.evolution_history.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize evolution system state."""
        return {
            'current_stage': self.current_stage.value,
            'evolution_history': self.evolution_history,
            'evolution_ready': self.evolution_ready,
            'evolution_delayed': self.evolution_delayed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvolutionSystem':
        """Deserialize evolution system state."""
        stage = EvolutionStage(data.get('current_stage', 'baby'))
        system = cls(current_stage=stage)

        system.evolution_history = data.get('evolution_history', [])
        system.evolution_ready = data.get('evolution_ready', False)
        system.evolution_delayed = data.get('evolution_delayed', False)

        return system
