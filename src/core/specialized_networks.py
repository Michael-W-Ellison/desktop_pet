"""
Multiple specialized neural networks for different aspects of creature behavior.

Each network focuses on a specific aspect:
- MovementNetwork: Decides where and how to move
- ActivityNetwork: Chooses activities based on context
- EmotionNetwork: Manages emotional responses
- SocialNetwork: Learns player interaction patterns

These networks communicate and influence each other for complex, realistic behavior.
"""
import datetime
import math
import random
import time
from collections import deque
import numpy as np
from typing import Callable, Dict, Any, List, Optional, Tuple
from .advanced_network import AdvancedNeuralNetwork
from .lstm_network import LSTMNetwork
from .config import (
    PersonalityType, ENHANCED_NETWORK_LAYERS, LEARNING_RATE, SEQUENCE_LENGTH, TRAINING_BATCH_SIZE,
    SOCIAL_PREDICTION_HORIZON, SOCIAL_LEARNING_RATE, SOCIAL_REPLAY_CAPACITY,
    SOCIAL_CALIBRATION_MOMENTS, SOCIAL_CALIBRATION_MIN_MOMENTS,
    SOCIAL_ACCURACY_SIGNIFICANCE, SOCIAL_ACCURACY_MIN_IMPROVEMENT
)

# Length of the one-hot personality encoding supplied in 'personality_vector'
PERSONALITY_SIZE = len(PersonalityType)

# Experiences kept per feedforward network for mini-batch training
EXPERIENCE_BUFFER_SIZE = 500

# Activities whose movement heads for a target location (see NetworkCoordinator.get_target)
TARGET_FOR_ACTIVITY = {
    'mouse_chase': 'mouse',
    'seek_interaction': 'mouse',
    'seek_food': 'mouse',
    'hide_seek': 'hiding_spot',
    'move_to_center': 'center',
}

# Activities during which the creature should not move
STATIONARY_ACTIVITIES = {'sleep', 'stay_still'}

# Speed (pixels per frame) the movement network learns for reaching a target
TARGET_SPEED = 3.0


