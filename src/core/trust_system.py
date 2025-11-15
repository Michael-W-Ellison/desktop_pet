"""
Trust System for Desktop Pet

Trust builds gradually through consistent positive interactions and care.
Trust affects willingness to follow commands, try new things, and respond to owner.
"""
from typing import Dict, Any, Optional, Tuple, List
import time
import numpy as np


class TrustSystem:
    """
    Manages trust buildup between owner and pet.

    Trust is distinct from bond:
    - Bond: Emotional attachment (how much pet loves you)
    - Trust: Confidence in owner (how much pet relies on you)

    Trust affects:
    - Command obedience
    - Willingness to try new tricks
    - Reaction to startling events
    - Confidence in unfamiliar situations
    - Response to being called

    Trust builds through:
    - Consistent care (feeding when hungry)
    - Gentle handling
    - Successful training
    - Not forcing uncomfortable situations
    - Being present during scary events

    Trust decays through:
    - Ignoring distress
    - Forcing unwanted interactions
    - Unpredictable behavior
    - Abandonment
    """

    def __init__(self, initial_trust: float = 0.0):
        """
        Initialize trust system.

        Args:
            initial_trust: Starting trust value (0-100)
        """
        self.trust = max(0, min(100, initial_trust))
        self.trust_history = []
        self.consistency_score = 50.0  # How consistent owner is (0-100)
        self.reliability_score = 50.0  # How reliable owner is (0-100)

        # Tracking for trust building
        self.times_responded_to_needs = 0
        self.times_ignored_distress = 0
        self.successful_commands = 0
        self.failed_commands = 0
        self.gentle_interactions = 0
        self.rough_interactions = 0

        # Time-based tracking
        self.last_care_time = time.time()
        self.care_schedule = []  # Track feeding/care times to detect patterns

    def add_trust(self, amount: float, reason: str = "positive_interaction"):
        """
        Increase trust value.

        Args:
            amount: Amount to increase
            reason: Why trust increased
        """
        old_trust = self.trust
        self.trust = min(100, self.trust + amount)

        # Record trust change
        self.trust_history.append({
            'timestamp': time.time(),
            'change': self.trust - old_trust,
            'reason': reason,
            'new_trust': self.trust
        })

    def reduce_trust(self, amount: float, reason: str = "negative_interaction"):
        """
        Decrease trust value.

        Args:
            amount: Amount to decrease
            reason: Why trust decreased
        """
        old_trust = self.trust
        self.trust = max(0, self.trust - amount)

        # Record trust change
        self.trust_history.append({
            'timestamp': time.time(),
            'change': self.trust - old_trust,
            'reason': reason,
            'new_trust': self.trust
        })

    def process_care_event(self, care_type: str, timely: bool = True):
        """
        Process a care event (feeding, playing, etc.).

        Args:
            care_type: Type of care provided
            timely: Whether care was provided in a timely manner
        """
        # Record care time for consistency tracking
        self.care_schedule.append({
            'type': care_type,
            'time': time.time(),
            'timely': timely
        })

        # Keep only recent history (last 50 events)
        if len(self.care_schedule) > 50:
            self.care_schedule = self.care_schedule[-50:]

        # Update consistency score
        self._update_consistency()

        # Trust gain depends on timeliness
        if timely:
            self.add_trust(1.0, f"timely_{care_type}")
            self.times_responded_to_needs += 1
        else:
            # Late care is better than no care
            self.add_trust(0.3, f"late_{care_type}")

    def process_command_result(self, success: bool, forced: bool = False):
        """
        Process result of a command.

        Args:
            success: Whether command was successful
            forced: Whether pet was forced to comply
        """
        if success:
            self.successful_commands += 1
            if not forced:
                self.add_trust(0.5, "successful_command")
            else:
                # Forcing compliance damages trust
                self.reduce_trust(1.0, "forced_command")
        else:
            self.failed_commands += 1
            # Failed commands don't hurt trust much
            self.reduce_trust(0.1, "failed_command")

        self._update_reliability()

    def process_interaction_quality(self, gentle: bool):
        """
        Process interaction quality (gentle vs rough).

        Args:
            gentle: Whether interaction was gentle
        """
        if gentle:
            self.gentle_interactions += 1
            self.add_trust(0.3, "gentle_interaction")
        else:
            self.rough_interactions += 1
            self.reduce_trust(0.8, "rough_interaction")

    def process_distress_response(self, responded: bool):
        """
        Process owner's response to pet distress.

        Args:
            responded: Whether owner responded to distress
        """
        if responded:
            self.times_responded_to_needs += 1
            self.add_trust(2.0, "responded_to_distress")
        else:
            self.times_ignored_distress += 1
            self.reduce_trust(3.0, "ignored_distress")

    def process_abandonment(self, hours_gone: float):
        """
        Process time owner was gone.

        Args:
            hours_gone: Hours owner was absent
        """
        if hours_gone > 12:
            # Long abandonment damages trust
            damage = (hours_gone - 12) * 0.5
            self.reduce_trust(min(damage, 10), "long_absence")

    def _update_consistency(self):
        """Update consistency score based on care patterns."""
        if len(self.care_schedule) < 3:
            return

        # Check if care happens at regular intervals
        recent_times = [event['time'] for event in self.care_schedule[-10:]]
        if len(recent_times) >= 3:
            intervals = []
            for i in range(1, len(recent_times)):
                intervals.append(recent_times[i] - recent_times[i-1])

            # Check interval consistency (lower variance = more consistent)
            if len(intervals) > 0:
                mean_interval = np.mean(intervals)
                std_interval = np.std(intervals)

                # Calculate consistency (0-100)
                if mean_interval > 0:
                    coefficient_of_variation = std_interval / mean_interval
                    # Lower CV = higher consistency
                    new_consistency = max(0, min(100, 100 - (coefficient_of_variation * 50)))

                    # Smooth the consistency score
                    self.consistency_score = self.consistency_score * 0.8 + new_consistency * 0.2

    def _update_reliability(self):
        """Update reliability score based on command success rate."""
        total_commands = self.successful_commands + self.failed_commands
        if total_commands > 0:
            success_rate = self.successful_commands / total_commands
            # Convert to 0-100 scale
            new_reliability = success_rate * 100

            # Smooth the reliability score
            self.reliability_score = self.reliability_score * 0.8 + new_reliability * 0.2

    def get_trust_level_description(self) -> str:
        """Get description of current trust level."""
        if self.trust >= 80:
            return "Complete Trust - Will follow you anywhere and try anything"
        elif self.trust >= 60:
            return "High Trust - Confident in your care and guidance"
        elif self.trust >= 40:
            return "Moderate Trust - Generally trusts you but still cautious"
        elif self.trust >= 20:
            return "Low Trust - Uncertain about you, needs reassurance"
        else:
            return "Very Low Trust - Doesn't trust you yet, very hesitant"

    def get_command_obedience_modifier(self) -> float:
        """
        Get modifier for command obedience based on trust.

        Returns:
            Multiplier for command success (0.5 to 1.5)
        """
        # Trust affects how likely pet is to obey
        return 0.5 + (self.trust / 100)

    def get_fear_response_modifier(self) -> float:
        """
        Get modifier for fear responses.

        Returns:
            Multiplier for fear intensity (0.5 to 1.5)
        """
        # Higher trust = less fear
        return 1.5 - (self.trust / 100)

    def should_try_new_trick(self, trick_difficulty: float) -> Tuple[bool, float]:
        """
        Determine if pet will attempt a new trick.

        Args:
            trick_difficulty: Difficulty of the trick (0-1)

        Returns:
            Tuple of (will_try, confidence)
        """
        # Trust affects willingness to try new things
        base_confidence = self.trust / 100

        # Adjust for difficulty
        confidence = base_confidence * (1.0 - trick_difficulty * 0.5)

        # Will try if confidence is high enough
        will_try = confidence > 0.3 and np.random.random() < confidence

        return will_try, confidence

    def get_trust_modifiers(self) -> Dict[str, float]:
        """
        Get behavioral modifiers based on trust level.

        Returns:
            Dictionary of modifier names to multipliers
        """
        trust_ratio = self.trust / 100  # 0-1 scale

        return {
            'command_obedience': 0.5 + trust_ratio,  # 0.5x to 1.5x
            'fear_response': 1.5 - trust_ratio,      # 1.5x to 0.5x
            'exploration_willingness': 0.3 + trust_ratio * 0.7,  # 0.3x to 1.0x
            'separation_anxiety': 0.2 + trust_ratio * 0.8,  # 0.2x to 1.0x
            'new_trick_willingness': 0.4 + trust_ratio * 0.6,  # 0.4x to 1.0x
            'confidence_level': trust_ratio,  # 0 to 1
            'consistency_bonus': self.consistency_score / 100,
            'reliability_bonus': self.reliability_score / 100
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed trust statistics."""
        total_commands = self.successful_commands + self.failed_commands
        success_rate = (self.successful_commands / total_commands * 100) if total_commands > 0 else 0

        total_interactions = self.gentle_interactions + self.rough_interactions
        gentleness_rate = (self.gentle_interactions / total_interactions * 100) if total_interactions > 0 else 0

        return {
            'trust': self.trust,
            'description': self.get_trust_level_description(),
            'consistency_score': self.consistency_score,
            'reliability_score': self.reliability_score,
            'times_responded_to_needs': self.times_responded_to_needs,
            'times_ignored_distress': self.times_ignored_distress,
            'command_success_rate': success_rate,
            'gentleness_rate': gentleness_rate,
            'modifiers': self.get_trust_modifiers()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize trust system state."""
        return {
            'trust': self.trust,
            'trust_history': self.trust_history[-100:],  # Last 100 events
            'consistency_score': self.consistency_score,
            'reliability_score': self.reliability_score,
            'times_responded_to_needs': self.times_responded_to_needs,
            'times_ignored_distress': self.times_ignored_distress,
            'successful_commands': self.successful_commands,
            'failed_commands': self.failed_commands,
            'gentle_interactions': self.gentle_interactions,
            'rough_interactions': self.rough_interactions,
            'last_care_time': self.last_care_time,
            'care_schedule': self.care_schedule
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrustSystem':
        """Deserialize trust system state."""
        system = cls(initial_trust=data.get('trust', 0.0))

        system.trust_history = data.get('trust_history', [])
        system.consistency_score = data.get('consistency_score', 50.0)
        system.reliability_score = data.get('reliability_score', 50.0)
        system.times_responded_to_needs = data.get('times_responded_to_needs', 0)
        system.times_ignored_distress = data.get('times_ignored_distress', 0)
        system.successful_commands = data.get('successful_commands', 0)
        system.failed_commands = data.get('failed_commands', 0)
        system.gentle_interactions = data.get('gentle_interactions', 0)
        system.rough_interactions = data.get('rough_interactions', 0)
        system.last_care_time = data.get('last_care_time', time.time())
        system.care_schedule = data.get('care_schedule', [])

        return system
