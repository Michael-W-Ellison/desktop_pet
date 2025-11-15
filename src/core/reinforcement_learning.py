"""
Reinforcement Learning system for goal-oriented behavior.

Implements Q-learning and experience replay for creatures to learn:
- How to maximize happiness and survival
- Optimal strategies for different situations
- Long-term planning and goal-seeking
- Exploration vs exploitation balance
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from collections import deque
import random


class ExperienceReplayBuffer:
    """
    Stores and samples past experiences for learning.

    Experience replay improves learning by:
    - Breaking correlation between consecutive samples
    - Reusing rare experiences multiple times
    - Stabilizing training
    """

    def __init__(self, capacity: int = 10000):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)

    def add(self, state: np.ndarray, action: Any, reward: float,
            next_state: np.ndarray, done: bool):
        """
        Add experience to buffer.

        Args:
            state: State before action
            action: Action taken
            reward: Reward received
            next_state: State after action
            done: Whether episode ended
        """
        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> List[Tuple]:
        """
        Sample random batch of experiences.

        Args:
            batch_size: Number of experiences to sample

        Returns:
            List of (state, action, reward, next_state, done) tuples
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        return random.sample(self.buffer, batch_size)

    def __len__(self) -> int:
        """Get number of experiences in buffer."""
        return len(self.buffer)


