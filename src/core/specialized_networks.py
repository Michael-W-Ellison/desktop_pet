"""
Multiple specialized neural networks for different aspects of creature behavior.

Each network focuses on a specific aspect:
- MovementNetwork: Decides where and how to move
- ActivityNetwork: Chooses activities based on context
- EmotionNetwork: Manages emotional responses
- SocialNetwork: Learns player interaction patterns

These networks communicate and influence each other for complex, realistic behavior.
"""
import numpy as np
from typing import Dict, Any, List, Tuple
from .advanced_network import AdvancedNeuralNetwork
from .lstm_network import LSTMNetwork


class MovementNetwork:
    """
    Specialized network for movement decisions.

    Learns optimal movement patterns based on:
    - Current position on screen
    - Target location (mouse, food, hiding spot)
    - Energy level
    - Personality traits
    """

    def __init__(self, learning_rate: float = 0.001):
        """Initialize movement network."""
        # Input: [pos_x, pos_y, target_x, target_y, energy, distance_to_target,
        #         screen_edge_distances (4), personality_encoding (8)]
        # Output: [velocity_x, velocity_y, should_move]
        self.network = AdvancedNeuralNetwork(
            input_size=18,
            hidden_layers=[32, 16, 8],
            output_size=3,
            learning_rate=learning_rate,
            dropout_rate=0.2
        )

    def predict_movement(self, state: Dict[str, Any]) -> Tuple[float, float, bool]:
        """
        Predict movement action.

        Args:
            state: Dictionary with position, target, energy, etc.

        Returns:
            (velocity_x, velocity_y, should_move)
        """
        # Encode state
        input_vector = np.array([
            state.get('pos_x', 0) / 1920,  # Normalize to screen size
            state.get('pos_y', 0) / 1080,
            state.get('target_x', 0) / 1920,
            state.get('target_y', 0) / 1080,
            state.get('energy', 100) / 100,
            min(1.0, state.get('distance_to_target', 0) / 500),
            # Edge distances (normalized)
            state.get('edge_top', 0) / 1080,
            state.get('edge_bottom', 0) / 1080,
            state.get('edge_left', 0) / 1920,
            state.get('edge_right', 0) / 1920,
            # Personality (one-hot or distributed encoding)
            *state.get('personality_vector', [0] * 8)
        ])

        output = self.network.predict(input_vector)

        # Decode output
        velocity_x = (output[0][0] - 0.5) * 10  # -5 to +5
        velocity_y = (output[0][1] - 0.5) * 10
        should_move = output[0][2] > 0.5

        return float(velocity_x), float(velocity_y), bool(should_move)

    def learn(self, state: Dict[str, Any], action: Tuple[float, float, bool],
              reward: float):
        """
        Learn from movement outcome.

        Args:
            state: State when action was taken
            action: Action taken (velocity_x, velocity_y, should_move)
            reward: Reward received
        """
        # Encode input
        input_vector = np.array([
            state.get('pos_x', 0) / 1920,
            state.get('pos_y', 0) / 1080,
            state.get('target_x', 0) / 1920,
            state.get('target_y', 0) / 1080,
            state.get('energy', 100) / 100,
            min(1.0, state.get('distance_to_target', 0) / 500),
            state.get('edge_top', 0) / 1080,
            state.get('edge_bottom', 0) / 1080,
            state.get('edge_left', 0) / 1920,
            state.get('edge_right', 0) / 1920,
            *state.get('personality_vector', [0] * 8)
        ])

        # Target based on action and reward
        velocity_x, velocity_y, should_move = action
        target = np.array([[
            (velocity_x / 10 + 0.5) * reward,  # Scale by reward
            (velocity_y / 10 + 0.5) * reward,
            1.0 if (should_move and reward > 0.5) else 0.0
        ]])

        self.network.train_step(input_vector, target)


