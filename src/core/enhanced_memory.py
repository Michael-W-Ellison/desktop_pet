"""
Phase 7: Expanded Memory Systems

Enhanced memory features:
- Autobiographical memory ("I remember the first time...")
- Favorite memories (stores best moments)
- Trauma/fear memory (bad experiences with lasting effects)
- Associative memory (location/time patterns)
- Dream system (processes memories during sleep)
- Memory importance weighting (fade vs persist)
"""
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum


class MemoryCategory(Enum):
    """Categories of special memories."""
    FIRST_TIME = "first_time"          # Autobiographical firsts
    FAVORITE = "favorite"              # Best moments
    TRAUMA = "trauma"                  # Fearful/bad experiences
    MILESTONE = "milestone"            # Important achievements
    ASSOCIATION = "association"        # Learned patterns


class AutobiographicalMemory:
    """
    Stores "first time" memories and personal history.

    Examples:
    - "I remember the first time we played ball"
    - "The first time I was fed"
    - "When I learned my name"
    """

    def __init__(self):
        """Initialize autobiographical memory."""
        self.first_time_events = {}  # event_type: memory_dict
        self.milestones = []         # List of milestone memories
        self.life_story = []         # Chronological life events

    def record_first_time(self, event_type: str, details: Dict[str, Any],
                         emotional_intensity: float = 0.7) -> bool:
        """
        Record a first-time experience.

        Args:
            event_type: Type of first time event
            details: Event details
            emotional_intensity: How emotionally significant (0-1)

        Returns:
            True if this was actually a first time, False if already recorded
        """
        if event_type in self.first_time_events:
            return False  # Not a first time

        memory = {
            'event_type': event_type,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'details': details.copy(),
            'emotional_intensity': emotional_intensity,
            'times_recalled': 0,
            'last_recalled': None,
            'memory_strength': 1.0  # First times never fade
        }

        self.first_time_events[event_type] = memory
        self.life_story.append(memory)

        return True

    def recall_first_time(self, event_type: str) -> Optional[Dict[str, Any]]:
        """
        Recall a first time experience.

        Args:
            event_type: Type of event to recall

        Returns:
            Memory dictionary or None
        """
        if event_type not in self.first_time_events:
            return None

        memory = self.first_time_events[event_type]
        memory['times_recalled'] += 1
        memory['last_recalled'] = time.time()

        return memory

    def get_earliest_memory(self) -> Optional[Dict[str, Any]]:
        """Get the earliest memory (first thing that happened)."""
        if not self.life_story:
            return None
        return self.life_story[0]

    def get_life_summary(self, max_events: int = 10) -> List[Dict[str, Any]]:
        """
        Get summary of life story.

        Args:
            max_events: Maximum events to return

        Returns:
            List of most significant life events
        """
        # Sort by emotional intensity and return top N
        sorted_events = sorted(
            self.life_story,
            key=lambda m: m['emotional_intensity'],
            reverse=True
        )
        return sorted_events[:max_events]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize autobiographical memory."""
        return {
            'first_time_events': self.first_time_events.copy(),
            'milestones': self.milestones.copy(),
            'life_story': self.life_story.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutobiographicalMemory':
        """Deserialize autobiographical memory."""
        memory = cls()
        memory.first_time_events = data.get('first_time_events', {})
        memory.milestones = data.get('milestones', [])
        memory.life_story = data.get('life_story', [])
        return memory


class FavoriteMemories:
    """
    Stores the pet's favorite/best memories.

    Automatically keeps track of the happiest moments.
    """

    def __init__(self, max_favorites: int = 20):
        """
        Initialize favorite memories.

        Args:
            max_favorites: Maximum favorite memories to keep
        """
        self.max_favorites = max_favorites
        self.favorites = []  # List of favorite memory dicts
        self.happiness_threshold = 0.7  # Minimum happiness to be a favorite

    def consider_as_favorite(self, event_type: str, details: Dict[str, Any],
                            happiness_level: float, emotional_intensity: float):
        """
        Consider adding an event as a favorite memory.

        Args:
            event_type: Type of event
            details: Event details
            happiness_level: Happiness at time of event (0-1)
            emotional_intensity: Emotional significance (0-1)
        """
        # Calculate memory score
        score = (happiness_level * 0.6 + emotional_intensity * 0.4)

        if score < self.happiness_threshold:
            return  # Not happy enough

        memory = {
            'event_type': event_type,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'details': details.copy(),
            'happiness_level': happiness_level,
            'emotional_intensity': emotional_intensity,
            'score': score,
            'times_recalled': 0,
            'favorite_rank': 0
        }

        self.favorites.append(memory)

        # Sort by score and keep only top N
        self.favorites.sort(key=lambda m: m['score'], reverse=True)
        self.favorites = self.favorites[:self.max_favorites]

        # Update ranks
        for i, fav in enumerate(self.favorites):
            fav['favorite_rank'] = i + 1

    def get_favorites(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top favorite memories.

        Args:
            limit: Number of favorites to return

        Returns:
            List of favorite memories
        """
        return self.favorites[:limit]

    def get_favorite_activities(self) -> List[str]:
        """Get list of favorite activity types."""
        activity_counts = defaultdict(int)
        for fav in self.favorites:
            activity_counts[fav['event_type']] += 1

        # Sort by frequency
        sorted_activities = sorted(
            activity_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [activity for activity, count in sorted_activities[:5]]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize favorite memories."""
        return {
            'favorites': self.favorites.copy(),
            'happiness_threshold': self.happiness_threshold
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FavoriteMemories':
        """Deserialize favorite memories."""
        memory = cls()
        memory.favorites = data.get('favorites', [])
        memory.happiness_threshold = data.get('happiness_threshold', 0.7)
        return memory


class TraumaMemory:
    """
    Stores traumatic/fearful memories that create lasting effects.

    Bad experiences have stronger and longer-lasting impact than good ones.
    """

    def __init__(self):
        """Initialize trauma memory."""
        self.traumas = []  # List of trauma memories
        self.fear_triggers = {}  # trigger: fear_level
        self.avoidance_patterns = {}  # thing_to_avoid: reason

    def record_trauma(self, event_type: str, details: Dict[str, Any],
                     severity: float, trigger: Optional[str] = None):
        """
        Record a traumatic experience.

        Args:
            event_type: Type of traumatic event
            details: Event details
            severity: How traumatic (0-1, higher = worse)
            trigger: Optional trigger that causes fear response
        """
        trauma = {
            'event_type': event_type,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'details': details.copy(),
            'severity': severity,
            'trigger': trigger,
            'times_triggered': 0,
            'trauma_strength': severity,  # Decays slowly over time
            'healing_progress': 0.0  # 0-1, increases with positive experiences
        }

        self.traumas.append(trauma)

        # Add fear trigger
        if trigger:
            current_fear = self.fear_triggers.get(trigger, 0.0)
            self.fear_triggers[trigger] = min(1.0, current_fear + severity * 0.5)

    def check_trigger(self, trigger: str) -> Tuple[bool, float]:
        """
        Check if something triggers fear response.

        Args:
            trigger: Potential fear trigger

        Returns:
            Tuple of (is_triggered, fear_intensity)
        """
        if trigger not in self.fear_triggers:
            return False, 0.0

        fear = self.fear_triggers[trigger]

        # Mark as triggered
        for trauma in self.traumas:
            if trauma.get('trigger') == trigger:
                trauma['times_triggered'] += 1

        return fear > 0.2, fear

    def process_healing(self, positive_experience_type: str, healing_amount: float = 0.05):
        """
        Process healing from positive experiences.

        Args:
            positive_experience_type: Type of positive experience
            healing_amount: Amount of healing (0-1)
        """
        for trauma in self.traumas:
            # Relevant positive experiences help heal related traumas
            if trauma['event_type'] in positive_experience_type or positive_experience_type in trauma['event_type']:
                trauma['healing_progress'] = min(1.0, trauma['healing_progress'] + healing_amount)
                trauma['trauma_strength'] = max(0.0, trauma['trauma_strength'] - healing_amount * 0.5)

                # Reduce fear trigger
                if trauma.get('trigger'):
                    trigger = trauma['trigger']
                    if trigger in self.fear_triggers:
                        self.fear_triggers[trigger] = max(0.0, self.fear_triggers[trigger] - healing_amount * 0.3)

    def get_active_traumas(self) -> List[Dict[str, Any]]:
        """Get traumas that still have significant impact."""
        return [t for t in self.traumas if t['trauma_strength'] > 0.2]

    def get_fear_level(self, trigger: str) -> float:
        """Get fear level for a specific trigger."""
        return self.fear_triggers.get(trigger, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize trauma memory."""
        return {
            'traumas': self.traumas.copy(),
            'fear_triggers': self.fear_triggers.copy(),
            'avoidance_patterns': self.avoidance_patterns.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraumaMemory':
        """Deserialize trauma memory."""
        memory = cls()
        memory.traumas = data.get('traumas', [])
        memory.fear_triggers = data.get('fear_triggers', {})
        memory.avoidance_patterns = data.get('avoidance_patterns', {})
        return memory


class AssociativeMemory:
    """
    Learns associations between contexts and events.

    Examples:
    - "desk corner = good hiding spot"
    - "evening = playtime"
    - "that toy = fun times"
    - "owner's desk = they're working, leave alone"
    """

    def __init__(self):
        """Initialize associative memory."""
        self.location_associations = defaultdict(list)  # location: [events]
        self.time_associations = defaultdict(list)      # time_of_day: [events]
        self.object_associations = defaultdict(list)    # object: [events]
        self.pattern_strengths = {}  # pattern_key: strength (0-1)

    def record_association(self, context_type: str, context_value: str,
                          event_type: str, outcome_valence: float):
        """
        Record an association between context and event.

        Args:
            context_type: Type of context ('location', 'time', 'object')
            context_value: Specific context (e.g., 'desk_corner', '18:00', 'red_ball')
            event_type: What happened
            outcome_valence: How good/bad it was (-1 to 1)
        """
        association = {
            'timestamp': time.time(),
            'event_type': event_type,
            'outcome_valence': outcome_valence,
            'count': 1
        }

        # Store in appropriate category
        if context_type == 'location':
            self.location_associations[context_value].append(association)
        elif context_type == 'time':
            self.time_associations[context_value].append(association)
        elif context_type == 'object':
            self.object_associations[context_value].append(association)

        # Update pattern strength
        pattern_key = f"{context_type}:{context_value}:{event_type}"
        current_strength = self.pattern_strengths.get(pattern_key, 0.0)

        # Strengthen if positive, weaken if negative
        change = outcome_valence * 0.1
        self.pattern_strengths[pattern_key] = max(0.0, min(1.0, current_strength + change))

    def get_association(self, context_type: str, context_value: str) -> Optional[Dict[str, Any]]:
        """
        Get learned association for a context.

        Args:
            context_type: Type of context
            context_value: Specific context

        Returns:
            Dictionary with association info or None
        """
        if context_type == 'location':
            events = self.location_associations.get(context_value, [])
        elif context_type == 'time':
            events = self.time_associations.get(context_value, [])
        elif context_type == 'object':
            events = self.object_associations.get(context_value, [])
        else:
            return None

        if not events:
            return None

        # Calculate average valence and most common event
        total_valence = sum(e['outcome_valence'] for e in events)
        avg_valence = total_valence / len(events)

        event_counts = defaultdict(int)
        for e in events:
            event_counts[e['event_type']] += 1

        most_common = max(event_counts.items(), key=lambda x: x[1])[0]

        return {
            'context': context_value,
            'most_common_event': most_common,
            'average_valence': avg_valence,
            'total_occurrences': len(events),
            'is_positive': avg_valence > 0.3,
            'is_negative': avg_valence < -0.3
        }

    def get_pattern_prediction(self, context_type: str, context_value: str) -> Optional[str]:
        """
        Predict what might happen in a given context.

        Args:
            context_type: Type of context
            context_value: Specific context

        Returns:
            Predicted event type or None
        """
        association = self.get_association(context_type, context_value)
        if association and association['total_occurrences'] >= 3:
            return association['most_common_event']
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize associative memory."""
        return {
            'location_associations': dict(self.location_associations),
            'time_associations': dict(self.time_associations),
            'object_associations': dict(self.object_associations),
            'pattern_strengths': self.pattern_strengths.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssociativeMemory':
        """Deserialize associative memory."""
        memory = cls()

        # Convert back to defaultdict
        loc_data = data.get('location_associations', {})
        memory.location_associations = defaultdict(list, loc_data)

        time_data = data.get('time_associations', {})
        memory.time_associations = defaultdict(list, time_data)

        obj_data = data.get('object_associations', {})
        memory.object_associations = defaultdict(list, obj_data)

        memory.pattern_strengths = data.get('pattern_strengths', {})

        return memory


class DreamSystem:
    """
    Processes memories during sleep, consolidating and organizing them.

    Dreams help:
    - Consolidate important memories
    - Process emotional experiences
    - Strengthen patterns
    - Fade unimportant memories
    """

    def __init__(self):
        """Initialize dream system."""
        self.last_dream_time = None
        self.total_dreams = 0
        self.dream_log = []  # Recent dreams
        self.memory_consolidation_queue = []

    def should_dream(self, is_sleeping: bool, hours_since_last_dream: float) -> bool:
        """
        Determine if pet should dream.

        Args:
            is_sleeping: Whether pet is currently sleeping
            hours_since_last_dream: Hours since last dream

        Returns:
            True if should dream now
        """
        if not is_sleeping:
            return False

        # Dream roughly every 2-4 hours of sleep
        dream_chance = min(0.9, hours_since_last_dream / 3.0)
        return random.random() < dream_chance

    def process_dream(self, recent_memories: List[Dict[str, Any]],
                     emotional_state: float) -> Dict[str, Any]:
        """
        Process a dream cycle.

        Args:
            recent_memories: List of recent memory dictionaries
            emotional_state: Current emotional state (0-1)

        Returns:
            Dream summary dictionary
        """
        self.last_dream_time = time.time()
        self.total_dreams += 1

        # Select memories to dream about (prefer emotional ones)
        dream_memories = []
        for memory in recent_memories[:20]:  # Consider last 20 memories
            emotional_intensity = memory.get('emotional_intensity', 0.5)
            importance = memory.get('importance', 0.5)

            dream_score = (emotional_intensity * 0.6 + importance * 0.4)
            if random.random() < dream_score:
                dream_memories.append(memory)

        # Create dream
        dream = {
            'timestamp': time.time(),
            'dream_number': self.total_dreams,
            'memories_processed': len(dream_memories),
            'emotional_tone': emotional_state,
            'dream_type': self._classify_dream(emotional_state, dream_memories),
            'memory_themes': self._extract_themes(dream_memories),
            'consolidation_effect': len(dream_memories) * 0.1  # Strengthens memories
        }

        self.dream_log.append(dream)

        # Keep only recent dreams
        if len(self.dream_log) > 50:
            self.dream_log = self.dream_log[-50:]

        return dream

    def _classify_dream(self, emotional_state: float, memories: List[Dict]) -> str:
        """Classify dream type based on emotions."""
        if emotional_state > 0.7:
            return "happy_dream"
        elif emotional_state < 0.3:
            return "nightmare"
        elif len(memories) > 5:
            return "vivid_dream"
        else:
            return "peaceful_dream"

    def _extract_themes(self, memories: List[Dict]) -> List[str]:
        """Extract common themes from dream memories."""
        event_types = [m.get('event_type', 'unknown') for m in memories]

        # Count occurrences
        theme_counts = defaultdict(int)
        for event in event_types:
            theme_counts[event] += 1

        # Return top themes
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, count in sorted_themes[:3]]

    def get_dream_statistics(self) -> Dict[str, Any]:
        """Get statistics about dreams."""
        if not self.dream_log:
            return {'total_dreams': 0}

        dream_types = [d['dream_type'] for d in self.dream_log]
        type_counts = defaultdict(int)
        for dtype in dream_types:
            type_counts[dtype] += 1

        return {
            'total_dreams': self.total_dreams,
            'recent_dreams': len(self.dream_log),
            'dream_type_distribution': dict(type_counts),
            'last_dream_time': self.last_dream_time
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dream system."""
        return {
            'last_dream_time': self.last_dream_time,
            'total_dreams': self.total_dreams,
            'dream_log': self.dream_log.copy()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DreamSystem':
        """Deserialize dream system."""
        system = cls()
        system.last_dream_time = data.get('last_dream_time')
        system.total_dreams = data.get('total_dreams', 0)
        system.dream_log = data.get('dream_log', [])
        return system


class MemoryImportanceManager:
    """
    Manages memory importance weighting and fading.

    Determines which memories fade and which persist forever.
    """

    @staticmethod
    def calculate_retention_probability(importance: float, age_days: float,
                                       recall_count: int) -> float:
        """
        Calculate probability that a memory is retained.

        Args:
            importance: Base importance (0-1)
            age_days: Age of memory in days
            recall_count: How many times memory has been recalled

        Returns:
            Retention probability (0-1)
        """
        # Crucial memories never fade
        if importance >= 0.95:
            return 1.0

        # Base retention decreases with age
        age_decay = max(0.1, 1.0 - (age_days * 0.05))

        # Recall strengthens memory
        recall_boost = min(0.3, recall_count * 0.05)

        # Calculate final probability
        retention = (importance * 0.6 + age_decay * 0.3 + recall_boost * 0.1)

        return max(0.0, min(1.0, retention))

    @staticmethod
    def should_fade_memory(memory: Dict[str, Any]) -> bool:
        """
        Determine if a memory should fade.

        Args:
            memory: Memory dictionary

        Returns:
            True if memory should be forgotten
        """
        importance = memory.get('importance', 0.3)
        timestamp = memory.get('timestamp', time.time())
        recall_count = memory.get('recall_count', 0)

        age_days = (time.time() - timestamp) / (24 * 3600)

        retention_prob = MemoryImportanceManager.calculate_retention_probability(
            importance, age_days, recall_count
        )

        # Random chance to fade based on retention probability
        return random.random() > retention_prob

    @staticmethod
    def calculate_memory_strength(memory: Dict[str, Any]) -> float:
        """
        Calculate current strength of a memory.

        Args:
            memory: Memory dictionary

        Returns:
            Memory strength (0-1)
        """
        base_strength = memory.get('memory_strength', 0.5)
        importance = memory.get('importance', 0.3)
        timestamp = memory.get('timestamp', time.time())
        recall_count = memory.get('recall_count', 0)

        age_days = (time.time() - timestamp) / (24 * 3600)

        # Decay over time
        decay_factor = max(0.3, 1.0 - (age_days * 0.02))

        # Boost from recalls
        recall_boost = min(0.4, recall_count * 0.08)

        # Importance prevents decay
        importance_protection = importance * 0.5

        strength = base_strength * decay_factor + recall_boost + importance_protection

        return max(0.0, min(1.0, strength))
