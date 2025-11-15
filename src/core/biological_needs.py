"""
Phase 8: Biological Needs System

Handles bathroom needs and grooming/cleanliness for realistic pet simulation.
"""
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum


class CleanlinessLevel(Enum):
    """Cleanliness levels."""
    PRISTINE = "pristine"      # 90-100
    CLEAN = "clean"            # 70-90
    SLIGHTLY_DIRTY = "slightly_dirty"  # 50-70
    DIRTY = "dirty"            # 30-50
    VERY_DIRTY = "very_dirty"  # 10-30
    FILTHY = "filthy"          # 0-10


class BathroomNeedsSystem:
    """
    Manages bathroom needs (bladder and bowel).

    Features:
    - Bladder and bowel fill over time
    - Accidents if not attended to
    - Training affects accident probability
    - Age affects control (babies have less control)
    """

    def __init__(self, age_days: float = 0):
        """
        Initialize bathroom needs.

        Args:
            age_days: Age in days (affects bladder/bowel control)
        """
        self.bladder = 0.0  # 0-100, urge to urinate
        self.bowel = 0.0    # 0-100, urge to defecate

        # Fill rates (per hour)
        self.bladder_fill_rate = 8.0  # ~12.5 hours to fill
        self.bowel_fill_rate = 4.0    # ~25 hours to fill

        # Last bathroom times
        self.last_urination_time = time.time()
        self.last_defecation_time = time.time()

        # Accident history
        self.total_accidents = 0
        self.recent_accidents = 0  # Last 24 hours
        self.last_accident_time = 0
        self.accident_history = []  # List of accident events

        # House training progress
        self.house_trained = False
        self.training_level = 0.0  # 0-1, reduces accident probability

        # Age affects control
        self.age_days = age_days
        self.bladder_control = self._calculate_bladder_control(age_days)

    def _calculate_bladder_control(self, age_days: float) -> float:
        """
        Calculate bladder control based on age.

        Args:
            age_days: Age in days

        Returns:
            Control level 0-1 (higher = better control)
        """
        if age_days < 30:  # Baby (< 1 month)
            return 0.3
        elif age_days < 90:  # Young (< 3 months)
            return 0.5
        elif age_days < 180:  # Adolescent (< 6 months)
            return 0.7
        elif age_days < 365 * 8:  # Adult
            return 1.0
        else:  # Senior (> 8 years)
            return 0.8

    def update(self, hours_elapsed: float):
        """
        Update bladder and bowel levels.

        Args:
            hours_elapsed: Hours since last update
        """
        # Fill bladder and bowel
        self.bladder = min(100.0, self.bladder + self.bladder_fill_rate * hours_elapsed)
        self.bowel = min(100.0, self.bowel + self.bowel_fill_rate * hours_elapsed)

        # Clean up old accidents from history
        current_time = time.time()
        self.accident_history = [
            acc for acc in self.accident_history
            if current_time - acc['timestamp'] < 86400  # Keep last 24h
        ]
        self.recent_accidents = len(self.accident_history)

    def use_bathroom(self, bathroom_type: str = 'both') -> Dict[str, Any]:
        """
        Pet uses the bathroom.

        Args:
            bathroom_type: 'urinate', 'defecate', or 'both'

        Returns:
            Dictionary with results
        """
        result = {
            'success': True,
            'relief_amount': 0.0,
            'bladder_emptied': False,
            'bowel_emptied': False,
            'happiness_gain': 0.0
        }

        current_time = time.time()

        # Urinate
        if bathroom_type in ['urinate', 'both'] and self.bladder > 0:
            relief = self.bladder
            self.bladder = 0.0
            self.last_urination_time = current_time
            result['bladder_emptied'] = True
            result['relief_amount'] += relief

        # Defecate
        if bathroom_type in ['defecate', 'both'] and self.bowel > 0:
            relief = self.bowel
            self.bowel = 0.0
            self.last_defecation_time = current_time
            result['bowel_emptied'] = True
            result['relief_amount'] += relief

        # Happiness from relief (higher urgency = more relief)
        if result['relief_amount'] > 0:
            result['happiness_gain'] = min(10.0, result['relief_amount'] / 10.0)

        # Improve training
        if result['bladder_emptied'] or result['bowel_emptied']:
            self.training_level = min(1.0, self.training_level + 0.01)
            if self.training_level >= 0.9:
                self.house_trained = True

        return result

    def check_accident_risk(self) -> Tuple[bool, float, str]:
        """
        Check if pet might have an accident.

        Returns:
            Tuple of (will_have_accident, probability, reason)
        """
        import random

        # Calculate accident probability
        urgency_factor = max(self.bladder, self.bowel) / 100.0
        control_factor = 1.0 - self.bladder_control
        training_factor = 1.0 - self.training_level

        # Base probability increases with urgency
        if urgency_factor < 0.7:
            base_prob = 0.0
        elif urgency_factor < 0.85:
            base_prob = 0.1
        else:
            base_prob = 0.5

        # Modify by control and training
        accident_prob = base_prob * (1.0 + control_factor) * (1.0 + training_factor * 0.5)

        # Determine reason
        reason = ""
        if self.bladder > 90:
            reason = "full_bladder"
        elif self.bowel > 90:
            reason = "full_bowel"
        elif urgency_factor > 0.8:
            reason = "urgent_need"

        # Check if accident occurs
        will_accident = random.random() < accident_prob and urgency_factor > 0.7

        return will_accident, accident_prob, reason

    def have_accident(self, accident_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Pet has a bathroom accident.

        Args:
            accident_type: 'urinate', 'defecate', or None (auto-determine)

        Returns:
            Dictionary with accident details
        """
        current_time = time.time()

        # Determine type if not specified
        if accident_type is None:
            if self.bladder > self.bowel:
                accident_type = 'urinate'
            else:
                accident_type = 'defecate'

        accident = {
            'timestamp': current_time,
            'datetime': datetime.now().isoformat(),
            'type': accident_type,
            'bladder_level': self.bladder,
            'bowel_level': self.bowel,
            'training_level': self.training_level,
            'was_preventable': True
        }

        # Empty appropriate need
        if accident_type == 'urinate':
            self.bladder = 0.0
            self.last_urination_time = current_time
        else:  # defecate
            self.bowel = 0.0
            self.last_defecation_time = current_time

        # Record accident
        self.total_accidents += 1
        self.recent_accidents += 1
        self.last_accident_time = current_time
        self.accident_history.append(accident)

        # Regression in training
        self.training_level = max(0.0, self.training_level - 0.05)
        if self.training_level < 0.8:
            self.house_trained = False

        return accident

    def get_urgency_level(self) -> Tuple[str, float]:
        """
        Get current urgency level.

        Returns:
            Tuple of (urgency_description, urgency_value)
        """
        max_need = max(self.bladder, self.bowel)

        if max_need < 30:
            return "comfortable", max_need
        elif max_need < 60:
            return "slight_urge", max_need
        elif max_need < 80:
            return "moderate_need", max_need
        elif max_need < 95:
            return "urgent", max_need
        else:
            return "desperate", max_need

    def get_status(self) -> Dict[str, Any]:
        """Get current bathroom status."""
        urgency, urgency_value = self.get_urgency_level()

        return {
            'bladder': self.bladder,
            'bowel': self.bowel,
            'urgency_level': urgency,
            'urgency_value': urgency_value,
            'house_trained': self.house_trained,
            'training_level': self.training_level,
            'bladder_control': self.bladder_control,
            'total_accidents': self.total_accidents,
            'recent_accidents': self.recent_accidents,
            'hours_since_urination': (time.time() - self.last_urination_time) / 3600.0,
            'hours_since_defecation': (time.time() - self.last_defecation_time) / 3600.0
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'bladder': self.bladder,
            'bowel': self.bowel,
            'bladder_fill_rate': self.bladder_fill_rate,
            'bowel_fill_rate': self.bowel_fill_rate,
            'last_urination_time': self.last_urination_time,
            'last_defecation_time': self.last_defecation_time,
            'total_accidents': self.total_accidents,
            'recent_accidents': self.recent_accidents,
            'last_accident_time': self.last_accident_time,
            'accident_history': self.accident_history.copy(),
            'house_trained': self.house_trained,
            'training_level': self.training_level,
            'age_days': self.age_days,
            'bladder_control': self.bladder_control
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BathroomNeedsSystem':
        """Deserialize from dictionary."""
        system = cls(age_days=data.get('age_days', 0))
        system.bladder = data.get('bladder', 0.0)
        system.bowel = data.get('bowel', 0.0)
        system.bladder_fill_rate = data.get('bladder_fill_rate', 8.0)
        system.bowel_fill_rate = data.get('bowel_fill_rate', 4.0)
        system.last_urination_time = data.get('last_urination_time', time.time())
        system.last_defecation_time = data.get('last_defecation_time', time.time())
        system.total_accidents = data.get('total_accidents', 0)
        system.recent_accidents = data.get('recent_accidents', 0)
        system.last_accident_time = data.get('last_accident_time', 0)
        system.accident_history = data.get('accident_history', [])
        system.house_trained = data.get('house_trained', False)
        system.training_level = data.get('training_level', 0.0)
        system.bladder_control = data.get('bladder_control', 1.0)
        return system


class GroomingSystem:
    """
    Manages cleanliness and grooming needs.

    Features:
    - Cleanliness decreases over time
    - Activities (playing, eating) make pet dirtier
    - Grooming restores cleanliness
    - Affects happiness and health
    """

    def __init__(self):
        """Initialize grooming system."""
        self.cleanliness = 100.0  # 0-100
        self.last_bath_time = time.time()
        self.last_brushing_time = time.time()
        self.total_baths = 0
        self.total_brushings = 0

        # Dirt accumulation rate
        self.dirt_rate = 1.0  # Points per hour

        # Grooming preferences
        self.likes_baths = True  # Can be overridden by personality
        self.likes_brushing = True

    def update(self, hours_elapsed: float, activity_level: float = 0.0):
        """
        Update cleanliness over time.

        Args:
            hours_elapsed: Hours since last update
            activity_level: 0-1, how active the pet has been
        """
        # Base dirt accumulation
        dirt_gain = self.dirt_rate * hours_elapsed

        # More active = gets dirtier faster
        dirt_gain *= (1.0 + activity_level * 0.5)

        self.cleanliness = max(0.0, self.cleanliness - dirt_gain)

    def get_cleanliness_level(self) -> CleanlinessLevel:
        """Get current cleanliness level."""
        if self.cleanliness >= 90:
            return CleanlinessLevel.PRISTINE
        elif self.cleanliness >= 70:
            return CleanlinessLevel.CLEAN
        elif self.cleanliness >= 50:
            return CleanlinessLevel.SLIGHTLY_DIRTY
        elif self.cleanliness >= 30:
            return CleanlinessLevel.DIRTY
        elif self.cleanliness >= 10:
            return CleanlinessLevel.VERY_DIRTY
        else:
            return CleanlinessLevel.FILTHY

    def give_bath(self) -> Dict[str, Any]:
        """
        Give pet a bath.

        Returns:
            Dictionary with bath results
        """
        previous_cleanliness = self.cleanliness

        # Bath fully cleans
        self.cleanliness = 100.0
        self.last_bath_time = time.time()
        self.total_baths += 1

        cleanliness_gain = 100.0 - previous_cleanliness

        # Happiness change depends on preference
        if self.likes_baths:
            happiness_change = 5.0
            reaction = "enjoyed_bath"
        else:
            happiness_change = -3.0
            reaction = "tolerated_bath"

        return {
            'success': True,
            'cleanliness_gain': cleanliness_gain,
            'final_cleanliness': self.cleanliness,
            'happiness_change': happiness_change,
            'reaction': reaction
        }

    def brush(self) -> Dict[str, Any]:
        """
        Brush pet's fur/scales/feathers.

        Returns:
            Dictionary with brushing results
        """
        previous_cleanliness = self.cleanliness

        # Brushing improves cleanliness moderately
        cleanliness_gain = min(30.0, 100.0 - self.cleanliness)
        self.cleanliness = min(100.0, self.cleanliness + cleanliness_gain)

        self.last_brushing_time = time.time()
        self.total_brushings += 1

        # Most pets enjoy brushing
        if self.likes_brushing:
            happiness_change = 8.0
            reaction = "loved_brushing"
        else:
            happiness_change = 2.0
            reaction = "tolerated_brushing"

        return {
            'success': True,
            'cleanliness_gain': cleanliness_gain,
            'final_cleanliness': self.cleanliness,
            'happiness_change': happiness_change,
            'reaction': reaction,
            'bonding_gain': 0.5  # Grooming builds bond
        }

    def get_dirty_from_activity(self, activity: str, intensity: float = 1.0):
        """
        Pet gets dirty from an activity.

        Args:
            activity: Type of activity ('playing_outside', 'rolling', 'eating', etc.)
            intensity: How intense the activity was (0-1)
        """
        dirt_amounts = {
            'playing_outside': 15.0,
            'rolling_in_dirt': 25.0,
            'eating_messy_food': 5.0,
            'swimming': 10.0,
            'exploring': 8.0,
            'digging': 20.0
        }

        dirt = dirt_amounts.get(activity, 5.0) * intensity
        self.cleanliness = max(0.0, self.cleanliness - dirt)

    def needs_grooming(self) -> Tuple[bool, str]:
        """
        Check if pet needs grooming.

        Returns:
            Tuple of (needs_grooming, urgency_level)
        """
        level = self.get_cleanliness_level()

        if level in [CleanlinessLevel.FILTHY, CleanlinessLevel.VERY_DIRTY]:
            return True, "urgent"
        elif level == CleanlinessLevel.DIRTY:
            return True, "moderate"
        elif level == CleanlinessLevel.SLIGHTLY_DIRTY:
            return True, "slight"
        else:
            return False, "clean"

    def get_status(self) -> Dict[str, Any]:
        """Get current grooming status."""
        needs_grooming, urgency = self.needs_grooming()

        return {
            'cleanliness': self.cleanliness,
            'cleanliness_level': self.get_cleanliness_level().value,
            'needs_grooming': needs_grooming,
            'grooming_urgency': urgency,
            'hours_since_bath': (time.time() - self.last_bath_time) / 3600.0,
            'hours_since_brushing': (time.time() - self.last_brushing_time) / 3600.0,
            'total_baths': self.total_baths,
            'total_brushings': self.total_brushings,
            'likes_baths': self.likes_baths,
            'likes_brushing': self.likes_brushing
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'cleanliness': self.cleanliness,
            'last_bath_time': self.last_bath_time,
            'last_brushing_time': self.last_brushing_time,
            'total_baths': self.total_baths,
            'total_brushings': self.total_brushings,
            'dirt_rate': self.dirt_rate,
            'likes_baths': self.likes_baths,
            'likes_brushing': self.likes_brushing
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroomingSystem':
        """Deserialize from dictionary."""
        system = cls()
        system.cleanliness = data.get('cleanliness', 100.0)
        system.last_bath_time = data.get('last_bath_time', time.time())
        system.last_brushing_time = data.get('last_brushing_time', time.time())
        system.total_baths = data.get('total_baths', 0)
        system.total_brushings = data.get('total_brushings', 0)
        system.dirt_rate = data.get('dirt_rate', 1.0)
        system.likes_baths = data.get('likes_baths', True)
        system.likes_brushing = data.get('likes_brushing', True)
        return system