class ActivityNetwork:
    """
    Network for choosing activities based on context.

    Uses LSTM to remember recent activities and their outcomes.
    """

    def __init__(self, learning_rate: float = 0.001):
        """Initialize activity network."""
        # Input: [hunger, energy, happiness, time_of_day, recent_activities (5), emotional_state (5)]
        # Output: [ball_play, mouse_chase, hide_seek, explore, sleep, eat]
        self.network = LSTMNetwork(
            input_size=14,
            hidden_size=32,
            output_size=6,
            num_layers=2,
            learning_rate=learning_rate,
            sequence_length=20  # Remember last 20 activity decisions
        )

        self.activity_names = ['ball_play', 'mouse_chase', 'hide_seek', 'explore', 'sleep', 'eat']

    def choose_activity(self, state: Dict[str, Any]) -> str:
        """
        Choose best activity based on current state and history.

        Args:
            state: Current creature state

        Returns:
            Activity name
        """
        input_vector = self._encode_state(state)

        # Get prediction from LSTM
        output = self.network.predict(input_vector, use_sequence=True)

        # Choose activity with highest score
        activity_idx = np.argmax(output)
        return self.activity_names[activity_idx]

    def learn_from_activity(self, state: Dict[str, Any], activity: str,
                            enjoyment: float):
        """
        Learn from activity outcome.

        Args:
            state: State when activity was chosen
            activity: Activity that was performed
            enjoyment: How much the creature enjoyed it (0-1)
        """
        input_vector = self._encode_state(state)

        # Target: High score for chosen activity if enjoyed, low if not
        target = np.zeros((1, 6))
        activity_idx = self.activity_names.index(activity)
        target[0, activity_idx] = enjoyment

        # Add to sequence
        self.network.add_to_sequence(input_vector)

        # Train with short sequence
        if len(self.network.sequence_buffer) >= 3:
            sequence = list(self.network.sequence_buffer)[-3:]
            targets = [target] * len(sequence)  # Simplified
            self.network.train_sequence(sequence, targets)

    def _encode_state(self, state: Dict[str, Any]) -> np.ndarray:
        """Encode state into input vector."""
        return np.array([
            state.get('hunger', 0) / 100,
            state.get('energy', 100) / 100,
            state.get('happiness', 100) / 100,
            state.get('time_of_day', 12) / 24,  # 0-24 hours
            # Recent activities (simplified encoding)
            *state.get('recent_activities', [0, 0, 0, 0, 0]),
            # Emotional state
            *state.get('emotional_state', [0.5, 0.5, 0.5, 0.5, 0.5])
        ])


