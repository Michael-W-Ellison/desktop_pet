"""
Creature class representing the desktop pal with its attributes, personality, and state.

Enhanced with:
- Integrated Memory System (episodic, semantic, working memory)
- Training System (trick learning, commands, name recognition)
- Evolution System (baby -> juvenile -> adult -> elder stages)
- Element System (11 element types with interactions)
- Variant System (shiny, mystic, shadow, crystal forms)
- Bonding System (progressive relationship levels: stranger -> best friend)
- Trust System (builds through consistent care and interactions)
- Emotional States (jealousy, separation anxiety, excitement on return)
- Preference System (individual likes/dislikes for toys, foods, activities)
- Name Calling System (responds to being called by name)
"""
import random
import time
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from .config import (
    PersonalityType, BehaviorState, CREATURE_TYPES, COLOR_PALETTES,
    PERSONALITY_TRAITS, MAX_HUNGER, HUNGER_DECAY_RATE, STARVATION_THRESHOLD,
    EvolutionStage, ElementType, VariantType
)
from .memory_system import IntegratedMemorySystem, MemoryImportance
from .training_system import TrainingSystem
from .evolution_system import EvolutionSystem, EvolutionTrigger
from .element_system import ElementSystem, create_element_system_for_species
from .variant_system import VariantSystem, generate_random_variant
from .bonding_system import BondingSystem, BondLevel
from .trust_system import TrustSystem
from .emotional_states import EmotionalStateManager, EmotionalState
from .preference_system import PreferenceSystem
from .name_calling import NameCallingSystem


