"""
Phase 15: Autonomous Behavior System

Makes pets automatically interact with furniture based on needs.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class BehaviorPriority(Enum):
    """Priority levels for behaviors."""
    CRITICAL = "critical"      # Urgent needs (hunger < 20)
    HIGH = "high"              # Important needs (hunger < 40)
    MEDIUM = "medium"          # Moderate needs (hunger < 60)
    LOW = "low"                # Minor needs (hunger < 80)
    IDLE = "idle"              # No pressing needs


class BehaviorDecision:
    """Represents a behavior decision."""

    def __init__(self, action: str, furniture_id: Optional[str] = None,
                 priority: BehaviorPriority = BehaviorPriority.LOW):
        """
        Initialize behavior decision.

        Args:
            action: Action to perform
            furniture_id: Furniture to interact with (if applicable)
            priority: Priority level
        """
        self.action = action
        self.furniture_id = furniture_id
        self.priority = priority
        self.motivation = 0.0      # 0-100
        self.timestamp = time.time()


class AutonomousBehavior:
    """
    Manages autonomous pet behavior and furniture usage.

    Features:
    - Evaluate pet needs
    - Decide which furniture to use
    - Priority-based decision making
    - Automatic interaction triggering
    - Behavior patterns
    - Randomness for personality
    """

    def __init__(self):
        """Initialize autonomous behavior system."""
        # Behavior settings
        self.enabled = True
        self.decision_interval = 5.0    # seconds between decisions
        self.last_decision_time = 0.0

        # Need thresholds (when to trigger automatic behavior)
        self.critical_threshold = 20    # Critical need level
        self.high_threshold = 40        # High priority threshold
        self.medium_threshold = 60      # Medium priority threshold
        self.low_threshold = 80         # Low priority threshold

        # Behavior weights (how much each need influences behavior)
        self.need_weights = {
            'hunger': 1.5,              # Hunger is high priority
            'energy': 1.2,              # Energy is important
            'happiness': 1.0,           # Happiness is standard
            'boredom': 0.8,             # Boredom is lower priority
            'stress': 1.1,              # Stress is fairly important
            'cleanliness': 0.7          # Cleanliness is lower priority
        }

        # Interaction preferences (furniture type -> base motivation)
        self.interaction_preferences = {
            'bed': 30,
            'food_bowl': 40,
            'toy_box': 20,
            'scratching': 15,
            'perch': 10,
            'seating': 12
        }

        # Randomness factor (0-1, higher = more random)
        self.randomness = 0.3

        # Statistics
        self.total_decisions = 0
        self.autonomous_interactions = 0
        self.decisions_by_priority: Dict[str, int] = {}

        # Current decision
        self.current_decision: Optional[BehaviorDecision] = None

    def evaluate_needs(self, pet_stats: Dict[str, float]) -> Dict[str, BehaviorPriority]:
        """
        Evaluate pet needs and assign priorities.

        Args:
            pet_stats: Pet statistics (hunger, energy, etc.)

        Returns:
            Dictionary of need priorities
        """
        priorities = {}

        for need, value in pet_stats.items():
            if need not in self.need_weights:
                continue

            # Invert for needs that should be low (hunger, stress)
            # Higher values are better for happiness, energy
            if need in ['hunger', 'stress', 'boredom']:
                # For these, low values are bad
                need_level = 100 - value
            else:
                # For these, high values are good, so invert
                need_level = value

            # Assign priority based on need level
            if need_level < self.critical_threshold:
                priorities[need] = BehaviorPriority.CRITICAL
            elif need_level < self.high_threshold:
                priorities[need] = BehaviorPriority.HIGH
            elif need_level < self.medium_threshold:
                priorities[need] = BehaviorPriority.MEDIUM
            elif need_level < self.low_threshold:
                priorities[need] = BehaviorPriority.LOW
            else:
                priorities[need] = BehaviorPriority.IDLE

        return priorities

    def calculate_motivation(self, furniture_category: str, pet_stats: Dict[str, float],
                           interaction_effects: Dict[str, float]) -> float:
        """
        Calculate motivation to interact with furniture.

        Args:
            furniture_category: Category of furniture
            pet_stats: Current pet statistics
            interaction_effects: Effects the interaction would have

        Returns:
            Motivation score (0-100)
        """
        # Base motivation from preferences
        motivation = self.interaction_preferences.get(furniture_category, 10)

        # Add motivation based on needs that the interaction addresses
        for stat, effect in interaction_effects.items():
            if stat in pet_stats and stat in self.need_weights:
                current_value = pet_stats[stat]
                weight = self.need_weights[stat]

                # Calculate need urgency
                if stat in ['hunger', 'stress', 'boredom']:
                    # Higher current value = less need for action
                    if effect < 0:  # Negative effect reduces the stat (good for hunger/stress)
                        need_urgency = current_value * abs(effect) * 0.1
                        motivation += need_urgency * weight
                    else:  # Positive effect increases stat (bad for hunger/stress)
                        need_urgency = (100 - current_value) * effect * 0.05
                        motivation -= need_urgency * weight
                else:
                    # For positive stats (happiness, energy), low values = high need
                    if effect > 0:  # Positive effect is good
                        need_urgency = (100 - current_value) * effect * 0.1
                        motivation += need_urgency * weight
                    else:  # Negative effect is bad
                        need_urgency = current_value * abs(effect) * 0.05
                        motivation -= need_urgency * weight

        # Add randomness
        if self.randomness > 0:
            random_factor = random.uniform(-self.randomness, self.randomness) * motivation
            motivation += random_factor

        return max(0, min(100, motivation))

    def make_decision(self, pet_stats: Dict[str, float],
                     available_furniture: List[Tuple[str, str, Dict[str, float]]],
                     pet_position: Tuple[float, float]) -> Optional[BehaviorDecision]:
        """
        Make a behavior decision based on current state.

        Args:
            pet_stats: Current pet statistics
            available_furniture: List of (furniture_id, category, position, effects) tuples
            pet_position: Pet's current position

        Returns:
            BehaviorDecision or None
        """
        if not self.enabled:
            return None

        # Check if enough time has passed since last decision
        current_time = time.time()
        if current_time - self.last_decision_time < self.decision_interval:
            return self.current_decision

        self.last_decision_time = current_time

        # Evaluate needs
        need_priorities = self.evaluate_needs(pet_stats)

        # Find highest priority need
        highest_priority = BehaviorPriority.IDLE
        for priority in need_priorities.values():
            if self._priority_value(priority) > self._priority_value(highest_priority):
                highest_priority = priority

        # If all needs are satisfied, random idle behavior
        if highest_priority == BehaviorPriority.IDLE:
            # Sometimes do something fun anyway
            if random.random() < 0.3:
                highest_priority = BehaviorPriority.LOW
            else:
                self.current_decision = BehaviorDecision("wander", priority=BehaviorPriority.IDLE)
                self.total_decisions += 1
                return self.current_decision

        # Evaluate each furniture option
        best_motivation = 0.0
        best_furniture = None
        best_category = None

        for furniture_id, category, position, effects in available_furniture:
            # Calculate distance
            distance = ((pet_position[0] - position[0]) ** 2 +
                       (pet_position[1] - position[1]) ** 2) ** 0.5

            # Calculate motivation
            motivation = self.calculate_motivation(category, pet_stats, effects)

            # Reduce motivation based on distance
            distance_penalty = min(20, distance * 2)
            motivation -= distance_penalty

            if motivation > best_motivation:
                best_motivation = motivation
                best_furniture = furniture_id
                best_category = category

        # Make decision
        if best_furniture and best_motivation > 30:  # Threshold to act
            decision = BehaviorDecision(
                action="interact",
                furniture_id=best_furniture,
                priority=highest_priority
            )
            decision.motivation = best_motivation
        else:
            # No good furniture option, wander or idle
            decision = BehaviorDecision(
                action="wander",
                priority=BehaviorPriority.LOW
            )
            decision.motivation = 10

        self.current_decision = decision
        self.total_decisions += 1

        # Track statistics
        priority_key = decision.priority.value
        self.decisions_by_priority[priority_key] = \
            self.decisions_by_priority.get(priority_key, 0) + 1

        if decision.action == "interact":
            self.autonomous_interactions += 1

        return decision

    def _priority_value(self, priority: BehaviorPriority) -> int:
        """Get numeric value for priority."""
        values = {
            BehaviorPriority.CRITICAL: 4,
            BehaviorPriority.HIGH: 3,
            BehaviorPriority.MEDIUM: 2,
            BehaviorPriority.LOW: 1,
            BehaviorPriority.IDLE: 0
        }
        return values.get(priority, 0)

    def should_interrupt_for_critical(self, pet_stats: Dict[str, float]) -> bool:
        """
        Check if pet should interrupt current action for critical need.

        Args:
            pet_stats: Current pet statistics

        Returns:
            True if should interrupt
        """
        priorities = self.evaluate_needs(pet_stats)
        return BehaviorPriority.CRITICAL in priorities.values()

    def get_idle_behavior(self) -> str:
        """Get random idle behavior when no furniture interaction needed."""
        behaviors = [
            "wander",
            "sit",
            "stretch",
            "look_around",
            "groom_self",
            "play_solo"
        ]
        return random.choice(behaviors)

    def adjust_randomness(self, randomness: float):
        """
        Adjust randomness factor.

        Args:
            randomness: Randomness level (0-1)
        """
        self.randomness = max(0.0, min(1.0, randomness))

    def set_need_threshold(self, threshold_type: str, value: int):
        """
        Set need threshold.

        Args:
            threshold_type: Type of threshold (critical, high, medium, low)
            value: Threshold value (0-100)
        """
        value = max(0, min(100, value))

        if threshold_type == "critical":
            self.critical_threshold = value
        elif threshold_type == "high":
            self.high_threshold = value
        elif threshold_type == "medium":
            self.medium_threshold = value
        elif threshold_type == "low":
            self.low_threshold = value

    def get_statistics(self) -> Dict[str, Any]:
        """Get behavior statistics."""
        return {
            'enabled': self.enabled,
            'total_decisions': self.total_decisions,
            'autonomous_interactions': self.autonomous_interactions,
            'decisions_by_priority': self.decisions_by_priority,
            'randomness': self.randomness,
            'thresholds': {
                'critical': self.critical_threshold,
                'high': self.high_threshold,
                'medium': self.medium_threshold,
                'low': self.low_threshold
            },
            'interaction_rate': (
                (self.autonomous_interactions / self.total_decisions * 100)
                if self.total_decisions > 0 else 0.0
            )
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'enabled': self.enabled,
            'decision_interval': self.decision_interval,
            'last_decision_time': self.last_decision_time,
            'critical_threshold': self.critical_threshold,
            'high_threshold': self.high_threshold,
            'medium_threshold': self.medium_threshold,
            'low_threshold': self.low_threshold,
            'need_weights': self.need_weights,
            'interaction_preferences': self.interaction_preferences,
            'randomness': self.randomness,
            'total_decisions': self.total_decisions,
            'autonomous_interactions': self.autonomous_interactions,
            'decisions_by_priority': self.decisions_by_priority
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutonomousBehavior':
        """Deserialize from dictionary."""
        behavior = cls()

        behavior.enabled = data.get('enabled', True)
        behavior.decision_interval = data.get('decision_interval', 5.0)
        behavior.last_decision_time = data.get('last_decision_time', 0.0)
        behavior.critical_threshold = data.get('critical_threshold', 20)
        behavior.high_threshold = data.get('high_threshold', 40)
        behavior.medium_threshold = data.get('medium_threshold', 60)
        behavior.low_threshold = data.get('low_threshold', 80)
        behavior.need_weights = data.get('need_weights', behavior.need_weights)
        behavior.interaction_preferences = data.get('interaction_preferences',
                                                    behavior.interaction_preferences)
        behavior.randomness = data.get('randomness', 0.3)
        behavior.total_decisions = data.get('total_decisions', 0)
        behavior.autonomous_interactions = data.get('autonomous_interactions', 0)
        behavior.decisions_by_priority = data.get('decisions_by_priority', {})

        return behavior