class ExperienceBuffer:
    """Recent (input, target) pairs, sampled in mini-batches for training."""

    def __init__(self, capacity: int = EXPERIENCE_BUFFER_SIZE):
        self.inputs = deque(maxlen=capacity)
        self.targets = deque(maxlen=capacity)

    def add(self, x: np.ndarray, y: np.ndarray):
        self.inputs.append(np.asarray(x, dtype=float).ravel())
        self.targets.append(np.asarray(y, dtype=float).ravel())

    def sample(self, batch_size: int) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Random mini-batch that always includes the newest experience, or None if too few."""
        if len(self.inputs) < batch_size:
            return None
        newest = len(self.inputs) - 1
        indices = random.sample(range(newest), batch_size - 1) + [newest]
        return (np.array([self.inputs[i] for i in indices]),
                np.array([self.targets[i] for i in indices]))


def _train_on_batch(network: AdvancedNeuralNetwork, buffer: ExperienceBuffer):
    """Train once on a mini-batch from the buffer (batch norm needs several samples)."""
    batch = buffer.sample(TRAINING_BATCH_SIZE)
    if batch is not None:
        network.train_step(*batch)


class MovementNetwork:
    """
    Specialized network for movement decisions.

    Learns optimal movement patterns based on:
    - Current position on screen
    - Target location (mouse, food, hiding spot)
    - Energy level
    - Personality traits
    """

    def __init__(self, learning_rate: float = LEARNING_RATE):
        """Initialize movement network."""
        # Input: [pos_x, pos_y, target_x, target_y, energy, distance_to_target,
        #         screen_edge_distances (4), personality_encoding (PERSONALITY_SIZE)]
        # Output: [velocity_x, velocity_y, should_move]
        self.network = AdvancedNeuralNetwork(
            input_size=10 + PERSONALITY_SIZE,
            hidden_layers=list(ENHANCED_NETWORK_LAYERS),
            output_size=3,
            learning_rate=learning_rate
        )
        self.experiences = ExperienceBuffer()

    @staticmethod
    def encode_state(state: Dict[str, Any]) -> np.ndarray:
        """Encode position, target, energy, edges and personality as the network input."""
        return np.array([
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
            # Personality (one-hot encoding)
            *state.get('personality_vector', [0] * PERSONALITY_SIZE)
        ])

    def predict_movement(self, state: Dict[str, Any]) -> Tuple[float, float, bool]:
        """
        Predict movement action.

        Args:
            state: Dictionary with position, target, energy, etc.

        Returns:
            (velocity_x, velocity_y, should_move)
        """
        output = self.network.predict(self.encode_state(state))

        # Decode output
        velocity_x = (output[0][0] - 0.5) * 10  # -5 to +5
        velocity_y = (output[0][1] - 0.5) * 10
        should_move = output[0][2] > 0.5

        return float(velocity_x), float(velocity_y), bool(should_move)

    def learn(self, state: Dict[str, Any], target_velocity: Tuple[float, float], should_move: bool):
        """
        Learn the movement that should have been made in a state.

        Args:
            state: State when the movement was chosen
            target_velocity: Velocity (x, y) that would have served the activity
            should_move: Whether the creature should have been moving
        """
        target = np.array([
            np.clip(target_velocity[0] / 10 + 0.5, 0.0, 1.0),
            np.clip(target_velocity[1] / 10 + 0.5, 0.0, 1.0),
            1.0 if should_move else 0.0
        ])
        self.experiences.add(self.encode_state(state), target)
        _train_on_batch(self.network, self.experiences)


class ActivityNetwork:
    """
    Network for choosing activities based on context.

    Uses LSTM to remember recent activities and their outcomes.
    """

    def __init__(self, learning_rate: float = LEARNING_RATE):
        """Initialize activity network."""
        # Input: [hunger, energy, happiness, time_of_day, recent_activities (5), emotional_state (5)]
        # Output: [ball_play, mouse_chase, hide_seek, explore, sleep, eat]
        self.network = LSTMNetwork(
            input_size=14,
            hidden_size=32,
            output_size=6,
            num_layers=2,
            learning_rate=learning_rate,
            sequence_length=SEQUENCE_LENGTH  # Remember recent activity decisions
        )

        self.activity_names = ['ball_play', 'mouse_chase', 'hide_seek', 'explore', 'sleep', 'eat']

    def choose_activity(self, state: Dict[str, Any],
                        modifiers: Optional[Dict[str, float]] = None,
                        choose: Optional[Callable[[Dict[str, float]], str]] = None) -> str:
        """
        Choose an activity based on current state and history.

        Args:
            state: Current creature state
            modifiers: Emotional modifiers; playfulness favors play activities
            choose: Picks an activity from the scores (e.g. shaped by personality);
                defaults to the highest score

        Returns:
            Activity name
        """
        input_vector = self._encode_state(state)

        # Get prediction from LSTM
        scores = self.network.predict(input_vector, use_sequence=True)[0].copy()

        # Playful moods favor play; low playfulness favors calmer activities
        if modifiers:
            playfulness = modifiers.get('playfulness', 0.5)
            for name in ('ball_play', 'mouse_chase', 'hide_seek'):
                scores[self.activity_names.index(name)] *= 0.5 + playfulness

        if choose is not None:
            return choose(dict(zip(self.activity_names, (float(s) for s in scores))))
        return self.activity_names[int(np.argmax(scores))]

    def learn_from_activity(self, state: Dict[str, Any], activity: str,
                            enjoyment: float):
        """
        Learn from activity outcome.

        Args:
            state: State when activity was chosen
            activity: Activity that was performed
            enjoyment: How much the creature enjoyed it (0-1)
        """
        # Interactions such as 'pet' are not activity choices
        if activity not in self.activity_names:
            return

        input_vector = self._encode_state(state)

        # Only the chosen activity's score is trained (toward how much it was
        # enjoyed); the others are left alone so no activity crowds out the rest
        target = np.zeros((1, 6))
        mask = np.zeros((1, 6))
        activity_idx = self.activity_names.index(activity)
        target[0, activity_idx] = enjoyment
        mask[0, activity_idx] = 1.0

        # Add to sequence
        self.network.add_to_sequence(input_vector)

        # Train with short sequence
        if len(self.network.sequence_buffer) >= 3:
            sequence = list(self.network.sequence_buffer)[-3:]
            targets = [target] * len(sequence)  # Simplified
            self.network.train_sequence(sequence, targets, output_mask=mask)

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

    def __init__(self, learning_rate: float = LEARNING_RATE):
        """Initialize emotion network."""
        # Input: [hunger, energy, happiness, recent_interactions (10), personality (PERSONALITY_SIZE)]
        # Output: [joy, excitement, contentment, anxiety, loneliness]
        self.network = AdvancedNeuralNetwork(
            input_size=13 + PERSONALITY_SIZE,
            hidden_layers=list(ENHANCED_NETWORK_LAYERS),
            output_size=5,
            learning_rate=learning_rate
        )
        self.experiences = ExperienceBuffer()

        self.emotion_names = ['joy', 'excitement', 'contentment', 'anxiety', 'loneliness']
        self.current_emotions = np.array([0.5, 0.5, 0.5, 0.3, 0.3])  # Initial state

    @staticmethod
    def encode_state(state: Dict[str, Any]) -> np.ndarray:
        """Encode needs, recent interaction quality and personality as the network input."""
        return np.array([
            state.get('hunger', 0) / 100,
            state.get('energy', 100) / 100,
            state.get('happiness', 100) / 100,
            *state.get('recent_interaction_quality', [0.5] * 10),  # Last 10 interactions
            *state.get('personality_vector', [0] * PERSONALITY_SIZE)
        ])

    def update_emotions(self, state: Dict[str, Any]) -> Dict[str, float]:
        """
        Update emotional state based on current conditions.

        Args:
            state: Current creature state

        Returns:
            Dictionary of emotion intensities
        """
        emotions = self.network.predict(self.encode_state(state))
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
        target = np.array([expected_emotions.get(name, 0.5) for name in self.emotion_names])
        self.experiences.add(self.encode_state(state), target)
        _train_on_batch(self.network, self.experiences)

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

    Learns when the player is likely to interact (time of day, day of week) and
    what they like to do. It predicts whether the player will interact within the
    next SOCIAL_PREDICTION_HORIZON seconds; each moment is labelled once that
    period has passed.
    """

    INTERACTION_TYPES = ['feed', 'play_ball', 'pet', 'talk', 'ignore']

    def __init__(self, learning_rate: float = SOCIAL_LEARNING_RATE):
        """Initialize social network."""
        # Input: [time_of_day (sin, cos), day_of_week (sin, cos), is_weekend,
        #         time_since_last_interaction, recent_interaction_types (5), player_mood_estimate,
        #         interacted at this time yesterday, share of last 7 days with an interaction now]
        # Output: [interaction_probability, predicted_interaction_type (5)]
        self.network = LSTMNetwork(
            input_size=14,
            hidden_size=24,
            output_size=6,
            num_layers=1,
            learning_rate=learning_rate,
            sequence_length=50  # Remember patterns over many interactions
        )

        # Moments waiting to be labelled: (timestamp, encoded input)
        self.pending = deque()
        # Recent player interactions: (timestamp, type, positive)
        self.recent_interactions = deque()

        # Labelled moments for replay, as a ring buffer (not saved)
        self.replay_inputs = np.zeros((SOCIAL_REPLAY_CAPACITY, 14), dtype=np.float32)
        self.replay_targets = np.zeros((SOCIAL_REPLAY_CAPACITY, 6), dtype=np.float32)
        self.replay_count = 0  # Moments stored so far (the buffer holds the newest)

        # Decaying sums over labelled moments of the network's forecast f (made before
        # learning from the moment) and what happened y: [count, y, f, f*f, f*y]
        self.calibration = [0.0] * 5

        # Accuracy of the forecasts as used, checked when each moment is labelled:
        # hour number -> [sum of squared errors, moments, moments the player interacted]
        # for the last 48 hours
        self.forecast_errors: Dict[int, List[float]] = {}

    @staticmethod
    def encode_state(state: Dict[str, Any], when: Optional[float] = None) -> np.ndarray:
        """
        Encode time (as cycles), time since interaction, recent interaction types and player mood.

        Args:
            state: Creature state
            when: Timestamp to encode (defaults to now; the planner forecasts future times)
        """
        now = datetime.datetime.now() if when is None else datetime.datetime.fromtimestamp(when)
        hour = now.hour + now.minute / 60.0
        weekday = now.weekday() + hour / 24.0
        return np.array([
            math.sin(2 * math.pi * hour / 24), math.cos(2 * math.pi * hour / 24),
            math.sin(2 * math.pi * weekday / 7), math.cos(2 * math.pi * weekday / 7),
            1.0 if now.weekday() >= 5 else 0.0,
            min(1.0, state.get('time_since_interaction', 0) / 3600),  # Hours
            *state.get('recent_interaction_types', [0, 0, 0, 0, 0]),
            state.get('player_mood_estimate', 0.5),
            state.get('yesterday_same_time', 0.0),
            state.get('week_same_time', 0.0)
        ])

    def predict_player_behavior(self, state: Dict[str, Any], when: Optional[float] = None) -> Dict[str, Any]:
        """
        Predict whether the player will interact soon, and how.

        Args:
            state: Current time and context
            when: Time to predict for (defaults to now)

        Returns:
            Predictions about player behavior
        """
        output = self.network.predict_single(self.encode_state(state, when))

        return {
            'interaction_probability': self.calibrated(float(output[0][0])),
            'likely_interaction_type': {
                name: float(output[0][i + 1]) for i, name in enumerate(self.INTERACTION_TYPES)
            }
        }

    def observe(self, state: Dict[str, Any], interaction_type: Optional[str], positive: bool = True,
                now: Optional[float] = None):
        """
        Record one decision period and learn from periods that are now labelled.

        Args:
            state: State at the start of the period
            interaction_type: Player interaction during the period ('feed', 'play_ball',
                'pet', 'talk', ...), or None if the player did not interact
            positive: Whether that interaction was positive
            now: Current time (defaults to time.time())
        """
        now = time.time() if now is None else now
        self.pending.append((now, self.encode_state(state)))
        if interaction_type is not None:
            self.recent_interactions.append((now, interaction_type, positive))

        # Label every moment whose prediction window has passed
        while self.pending and now - self.pending[0][0] >= SOCIAL_PREDICTION_HORIZON:
            moment, x = self.pending.popleft()
            target = np.zeros((1, 6))
            following = [i for i in self.recent_interactions
                         if moment < i[0] <= moment + SOCIAL_PREDICTION_HORIZON]
            if following:
                _, kind, was_positive = following[0]
                target[0, 0] = 1.0  # The player interacted within the window
                if kind in self.INTERACTION_TYPES:
                    target[0, self.INTERACTION_TYPES.index(kind) + 1] = 1.0 if was_positive else 0.2
            else:
                target[0, 5] = 1.0  # 'ignore'
            forecast = float(self.network.predict_single(x)[0][0])
            self._record_accuracy(moment, self.calibrated(forecast), target[0, 0])
            self._record_calibration(forecast, target[0, 0])

            # Store the moment, then train on a random stored one
            slot = self.replay_count % SOCIAL_REPLAY_CAPACITY
            self.replay_inputs[slot] = x
            self.replay_targets[slot] = target[0]
            self.replay_count += 1
            i = random.randrange(min(self.replay_count, SOCIAL_REPLAY_CAPACITY))
            self.network.train_sequence([self.replay_inputs[i]], [self.replay_targets[i:i + 1]])

        # Forget interactions too old to label any pending moment
        while self.recent_interactions and now - self.recent_interactions[0][0] > 2 * SOCIAL_PREDICTION_HORIZON:
            self.recent_interactions.popleft()


    def _record_calibration(self, forecast: float, happened: float):
        """Add one labelled moment to the record of how well forecasts matched what happened."""
        keep = 1.0 - 1.0 / SOCIAL_CALIBRATION_MOMENTS
        values = (1.0, happened, forecast, forecast * forecast, forecast * happened)
        self.calibration = [total * keep + value for total, value in zip(self.calibration, values)]

    def _record_accuracy(self, moment: float, forecast: float, happened: float):
        """Record the error of a forecast as used, for its hour; forget hours older than 48."""
        hour = int(moment // 3600)
        entry = self.forecast_errors.setdefault(hour, [0.0, 0, 0])
        entry[0] += (forecast - happened) ** 2
        entry[1] += 1
        entry[2] += happened
        for old in [h for h in self.forecast_errors if h <= hour - 48]:
            del self.forecast_errors[old]

    def accuracy_settledness(self) -> Optional[float]:
        """
        How settled the social network is, judged by the accuracy of its forecasts (0-1).

        Each hour of the last 24 is paired with the same hour the day before, and the
        drop in mean squared error, less SOCIAL_ACCURACY_MIN_IMPROVEMENT (drops too small
        to matter), is tested against its standard error. No improvement scores 1; an
        improvement SOCIAL_ACCURACY_SIGNIFICANCE standard errors or more scores 0. A player
        who cannot be predicted scores near 1 once the forecasts are as good as they get
        (blending keeps them at about the player's average rate).

        Returns:
            The score, or None with fewer than 12 hours that have forecasts on both days
        """
        if not self.forecast_errors:
            return None
        latest = max(self.forecast_errors)
        pairs = [(self.forecast_errors[h - 24], self.forecast_errors[h])
                 for h in range(latest - 23, latest + 1)
                 if h in self.forecast_errors and h - 24 in self.forecast_errors]
        if len(pairs) < 12:
            return None

        drops = np.array([before[0] / before[1] - after[0] / after[1] for before, after in pairs])
        improvement = drops.mean() - SOCIAL_ACCURACY_MIN_IMPROVEMENT
        spread = drops.std(ddof=1)
        if spread == 0:
            return 1.0 if improvement <= 0 else 0.0
        t = improvement / (spread / math.sqrt(len(drops)))
        return float(1.0 - min(1.0, max(0.0, t / SOCIAL_ACCURACY_SIGNIFICANCE)))

    def calibrated(self, forecast: float) -> float:
        """
        Blend a network forecast toward the player's average visit rate.

        Returns rate + s * (forecast - mean forecast), where s (0-1) is the weight that
        best fitted past labelled moments: near 1 when the network's forecasts carry
        information about this player, near 0 when they only fit noise (a player who
        visits at random). Raw forecast until enough moments are recorded.
        """
        count, happened, total, squares, products = self.calibration
        if count < SOCIAL_CALIBRATION_MIN_MOMENTS:
            return forecast
        rate, mean = happened / count, total / count
        variance = squares / count - mean * mean
        covariance = products / count - mean * rate
        weight = 0.0 if variance <= 1e-9 else min(1.0, max(0.0, covariance / variance))
        return float(min(1.0, max(0.0, rate + weight * (forecast - mean))))


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

    @staticmethod
    def get_target(state: Dict[str, Any], activity: str) -> Optional[Tuple[float, float]]:
        """Target location for an activity, or None if it has no destination."""
        name = TARGET_FOR_ACTIVITY.get(activity)
        target = state.get('targets', {}).get(name) if name else None
        return tuple(target) if target else None

    def movement_state(self, state: Dict[str, Any], activity: str) -> Dict[str, Any]:
        """State for the movement network, including the activity's target."""
        movement_state = state.copy()
        target = self.get_target(state, activity)
        x, y = state.get('pos_x', 0), state.get('pos_y', 0)
        tx, ty = target if target else (x, y)
        movement_state.update({
            'activity': activity,
            'target_x': tx,
            'target_y': ty,
            'distance_to_target': ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5
        })
        return movement_state

    def plan_movement(self, state: Dict[str, Any], activity: str,
                      emotional_modifiers: Dict[str, float]) -> Dict[str, Any]:
        """
        Decide how to move for an activity (influenced by emotions).

        Returns:
            Dictionary with velocity_x, velocity_y and should_move
        """
        velocity_x, velocity_y, should_move = self.movement_net.predict_movement(
            self.movement_state(state, activity)
        )

        # Apply emotional modifiers
        speed_modifier = emotional_modifiers['movement_speed']
        return {
            'velocity_x': velocity_x * speed_modifier,
            'velocity_y': velocity_y * speed_modifier,
            'should_move': should_move
        }

    def decide_behavior(self, state: Dict[str, Any],
                        choose: Optional[Callable[[Dict[str, float]], str]] = None) -> Dict[str, Any]:
        """
        Coordinate all networks to decide creature behavior.

        Args:
            state: Complete creature state
            choose: Picks an activity from the activity network's scores

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
        network_activity = self.activity_net.choose_activity(state, emotional_modifiers, choose)
        # The pet cannot feed itself, so wanting to eat means seeking food from the player
        activity = 'seek_food' if network_activity == 'eat' else network_activity

        decision = {
            'activity': activity,
            'network_activity': network_activity,
            'emotions': emotions,
            'player_prediction': player_prediction,
            'emotional_modifiers': emotional_modifiers
        }
        decision.update(self.plan_movement(state, activity, emotional_modifiers))
        return decision

    def learn_from_outcome(self, state: Dict[str, Any], decision: Dict[str, Any],
                           outcome: Dict[str, Any]):
        """
        Learn from the outcome of a behavioral decision across all networks.

        Args:
            state: State when the decision was made
            decision: Decision that was carried out (activity, velocity, ...)
            outcome: Result of the decision:
                - reward01: Reward scaled to 0-1
                - expected_emotions: Emotions the situation called for
                - interaction_type: Player interaction during the period, or None
                - positive: Whether that interaction was positive
        """
        reward01 = outcome.get('reward01', 0.5)
        activity = decision.get('activity', 'explore')

        # Movement: head for the activity's target, stay put when resting,
        # and repeat free movement that turned out well
        target = self.get_target(state, activity)
        movement_state = self.movement_state(state, activity)
        if activity in STATIONARY_ACTIVITIES:
            self.movement_net.learn(movement_state, (0.0, 0.0), False)
        elif target is not None:
            dx, dy = target[0] - movement_state['pos_x'], target[1] - movement_state['pos_y']
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 10:
                velocity = (dx / distance * TARGET_SPEED, dy / distance * TARGET_SPEED)
                self.movement_net.learn(movement_state, velocity, True)
            else:
                self.movement_net.learn(movement_state, (0.0, 0.0), False)
        elif reward01 >= 0.5 and 'velocity_x' in decision:
            self.movement_net.learn(movement_state, (decision['velocity_x'], decision['velocity_y']),
                                    decision.get('should_move', True))

        # Activity choice, judged by how the period went
        network_activity = decision.get('network_activity', activity)
        self.activity_net.learn_from_activity(state, network_activity, reward01)

        # Emotions the situation called for
        if 'expected_emotions' in outcome:
            self.emotion_net.learn_emotional_response(state, outcome['expected_emotions'])

        # Whether (and how) the player interacted during the period
        self.social_net.observe(state, outcome.get('interaction_type'), outcome.get('positive', True))

    def to_dict(self) -> Dict[str, Any]:
        """Save all networks."""
        return {
            'movement': self.movement_net.network.to_dict(),
            'activity': self.activity_net.network.to_dict(),
            'emotion': self.emotion_net.network.to_dict(),
            'social': self.social_net.network.to_dict(),
            'social_calibration': self.social_net.calibration,
            'social_forecast_errors': {str(h): v for h, v in self.social_net.forecast_errors.items()},
            'current_emotions': self.emotion_net.current_emotions.tolist()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkCoordinator':
        """Load all networks."""
        coordinator = cls()

        # Saves from older versions may hold networks with a different architecture;
        # keep the freshly built network in that case
        def architecture(network):
            if isinstance(network, LSTMNetwork):
                return ('lstm', network.input_size, network.hidden_size,
                        network.output_size, network.num_layers)
            return ('advanced', tuple(network.layers), bool(network.shortcut_weights))

        loaded = {
            'movement': (coordinator.movement_net, AdvancedNeuralNetwork.from_dict(data['movement'])),
            'activity': (coordinator.activity_net, LSTMNetwork.from_dict(data['activity'])),
            'emotion': (coordinator.emotion_net, AdvancedNeuralNetwork.from_dict(data['emotion'])),
            'social': (coordinator.social_net, LSTMNetwork.from_dict(data['social'])),
        }
        for net, saved_network in loaded.values():
            if architecture(saved_network) == architecture(net.network):
                if isinstance(saved_network, LSTMNetwork):
                    saved_network.set_sequence_length(net.network.sequence_length)
                net.network = saved_network

        coordinator.emotion_net.current_emotions = np.array(data['current_emotions'])
        coordinator.social_net.calibration = list(data.get('social_calibration', [0.0] * 5))
        coordinator.social_net.forecast_errors = {
            int(h): list(v) for h, v in data.get('social_forecast_errors', {}).items()}

        return coordinator
