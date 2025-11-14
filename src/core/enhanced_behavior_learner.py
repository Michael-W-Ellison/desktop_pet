"""
Enhanced Behavior Learner integrating all sophisticated AI systems.

Provides different AI complexity levels:
- SIMPLE: Basic feedforward network
- MEDIUM: Advanced network with LSTM memory
- ADVANCED: Full system with specialized networks and RL
- EXPERT: All features plus visualization and detailed logging
"""
import numpy as np
from typing import Dict, Any, Optional
from .config import AIComplexity, DEFAULT_AI_COMPLEXITY
from .neural_network import NeuralNetwork, BehaviorLearner as SimpleBehaviorLearner
from .advanced_network import AdvancedNeuralNetwork
from .lstm_network import LSTMNetwork
from .specialized_networks import NetworkCoordinator
from .sensory_system import CompleteSensorySystem
from .reinforcement_learning import GoalOrientedBehaviorSystem


class EnhancedBehaviorLearner:
    """
    Enhanced behavior learner with multiple AI complexity levels.

    Adapts sophistication based on user preference and creature age.
    """

    def __init__(self, creature, complexity: AIComplexity = DEFAULT_AI_COMPLEXITY):
        """
        Initialize enhanced behavior learner.

        Args:
            creature: The Creature instance to learn for
            complexity: AI complexity level
        """
        self.creature = creature
        self.complexity = complexity

        # Sensory system (used by all complexity levels above SIMPLE)
        self.sensory_system = None
        if complexity != AIComplexity.SIMPLE:
            self.sensory_system = CompleteSensorySystem()

        # Initialize appropriate AI system based on complexity
        if complexity == AIComplexity.SIMPLE:
            self._init_simple()
        elif complexity == AIComplexity.MEDIUM:
            self._init_medium()
        elif complexity == AIComplexity.ADVANCED:
            self._init_advanced()
        elif complexity == AIComplexity.EXPERT:
            self._init_expert()

        # Performance monitoring
        self.total_interactions = 0
        self.learning_history = []

    def _init_simple(self):
        """Initialize simple AI (basic feedforward network)."""
        self.simple_learner = SimpleBehaviorLearner(self.creature)
        self.network_coordinator = None
        self.rl_system = None

    def _init_medium(self):
        """Initialize medium AI (advanced network with LSTM)."""
        # Use advanced network with LSTM for activity prediction
        self.activity_network = LSTMNetwork(
            input_size=37,  # State + sensory inputs
            hidden_size=32,
            output_size=5,  # Activity probabilities
            num_layers=2,
            learning_rate=0.001,
            sequence_length=30
        )

        self.network_coordinator = None
        self.rl_system = None

    def _init_advanced(self):
        """Initialize advanced AI (full specialized networks + RL)."""
        # Complete network coordinator with all specialized networks
        self.network_coordinator = NetworkCoordinator()

        # Reinforcement learning system
        self.rl_system = GoalOrientedBehaviorSystem()

        self.activity_network = None

    def _init_expert(self):
        """Initialize expert AI (advanced + visualization + logging)."""
        # Same as advanced, but with additional monitoring
        self._init_advanced()

        # Additional expert features
        self.detailed_logging = True
        self.visualization_enabled = True
        self.performance_metrics = {
            'decisions_per_minute': [],
            'learning_rate_history': [],
            'reward_history': [],
            'exploration_rate': []
        }

    def update_sensory_inputs(self, mouse_x: float, mouse_y: float):
        """Update sensory system with current mouse position."""
        if self.sensory_system:
            self.sensory_system.update_mouse_position(mouse_x, mouse_y)

    def get_state_vector(self, activity_type: str = None) -> np.ndarray:
        """
        Get complete state vector for neural networks.

        Args:
            activity_type: Optional activity type for simple mode

        Returns:
            State vector appropriate for current complexity level
        """
        if self.complexity == AIComplexity.SIMPLE:
            # Simple state (from original implementation)
            state = [
                self.creature.hunger / 100.0,
                self.creature.energy / 100.0,
                self.creature.happiness / 100.0,
                min(1.0, (time.time() - self.creature.last_interaction_time) / 3600.0)
            ]

            if activity_type:
                activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'icon_interaction', 'idle']
                encoding = [0.0] * len(activities)
                if activity_type in activities:
                    encoding[activities.index(activity_type)] = 1.0
                state.extend(encoding)

            return np.array(state)

        else:
            # Enhanced state with sensory inputs
            basic_state = [
                self.creature.hunger / 100.0,
                self.creature.energy / 100.0,
                self.creature.happiness / 100.0,
                min(1.0, (time.time() - self.creature.last_interaction_time) / 3600.0),
                # Personality encoding
                *self._encode_personality()
            ]

            # Add sensory inputs
            if self.sensory_system:
                sensory_vector = self.sensory_system.get_complete_sensory_input(
                    self.creature.position[0],
                    self.creature.position[1]
                )
                basic_state = np.concatenate([basic_state, sensory_vector])

            return np.array(basic_state)

    def _encode_personality(self) -> list:
        """Encode personality as one-hot vector."""
        from .config import PersonalityType
        personalities = list(PersonalityType)
        encoding = [0.0] * len(personalities)

        try:
            idx = personalities.index(self.creature.personality)
            encoding[idx] = 1.0
        except (ValueError, AttributeError):
            pass

        return encoding

    def choose_activity(self) -> str:
        """
        Choose best activity based on AI complexity level.

        Returns:
            Activity name
        """
        if self.complexity == AIComplexity.SIMPLE:
            # Use simple learner
            return self.simple_learner.get_best_activity()

        elif self.complexity == AIComplexity.MEDIUM:
            # Use LSTM network
            state = self.get_state_vector()
            output = self.activity_network.predict(state)

            activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'explore', 'idle']
            return activities[np.argmax(output)]

        else:  # ADVANCED or EXPERT
            # Use full network coordinator
            state_dict = self._get_complete_state_dict()
            behavior = self.network_coordinator.decide_behavior(state_dict)

            return behavior.get('activity', 'idle')

    def _get_complete_state_dict(self) -> Dict[str, Any]:
        """Get complete state dictionary for advanced AI."""
        import time

        state_dict = {
            'hunger': self.creature.hunger,
            'energy': self.creature.energy,
            'happiness': self.creature.happiness,
            'time_since_interaction': time.time() - self.creature.last_interaction_time,
            'personality_vector': self._encode_personality(),
            'recent_interaction_quality': self._get_recent_interaction_quality(),
            'recent_activities': [0, 0, 0, 0, 0],  # Simplified
        }

        # Add sensory information
        if self.sensory_system:
            sensory_state = self.sensory_system.get_state_dict(
                self.creature.position[0],
                self.creature.position[1]
            )
            state_dict.update(sensory_state)

        return state_dict

    def _get_recent_interaction_quality(self) -> list:
        """Get quality of recent interactions (0-1 scale)."""
        if not hasattr(self.creature, 'interaction_history'):
            return [0.5] * 10

        recent = self.creature.interaction_history[-10:]
        quality = []

        for interaction in recent:
            # Calculate quality based on positive feedback
            q = 1.0 if interaction.get('positive', False) else 0.3
            quality.append(q)

        # Pad if needed
        while len(quality) < 10:
            quality.append(0.5)

        return quality[:10]

    def learn_from_interaction(self, activity_type: str, enjoyed: bool, outcome: Dict[str, Any] = None):
        """
        Learn from an interaction.

        Args:
            activity_type: Type of activity performed
            enjoyed: Whether the creature enjoyed it
            outcome: Additional outcome information
        """
        self.total_interactions += 1

        if self.complexity == AIComplexity.SIMPLE:
            # Simple learning
            self.simple_learner.learn_from_interaction(activity_type, enjoyed)

        elif self.complexity == AIComplexity.MEDIUM:
            # LSTM learning
            state = self.get_state_vector()
            target = np.zeros((1, 5))

            activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'explore', 'idle']
            if activity_type in activities:
                idx = activities.index(activity_type)
                target[0, idx] = 1.0 if enjoyed else 0.2

            self.activity_network.add_to_sequence(state)

            if len(self.activity_network.sequence_buffer) >= 3:
                sequence = list(self.activity_network.sequence_buffer)[-3:]
                targets = [target] * len(sequence)
                self.activity_network.train_sequence(sequence, targets)

        else:  # ADVANCED or EXPERT
            # Full learning with all systems
            state_dict = self._get_complete_state_dict()

            # Learn with network coordinator
            action = {'activity': activity_type}
            outcome_dict = outcome or {'enjoyment': 1.0 if enjoyed else 0.3, 'reward': 0.5}

            self.network_coordinator.learn_from_outcome(
                state_dict,
                action,
                outcome_dict
            )

            # RL learning
            if self.rl_system and outcome:
                state_vector = self.get_state_vector()
                self.rl_system.learn_from_outcome(
                    state_vector,
                    outcome.get('action_idx', 0),
                    state_vector,  # Simplified - should be next state
                    outcome
                )

        # Record for expert mode
        if self.complexity == AIComplexity.EXPERT:
            self.learning_history.append({
                'interaction': self.total_interactions,
                'activity': activity_type,
                'enjoyed': enjoyed,
                'timestamp': time.time()
            })

    def get_behavioral_decision(self) -> Dict[str, Any]:
        """
        Get complete behavioral decision.

        Returns:
            Dictionary with activity, movement, emotional state, etc.
        """
        if self.complexity in [AIComplexity.SIMPLE, AIComplexity.MEDIUM]:
            # Simplified decision
            activity = self.choose_activity()
            return {
                'activity': activity,
                'velocity_x': 0,
                'velocity_y': 0,
                'should_move': False
            }

        else:  # ADVANCED or EXPERT
            # Full decision with all systems
            state_dict = self._get_complete_state_dict()

            # Get decision from network coordinator
            decision = self.network_coordinator.decide_behavior(state_dict)

            # Optionally use RL to refine decision
            if self.rl_system:
                state_vector = self.get_state_vector()
                rl_decision = self.rl_system.execute_goal(state_vector, state_dict)
                decision['rl_goal'] = rl_decision.get('goal')
                decision['rl_action'] = rl_decision.get('action')

            return decision

    def to_dict(self) -> Dict[str, Any]:
        """Save learner state."""
        data = {
            'complexity': self.complexity.value,
            'total_interactions': self.total_interactions
        }

        if self.complexity == AIComplexity.SIMPLE:
            data['simple_learner'] = self.simple_learner.to_dict()

        elif self.complexity == AIComplexity.MEDIUM:
            data['activity_network'] = self.activity_network.to_dict()

        else:  # ADVANCED or EXPERT
            if self.network_coordinator:
                data['network_coordinator'] = self.network_coordinator.to_dict()

            if self.rl_system:
                data['rl_system'] = self.rl_system.rl_agent.to_dict()

        if self.complexity == AIComplexity.EXPERT:
            data['learning_history'] = self.learning_history[-100:]  # Last 100 only

        return data

    @classmethod
    def from_dict(cls, creature, data: Dict[str, Any]) -> 'EnhancedBehaviorLearner':
        """Load learner state."""
        from .config import AIComplexity

        complexity_str = data.get('complexity', DEFAULT_AI_COMPLEXITY.value)
        complexity = AIComplexity(complexity_str)

        learner = cls(creature, complexity)
        learner.total_interactions = data.get('total_interactions', 0)

        if complexity == AIComplexity.SIMPLE and 'simple_learner' in data:
            learner.simple_learner = SimpleBehaviorLearner.from_dict(creature, data['simple_learner'])

        elif complexity == AIComplexity.MEDIUM and 'activity_network' in data:
            learner.activity_network = LSTMNetwork.from_dict(data['activity_network'])

        else:  # ADVANCED or EXPERT
            if 'network_coordinator' in data:
                learner.network_coordinator = NetworkCoordinator.from_dict(data['network_coordinator'])

            if 'rl_system' in data:
                from .reinforcement_learning import ReinforcementLearningAgent
                learner.rl_system.rl_agent = ReinforcementLearningAgent.from_dict(data['rl_system'])

        if complexity == AIComplexity.EXPERT and 'learning_history' in data:
            learner.learning_history = data['learning_history']

        return learner


# Import time at module level
import time
