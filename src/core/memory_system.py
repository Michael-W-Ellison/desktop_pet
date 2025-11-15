"""
Enhanced Memory System for Desktop Pet

Provides three types of memory:
1. Episodic Memory - Specific memorable events (first feeding, special moments)
2. Semantic Memory - General knowledge and patterns (feeding schedule, preferences)
3. Working Memory - Enhanced LSTM with 100+ interaction capacity

This system mimics how real creatures remember:
- Vivid memories of important events
- General knowledge learned over time
- Recent interaction history
"""
import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
from datetime import datetime, timedelta
from enum import Enum


class MemoryImportance(Enum):
    """How important a memory is for retention."""
    TRIVIAL = 0.1      # Forgotten quickly
    NORMAL = 0.3       # Typical interaction
    INTERESTING = 0.6  # Notable event
    IMPORTANT = 0.8    # Significant moment
    CRUCIAL = 1.0      # Never forget (first feeding, naming, etc.)


class EpisodicMemory:
    """
    Episodic memory stores specific events and experiences.

    Like a human remembering "the first time I rode a bike" or "that time
    I went to the beach", episodic memory stores specific moments with
    context, emotions, and details.
    """

    def __init__(self, max_memories: int = 500):
        """
        Initialize episodic memory.

        Args:
            max_memories: Maximum number of memories to retain
        """
        self.max_memories = max_memories
        self.memories = []  # List of memory dictionaries
        self.memory_id_counter = 0

    def add_memory(self, event_type: str, details: Dict[str, Any],
                   importance: float = 0.3, emotional_valence: float = 0.5):
        """
        Add a new episodic memory.

        Args:
            event_type: Type of event (e.g., 'first_feeding', 'learned_trick', 'played_ball')
            details: Dictionary with event details
            importance: How important this memory is (0-1), affects retention
            emotional_valence: How positive/negative (0=very negative, 1=very positive)
        """
        memory = {
            'id': self.memory_id_counter,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details.copy(),
            'importance': importance,
            'emotional_valence': emotional_valence,
            'recall_count': 0,  # How many times this memory has been accessed
            'last_recalled': None,
            'memory_strength': importance  # Decays over time unless reinforced
        }

        self.memory_id_counter += 1
        self.memories.append(memory)

        # Sort by importance and trim if needed
        self._consolidate_memories()

    def recall_memory(self, event_type: Optional[str] = None,
                     min_importance: float = 0.0,
                     time_range: Optional[Tuple[float, float]] = None,
                     limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recall memories matching criteria.

        Args:
            event_type: Filter by event type (None = all types)
            min_importance: Minimum importance level
            time_range: Tuple of (start_timestamp, end_timestamp) or None
            limit: Maximum number of memories to return

        Returns:
            List of matching memories, sorted by relevance
        """
        matching_memories = []

        for memory in self.memories:
            # Filter by type
            if event_type and memory['event_type'] != event_type:
                continue

            # Filter by importance
            if memory['memory_strength'] < min_importance:
                continue

            # Filter by time range
            if time_range:
                if memory['timestamp'] < time_range[0] or memory['timestamp'] > time_range[1]:
                    continue

            matching_memories.append(memory)

        # Sort by memory strength (combination of importance and recency)
        now = time.time()
        for mem in matching_memories:
            # Recent memories are easier to recall
            days_ago = (now - mem['timestamp']) / (24 * 3600)
            recency_bonus = max(0, 1.0 - days_ago / 30)  # Decays over 30 days

            # Frequently recalled memories are stronger
            recall_bonus = min(0.3, mem['recall_count'] * 0.05)

            mem['_recall_score'] = mem['memory_strength'] + recency_bonus * 0.3 + recall_bonus

        matching_memories.sort(key=lambda x: x['_recall_score'], reverse=True)

        # Mark as recalled
        for memory in matching_memories[:limit]:
            memory['recall_count'] += 1
            memory['last_recalled'] = time.time()
            # Strengthen memory slightly when recalled
            memory['memory_strength'] = min(1.0, memory['memory_strength'] + 0.02)

        return matching_memories[:limit]

    def get_first_memory_of_type(self, event_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the first memory of a specific type.

        Useful for "firsts" - first feeding, first play, first trick learned, etc.

        Args:
            event_type: Type of event to find

        Returns:
            First memory of that type, or None
        """
        memories_of_type = [m for m in self.memories if m['event_type'] == event_type]
        if memories_of_type:
            # Sort by timestamp to get the earliest
            memories_of_type.sort(key=lambda x: x['timestamp'])
            return memories_of_type[0]
        return None

    def _consolidate_memories(self):
        """
        Consolidate memories - forget less important ones if at capacity.

        This simulates how real memories fade over time. Important memories
        are retained, trivial ones are forgotten.
        """
        if len(self.memories) <= self.max_memories:
            return

        # Decay memory strength over time for non-crucial memories
        now = time.time()
        for memory in self.memories:
            if memory['importance'] < MemoryImportance.CRUCIAL.value:
                days_ago = (now - memory['timestamp']) / (24 * 3600)
                decay_rate = 0.01 * (1.0 - memory['importance'])  # Important memories decay slower
                memory['memory_strength'] = max(0, memory['memory_strength'] - decay_rate * days_ago)

        # Sort by memory strength
        self.memories.sort(key=lambda x: x['memory_strength'], reverse=True)

        # Keep only the strongest memories
        self.memories = self.memories[:self.max_memories]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize episodic memory for saving."""
        return {
            'max_memories': self.max_memories,
            'memories': self.memories,
            'memory_id_counter': self.memory_id_counter
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EpisodicMemory':
        """Deserialize episodic memory from saved data."""
        memory = cls(max_memories=data['max_memories'])
        memory.memories = data['memories']
        memory.memory_id_counter = data['memory_id_counter']
        return memory


class SemanticMemory:
    """
    Semantic memory stores general knowledge and patterns.

    Unlike episodic memory (specific events), semantic memory stores facts:
    - "My owner usually feeds me at 7pm"
    - "When I do tricks, I get praise"
    - "The ball appears on weekends"
    - "Happiness increases when I play"
    """

    def __init__(self):
        """Initialize semantic memory."""
        # Pattern recognition: maps patterns to learned knowledge
        self.feeding_patterns = {
            'times': [],  # List of feeding times
            'typical_time': None,  # Most common feeding time
            'average_interval': None  # Average time between feedings
        }

        self.interaction_patterns = {
            'active_hours': [],  # Hours when owner is active
            'preferred_interactions': {},  # Which interactions are most common
            'response_patterns': {}  # How owner typically responds
        }

        self.learned_knowledge = {
            # General facts learned over time
            'owner_is_morning_person': None,  # True/False/None
            'weekend_patterns': {},
            'trick_success_rates': {},  # Which tricks work best
            'command_associations': {}  # Which commands mean what
        }

        # Statistical tracking
        self.stats = {
            'total_interactions': 0,
            'total_feedings': 0,
            'total_play_sessions': 0,
            'average_happiness_change': 0.0
        }

    def update_feeding_pattern(self, feeding_time: float):
        """
        Update knowledge about feeding patterns.

        Args:
            feeding_time: Timestamp of feeding
        """
        hour_of_day = datetime.fromtimestamp(feeding_time).hour
        self.feeding_patterns['times'].append((feeding_time, hour_of_day))

        # Keep only last 50 feedings for pattern detection
        if len(self.feeding_patterns['times']) > 50:
            self.feeding_patterns['times'] = self.feeding_patterns['times'][-50:]

        # Calculate typical feeding time
        if len(self.feeding_patterns['times']) >= 5:
            hours = [h for _, h in self.feeding_patterns['times']]
            self.feeding_patterns['typical_time'] = int(np.median(hours))

            # Calculate average interval
            timestamps = [t for t, _ in self.feeding_patterns['times']]
            if len(timestamps) >= 2:
                intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                self.feeding_patterns['average_interval'] = np.mean(intervals)

        self.stats['total_feedings'] += 1

    def update_interaction_pattern(self, interaction_type: str, hour: int, success: bool):
        """
        Update knowledge about interaction patterns.

        Args:
            interaction_type: Type of interaction
            hour: Hour of day (0-23)
            success: Whether interaction was successful/positive
        """
        # Track active hours
        if hour not in self.interaction_patterns['active_hours']:
            self.interaction_patterns['active_hours'].append(hour)

        # Track preferred interactions
        if interaction_type not in self.interaction_patterns['preferred_interactions']:
            self.interaction_patterns['preferred_interactions'][interaction_type] = 0
        self.interaction_patterns['preferred_interactions'][interaction_type] += 1

        # Track response patterns
        if interaction_type not in self.interaction_patterns['response_patterns']:
            self.interaction_patterns['response_patterns'][interaction_type] = {'success': 0, 'total': 0}

        self.interaction_patterns['response_patterns'][interaction_type]['total'] += 1
        if success:
            self.interaction_patterns['response_patterns'][interaction_type]['success'] += 1

        self.stats['total_interactions'] += 1

    def learn_fact(self, fact_name: str, value: Any):
        """
        Learn a general fact.

        Args:
            fact_name: Name of the fact
            value: Value of the fact
        """
        self.learned_knowledge[fact_name] = value

    def get_expected_feeding_time(self) -> Optional[int]:
        """Get the expected hour for next feeding based on patterns."""
        return self.feeding_patterns.get('typical_time')

    def get_interaction_preference(self, interaction_type: str) -> float:
        """
        Get how much this interaction type is preferred.

        Args:
            interaction_type: Type of interaction

        Returns:
            Preference score (0-1)
        """
        total = sum(self.interaction_patterns['preferred_interactions'].values())
        if total == 0:
            return 0.5

        count = self.interaction_patterns['preferred_interactions'].get(interaction_type, 0)
        return count / total

    def to_dict(self) -> Dict[str, Any]:
        """Serialize semantic memory."""
        return {
            'feeding_patterns': self.feeding_patterns,
            'interaction_patterns': self.interaction_patterns,
            'learned_knowledge': self.learned_knowledge,
            'stats': self.stats
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticMemory':
        """Deserialize semantic memory."""
        memory = cls()
        memory.feeding_patterns = data['feeding_patterns']
        memory.interaction_patterns = data['interaction_patterns']
        memory.learned_knowledge = data['learned_knowledge']
        memory.stats = data['stats']
        return memory


class EnhancedWorkingMemory:
    """
    Enhanced working memory with expanded LSTM capacity.

    Stores recent interactions (100+) for immediate recall and pattern recognition.
    This is the "short-term" memory that feeds into long-term memories.
    """

    def __init__(self, capacity: int = 150):
        """
        Initialize enhanced working memory.

        Args:
            capacity: Maximum number of recent interactions to remember
        """
        self.capacity = capacity
        self.interactions = deque(maxlen=capacity)

    def add_interaction(self, interaction: Dict[str, Any]):
        """
        Add an interaction to working memory.

        Args:
            interaction: Dictionary with interaction details
        """
        interaction['timestamp'] = time.time()
        self.interactions.append(interaction)

    def get_recent_interactions(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the N most recent interactions.

        Args:
            count: Number of interactions to retrieve

        Returns:
            List of recent interactions
        """
        return list(self.interactions)[-count:]

    def get_interactions_by_type(self, interaction_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent interactions of a specific type.

        Args:
            interaction_type: Type to filter by
            limit: Maximum number to return

        Returns:
            List of matching interactions
        """
        matching = [i for i in self.interactions if i.get('type') == interaction_type]
        return matching[-limit:]

    def get_interaction_sequence(self, length: int = 50) -> List[Dict[str, Any]]:
        """
        Get a sequence of recent interactions for LSTM processing.

        Args:
            length: Sequence length

        Returns:
            List of interactions
        """
        return list(self.interactions)[-length:]

    def clear(self):
        """Clear all working memory."""
        self.interactions.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize working memory."""
        return {
            'capacity': self.capacity,
            'interactions': list(self.interactions)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedWorkingMemory':
        """Deserialize working memory."""
        memory = cls(capacity=data['capacity'])
        for interaction in data['interactions']:
            memory.interactions.append(interaction)
        return memory


class MemoryConsolidation:
    """
    Manages consolidation of working memory into long-term storage.

    This process:
    1. Reviews recent interactions in working memory
    2. Identifies important patterns and events
    3. Promotes them to episodic or semantic memory
    4. Strengthens existing related memories
    """

    def __init__(self, episodic_memory: EpisodicMemory,
                 semantic_memory: SemanticMemory,
                 working_memory: EnhancedWorkingMemory):
        """
        Initialize consolidation system.

        Args:
            episodic_memory: Episodic memory system
            semantic_memory: Semantic memory system
            working_memory: Working memory system
        """
        self.episodic = episodic_memory
        self.semantic = semantic_memory
        self.working = working_memory

        self.last_consolidation = time.time()
        self.consolidation_interval = 300  # Consolidate every 5 minutes

    def should_consolidate(self) -> bool:
        """Check if it's time to consolidate memories."""
        return (time.time() - self.last_consolidation) >= self.consolidation_interval

    def consolidate(self):
        """
        Perform memory consolidation.

        Reviews recent interactions and:
        - Creates episodic memories for important events
        - Updates semantic knowledge with patterns
        - Clears processed working memory
        """
        recent = self.working.get_recent_interactions(50)

        if not recent:
            return

        # Look for important events to store as episodic memories
        for interaction in recent:
            importance = self._assess_importance(interaction)

            if importance >= MemoryImportance.INTERESTING.value:
                # Store as episodic memory
                event_type = interaction.get('type', 'interaction')
                details = {
                    'stats': interaction.get('stats', {}),
                    'context': interaction.get('context', {}),
                    'outcome': interaction.get('outcome', 'neutral')
                }

                emotional_valence = 0.7 if interaction.get('positive', True) else 0.3

                self.episodic.add_memory(
                    event_type=event_type,
                    details=details,
                    importance=importance,
                    emotional_valence=emotional_valence
                )

        # Update semantic patterns
        for interaction in recent:
            i_type = interaction.get('type', 'unknown')
            timestamp = interaction.get('timestamp', time.time())
            hour = datetime.fromtimestamp(timestamp).hour
            success = interaction.get('positive', True)

            if i_type == 'feed':
                self.semantic.update_feeding_pattern(timestamp)

            self.semantic.update_interaction_pattern(i_type, hour, success)

        self.last_consolidation = time.time()

    def _assess_importance(self, interaction: Dict[str, Any]) -> float:
        """
        Assess how important an interaction is.

        Args:
            interaction: Interaction dictionary

        Returns:
            Importance score (0-1)
        """
        i_type = interaction.get('type', '')

        # Check if this is a "first" event
        first_memory = self.episodic.get_first_memory_of_type(i_type)
        if first_memory is None:
            # This is the first time! Very important
            return MemoryImportance.CRUCIAL.value

        # Certain event types are inherently more important
        important_types = {
            'learned_trick': MemoryImportance.IMPORTANT.value,
            'name_recognition': MemoryImportance.IMPORTANT.value,
            'evolution': MemoryImportance.CRUCIAL.value,
            'achievement': MemoryImportance.IMPORTANT.value
        }

        if i_type in important_types:
            return important_types[i_type]

        # High emotional events are more memorable
        if interaction.get('emotional_intensity', 0) > 0.7:
            return MemoryImportance.INTERESTING.value

        # Default importance
        return MemoryImportance.NORMAL.value


class IntegratedMemorySystem:
    """
    Integrated memory system combining all memory types.

    Provides a unified interface for:
    - Episodic memory (specific events)
    - Semantic memory (general knowledge)
    - Working memory (recent interactions, 100+)
    - Memory consolidation
    """

    def __init__(self,
                 episodic_capacity: int = 500,
                 working_capacity: int = 150):
        """
        Initialize integrated memory system.

        Args:
            episodic_capacity: Max episodic memories
            working_capacity: Max working memory interactions (100+)
        """
        self.episodic = EpisodicMemory(max_memories=episodic_capacity)
        self.semantic = SemanticMemory()
        self.working = EnhancedWorkingMemory(capacity=working_capacity)
        self.consolidation = MemoryConsolidation(self.episodic, self.semantic, self.working)

    def record_interaction(self, interaction_type: str, details: Dict[str, Any],
                          important: bool = False, emotional_intensity: float = 0.5):
        """
        Record a new interaction.

        This is the main entry point for adding new experiences.

        Args:
            interaction_type: Type of interaction
            details: Interaction details
            important: Mark as immediately important (bypass normal assessment)
            emotional_intensity: How emotionally significant (0-1)
        """
        interaction = {
            'type': interaction_type,
            'details': details,
            'emotional_intensity': emotional_intensity,
            'positive': details.get('positive', True),
            'stats': details.get('stats', {}),
            'context': details.get('context', {}),
            'outcome': details.get('outcome', 'neutral')
        }

        # Add to working memory
        self.working.add_interaction(interaction)

        # If marked as important, immediately add to episodic memory
        if important or emotional_intensity > 0.8:
            importance = MemoryImportance.IMPORTANT.value if important else MemoryImportance.INTERESTING.value
            emotional_valence = 0.7 if details.get('positive', True) else 0.3

            self.episodic.add_memory(
                event_type=interaction_type,
                details=details,
                importance=importance,
                emotional_valence=emotional_valence
            )

        # Check if consolidation is needed
        if self.consolidation.should_consolidate():
            self.consolidation.consolidate()

    def recall_event(self, event_type: str, first_only: bool = False) -> Optional[Dict[str, Any]]:
        """
        Recall a specific type of event.

        Args:
            event_type: Type of event to recall
            first_only: If True, return only the first memory of this type

        Returns:
            Memory dictionary or None
        """
        if first_only:
            return self.episodic.get_first_memory_of_type(event_type)
        else:
            memories = self.episodic.recall_memory(event_type=event_type, limit=1)
            return memories[0] if memories else None

    def get_pattern_knowledge(self, pattern_type: str) -> Any:
        """
        Get learned pattern knowledge.

        Args:
            pattern_type: Type of pattern ('feeding_time', 'interaction_preference', etc.)

        Returns:
            Pattern knowledge or None
        """
        if pattern_type == 'feeding_time':
            return self.semantic.get_expected_feeding_time()
        elif pattern_type == 'feeding_interval':
            return self.semantic.feeding_patterns.get('average_interval')
        else:
            return self.semantic.learned_knowledge.get(pattern_type)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire memory system."""
        return {
            'episodic': self.episodic.to_dict(),
            'semantic': self.semantic.to_dict(),
            'working': self.working.to_dict(),
            'last_consolidation': self.consolidation.last_consolidation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegratedMemorySystem':
        """Deserialize memory system."""
        system = cls()
        system.episodic = EpisodicMemory.from_dict(data['episodic'])
        system.semantic = SemanticMemory.from_dict(data['semantic'])
        system.working = EnhancedWorkingMemory.from_dict(data['working'])
        system.consolidation = MemoryConsolidation(system.episodic, system.semantic, system.working)
        system.consolidation.last_consolidation = data.get('last_consolidation', time.time())
        return system
