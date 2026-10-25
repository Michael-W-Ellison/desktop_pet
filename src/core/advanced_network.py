"""
Advanced neural network with dropout, batch normalization, and residual connections.
"""
import numpy as np
from typing import List
from .optimizers import (
    AdamOptimizer, clip_gradients, LearningRateScheduler, make_adam_optimizer, make_lr_scheduler
)
from .config import (
    LEARNING_RATE, DROPOUT_RATE, USE_DROPOUT, USE_BATCH_NORMALIZATION, USE_RESIDUAL_CONNECTIONS,
    GRADIENT_CLIP_NORM
)


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
            self.cache = (None, x_normalized, None, None)

        # Scale and shift
        out = self.gamma * x_normalized + self.beta

        return out

    def backward(self, dout, cache=None):
        """
        Backward pass through batch normalization.

        Args:
            dout: Gradient from next layer
            cache: Values saved by forward() (defaults to the most recent forward pass)

        Returns:
            Gradient for previous layer, and gradients for gamma and beta
        """
        cache = cache if cache is not None else self.cache
        if cache[0] is None:
            # Forward pass used the running statistics (inference mode or a batch of one)
            _, x_normalized, _, _ = cache
            dgamma = np.sum(dout * x_normalized, axis=0, keepdims=True)
            dbeta = np.sum(dout, axis=0, keepdims=True)
            dx = dout * self.gamma / np.sqrt(self.running_var + self.epsilon)
            return dx, dgamma, dbeta

        x, x_normalized, mean, var = cache
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
                 learning_rate: float = LEARNING_RATE,
                 dropout_rate: float = DROPOUT_RATE if USE_DROPOUT else 0.0,
                 use_batch_norm: bool = USE_BATCH_NORMALIZATION,
                 use_residual: bool = USE_RESIDUAL_CONNECTIONS,
                 gradient_clip_norm: float = GRADIENT_CLIP_NORM):
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

        # Residual shortcuts into every hidden layer after the first. Equal-sized
        # layers use the identity; otherwise a learned projection matches the sizes.
        self.shortcut_weights = {}
        if use_residual:
            for i in range(1, len(hidden_layers)):
                if self.layers[i] != self.layers[i + 1]:
                    self.shortcut_weights[i] = (np.random.randn(self.layers[i], self.layers[i + 1])
                                                * np.sqrt(1.0 / self.layers[i]))

        # Optimizers (weights/biases/shortcuts, and batch norm scale/shift)
        self.optimizer = make_adam_optimizer(learning_rate)
        self.bn_optimizer = make_adam_optimizer(learning_rate)

        # Learning rate scheduler
        self.lr_scheduler = make_lr_scheduler(learning_rate)

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

    def _shortcut(self, i, a_prev):
        """Residual input to hidden layer i from the previous layer's activations."""
        if i in self.shortcut_weights:
            return np.dot(a_prev, self.shortcut_weights[i])
        return a_prev

    def _has_shortcut(self, i):
        """Whether hidden layer i receives a residual connection."""
        return self.use_residual and 0 < i < len(self.weights) - 1

    def forward(self, X, training=True):
        """
        Forward pass through the network.

        Hidden layer i: a = dropout(relu(batch_norm(a_prev @ W + b))) + shortcut(a_prev)

        Args:
            X: Input data (numpy array)
            training: Whether in training mode (affects dropout and batch norm)

        Returns:
            List of activations for each layer, and caches for backprop
        """
        activations = [X]
        dropout_masks = []
        batch_norm_caches = []
        relu_inputs = []

        for i in range(len(self.weights)):
            z = np.dot(activations[-1], self.weights[i]) + self.biases[i]

            if i < len(self.weights) - 1:
                # Batch normalization before the activation
                if self.use_batch_norm:
                    # Batch statistics need more than one sample
                    z = self.batch_norms[i].forward(z, training=training and z.shape[0] > 1)
                    batch_norm_caches.append(self.batch_norms[i].cache)
                relu_inputs.append(z)

                a = self.relu(z)
                a, mask = self.dropout(a, self.dropout_rate, training=training)
                dropout_masks.append(mask)

                if self._has_shortcut(i):
                    a = a + self._shortcut(i, activations[-1])
            else:
                # Output layer: Sigmoid
                a = self.sigmoid(z)

            activations.append(a)

        return activations, {
            'dropout_masks': dropout_masks,
            'batch_norm_caches': batch_norm_caches,
            'relu_inputs': relu_inputs
        }

    def compute_gradients(self, X, y, activations, caches):
        """
        Backpropagate the mean squared error over the batch.

        Args:
            X: Input data
            y: Target output
            activations: Activations from forward pass
            caches: Caches from forward pass

        Returns:
            Dictionary with weight, bias, shortcut, gamma and beta gradients
        """
        m = X.shape[0]
        num_layers = len(self.weights)
        weight_grads = [None] * num_layers
        bias_grads = [None] * num_layers
        shortcut_grads = {}
        gamma_grads = [None] * len(self.batch_norms)
        beta_grads = [None] * len(self.batch_norms)

        # Output layer: loss = mean over the batch of 1/2 * ||a - y||^2 with sigmoid output
        out = activations[-1]
        dz = (out - y) * self.sigmoid_derivative(out) / m
        weight_grads[-1] = np.dot(activations[-2].T, dz)
        bias_grads[-1] = np.sum(dz, axis=0, keepdims=True)
        da = np.dot(dz, self.weights[-1].T)

        # Hidden layer j maps activations[j] to activations[j + 1]; da is the
        # gradient with respect to activations[j + 1]
        for j in reversed(range(num_layers - 1)):
            residual = 0
            if self._has_shortcut(j):
                if j in self.shortcut_weights:
                    shortcut_grads[j] = np.dot(activations[j].T, da)
                    residual = np.dot(da, self.shortcut_weights[j].T)
                else:
                    residual = da

            mask = caches['dropout_masks'][j]
            dz = (da * mask if mask is not None else da) * self.relu_derivative(caches['relu_inputs'][j])

            if self.use_batch_norm:
                dz, gamma_grads[j], beta_grads[j] = self.batch_norms[j].backward(
                    dz, caches['batch_norm_caches'][j]
                )

            weight_grads[j] = np.dot(activations[j].T, dz)
            bias_grads[j] = np.sum(dz, axis=0, keepdims=True)
            da = np.dot(dz, self.weights[j].T) + residual

        return {
            'weights': weight_grads,
            'biases': bias_grads,
            'shortcuts': shortcut_grads,
            'gammas': gamma_grads,
            'betas': beta_grads
        }

    def backward(self, X, y, activations, caches):
        """
        Backpropagate and update all parameters.

        Args:
            X: Input data
            y: Target output
            activations: Activations from forward pass
            caches: Caches from forward pass
        """
        grads = self.compute_gradients(X, y, activations, caches)
        shortcut_keys = sorted(self.shortcut_weights)

        # Clip by the global norm of every gradient
        groups = [grads['weights'], [grads['shortcuts'][k] for k in shortcut_keys], grads['biases'],
                  [g for g in grads['gammas'] if g is not None], [g for g in grads['betas'] if g is not None]]
        flat = [g for group in groups for g in group]
        if self.gradient_clip_norm > 0:
            flat = clip_gradients(flat, self.gradient_clip_norm)
        sizes = [len(group) for group in groups]
        split, start = [], 0
        for size in sizes:
            split.append(flat[start:start + size])
            start += size
        weight_grads, shortcut_grads, bias_grads, gamma_grads, beta_grads = split

        # Scheduled learning rate for both optimizers
        lr = self.lr_scheduler.get_lr()
        self.lr_scheduler.step()
        self.optimizer.learning_rate = lr
        self.bn_optimizer.learning_rate = lr

        # Weights and shortcut projections share one optimizer (arrays updated in place)
        self.optimizer.update(self.weights + [self.shortcut_weights[k] for k in shortcut_keys],
                              self.biases, weight_grads + shortcut_grads, bias_grads)

        if self.use_batch_norm and gamma_grads:
            self.bn_optimizer.update([bn.gamma for bn in self.batch_norms],
                                     [bn.beta for bn in self.batch_norms],
                                     gamma_grads, beta_grads)

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
            'shortcut_weights': {str(k): w.tolist() for k, w in self.shortcut_weights.items()},
            'optimizer': self.optimizer.to_dict(),
            'bn_optimizer': self.bn_optimizer.to_dict(),
            'lr_scheduler': self.lr_scheduler.to_dict()
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

        if 'shortcut_weights' in data:
            network.shortcut_weights = {int(k): np.array(w) for k, w in data['shortcut_weights'].items()}

        # Restore optimizers and scheduler
        network.optimizer = AdamOptimizer.from_dict(data['optimizer'])
        if data.get('bn_optimizer'):
            network.bn_optimizer = AdamOptimizer.from_dict(data['bn_optimizer'])
        network.lr_scheduler = LearningRateScheduler.from_dict(data['lr_scheduler'])

        # Restore batch norm parameters
        if 'batch_norms' in data and data['batch_norms']:
            for i, bn_data in enumerate(data['batch_norms']):
                network.batch_norms[i].gamma = np.array(bn_data['gamma'])
                network.batch_norms[i].beta = np.array(bn_data['beta'])
                network.batch_norms[i].running_mean = np.array(bn_data['running_mean'])
                network.batch_norms[i].running_var = np.array(bn_data['running_var'])

        return network
