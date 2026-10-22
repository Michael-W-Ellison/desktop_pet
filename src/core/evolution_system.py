"""
Evolution System for Desktop Pal

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

    Evolution progression is driven by how settled the pet's neural networks have
    become; at ADVANCED/EXPERT every network must have settled (see
    EVOLUTION_REQUIREMENTS in config):
    - BABY: starting stage
    - JUVENILE: decisions 25%+ settled
    - ADULT: decisions 50%+ settled
    - ELDER: decisions 75%+ settled; learning stops and no new tricks can be taught
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
                - decision_stability: How settled the neural networks are (0-1)

        Returns:
            Tuple of (can_evolve, next_stage, reason)
        """
        # Already at max stage
        if self.current_stage == EvolutionStage.ELDER:
            return False, None, "Already at maximum evolution stage (Elder)"

        next_stage = self._next_stage()
        required = EVOLUTION_REQUIREMENTS[next_stage]['min_decision_stability']
        stability = creature_stats.get('decision_stability', 0.0)

        if stability < required:
            return False, None, (f"Behavior still developing - decisions {stability:.0%} settled, "
                                 f"needs {required:.0%}")

        return True, next_stage, f"Ready to evolve to {next_stage.value.title()}!"

    def _next_stage(self) -> EvolutionStage:
        """Get the stage after the current one (current stage must not be Elder)."""
        stage_progression = {
            EvolutionStage.BABY: EvolutionStage.JUVENILE,
            EvolutionStage.JUVENILE: EvolutionStage.ADULT,
            EvolutionStage.ADULT: EvolutionStage.ELDER
        }
        return stage_progression[self.current_stage]

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
            'from_stage': old_stage.value,
            'to_stage': next_stage.value,
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

        next_stage = self._next_stage()
        required = EVOLUTION_REQUIREMENTS[next_stage]['min_decision_stability']
        stability = creature_stats.get('decision_stability', 0.0)
        progress = min(100, (stability / required) * 100) if required > 0 else 100

        can_evolve, _, reason = self.check_evolution_eligibility(creature_stats)

        return {
            'current_stage': self.current_stage,
            'next_stage': next_stage,
            'can_evolve': can_evolve,
            'progress_percent': progress,
            'requirements': [{
                'name': 'Decision Stability',
                'current': stability,
                'required': required,
                'progress': progress,
                'met': stability >= required
            }],
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

        next_stage = self._next_stage()

        old_stage = self.current_stage
        self.current_stage = next_stage
        self.evolution_ready = False

        # Record evolution
        evolution_event = {
            'timestamp': time.time(),
            'from_stage': old_stage.value,
            'to_stage': next_stage.value,
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
