"""
Advanced neural network for creature learning and behavior adaptation.
"""
import numpy as np
from typing import List, Optional
import json
import time
from .optimizers import AdamOptimizer, clip_gradients, LearningRateScheduler


class NeuralNetwork:
    """
    Simple feedforward neural network for learning creature behaviors.

    This network learns from player interactions and adjusts the creature's
    behavior preferences over time.
    """

    def __init__(self, input_size: int, hidden_layers: List[int], output_size: int,
                 learning_rate: float = 0.001, use_adam: bool = True,
                 gradient_clip_norm: float = 5.0, use_lr_schedule: bool = False):
        """
        Initialize the neural network.

        Args:
            input_size: Number of input neurons
            hidden_layers: List of hidden layer sizes
            output_size: Number of output neurons
            learning_rate: Learning rate for training
            use_adam: Whether to use Adam optimizer (True) or SGD (False)
            gradient_clip_norm: Maximum gradient norm for clipping
            use_lr_schedule: Whether to use learning rate scheduling
        """
        self.learning_rate = learning_rate
        self.layers = [input_size] + hidden_layers + [output_size]
        self.gradient_clip_norm = gradient_clip_norm

        # Initialize weights and biases
        self.weights = []
        self.biases = []

        for i in range(len(self.layers) - 1):
            # Xavier/He initialization (better for ReLU)
            weight = np.random.randn(self.layers[i], self.layers[i + 1]) * np.sqrt(2.0 / self.layers[i])
            bias = np.zeros((1, self.layers[i + 1]))
            self.weights.append(weight)
            self.biases.append(bias)

        # Initialize optimizer
        if use_adam:
            self.optimizer = AdamOptimizer(learning_rate=learning_rate)
        else:
            from .optimizers import SGDOptimizer
            self.optimizer = SGDOptimizer(learning_rate=learning_rate)

        # Initialize learning rate scheduler
        self.lr_scheduler = None
        if use_lr_schedule:
            self.lr_scheduler = LearningRateScheduler(
                initial_lr=learning_rate,
                schedule_type='exponential',
                decay_rate=0.0001,
                decay_steps=1000
            )

    @staticmethod
    def sigmoid(x):
        """Sigmoid activation function."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    @staticmethod
    def sigmoid_derivative(x):
        """Derivative of sigmoid function."""
        return x * (1 - x)

    @staticmethod
    def relu(x):
        """ReLU activation function."""
        return np.maximum(0, x)

    @staticmethod
    def relu_derivative(x):
        """Derivative of ReLU function."""
        return (x > 0).astype(float)

    def forward(self, X):
        """
        Forward pass through the network.

        Args:
            X: Input data (numpy array)

        Returns:
            List of activations for each layer
        """
        activations = [X]

        for i in range(len(self.weights)):
            # Linear transformation
            z = np.dot(activations[-1], self.weights[i]) + self.biases[i]

            # Apply activation function
            if i < len(self.weights) - 1:
                # Use ReLU for hidden layers
                a = self.relu(z)
            else:
                # Use sigmoid for output layer
                a = self.sigmoid(z)

            activations.append(a)

        return activations

    def backward(self, X, y, activations):
        """
        Backward pass (backpropagation) with gradient clipping and optimizer update.

        Args:
            X: Input data
            y: Target output
            activations: Activations from forward pass
        """
        m = X.shape[0]
        deltas = [None] * len(self.weights)

        # Calculate output layer delta
        output_error = activations[-1] - y
        deltas[-1] = output_error * self.sigmoid_derivative(activations[-1])

        # Backpropagate the error
        for i in range(len(deltas) - 2, -1, -1):
            error = np.dot(deltas[i + 1], self.weights[i + 1].T)
            deltas[i] = error * self.relu_derivative(activations[i + 1])

        # Calculate gradients
        weight_gradients = []
        bias_gradients = []

        for i in range(len(self.weights)):
            weight_grad = np.dot(activations[i].T, deltas[i]) / m
            bias_grad = np.sum(deltas[i], axis=0, keepdims=True) / m
            weight_gradients.append(weight_grad)
            bias_gradients.append(bias_grad)

        # Apply gradient clipping
        if self.gradient_clip_norm > 0:
            weight_gradients = clip_gradients(weight_gradients, self.gradient_clip_norm)
            bias_gradients = clip_gradients(bias_gradients, self.gradient_clip_norm)

        # Update learning rate if using scheduler
        if self.lr_scheduler:
            self.optimizer.learning_rate = self.lr_scheduler.get_lr()
            self.lr_scheduler.step()

        # Update weights and biases using optimizer
        self.optimizer.update(self.weights, self.biases, weight_gradients, bias_gradients)

    def train(self, X, y, epochs: int = 1):
        """
        Train the network on input-output pairs.

        Args:
            X: Input data (numpy array)
            y: Target output (numpy array)
            epochs: Number of training epochs
        """
        X = np.array(X)
        y = np.array(y)

        # Ensure proper shape
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)

        for _ in range(epochs):
            activations = self.forward(X)
            self.backward(X, y, activations)

    def predict(self, X):
        """
        Make a prediction.

        Args:
            X: Input data

        Returns:
            Network output (numpy array)
        """
        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(1, -1)

        activations = self.forward(X)
        return activations[-1]

    def to_dict(self):
        """Convert network to dictionary for saving."""
        data = {
            'learning_rate': self.learning_rate,
            'layers': self.layers,
            'weights': [w.tolist() for w in self.weights],
            'biases': [b.tolist() for b in self.biases],
            'gradient_clip_norm': self.gradient_clip_norm
        }

        # Save optimizer state if it's Adam
        if isinstance(self.optimizer, AdamOptimizer):
            data['optimizer'] = self.optimizer.to_dict()
        else:
            data['optimizer'] = {'type': 'sgd', 'learning_rate': self.learning_rate}

        # Save scheduler state if exists
        if self.lr_scheduler:
            data['lr_scheduler'] = {
                'initial_lr': self.lr_scheduler.initial_lr,
                'schedule_type': self.lr_scheduler.schedule_type,
                'decay_rate': self.lr_scheduler.decay_rate,
                'decay_steps': self.lr_scheduler.decay_steps,
                'current_step': self.lr_scheduler.current_step
            }

        return data

    @classmethod
    def from_dict(cls, data):
        """Create network from dictionary."""
        layers = data['layers']

        # Determine if using Adam based on saved optimizer
        use_adam = data.get('optimizer', {}).get('type') == 'adam'
        use_lr_schedule = 'lr_scheduler' in data

        network = cls(
            input_size=layers[0],
            hidden_layers=layers[1:-1],
            output_size=layers[-1],
            learning_rate=data['learning_rate'],
            use_adam=use_adam,
            gradient_clip_norm=data.get('gradient_clip_norm', 5.0),
            use_lr_schedule=use_lr_schedule
        )

        network.weights = [np.array(w) for w in data['weights']]
        network.biases = [np.array(b) for b in data['biases']]

        # Restore optimizer state
        if 'optimizer' in data and data['optimizer'].get('type') == 'adam':
            network.optimizer = AdamOptimizer.from_dict(data['optimizer'])

        # Restore scheduler state
        if 'lr_scheduler' in data:
            sched_data = data['lr_scheduler']
            network.lr_scheduler = LearningRateScheduler(
                initial_lr=sched_data['initial_lr'],
                schedule_type=sched_data['schedule_type'],
                decay_rate=sched_data['decay_rate'],
                decay_steps=sched_data['decay_steps']
            )
            network.lr_scheduler.current_step = sched_data['current_step']

        return network


class BehaviorLearner:
    """
    Manages learning and behavior adaptation for creatures using neural networks.
    """

    def __init__(self, creature):
        """
        Initialize the behavior learner.

        Args:
            creature: The Creature instance to learn for
        """
        self.creature = creature

        # Neural network for predicting enjoyment of activities
        # Input: [hunger, energy, happiness, time_since_last_interaction, activity_type (one-hot)]
        # Output: [predicted_enjoyment]
        self.network = NeuralNetwork(
            input_size=9,  # 4 stats + 5 activity types (one-hot)
            hidden_layers=[8, 6],
            output_size=1,
            learning_rate=0.01
        )

    def encode_activity(self, activity_type: str) -> List[float]:
        """Encode activity type as one-hot vector."""
        activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'icon_interaction', 'idle']
        encoding = [0.0] * len(activities)
        if activity_type in activities:
            encoding[activities.index(activity_type)] = 1.0
        return encoding

    def get_state_vector(self, activity_type: str) -> np.ndarray:
        """Get current state as input vector for neural network."""
        state = [
            self.creature.hunger / 100.0,
            self.creature.energy / 100.0,
            self.creature.happiness / 100.0,
            min(1.0, (time.time() - self.creature.last_interaction_time) / 3600.0)  # Normalized to hours
        ]
        state.extend(self.encode_activity(activity_type))
        return np.array(state)

    def predict_enjoyment(self, activity_type: str) -> float:
        """
        Predict how much the creature will enjoy an activity.

        Args:
            activity_type: Type of activity to predict enjoyment for

        Returns:
            Predicted enjoyment score (0-1)
        """
        state = self.get_state_vector(activity_type)
        prediction = self.network.predict(state)
        return float(prediction[0][0])

    def learn_from_interaction(self, activity_type: str, enjoyed: bool):
        """
        Learn from an interaction.

        Args:
            activity_type: Type of activity performed
            enjoyed: Whether the creature enjoyed it (positive feedback)
        """
        state = self.get_state_vector(activity_type)
        target = np.array([[1.0 if enjoyed else 0.0]])

        # Train the network
        self.network.train(state, target, epochs=1)

    def get_best_activity(self) -> str:
        """Get the activity with highest predicted enjoyment."""
        activities = ['ball_play', 'mouse_chase', 'hide_and_seek', 'icon_interaction']
        predictions = [(activity, self.predict_enjoyment(activity)) for activity in activities]
        return max(predictions, key=lambda x: x[1])[0]

    def to_dict(self):
        """Convert learner to dictionary for saving."""
        return {
            'network': self.network.to_dict()
        }

    @classmethod
    def from_dict(cls, creature, data):
        """Create learner from dictionary."""
        learner = cls(creature)
        learner.network = NeuralNetwork.from_dict(data['network'])
        return learner
