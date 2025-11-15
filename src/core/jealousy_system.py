"""
Phase 9: Jealousy and Competition System

Manages jealousy when owner gives attention to other pets and competition for resources.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class JealousyLevel(Enum):
    """Jealousy intensity levels."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class CompetitionType(Enum):
    """Types of resource competition."""
    FOOD = "food"
    TOY = "toy"
    ATTENTION = "attention"
    SLEEPING_SPOT = "sleeping_spot"
    TREAT = "treat"


class JealousySystem:
    """
    Manages jealousy and competition between pets.

    Features:
    - Jealousy when owner gives attention to others
    - Competition for resources
    - Rivalry development
    - Behavioral changes from jealousy
    """

    def __init__(self, pet_id: str):
        """
        Initialize jealousy system.

        Args:
            pet_id: This pet's ID
        """
        self.pet_id = pet_id

        # Jealousy levels toward other pets
        self.jealousy = {}  # other_pet_id: jealousy_level (0-100)

        # Competition tracking
        self.competition_history = []
        self.total_competitions = 0
        self.competitions_won = 0
        self.competitions_lost = 0

        # Personality factors
        self.possessiveness = random.uniform(0.3, 1.0)  # How possessive of owner/resources
        self.competitiveness = random.uniform(0.3, 1.0)  # How competitive

        # Current jealousy state
        self.is_jealous = False
        self.jealous_of = None  # Pet ID currently jealous of

        # Attention tracking
        self.attention_received = 0  # Counter
        self.last_attention_time = time.time()

        # Rivalry
        self.rivals = []  # List of rival pet IDs

    def witness_attention_to_other(self, other_pet_id: str, attention_type: str,
                                   attention_duration: float = 1.0) -> Dict[str, Any]:
        """
        Pet witnesses owner giving attention to another pet.

        Args:
            other_pet_id: ID of pet receiving attention
            attention_type: Type of attention (petting, playing, feeding, etc.)
            attention_duration: How long (minutes)

        Returns:
            Jealousy response
        """
        # Calculate jealousy increase
        base_jealousy = 10.0 * attention_duration

        # Modifiers
        if attention_type in ['feeding', 'treat']:
            base_jealousy *= 1.5  # Food is very important
        elif attention_type in ['playing', 'cuddling']:
            base_jealousy *= 1.3
        elif attention_type in ['grooming', 'petting']:
            base_jealousy *= 1.1

        # Personality factor
        base_jealousy *= self.possessiveness

        # Time since last attention matters
        hours_since_attention = (time.time() - self.last_attention_time) / 3600.0
        if hours_since_attention > 2.0:
            base_jealousy *= 1.5  # More jealous if haven't gotten attention
        elif hours_since_attention < 0.5:
            base_jealousy *= 0.7  # Less jealous if just got attention

        # Update jealousy toward other pet
        if other_pet_id not in self.jealousy:
            self.jealousy[other_pet_id] = 0.0

        old_jealousy = self.jealousy[other_pet_id]
        self.jealousy[other_pet_id] = min(100.0, old_jealousy + base_jealousy)

        # Update state
        self.is_jealous = True
        self.jealous_of = other_pet_id

        # Determine jealousy level
        jealousy_level = self._get_jealousy_level(self.jealousy[other_pet_id])

        # Behavioral response
        response = self._generate_jealousy_response(jealousy_level)

        return {
            'is_jealous': True,
            'jealous_of': other_pet_id,
            'jealousy_increase': base_jealousy,
            'total_jealousy': self.jealousy[other_pet_id],
            'jealousy_level': jealousy_level.value,
            'response': response
        }

    def receive_attention(self, attention_type: str, duration: float = 1.0):
        """
        Pet receives attention from owner.

        Args:
            attention_type: Type of attention
            duration: Duration in minutes
        """
        self.attention_received += 1
        self.last_attention_time = time.time()

        # Reduce jealousy toward all pets
        for pet_id in self.jealousy.keys():
            reduction = 15.0 * duration
            self.jealousy[pet_id] = max(0.0, self.jealousy[pet_id] - reduction)

        # Clear jealous state if jealousy low enough
        if all(j < 20.0 for j in self.jealousy.values()):
            self.is_jealous = False
            self.jealous_of = None

    def compete_for_resource(self, other_pet_id: str, resource_type: str) -> Dict[str, Any]:
        """
        Compete with another pet for a resource.

        Args:
            other_pet_id: Competing pet's ID
            resource_type: What they're competing for

        Returns:
            Competition results
        """
        # Calculate win probability
        base_prob = 0.5  # 50/50 base

        # Possessiveness increases chance
        base_prob += (self.possessiveness - 0.5) * 0.2

        # Competitiveness increases chance
        base_prob += (self.competitiveness - 0.5) * 0.2

        # Jealousy increases desperation
        if other_pet_id in self.jealousy:
            jealousy_boost = (self.jealousy[other_pet_id] / 100.0) * 0.3
            base_prob += jealousy_boost

        # Resource type modifiers
        if resource_type == CompetitionType.FOOD.value:
            base_prob += 0.1  # Slightly more motivated for food
        elif resource_type == CompetitionType.ATTENTION.value:
            base_prob += 0.15  # Very motivated for attention

        # Clamp probability
        base_prob = max(0.0, min(1.0, base_prob))

        # Determine winner
        self_wins = random.random() < base_prob

        # Record competition
        self.total_competitions += 1
        if self_wins:
            self.competitions_won += 1
        else:
            self.competitions_lost += 1

        competition = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'other_pet_id': other_pet_id,
            'resource_type': resource_type,
            'winner': self.pet_id if self_wins else other_pet_id,
            'self_wins': self_wins
        }
        self.competition_history.append(competition)

        # Update jealousy/rivalry
        if not self_wins:
            # Losing increases jealousy
            if other_pet_id not in self.jealousy:
                self.jealousy[other_pet_id] = 0.0
            self.jealousy[other_pet_id] = min(100.0, self.jealousy[other_pet_id] + 10.0)

            # May become rivals
            self._check_rivalry(other_pet_id)
        else:
            # Winning reduces jealousy
            if other_pet_id in self.jealousy:
                self.jealousy[other_pet_id] = max(0.0, self.jealousy[other_pet_id] - 5.0)

        return {
            'winner': self.pet_id if self_wins else other_pet_id,
            'self_wins': self_wins,
            'resource_type': resource_type,
            'probability': base_prob,
            'jealousy_change': -5.0 if self_wins else 10.0
        }

    def _check_rivalry(self, other_pet_id: str):
        """Check if should become rivals with another pet."""
        if other_pet_id in self.rivals:
            return

        # Count recent losses to this pet
        recent_competitions = [
            c for c in self.competition_history
            if c['other_pet_id'] == other_pet_id
            and time.time() - c['timestamp'] < 86400 * 7  # Last week
        ]

        if not recent_competitions:
            return

        losses = sum(1 for c in recent_competitions if not c['self_wins'])

        # Become rivals if lost 3+ times
        if losses >= 3:
            if other_pet_id not in self.rivals:
                self.rivals.append(other_pet_id)

    def _get_jealousy_level(self, jealousy_value: float) -> JealousyLevel:
        """Get jealousy level from value."""
        if jealousy_value < 20:
            return JealousyLevel.NONE
        elif jealousy_value < 40:
            return JealousyLevel.MILD
        elif jealousy_value < 60:
            return JealousyLevel.MODERATE
        elif jealousy_value < 80:
            return JealousyLevel.HIGH
        else:
            return JealousyLevel.EXTREME

    def _generate_jealousy_response(self, level: JealousyLevel) -> str:
        """Generate behavioral response to jealousy."""
        responses = {
            JealousyLevel.NONE: "calm",
            JealousyLevel.MILD: random.choice(["whines", "watches_sadly", "sits_nearby"]),
            JealousyLevel.MODERATE: random.choice(["pushes_between", "demands_attention", "vocalizes"]),
            JealousyLevel.HIGH: random.choice(["blocks_other_pet", "steals_toy", "acts_out"]),
            JealousyLevel.EXTREME: random.choice(["aggressive_display", "destroys_item", "refuses_to_share"])
        }
        return responses.get(level, "calm")

    def get_most_jealous_of(self) -> Optional[Tuple[str, float]]:
        """Get pet most jealous of."""
        if not self.jealousy:
            return None

        max_jealousy = max(self.jealousy.items(), key=lambda x: x[1])
        if max_jealousy[1] > 20.0:  # Only if significant jealousy
            return max_jealousy
        return None

    def is_rival(self, other_pet_id: str) -> bool:
        """Check if another pet is a rival."""
        return other_pet_id in self.rivals

    def decay_jealousy(self, hours_elapsed: float):
        """Natural jealousy decay over time."""
        decay_rate = 2.0 * hours_elapsed  # 2 points per hour

        for pet_id in list(self.jealousy.keys()):
            self.jealousy[pet_id] = max(0.0, self.jealousy[pet_id] - decay_rate)

            # Remove if completely gone
            if self.jealousy[pet_id] == 0.0:
                del self.jealousy[pet_id]

        # Update state
        if not self.jealousy or all(j < 20.0 for j in self.jealousy.values()):
            self.is_jealous = False
            self.jealous_of = None

    def get_status(self) -> Dict[str, Any]:
        """Get jealousy status."""
        most_jealous = self.get_most_jealous_of()

        return {
            'is_jealous': self.is_jealous,
            'jealous_of': self.jealous_of,
            'most_jealous_of': most_jealous[0] if most_jealous else None,
            'max_jealousy_level': most_jealous[1] if most_jealous else 0.0,
            'rivals': self.rivals.copy(),
            'rival_count': len(self.rivals),
            'possessiveness': self.possessiveness,
            'competitiveness': self.competitiveness,
            'total_competitions': self.total_competitions,
            'competitions_won': self.competitions_won,
            'competitions_lost': self.competitions_lost,
            'win_rate': (
                self.competitions_won / max(1, self.total_competitions)
            ),
            'attention_received': self.attention_received,
            'hours_since_attention': (time.time() - self.last_attention_time) / 3600.0
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'pet_id': self.pet_id,
            'jealousy': self.jealousy.copy(),
            'competition_history': self.competition_history.copy(),
            'total_competitions': self.total_competitions,
            'competitions_won': self.competitions_won,
            'competitions_lost': self.competitions_lost,
            'possessiveness': self.possessiveness,
            'competitiveness': self.competitiveness,
            'is_jealous': self.is_jealous,
            'jealous_of': self.jealous_of,
            'attention_received': self.attention_received,
            'last_attention_time': self.last_attention_time,
            'rivals': self.rivals.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JealousySystem':
        """Deserialize from dictionary."""
        system = cls(pet_id=data.get('pet_id', 'unknown'))
        system.jealousy = data.get('jealousy', {})
        system.competition_history = data.get('competition_history', [])
        system.total_competitions = data.get('total_competitions', 0)
        system.competitions_won = data.get('competitions_won', 0)
        system.competitions_lost = data.get('competitions_lost', 0)
        system.possessiveness = data.get('possessiveness', 0.5)
        system.competitiveness = data.get('competitiveness', 0.5)
        system.is_jealous = data.get('is_jealous', False)
        system.jealous_of = data.get('jealous_of')
        system.attention_received = data.get('attention_received', 0)
        system.last_attention_time = data.get('last_attention_time', time.time())
        system.rivals = data.get('rivals', [])
        return system
