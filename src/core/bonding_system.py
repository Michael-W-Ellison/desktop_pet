"""
Bonding System for Desktop Pet

Manages the emotional bond between owner and pet with progressive relationship levels.
Bond strengthens through positive interactions and weakens with neglect.
"""
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
import time
import numpy as np


class BondLevel(Enum):
    """Progressive bonding levels from stranger to best friend."""
    STRANGER = "stranger"                  # 0-20 bond
    ACQUAINTANCE = "acquaintance"          # 20-40 bond
    FRIEND = "friend"                      # 40-60 bond
    CLOSE_FRIEND = "close_friend"          # 60-80 bond
    BEST_FRIEND = "best_friend"            # 80-100 bond


class BondingSystem:
    """
    Manages the emotional bond between owner and pet.

    Bond progression:
    - Stranger (0-20): Just met, cautious, doesn't know you
    - Acquaintance (20-40): Getting comfortable, occasional affection
    - Friend (40-60): Trusts you, seeks interaction
    - Close Friend (60-80): Very attached, shows clear preferences
    - Best Friend (80-100): Deep bond, separation anxiety, excitement on return

    Bond is affected by:
    - Positive interactions (feeding, playing, petting)
    - Consistency of care
    - Time spent together
    - Responding to needs
    - Neglect causes bond decay
    """

    def __init__(self, initial_bond: float = 0.0):
        """
        Initialize bonding system.

        Args:
            initial_bond: Starting bond value (0-100)
        """
        self.bond = max(0, min(100, initial_bond))
        self.last_interaction_time = time.time()
        self.last_presence_check = time.time()
        self.total_time_together = 0.0  # Total seconds spent together
        self.consecutive_days_cared = 0
        self.bond_history = []  # Track bond changes over time

        # Tracking for bonding mechanics
        self.times_fed = 0
        self.times_played = 0
        self.times_petted = 0
        self.times_ignored_needs = 0
        self.longest_absence = 0.0

        # Special bonding moments
        self.first_time_called_by_name = None
        self.bond_milestones_reached = set()

    def get_bond_level(self) -> BondLevel:
        """
        Get current bond level based on bond value.

        Returns:
            BondLevel enum
        """
        if self.bond >= 80:
            return BondLevel.BEST_FRIEND
        elif self.bond >= 60:
            return BondLevel.CLOSE_FRIEND
        elif self.bond >= 40:
            return BondLevel.FRIEND
        elif self.bond >= 20:
            return BondLevel.ACQUAINTANCE
        else:
            return BondLevel.STRANGER

    def get_bond_description(self) -> str:
        """Get a description of the current bond level."""
        descriptions = {
            BondLevel.STRANGER: "Still getting to know you. Acts cautious and reserved.",
            BondLevel.ACQUAINTANCE: "Starting to warm up. Occasional displays of affection.",
            BondLevel.FRIEND: "Trusts you and enjoys your company. Seeks interaction.",
            BondLevel.CLOSE_FRIEND: "Very attached and affectionate. Shows clear preferences.",
            BondLevel.BEST_FRIEND: "Deep emotional bond. Misses you when gone, ecstatic when you return."
        }
        return descriptions.get(self.get_bond_level(), "Unknown bond level")

    def add_bond(self, amount: float, reason: str = "interaction"):
        """
        Increase bond value.

        Args:
            amount: Amount to increase (0-100 scale)
            reason: Why bond increased
        """
        old_level = self.get_bond_level()
        old_bond = self.bond

        self.bond = min(100, self.bond + amount)
        self.last_interaction_time = time.time()

        # Record bond change
        self.bond_history.append({
            'timestamp': time.time(),
            'change': self.bond - old_bond,
            'reason': reason,
            'new_bond': self.bond
        })

        # Check for level up
        new_level = self.get_bond_level()
        if new_level != old_level:
            self._on_bond_level_up(old_level, new_level)

    def reduce_bond(self, amount: float, reason: str = "neglect"):
        """
        Decrease bond value (from neglect or negative experiences).

        Args:
            amount: Amount to decrease
            reason: Why bond decreased
        """
        old_bond = self.bond
        self.bond = max(0, self.bond - amount)

        # Record bond change
        self.bond_history.append({
            'timestamp': time.time(),
            'change': self.bond - old_bond,
            'reason': reason,
            'new_bond': self.bond
        })

    def _on_bond_level_up(self, old_level: BondLevel, new_level: BondLevel):
        """Handle reaching a new bond level."""
        milestone = f"reached_{new_level.value}"
        if milestone not in self.bond_milestones_reached:
            self.bond_milestones_reached.add(milestone)
            # This event can trigger special animations/messages

    def process_interaction(self, interaction_type: str, positive: bool = True,
                          quality: float = 1.0) -> Tuple[float, str]:
        """
        Process an interaction and update bond.

        Args:
            interaction_type: Type of interaction (feed, play, pet, etc.)
            positive: Whether interaction was positive
            quality: Quality multiplier (0-1)

        Returns:
            Tuple of (bond_gain, message)
        """
        base_bond_gains = {
            'feed': 1.5,
            'play_ball': 2.0,
            'pet': 1.0,
            'talk': 0.5,
            'call_by_name': 1.5,
            'training_success': 2.5,
            'trick_performed': 1.0,
            'give_toy': 2.0,
            'respond_to_need': 3.0,  # Responding when hungry/unhappy
        }

        bond_gain = base_bond_gains.get(interaction_type, 0.5)

        if not positive:
            bond_gain = -bond_gain * 0.5  # Negative interactions hurt less than positive help

        # Apply quality multiplier
        bond_gain *= quality

        # Bond level affects gain rate
        level = self.get_bond_level()
        if level == BondLevel.STRANGER:
            bond_gain *= 0.7  # Slower to build trust initially
        elif level == BondLevel.BEST_FRIEND:
            bond_gain *= 0.5  # Harder to increase when already at max

        # Track interaction counts
        if interaction_type == 'feed':
            self.times_fed += 1
        elif interaction_type in ['play_ball', 'give_toy']:
            self.times_played += 1
        elif interaction_type == 'pet':
            self.times_petted += 1

        # Apply bond change
        if bond_gain > 0:
            self.add_bond(bond_gain, f"{interaction_type}_positive")
            message = self._get_bond_gain_message(interaction_type, bond_gain)
        else:
            self.reduce_bond(abs(bond_gain), f"{interaction_type}_negative")
            message = "Bond decreased slightly..."

        return bond_gain, message

    def _get_bond_gain_message(self, interaction_type: str, gain: float) -> str:
        """Get a message about bond increase."""
        level = self.get_bond_level()

        if level == BondLevel.STRANGER:
            return "Seems a bit more comfortable with you."
        elif level == BondLevel.ACQUAINTANCE:
            return "Starting to enjoy your company!"
        elif level == BondLevel.FRIEND:
            return "Your bond grows stronger!"
        elif level == BondLevel.CLOSE_FRIEND:
            return "You can see the affection in its eyes!"
        else:  # BEST_FRIEND
            return "Your pet adores you!"

    def process_neglect(self, hours_neglected: float):
        """
        Process bond decay from neglect.

        Args:
            hours_neglected: How many hours since last meaningful interaction
        """
        if hours_neglected > 1:
            # Bond decays after 1 hour of no interaction
            decay_per_hour = 0.5
            total_decay = (hours_neglected - 1) * decay_per_hour

            # Stronger bonds decay slower
            level = self.get_bond_level()
            if level == BondLevel.BEST_FRIEND:
                total_decay *= 0.5  # Best friends are more forgiving
            elif level == BondLevel.CLOSE_FRIEND:
                total_decay *= 0.7

            self.reduce_bond(total_decay, "neglect")
            self.times_ignored_needs += 1

    def update_presence(self, is_present: bool, delta_time: float):
        """
        Update time tracking for presence/absence.

        Args:
            is_present: Whether owner is currently present
            delta_time: Time since last update in seconds
        """
        if is_present:
            self.total_time_together += delta_time
        else:
            # Track absence
            time_away = time.time() - self.last_presence_check
            if time_away > self.longest_absence:
                self.longest_absence = time_away

        self.last_presence_check = time.time()

    def get_bond_modifiers(self) -> Dict[str, float]:
        """
        Get behavioral modifiers based on bond level.

        Returns:
            Dictionary of modifier names to multipliers
        """
        level = self.get_bond_level()

        modifiers = {
            BondLevel.STRANGER: {
                'interaction_desire': 0.5,
                'obedience': 0.6,
                'excitement_on_interaction': 0.4,
                'separation_anxiety': 0.0,
                'trust_level': 0.3
            },
            BondLevel.ACQUAINTANCE: {
                'interaction_desire': 0.7,
                'obedience': 0.75,
                'excitement_on_interaction': 0.6,
                'separation_anxiety': 0.2,
                'trust_level': 0.5
            },
            BondLevel.FRIEND: {
                'interaction_desire': 1.0,
                'obedience': 0.9,
                'excitement_on_interaction': 0.8,
                'separation_anxiety': 0.5,
                'trust_level': 0.7
            },
            BondLevel.CLOSE_FRIEND: {
                'interaction_desire': 1.3,
                'obedience': 1.1,
                'excitement_on_interaction': 1.2,
                'separation_anxiety': 0.8,
                'trust_level': 0.9
            },
            BondLevel.BEST_FRIEND: {
                'interaction_desire': 1.5,
                'obedience': 1.3,
                'excitement_on_interaction': 1.5,
                'separation_anxiety': 1.0,
                'trust_level': 1.0
            }
        }

        return modifiers.get(level, modifiers[BondLevel.STRANGER])

    def should_show_separation_anxiety(self, hours_away: float) -> bool:
        """
        Check if pet should show separation anxiety.

        Args:
            hours_away: Hours since owner left

        Returns:
            True if should show separation anxiety
        """
        level = self.get_bond_level()

        # Only close friends and best friends get separation anxiety
        if level not in [BondLevel.CLOSE_FRIEND, BondLevel.BEST_FRIEND]:
            return False

        # Threshold depends on bond level
        threshold = 2.0 if level == BondLevel.CLOSE_FRIEND else 1.0
        return hours_away >= threshold

    def should_show_excitement_on_return(self, hours_away: float) -> Tuple[bool, float]:
        """
        Check if pet should show excitement when owner returns.

        Args:
            hours_away: Hours since owner left

        Returns:
            Tuple of (should_show_excitement, excitement_intensity)
        """
        level = self.get_bond_level()

        if level == BondLevel.STRANGER:
            return False, 0.0
        elif level == BondLevel.ACQUAINTANCE:
            # Only if gone for a while
            if hours_away > 4:
                return True, 0.3
        elif level == BondLevel.FRIEND:
            if hours_away > 2:
                return True, 0.6
        elif level == BondLevel.CLOSE_FRIEND:
            if hours_away > 1:
                return True, 0.8
        else:  # BEST_FRIEND
            if hours_away > 0.5:
                return True, 1.0

        return False, 0.0

    def get_jealousy_chance(self, attention_to_others: float) -> float:
        """
        Get chance of showing jealousy based on attention given to others.

        Args:
            attention_to_others: Amount of attention to other pets (0-1)

        Returns:
            Probability of jealousy (0-1)
        """
        level = self.get_bond_level()

        # Higher bond = more likely to get jealous
        base_jealousy = {
            BondLevel.STRANGER: 0.0,
            BondLevel.ACQUAINTANCE: 0.1,
            BondLevel.FRIEND: 0.3,
            BondLevel.CLOSE_FRIEND: 0.6,
            BondLevel.BEST_FRIEND: 0.8
        }

        jealousy_chance = base_jealousy.get(level, 0.0) * attention_to_others
        return min(1.0, jealousy_chance)

    def get_stats(self) -> Dict[str, Any]:
        """Get detailed bonding statistics."""
        return {
            'bond': self.bond,
            'level': self.get_bond_level().value,
            'description': self.get_bond_description(),
            'total_time_together_hours': self.total_time_together / 3600,
            'times_fed': self.times_fed,
            'times_played': self.times_played,
            'times_petted': self.times_petted,
            'times_ignored': self.times_ignored_needs,
            'longest_absence_hours': self.longest_absence / 3600,
            'milestones': list(self.bond_milestones_reached),
            'modifiers': self.get_bond_modifiers()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize bonding system state."""
        return {
            'bond': self.bond,
            'last_interaction_time': self.last_interaction_time,
            'last_presence_check': self.last_presence_check,
            'total_time_together': self.total_time_together,
            'consecutive_days_cared': self.consecutive_days_cared,
            'bond_history': self.bond_history[-100:],  # Keep last 100 events
            'times_fed': self.times_fed,
            'times_played': self.times_played,
            'times_petted': self.times_petted,
            'times_ignored_needs': self.times_ignored_needs,
            'longest_absence': self.longest_absence,
            'first_time_called_by_name': self.first_time_called_by_name,
            'bond_milestones_reached': list(self.bond_milestones_reached)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BondingSystem':
        """Deserialize bonding system state."""
        system = cls(initial_bond=data.get('bond', 0.0))

        system.last_interaction_time = data.get('last_interaction_time', time.time())
        system.last_presence_check = data.get('last_presence_check', time.time())
        system.total_time_together = data.get('total_time_together', 0.0)
        system.consecutive_days_cared = data.get('consecutive_days_cared', 0)
        system.bond_history = data.get('bond_history', [])
        system.times_fed = data.get('times_fed', 0)
        system.times_played = data.get('times_played', 0)
        system.times_petted = data.get('times_petted', 0)
        system.times_ignored_needs = data.get('times_ignored_needs', 0)
        system.longest_absence = data.get('longest_absence', 0.0)
        system.first_time_called_by_name = data.get('first_time_called_by_name')
        system.bond_milestones_reached = set(data.get('bond_milestones_reached', []))

        return system
