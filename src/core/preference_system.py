"""
Preference System for Desktop Pal

Each pet develops individual preferences for toys, foods, activities, and times of day.
Preferences are learned through experience and influenced by personality.
"""
from typing import Dict, Any, Optional, Tuple, List
import random
import numpy as np


class PreferenceCategory(str):
    """Categories of preferences."""
    TOY = "toy"
    FOOD = "food"
    ACTIVITY = "activity"
    TIME_OF_DAY = "time_of_day"
    INTERACTION_TYPE = "interaction_type"


class PreferenceSystem:
    """
    Manages individual preferences that develop over time.

    Preferences are rated on a scale of 0-100:
    - 0-20: Dislikes / Avoids
    - 20-40: Not preferred
    - 40-60: Neutral
    - 60-80: Likes
    - 80-100: Loves / Favorite

    Preferences change based on:
    - Experiences (positive/negative)
    - Personality traits
    - Mood during experience
    - Consistency of experiences
    """

    def __init__(self, personality_type: Optional[str] = None):
        """
        Initialize preference system.

        Args:
            personality_type: Personality to influence initial preferences
        """
        self.personality_type = personality_type

        # Preference scores (item_name: score 0-100)
        self.toy_preferences = {}
        self.food_preferences = {}
        self.activity_preferences = {}
        self.time_preferences = {
            'morning': 50,
            'afternoon': 50,
            'evening': 50,
            'night': 50
        }
        self.interaction_preferences = {
            'petting': 50,
            'playing': 50,
            'training': 50,
            'talking': 50,
            'grooming': 50
        }

        # Experience tracking
        self.experiences = []  # List of experiences with each item
        self.favorite_toy = None
        self.least_favorite_toy = None
        self.favorite_food = None
        self.least_favorite_food = None

        # Initialize based on personality
        if personality_type:
            self._initialize_personality_preferences(personality_type)

    def _initialize_personality_preferences(self, personality: str):
        """Set initial preferences based on personality."""
        # Personality-based preference biases
        personality_biases = {
            'playful': {
                'toy_bias': 20,
                'activity_preferences': {'playing': 70, 'training': 60}
            },
            'lazy': {
                'toy_bias': -10,
                'activity_preferences': {'playing': 30, 'training': 20, 'petting': 70}
            },
            'energetic': {
                'toy_bias': 15,
                'activity_preferences': {'playing': 80, 'training': 70}
            },
            'shy': {
                'interaction_preferences': {'petting': 40, 'talking': 40, 'grooming': 30}
            },
            'curious': {
                'activity_preferences': {'playing': 65, 'training': 75}
            },
            'affectionate': {
                'interaction_preferences': {'petting': 80, 'grooming': 70}
            }
        }

        if personality in personality_biases:
            biases = personality_biases[personality]

            # Apply activity preference biases
            if 'activity_preferences' in biases:
                for activity, value in biases['activity_preferences'].items():
                    self.activity_preferences[activity] = value

            # Apply interaction preference biases
            if 'interaction_preferences' in biases:
                for interaction, value in biases['interaction_preferences'].items():
                    self.interaction_preferences[interaction] = value

    def record_experience(self, category: str, item: str, enjoyment: float,
                         context: Optional[Dict[str, Any]] = None):
        """
        Record an experience with an item.

        Args:
            category: Category (toy, food, activity, etc.)
            item: Specific item name
            enjoyment: How much they enjoyed it (-1 to 1)
            context: Additional context (mood, time of day, etc.)
        """
        # Record experience
        experience = {
            'category': category,
            'item': item,
            'enjoyment': enjoyment,
            'context': context or {},
            'timestamp': np.random.random()  # Simplified timestamp
        }
        self.experiences.append(experience)

        # Keep last 200 experiences
        if len(self.experiences) > 200:
            self.experiences = self.experiences[-200:]

        # Update preference
        self._update_preference(category, item, enjoyment)

    def _update_preference(self, category: str, item: str, enjoyment: float):
        """
        Update preference score based on experience.

        Args:
            category: Category of preference
            item: Item name
            enjoyment: Enjoyment from experience (-1 to 1)
        """
        # Get appropriate preference dict
        pref_dict = self._get_preference_dict(category)
        if pref_dict is None:
            return

        # Initialize if new
        if item not in pref_dict:
            pref_dict[item] = 50  # Start neutral

        current = pref_dict[item]

        # Calculate change (larger changes near neutral, smaller at extremes)
        if enjoyment > 0:
            # Positive experience
            change = enjoyment * 10 * (1 - current / 100)
        else:
            # Negative experience
            change = enjoyment * 10 * (current / 100)

        # Update preference
        new_pref = max(0, min(100, current + change))
        pref_dict[item] = new_pref

        # Update favorites
        self._update_favorites(category)

    def _get_preference_dict(self, category: str) -> Optional[Dict[str, float]]:
        """Get the appropriate preference dictionary for a category."""
        if category == PreferenceCategory.TOY:
            return self.toy_preferences
        elif category == PreferenceCategory.FOOD:
            return self.food_preferences
        elif category == PreferenceCategory.ACTIVITY:
            return self.activity_preferences
        elif category == PreferenceCategory.INTERACTION_TYPE:
            return self.interaction_preferences
        return None

    def _update_favorites(self, category: str):
        """Update favorite and least favorite for a category."""
        pref_dict = self._get_preference_dict(category)
        if not pref_dict or len(pref_dict) == 0:
            return

        sorted_prefs = sorted(pref_dict.items(), key=lambda x: x[1], reverse=True)

        if category == PreferenceCategory.TOY:
            self.favorite_toy = sorted_prefs[0][0] if sorted_prefs[0][1] > 60 else None
            self.least_favorite_toy = sorted_prefs[-1][0] if sorted_prefs[-1][1] < 40 else None
        elif category == PreferenceCategory.FOOD:
            self.favorite_food = sorted_prefs[0][0] if sorted_prefs[0][1] > 60 else None
            self.least_favorite_food = sorted_prefs[-1][0] if sorted_prefs[-1][1] < 40 else None

    def get_preference(self, category: str, item: str) -> float:
        """
        Get preference score for an item.

        Args:
            category: Category of item
            item: Item name

        Returns:
            Preference score (0-100)
        """
        pref_dict = self._get_preference_dict(category)
        if pref_dict is None:
            return 50  # Neutral default

        return pref_dict.get(item, 50)

    def get_preference_description(self, score: float) -> str:
        """Get text description of preference level."""
        if score >= 80:
            return "Absolutely loves"
        elif score >= 60:
            return "Really likes"
        elif score >= 40:
            return "Neutral about"
        elif score >= 20:
            return "Doesn't prefer"
        else:
            return "Dislikes"

    def get_favorites(self) -> Dict[str, Optional[str]]:
        """Get current favorites."""
        return {
            'favorite_toy': self.favorite_toy,
            'least_favorite_toy': self.least_favorite_toy,
            'favorite_food': self.favorite_food,
            'least_favorite_food': self.least_favorite_food
        }

    def get_top_preferences(self, category: str, limit: int = 3) -> List[Tuple[str, float]]:
        """
        Get top preferred items in a category.

        Args:
            category: Category to check
            limit: Max number of items to return

        Returns:
            List of (item_name, score) tuples
        """
        pref_dict = self._get_preference_dict(category)
        if not pref_dict:
            return []

        sorted_prefs = sorted(pref_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_prefs[:limit]

    def should_show_excitement_for_item(self, category: str, item: str) -> Tuple[bool, float]:
        """
        Check if pet should show excitement for an item.

        Args:
            category: Category of item
            item: Item name

        Returns:
            Tuple of (should_show_excitement, excitement_level)
        """
        preference = self.get_preference(category, item)

        if preference >= 80:
            return True, 1.0  # Maximum excitement
        elif preference >= 70:
            return True, 0.7
        elif preference >= 60:
            return True, 0.4
        else:
            return False, 0.0

    def should_show_dislike_for_item(self, category: str, item: str) -> Tuple[bool, float]:
        """
        Check if pet should show dislike for an item.

        Args:
            category: Category of item
            item: Item name

        Returns:
            Tuple of (should_show_dislike, dislike_level)
        """
        preference = self.get_preference(category, item)

        if preference <= 20:
            return True, 1.0  # Strong dislike
        elif preference <= 30:
            return True, 0.6
        elif preference <= 40:
            return True, 0.3
        else:
            return False, 0.0

    def get_reaction_to_item(self, category: str, item: str) -> Dict[str, Any]:
        """
        Get expected reaction to an item.

        Args:
            category: Category of item
            item: Item name

        Returns:
            Dictionary describing reaction
        """
        preference = self.get_preference(category, item)
        description = self.get_preference_description(preference)

        # Determine reaction type
        if preference >= 80:
            reaction = "ecstatic"
            animation = "jump_for_joy"
        elif preference >= 60:
            reaction = "happy"
            animation = "wag_tail"
        elif preference >= 40:
            reaction = "neutral"
            animation = "sniff"
        elif preference >= 20:
            reaction = "reluctant"
            animation = "turn_away"
        else:
            reaction = "refuse"
            animation = "reject"

        return {
            'preference_score': preference,
            'description': description,
            'reaction': reaction,
            'animation': animation,
            'will_accept': preference >= 20
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get preference statistics."""
        return {
            'favorites': self.get_favorites(),
            'total_experiences': len(self.experiences),
            'top_toys': self.get_top_preferences(PreferenceCategory.TOY, 3),
            'top_foods': self.get_top_preferences(PreferenceCategory.FOOD, 3),
            'top_activities': self.get_top_preferences(PreferenceCategory.ACTIVITY, 3),
            'interaction_preferences': self.interaction_preferences.copy(),
            'time_preferences': self.time_preferences.copy()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize preference system state."""
        return {
            'personality_type': self.personality_type,
            'toy_preferences': self.toy_preferences,
            'food_preferences': self.food_preferences,
            'activity_preferences': self.activity_preferences,
            'time_preferences': self.time_preferences,
            'interaction_preferences': self.interaction_preferences,
            'experiences': self.experiences[-100:],  # Last 100
            'favorite_toy': self.favorite_toy,
            'least_favorite_toy': self.least_favorite_toy,
            'favorite_food': self.favorite_food,
            'least_favorite_food': self.least_favorite_food
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreferenceSystem':
        """Deserialize preference system state."""
        system = cls(personality_type=data.get('personality_type'))

        system.toy_preferences = data.get('toy_preferences', {})
        system.food_preferences = data.get('food_preferences', {})
        system.activity_preferences = data.get('activity_preferences', {})
        system.time_preferences = data.get('time_preferences', system.time_preferences)
        system.interaction_preferences = data.get('interaction_preferences', system.interaction_preferences)
        system.experiences = data.get('experiences', [])
        system.favorite_toy = data.get('favorite_toy')
        system.least_favorite_toy = data.get('least_favorite_toy')
        system.favorite_food = data.get('favorite_food')
        system.least_favorite_food = data.get('least_favorite_food')

        return system
