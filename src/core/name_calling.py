"""
Name Calling System for Desktop Pal

Handles calling the pet by name with appropriate responses based on bond, trust, and personality.
Integrates with existing NameRecognition from training_system.
"""
from typing import Dict, Any, Optional, Tuple
import random
import time


class NameCallingSystem:
    """
    Manages calling the pet by name and generating appropriate responses.

    Response depends on:
    - Name recognition proficiency (from training_system)
    - Bond level (how much they love you)
    - Trust level (how much they trust you)
    - Personality type
    - Current mood/emotional state
    - Distance from owner
    """

    def __init__(self):
        """Initialize name calling system."""
        self.times_called = 0
        self.times_responded = 0
        self.last_call_time = None
        self.call_history = []

    def call_pet(self, pet_name: str, actual_name: str, bond_level: float,
                trust_level: float, personality: str,
                name_recognition_proficiency: float,
                current_mood: Optional[str] = None) -> Dict[str, Any]:
        """
        Call the pet by name and get response.

        Args:
            pet_name: Name being called
            actual_name: Pet's actual name
            bond_level: Current bond (0-100)
            trust_level: Current trust (0-100)
            personality: Personality type
            name_recognition_proficiency: How well pet knows its name (0-1)
            current_mood: Current mood if any

        Returns:
            Dictionary with response details
        """
        self.times_called += 1
        self.last_call_time = time.time()

        # Check if they recognize their name
        is_correct_name = pet_name.lower() == actual_name.lower()

        # Base response chance on name recognition
        will_respond = self._will_respond_to_call(
            is_correct_name,
            name_recognition_proficiency,
            bond_level,
            trust_level,
            current_mood
        )

        if not will_respond:
            return {
                'responded': False,
                'reason': self._get_ignore_reason(name_recognition_proficiency, bond_level),
                'animation': 'ignore',
                'bond_change': -0.5 if is_correct_name else 0  # Slight bond loss if ignored
            }

        # They responded!
        self.times_responded += 1

        # Get response type based on factors
        response_type, animation = self._get_response_type(
            bond_level,
            trust_level,
            personality,
            current_mood
        )

        # Calculate bond gain from being called
        bond_gain = self._calculate_bond_gain(
            is_correct_name,
            name_recognition_proficiency,
            bond_level
        )

        # Record call
        self.call_history.append({
            'timestamp': time.time(),
            'responded': True,
            'response_type': response_type,
            'bond_level': bond_level
        })

        # Keep last 50 calls
        if len(self.call_history) > 50:
            self.call_history = self.call_history[-50:]

        return {
            'responded': True,
            'response_type': response_type,
            'animation': animation,
            'bond_change': bond_gain,
            'message': self._get_response_message(response_type, bond_level, personality)
        }

    def _will_respond_to_call(self, is_correct_name: bool, recognition: float,
                             bond: float, trust: float,
                             mood: Optional[str]) -> bool:
        """Determine if pet will respond to being called."""
        if not is_correct_name:
            # Wrong name - very low chance of response
            return random.random() < 0.1

        # Base chance from name recognition
        base_chance = recognition * 0.7  # Max 70% from just knowing name

        # Bond increases chance
        bond_bonus = (bond / 100) * 0.2  # Up to +20%

        # Trust increases chance
        trust_bonus = (trust / 100) * 0.1  # Up to +10%

        total_chance = min(0.95, base_chance + bond_bonus + trust_bonus)

        # Mood can affect it
        if mood in ['grumpy', 'angry', 'tired']:
            total_chance *= 0.7
        elif mood in ['happy', 'excited', 'playful']:
            total_chance *= 1.2

        return random.random() < total_chance

    def _get_ignore_reason(self, recognition: float, bond: float) -> str:
        """Get reason why pet ignored the call."""
        if recognition < 0.3:
            return "Doesn't recognize name yet"
        elif bond < 20:
            return "Doesn't care enough to respond"
        else:
            return "Distracted or didn't hear"

    def _get_response_type(self, bond: float, trust: float, personality: str,
                          mood: Optional[str]) -> Tuple[str, str]:
        """
        Get response type and animation.

        Returns:
            Tuple of (response_type, animation)
        """
        # Response intensity based on bond level
        if bond >= 80:  # Best friend
            responses = [
                ('ecstatic_rush', 'run_to_owner'),
                ('excited_jump', 'jump_and_spin'),
                ('devoted_approach', 'happy_trot')
            ]
        elif bond >= 60:  # Close friend
            responses = [
                ('happy_approach', 'trot_over'),
                ('tail_wag', 'wag_approach'),
                ('excited_look', 'turn_and_approach')
            ]
        elif bond >= 40:  # Friend
            responses = [
                ('friendly_response', 'walk_over'),
                ('acknowledgment', 'look_and_approach'),
                ('casual_approach', 'slow_walk')
            ]
        elif bond >= 20:  # Acquaintance
            responses = [
                ('cautious_approach', 'slow_approach'),
                ('hesitant_response', 'peek_and_approach'),
                ('neutral_acknowledgment', 'turn_head')
            ]
        else:  # Stranger
            responses = [
                ('wary_acknowledgment', 'cautious_glance'),
                ('minimal_response', 'ear_twitch'),
                ('reluctant_turn', 'slow_turn')
            ]

        # Personality modifies response
        personality_overrides = {
            'energetic': ('bouncy_response', 'bounce_over'),
            'lazy': ('slow_response', 'lazy_stretch_then_approach'),
            'playful': ('playful_response', 'playful_pounce'),
            'shy': ('timid_response', 'peek_then_approach'),
            'affectionate': ('loving_response', 'rush_over_affectionately'),
            'independent': ('casual_glance', 'brief_acknowledgment')
        }

        if personality in personality_overrides and bond >= 40:
            return personality_overrides[personality]

        # Pick random from appropriate level
        return random.choice(responses)

    def _calculate_bond_gain(self, correct_name: bool, recognition: float,
                            current_bond: float) -> float:
        """Calculate how much bond increases from being called."""
        if not correct_name:
            return 0.0

        # Base gain
        base_gain = 1.0

        # Less gain at higher bonds (harder to increase)
        bond_modifier = 1.0 - (current_bond / 150)  # Reduces as bond increases

        # More gain if they don't know name well yet (learning)
        recognition_bonus = (1.0 - recognition) * 0.5

        total_gain = base_gain * bond_modifier + recognition_bonus

        return max(0.3, min(2.0, total_gain))

    def _get_response_message(self, response_type: str, bond: float,
                             personality: str) -> str:
        """Get message describing the response."""
        if bond >= 80:
            messages = [
                f"Rushes over excitedly, thrilled to hear your voice!",
                f"Drops everything and bounds toward you with pure joy!",
                f"Responds immediately with obvious delight!"
            ]
        elif bond >= 60:
            messages = [
                f"Perks up and hurries over happily!",
                f"Turns toward you with clear affection!",
                f"Responds warmly and approaches!"
            ]
        elif bond >= 40:
            messages = [
                f"Looks up and walks over casually.",
                f"Acknowledges you and comes closer.",
                f"Responds and approaches in a friendly manner."
            ]
        elif bond >= 20:
            messages = [
                f"Glances over hesitantly.",
                f"Acknowledges you but seems uncertain.",
                f"Responds cautiously."
            ]
        else:
            messages = [
                f"Barely acknowledges you.",
                f"Gives you a wary glance.",
                f"Seems to notice but doesn't approach."
            ]

        return random.choice(messages)

    def get_response_rate(self) -> float:
        """Get percentage of times pet has responded to calls."""
        if self.times_called == 0:
            return 0.0
        return (self.times_responded / self.times_called) * 100

    def get_stats(self) -> Dict[str, Any]:
        """Get name calling statistics."""
        return {
            'times_called': self.times_called,
            'times_responded': self.times_responded,
            'response_rate': self.get_response_rate(),
            'last_call_time': self.last_call_time,
            'recent_responses': self.call_history[-10:] if self.call_history else []
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize name calling system."""
        return {
            'times_called': self.times_called,
            'times_responded': self.times_responded,
            'last_call_time': self.last_call_time,
            'call_history': self.call_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NameCallingSystem':
        """Deserialize name calling system."""
        system = cls()
        system.times_called = data.get('times_called', 0)
        system.times_responded = data.get('times_responded', 0)
        system.last_call_time = data.get('last_call_time')
        system.call_history = data.get('call_history', [])
        return system