class Creature:
    """Represents a desktop pal creature with personality, stats, and learning capabilities."""

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
        self.total_interactions = 0  # Track total interactions for evolution (Phase 4)

        # State
        self.current_state = BehaviorState.IDLE
        self.position = [100, 100]  # x, y position on screen
        self.velocity = [0, 0]  # x, y velocity
        self.facing_right = True

        # Learning and behavior
        self.learned_behaviors = {}
        self.interaction_history = []

        # Personality trait modifiers
        self.trait_modifiers = PERSONALITY_TRAITS[self.personality]

        # Phase 2: Enhanced Memory System
        self.memory = IntegratedMemorySystem(
            episodic_capacity=500,  # 500 memorable events
            working_capacity=150    # 150 recent interactions (100+)
        )

        # Phase 2: Training System
        self.training = TrainingSystem(
            creature_name=self.name,
            personality=self.personality
        )

        # Phase 4: Evolution System
        self.evolution = EvolutionSystem(current_stage=EvolutionStage.BABY)

        # Phase 4: Element System
        self.element = create_element_system_for_species(self.creature_type)

        # Phase 4: Variant System
        self.variant = generate_random_variant()

        # Apply variant modifiers to initial stats
        variant_mods = self.variant.get_variant_modifiers()
        self.happiness *= variant_mods.get('happiness_gain', 1.0)

        # Phase 5: Advanced Bonding Systems
        self.bonding = BondingSystem(initial_bond=0.0)
        self.trust = TrustSystem(initial_trust=0.0)
        self.emotional_states = EmotionalStateManager()
        self.preferences = PreferenceSystem(personality_type=self.personality.value)
        self.name_calling = NameCallingSystem()

        # Phase 7: Enhanced Memory Systems
        try:
            from .enhanced_memory import (
                AutobiographicalMemory, FavoriteMemories, TraumaMemory,
                AssociativeMemory, DreamSystem, MemoryImportanceManager
            )
            self.autobiographical = AutobiographicalMemory()
            self.favorite_memories = FavoriteMemories(max_favorites=20)
            self.trauma_memory = TraumaMemory()
            self.associative_memory = AssociativeMemory()
            self.dream_system = DreamSystem()
            self.memory_manager = MemoryImportanceManager()
            self.phase7_enabled = True
        except ImportError:
            # Phase 7 not available
            self.autobiographical = None
            self.favorite_memories = None
            self.trauma_memory = None
            self.associative_memory = None
            self.dream_system = None
            self.memory_manager = None
            self.phase7_enabled = False

        # Record birth as first episodic memory
        birth_details = {
            'creature_type': self.creature_type,
            'personality': self.personality.value,
            'evolution_stage': self.evolution.current_stage.value,
            'element': self.element.primary_element.value,
            'variant': self.variant.variant.value
        }
        self.memory.record_interaction(
            'birth',
            birth_details,
            important=True,
            emotional_intensity=1.0
        )

        # Phase 7: Record birth as first time (autobiographical memory)
        if self.phase7_enabled and self.autobiographical:
            self.autobiographical.record_first_time('birth', birth_details, emotional_intensity=1.0)

        # Show special message for rare variants
        if self.variant.is_rare():
            rare_message = self.variant.get_encounter_message()
            # This message will be shown by pet_manager when creature hatches

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

        # Phase 5: Update emotional states
        self.emotional_states.update(delta_time)

        # Phase 5: Process bonding decay from neglect
        hours_since_interaction = time_since_interaction / 3600.0
        if hours_since_interaction > 1:
            self.bonding.process_neglect(hours_since_interaction)

        # Phase 5: Update presence tracking
        # Note: This assumes owner is present if app is running
        # In a more complete implementation, this could track actual user presence
        self.bonding.update_presence(is_present=True, delta_time=delta_time)

    def feed(self, amount: float = 30, food_type: str = "generic"):
        """
        Feed the creature, reducing hunger.

        Args:
            amount: Amount to reduce hunger (default 30)
            food_type: Type of food being given (for preferences)
        """
        old_hunger = self.hunger
        self.hunger = max(0, self.hunger - amount)
        self.last_fed_time = time.time()
        self.happiness = min(100, self.happiness + 5)
        self.last_interaction_time = time.time()

        # Phase 5: Determine if feeding was timely based on hunger level
        timely = old_hunger > 40  # Feeding when actually hungry is timely

        # Phase 5: Process bonding interaction
        bond_gain, bond_message = self.bonding.process_interaction(
            'feed',
            positive=True,
            quality=1.0 if timely else 0.7
        )

        # Phase 5: Process trust care event
        self.trust.process_care_event('feed', timely=timely)

        # Phase 5: Update food preference based on enjoyment
        enjoyment = 0.3  # Base enjoyment from feeding
        if old_hunger > 70:
            enjoyment = 0.8  # Very hungry = really enjoyed food
        elif old_hunger > 40:
            enjoyment = 0.5  # Moderately hungry
        self.preferences.record_experience('food', food_type, enjoyment)

        # Record in memory system (Phase 2)
        # Check if this is first feeding
        first_feeding = self.memory.recall_event('feed', first_only=True) is None
        importance = MemoryImportance.CRUCIAL.value if first_feeding else MemoryImportance.NORMAL.value

        self.memory.record_interaction(
            'feed',
            {
                'hunger_before': old_hunger,
                'hunger_after': self.hunger,
                'amount': amount,
                'food_type': food_type,
                'first_feeding': first_feeding,
                'positive': True,
                'timely': timely,
                'bond_gain': bond_gain,
                'stats': {'hunger': self.hunger, 'happiness': self.happiness, 'energy': self.energy}
            },
            important=first_feeding,
            emotional_intensity=0.7 if old_hunger > 70 else 0.5
        )

    def interact(self, interaction_type: str, positive: bool = True,
                 item: str = None, gentle: bool = True):
        """
        Record an interaction with the creature.

        Args:
            interaction_type: Type of interaction (e.g., 'play_ball', 'pet', 'give_toy')
            positive: Whether the interaction was positive (enjoyed) or negative
            item: Specific item involved (toy name, food type, etc.)
            gentle: Whether interaction was gentle (affects trust)
        """
        self.last_interaction_time = time.time()
        self.total_interactions += 1  # Phase 4: Track for evolution

        # Phase 5: Determine quality of interaction
        quality = 1.0
        if not positive:
            quality = 0.3
        elif self.energy < 20:
            quality = 0.6  # Too tired to fully enjoy

        # Phase 5: Process bonding interaction
        bond_gain, bond_message = self.bonding.process_interaction(
            interaction_type,
            positive=positive,
            quality=quality
        )

        # Phase 5: Process trust based on interaction quality
        self.trust.process_interaction_quality(gentle=gentle)

        # Phase 5: Reset attention to others tracking (receiving attention)
        self.emotional_states.reset_attention_tracking()

        # Phase 5: Update preferences based on interaction
        if item:
            # Map interaction type to preference category
            category = None
            if interaction_type in ['play_ball', 'give_toy', 'toy_interaction']:
                category = 'toy'
            elif interaction_type in ['feed']:
                category = 'food'
            elif interaction_type in ['play', 'training', 'pet', 'talk']:
                category = 'activity'

            if category:
                enjoyment = 0.7 if positive else -0.4
                if not gentle:
                    enjoyment -= 0.3  # Rough handling reduces enjoyment
                self.preferences.record_experience(category, item or interaction_type, enjoyment)

        # Record in history for neural network learning
        interaction_data = {
            'type': interaction_type,
            'positive': positive,
            'timestamp': time.time(),
            'hunger_level': self.hunger,
            'energy_level': self.energy,
            'happiness_level': self.happiness,
            'bond_gain': bond_gain,
            'gentle': gentle
        }
        self.interaction_history.append(interaction_data)

        # Keep only recent history (last 100 interactions)
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]

        # Update happiness
        happiness_change = 3 if positive else -1
        happiness_multiplier = self.trait_modifiers.get('happiness_gain', 1.0)
        variant_multiplier = self.variant.get_happiness_multiplier()  # Phase 4

        # Phase 5: Apply emotional state modifiers
        emotional_mods = self.emotional_states.get_behavioral_modifiers()
        happiness_multiplier *= emotional_mods.get('happiness_modifier', 1.0)

        self.happiness = max(0, min(100, self.happiness + happiness_change * happiness_multiplier * variant_multiplier))

        # Phase 4: Check for evolution after interaction
        self._check_evolution(EvolutionTrigger.INTERACTION)

        # Record in memory system (Phase 2)
        emotional_intensity = 0.7 if positive else 0.3
        self.memory.record_interaction(
            interaction_type,
            {
                'positive': positive,
                'gentle': gentle,
                'item': item,
                'bond_gain': bond_gain,
                'quality': quality,
                'stats': {
                    'hunger': self.hunger,
                    'happiness': self.happiness,
                    'energy': self.energy
                },
                'outcome': 'enjoyed' if positive else 'disliked'
            },
            important=False,
            emotional_intensity=emotional_intensity
        )

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

    def get_recent_interaction_quality(self, count: int = 10) -> list:
        """
        Get quality scores of recent interactions for emotion network.

        Args:
            count: Number of recent interactions to return

        Returns:
            List of quality scores (0-1 scale) for recent interactions
        """
        if not self.interaction_history:
            return [0.5] * count

        recent = self.interaction_history[-count:]
        quality = []

        for interaction in recent:
            # Calculate quality based on positive feedback
            q = 1.0 if interaction.get('positive', False) else 0.3
            quality.append(q)

        # Pad if needed
        while len(quality) < count:
            quality.insert(0, 0.5)

        return quality[:count]

    def get_recent_interaction_types(self, count: int = 5) -> list:
        """
        Get encoding of recent interaction types for social network.

        Args:
            count: Number of recent interactions to encode

        Returns:
            List of encoded interaction types
        """
        if not self.interaction_history:
            return [0.0] * count

        recent = self.interaction_history[-count:]
        type_mapping = {'feed': 0.2, 'play_ball': 0.4, 'pet': 0.6, 'talk': 0.8, 'other': 0.5}

        encoded = []
        for interaction in recent:
            interaction_type = interaction.get('type', 'other')
            encoded.append(type_mapping.get(interaction_type, 0.5))

        # Pad if needed
        while len(encoded) < count:
            encoded.insert(0, 0.0)

        return encoded[:count]

    def get_recent_activities(self, count: int = 5) -> list:
        """
        Get encoding of recent activities for activity network.

        Args:
            count: Number of recent activities to return

        Returns:
            List of activity encodings (0-1 scale)
        """
        # This is a simplified version - in a more complete implementation,
        # we would track activity history similar to interaction history
        if not self.interaction_history:
            return [0.0] * count

        # Use interaction history as proxy for activities
        recent = self.interaction_history[-count:]
        activities = []

        for interaction in recent:
            # Map interaction types to activity encodings
            itype = interaction.get('type', 'idle')
            if itype == 'ball_play':
                activities.append(0.8)
            elif itype == 'mouse_chase':
                activities.append(0.6)
            elif itype in ['hide_and_seek', 'hide']:
                activities.append(0.4)
            elif itype == 'feed':
                activities.append(0.2)
            else:
                activities.append(0.0)

        # Pad if needed
        while len(activities) < count:
            activities.insert(0, 0.0)

        return activities[:count]

    def get_personality_vector(self) -> list:
        """
        Get one-hot encoded personality vector for networks.

        Returns:
            List representing personality as one-hot encoding
        """
        personalities = list(PersonalityType)
        encoding = [0.0] * len(personalities)

        try:
            idx = personalities.index(self.personality)
            encoding[idx] = 1.0
        except ValueError:
            pass

        return encoding

    def get_state_for_networks(self, target_x: float = None, target_y: float = None) -> Dict[str, Any]:
        """
        Get comprehensive state dictionary for all AI networks.

        This provides all the state information needed by:
        - MovementNetwork
        - ActivityNetwork
        - EmotionNetwork
        - SocialNetwork
        - ReinforcementLearning systems

        Args:
            target_x: Optional target x coordinate for movement
            target_y: Optional target y coordinate for movement

        Returns:
            Dictionary with complete state information
        """
        import math

        # Calculate distance to target if provided
        distance_to_target = 0.0
        if target_x is not None and target_y is not None:
            dx = target_x - self.position[0]
            dy = target_y - self.position[1]
            distance_to_target = math.sqrt(dx * dx + dy * dy)

        return {
            # Basic stats
            'hunger': self.hunger,
            'energy': self.energy,
            'happiness': self.happiness,
            'age': self.age,

            # Position and movement
            'pos_x': self.position[0],
            'pos_y': self.position[1],
            'target_x': target_x if target_x is not None else self.position[0],
            'target_y': target_y if target_y is not None else self.position[1],
            'distance_to_target': distance_to_target,
            'velocity_x': self.velocity[0],
            'velocity_y': self.velocity[1],

            # Time-based
            'time_since_interaction': time.time() - self.last_interaction_time,
            'time_since_fed': time.time() - self.last_fed_time,

            # Personality
            'personality': self.personality.value,
            'personality_vector': self.get_personality_vector(),

            # Learning and history
            'recent_interaction_quality': self.get_recent_interaction_quality(10),
            'recent_interaction_types': self.get_recent_interaction_types(5),
            'recent_activities': self.get_recent_activities(5),

            # Preferences
            'preference_scores': self.preference_scores.copy(),

            # State
            'current_state': self.current_state.value,
            'alive': not self.is_starving(),
            'should_sleep': self.should_sleep(),

            # Emotional state placeholder (will be filled by emotion network)
            'emotional_state': [0.5, 0.5, 0.5, 0.5, 0.5],

            # Player mood estimate (simplified - could be enhanced)
            'player_mood_estimate': 0.5 if self.happiness > 60 else 0.3,

            # Screen edge distances (will be filled by sensory system or pet_manager)
            'edge_top': 0,
            'edge_bottom': 0,
            'edge_left': 0,
            'edge_right': 0,
        }

    # ============ Phase 2: Training & Memory Methods ============

    def process_command(self, command_text: str) -> Tuple[bool, str, Optional[str]]:
        """
        Process a training command.

        Args:
            command_text: Text command from user

        Returns:
            Tuple of (success, message, action_to_perform)
        """
        mood = self.happiness / 100.0  # Convert happiness to 0-1 mood
        return self.training.process_command(command_text, current_mood=mood)

    def practice_trick(self, trick_name: str) -> Tuple[bool, str, float]:
        """
        Practice a specific trick.

        Args:
            trick_name: Name of the trick

        Returns:
            Tuple of (success, message, proficiency_gain)
        """
        mood = self.happiness / 100.0
        success, message, gain = self.training.practice_trick(trick_name, mood=mood)

        # Record in memory if learned trick
        if success:
            trick = self.training.learned_tricks.get(trick_name)
            if trick and trick.can_perform() and gain > 0.1:  # Significant progress
                self.memory.record_interaction(
                    'learned_trick',
                    {
                        'trick_name': trick_name,
                        'proficiency': trick.proficiency,
                        'practice_count': trick.practice_count
                    },
                    important=True,
                    emotional_intensity=0.8
                )

        return success, message, gain

    def get_known_tricks(self) -> List[str]:
        """Get list of tricks the pet knows how to perform."""
        return self.training.get_known_tricks()

    def get_learning_tricks(self) -> List[str]:
        """Get list of tricks currently being learned."""
        return self.training.get_learning_tricks()

    def recall_memory(self, event_type: Optional[str] = None, first_only: bool = False) -> Optional[Dict[str, Any]]:
        """
        Recall a memory.

        Args:
            event_type: Type of event to recall (None = any)
            first_only: Return only the first memory of this type

        Returns:
            Memory dict or None
        """
        return self.memory.recall_event(event_type, first_only=first_only)

    def get_feeding_pattern(self) -> Optional[int]:
        """Get the expected hour for feeding based on learned patterns."""
        return self.memory.get_pattern_knowledge('feeding_time')

    def consolidate_memories(self):
        """Consolidate working memory into long-term storage."""
        if self.memory.consolidation.should_consolidate():
            self.memory.consolidation.consolidate()

    def update_training(self):
        """Update training system (handle skill decay, etc.)."""
        self.training.update_skill_decay()

    # ============ Phase 4: Evolution, Element, Variant Methods ============

    def _check_evolution(self, trigger: EvolutionTrigger):
        """
        Internal method to check if evolution should occur.

        Args:
            trigger: What triggered this evolution check
        """
        stats = self.get_evolution_stats()
        result = self.evolution.auto_check_evolution(stats, trigger)

        if result and result.get('ready'):
            # Record evolution readiness in memory
            self.memory.record_interaction(
                'evolution_ready',
                {
                    'next_stage': result['next_stage'].value,
                    'current_stage': self.evolution.current_stage.value
                },
                important=True,
                emotional_intensity=0.9
            )

    def get_evolution_stats(self) -> Dict[str, Any]:
        """
        Get current stats for evolution checking.

        Returns:
            Dictionary with evolution-relevant stats
        """
        return {
            'age_hours': self.age / 3600.0,  # Convert seconds to hours
            'happiness': self.happiness,
            'bond': self.bonding.bond,  # Phase 5: Use bonding system
            'total_interactions': self.total_interactions,
            'tricks_learned': len(self.get_known_tricks())
        }

    def can_evolve(self) -> Tuple[bool, Optional[EvolutionStage], str]:
        """
        Check if creature can evolve.

        Returns:
            Tuple of (can_evolve, next_stage, reason)
        """
        stats = self.get_evolution_stats()
        return self.evolution.check_evolution_eligibility(stats)

    def evolve(self) -> Tuple[bool, str]:
        """
        Attempt to evolve the creature.

        Returns:
            Tuple of (success, message)
        """
        stats = self.get_evolution_stats()
        success, new_stage, message = self.evolution.evolve(stats)

        if success:
            # Record evolution in memory as crucial event
            self.memory.record_interaction(
                'evolved',
                {
                    'old_stage': self.evolution.evolution_history[-1]['from_stage'].value,
                    'new_stage': new_stage.value,
                    'age_hours': stats['age_hours'],
                    'bond': self.bonding.bond  # Phase 5: Use bonding system
                },
                important=True,
                emotional_intensity=1.0
            )

        return success, message

    def get_evolution_progress(self) -> Dict[str, Any]:
        """Get detailed evolution progress information."""
        stats = self.get_evolution_stats()
        return self.evolution.get_evolution_progress(stats)

    def interact_with_element(self, other_element: ElementType) -> Dict[str, Any]:
        """
        Interact with another element (e.g., elemental toy, another creature).

        Args:
            other_element: The other element involved

        Returns:
            Dictionary with interaction results
        """
        result = self.element.interact_with_element(other_element)

        # Apply effects
        happiness_change = result.get('happiness_change', 0)
        bond_change = result.get('bond_change', 0)

        self.happiness = max(0, min(100, self.happiness + happiness_change))
        # Phase 5: Use bonding system for bond changes
        if bond_change > 0:
            self.bonding.add_bond(bond_change, 'elemental_interaction')
        elif bond_change < 0:
            self.bonding.reduce_bond(abs(bond_change), 'elemental_interaction')

        # Record in memory if significant
        if abs(happiness_change) > 5 or bond_change > 3:
            self.memory.record_interaction(
                'elemental_interaction',
                {
                    'my_element': self.element.primary_element.value,
                    'other_element': other_element.value,
                    'interaction_type': result['interaction_type'],
                    'multiplier': result['multiplier']
                },
                important=(result['interaction_type'] == 'super_effective'),
                emotional_intensity=0.6
            )

        return result

    def get_display_info(self) -> Dict[str, Any]:
        """
        Get information for UI display.

        Returns:
            Dictionary with display information
        """
        return {
            'name': self.name,
            'type': self.creature_type,
            'personality': self.personality.value,
            'stage': self.evolution.get_stage_name(),
            'element': self.element.primary_element.value,
            'variant': self.variant.variant.value,
            'variant_emoji': self.variant.get_variant_emoji(),
            'is_rare': self.variant.is_rare(),
            'level': self.evolution.current_stage.value,
            'age_hours': self.age / 3600.0,
            'stats': {
                'hunger': self.hunger,
                'happiness': self.happiness,
                'energy': self.energy,
                'bond': self.bonding.bond  # Phase 5: Use bonding system
            },
            'known_tricks': len(self.get_known_tricks()),
            'total_interactions': self.total_interactions
        }

    def get_particle_effects(self) -> List[str]:
        """
        Get list of particle effects to display.

        Returns:
            List of particle effect identifiers
        """
        effects = []

        # Element-based particles
        effects.append(self.element.get_particle_effect_type())

        # Variant-based particles
        effects.extend(self.variant.get_particle_effects())

        return effects

    # ============ Phase 5: Advanced Bonding Methods ============

    def call_by_name(self, called_name: str) -> Dict[str, Any]:
        """
        Call the pet by name and get response.

        Args:
            called_name: Name being called

        Returns:
            Dictionary with response details (responded, animation, message, bond_change)
        """
        # Get name recognition proficiency from training system
        name_recognition = self.training.name_recognition.recognition_proficiency

        # Get current mood (basic version using happiness)
        current_mood = None
        if self.happiness > 80:
            current_mood = 'happy'
        elif self.happiness < 30:
            current_mood = 'grumpy'
        elif self.energy < 20:
            current_mood = 'tired'

        # Call the pet
        result = self.name_calling.call_pet(
            pet_name=called_name,
            actual_name=self.name,
            bond_level=self.bonding.bond,
            trust_level=self.trust.trust,
            personality=self.personality.value,
            name_recognition_proficiency=name_recognition,
            current_mood=current_mood
        )

        # Apply bond change if any
        if result.get('bond_change', 0) != 0:
            bond_change = result['bond_change']
            if bond_change > 0:
                self.bonding.add_bond(bond_change, 'called_by_name')
            else:
                self.bonding.reduce_bond(abs(bond_change), 'ignored_call')

        # Record in memory if responded
        if result['responded']:
            self.memory.record_interaction(
                'called_by_name',
                {
                    'name_called': called_name,
                    'response_type': result.get('response_type'),
                    'bond_change': result.get('bond_change', 0)
                },
                important=(self.bonding.first_time_called_by_name is None),
                emotional_intensity=0.6
            )

            # Mark first time called by name
            if self.bonding.first_time_called_by_name is None:
                self.bonding.first_time_called_by_name = time.time()

        return result

    def check_separation_anxiety(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if pet has separation anxiety.

        Returns:
            Tuple of (has_anxiety, anxiety_info)
        """
        has_anxiety = self.emotional_states.has_state(EmotionalState.SEPARATION_ANXIETY)

        if has_anxiety:
            intensity = self.emotional_states.get_state_intensity(EmotionalState.SEPARATION_ANXIETY)
            return True, {
                'intensity': intensity,
                'bond_level': self.bonding.bond,
                'times_experienced': self.emotional_states.times_experienced_separation
            }

        return False, None

    def process_owner_return(self, hours_away: float):
        """
        Process owner returning after being away.

        Args:
            hours_away: How many hours owner was gone
        """
        # Trigger excited return emotional state
        self.emotional_states.trigger_excited_return(
            bond_level=self.bonding.bond,
            hours_away=hours_away
        )

        # Update bonding system presence
        self.emotional_states.set_owner_presence(
            present=True,
            bond_level=self.bonding.bond,
            trust_level=self.trust.trust
        )

        # Record in memory if significant absence
        if hours_away > 2:
            self.memory.record_interaction(
                'owner_returned',
                {
                    'hours_away': hours_away,
                    'bond_level': self.bonding.bond,
                    'excitement_level': self.emotional_states.reunion_excitement_level
                },
                important=(hours_away > 6),
                emotional_intensity=min(1.0, hours_away / 6)
            )

    def process_owner_departure(self):
        """Process owner leaving."""
        self.emotional_states.set_owner_presence(
            present=False,
            bond_level=self.bonding.bond,
            trust_level=self.trust.trust
        )

    def trigger_jealousy(self, attention_amount: float = 0.3):
        """
        Trigger jealousy from seeing attention given to others.

        Args:
            attention_amount: Amount of attention given to others (0-1)
        """
        # Process attention to others
        self.emotional_states.process_attention_to_other(attention_amount)

        # Maybe trigger jealousy based on bond level
        jealousy_chance = self.bonding.get_jealousy_chance(
            self.emotional_states.attention_to_others_score
        )

        if random.random() < jealousy_chance:
            self.emotional_states.trigger_jealousy(
                bond_level=self.bonding.bond,
                trigger_intensity=attention_amount
            )

    def get_preference_reaction(self, category: str, item: str) -> Dict[str, Any]:
        """
        Get reaction to a specific item based on preferences.

        Args:
            category: Category ('toy', 'food', 'activity')
            item: Specific item name

        Returns:
            Dictionary with reaction info
        """
        return self.preferences.get_reaction_to_item(category, item)

    def get_favorite_items(self) -> Dict[str, Optional[str]]:
        """
        Get favorite items across all categories.

        Returns:
            Dictionary with favorite items
        """
        favorites = self.preferences.get_favorites()

        # Also add top preference from each category
        top_toys = self.preferences.get_top_preferences('toy', 1)
        top_foods = self.preferences.get_top_preferences('food', 1)
        top_activities = self.preferences.get_top_preferences('activity', 1)

        favorites['top_toy'] = top_toys[0][0] if top_toys else None
        favorites['top_food'] = top_foods[0][0] if top_foods else None
        favorites['top_activity'] = top_activities[0][0] if top_activities else None

        return favorites

    def get_bond_level_name(self) -> str:
        """Get the name of current bond level."""
        return self.bonding.get_bond_level().value

    def get_bonding_stats(self) -> Dict[str, Any]:
        """Get detailed bonding statistics."""
        stats = {
            'bond': self.bonding.bond,
            'bond_level': self.bonding.get_bond_level().value,
            'bond_description': self.bonding.get_bond_description(),
            'trust': self.trust.trust,
            'trust_description': self.trust.get_trust_level_description(),
            'emotional_states': self.emotional_states.get_current_states(),
            'favorite_items': self.get_favorite_items(),
            'name_calling_stats': self.name_calling.get_stats()
        }
        return stats

    # ============ Phase 6: Enhanced Training Methods ============

    def train_with_reinforcement(self, trick_name: str, reinforcement_type: str = 'verbal_praise') -> Dict[str, Any]:
        """
        Practice a trick with specific reinforcement.

        Args:
            trick_name: Name of trick to practice
            reinforcement_type: Type of reinforcement (verbal_praise, treat, toy_reward, affection, punishment, ignore)

        Returns:
            Dictionary with training results and effects
        """
        # Practice the trick
        success, message, gain = self.practice_trick(trick_name)

        result = {
            'success': success,
            'message': message,
            'proficiency_gain': gain,
            'reinforcement_applied': False
        }

        # Apply reinforcement if Phase 6 is enabled
        if self.training.phase6_enabled and self.training.reinforcement:
            try:
                from .enhanced_training import ReinforcementType
                rtype = ReinforcementType(reinforcement_type)

                effects = self.training.reinforcement.apply_reinforcement(
                    rtype,
                    trick_name,
                    success,
                    self.trait_modifiers
                )

                # Apply effects
                self.bonding.add_bond(effects['bond_change'], 'training_reinforcement')
                self.trust.process_training_reinforcement(
                    trust_change=effects['trust_change'],
                    was_positive=(effects['trust_change'] >= 0)
                )
                self.happiness = max(0, min(100, self.happiness + effects['happiness_change']))

                result['reinforcement_applied'] = True
                result['reinforcement_effects'] = effects
                result['message'] += f" {effects['message']}"

            except (ImportError, ValueError):
                pass  # Phase 6 not available or invalid reinforcement type

        return result

    def check_command_compliance(self, command: str) -> Tuple[bool, str]:
        """
        Check if pet will comply with a command based on current state.

        Uses Phase 6 advanced stubbornness calculator if available.

        Args:
            command: Command to check

        Returns:
            Tuple of (will_comply, refusal_reason)
        """
        # Count recent commands (last 5 minutes)
        now = time.time()
        recent_commands = sum(1 for h in self.interaction_history
                            if now - h['timestamp'] < 300)

        if self.training.phase6_enabled and self.training.stubbornness_calc:
            # Phase 6: Advanced stubbornness calculation
            refusal_chance, reason = self.training.stubbornness_calc.calculate_refusal_chance(
                base_stubbornness=self.training.learning_modifiers.get('stubbornness', 0.5),
                happiness=self.happiness,
                trust=self.trust.trust,
                bond=self.bonding.bond,
                hunger=self.hunger,
                energy=self.energy,
                recent_commands=recent_commands
            )

            will_comply = self.training.stubbornness_calc.will_comply(refusal_chance)
            return will_comply, reason if not will_comply else ""

        else:
            # Fallback to basic stubbornness (Phase 2 behavior)
            base_stubbornness = self.training.learning_modifiers.get('stubbornness', 0.5)
            will_comply = random.random() > base_stubbornness
            return will_comply, "feeling stubborn" if not will_comply else ""

    def start_training_session(self):
        """Start a new training session (Phase 6)."""
        if self.training.phase6_enabled and self.training.progress_tracker:
            self.training.progress_tracker.start_session()

    def end_training_session(self) -> Optional[Dict[str, Any]]:
        """
        End current training session and get statistics (Phase 6).

        Returns:
            Session statistics or None if Phase 6 not enabled
        """
        if self.training.phase6_enabled and self.training.progress_tracker:
            return self.training.progress_tracker.end_session()
        return None

    def get_training_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive training statistics.

        Returns:
            Dictionary with training analytics
        """
        stats = {
            'known_tricks': len(self.get_known_tricks()),
            'learning_tricks': len(self.get_learning_tricks()),
            'mastered_tricks': len(self.training.get_mastered_tricks()) if hasattr(self.training, 'get_mastered_tricks') else 0,
            'phase6_enabled': self.training.phase6_enabled
        }

        # Add Phase 6 statistics if available
        if self.training.phase6_enabled:
            if self.training.progress_tracker:
                stats.update(self.training.progress_tracker.get_training_stats())

            if self.training.reinforcement:
                stats['total_treats_given'] = self.training.reinforcement.total_treats_given
                stats['total_praise_given'] = self.training.reinforcement.total_praise_given
                stats['total_punishments'] = self.training.reinforcement.total_punishments
                stats['most_effective_reinforcement'] = self.training.reinforcement.get_most_effective_reinforcement().value

        return stats

    # ============ Phase 7: Enhanced Memory Methods ============

    def process_sleep_cycle(self, sleep_duration_hours: float):
        """
        Process dreaming during sleep (Phase 7).

        Args:
            sleep_duration_hours: How long the pet has been sleeping
        """
        if not self.phase7_enabled or not self.dream_system:
            return

        # Check if should dream
        hours_since_dream = 999  # Default to trigger first dream
        if self.dream_system.last_dream_time:
            hours_since_dream = (time.time() - self.dream_system.last_dream_time) / 3600

        if self.dream_system.should_dream(True, hours_since_dream):
            # Get recent memories for dream processing
            recent_memories = self.interaction_history[-20:] if self.interaction_history else []

            # Process dream
            emotional_state = self.happiness / 100.0
            dream = self.dream_system.process_dream(recent_memories, emotional_state)

            # Record dream in memory
            self.memory.record_interaction(
                'dreamed',
                {
                    'dream_type': dream['dream_type'],
                    'themes': dream['memory_themes'],
                    'memories_processed': dream['memories_processed']
                },
                important=False,
                emotional_intensity=0.4
            )

    def record_first_time_experience(self, event_type: str, details: Dict[str, Any]) -> bool:
        """
        Record a first-time experience (Phase 7).

        Args:
            event_type: Type of first time event
            details: Event details

        Returns:
            True if this was actually a first time
        """
        if not self.phase7_enabled or not self.autobiographical:
            return False

        emotional_intensity = min(1.0, self.happiness / 100.0 + 0.3)
        was_first_time = self.autobiographical.record_first_time(
            event_type, details, emotional_intensity
        )

        return was_first_time

    def consider_as_favorite_memory(self, event_type: str, details: Dict[str, Any]):
        """
        Consider adding current experience as a favorite memory (Phase 7).

        Args:
            event_type: Type of event
            details: Event details
        """
        if not self.phase7_enabled or not self.favorite_memories:
            return

        happiness_level = self.happiness / 100.0
        emotional_intensity = 0.5  # Base level

        # High happiness + high energy = more emotionally intense
        if self.happiness > 80 and self.energy > 60:
            emotional_intensity = 0.9

        self.favorite_memories.consider_as_favorite(
            event_type, details, happiness_level, emotional_intensity
        )

    def record_trauma(self, event_type: str, details: Dict[str, Any],
                     severity: float, trigger: Optional[str] = None):
        """
        Record a traumatic experience (Phase 7).

        Args:
            event_type: Type of trauma
            details: Event details
            severity: How traumatic (0-1)
            trigger: Optional fear trigger
        """
        if not self.phase7_enabled or not self.trauma_memory:
            return

        self.trauma_memory.record_trauma(event_type, details, severity, trigger)

        # Traumatic experiences affect trust and bond
        self.trust.reduce_trust(severity * 10, 'traumatic_experience')
        self.bonding.reduce_bond(severity * 5, 'traumatic_experience')

    def check_fear_trigger(self, trigger: str) -> Tuple[bool, float]:
        """
        Check if something triggers a fear response (Phase 7).

        Args:
            trigger: Potential fear trigger

        Returns:
            Tuple of (is_triggered, fear_intensity)
        """
        if not self.phase7_enabled or not self.trauma_memory:
            return False, 0.0

        return self.trauma_memory.check_trigger(trigger)

    def learn_association(self, context_type: str, context_value: str,
                         event_type: str, was_positive: bool):
        """
        Learn an association between context and outcome (Phase 7).

        Args:
            context_type: 'location', 'time', or 'object'
            context_value: Specific context value
            event_type: What happened
            was_positive: Whether outcome was positive
        """
        if not self.phase7_enabled or not self.associative_memory:
            return

        outcome_valence = 0.7 if was_positive else -0.7
        self.associative_memory.record_association(
            context_type, context_value, event_type, outcome_valence
        )

    def predict_from_context(self, context_type: str, context_value: str) -> Optional[str]:
        """
        Predict what might happen based on learned associations (Phase 7).

        Args:
            context_type: Type of context
            context_value: Specific context

        Returns:
            Predicted event or None
        """
        if not self.phase7_enabled or not self.associative_memory:
            return None

        return self.associative_memory.get_pattern_prediction(context_type, context_value)

    def get_favorite_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get pet's favorite memories (Phase 7).

        Args:
            limit: Number of favorites to return

        Returns:
            List of favorite memory dictionaries
        """
        if not self.phase7_enabled or not self.favorite_memories:
            return []

        return self.favorite_memories.get_favorites(limit)

    def recall_first_time(self, event_type: str) -> Optional[Dict[str, Any]]:
        """
        Recall a first-time experience (Phase 7).

        Args:
            event_type: Type of event to recall

        Returns:
            First time memory or None
        """
        if not self.phase7_enabled or not self.autobiographical:
            return None

        return self.autobiographical.recall_first_time(event_type)

    def get_life_story(self, max_events: int = 10) -> List[Dict[str, Any]]:
        """
        Get summary of pet's life story (Phase 7).

        Args:
            max_events: Maximum events to return

        Returns:
            List of significant life events
        """
        if not self.phase7_enabled or not self.autobiographical:
            return []

        return self.autobiographical.get_life_summary(max_events)

    def get_dream_statistics(self) -> Dict[str, Any]:
        """Get statistics about dreams (Phase 7)."""
        if not self.phase7_enabled or not self.dream_system:
            return {'total_dreams': 0, 'phase7_enabled': False}

        stats = self.dream_system.get_dream_statistics()
        stats['phase7_enabled'] = True
        return stats

    def to_dict(self) -> Dict[str, Any]:
        """Convert creature to dictionary for saving (with Phases 2-7)."""
        data = {
            'creature_type': self.creature_type,
            'personality': self.personality.value,
            'color_palette': self.color_palette,
            'name': self.name,
            'hunger': self.hunger,
            'happiness': self.happiness,
            'energy': self.energy,
            'total_interactions': self.total_interactions,
            'birth_time': self.birth_time,
            'last_fed_time': self.last_fed_time,
            'last_interaction_time': self.last_interaction_time,
            'position': self.position,
            'interaction_history': self.interaction_history,
            # Phase 2: Memory and Training
            'memory_system': self.memory.to_dict(),
            'training_system': self.training.to_dict(),
            # Phase 4: Evolution, Element, Variant
            'evolution_system': self.evolution.to_dict(),
            'element_system': self.element.to_dict(),
            'variant_system': self.variant.to_dict(),
            # Phase 5: Advanced Bonding Systems
            'bonding_system': self.bonding.to_dict(),
            'trust_system': self.trust.to_dict(),
            'emotional_states': self.emotional_states.to_dict(),
            'preference_system': self.preferences.to_dict(),
            'name_calling_system': self.name_calling.to_dict(),
            # Phase 7: Enhanced Memory Systems
            'phase7_enabled': self.phase7_enabled
        }

        # Phase 7: Save enhanced memory systems
        if self.phase7_enabled:
            if self.autobiographical:
                data['autobiographical_memory'] = self.autobiographical.to_dict()
            if self.favorite_memories:
                data['favorite_memories'] = self.favorite_memories.to_dict()
            if self.trauma_memory:
                data['trauma_memory'] = self.trauma_memory.to_dict()
            if self.associative_memory:
                data['associative_memory'] = self.associative_memory.to_dict()
            if self.dream_system:
                data['dream_system'] = self.dream_system.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Creature':
        """Create a creature from a dictionary (with Phases 2-5)."""
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
        creature.total_interactions = data.get('total_interactions', 0)
        creature.birth_time = data['birth_time']
        creature.last_fed_time = data['last_fed_time']
        creature.last_interaction_time = data['last_interaction_time']
        creature.position = data['position']
        creature.interaction_history = data['interaction_history']

        # Phase 2: Restore memory and training if present
        if 'memory_system' in data:
            creature.memory = IntegratedMemorySystem.from_dict(data['memory_system'])

        if 'training_system' in data:
            creature.training = TrainingSystem.from_dict(data['training_system'])

        # Phase 4: Restore evolution, element, variant if present
        if 'evolution_system' in data:
            creature.evolution = EvolutionSystem.from_dict(data['evolution_system'])

        if 'element_system' in data:
            creature.element = ElementSystem.from_dict(data['element_system'])

        if 'variant_system' in data:
            creature.variant = VariantSystem.from_dict(data['variant_system'])

        # Phase 5: Restore bonding systems if present
        if 'bonding_system' in data:
            creature.bonding = BondingSystem.from_dict(data['bonding_system'])

        if 'trust_system' in data:
            creature.trust = TrustSystem.from_dict(data['trust_system'])

        if 'emotional_states' in data:
            creature.emotional_states = EmotionalStateManager.from_dict(data['emotional_states'])

        if 'preference_system' in data:
            creature.preferences = PreferenceSystem.from_dict(data['preference_system'])

        if 'name_calling_system' in data:
            creature.name_calling = NameCallingSystem.from_dict(data['name_calling_system'])

        # Phase 7: Restore enhanced memory systems if present
        if data.get('phase7_enabled', False) and creature.phase7_enabled:
            if 'autobiographical_memory' in data:
                from .enhanced_memory import AutobiographicalMemory
                creature.autobiographical = AutobiographicalMemory.from_dict(data['autobiographical_memory'])

            if 'favorite_memories' in data:
                from .enhanced_memory import FavoriteMemories
                creature.favorite_memories = FavoriteMemories.from_dict(data['favorite_memories'])

            if 'trauma_memory' in data:
                from .enhanced_memory import TraumaMemory
                creature.trauma_memory = TraumaMemory.from_dict(data['trauma_memory'])

            if 'associative_memory' in data:
                from .enhanced_memory import AssociativeMemory
                creature.associative_memory = AssociativeMemory.from_dict(data['associative_memory'])

            if 'dream_system' in data:
                from .enhanced_memory import DreamSystem
                creature.dream_system = DreamSystem.from_dict(data['dream_system'])

        return creature

    def __str__(self) -> str:
        """String representation of the creature."""
        return (f"{self.name} the {self.personality.value} {self.creature_type} "
                f"(Hunger: {self.hunger:.1f}, Happiness: {self.happiness:.1f}, "
                f"Energy: {self.energy:.1f})")
