"""
Advanced optimizers for neural network training.
"""
import numpy as np
from typing import List, Optional


class Optimizer:
    """Base optimizer class."""

    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate

    def update(self, weights: List[np.ndarray], biases: List[np.ndarray],
               weight_gradients: List[np.ndarray], bias_gradients: List[np.ndarray]):
        """Update weights and biases using gradients."""
        raise NotImplementedError


class SGDOptimizer(Optimizer):
    """Stochastic Gradient Descent optimizer."""

    def update(self, weights: List[np.ndarray], biases: List[np.ndarray],
               weight_gradients: List[np.ndarray], bias_gradients: List[np.ndarray]):
        """Update using standard gradient descent."""
        for i in range(len(weights)):
            weights[i] -= self.learning_rate * weight_gradients[i]
            biases[i] -= self.learning_rate * bias_gradients[i]


class AdamOptimizer(Optimizer):
    """
    Adam (Adaptive Moment Estimation) optimizer.

    Combines the advantages of AdaGrad and RMSprop:
    - Adaptive learning rates for each parameter
    - Momentum for smoother convergence
    - Bias correction for early training steps
    """

    def __init__(self, learning_rate: float = 0.001, beta1: float = 0.9,
                 beta2: float = 0.999, epsilon: float = 1e-8):
        """
        Initialize Adam optimizer.

        Args:
            learning_rate: Initial learning rate
            beta1: Exponential decay rate for first moment estimates (momentum)
            beta2: Exponential decay rate for second moment estimates (RMSprop)
            epsilon: Small constant for numerical stability
        """
        super().__init__(learning_rate)
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon

        # Moment estimates (initialized on first update)
        self.m_weights = None  # First moment (momentum)
        self.v_weights = None  # Second moment (adaptive learning rate)
        self.m_biases = None
        self.v_biases = None

        self.t = 0  # Time step

    def _initialize_moments(self, weights: List[np.ndarray], biases: List[np.ndarray]):
        """Initialize moment vectors with zeros."""
        self.m_weights = [np.zeros_like(w) for w in weights]
        self.v_weights = [np.zeros_like(w) for w in weights]
        self.m_biases = [np.zeros_like(b) for b in biases]
        self.v_biases = [np.zeros_like(b) for b in biases]

    def update(self, weights: List[np.ndarray], biases: List[np.ndarray],
               weight_gradients: List[np.ndarray], bias_gradients: List[np.ndarray]):
        """
        Update weights and biases using Adam algorithm.

        Adam algorithm:
        1. Update biased first moment estimate (momentum)
        2. Update biased second moment estimate (adaptive learning rate)
        3. Compute bias-corrected moment estimates
        4. Update parameters
        """
        # Initialize moments on first call
        if self.m_weights is None:
            self._initialize_moments(weights, biases)

        self.t += 1

        # Update weights
        for i in range(len(weights)):
            # Update biased first moment estimate (momentum)
            self.m_weights[i] = self.beta1 * self.m_weights[i] + (1 - self.beta1) * weight_gradients[i]

            # Update biased second raw moment estimate (RMSprop)
            self.v_weights[i] = self.beta2 * self.v_weights[i] + (1 - self.beta2) * (weight_gradients[i] ** 2)

            # Compute bias-corrected first moment estimate
            m_hat = self.m_weights[i] / (1 - self.beta1 ** self.t)

            # Compute bias-corrected second raw moment estimate
            v_hat = self.v_weights[i] / (1 - self.beta2 ** self.t)

            # Update weights
            weights[i] -= self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)

        # Update biases
        for i in range(len(biases)):
            # Update biased first moment estimate
            self.m_biases[i] = self.beta1 * self.m_biases[i] + (1 - self.beta1) * bias_gradients[i]

            # Update biased second raw moment estimate
            self.v_biases[i] = self.beta2 * self.v_biases[i] + (1 - self.beta2) * (bias_gradients[i] ** 2)

            # Compute bias-corrected estimates
            m_hat = self.m_biases[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v_biases[i] / (1 - self.beta2 ** self.t)

            # Update biases
            biases[i] -= self.learning_rate * m_hat / (np.sqrt(v_hat) + self.epsilon)

    def to_dict(self):
        """Convert optimizer state to dictionary for saving."""
        return {
            'type': 'adam',
            'learning_rate': self.learning_rate,
            'beta1': self.beta1,
            'beta2': self.beta2,
            'epsilon': self.epsilon,
            't': self.t,
            'm_weights': [m.tolist() for m in self.m_weights] if self.m_weights else None,
            'v_weights': [v.tolist() for v in self.v_weights] if self.v_weights else None,
            'm_biases': [m.tolist() for m in self.m_biases] if self.m_biases else None,
            'v_biases': [v.tolist() for v in self.v_biases] if self.v_biases else None,
        }

    @classmethod
    def from_dict(cls, data):
        """Create optimizer from dictionary."""
        optimizer = cls(
            learning_rate=data['learning_rate'],
            beta1=data['beta1'],
            beta2=data['beta2'],
            epsilon=data['epsilon']
        )
        optimizer.t = data['t']

        if data['m_weights']:
            optimizer.m_weights = [np.array(m) for m in data['m_weights']]
            optimizer.v_weights = [np.array(v) for v in data['v_weights']]
            optimizer.m_biases = [np.array(m) for m in data['m_biases']]
            optimizer.v_biases = [np.array(v) for v in data['v_biases']]

        return optimizer


class RMSpropOptimizer(Optimizer):
    """
    RMSprop (Root Mean Square Propagation) optimizer.

    Uses adaptive learning rates based on running average of squared gradients.
    """

    def __init__(self, learning_rate: float = 0.001, decay_rate: float = 0.9,
                 epsilon: float = 1e-8):
        """
        Initialize RMSprop optimizer.

        Args:
            learning_rate: Initial learning rate
            decay_rate: Decay rate for moving average
            epsilon: Small constant for numerical stability
        """
        super().__init__(learning_rate)
        self.decay_rate = decay_rate
        self.epsilon = epsilon

        # Moving average of squared gradients
        self.cache_weights = None
        self.cache_biases = None

    def _initialize_cache(self, weights: List[np.ndarray], biases: List[np.ndarray]):
        """Initialize cache with zeros."""
        self.cache_weights = [np.zeros_like(w) for w in weights]
        self.cache_biases = [np.zeros_like(b) for b in biases]

    def update(self, weights: List[np.ndarray], biases: List[np.ndarray],
               weight_gradients: List[np.ndarray], bias_gradients: List[np.ndarray]):
        """Update weights and biases using RMSprop."""
        if self.cache_weights is None:
            self._initialize_cache(weights, biases)

        # Update weights
        for i in range(len(weights)):
            # Update cache (moving average of squared gradients)
            self.cache_weights[i] = (self.decay_rate * self.cache_weights[i] +
                                     (1 - self.decay_rate) * (weight_gradients[i] ** 2))

            # Update weights with adaptive learning rate
            weights[i] -= self.learning_rate * weight_gradients[i] / (np.sqrt(self.cache_weights[i]) + self.epsilon)

        # Update biases
        for i in range(len(biases)):
            self.cache_biases[i] = (self.decay_rate * self.cache_biases[i] +
                                    (1 - self.decay_rate) * (bias_gradients[i] ** 2))
            biases[i] -= self.learning_rate * bias_gradients[i] / (np.sqrt(self.cache_biases[i]) + self.epsilon)


def clip_gradients(gradients: List[np.ndarray], max_norm: float = 5.0) -> List[np.ndarray]:
    """
    Clip gradients by global norm to prevent exploding gradients.

    Args:
        gradients: List of gradient arrays
        max_norm: Maximum allowed gradient norm

    Returns:
        Clipped gradients
    """
    # Calculate global norm
    total_norm = 0.0
    for grad in gradients:
        total_norm += np.sum(grad ** 2)
    total_norm = np.sqrt(total_norm)

    # Clip if necessary
    if total_norm > max_norm:
        clip_coef = max_norm / (total_norm + 1e-6)
        gradients = [grad * clip_coef for grad in gradients]

    return gradients


class LearningRateScheduler:
    """
    Learning rate scheduler for adaptive learning rate decay.
    """

    def __init__(self, initial_lr: float, schedule_type: str = 'step',
                 decay_rate: float = 0.1, decay_steps: int = 1000):
        """
        Initialize learning rate scheduler.

        Args:
            initial_lr: Initial learning rate
            schedule_type: Type of schedule ('step', 'exponential', 'cosine')
            decay_rate: Rate of decay
            decay_steps: Steps between decay (for step schedule)
        """
        self.initial_lr = initial_lr
        self.schedule_type = schedule_type
        self.decay_rate = decay_rate
        self.decay_steps = decay_steps
        self.current_step = 0

    def get_lr(self) -> float:
        """Get current learning rate based on schedule."""
        if self.schedule_type == 'step':
            # Step decay: lr = initial_lr * decay_rate^(step // decay_steps)
            return self.initial_lr * (self.decay_rate ** (self.current_step // self.decay_steps))

        elif self.schedule_type == 'exponential':
            # Exponential decay: lr = initial_lr * exp(-decay_rate * step)
            return self.initial_lr * np.exp(-self.decay_rate * self.current_step)

        elif self.schedule_type == 'cosine':
            # Cosine annealing
            return self.initial_lr * 0.5 * (1 + np.cos(np.pi * self.current_step / self.decay_steps))

        else:
            return self.initial_lr

    def step(self):
        """Increment step counter."""
        self.current_step += 1
