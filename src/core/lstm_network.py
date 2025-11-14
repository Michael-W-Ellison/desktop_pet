"""
LSTM (Long Short-Term Memory) network for temporal pattern learning and memory.
"""
import numpy as np
from typing import List, Tuple, Optional
from collections import deque
from .optimizers import AdamOptimizer, clip_gradients


class LSTMCell:
    """
    Single LSTM cell with forget, input, and output gates.

    LSTM can remember information over long sequences and learn
    what to remember and what to forget.
    """

    def __init__(self, input_size: int, hidden_size: int):
        """
        Initialize LSTM cell.

        Args:
            input_size: Size of input vector
            hidden_size: Size of hidden state
        """
        self.input_size = input_size
        self.hidden_size = hidden_size

        # Initialize weights for gates (input, forget, cell, output)
        # Concatenate input and hidden, so weight matrix is (input_size + hidden_size, hidden_size)

        # Forget gate weights
        self.Wf = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.bf = np.zeros((1, hidden_size))

        # Input gate weights
        self.Wi = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.bi = np.zeros((1, hidden_size))

        # Cell gate weights (candidate values)
        self.Wc = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.bc = np.zeros((1, hidden_size))

        # Output gate weights
        self.Wo = np.random.randn(input_size + hidden_size, hidden_size) * 0.01
        self.bo = np.zeros((1, hidden_size))

    @staticmethod
    def sigmoid(x):
        """Sigmoid activation function."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    @staticmethod
    def tanh(x):
        """Tanh activation function."""
        return np.tanh(np.clip(x, -500, 500))

    def forward(self, x, h_prev, c_prev):
        """
        Forward pass through LSTM cell.

        Args:
            x: Input at current timestep (batch_size, input_size)
            h_prev: Previous hidden state (batch_size, hidden_size)
            c_prev: Previous cell state (batch_size, hidden_size)

        Returns:
            h_next: Next hidden state
            c_next: Next cell state
            cache: Values needed for backprop
        """
        # Concatenate input and previous hidden state
        concat = np.concatenate([x, h_prev], axis=1)

        # Forget gate: decides what to forget from cell state
        f = self.sigmoid(np.dot(concat, self.Wf) + self.bf)

        # Input gate: decides what new information to store
        i = self.sigmoid(np.dot(concat, self.Wi) + self.bi)

        # Candidate cell state
        c_candidate = self.tanh(np.dot(concat, self.Wc) + self.bc)

        # Update cell state
        c_next = f * c_prev + i * c_candidate

        # Output gate: decides what to output
        o = self.sigmoid(np.dot(concat, self.Wo) + self.bo)

        # Update hidden state
        h_next = o * self.tanh(c_next)

        # Cache values for backpropagation
        cache = (x, h_prev, c_prev, concat, f, i, c_candidate, c_next, o)

        return h_next, c_next, cache

    def backward(self, dh_next, dc_next, cache):
        """
        Backward pass through LSTM cell.

        Args:
            dh_next: Gradient of loss with respect to next hidden state
            dc_next: Gradient of loss with respect to next cell state
            cache: Cached values from forward pass

        Returns:
            dx: Gradient with respect to input
            dh_prev: Gradient with respect to previous hidden state
            dc_prev: Gradient with respect to previous cell state
            grads: Dictionary of gradients for parameters
        """
        x, h_prev, c_prev, concat, f, i, c_candidate, c_next, o = cache

        # Gradient of output gate
        do = dh_next * self.tanh(c_next)
        do = do * o * (1 - o)  # Sigmoid derivative

        # Gradient flowing to cell state
        dc = dh_next * o * (1 - self.tanh(c_next) ** 2) + dc_next

        # Gradient of forget gate
        df = dc * c_prev
        df = df * f * (1 - f)  # Sigmoid derivative

        # Gradient of input gate
        di = dc * c_candidate
        di = di * i * (1 - i)  # Sigmoid derivative

        # Gradient of candidate cell state
        dc_candidate = dc * i
        dc_candidate = dc_candidate * (1 - c_candidate ** 2)  # Tanh derivative

        # Gradient of cell state (for next timestep)
        dc_prev = dc * f

        # Gradients for weights and biases
        dWf = np.dot(concat.T, df)
        dbf = np.sum(df, axis=0, keepdims=True)

        dWi = np.dot(concat.T, di)
        dbi = np.sum(di, axis=0, keepdims=True)

        dWc = np.dot(concat.T, dc_candidate)
        dbc = np.sum(dc_candidate, axis=0, keepdims=True)

        dWo = np.dot(concat.T, do)
        dbo = np.sum(do, axis=0, keepdims=True)

        # Gradient for concatenated [x, h_prev]
        dconcat = (np.dot(df, self.Wf.T) +
                   np.dot(di, self.Wi.T) +
                   np.dot(dc_candidate, self.Wc.T) +
                   np.dot(do, self.Wo.T))

        # Split gradient
        dx = dconcat[:, :self.input_size]
        dh_prev = dconcat[:, self.input_size:]

        grads = {
            'Wf': dWf, 'bf': dbf,
            'Wi': dWi, 'bi': dbi,
            'Wc': dWc, 'bc': dbc,
            'Wo': dWo, 'bo': dbo
        }

        return dx, dh_prev, dc_prev, grads


class LSTMNetwork:
    """
    LSTM network for sequence learning and temporal pattern recognition.

    This network can remember past interactions and recognize patterns over time,
    allowing creatures to develop more sophisticated behaviors based on history.
    """

    def __init__(self, input_size: int, hidden_size: int, output_size: int,
                 num_layers: int = 2, learning_rate: float = 0.001,
                 sequence_length: int = 50):
        """
        Initialize LSTM network.

        Args:
            input_size: Size of input vector
            hidden_size: Size of hidden state (LSTM memory)
            output_size: Size of output vector
            num_layers: Number of LSTM layers (stacked)
            learning_rate: Learning rate for training
            sequence_length: Maximum sequence length to remember
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.num_layers = num_layers
        self.learning_rate = learning_rate
        self.sequence_length = sequence_length

        # Create LSTM layers
        self.lstm_layers = []
        for i in range(num_layers):
            layer_input_size = input_size if i == 0 else hidden_size
            self.lstm_layers.append(LSTMCell(layer_input_size, hidden_size))

        # Output layer (hidden_size -> output_size)
        self.Wy = np.random.randn(hidden_size, output_size) * 0.01
        self.by = np.zeros((1, output_size))

        # Hidden and cell states for each layer
        self.h_states = [np.zeros((1, hidden_size)) for _ in range(num_layers)]
        self.c_states = [np.zeros((1, hidden_size)) for _ in range(num_layers)]

        # Sequence buffer (stores recent interactions)
        self.sequence_buffer = deque(maxlen=sequence_length)

        # Optimizer
        self.optimizer = AdamOptimizer(learning_rate=learning_rate)

    def reset_states(self):
        """Reset hidden and cell states to zero."""
        self.h_states = [np.zeros((1, self.hidden_size)) for _ in range(self.num_layers)]
        self.c_states = [np.zeros((1, self.hidden_size)) for _ in range(self.num_layers)]

    @staticmethod
    def sigmoid(x):
        """Sigmoid activation function."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def forward_sequence(self, sequence: List[np.ndarray], reset_state: bool = False):
        """
        Forward pass through entire sequence.

        Args:
            sequence: List of input vectors
            reset_state: Whether to reset states before processing

        Returns:
            outputs: List of output predictions
            caches: Cached values for backprop
        """
        if reset_state:
            self.reset_states()

        outputs = []
        all_caches = []

        for x in sequence:
            if len(x.shape) == 1:
                x = x.reshape(1, -1)

            layer_caches = []
            layer_input = x

            # Forward through each LSTM layer
            for layer_idx in range(self.num_layers):
                h, c, cache = self.lstm_layers[layer_idx].forward(
                    layer_input,
                    self.h_states[layer_idx],
                    self.c_states[layer_idx]
                )

                self.h_states[layer_idx] = h
                self.c_states[layer_idx] = c
                layer_caches.append(cache)

                layer_input = h  # Output of this layer is input to next

            # Output layer
            y = self.sigmoid(np.dot(self.h_states[-1], self.Wy) + self.by)

            outputs.append(y)
            all_caches.append(layer_caches)

        return outputs, all_caches

    def backward_sequence(self, sequence: List[np.ndarray], targets: List[np.ndarray],
                          outputs: List[np.ndarray], all_caches: List):
        """
        Backward pass through time (BPTT).

        Args:
            sequence: List of input vectors
            targets: List of target outputs
            outputs: List of predicted outputs
            all_caches: Cached values from forward pass

        Returns:
            Dictionary of gradients
        """
        # Initialize gradient accumulators
        grads = {}
        for layer_idx in range(self.num_layers):
            for param in ['Wf', 'bf', 'Wi', 'bi', 'Wc', 'bc', 'Wo', 'bo']:
                grads[f'layer_{layer_idx}_{param}'] = 0

        dWy = np.zeros_like(self.Wy)
        dby = np.zeros_like(self.by)

        # Initialize gradients for next timestep
        dh_next = [np.zeros((1, self.hidden_size)) for _ in range(self.num_layers)]
        dc_next = [np.zeros((1, self.hidden_size)) for _ in range(self.num_layers)]

        # Backpropagate through time
        for t in reversed(range(len(sequence))):
            # Output layer gradient
            dy = outputs[t] - targets[t]
            dWy += np.dot(self.h_states[-1].T, dy)
            dby += dy

            # Gradient flowing back to last LSTM layer
            dh = np.dot(dy, self.Wy.T) + dh_next[-1]

            # Backpropagate through LSTM layers (in reverse order)
            for layer_idx in reversed(range(self.num_layers)):
                cache = all_caches[t][layer_idx]

                dx, dh_prev, dc_prev, layer_grads = self.lstm_layers[layer_idx].backward(
                    dh, dc_next[layer_idx], cache
                )

                # Accumulate gradients
                for param, grad in layer_grads.items():
                    grads[f'layer_{layer_idx}_{param}'] += grad

                # Update gradients for next timestep
                dh_next[layer_idx] = dh_prev
                dc_next[layer_idx] = dc_prev

                # Gradient for previous layer
                if layer_idx > 0:
                    dh = dh_prev
                else:
                    # No need to backprop to input
                    pass

        # Add output layer gradients
        grads['Wy'] = dWy / len(sequence)
        grads['by'] = dby / len(sequence)

        # Average LSTM gradients over sequence
        for key in grads:
            if key.startswith('layer_'):
                grads[key] /= len(sequence)

        return grads

    def train_sequence(self, sequence: List[np.ndarray], targets: List[np.ndarray]):
        """
        Train on a sequence of inputs and targets.

        Args:
            sequence: List of input vectors
            targets: List of target outputs
        """
        # Forward pass
        outputs, all_caches = self.forward_sequence(sequence, reset_state=True)

        # Backward pass
        grads = self.backward_sequence(sequence, targets, outputs, all_caches)

        # Clip gradients
        grad_list = [grads[k] for k in sorted(grads.keys())]
        grad_list = clip_gradients(grad_list, max_norm=5.0)

        # Update parameters using optimizer
        # Note: This is simplified - in full implementation would organize params better
        for layer_idx in range(self.num_layers):
            for param in ['Wf', 'bf', 'Wi', 'bi', 'Wc', 'bc', 'Wo', 'bo']:
                key = f'layer_{layer_idx}_{param}'
                if key in grads:
                    current_param = getattr(self.lstm_layers[layer_idx], param)
                    current_param -= self.learning_rate * grads[key]

        # Update output layer
        self.Wy -= self.learning_rate * grads['Wy']
        self.by -= self.learning_rate * grads['by']

    def predict(self, x: np.ndarray, use_sequence: bool = True):
        """
        Make a prediction.

        Args:
            x: Input vector
            use_sequence: Whether to use sequence context

        Returns:
            Output prediction
        """
        if use_sequence:
            # Add to sequence buffer
            self.sequence_buffer.append(x)

            # Use recent sequence
            sequence = list(self.sequence_buffer)
            outputs, _ = self.forward_sequence(sequence, reset_state=False)
            return outputs[-1]  # Return last output
        else:
            # Single-step prediction
            outputs, _ = self.forward_sequence([x], reset_state=False)
            return outputs[0]

    def add_to_sequence(self, x: np.ndarray):
        """Add input to sequence buffer."""
        self.sequence_buffer.append(x)

    def to_dict(self):
        """Convert network to dictionary for saving."""
        data = {
            'type': 'lstm',
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'output_size': self.output_size,
            'num_layers': self.num_layers,
            'learning_rate': self.learning_rate,
            'sequence_length': self.sequence_length,
            'h_states': [h.tolist() for h in self.h_states],
            'c_states': [c.tolist() for c in self.c_states],
            'sequence_buffer': [x.tolist() for x in self.sequence_buffer],
            'Wy': self.Wy.tolist(),
            'by': self.by.tolist(),
            'lstm_layers': []
        }

        # Save each LSTM layer
        for layer in self.lstm_layers:
            data['lstm_layers'].append({
                'Wf': layer.Wf.tolist(), 'bf': layer.bf.tolist(),
                'Wi': layer.Wi.tolist(), 'bi': layer.bi.tolist(),
                'Wc': layer.Wc.tolist(), 'bc': layer.bc.tolist(),
                'Wo': layer.Wo.tolist(), 'bo': layer.bo.tolist()
            })

        return data

    @classmethod
    def from_dict(cls, data):
        """Create network from dictionary."""
        network = cls(
            input_size=data['input_size'],
            hidden_size=data['hidden_size'],
            output_size=data['output_size'],
            num_layers=data['num_layers'],
            learning_rate=data['learning_rate'],
            sequence_length=data['sequence_length']
        )

        # Restore states
        network.h_states = [np.array(h) for h in data['h_states']]
        network.c_states = [np.array(c) for c in data['c_states']]

        # Restore sequence buffer
        network.sequence_buffer = deque(
            [np.array(x) for x in data['sequence_buffer']],
            maxlen=data['sequence_length']
        )

        # Restore output layer
        network.Wy = np.array(data['Wy'])
        network.by = np.array(data['by'])

        # Restore LSTM layers
        for i, layer_data in enumerate(data['lstm_layers']):
            network.lstm_layers[i].Wf = np.array(layer_data['Wf'])
            network.lstm_layers[i].bf = np.array(layer_data['bf'])
            network.lstm_layers[i].Wi = np.array(layer_data['Wi'])
            network.lstm_layers[i].bi = np.array(layer_data['bi'])
            network.lstm_layers[i].Wc = np.array(layer_data['Wc'])
            network.lstm_layers[i].bc = np.array(layer_data['bc'])
            network.lstm_layers[i].Wo = np.array(layer_data['Wo'])
            network.lstm_layers[i].bo = np.array(layer_data['bo'])

        return network
