"""
Phase 15: Interaction System

Manages pet interactions with furniture and objects.
"""
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum


class InteractionType(Enum):
    """Types of interactions."""
    SLEEP = "sleep"                # Sleep in bed
    EAT = "eat"                    # Eat from food bowl
    DRINK = "drink"                # Drink from water bowl
    PLAY = "play"                  # Play with toy
    SCRATCH = "scratch"            # Use scratching post
    CLIMB = "climb"                # Climb perch/tree
    SIT = "sit"                    # Sit on furniture
    EXPLORE = "explore"            # Explore/investigate
    GROOM = "groom"                # Use grooming items
    WATCH = "watch"                # Watch/observe


class InteractionState(Enum):
    """State of an interaction."""
    IDLE = "idle"                  # Not interacting
    APPROACHING = "approaching"    # Moving to furniture
    INTERACTING = "interacting"    # Currently interacting
    COMPLETING = "completing"      # Finishing interaction
    COOLDOWN = "cooldown"          # Cooldown period


class Interaction:
    """Represents a single interaction instance."""

    def __init__(self, interaction_id: str, interaction_type: InteractionType,
                 furniture_id: str, pet_id: str = "default"):
        """
        Initialize interaction.

        Args:
            interaction_id: Unique interaction ID
            interaction_type: Type of interaction
            furniture_id: Furniture being interacted with
            pet_id: Pet performing interaction
        """
        self.interaction_id = interaction_id
        self.interaction_type = interaction_type
        self.furniture_id = furniture_id
        self.pet_id = pet_id

        # State
        self.state = InteractionState.IDLE
        self.progress = 0.0            # 0-1
        self.duration = 5.0            # seconds
        self.elapsed_time = 0.0

        # Timing
        self.start_timestamp: Optional[float] = None
        self.end_timestamp: Optional[float] = None
        self.cooldown_duration = 10.0  # seconds
        self.cooldown_end: Optional[float] = None

        # Effects
        self.effects_applied: Dict[str, float] = {}
        self.satisfaction = 0.0        # 0-1

        # Success
        self.completed = False
        self.interrupted = False

    def start(self):
        """Start the interaction."""
        self.state = InteractionState.INTERACTING
        self.start_timestamp = time.time()
        self.progress = 0.0

    def update(self, delta_time: float):
        """
        Update interaction progress.

        Args:
            delta_time: Time since last update (seconds)
        """
        if self.state != InteractionState.INTERACTING:
            return

        self.elapsed_time += delta_time
        self.progress = min(1.0, self.elapsed_time / self.duration)

        # Check if completed
        if self.progress >= 1.0:
            self.complete()

    def complete(self):
        """Complete the interaction successfully."""
        self.state = InteractionState.COMPLETING
        self.completed = True
        self.end_timestamp = time.time()
        self.satisfaction = self.progress  # Higher progress = more satisfaction

        # Start cooldown
        self.cooldown_end = time.time() + self.cooldown_duration

    def interrupt(self):
        """Interrupt the interaction."""
        self.state = InteractionState.IDLE
        self.interrupted = True
        self.end_timestamp = time.time()
        self.satisfaction = self.progress * 0.5  # Partial satisfaction

    def is_on_cooldown(self) -> bool:
        """Check if interaction is on cooldown."""
        if not self.cooldown_end:
            return False
        return time.time() < self.cooldown_end

    def get_remaining_cooldown(self) -> float:
        """Get remaining cooldown time."""
        if not self.cooldown_end:
            return 0.0
        remaining = self.cooldown_end - time.time()
        return max(0.0, remaining)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'interaction_id': self.interaction_id,
            'interaction_type': self.interaction_type.value,
            'furniture_id': self.furniture_id,
            'pet_id': self.pet_id,
            'state': self.state.value,
            'progress': self.progress,
            'duration': self.duration,
            'elapsed_time': self.elapsed_time,
            'start_timestamp': self.start_timestamp,
            'end_timestamp': self.end_timestamp,
            'cooldown_duration': self.cooldown_duration,
            'cooldown_end': self.cooldown_end,
            'effects_applied': self.effects_applied,
            'satisfaction': self.satisfaction,
            'completed': self.completed,
            'interrupted': self.interrupted
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        """Deserialize from dictionary."""
        interaction = cls(
            interaction_id=data['interaction_id'],
            interaction_type=InteractionType(data['interaction_type']),
            furniture_id=data['furniture_id'],
            pet_id=data.get('pet_id', 'default')
        )
        interaction.state = InteractionState(data.get('state', 'idle'))
        interaction.progress = data.get('progress', 0.0)
        interaction.duration = data.get('duration', 5.0)
        interaction.elapsed_time = data.get('elapsed_time', 0.0)
        interaction.start_timestamp = data.get('start_timestamp')
        interaction.end_timestamp = data.get('end_timestamp')
        interaction.cooldown_duration = data.get('cooldown_duration', 10.0)
        interaction.cooldown_end = data.get('cooldown_end')
        interaction.effects_applied = data.get('effects_applied', {})
        interaction.satisfaction = data.get('satisfaction', 0.0)
        interaction.completed = data.get('completed', False)
        interaction.interrupted = data.get('interrupted', False)
        return interaction