class EmotionNetwork:
    """
    Network for managing emotional responses and mood.

    Emotions affect all other behaviors and change based on interactions.
    """

    def __init__(self, learning_rate: float = 0.001):
        """Initialize emotion network."""
        # Input: [hunger, energy, happiness, recent_interactions (10), personality (8)]
        # Output: [joy, excitement, contentment, anxiety, loneliness]
        self.network = AdvancedNeuralNetwork(
            input_size=21,
            hidden_layers=[32, 16],
            output_size=5,
            learning_rate=learning_rate
        )

        self.emotion_names = ['joy', 'excitement', 'contentment', 'anxiety', 'loneliness']
        self.current_emotions = np.array([0.5, 0.5, 0.5, 0.3, 0.3])  # Initial state

    def update_emotions(self, state: Dict[str, Any]) -> Dict[str, float]:
        """
        Update emotional state based on current conditions.

        Args:
            state: Current creature state

        Returns:
            Dictionary of emotion intensities
        """
        input_vector = np.array([
            state.get('hunger', 0) / 100,
            state.get('energy', 100) / 100,
            state.get('happiness', 100) / 100,
            *state.get('recent_interaction_quality', [0.5] * 10),  # Last 10 interactions
            *state.get('personality_vector', [0] * 8)
        ])

        # Predict emotions
        emotions = self.network.predict(input_vector)
        self.current_emotions = emotions[0]

        return {
            name: float(self.current_emotions[i])
            for i, name in enumerate(self.emotion_names)
        }

    def learn_emotional_response(self, state: Dict[str, Any],
                                  expected_emotions: Dict[str, float]):
        """
        Learn what emotions to feel in given situations.

        Args:
            state: State that triggered emotions
            expected_emotions: Target emotional response
        """
        input_vector = np.array([
            state.get('hunger', 0) / 100,
            state.get('energy', 100) / 100,
            state.get('happiness', 100) / 100,
            *state.get('recent_interaction_quality', [0.5] * 10),
            *state.get('personality_vector', [0] * 8)
        ])

        target = np.array([[
            expected_emotions.get(name, 0.5)
            for name in self.emotion_names
        ]])

        self.network.train_step(input_vector, target)

    def get_emotional_modifiers(self) -> Dict[str, float]:
        """
        Get modifiers for other behaviors based on emotions.

        Returns:
            Dictionary of behavioral modifiers
        """
        joy, excitement, contentment, anxiety, loneliness = self.current_emotions

        return {
            'movement_speed': 0.5 + excitement * 0.8 - contentment * 0.3,
            'interaction_desire': joy * 0.5 + loneliness * 0.8,
            'playfulness': excitement * 0.7 + joy * 0.5,
            'fearfulness': anxiety * 0.9,
            'energy_consumption': 0.8 + excitement * 0.4 - contentment * 0.2
        }


