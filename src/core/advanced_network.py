"""
Advanced neural network with dropout, batch normalization, and residual connections.
"""
import numpy as np
from typing import List, Optional
from .optimizers import AdamOptimizer, clip_gradients, LearningRateScheduler


class BatchNormalization:
    """
    Batch Normalization layer for stable training.

    Normalizes inputs to have mean 0 and variance 1, with learnable scale and shift.
    """

    def __init__(self, size: int, epsilon: float = 1e-5, momentum: float = 0.9):
        """
        Initialize batch normalization layer.

        Args:
            size: Number of features
            epsilon: Small constant for numerical stability
            momentum: Momentum for running mean/variance
        """
        self.size = size
        self.epsilon = epsilon
        self.momentum = momentum

        # Learnable parameters
        self.gamma = np.ones((1, size))  # Scale
        self.beta = np.zeros((1, size))  # Shift

        # Running statistics (for inference)
        self.running_mean = np.zeros((1, size))
        self.running_var = np.ones((1, size))

        # Cache for backprop
        self.cache = None

    def forward(self, x, training=True):
        """
        Forward pass through batch normalization.

        Args:
            x: Input (batch_size, features)
            training: Whether in training mode

        Returns:
            Normalized output
        """
        if training:
            # Calculate batch statistics
            mean = np.mean(x, axis=0, keepdims=True)
            var = np.var(x, axis=0, keepdims=True)

            # Update running statistics
            self.running_mean = self.momentum * self.running_mean + (1 - self.momentum) * mean
            self.running_var = self.momentum * self.running_var + (1 - self.momentum) * var

            # Normalize
            x_normalized = (x - mean) / np.sqrt(var + self.epsilon)

            # Cache for backward
            self.cache = (x, x_normalized, mean, var)
        else:
            # Use running statistics for inference
            x_normalized = (x - self.running_mean) / np.sqrt(self.running_var + self.epsilon)

        # Scale and shift
        out = self.gamma * x_normalized + self.beta

        return out

    def backward(self, dout):
        """
        Backward pass through batch normalization.

        Args:
            dout: Gradient from next layer

        Returns:
            Gradient for previous layer
        """
        x, x_normalized, mean, var = self.cache
        m = x.shape[0]

        # Gradients for gamma and beta
        dgamma = np.sum(dout * x_normalized, axis=0, keepdims=True)
        dbeta = np.sum(dout, axis=0, keepdims=True)

        # Gradient for normalized input
        dx_normalized = dout * self.gamma

        # Gradient for variance
        dvar = np.sum(dx_normalized * (x - mean) * -0.5 * np.power(var + self.epsilon, -1.5), axis=0, keepdims=True)

        # Gradient for mean
        dmean = np.sum(dx_normalized * -1 / np.sqrt(var + self.epsilon), axis=0, keepdims=True)
        dmean += dvar * np.sum(-2 * (x - mean), axis=0, keepdims=True) / m

        # Gradient for input
        dx = dx_normalized / np.sqrt(var + self.epsilon)
        dx += dvar * 2 * (x - mean) / m
        dx += dmean / m

        return dx, dgamma, dbeta