class QNetwork:
    """
    Q-Network for estimating action values.

    Predicts expected reward for each action in a given state.
    """

    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.001):
        """
        Initialize Q-Network.

        Args:
            state_size: Dimension of state space
            action_size: Number of possible actions
            learning_rate: Learning rate
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate

        # Network architecture: state -> hidden layers -> Q-values for each action
        self.layers = [state_size, 64, 32, action_size]

        # Initialize weights
        self.weights = []
        self.biases = []

        for i in range(len(self.layers) - 1):
            weight = np.random.randn(self.layers[i], self.layers[i + 1]) * np.sqrt(2.0 / self.layers[i])
            bias = np.zeros((1, self.layers[i + 1]))
            self.weights.append(weight)
            self.biases.append(bias)

    @staticmethod
    def relu(x):
        """ReLU activation function."""
        return np.maximum(0, x)

    @staticmethod
    def relu_derivative(x):
        """Derivative of ReLU."""
        return (x > 0).astype(float)

    def forward(self, state):
        """
        Forward pass to get Q-values.

        Args:
            state: Input state

        Returns:
            Q-values for each action
        """
        if len(state.shape) == 1:
            state = state.reshape(1, -1)

        activations = [state]

        for i in range(len(self.weights)):
            z = np.dot(activations[-1], self.weights[i]) + self.biases[i]

            if i < len(self.weights) - 1:
                # Hidden layers: ReLU
                a = self.relu(z)
            else:
                # Output layer: Linear (Q-values can be any value)
                a = z

            activations.append(a)

        return activations[-1], activations

    def train(self, states: np.ndarray, targets: np.ndarray):
        """
        Train network on batch of states and target Q-values.

        Args:
            states: Batch of states
            targets: Target Q-values
        """
        # Forward pass
        predictions, activations = self.forward(states)

        # Backward pass (simplified)
        m = states.shape[0]
        delta = predictions - targets

        # Update weights (gradient descent)
        for i in reversed(range(len(self.weights))):
            # Gradient for weights and biases
            weight_grad = np.dot(activations[i].T, delta) / m
            bias_grad = np.sum(delta, axis=0, keepdims=True) / m

            # Update
            self.weights[i] -= self.learning_rate * weight_grad
            self.biases[i] -= self.learning_rate * bias_grad

            # Backpropagate error
            if i > 0:
                delta = np.dot(delta, self.weights[i].T) * self.relu_derivative(activations[i])


class ReinforcementLearningAgent:
    """
    RL agent for goal-oriented creature behavior.

    Uses Q-learning with experience replay and epsilon-greedy exploration.
    """

    def __init__(self, state_size: int = 35, action_size: int = 10,
                 learning_rate: float = 0.001, gamma: float = 0.95,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.1):
        """
        Initialize RL agent.

        Args:
            state_size: Dimension of state space
            action_size: Number of discrete actions
            learning_rate: Learning rate for Q-network
            gamma: Discount factor for future rewards
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            epsilon_min: Minimum epsilon value
        """
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma  # Discount factor (how much to value future rewards)
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Q-networks (main and target for stable learning)
        self.q_network = QNetwork(state_size, action_size, learning_rate)
        self.target_network = QNetwork(state_size, action_size, learning_rate)
        self._copy_weights()

        # Experience replay
        self.replay_buffer = ExperienceReplayBuffer(capacity=10000)

        # Action mapping (discrete actions)
        self.action_map = self._create_action_map()

        # Curiosity bonus parameters
        self.action_counts = np.zeros(action_size)
        self.curiosity_weight = 0.1

    def _create_action_map(self) -> Dict[int, Dict[str, Any]]:
        """
        Create mapping from action indices to actual actions.

        Returns:
            Dictionary mapping action index to action description
        """
        return {
            0: {'type': 'move_to_mouse', 'name': 'Chase Mouse'},
            1: {'type': 'explore', 'name': 'Explore'},
            2: {'type': 'seek_food', 'name': 'Seek Food'},
            3: {'type': 'hide', 'name': 'Hide'},
            4: {'type': 'play_ball', 'name': 'Play with Ball'},
            5: {'type': 'sleep', 'name': 'Sleep'},
            6: {'type': 'move_to_center', 'name': 'Move to Center'},
            7: {'type': 'stay_still', 'name': 'Stay Still'},
            8: {'type': 'seek_interaction', 'name': 'Seek Player Interaction'},
            9: {'type': 'random_wander', 'name': 'Wander'}
        }

    def _copy_weights(self):
        """Copy weights from Q-network to target network."""
        for i in range(len(self.q_network.weights)):
            self.target_network.weights[i] = self.q_network.weights[i].copy()
            self.target_network.biases[i] = self.q_network.biases[i].copy()

    def choose_action(self, state: np.ndarray, explore: bool = True) -> int:
        """
        Choose action using epsilon-greedy policy.

        Args:
            state: Current state
            explore: Whether to use exploration

        Returns:
            Action index
        """
        # Exploration vs exploitation
        if explore and random.random() < self.epsilon:
            # Explore: choose random action (with curiosity bias)
            # Actions that have been tried less get higher probability
            action_probs = 1.0 / (self.action_counts + 1)  # Inverse frequency
            action_probs /= action_probs.sum()  # Normalize
            return np.random.choice(self.action_size, p=action_probs)
        else:
            # Exploit: choose action with highest Q-value
            q_values, _ = self.q_network.forward(state)

            # Add small curiosity bonus to Q-values
            if explore:
                curiosity_bonus = self.curiosity_weight / (self.action_counts + 1)
                q_values = q_values + curiosity_bonus

            return int(np.argmax(q_values[0]))

    def get_action_description(self, action_idx: int) -> Dict[str, Any]:
        """Get description of action."""
        return self.action_map.get(action_idx, {'type': 'unknown', 'name': 'Unknown'})

    def store_experience(self, state: np.ndarray, action: int, reward: float,
                        next_state: np.ndarray, done: bool):
        """
        Store experience in replay buffer.

        Args:
            state: State before action
            action: Action taken
            reward: Reward received
            next_state: State after action
            done: Whether episode ended
        """
        self.replay_buffer.add(state, action, reward, next_state, done)
        self.action_counts[action] += 1

    def calculate_reward(self, state_before: Dict[str, Any],
                        state_after: Dict[str, Any],
                        action: Dict[str, Any]) -> float:
        """
        Calculate reward for an action.

        Reward function considers:
        - Happiness change (primary goal)
        - Hunger (penalty for high hunger)
        - Energy management
        - Survival (staying alive)
        - Player interaction (bonus)

        Args:
            state_before: State before action
            state_after: State after action
            action: Action taken

        Returns:
            Reward value
        """
        reward = 0.0

        # Happiness change (most important)
        happiness_before = state_before.get('happiness', 50)
        happiness_after = state_after.get('happiness', 50)
        happiness_delta = happiness_after - happiness_before
        reward += happiness_delta * 0.1  # Scale to reasonable range

        # Hunger penalty (encourage eating before starving)
        hunger_after = state_after.get('hunger', 0)
        if hunger_after > 80:
            reward -= 2.0  # Strong penalty for high hunger
        elif hunger_after > 60:
            reward -= 0.5

        # Energy management
        energy_after = state_after.get('energy', 100)
        if energy_after < 20:
            reward -= 1.0  # Penalty for low energy
        elif action.get('type') == 'sleep' and energy_after < 50:
            reward += 1.0  # Reward for sleeping when tired

        # Survival bonus
        if state_after.get('alive', True):
            reward += 0.5  # Small constant bonus for staying alive
        else:
            reward -= 50.0  # Large penalty for dying

        # Player interaction bonus
        if state_after.get('player_interacted', False):
            reward += 2.0
            if state_after.get('interaction_positive', False):
                reward += 1.0

        # Activity-specific rewards
        if action.get('type') == 'seek_food' and hunger_after < hunger_before:
            reward += 1.5  # Reward for successfully eating

        if action.get('type') == 'play_ball' and state_after.get('ball_caught', False):
            reward += 1.0

        # Curiosity bonus (reward for trying new things)
        action_count = self.action_counts[state_after.get('last_action', 0)]
        if action_count < 5:  # New or rare action
            reward += 0.3

        return reward

    def learn(self, batch_size: int = 32):
        """
        Learn from experiences in replay buffer.

        Args:
            batch_size: Number of experiences to sample
        """
        if len(self.replay_buffer) < batch_size:
            return

        # Sample batch of experiences
        experiences = self.replay_buffer.sample(batch_size)

        # Prepare batch
        states = np.array([exp[0] for exp in experiences])
        actions = np.array([exp[1] for exp in experiences])
        rewards = np.array([exp[2] for exp in experiences])
        next_states = np.array([exp[3] for exp in experiences])
        dones = np.array([exp[4] for exp in experiences])

        # Get current Q-values
        current_q_values, _ = self.q_network.forward(states)

        # Get target Q-values using target network (for stability)
        next_q_values, _ = self.target_network.forward(next_states)

        # Calculate target Q-values using Bellman equation
        # Q(s, a) = r + gamma * max(Q(s', a'))
        targets = current_q_values.copy()

        for i in range(batch_size):
            if dones[i]:
                # If episode ended, no future reward
                targets[i, actions[i]] = rewards[i]
            else:
                # Q-learning update
                targets[i, actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])

        # Train Q-network
        self.q_network.train(states, targets)

        # Decay epsilon (reduce exploration over time)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target_network(self):
        """Update target network to match Q-network (for stable learning)."""
        self._copy_weights()

    def to_dict(self) -> Dict[str, Any]:
        """Save agent state."""
        return {
            'epsilon': self.epsilon,
            'action_counts': self.action_counts.tolist(),
            'q_network_weights': [w.tolist() for w in self.q_network.weights],
            'q_network_biases': [b.tolist() for b in self.q_network.biases],
            'replay_buffer': list(self.replay_buffer.buffer)[:100]  # Save recent experiences only
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReinforcementLearningAgent':
        """Load agent state."""
        agent = cls()

        agent.epsilon = data['epsilon']
        agent.action_counts = np.array(data['action_counts'])

        # Restore Q-network weights
        agent.q_network.weights = [np.array(w) for w in data['q_network_weights']]
        agent.q_network.biases = [np.array(b) for w in data['q_network_biases']]

        # Copy to target network
        agent._copy_weights()

        # Restore some replay buffer experiences (if saved)
        if 'replay_buffer' in data:
            for exp in data['replay_buffer']:
                agent.replay_buffer.add(*exp)

        return agent


class GoalOrientedBehaviorSystem:
    """
    High-level goal-oriented behavior system.

    Manages creature goals and uses RL to achieve them.
    """

    def __init__(self):
        """Initialize goal-oriented system."""
        self.rl_agent = ReinforcementLearningAgent()
        self.current_goal = None
        self.goal_progress = 0.0
        self.steps_since_goal_update = 0

    def set_goal_based_on_state(self, state: Dict[str, Any]) -> str:
        """
        Set appropriate goal based on creature state.

        Args:
            state: Current creature state

        Returns:
            Goal description
        """
        hunger = state.get('hunger', 0)
        energy = state.get('energy', 100)
        happiness = state.get('happiness', 100)

        # Priority-based goal setting
        if hunger > 70:
            self.current_goal = 'seek_food'
        elif energy < 25:
            self.current_goal = 'rest'
        elif happiness < 40:
            self.current_goal = 'seek_interaction'
        elif state.get('player_nearby', False):
            self.current_goal = 'play'
        else:
            self.current_goal = 'explore'

        return self.current_goal

    def execute_goal(self, state: np.ndarray, full_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute current goal using RL agent.

        Args:
            state: Encoded state for RL
            full_state: Complete state dictionary

        Returns:
            Action to take
        """
        # Choose action using RL
        action_idx = self.rl_agent.choose_action(state)
        action = self.rl_agent.get_action_description(action_idx)

        self.steps_since_goal_update += 1

        # Update goal if needed (every 10 steps)
        if self.steps_since_goal_update > 10:
            self.set_goal_based_on_state(full_state)
            self.steps_since_goal_update = 0

        return {
            'action_idx': action_idx,
            'action': action,
            'goal': self.current_goal
        }

    def learn_from_outcome(self, state_before: np.ndarray, action_idx: int,
                          state_after: np.ndarray, outcome: Dict[str, Any]):
        """
        Learn from action outcome.

        Args:
            state_before: State before action
            action_idx: Action taken
            state_after: State after action
            outcome: Outcome information
        """
        # Calculate reward
        reward = self.rl_agent.calculate_reward(
            outcome.get('state_before_dict', {}),
            outcome.get('state_after_dict', {}),
            self.rl_agent.get_action_description(action_idx)
        )

        # Store experience
        done = not outcome.get('state_after_dict', {}).get('alive', True)
        self.rl_agent.store_experience(state_before, action_idx, reward, state_after, done)

        # Learn from experiences
        self.rl_agent.learn(batch_size=32)

        # Periodically update target network
        if len(self.rl_agent.replay_buffer) % 100 == 0:
            self.rl_agent.update_target_network()
