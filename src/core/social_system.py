"""
Phase 9: Social System

Manages pet-to-pet relationships and interactions.
"""
import time
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class RelationshipType(Enum):
    """Types of relationships between pets."""
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    BEST_FRIEND = "best_friend"
    RIVAL = "rival"
    ENEMY = "enemy"


class InteractionType(Enum):
    """Types of pet-to-pet interactions."""
    PLAY_TOGETHER = "play_together"
    GROOM_EACH_OTHER = "groom_each_other"
    SHARE_FOOD = "share_food"
    SHARE_TOY = "share_toy"
    FIGHT = "fight"
    ARGUE = "argue"
    COMFORT = "comfort"
    IGNORE = "ignore"
    FOLLOW = "follow"
    CUDDLE = "cuddle"
    COMPETE = "compete"
    TEACH = "teach"


class SocialSystem:
    """
    Manages social relationships and interactions between pets.

    Features:
    - Relationship tracking (friendship/rivalry)
    - Interaction history
    - Compatibility calculation
    - Social preferences
    """

    def __init__(self, pet_id: str):
        """
        Initialize social system.

        Args:
            pet_id: Unique ID of this pet
        """
        self.pet_id = pet_id

        # Relationships with other pets
        self.relationships = {}  # other_pet_id: relationship_data

        # Interaction history
        self.interaction_history = []  # List of interaction events
        self.total_interactions = 0

        # Social preferences
        self.social_energy = 50.0  # 0-100, how much social interaction desired
        self.sociability = random.uniform(0.3, 1.0)  # Personality trait
        self.tolerance = random.uniform(0.3, 1.0)  # Tolerance for annoying behaviors

        # Best friend
        self.best_friend_id = None

        # Statistics
        self.total_positive_interactions = 0
        self.total_negative_interactions = 0

    def meet_pet(self, other_pet_id: str, other_personality: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meet another pet for the first time.

        Args:
            other_pet_id: ID of the other pet
            other_personality: Personality info of other pet

        Returns:
            First meeting results
        """
        if other_pet_id in self.relationships:
            return {'first_meeting': False, 'already_know': True}

        # Create new relationship
        initial_impression = self._calculate_initial_impression(other_personality)

        relationship = {
            'pet_id': other_pet_id,
            'friendship': initial_impression,  # -100 to 100
            'met_time': time.time(),
            'interactions_count': 0,
            'last_interaction_time': time.time(),
            'relationship_type': self._determine_relationship_type(initial_impression),
            'compatibility': self._calculate_compatibility(other_personality),
            'positive_interactions': 0,
            'negative_interactions': 0
        }

        self.relationships[other_pet_id] = relationship

        return {
            'first_meeting': True,
            'initial_impression': initial_impression,
            'relationship_type': relationship['relationship_type'].value,
            'compatibility': relationship['compatibility']
        }

    def _calculate_initial_impression(self, other_personality: Dict[str, Any]) -> float:
        """Calculate initial impression on first meeting."""
        # Random component
        impression = random.uniform(-20, 40)

        # Personality factors
        if 'friendliness' in other_personality:
            impression += (other_personality['friendliness'] - 50) * 0.3

        if 'energy' in other_personality:
            # Similar energy levels = better impression
            energy_diff = abs(self.sociability * 100 - other_personality['energy'])
            impression -= energy_diff * 0.1

        return max(-100, min(100, impression))

    def _calculate_compatibility(self, other_personality: Dict[str, Any]) -> float:
        """Calculate long-term compatibility (0-1)."""
        compatibility = 0.5

        # Personality similarity increases compatibility
        if 'energy' in other_personality:
            energy_similarity = 1.0 - abs(self.sociability - other_personality['energy'] / 100.0)
            compatibility += energy_similarity * 0.3

        if 'friendliness' in other_personality:
            if other_personality['friendliness'] > 70:
                compatibility += 0.2

        return max(0.0, min(1.0, compatibility))

    def _determine_relationship_type(self, friendship: float) -> RelationshipType:
        """Determine relationship type from friendship level."""
        if friendship >= 80:
            return RelationshipType.BEST_FRIEND
        elif friendship >= 40:
            return RelationshipType.FRIEND
        elif friendship >= 0:
            return RelationshipType.ACQUAINTANCE
        elif friendship >= -40:
            return RelationshipType.RIVAL
        else:
            return RelationshipType.ENEMY

    def interact_with_pet(self, other_pet_id: str, interaction_type: str,
                         success: bool = True) -> Dict[str, Any]:
        """
        Interact with another pet.

        Args:
            other_pet_id: ID of other pet
            interaction_type: Type of interaction
            success: Whether interaction was successful

        Returns:
            Interaction results
        """
        # Ensure relationship exists
        if other_pet_id not in self.relationships:
            return {'error': 'no_relationship'}

        relationship = self.relationships[other_pet_id]

        # Calculate friendship change
        friendship_change = self._calculate_friendship_change(
            interaction_type, success, relationship['friendship']
        )

        # Apply change
        old_friendship = relationship['friendship']
        relationship['friendship'] = max(-100, min(100, old_friendship + friendship_change))
        relationship['interactions_count'] += 1
        relationship['last_interaction_time'] = time.time()

        # Update counters
        if friendship_change > 0:
            relationship['positive_interactions'] += 1
            self.total_positive_interactions += 1
        elif friendship_change < 0:
            relationship['negative_interactions'] += 1
            self.total_negative_interactions += 1

        # Update relationship type
        old_type = relationship['relationship_type']
        relationship['relationship_type'] = self._determine_relationship_type(
            relationship['friendship']
        )

        # Record in history
        interaction_event = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'other_pet_id': other_pet_id,
            'interaction_type': interaction_type,
            'success': success,
            'friendship_change': friendship_change,
            'new_friendship': relationship['friendship']
        }
        self.interaction_history.append(interaction_event)
        self.total_interactions += 1

        # Update best friend
        self._update_best_friend()

        # Update social energy
        self._update_social_energy(interaction_type)

        return {
            'interaction': interaction_type,
            'success': success,
            'friendship_change': friendship_change,
            'old_friendship': old_friendship,
            'new_friendship': relationship['friendship'],
            'old_type': old_type.value,
            'new_type': relationship['relationship_type'].value,
            'type_changed': old_type != relationship['relationship_type']
        }

    def _calculate_friendship_change(self, interaction_type: str, success: bool,
                                    current_friendship: float) -> float:
        """Calculate friendship change from interaction."""
        # Base changes by interaction type
        changes = {
            'play_together': 10.0 if success else -2.0,
            'groom_each_other': 8.0 if success else 0.0,
            'share_food': 12.0 if success else -5.0,
            'share_toy': 8.0 if success else -3.0,
            'fight': -15.0,
            'argue': -8.0,
            'comfort': 10.0 if success else 0.0,
            'ignore': -2.0,
            'follow': 3.0,
            'cuddle': 12.0 if success else -1.0,
            'compete': 5.0 if success else -5.0,
            'teach': 8.0 if success else -2.0
        }

        change = changes.get(interaction_type, 0.0)

        # Diminishing returns for high friendship
        if current_friendship > 60:
            change *= 0.7
        elif current_friendship > 80:
            change *= 0.5

        # Amplify for low friendship (easier to improve from bad)
        if current_friendship < -40:
            change *= 1.3

        return change

    def _update_social_energy(self, interaction_type: str):
        """Update social energy based on interaction."""
        # Positive interactions restore social energy
        positive = ['play_together', 'cuddle', 'groom_each_other', 'share_food']
        negative = ['fight', 'argue']

        if interaction_type in positive:
            self.social_energy = min(100.0, self.social_energy + 5.0)
        elif interaction_type in negative:
            self.social_energy = max(0.0, self.social_energy - 10.0)

    def _update_best_friend(self):
        """Update best friend based on highest friendship."""
        if not self.relationships:
            self.best_friend_id = None
            return

        # Find pet with highest friendship
        best = max(self.relationships.items(), key=lambda x: x[1]['friendship'])

        # Must have friendship >= 60 to be best friend
        if best[1]['friendship'] >= 60:
            self.best_friend_id = best[0]
        else:
            self.best_friend_id = None

    def get_relationship(self, other_pet_id: str) -> Optional[Dict[str, Any]]:
        """Get relationship data with another pet."""
        if other_pet_id not in self.relationships:
            return None

        rel = self.relationships[other_pet_id].copy()
        rel['relationship_type'] = rel['relationship_type'].value
        return rel

    def get_friends(self, min_friendship: float = 40.0) -> List[str]:
        """Get list of friend pet IDs."""
        friends = []
        for pet_id, rel in self.relationships.items():
            if rel['friendship'] >= min_friendship:
                friends.append(pet_id)
        return friends

    def get_rivals(self, max_friendship: float = -20.0) -> List[str]:
        """Get list of rival pet IDs."""
        rivals = []
        for pet_id, rel in self.relationships.items():
            if rel['friendship'] <= max_friendship:
                rivals.append(pet_id)
        return rivals

    def wants_social_interaction(self) -> Tuple[bool, str]:
        """Check if pet wants social interaction."""
        if self.social_energy < 30:
            return True, "lonely"
        elif self.social_energy < 50 and self.sociability > 0.7:
            return True, "wants_company"
        elif len(self.get_friends()) == 0:
            return True, "no_friends"
        else:
            return False, "content"

    def suggest_interaction(self, other_pet_id: str) -> str:
        """Suggest appropriate interaction with another pet."""
        if other_pet_id not in self.relationships:
            return "meet"

        relationship = self.relationships[other_pet_id]
        friendship = relationship['friendship']

        if friendship >= 60:
            return random.choice(['play_together', 'cuddle', 'groom_each_other'])
        elif friendship >= 20:
            return random.choice(['play_together', 'share_toy', 'follow'])
        elif friendship >= -20:
            return random.choice(['play_together', 'ignore', 'compete'])
        else:
            return random.choice(['ignore', 'argue', 'compete'])

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive social status."""
        return {
            'pet_id': self.pet_id,
            'known_pets': len(self.relationships),
            'friends': len(self.get_friends()),
            'rivals': len(self.get_rivals()),
            'best_friend': self.best_friend_id,
            'social_energy': self.social_energy,
            'sociability': self.sociability,
            'tolerance': self.tolerance,
            'total_interactions': self.total_interactions,
            'positive_interactions': self.total_positive_interactions,
            'negative_interactions': self.total_negative_interactions,
            'wants_interaction': self.wants_social_interaction()[0]
        }

    def get_relationship_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all relationships."""
        summary = []
        for pet_id, rel in self.relationships.items():
            summary.append({
                'pet_id': pet_id,
                'friendship': rel['friendship'],
                'relationship_type': rel['relationship_type'].value,
                'interactions': rel['interactions_count'],
                'days_known': (time.time() - rel['met_time']) / 86400.0
            })

        # Sort by friendship (highest first)
        summary.sort(key=lambda x: x['friendship'], reverse=True)
        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        relationships_dict = {}
        for pet_id, rel in self.relationships.items():
            rel_copy = rel.copy()
            rel_copy['relationship_type'] = rel['relationship_type'].value
            relationships_dict[pet_id] = rel_copy

        return {
            'pet_id': self.pet_id,
            'relationships': relationships_dict,
            'interaction_history': self.interaction_history.copy(),
            'total_interactions': self.total_interactions,
            'social_energy': self.social_energy,
            'sociability': self.sociability,
            'tolerance': self.tolerance,
            'best_friend_id': self.best_friend_id,
            'total_positive_interactions': self.total_positive_interactions,
            'total_negative_interactions': self.total_negative_interactions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialSystem':
        """Deserialize from dictionary."""
        system = cls(pet_id=data.get('pet_id', 'unknown'))

        # Restore relationships
        relationships_data = data.get('relationships', {})
        for pet_id, rel in relationships_data.items():
            rel_copy = rel.copy()
            rel_copy['relationship_type'] = RelationshipType(rel['relationship_type'])
            system.relationships[pet_id] = rel_copy

        system.interaction_history = data.get('interaction_history', [])
        system.total_interactions = data.get('total_interactions', 0)
        system.social_energy = data.get('social_energy', 50.0)
        system.sociability = data.get('sociability', 0.5)
        system.tolerance = data.get('tolerance', 0.5)
        system.best_friend_id = data.get('best_friend_id')
        system.total_positive_interactions = data.get('total_positive_interactions', 0)
        system.total_negative_interactions = data.get('total_negative_interactions', 0)

        return system
