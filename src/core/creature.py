"""
Creature class representing the desktop pet with its attributes, personality, and state.
"""
import random
import time
from typing import Dict, Any
from datetime import datetime
from .config import (
    PersonalityType, BehaviorState, CREATURE_TYPES, COLOR_PALETTES,
    PERSONALITY_TRAITS, MAX_HUNGER, HUNGER_DECAY_RATE, STARVATION_THRESHOLD
)


class Creature:
    """Represents a desktop pet creature with personality, stats, and learning capabilities."""

    def __init__(self, creature_type: str = None, personality: PersonalityType = None,
                 color_palette: list = None, name: str = None):
        """
        Initialize a new creature.

        Args:
            creature_type: Type of creature (e.g., 'dragon', 'cat'). Random if None.
            personality: Personality type. Random if None.
            color_palette: Color palette for the creature. Random if None.
            name: Name of the creature. Generated if None.
        """
        self.creature_type = creature_type or random.choice(CREATURE_TYPES)
        self.personality = personality or random.choice(list(PersonalityType))
        self.color_palette = color_palette or random.choice(COLOR_PALETTES)
        self.name = name or self._generate_name()

        # Stats
        self.hunger = 0.0  # 0 = not hungry, 100 = starving
        self.happiness = 100.0  # 0-100
        self.energy = 100.0  # 0-100
        self.age = 0  # in seconds
        self.birth_time = time.time()
        self.last_fed_time = time.time()
        self.last_interaction_time = time.time()

        # State
        self.current_state = BehaviorState.IDLE
        self.position = [100, 100]  # x, y position on screen
        self.velocity = [0, 0]  # x, y velocity
        self.facing_right = True

        # Learning and behavior
        self.learned_behaviors = {}
        self.interaction_history = []
        self.preference_scores = {
            'ball_play': 0.5,
            'mouse_chase': 0.5,
            'hide_and_seek': 0.5,
            'icon_interaction': 0.5,
            'being_fed': 1.0
        }

        # Personality trait modifiers
        self.trait_modifiers = PERSONALITY_TRAITS[self.personality]

    def _generate_name(self) -> str:
        """Generate a random name for the creature."""
        prefixes = ['Pip', 'Moo', 'Fluff', 'Spark', 'Dash', 'Glow', 'Puff', 'Zip']
        suffixes = ['kin', 'zy', 'bit', 'ie', 'er', 'ling', 'y', 'o']
        return random.choice(prefixes) + random.choice(suffixes)

    def update(self, delta_time: float):
        """
        Update creature state based on elapsed time.

        Args:
            delta_time: Time elapsed since last update in seconds.
        """
        # Update age
        self.age = time.time() - self.birth_time

        # Update hunger
        minutes_elapsed = delta_time / 60.0
        hunger_increase = HUNGER_DECAY_RATE * minutes_elapsed
        self.hunger = min(MAX_HUNGER, self.hunger + hunger_increase)

        # Update energy based on activity
        if self.current_state in [BehaviorState.RUNNING, BehaviorState.PLAYING]:
            energy_drain = 0.5 * delta_time * self.trait_modifiers.get('energy_consumption', 1.0)
            self.energy = max(0, self.energy - energy_drain)
        elif self.current_state == BehaviorState.SLEEPING:
            energy_gain = 2.0 * delta_time
            self.energy = min(100, self.energy + energy_gain)
        else:
            # Slow energy recovery during idle/walking
            energy_gain = 0.2 * delta_time
            self.energy = min(100, self.energy + energy_gain)

        # Update happiness based on interactions and care
        time_since_interaction = time.time() - self.last_interaction_time
        if time_since_interaction > 300:  # 5 minutes without interaction
            happiness_decay = 0.1 * delta_time
            self.happiness = max(0, self.happiness - happiness_decay)

        # Hunger affects happiness
        if self.hunger > 50:
            happiness_decay = 0.05 * delta_time * (self.hunger / 50)
            self.happiness = max(0, self.happiness - happiness_decay)

    def feed(self, amount: float = 30):
        """Feed the creature, reducing hunger."""
        self.hunger = max(0, self.hunger - amount)
        self.last_fed_time = time.time()
        self.happiness = min(100, self.happiness + 5)
        self.last_interaction_time = time.time()

        # Update preference for being fed
        self.preference_scores['being_fed'] = min(1.0, self.preference_scores['being_fed'] + 0.05)

    def interact(self, interaction_type: str, positive: bool = True):
        """
        Record an interaction with the creature.

        Args:
            interaction_type: Type of interaction (e.g., 'ball_play', 'mouse_chase')
            positive: Whether the interaction was positive (enjoyed) or negative
        """
        self.last_interaction_time = time.time()

        # Update preference scores based on interaction
        if interaction_type in self.preference_scores:
            change = 0.05 if positive else -0.03
            self.preference_scores[interaction_type] = max(0, min(1,
                self.preference_scores[interaction_type] + change))

        # Record in history for neural network learning
        self.interaction_history.append({
            'type': interaction_type,
            'positive': positive,
            'timestamp': time.time(),
            'hunger_level': self.hunger,
            'energy_level': self.energy,
            'happiness_level': self.happiness
        })

        # Keep only recent history (last 100 interactions)
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]

        # Update happiness
        happiness_change = 3 if positive else -1
        happiness_multiplier = self.trait_modifiers.get('happiness_gain', 1.0)
        self.happiness = max(0, min(100, self.happiness + happiness_change * happiness_multiplier))

    def is_starving(self) -> bool:
        """Check if the creature is starving (will die)."""
        return self.hunger >= STARVATION_THRESHOLD

    def should_sleep(self) -> bool:
        """Determine if creature should sleep based on energy."""
        return self.energy < 20

    def get_preferred_activity(self) -> str:
        """Get the creature's currently most preferred activity."""
        # Filter out being_fed from activities
        activities = {k: v for k, v in self.preference_scores.items() if k != 'being_fed'}
        if not activities:
            return 'idle'
        return max(activities.items(), key=lambda x: x[1])[0]

    def set_state(self, state: BehaviorState):
        """Change the creature's behavior state."""
        self.current_state = state

    def to_dict(self) -> Dict[str, Any]:
        """Convert creature to dictionary for saving."""
        return {
            'creature_type': self.creature_type,
            'personality': self.personality.value,
            'color_palette': self.color_palette,
            'name': self.name,
            'hunger': self.hunger,
            'happiness': self.happiness,
            'energy': self.energy,
            'birth_time': self.birth_time,
            'last_fed_time': self.last_fed_time,
            'last_interaction_time': self.last_interaction_time,
            'position': self.position,
            'preference_scores': self.preference_scores,
            'interaction_history': self.interaction_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Creature':
        """Create a creature from a dictionary."""
        personality = PersonalityType(data['personality'])
        creature = cls(
            creature_type=data['creature_type'],
            personality=personality,
            color_palette=data['color_palette'],
            name=data['name']
        )

        creature.hunger = data['hunger']
        creature.happiness = data['happiness']
        creature.energy = data['energy']
        creature.birth_time = data['birth_time']
        creature.last_fed_time = data['last_fed_time']
        creature.last_interaction_time = data['last_interaction_time']
        creature.position = data['position']
        creature.preference_scores = data['preference_scores']
        creature.interaction_history = data['interaction_history']

        return creature

    def __str__(self) -> str:
        """String representation of the creature."""
        return (f"{self.name} the {self.personality.value} {self.creature_type} "
                f"(Hunger: {self.hunger:.1f}, Happiness: {self.happiness:.1f}, "
                f"Energy: {self.energy:.1f})")
