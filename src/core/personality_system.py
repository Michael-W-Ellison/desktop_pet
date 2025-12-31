"""
Enhanced Personality System for Desktop Pal (Phase 3)

Features:
- 25 distinct personality types
- Multi-dimensional trait system (sliding scales, not just categories)
- Mood system (temporary emotional states)
- Personality drift (changes based on life experiences)
- Personality blending (creatures can have mixed personalities)
"""
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from .config import PersonalityType


class TraitDimension(Enum):
    """Core personality dimensions (sliding scales 0-1)."""
    SOCIABILITY = "sociability"          # 0=aloof, 1=social
    ENERGY_LEVEL = "energy_level"        # 0=calm, 1=hyperactive
    CONFIDENCE = "confidence"             # 0=timid, 1=bold
    COMPLIANCE = "compliance"             # 0=stubborn, 1=obedient
    EMOTIONAL_STABILITY = "emotional_stability"  # 0=volatile, 1=stable
    INTELLIGENCE = "intelligence"         # 0=simple, 1=clever
    PLAYFULNESS = "playfulness"          # 0=serious, 1=playful
    CURIOSITY = "curiosity"              # 0=routine-bound, 1=exploratory
    AGGRESSION = "aggression"            # 0=gentle, 1=fierce
    TRUST = "trust"                      # 0=suspicious, 1=trusting
    PATIENCE = "patience"                # 0=impatient, 1=patient
    INDEPENDENCE = "independence"        # 0=clingy, 1=independent


class Mood(Enum):
    """Temporary emotional states (last minutes to hours)."""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    ANGRY = "angry"
    CONTENT = "content"
    SCARED = "scared"
    PLAYFUL = "playful"
    TIRED = "tired"
    CURIOUS = "curious"
    GRUMPY = "grumpy"
    AFFECTIONATE = "affectionate"