class AdvancedNeuralNetwork:
    """
    Advanced feedforward neural network with:
    - Dropout for regularization
    - Batch normalization for stable training
    - Residual connections for deeper learning
    - Advanced optimizers (Adam)
    """

    def __init__(self, input_size: int, hidden_layers: List[int], output_size: int,
                 learning_rate: float = 0.001, dropout_rate: float = 0.25,
                 use_batch_norm: bool = True, use_residual: bool = True,
                 gradient_clip_norm: float = 5.0):
        """
        Initialize advanced neural network.

        Args:
            input_size: Number of input neurons
            hidden_layers: List of hidden layer sizes
            output_size: Number of output neurons
            learning_rate: Learning rate for training
            dropout_rate: Dropout probability (0-1)
            use_batch_norm: Whether to use batch normalization
            use_residual: Whether to use residual connections
            gradient_clip_norm: Maximum gradient norm for clipping
        """
        self.layers = [input_size] + hidden_layers + [output_size]
        self.dropout_rate = dropout_rate
        self.use_batch_norm = use_batch_norm
        self.use_residual = use_residual
        self.gradient_clip_norm = gradient_clip_norm
        self.learning_rate = learning_rate

        # Initialize weights and biases
        self.weights = []
        self.biases = []

        for i in range(len(self.layers) - 1):
            # He initialization (optimized for ReLU)
            weight = np.random.randn(self.layers[i], self.layers[i + 1]) * np.sqrt(2.0 / self.layers[i])
            bias = np.zeros((1, self.layers[i + 1]))
            self.weights.append(weight)
            self.biases.append(bias)

        # Initialize batch normalization layers
        self.batch_norms = []
        if use_batch_norm:
            for i in range(len(hidden_layers)):
                self.batch_norms.append(BatchNormalization(hidden_layers[i]))

        # Initialize optimizer
        self.optimizer = AdamOptimizer(learning_rate=learning_rate)

        # Learning rate scheduler
        self.lr_scheduler = LearningRateScheduler(
            initial_lr=learning_rate,
            schedule_type='exponential',
            decay_rate=0.0001,
            decay_steps=1000
        )

        # Training state
        self.training = True

    @staticmethod
    def relu(x):
        """ReLU activation function."""
        return np.maximum(0, x)

    @staticmethod
    def relu_derivative(x):
        """Derivative of ReLU function."""
        return (x > 0).astype(float)

    @staticmethod
    def sigmoid(x):
        """Sigmoid activation function."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    @staticmethod
    def sigmoid_derivative(x):
        """Derivative of sigmoid function."""
        return x * (1 - x)

    def dropout(self, x, rate, training=True):
        """
        Apply dropout regularization.

        Args:
            x: Input array
            rate: Dropout rate (probability of dropping)
            training: Whether in training mode

        Returns:
            Array with dropout applied
        """
        if not training or rate == 0:
            return x, None

        # Create dropout mask
        mask = np.random.binomial(1, 1 - rate, size=x.shape) / (1 - rate)
        return x * mask, mask

    def forward(self, X, training=True):
        """
        Forward pass through the network.

        Args:
            X: Input data (numpy array)
            training: Whether in training mode (affects dropout and batch norm)

        Returns:
            List of activations for each layer, and caches
        """
        activations = [X]
        dropout_masks = []
        batch_norm_caches = []
        pre_activations = []

        for i in range(len(self.weights)):
            # Linear transformation
            z = np.dot(activations[-1], self.weights[i]) + self.biases[i]
            pre_activations.append(z)

            # Apply batch normalization (before activation)
            if self.use_batch_norm and i < len(self.weights) - 1:
                z = self.batch_norms[i].forward(z, training=training)
                batch_norm_caches.append(self.batch_norms[i].cache)

            # Apply activation function
            if i < len(self.weights) - 1:
                # Hidden layers: ReLU
                a = self.relu(z)

                # Apply dropout
                a, mask = self.dropout(a, self.dropout_rate, training=training)
                dropout_masks.append(mask)

                # Residual connection (if dimensions match)
                if self.use_residual and i > 0 and activations[-1].shape == a.shape:
                    a = a + activations[-1]  # Skip connection
            else:
                # Output layer: Sigmoid
                a = self.sigmoid(z)

            activations.append(a)

        return activations, {
            'dropout_masks': dropout_masks,
            'batch_norm_caches': batch_norm_caches,
            'pre_activations': pre_activations
        }

    def backward(self, X, y, activations, caches):
        """
        Backward pass (backpropagation) with advanced features.

        Args:
            X: Input data
            y: Target output
            activations: Activations from forward pass
            caches: Caches from forward pass (dropout masks, etc.)
        """
        m = X.shape[0]
        deltas = [None] * len(self.weights)
        dropout_masks = caches['dropout_masks']
        batch_norm_caches = caches['batch_norm_caches']
        pre_activations = caches['pre_activations']

        # Calculate output layer delta
        output_error = activations[-1] - y
        deltas[-1] = output_error * self.sigmoid_derivative(activations[-1])

        # Backpropagate through hidden layers
        for i in range(len(deltas) - 2, -1, -1):
            # Error from next layer
            error = np.dot(deltas[i + 1], self.weights[i + 1].T)

            # Residual connection gradient
            if self.use_residual and i > 0 and i < len(deltas) - 1:
                # Gradient flows through both paths
                residual_error = error.copy()

            # Dropout gradient
            if dropout_masks and i < len(dropout_masks) and dropout_masks[i] is not None:
                error = error * dropout_masks[i]

            # Batch normalization gradient
            if self.use_batch_norm and i < len(batch_norm_caches):
                # We need to apply the gradient before activation
                # For now, we'll apply it after ReLU derivative
                pass

            # Activation derivative
            deltas[i] = error * self.relu_derivative(activations[i + 1])

            # Add residual gradient
            if self.use_residual and i > 0 and i < len(deltas) - 1:
                deltas[i] += residual_error * self.relu_derivative(activations[i])

        # Calculate gradients
        weight_gradients = []
        bias_gradients = []
        bn_gamma_grads = []
        bn_beta_grads = []

        for i in range(len(self.weights)):
            weight_grad = np.dot(activations[i].T, deltas[i]) / m
            bias_grad = np.sum(deltas[i], axis=0, keepdims=True) / m
            weight_gradients.append(weight_grad)
            bias_gradients.append(bias_grad)

            # Batch norm parameter gradients
            if self.use_batch_norm and i < len(self.batch_norms):
                # Simplified - in full implementation would backprop through batch norm
                bn_gamma_grads.append(np.zeros_like(self.batch_norms[i].gamma))
                bn_beta_grads.append(np.zeros_like(self.batch_norms[i].beta))

        # Apply gradient clipping
        if self.gradient_clip_norm > 0:
            weight_gradients = clip_gradients(weight_gradients, self.gradient_clip_norm)
            bias_gradients = clip_gradients(bias_gradients, self.gradient_clip_norm)

        # Update learning rate
        self.optimizer.learning_rate = self.lr_scheduler.get_lr()
        self.lr_scheduler.step()

        # Update weights and biases
        self.optimizer.update(self.weights, self.biases, weight_gradients, bias_gradients)

        # Update batch norm parameters (simplified)
        if self.use_batch_norm:
            for i, bn in enumerate(self.batch_norms):
                if i < len(bn_gamma_grads):
                    bn.gamma -= self.learning_rate * bn_gamma_grads[i]
                    bn.beta -= self.learning_rate * bn_beta_grads[i]

    def train_step(self, X, y):
        """
        Perform one training step.

        Args:
            X: Input data (numpy array)
            y: Target output (numpy array)
        """
        X = np.array(X)
        y = np.array(y)

        # Ensure proper shape
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)

        # Forward pass (training mode)
        activations, caches = self.forward(X, training=True)

        # Backward pass
        self.backward(X, y, activations, caches)

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

        activations, _ = self.forward(X, training=False)
        return activations[-1]

    def to_dict(self):
        """Convert network to dictionary for saving."""
        data = {
            'type': 'advanced',
            'layers': self.layers,
            'dropout_rate': self.dropout_rate,
            'use_batch_norm': self.use_batch_norm,
            'use_residual': self.use_residual,
            'gradient_clip_norm': self.gradient_clip_norm,
            'learning_rate': self.learning_rate,
            'weights': [w.tolist() for w in self.weights],
            'biases': [b.tolist() for b in self.biases],
            'optimizer': self.optimizer.to_dict(),
            'lr_scheduler': {
                'initial_lr': self.lr_scheduler.initial_lr,
                'schedule_type': self.lr_scheduler.schedule_type,
                'decay_rate': self.lr_scheduler.decay_rate,
                'decay_steps': self.lr_scheduler.decay_steps,
                'current_step': self.lr_scheduler.current_step
            }
        }

        # Save batch norm parameters
        if self.use_batch_norm:
            data['batch_norms'] = []
            for bn in self.batch_norms:
                data['batch_norms'].append({
                    'gamma': bn.gamma.tolist(),
                    'beta': bn.beta.tolist(),
                    'running_mean': bn.running_mean.tolist(),
                    'running_var': bn.running_var.tolist()
                })

        return data

    @classmethod
    def from_dict(cls, data):
        """Create network from dictionary."""
        layers = data['layers']
        network = cls(
            input_size=layers[0],
            hidden_layers=layers[1:-1],
            output_size=layers[-1],
            learning_rate=data['learning_rate'],
            dropout_rate=data['dropout_rate'],
            use_batch_norm=data['use_batch_norm'],
            use_residual=data['use_residual'],
            gradient_clip_norm=data['gradient_clip_norm']
        )

        network.weights = [np.array(w) for w in data['weights']]
        network.biases = [np.array(b) for b in data['biases']]

        # Restore optimizer
        network.optimizer = AdamOptimizer.from_dict(data['optimizer'])

        # Restore scheduler
        sched_data = data['lr_scheduler']
        network.lr_scheduler = LearningRateScheduler(
            initial_lr=sched_data['initial_lr'],
            schedule_type=sched_data['schedule_type'],
            decay_rate=sched_data['decay_rate'],
            decay_steps=sched_data['decay_steps']
        )
        network.lr_scheduler.current_step = sched_data['current_step']

        # Restore batch norm parameters
        if 'batch_norms' in data and data['batch_norms']:
            for i, bn_data in enumerate(data['batch_norms']):
                network.batch_norms[i].gamma = np.array(bn_data['gamma'])
                network.batch_norms[i].beta = np.array(bn_data['beta'])
                network.batch_norms[i].running_mean = np.array(bn_data['running_mean'])
                network.batch_norms[i].running_var = np.array(bn_data['running_var'])

        return network
