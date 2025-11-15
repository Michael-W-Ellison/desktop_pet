"""
Emotional States System for Desktop Pet

Manages complex emotional states including jealousy, separation anxiety, and excitement.
These emotional states are influenced by bonding level and recent experiences.
"""
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
import time
import numpy as np


class EmotionalState(Enum):
    """Complex emotional states beyond basic moods."""
    JEALOUS = "jealous"                    # Seeing attention go to others
    SEPARATION_ANXIETY = "separation_anxiety"  # Owner gone too long
    EXCITED_RETURN = "excited_return"      # Owner just came back
    LONGING = "longing"                    # Missing owner
    POSSESSIVE = "possessive"              # Protecting relationship
    INSECURE = "insecure"                  # Worried about relationship
    CONTENT = "content"                    # Happy with current state
    YEARNING = "yearning"                  # Wanting more attention


class EmotionalStateManager:
    """
    Manages complex emotional states that emerge from bonding and experiences.

    Emotional states are temporary but influenced by:
    - Bond level
    - Trust level
    - Recent experiences
    - Personality
    - Time patterns
    """

    def __init__(self):
        """Initialize emotional state manager."""
        self.current_states = {}  # {state: (intensity, expires_at)}
        self.state_history = []
        self.last_owner_seen = time.time()
        self.owner_present = True

        # Jealousy tracking
        self.attention_to_others_score = 0.0  # How much attention others got
        self.last_jealousy_trigger = None

        # Separation tracking
        self.time_owner_left = None
        self.times_experienced_separation = 0
        self.longest_separation = 0.0

        # Excitement tracking
        self.last_reunion = None
        self.reunion_excitement_level = 0.0

    def set_emotional_state(self, state: EmotionalState, intensity: float, duration: float = 300):
        """
        Set an emotional state.

        Args:
            state: The emotional state
            intensity: Intensity of the state (0-1)
            duration: How long state lasts in seconds
        """
        expires_at = time.time() + duration
        self.current_states[state] = (intensity, expires_at)

        # Record in history
        self.state_history.append({
            'state': state.value,
            'intensity': intensity,
            'timestamp': time.time()
        })

        # Keep history manageable
        if len(self.state_history) > 100:
            self.state_history = self.state_history[-100:]

    def remove_emotional_state(self, state: EmotionalState):
        """Remove an emotional state."""
        if state in self.current_states:
            del self.current_states[state]

    def has_state(self, state: EmotionalState) -> bool:
        """Check if currently in an emotional state."""
        if state not in self.current_states:
            return False

        # Check if expired
        intensity, expires_at = self.current_states[state]
        if time.time() > expires_at:
            del self.current_states[state]
            return False

        return True

    def get_state_intensity(self, state: EmotionalState) -> float:
        """Get intensity of a state (0 if not active)."""
        if not self.has_state(state):
            return 0.0

        intensity, _ = self.current_states[state]
        return intensity

    def update(self, delta_time: float):
        """
        Update emotional states (remove expired ones).

        Args:
            delta_time: Time since last update in seconds
        """
        current_time = time.time()
        expired_states = []

        for state, (intensity, expires_at) in self.current_states.items():
            if current_time > expires_at:
                expired_states.append(state)

        for state in expired_states:
            del self.current_states[state]

    def trigger_jealousy(self, bond_level: float, trigger_intensity: float = 0.5):
        """
        Trigger jealousy emotional state.

        Args:
            bond_level: Current bond level (0-100)
            trigger_intensity: How much to trigger by
        """
        # Higher bond = stronger jealousy
        jealousy_intensity = (bond_level / 100) * trigger_intensity

        if jealousy_intensity > 0.3:
            # Duration depends on intensity
            duration = 300 + (jealousy_intensity * 600)  # 5-15 minutes

            self.set_emotional_state(
                EmotionalState.JEALOUS,
                jealousy_intensity,
                duration
            )

            self.last_jealousy_trigger = time.time()
            self.attention_to_others_score += trigger_intensity

    def process_attention_to_other(self, amount: float = 0.1):
        """
        Process attention being given to another pet.

        Args:
            amount: Amount of attention (0-1)
        """
        self.attention_to_others_score = min(1.0, self.attention_to_others_score + amount)

    def reset_attention_tracking(self):
        """Reset attention to others tracking after receiving attention."""
        # Gradually reduce, not instant reset
        self.attention_to_others_score *= 0.5

    def trigger_separation_anxiety(self, bond_level: float, hours_away: float):
        """
        Trigger separation anxiety.

        Args:
            bond_level: Current bond level (0-100)
            hours_away: How many hours owner has been gone
        """
        # Need strong bond for separation anxiety
        if bond_level < 60:
            return

        # Intensity based on bond and time away
        base_intensity = (bond_level - 60) / 40  # 0-1 for bonds 60-100
        time_multiplier = min(1.5, hours_away / 4)  # Caps at 4 hours
        anxiety_intensity = min(1.0, base_intensity * time_multiplier)

        if anxiety_intensity > 0.4:
            self.set_emotional_state(
                EmotionalState.SEPARATION_ANXIETY,
                anxiety_intensity,
                duration=3600  # Lasts 1 hour
            )

            self.times_experienced_separation += 1

    def trigger_excited_return(self, bond_level: float, hours_away: float):
        """
        Trigger excitement when owner returns.

        Args:
            bond_level: Current bond level (0-100)
            hours_away: How many hours owner was gone
        """
        # Calculate excitement
        bond_factor = bond_level / 100
        time_factor = min(1.0, hours_away / 6)  # Max excitement at 6+ hours
        excitement = bond_factor * (0.5 + time_factor * 0.5)

        if excitement > 0.3:
            # Duration based on how long they were gone
            duration = min(900, 300 + hours_away * 60)  # 5-15 minutes

            self.set_emotional_state(
                EmotionalState.EXCITED_RETURN,
                excitement,
                duration
            )

            self.reunion_excitement_level = excitement
            self.last_reunion = time.time()

    def trigger_longing(self, bond_level: float, minutes_away: float):
        """
        Trigger longing for owner.

        Args:
            bond_level: Current bond level (0-100)
            minutes_away: Minutes since owner left
        """
        if bond_level < 40:
            return

        # Longing starts after owner is gone a while
        if minutes_away > 30:
            longing_intensity = (bond_level / 100) * min(1.0, (minutes_away - 30) / 60)

            if longing_intensity > 0.3:
                self.set_emotional_state(
                    EmotionalState.LONGING,
                    longing_intensity,
                    duration=1800  # 30 minutes
                )

    def trigger_possessiveness(self, bond_level: float, threat_level: float):
        """
        Trigger possessive behavior.

        Args:
            bond_level: Current bond level (0-100)
            threat_level: Perceived threat to relationship (0-1)
        """
        if bond_level < 60:
            return

        possessive_intensity = (bond_level / 100) * threat_level

        if possessive_intensity > 0.4:
            self.set_emotional_state(
                EmotionalState.POSSESSIVE,
                possessive_intensity,
                duration=600  # 10 minutes
            )

    def trigger_insecurity(self, bond_level: float, trust_level: float):
        """
        Trigger insecurity about relationship.

        Args:
            bond_level: Current bond level (0-100)
            trust_level: Current trust level (0-100)
        """
        # Insecurity when bond is high but trust is low
        if bond_level > 50 and trust_level < 40:
            insecurity = (bond_level - trust_level) / 100

            if insecurity > 0.3:
                self.set_emotional_state(
                    EmotionalState.INSECURE,
                    insecurity,
                    duration=900  # 15 minutes
                )

    def set_owner_presence(self, present: bool, bond_level: float = 50, trust_level: float = 50):
        """
        Update owner presence and trigger appropriate states.

        Args:
            present: Whether owner is currently present
            bond_level: Current bond level
            trust_level: Current trust level
        """
        was_present = self.owner_present
        self.owner_present = present

        if present and not was_present:
            # Owner just returned!
            if self.time_owner_left:
                hours_away = (time.time() - self.time_owner_left) / 3600
                self.trigger_excited_return(bond_level, hours_away)

                # Update longest separation
                time_away = time.time() - self.time_owner_left
                if time_away > self.longest_separation:
                    self.longest_separation = time_away

                self.time_owner_left = None

            self.last_owner_seen = time.time()

        elif not present and was_present:
            # Owner just left
            self.time_owner_left = time.time()

    def get_current_states(self) -> Dict[str, float]:
        """
        Get all currently active emotional states.

        Returns:
            Dictionary of {state_name: intensity}
        """
        states = {}
        for state in list(self.current_states.keys()):
            if self.has_state(state):
                states[state.value] = self.get_state_intensity(state)

        return states

    def get_dominant_state(self) -> Optional[Tuple[EmotionalState, float]]:
        """
        Get the most intense current emotional state.

        Returns:
            Tuple of (state, intensity) or None
        """
        if not self.current_states:
            return None

        max_intensity = 0
        dominant_state = None

        for state in self.current_states:
            if self.has_state(state):
                intensity = self.get_state_intensity(state)
                if intensity > max_intensity:
                    max_intensity = intensity
                    dominant_state = state

        if dominant_state:
            return dominant_state, max_intensity

        return None

    def get_behavioral_modifiers(self) -> Dict[str, float]:
        """
        Get behavioral modifiers based on current emotional states.

        Returns:
            Dictionary of behavior modifiers
        """
        modifiers = {
            'happiness_modifier': 1.0,
            'activity_level': 1.0,
            'attention_seeking': 1.0,
            'clinginess': 1.0,
            'irritability': 1.0
        }

        # Jealousy effects
        if self.has_state(EmotionalState.JEALOUS):
            intensity = self.get_state_intensity(EmotionalState.JEALOUS)
            modifiers['happiness_modifier'] *= (1.0 - intensity * 0.3)
            modifiers['attention_seeking'] *= (1.0 + intensity * 0.8)
            modifiers['irritability'] *= (1.0 + intensity * 0.5)

        # Separation anxiety effects
        if self.has_state(EmotionalState.SEPARATION_ANXIETY):
            intensity = self.get_state_intensity(EmotionalState.SEPARATION_ANXIETY)
            modifiers['happiness_modifier'] *= (1.0 - intensity * 0.5)
            modifiers['activity_level'] *= (1.0 - intensity * 0.4)
            modifiers['clinginess'] *= (1.0 + intensity)

        # Excited return effects
        if self.has_state(EmotionalState.EXCITED_RETURN):
            intensity = self.get_state_intensity(EmotionalState.EXCITED_RETURN)
            modifiers['happiness_modifier'] *= (1.0 + intensity * 0.5)
            modifiers['activity_level'] *= (1.0 + intensity * 0.6)
            modifiers['attention_seeking'] *= (1.0 + intensity)

        # Longing effects
        if self.has_state(EmotionalState.LONGING):
            intensity = self.get_state_intensity(EmotionalState.LONGING)
            modifiers['happiness_modifier'] *= (1.0 - intensity * 0.4)
            modifiers['activity_level'] *= (1.0 - intensity * 0.3)

        # Possessive effects
        if self.has_state(EmotionalState.POSSESSIVE):
            intensity = self.get_state_intensity(EmotionalState.POSSESSIVE)
            modifiers['clinginess'] *= (1.0 + intensity * 0.7)
            modifiers['irritability'] *= (1.0 + intensity * 0.4)

        # Insecurity effects
        if self.has_state(EmotionalState.INSECURE):
            intensity = self.get_state_intensity(EmotionalState.INSECURE)
            modifiers['attention_seeking'] *= (1.0 + intensity * 0.6)
            modifiers['clinginess'] *= (1.0 + intensity * 0.5)

        return modifiers

    def get_stats(self) -> Dict[str, Any]:
        """Get emotional state statistics."""
        return {
            'current_states': self.get_current_states(),
            'owner_present': self.owner_present,
            'times_experienced_separation': self.times_experienced_separation,
            'longest_separation_hours': self.longest_separation / 3600,
            'attention_to_others_score': self.attention_to_others_score,
            'behavioral_modifiers': self.get_behavioral_modifiers()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize emotional state manager."""
        serialized_states = {}
        for state, (intensity, expires_at) in self.current_states.items():
            serialized_states[state.value] = {
                'intensity': intensity,
                'expires_at': expires_at
            }

        return {
            'current_states': serialized_states,
            'state_history': self.state_history[-50:],
            'last_owner_seen': self.last_owner_seen,
            'owner_present': self.owner_present,
            'attention_to_others_score': self.attention_to_others_score,
            'last_jealousy_trigger': self.last_jealousy_trigger,
            'time_owner_left': self.time_owner_left,
            'times_experienced_separation': self.times_experienced_separation,
            'longest_separation': self.longest_separation,
            'last_reunion': self.last_reunion,
            'reunion_excitement_level': self.reunion_excitement_level
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionalStateManager':
        """Deserialize emotional state manager."""
        manager = cls()

        # Restore current states
        for state_name, state_data in data.get('current_states', {}).items():
            state = EmotionalState(state_name)
            manager.current_states[state] = (
                state_data['intensity'],
                state_data['expires_at']
            )

        manager.state_history = data.get('state_history', [])
        manager.last_owner_seen = data.get('last_owner_seen', time.time())
        manager.owner_present = data.get('owner_present', True)
        manager.attention_to_others_score = data.get('attention_to_others_score', 0.0)
        manager.last_jealousy_trigger = data.get('last_jealousy_trigger')
        manager.time_owner_left = data.get('time_owner_left')
        manager.times_experienced_separation = data.get('times_experienced_separation', 0)
        manager.longest_separation = data.get('longest_separation', 0.0)
        manager.last_reunion = data.get('last_reunion')
        manager.reunion_excitement_level = data.get('reunion_excitement_level', 0.0)

        return manager