class SocialNetwork:
    """
    Network for learning player interaction patterns.

    Learns when player is likely to interact, what they like to do, etc.
    """

    def __init__(self, learning_rate: float = 0.001):
        """Initialize social network."""
        # Input: [time_of_day, day_of_week, time_since_last_interaction,
        #         recent_interaction_types (5), player_mood_estimate]
        # Output: [interaction_probability, predicted_interaction_type (5)]
        self.network = LSTMNetwork(
            input_size=12,
            hidden_size=24,
            output_size=6,
            num_layers=1,
            learning_rate=learning_rate,
            sequence_length=50  # Remember patterns over many interactions
        )

    def predict_player_behavior(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict player interaction likelihood and type.

        Args:
            state: Current time and context

        Returns:
            Predictions about player behavior
        """
        import datetime
        now = datetime.datetime.now()

        input_vector = np.array([
            now.hour / 24.0,  # Time of day
            now.weekday() / 7.0,  # Day of week
            min(1.0, state.get('time_since_interaction', 0) / 3600),  # Hours
            *state.get('recent_interaction_types', [0, 0, 0, 0, 0]),
            state.get('player_mood_estimate', 0.5)
        ])

        output = self.network.predict(input_vector, use_sequence=True)

        return {
            'interaction_probability': float(output[0][0]),
            'likely_interaction_type': {
                'feed': float(output[0][1]),
                'play_ball': float(output[0][2]),
                'pet': float(output[0][3]),
                'talk': float(output[0][4]),
                'ignore': float(output[0][5])
            }
        }

    def learn_from_interaction(self, state: Dict[str, Any],
                                interaction_type: str, positive: bool):
        """
        Learn from player interaction.

        Args:
            state: State when interaction occurred
            interaction_type: Type of interaction
            positive: Whether it was positive
        """
        import datetime
        now = datetime.datetime.now()

        input_vector = np.array([
            now.hour / 24.0,
            now.weekday() / 7.0,
            min(1.0, state.get('time_since_interaction', 0) / 3600),
            *state.get('recent_interaction_types', [0, 0, 0, 0, 0]),
            state.get('player_mood_estimate', 0.5)
        ])

        # Build target
        interaction_types = ['feed', 'play_ball', 'pet', 'talk', 'ignore']
        target = np.zeros((1, 6))
        target[0, 0] = 1.0  # Interaction occurred

        if interaction_type in interaction_types:
            idx = interaction_types.index(interaction_type) + 1
            target[0, idx] = 1.0 if positive else 0.2

        self.network.add_to_sequence(input_vector)


class NetworkCoordinator:
    """
    Coordinates multiple specialized networks to produce unified behavior.

    Combines outputs from movement, activity, emotion, and social networks
    while allowing inter-network communication.
    """

    def __init__(self):
        """Initialize network coordinator."""
        self.movement_net = MovementNetwork()
        self.activity_net = ActivityNetwork()
        self.emotion_net = EmotionNetwork()
        self.social_net = SocialNetwork()

    def decide_behavior(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate all networks to decide creature behavior.

        Args:
            state: Complete creature state

        Returns:
            Unified behavioral decision
        """
        # Update emotions first (affects everything else)
        emotions = self.emotion_net.update_emotions(state)
        emotional_modifiers = self.emotion_net.get_emotional_modifiers()

        # Add emotional state to state dict
        state['emotional_state'] = list(self.emotion_net.current_emotions)

        # Predict player behavior
        player_prediction = self.social_net.predict_player_behavior(state)

        # Choose activity (influenced by emotions and player prediction)
        state['player_interaction_likely'] = player_prediction['interaction_probability']
        activity = self.activity_net.choose_activity(state)

        # Decide movement based on chosen activity and emotions
        movement_state = state.copy()
        movement_state.update({
            'activity': activity,
            'emotional_modifiers': emotional_modifiers
        })

        velocity_x, velocity_y, should_move = self.movement_net.predict_movement(movement_state)

        # Apply emotional modifiers
        speed_modifier = emotional_modifiers['movement_speed']
        velocity_x *= speed_modifier
        velocity_y *= speed_modifier

        return {
            'activity': activity,
            'velocity_x': velocity_x,
            'velocity_y': velocity_y,
            'should_move': should_move,
            'emotions': emotions,
            'player_prediction': player_prediction,
            'emotional_modifiers': emotional_modifiers
        }

    def learn_from_outcome(self, state: Dict[str, Any], action: Dict[str, Any],
                           outcome: Dict[str, Any]):
        """
        Learn from behavioral outcome across all networks.

        Args:
            state: State when action was taken
            action: Action that was performed
            outcome: Result of the action
        """
        reward = outcome.get('reward', 0.5)

        # Learn movement
        if 'velocity_x' in action:
            self.movement_net.learn(
                state,
                (action['velocity_x'], action['velocity_y'], action['should_move']),
                reward
            )

        # Learn activity choice
        if 'activity' in action:
            self.activity_net.learn_from_activity(
                state,
                action['activity'],
                outcome.get('enjoyment', reward)
            )

        # Learn emotions
        if 'expected_emotions' in outcome:
            self.emotion_net.learn_emotional_response(
                state,
                outcome['expected_emotions']
            )

        # Learn social patterns
        if outcome.get('player_interaction'):
            self.social_net.learn_from_interaction(
                state,
                outcome.get('interaction_type', 'unknown'),
                outcome.get('positive', True)
            )

    def to_dict(self) -> Dict[str, Any]:
        """Save all networks."""
        return {
            'movement': self.movement_net.network.to_dict(),
            'activity': self.activity_net.network.to_dict(),
            'emotion': self.emotion_net.network.to_dict(),
            'social': self.social_net.network.to_dict(),
            'current_emotions': self.emotion_net.current_emotions.tolist()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkCoordinator':
        """Load all networks."""
        coordinator = cls()

        coordinator.movement_net.network = AdvancedNeuralNetwork.from_dict(data['movement'])
        coordinator.activity_net.network = LSTMNetwork.from_dict(data['activity'])
        coordinator.emotion_net.network = AdvancedNeuralNetwork.from_dict(data['emotion'])
        coordinator.social_net.network = LSTMNetwork.from_dict(data['social'])
        coordinator.emotion_net.current_emotions = np.array(data['current_emotions'])

        return coordinator