class MultiDimensionalPersonality:
    """
    Personality represented as sliding scales on multiple dimensions.

    Instead of just "playful" or "serious", a creature has scores on
    12 different trait dimensions. This creates much more nuanced personalities.
    """

    def __init__(self, base_personality: PersonalityType = None):
        """
        Initialize multi-dimensional personality.

        Args:
            base_personality: Starting personality type (generates trait scores)
        """
        self.base_personality = base_personality

        # Initialize trait dimensions (0-1 scale for each)
        if base_personality:
            self.traits = self._generate_traits_from_type(base_personality)
        else:
            # Random personality
            self.traits = {dim: np.random.uniform(0.3, 0.7) for dim in TraitDimension}

        # Track original traits for drift measurement
        self.original_traits = self.traits.copy()

    def _generate_traits_from_type(self, personality: PersonalityType) -> Dict[TraitDimension, float]:
        """
        Generate trait scores based on personality type.

        Returns:
            Dictionary mapping trait dimensions to values (0-1)
        """
        # Base profiles for each personality type
        profiles = {
            PersonalityType.PLAYFUL: {
                TraitDimension.SOCIABILITY: 0.8,
                TraitDimension.ENERGY_LEVEL: 0.9,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.5,
                TraitDimension.EMOTIONAL_STABILITY: 0.6,
                TraitDimension.INTELLIGENCE: 0.5,
                TraitDimension.PLAYFULNESS: 0.95,
                TraitDimension.CURIOSITY: 0.7,
                TraitDimension.AGGRESSION: 0.2,
                TraitDimension.TRUST: 0.7,
                TraitDimension.PATIENCE: 0.4,
                TraitDimension.INDEPENDENCE: 0.4
            },
            PersonalityType.SHY: {
                TraitDimension.SOCIABILITY: 0.2,
                TraitDimension.ENERGY_LEVEL: 0.4,
                TraitDimension.CONFIDENCE: 0.2,
                TraitDimension.COMPLIANCE: 0.7,
                TraitDimension.EMOTIONAL_STABILITY: 0.5,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.3,
                TraitDimension.CURIOSITY: 0.4,
                TraitDimension.AGGRESSION: 0.1,
                TraitDimension.TRUST: 0.3,
                TraitDimension.PATIENCE: 0.6,
                TraitDimension.INDEPENDENCE: 0.5
            },
            PersonalityType.CURIOUS: {
                TraitDimension.SOCIABILITY: 0.6,
                TraitDimension.ENERGY_LEVEL: 0.7,
                TraitDimension.CONFIDENCE: 0.6,
                TraitDimension.COMPLIANCE: 0.5,
                TraitDimension.EMOTIONAL_STABILITY: 0.5,
                TraitDimension.INTELLIGENCE: 0.8,
                TraitDimension.PLAYFULNESS: 0.6,
                TraitDimension.CURIOSITY: 0.95,
                TraitDimension.AGGRESSION: 0.3,
                TraitDimension.TRUST: 0.5,
                TraitDimension.PATIENCE: 0.4,
                TraitDimension.INDEPENDENCE: 0.7
            },
            PersonalityType.LAZY: {
                TraitDimension.SOCIABILITY: 0.4,
                TraitDimension.ENERGY_LEVEL: 0.1,
                TraitDimension.CONFIDENCE: 0.5,
                TraitDimension.COMPLIANCE: 0.6,
                TraitDimension.EMOTIONAL_STABILITY: 0.8,
                TraitDimension.INTELLIGENCE: 0.4,
                TraitDimension.PLAYFULNESS: 0.2,
                TraitDimension.CURIOSITY: 0.2,
                TraitDimension.AGGRESSION: 0.2,
                TraitDimension.TRUST: 0.5,
                TraitDimension.PATIENCE: 0.8,
                TraitDimension.INDEPENDENCE: 0.6
            },
            PersonalityType.ENERGETIC: {
                TraitDimension.SOCIABILITY: 0.7,
                TraitDimension.ENERGY_LEVEL: 0.95,
                TraitDimension.CONFIDENCE: 0.8,
                TraitDimension.COMPLIANCE: 0.4,
                TraitDimension.EMOTIONAL_STABILITY: 0.5,
                TraitDimension.INTELLIGENCE: 0.5,
                TraitDimension.PLAYFULNESS: 0.8,
                TraitDimension.CURIOSITY: 0.7,
                TraitDimension.AGGRESSION: 0.4,
                TraitDimension.TRUST: 0.6,
                TraitDimension.PATIENCE: 0.3,
                TraitDimension.INDEPENDENCE: 0.5
            },
            PersonalityType.MISCHIEVOUS: {
                TraitDimension.SOCIABILITY: 0.6,
                TraitDimension.ENERGY_LEVEL: 0.7,
                TraitDimension.CONFIDENCE: 0.8,
                TraitDimension.COMPLIANCE: 0.2,
                TraitDimension.EMOTIONAL_STABILITY: 0.6,
                TraitDimension.INTELLIGENCE: 0.7,
                TraitDimension.PLAYFULNESS: 0.85,
                TraitDimension.CURIOSITY: 0.8,
                TraitDimension.AGGRESSION: 0.3,
                TraitDimension.TRUST: 0.4,
                TraitDimension.PATIENCE: 0.3,
                TraitDimension.INDEPENDENCE: 0.7
            },
            PersonalityType.AFFECTIONATE: {
                TraitDimension.SOCIABILITY: 0.9,
                TraitDimension.ENERGY_LEVEL: 0.6,
                TraitDimension.CONFIDENCE: 0.6,
                TraitDimension.COMPLIANCE: 0.8,
                TraitDimension.EMOTIONAL_STABILITY: 0.7,
                TraitDimension.INTELLIGENCE: 0.5,
                TraitDimension.PLAYFULNESS: 0.7,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.1,
                TraitDimension.TRUST: 0.9,
                TraitDimension.PATIENCE: 0.7,
                TraitDimension.INDEPENDENCE: 0.2
            },
            PersonalityType.INDEPENDENT: {
                TraitDimension.SOCIABILITY: 0.3,
                TraitDimension.ENERGY_LEVEL: 0.6,
                TraitDimension.CONFIDENCE: 0.8,
                TraitDimension.COMPLIANCE: 0.3,
                TraitDimension.EMOTIONAL_STABILITY: 0.8,
                TraitDimension.INTELLIGENCE: 0.7,
                TraitDimension.PLAYFULNESS: 0.4,
                TraitDimension.CURIOSITY: 0.7,
                TraitDimension.AGGRESSION: 0.3,
                TraitDimension.TRUST: 0.5,
                TraitDimension.PATIENCE: 0.6,
                TraitDimension.INDEPENDENCE: 0.95
            },
            # Phase 3 new personalities
            PersonalityType.CRANKY: {
                TraitDimension.SOCIABILITY: 0.2,
                TraitDimension.ENERGY_LEVEL: 0.4,
                TraitDimension.CONFIDENCE: 0.5,
                TraitDimension.COMPLIANCE: 0.2,
                TraitDimension.EMOTIONAL_STABILITY: 0.3,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.1,
                TraitDimension.CURIOSITY: 0.3,
                TraitDimension.AGGRESSION: 0.6,
                TraitDimension.TRUST: 0.3,
                TraitDimension.PATIENCE: 0.2,
                TraitDimension.INDEPENDENCE: 0.7
            },
            PersonalityType.STUBBORN: {
                TraitDimension.SOCIABILITY: 0.4,
                TraitDimension.ENERGY_LEVEL: 0.5,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.1,
                TraitDimension.EMOTIONAL_STABILITY: 0.6,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.3,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.4,
                TraitDimension.TRUST: 0.4,
                TraitDimension.PATIENCE: 0.4,
                TraitDimension.INDEPENDENCE: 0.8
            },
            PersonalityType.SKITTISH: {
                TraitDimension.SOCIABILITY: 0.2,
                TraitDimension.ENERGY_LEVEL: 0.8,
                TraitDimension.CONFIDENCE: 0.1,
                TraitDimension.COMPLIANCE: 0.6,
                TraitDimension.EMOTIONAL_STABILITY: 0.2,
                TraitDimension.INTELLIGENCE: 0.5,
                TraitDimension.PLAYFULNESS: 0.3,
                TraitDimension.CURIOSITY: 0.4,
                TraitDimension.AGGRESSION: 0.1,
                TraitDimension.TRUST: 0.2,
                TraitDimension.PATIENCE: 0.3,
                TraitDimension.INDEPENDENCE: 0.4
            },
            PersonalityType.BRAVE: {
                TraitDimension.SOCIABILITY: 0.7,
                TraitDimension.ENERGY_LEVEL: 0.7,
                TraitDimension.CONFIDENCE: 0.95,
                TraitDimension.COMPLIANCE: 0.4,
                TraitDimension.EMOTIONAL_STABILITY: 0.8,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.6,
                TraitDimension.CURIOSITY: 0.8,
                TraitDimension.AGGRESSION: 0.4,
                TraitDimension.TRUST: 0.6,
                TraitDimension.PATIENCE: 0.5,
                TraitDimension.INDEPENDENCE: 0.7
            },
            PersonalityType.GENTLE: {
                TraitDimension.SOCIABILITY: 0.7,
                TraitDimension.ENERGY_LEVEL: 0.4,
                TraitDimension.CONFIDENCE: 0.5,
                TraitDimension.COMPLIANCE: 0.8,
                TraitDimension.EMOTIONAL_STABILITY: 0.8,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.5,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.05,
                TraitDimension.TRUST: 0.8,
                TraitDimension.PATIENCE: 0.9,
                TraitDimension.INDEPENDENCE: 0.4
            },
            PersonalityType.FIERCE: {
                TraitDimension.SOCIABILITY: 0.3,
                TraitDimension.ENERGY_LEVEL: 0.8,
                TraitDimension.CONFIDENCE: 0.9,
                TraitDimension.COMPLIANCE: 0.2,
                TraitDimension.EMOTIONAL_STABILITY: 0.5,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.4,
                TraitDimension.CURIOSITY: 0.6,
                TraitDimension.AGGRESSION: 0.95,
                TraitDimension.TRUST: 0.3,
                TraitDimension.PATIENCE: 0.3,
                TraitDimension.INDEPENDENCE: 0.8
            },
            PersonalityType.CLEVER: {
                TraitDimension.SOCIABILITY: 0.6,
                TraitDimension.ENERGY_LEVEL: 0.6,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.4,
                TraitDimension.EMOTIONAL_STABILITY: 0.7,
                TraitDimension.INTELLIGENCE: 0.95,
                TraitDimension.PLAYFULNESS: 0.5,
                TraitDimension.CURIOSITY: 0.9,
                TraitDimension.AGGRESSION: 0.3,
                TraitDimension.TRUST: 0.5,
                TraitDimension.PATIENCE: 0.6,
                TraitDimension.INDEPENDENCE: 0.7
            },
            PersonalityType.SILLY: {
                TraitDimension.SOCIABILITY: 0.8,
                TraitDimension.ENERGY_LEVEL: 0.9,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.3,
                TraitDimension.EMOTIONAL_STABILITY: 0.6,
                TraitDimension.INTELLIGENCE: 0.3,
                TraitDimension.PLAYFULNESS: 0.95,
                TraitDimension.CURIOSITY: 0.7,
                TraitDimension.AGGRESSION: 0.2,
                TraitDimension.TRUST: 0.7,
                TraitDimension.PATIENCE: 0.2,
                TraitDimension.INDEPENDENCE: 0.4
            },
            PersonalityType.SERIOUS: {
                TraitDimension.SOCIABILITY: 0.4,
                TraitDimension.ENERGY_LEVEL: 0.5,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.6,
                TraitDimension.EMOTIONAL_STABILITY: 0.9,
                TraitDimension.INTELLIGENCE: 0.8,
                TraitDimension.PLAYFULNESS: 0.1,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.3,
                TraitDimension.TRUST: 0.5,
                TraitDimension.PATIENCE: 0.8,
                TraitDimension.INDEPENDENCE: 0.7
            },
            PersonalityType.PATIENT: {
                TraitDimension.SOCIABILITY: 0.6,
                TraitDimension.ENERGY_LEVEL: 0.4,
                TraitDimension.CONFIDENCE: 0.6,
                TraitDimension.COMPLIANCE: 0.7,
                TraitDimension.EMOTIONAL_STABILITY: 0.9,
                TraitDimension.INTELLIGENCE: 0.7,
                TraitDimension.PLAYFULNESS: 0.4,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.2,
                TraitDimension.TRUST: 0.7,
                TraitDimension.PATIENCE: 0.95,
                TraitDimension.INDEPENDENCE: 0.6
            },
            PersonalityType.IMPATIENT: {
                TraitDimension.SOCIABILITY: 0.5,
                TraitDimension.ENERGY_LEVEL: 0.8,
                TraitDimension.CONFIDENCE: 0.6,
                TraitDimension.COMPLIANCE: 0.3,
                TraitDimension.EMOTIONAL_STABILITY: 0.4,
                TraitDimension.INTELLIGENCE: 0.5,
                TraitDimension.PLAYFULNESS: 0.6,
                TraitDimension.CURIOSITY: 0.6,
                TraitDimension.AGGRESSION: 0.5,
                TraitDimension.TRUST: 0.4,
                TraitDimension.PATIENCE: 0.1,
                TraitDimension.INDEPENDENCE: 0.6
            },
            PersonalityType.TRUSTING: {
                TraitDimension.SOCIABILITY: 0.8,
                TraitDimension.ENERGY_LEVEL: 0.6,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.8,
                TraitDimension.EMOTIONAL_STABILITY: 0.7,
                TraitDimension.INTELLIGENCE: 0.5,
                TraitDimension.PLAYFULNESS: 0.6,
                TraitDimension.CURIOSITY: 0.6,
                TraitDimension.AGGRESSION: 0.2,
                TraitDimension.TRUST: 0.95,
                TraitDimension.PATIENCE: 0.7,
                TraitDimension.INDEPENDENCE: 0.3
            },
            PersonalityType.SUSPICIOUS: {
                TraitDimension.SOCIABILITY: 0.2,
                TraitDimension.ENERGY_LEVEL: 0.5,
                TraitDimension.CONFIDENCE: 0.4,
                TraitDimension.COMPLIANCE: 0.3,
                TraitDimension.EMOTIONAL_STABILITY: 0.4,
                TraitDimension.INTELLIGENCE: 0.8,
                TraitDimension.PLAYFULNESS: 0.3,
                TraitDimension.CURIOSITY: 0.6,
                TraitDimension.AGGRESSION: 0.4,
                TraitDimension.TRUST: 0.1,
                TraitDimension.PATIENCE: 0.5,
                TraitDimension.INDEPENDENCE: 0.8
            },
            PersonalityType.CALM: {
                TraitDimension.SOCIABILITY: 0.5,
                TraitDimension.ENERGY_LEVEL: 0.3,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.6,
                TraitDimension.EMOTIONAL_STABILITY: 0.95,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.4,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.2,
                TraitDimension.TRUST: 0.6,
                TraitDimension.PATIENCE: 0.9,
                TraitDimension.INDEPENDENCE: 0.7
            },
            PersonalityType.ANXIOUS: {
                TraitDimension.SOCIABILITY: 0.3,
                TraitDimension.ENERGY_LEVEL: 0.7,
                TraitDimension.CONFIDENCE: 0.2,
                TraitDimension.COMPLIANCE: 0.6,
                TraitDimension.EMOTIONAL_STABILITY: 0.1,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.3,
                TraitDimension.CURIOSITY: 0.4,
                TraitDimension.AGGRESSION: 0.2,
                TraitDimension.TRUST: 0.3,
                TraitDimension.PATIENCE: 0.3,
                TraitDimension.INDEPENDENCE: 0.4
            },
            PersonalityType.LOYAL: {
                TraitDimension.SOCIABILITY: 0.8,
                TraitDimension.ENERGY_LEVEL: 0.6,
                TraitDimension.CONFIDENCE: 0.6,
                TraitDimension.COMPLIANCE: 0.9,
                TraitDimension.EMOTIONAL_STABILITY: 0.7,
                TraitDimension.INTELLIGENCE: 0.6,
                TraitDimension.PLAYFULNESS: 0.6,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.3,
                TraitDimension.TRUST: 0.9,
                TraitDimension.PATIENCE: 0.7,
                TraitDimension.INDEPENDENCE: 0.1
            },
            PersonalityType.SELFISH: {
                TraitDimension.SOCIABILITY: 0.3,
                TraitDimension.ENERGY_LEVEL: 0.5,
                TraitDimension.CONFIDENCE: 0.7,
                TraitDimension.COMPLIANCE: 0.2,
                TraitDimension.EMOTIONAL_STABILITY: 0.6,
                TraitDimension.INTELLIGENCE: 0.7,
                TraitDimension.PLAYFULNESS: 0.4,
                TraitDimension.CURIOSITY: 0.5,
                TraitDimension.AGGRESSION: 0.5,
                TraitDimension.TRUST: 0.3,
                TraitDimension.PATIENCE: 0.4,
                TraitDimension.INDEPENDENCE: 0.9
            }
        }

        if personality in profiles:
            traits = profiles[personality].copy()
            # Add some randomness (±10%)
            for dim in traits:
                noise = np.random.uniform(-0.1, 0.1)
                traits[dim] = np.clip(traits[dim] + noise, 0.0, 1.0)
            return traits
        else:
            # Fallback: random traits
            return {dim: np.random.uniform(0.3, 0.7) for dim in TraitDimension}

    def get_trait(self, dimension: TraitDimension) -> float:
        """Get current value for a trait dimension."""
        return self.traits.get(dimension, 0.5)

    def adjust_trait(self, dimension: TraitDimension, change: float):
        """
        Adjust a trait by a certain amount (personality drift).

        Args:
            dimension: Which trait to adjust
            change: How much to change (can be positive or negative)
        """
        current = self.traits.get(dimension, 0.5)
        new_value = np.clip(current + change, 0.0, 1.0)
        self.traits[dimension] = new_value

    def get_drift_amount(self) -> float:
        """
        Calculate how much personality has drifted from original.

        Returns:
            Average absolute difference across all traits
        """
        diffs = []
        for dim in TraitDimension:
            original = self.original_traits.get(dim, 0.5)
            current = self.traits.get(dim, 0.5)
            diffs.append(abs(current - original))

        return np.mean(diffs)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize personality."""
        return {
            'base_personality': self.base_personality.value if self.base_personality else None,
            'traits': {dim.value: val for dim, val in self.traits.items()},
            'original_traits': {dim.value: val for dim, val in self.original_traits.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiDimensionalPersonality':
        """Deserialize personality."""
        base_type = PersonalityType(data['base_personality']) if data.get('base_personality') else None
        personality = cls(base_personality=base_type)

        # Restore traits
        personality.traits = {
            TraitDimension(k): v for k, v in data['traits'].items()
        }
        personality.original_traits = {
            TraitDimension(k): v for k, v in data['original_traits'].items()
        }

        return personality


class MoodSystem:
    """
    Manages temporary emotional states (moods).

    Moods are short-lived (minutes to hours) and influenced by recent events.
    Unlike personality (stable), mood changes frequently.
    """

    def __init__(self):
        """Initialize mood system."""
        self.current_mood = Mood.CONTENT
        self.mood_intensity = 0.5  # How strongly they feel the mood (0-1)
        self.mood_start_time = time.time()
        self.mood_duration = 300  # How long mood lasts (seconds)

        # Mood influence modifiers (how mood affects behavior)
        self.mood_effects = {
            Mood.HAPPY: {'energy_bonus': 0.2, 'sociability_bonus': 0.2, 'learning_bonus': 0.1},
            Mood.SAD: {'energy_penalty': 0.2, 'sociability_penalty': 0.3, 'playfulness_penalty': 0.2},
            Mood.EXCITED: {'energy_bonus': 0.3, 'playfulness_bonus': 0.4, 'patience_penalty': 0.3},
            Mood.ANXIOUS: {'stress_level': 0.7, 'hiding_tendency': 0.4, 'compliance_penalty': 0.2},
            Mood.ANGRY: {'aggression_bonus': 0.5, 'compliance_penalty': 0.6, 'sociability_penalty': 0.3},
            Mood.CONTENT: {},  # Neutral, no modifiers
            Mood.SCARED: {'hiding_tendency': 0.8, 'sociability_penalty': 0.5, 'confidence_penalty': 0.4},
            Mood.PLAYFUL: {'playfulness_bonus': 0.5, 'energy_bonus': 0.2, 'interaction_desire': 0.3},
            Mood.TIRED: {'energy_penalty': 0.4, 'patience_bonus': 0.2, 'playfulness_penalty': 0.3},
            Mood.CURIOUS: {'curiosity_bonus': 0.4, 'exploration_bonus': 0.3, 'focus_bonus': 0.2},
            Mood.GRUMPY: {'irritability': 0.5, 'sociability_penalty': 0.3, 'compliance_penalty': 0.3},
            Mood.AFFECTIONATE: {'sociability_bonus': 0.4, 'trust_bonus': 0.3, 'interaction_desire': 0.4}
        }

    def set_mood(self, mood: Mood, intensity: float = 0.7, duration: float = 300):
        """
        Change to a new mood.

        Args:
            mood: The new mood
            intensity: How strongly felt (0-1)
            duration: How long it lasts (seconds)
        """
        self.current_mood = mood
        self.mood_intensity = np.clip(intensity, 0.0, 1.0)
        self.mood_start_time = time.time()
        self.mood_duration = duration

    def update(self):
        """Update mood (check if it should expire)."""
        elapsed = time.time() - self.mood_start_time

        if elapsed > self.mood_duration:
            # Mood expired, return to content
            if self.current_mood != Mood.CONTENT:
                self.set_mood(Mood.CONTENT, intensity=0.5, duration=float('inf'))

            # Gradually reduce intensity
            decay_rate = 0.1  # per hour
            hours_elapsed = elapsed / 3600
            self.mood_intensity = max(0.1, self.mood_intensity - decay_rate * hours_elapsed)

    def trigger_mood_from_event(self, event_type: str, positive: bool, intensity: float = 0.6):
        """
        Trigger a mood based on an event.

        Args:
            event_type: Type of event
            positive: Whether event was positive
            intensity: Base intensity
        """
        mood_mappings = {
            ('feed', True): (Mood.CONTENT, 0.5, 600),
            ('feed', False): (Mood.GRUMPY, 0.4, 300),
            ('play_ball', True): (Mood.PLAYFUL, 0.8, 900),
            ('play_ball', False): (Mood.SAD, 0.5, 400),
            ('pet', True): (Mood.AFFECTIONATE, 0.7, 500),
            ('startle', False): (Mood.SCARED, 0.9, 300),
            ('learning_success', True): (Mood.EXCITED, 0.6, 400),
            ('learning_failure', False): (Mood.GRUMPY, 0.5, 300),
            ('waiting', False): (Mood.GRUMPY, 0.6, 200),
            ('exploration', True): (Mood.CURIOUS, 0.7, 600)
        }

        key = (event_type, positive)
        if key in mood_mappings:
            mood, base_intensity, duration = mood_mappings[key]
            self.set_mood(mood, intensity=base_intensity * intensity, duration=duration)

    def get_mood_modifiers(self) -> Dict[str, float]:
        """
        Get current behavioral modifiers from mood.

        Returns:
            Dictionary of modifiers
        """
        base_effects = self.mood_effects.get(self.current_mood, {})

        # Scale by intensity
        return {k: v * self.mood_intensity for k, v in base_effects.items()}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize mood system."""
        return {
            'current_mood': self.current_mood.value,
            'mood_intensity': self.mood_intensity,
            'mood_start_time': self.mood_start_time,
            'mood_duration': self.mood_duration
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoodSystem':
        """Deserialize mood system."""
        mood_system = cls()
        mood_system.current_mood = Mood(data['current_mood'])
        mood_system.mood_intensity = data['mood_intensity']
        mood_system.mood_start_time = data['mood_start_time']
        mood_system.mood_duration = data['mood_duration']
        return mood_system


class PersonalityDrift:
    """
    Manages personality changes based on life experiences.

    Personalities aren't completely fixed - they evolve based on how
    the creature is treated and what experiences it has.
    """

    def __init__(self, personality: MultiDimensionalPersonality):
        """
        Initialize personality drift system.

        Args:
            personality: The personality to manage
        """
        self.personality = personality
        self.drift_rate = 0.001  # How quickly personality changes
        self.experience_buffer = []  # Recent experiences

    def record_experience(self, experience_type: str, outcome: str, impact: float = 1.0):
        """
        Record an experience that might influence personality.

        Args:
            experience_type: Type of experience
            outcome: Result ('positive', 'negative', 'neutral')
            impact: How impactful (0-1)
        """
        self.experience_buffer.append({
            'type': experience_type,
            'outcome': outcome,
            'impact': impact,
            'timestamp': time.time()
        })

        # Keep only recent experiences (last 100)
        if len(self.experience_buffer) > 100:
            self.experience_buffer = self.experience_buffer[-100:]

        # Apply immediate drift
        self._apply_experience_drift(experience_type, outcome, impact)

    def _apply_experience_drift(self, experience_type: str, outcome: str, impact: float):
        """
        Apply personality drift from an experience.

        Args:
            experience_type: Type of experience
            outcome: Outcome of experience
            impact: How impactful
        """
        # Define how experiences affect traits
        drift_mappings = {
            ('training_success', 'positive'): [(TraitDimension.COMPLIANCE, +0.01), (TraitDimension.INTELLIGENCE, +0.005)],
            ('training_failure', 'negative'): [(TraitDimension.COMPLIANCE, -0.005), (TraitDimension.PATIENCE, -0.005)],
            ('positive_interaction', 'positive'): [(TraitDimension.SOCIABILITY, +0.01), (TraitDimension.TRUST, +0.008)],
            ('negative_interaction', 'negative'): [(TraitDimension.TRUST, -0.01), (TraitDimension.SOCIABILITY, -0.005)],
            ('exploration_success', 'positive'): [(TraitDimension.CONFIDENCE, +0.008), (TraitDimension.CURIOSITY, +0.006)],
            ('scary_event', 'negative'): [(TraitDimension.CONFIDENCE, -0.01), (TraitDimension.TRUST, -0.005)],
            ('play_enjoyed', 'positive'): [(TraitDimension.PLAYFULNESS, +0.008), (TraitDimension.SOCIABILITY, +0.005)],
            ('ignored', 'negative'): [(TraitDimension.INDEPENDENCE, +0.01), (TraitDimension.SOCIABILITY, -0.008)],
            ('rewarded', 'positive'): [(TraitDimension.COMPLIANCE, +0.008), (TraitDimension.TRUST, +0.006)],
            ('punished', 'negative'): [(TraitDimension.TRUST, -0.01), (TraitDimension.AGGRESSION, +0.005)],
        }

        key = (experience_type, outcome)
        if key in drift_mappings:
            for dimension, change in drift_mappings[key]:
                scaled_change = change * impact * self.drift_rate * 100  # Scale by impact
                self.personality.adjust_trait(dimension, scaled_change)

    def consolidate_drift(self):
        """
        Consolidate recent experiences into long-term personality changes.

        Called periodically (e.g., every hour) to apply cumulative drift.
        """
        if len(self.experience_buffer) < 10:
            return  # Not enough data

        # Analyze patterns in recent experiences
        positive_count = sum(1 for exp in self.experience_buffer if exp['outcome'] == 'positive')
        negative_count = sum(1 for exp in self.experience_buffer if exp['outcome'] == 'negative')

        total = len(self.experience_buffer)
        positive_ratio = positive_count / total if total > 0 else 0.5

        # Overall positive experiences -> increase trust, sociability
        if positive_ratio > 0.7:
            self.personality.adjust_trait(TraitDimension.TRUST, +0.02)
            self.personality.adjust_trait(TraitDimension.SOCIABILITY, +0.015)
            self.personality.adjust_trait(TraitDimension.EMOTIONAL_STABILITY, +0.01)

        # Overall negative experiences -> decrease trust, increase independence
        elif positive_ratio < 0.3:
            self.personality.adjust_trait(TraitDimension.TRUST, -0.02)
            self.personality.adjust_trait(TraitDimension.INDEPENDENCE, +0.015)
            self.personality.adjust_trait(TraitDimension.EMOTIONAL_STABILITY, -0.01)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize drift system."""
        return {
            'drift_rate': self.drift_rate,
            'experience_buffer': self.experience_buffer
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], personality: MultiDimensionalPersonality) -> 'PersonalityDrift':
        """Deserialize drift system."""
        drift = cls(personality)
        drift.drift_rate = data['drift_rate']
        drift.experience_buffer = data['experience_buffer']
        return drift


class EnhancedPersonalitySystem:
    """
    Complete personality system integrating:
    - Multi-dimensional traits
    - Mood system
    - Personality drift
    """

    def __init__(self, base_personality: PersonalityType = None):
        """
        Initialize enhanced personality system.

        Args:
            base_personality: Starting personality type
        """
        self.personality = MultiDimensionalPersonality(base_personality)
        self.mood = MoodSystem()
        self.drift = PersonalityDrift(self.personality)

    def get_effective_trait(self, dimension: TraitDimension) -> float:
        """
        Get effective trait value including mood modifiers.

        Args:
            dimension: Trait to get

        Returns:
            Trait value adjusted by current mood
        """
        base_value = self.personality.get_trait(dimension)

        # Apply mood modifiers
        mood_mods = self.mood.get_mood_modifiers()

        # Map mood modifiers to trait dimensions
        modifier = 0.0
        dim_name = dimension.value

        # Check if mood affects this dimension
        for mod_name, mod_value in mood_mods.items():
            if dim_name in mod_name or mod_name.replace('_bonus', '').replace('_penalty', '') == dim_name:
                if 'bonus' in mod_name:
                    modifier += mod_value
                elif 'penalty' in mod_name:
                    modifier -= mod_value

        return np.clip(base_value + modifier, 0.0, 1.0)

    def record_experience(self, event_type: str, positive: bool, impact: float = 1.0):
        """
        Record an experience (affects mood and personality drift).

        Args:
            event_type: Type of event
            positive: Whether positive
            impact: How impactful
        """
        outcome = 'positive' if positive else 'negative'

        # Trigger mood change
        self.mood.trigger_mood_from_event(event_type, positive, intensity=impact)

        # Record for personality drift
        self.drift.record_experience(event_type, outcome, impact)

    def update(self):
        """Update mood and check for drift consolidation."""
        self.mood.update()

        # Periodically consolidate drift (every hour)
        # This would be called by the creature's update method

    def to_dict(self) -> Dict[str, Any]:
        """Serialize personality system."""
        return {
            'personality': self.personality.to_dict(),
            'mood': self.mood.to_dict(),
            'drift': self.drift.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedPersonalitySystem':
        """Deserialize personality system."""
        # Reconstruct personality
        personality_data = data['personality']
        base_type = PersonalityType(personality_data['base_personality']) if personality_data.get('base_personality') else None

        system = cls(base_personality=base_type)
        system.personality = MultiDimensionalPersonality.from_dict(personality_data)
        system.mood = MoodSystem.from_dict(data['mood'])
        system.drift = PersonalityDrift.from_dict(data['drift'], system.personality)

        return system