class InteractionSystem:
    """
    Manages pet-furniture interactions.

    Features:
    - Detect available interactions
    - Start/stop interactions
    - Update interaction progress
    - Apply effects from interactions
    - Track interaction history
    - Cooldown management
    """

    def __init__(self):
        """Initialize interaction system."""
        # Active interactions
        self.active_interactions: Dict[str, Interaction] = {}
        self.interaction_history: List[Interaction] = []

        # Interaction definitions (furniture category -> interaction types)
        self.furniture_interactions: Dict[str, List[InteractionType]] = {
            'bed': [InteractionType.SLEEP, InteractionType.SIT],
            'food_bowl': [InteractionType.EAT],
            'water_bowl': [InteractionType.DRINK],
            'toy_box': [InteractionType.PLAY, InteractionType.EXPLORE],
            'scratching': [InteractionType.SCRATCH],
            'perch': [InteractionType.CLIMB, InteractionType.SIT, InteractionType.WATCH],
            'decoration': [InteractionType.EXPLORE, InteractionType.WATCH],
            'plant': [InteractionType.EXPLORE, InteractionType.SCRATCH],
            'seating': [InteractionType.SIT],
            'toy': [InteractionType.PLAY]
        }

        # Interaction durations (seconds)
        self.interaction_durations = {
            InteractionType.SLEEP: 30.0,
            InteractionType.EAT: 5.0,
            InteractionType.DRINK: 3.0,
            InteractionType.PLAY: 15.0,
            InteractionType.SCRATCH: 8.0,
            InteractionType.CLIMB: 6.0,
            InteractionType.SIT: 20.0,
            InteractionType.EXPLORE: 10.0,
            InteractionType.GROOM: 12.0,
            InteractionType.WATCH: 25.0
        }

        # Interaction effects (type -> stat changes)
        self.interaction_effects = {
            InteractionType.SLEEP: {'energy': 30, 'happiness': 5},
            InteractionType.EAT: {'hunger': -40, 'happiness': 10},
            InteractionType.DRINK: {'hunger': -10, 'happiness': 5},
            InteractionType.PLAY: {'energy': -10, 'happiness': 20, 'boredom': -30},
            InteractionType.SCRATCH: {'stress': -15, 'happiness': 10},
            InteractionType.CLIMB: {'energy': -5, 'happiness': 15, 'boredom': -10},
            InteractionType.SIT: {'energy': 10, 'stress': -10},
            InteractionType.EXPLORE: {'happiness': 10, 'boredom': -15, 'intelligence': 2},
            InteractionType.GROOM: {'cleanliness': 20, 'happiness': 10},
            InteractionType.WATCH: {'stress': -10, 'boredom': -10}
        }

        # Interaction range (grid units)
        self.interaction_range = 1.5

        # Statistics
        self.total_interactions = 0
        self.completed_interactions = 0
        self.interrupted_interactions = 0
        self.total_interaction_time = 0.0

        # Interaction counter for unique IDs
        self._interaction_counter = 0

    def get_available_interactions(self, furniture_category: str) -> List[InteractionType]:
        """
        Get available interaction types for furniture category.

        Args:
            furniture_category: Furniture category

        Returns:
            List of available interaction types
        """
        return self.furniture_interactions.get(furniture_category, [])

    def can_interact(self, furniture_id: str, interaction_type: InteractionType,
                    pet_position: Tuple[float, float],
                    furniture_position: Tuple[float, float]) -> bool:
        """
        Check if pet can interact with furniture.

        Args:
            furniture_id: Furniture to interact with
            interaction_type: Type of interaction
            pet_position: Pet's current position
            furniture_position: Furniture position

        Returns:
            True if interaction is possible
        """
        # Check if already interacting with this furniture
        for interaction in self.active_interactions.values():
            if interaction.furniture_id == furniture_id:
                return False

        # Check if interaction type is on cooldown
        for interaction in self.interaction_history[-10:]:  # Check recent history
            if (interaction.furniture_id == furniture_id and
                interaction.interaction_type == interaction_type and
                interaction.is_on_cooldown()):
                return False

        # Check distance
        distance = ((pet_position[0] - furniture_position[0]) ** 2 +
                   (pet_position[1] - furniture_position[1]) ** 2) ** 0.5

        return distance <= self.interaction_range

    def start_interaction(self, furniture_id: str, furniture_category: str,
                         interaction_type: InteractionType,
                         pet_id: str = "default") -> Optional[Interaction]:
        """
        Start a new interaction.

        Args:
            furniture_id: Furniture to interact with
            furniture_category: Furniture category
            interaction_type: Type of interaction
            pet_id: Pet performing interaction

        Returns:
            Interaction if started successfully
        """
        # Check if interaction type is valid for furniture
        available = self.get_available_interactions(furniture_category)
        if interaction_type not in available:
            return None

        # Generate unique ID
        self._interaction_counter += 1
        interaction_id = f"interact_{self._interaction_counter}_{int(time.time())}"

        # Create interaction
        interaction = Interaction(interaction_id, interaction_type, furniture_id, pet_id)
        interaction.duration = self.interaction_durations.get(interaction_type, 5.0)

        # Start interaction
        interaction.start()

        # Store
        self.active_interactions[interaction_id] = interaction
        self.total_interactions += 1

        return interaction

    def update_interactions(self, delta_time: float):
        """
        Update all active interactions.

        Args:
            delta_time: Time since last update (seconds)
        """
        completed_ids = []

        for interaction_id, interaction in self.active_interactions.items():
            interaction.update(delta_time)

            # Check if completed
            if interaction.state == InteractionState.COMPLETING:
                # Apply effects
                effects = self.interaction_effects.get(interaction.interaction_type, {})
                interaction.effects_applied = effects.copy()

                # Move to history
                self.interaction_history.append(interaction)
                self.completed_interactions += 1
                self.total_interaction_time += interaction.elapsed_time
                completed_ids.append(interaction_id)

        # Remove completed interactions
        for interaction_id in completed_ids:
            del self.active_interactions[interaction_id]

    def stop_interaction(self, interaction_id: str, interrupt: bool = True) -> bool:
        """
        Stop an active interaction.

        Args:
            interaction_id: Interaction to stop
            interrupt: Whether to interrupt (True) or complete normally (False)

        Returns:
            True if stopped successfully
        """
        interaction = self.active_interactions.get(interaction_id)
        if not interaction:
            return False

        if interrupt:
            interaction.interrupt()
            self.interrupted_interactions += 1
        else:
            interaction.complete()
            self.completed_interactions += 1

        # Move to history
        self.interaction_history.append(interaction)
        self.total_interaction_time += interaction.elapsed_time

        # Remove from active
        del self.active_interactions[interaction_id]

        return True

    def get_active_interaction(self, pet_id: str = "default") -> Optional[Interaction]:
        """Get active interaction for pet."""
        for interaction in self.active_interactions.values():
            if interaction.pet_id == pet_id:
                return interaction
        return None

    def get_interaction_effects(self, interaction_type: InteractionType) -> Dict[str, float]:
        """Get effects for an interaction type."""
        return self.interaction_effects.get(interaction_type, {}).copy()

    def get_interaction_history(self, limit: int = 20) -> List[Interaction]:
        """Get recent interaction history."""
        return self.interaction_history[-limit:]

    def get_interactions_by_type(self, interaction_type: InteractionType) -> List[Interaction]:
        """Get all interactions of a type from history."""
        return [
            i for i in self.interaction_history
            if i.interaction_type == interaction_type
        ]

    def get_furniture_usage(self, furniture_id: str) -> int:
        """Get number of times furniture was used."""
        return sum(
            1 for i in self.interaction_history
            if i.furniture_id == furniture_id
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get interaction statistics."""
        interaction_counts = {}
        for interaction in self.interaction_history:
            itype = interaction.interaction_type.value
            interaction_counts[itype] = interaction_counts.get(itype, 0) + 1

        avg_duration = (
            self.total_interaction_time / self.completed_interactions
            if self.completed_interactions > 0 else 0.0
        )

        return {
            'total_interactions': self.total_interactions,
            'completed_interactions': self.completed_interactions,
            'interrupted_interactions': self.interrupted_interactions,
            'active_interactions': len(self.active_interactions),
            'total_interaction_time': self.total_interaction_time,
            'average_duration': avg_duration,
            'completion_rate': (
                (self.completed_interactions / self.total_interactions * 100)
                if self.total_interactions > 0 else 0.0
            ),
            'interactions_by_type': interaction_counts
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'active_interactions': {
                int_id: interaction.to_dict()
                for int_id, interaction in self.active_interactions.items()
            },
            'interaction_history': [
                i.to_dict() for i in self.interaction_history
            ],
            'interaction_range': self.interaction_range,
            'total_interactions': self.total_interactions,
            'completed_interactions': self.completed_interactions,
            'interrupted_interactions': self.interrupted_interactions,
            'total_interaction_time': self.total_interaction_time,
            'interaction_counter': self._interaction_counter
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionSystem':
        """Deserialize from dictionary."""
        system = cls()

        # Restore active interactions
        active_data = data.get('active_interactions', {})
        for int_id, int_data in active_data.items():
            system.active_interactions[int_id] = Interaction.from_dict(int_data)

        # Restore history
        history_data = data.get('interaction_history', [])
        for int_data in history_data:
            system.interaction_history.append(Interaction.from_dict(int_data))

        system.interaction_range = data.get('interaction_range', 1.5)
        system.total_interactions = data.get('total_interactions', 0)
        system.completed_interactions = data.get('completed_interactions', 0)
        system.interrupted_interactions = data.get('interrupted_interactions', 0)
        system.total_interaction_time = data.get('total_interaction_time', 0.0)
        system._interaction_counter = data.get('interaction_counter', 0)

        return system
