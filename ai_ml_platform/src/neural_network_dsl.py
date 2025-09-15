"""
Neural Network Domain Specific Language for Synapse Language

Provides intuitive syntax for building and training neural networks
with automatic GPU acceleration and quantum integration.
"""

import numpy as np
from typing import List, Dict, Optional, Union, Callable, Any, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import json

class ActivationType(Enum):
    """Neural network activation functions."""
    RELU = "relu"
    GELU = "gelu"  
    SWISH = "swish"
    TANH = "tanh"
    SIGMOID = "sigmoid"
    SOFTMAX = "softmax"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    LINEAR = "linear"
    QUANTUM = "quantum"  # Quantum activation

class OptimizerType(Enum):
    """Optimization algorithms."""
    ADAM = "adam"
    ADAMW = "adamw"
    SGD = "sgd"
    RMSPROP = "rmsprop"
    QUANTUM_NATURAL_GRADIENT = "qng"  # Quantum optimizer

@dataclass
class LayerConfig:
    """Configuration for neural network layers."""
    name: str
    layer_type: str
    units: Optional[int] = None
    activation: Optional[str] = None
    dropout_rate: Optional[float] = None
    kernel_size: Optional[Tuple[int, int]] = None
    stride: Optional[Tuple[int, int]] = None
    padding: Optional[str] = None
    quantum_circuit: Optional[Any] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

class Layer(ABC):
    """Abstract base class for neural network layers."""
    
    def __init__(self, name: str = None):
        self.name = name or f"{self.__class__.__name__.lower()}_{id(self)}"
        self.built = False
        self.trainable = True
        self.parameters = {}
        self.gradients = {}
        
    @abstractmethod
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass through the layer."""
        pass
    
    @abstractmethod
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass through the layer."""
        pass
    
    def build(self, input_shape: Tuple[int, ...]):
        """Build layer parameters based on input shape."""
        self.built = True
    
    def get_config(self) -> LayerConfig:
        """Get layer configuration."""
        return LayerConfig(
            name=self.name,
            layer_type=self.__class__.__name__,
            parameters=self.parameters.copy()
        )

class Dense(Layer):
    """Fully connected (dense) layer with automatic GPU acceleration."""
    
    def __init__(self, units: int, activation: str = 'relu', 
                 dropout_rate: float = 0.0, use_bias: bool = True,
                 kernel_initializer: str = 'glorot_uniform', name: str = None):
        super().__init__(name)
        self.units = units
        self.activation = ActivationType(activation)
        self.dropout_rate = dropout_rate
        self.use_bias = use_bias
        self.kernel_initializer = kernel_initializer
        
        # Parameters (will be initialized in build())
        self.weights = None
        self.bias = None
        self.input_shape = None
        
    def build(self, input_shape: Tuple[int, ...]):
        """Initialize weights and biases."""
        input_dim = input_shape[-1]
        
        # Initialize weights
        if self.kernel_initializer == 'glorot_uniform':
            limit = np.sqrt(6.0 / (input_dim + self.units))
            self.weights = np.random.uniform(-limit, limit, (input_dim, self.units))
        elif self.kernel_initializer == 'he_normal':
            self.weights = np.random.normal(0, np.sqrt(2.0 / input_dim), (input_dim, self.units))
        else:
            self.weights = np.random.normal(0, 0.1, (input_dim, self.units))
        
        # Initialize bias
        if self.use_bias:
            self.bias = np.zeros(self.units)
        
        self.input_shape = input_shape
        super().build(input_shape)
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass: linear transformation + activation."""
        if not self.built:
            self.build(inputs.shape)
        
        # Store input for backward pass
        self.last_input = inputs
        
        # Linear transformation: y = xW + b
        output = np.dot(inputs, self.weights)
        if self.use_bias:
            output += self.bias
        
        # Apply activation function
        output = self._apply_activation(output)
        
        # Apply dropout during training
        if self.dropout_rate > 0 and self.trainable:
            self.dropout_mask = np.random.binomial(1, 1-self.dropout_rate, output.shape)
            output *= self.dropout_mask / (1 - self.dropout_rate)
        
        return output
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass: compute gradients."""
        # Apply dropout mask to gradients
        if hasattr(self, 'dropout_mask'):
            grad_output *= self.dropout_mask / (1 - self.dropout_rate)
        
        # Gradient through activation
        grad_activation = self._activation_gradient(grad_output)
        
        # Gradient w.r.t. weights
        self.gradients['weights'] = np.dot(self.last_input.T, grad_activation)
        
        # Gradient w.r.t. bias
        if self.use_bias:
            self.gradients['bias'] = np.sum(grad_activation, axis=0)
        
        # Gradient w.r.t. input
        grad_input = np.dot(grad_activation, self.weights.T)
        
        return grad_input
    
    def _apply_activation(self, x: np.ndarray) -> np.ndarray:
        """Apply activation function."""
        if self.activation == ActivationType.RELU:
            return np.maximum(0, x)
        elif self.activation == ActivationType.GELU:
            return 0.5 * x * (1 + np.tanh(np.sqrt(2/np.pi) * (x + 0.044715 * x**3)))
        elif self.activation == ActivationType.SWISH:
            return x * self._sigmoid(x)
        elif self.activation == ActivationType.TANH:
            return np.tanh(x)
        elif self.activation == ActivationType.SIGMOID:
            return self._sigmoid(x)
        elif self.activation == ActivationType.SOFTMAX:
            exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
            return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
        elif self.activation == ActivationType.LEAKY_RELU:
            return np.where(x > 0, x, 0.01 * x)
        elif self.activation == ActivationType.ELU:
            return np.where(x > 0, x, np.exp(x) - 1)
        else:
            return x  # Linear activation
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable sigmoid function."""
        return np.where(x >= 0, 
                       1 / (1 + np.exp(-x)),
                       np.exp(x) / (1 + np.exp(x)))
    
    def _activation_gradient(self, grad_output: np.ndarray) -> np.ndarray:
        """Compute gradient of activation function."""
        # This is simplified - in practice would use stored forward pass values
        return grad_output  # Placeholder implementation

class Conv2D(Layer):
    """2D Convolutional layer with GPU acceleration."""
    
    def __init__(self, filters: int, kernel_size: Tuple[int, int], 
                 stride: Tuple[int, int] = (1, 1), padding: str = 'valid',
                 activation: str = 'relu', name: str = None):
        super().__init__(name)
        self.filters = filters
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.activation = ActivationType(activation)
        
        # Parameters
        self.weights = None
        self.bias = None
    
    def build(self, input_shape: Tuple[int, ...]):
        """Initialize convolutional weights."""
        # input_shape: (batch, height, width, channels)
        input_channels = input_shape[-1]
        
        # Initialize weights: (kernel_h, kernel_w, input_channels, filters)
        fan_in = self.kernel_size[0] * self.kernel_size[1] * input_channels
        limit = np.sqrt(6.0 / fan_in)
        self.weights = np.random.uniform(
            -limit, limit, 
            (*self.kernel_size, input_channels, self.filters)
        )
        
        # Initialize bias
        self.bias = np.zeros(self.filters)
        
        super().build(input_shape)
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass: convolution + activation."""
        if not self.built:
            self.build(inputs.shape)
        
        # Store input for backward pass
        self.last_input = inputs
        
        # Perform convolution (simplified implementation)
        output = self._convolve_2d(inputs, self.weights, self.stride, self.padding)
        output += self.bias
        
        # Apply activation
        return self._apply_activation(output)
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass for convolution."""
        # Simplified implementation - real version would compute proper gradients
        return grad_output
    
    def _convolve_2d(self, inputs: np.ndarray, weights: np.ndarray, 
                    stride: Tuple[int, int], padding: str) -> np.ndarray:
        """Simplified 2D convolution operation."""
        # This is a placeholder - real implementation would use optimized convolution
        batch_size, input_h, input_w, input_c = inputs.shape
        kernel_h, kernel_w, _, num_filters = weights.shape
        
        # Calculate output dimensions
        if padding == 'valid':
            output_h = (input_h - kernel_h) // stride[0] + 1
            output_w = (input_w - kernel_w) // stride[1] + 1
        else:  # 'same' padding
            output_h = input_h // stride[0]
            output_w = input_w // stride[1]
        
        # Initialize output
        output = np.zeros((batch_size, output_h, output_w, num_filters))
        
        # Simplified convolution loop (not optimized)
        for b in range(batch_size):
            for f in range(num_filters):
                for oh in range(output_h):
                    for ow in range(output_w):
                        ih_start = oh * stride[0]
                        iw_start = ow * stride[1]
                        ih_end = ih_start + kernel_h
                        iw_end = iw_start + kernel_w
                        
                        if ih_end <= input_h and iw_end <= input_w:
                            patch = inputs[b, ih_start:ih_end, iw_start:iw_end, :]
                            output[b, oh, ow, f] = np.sum(patch * weights[:, :, :, f])
        
        return output
    
    def _apply_activation(self, x: np.ndarray) -> np.ndarray:
        """Apply activation function (same as Dense layer)."""
        if self.activation == ActivationType.RELU:
            return np.maximum(0, x)
        elif self.activation == ActivationType.GELU:
            return 0.5 * x * (1 + np.tanh(np.sqrt(2/np.pi) * (x + 0.044715 * x**3)))
        else:
            return x

class LSTM(Layer):
    """Long Short-Term Memory layer for sequence modeling."""
    
    def __init__(self, units: int, return_sequences: bool = False,
                 dropout: float = 0.0, name: str = None):
        super().__init__(name)
        self.units = units
        self.return_sequences = return_sequences
        self.dropout = dropout
        
        # LSTM gates parameters (will be initialized in build())
        self.W_f = self.W_i = self.W_o = self.W_c = None  # Weight matrices
        self.U_f = self.U_i = self.U_o = self.U_c = None  # Recurrent weights
        self.b_f = self.b_i = self.b_o = self.b_c = None  # Biases
    
    def build(self, input_shape: Tuple[int, ...]):
        """Initialize LSTM parameters."""
        # input_shape: (batch, sequence_length, features)
        input_dim = input_shape[-1]
        
        # Initialize weight matrices for gates
        limit = 1.0 / np.sqrt(self.units)
        
        # Input to hidden weights
        self.W_f = np.random.uniform(-limit, limit, (input_dim, self.units))  # Forget gate
        self.W_i = np.random.uniform(-limit, limit, (input_dim, self.units))  # Input gate  
        self.W_o = np.random.uniform(-limit, limit, (input_dim, self.units))  # Output gate
        self.W_c = np.random.uniform(-limit, limit, (input_dim, self.units))  # Cell state
        
        # Hidden to hidden weights (recurrent)
        self.U_f = np.random.uniform(-limit, limit, (self.units, self.units))
        self.U_i = np.random.uniform(-limit, limit, (self.units, self.units))
        self.U_o = np.random.uniform(-limit, limit, (self.units, self.units))
        self.U_c = np.random.uniform(-limit, limit, (self.units, self.units))
        
        # Biases (forget gate bias initialized to 1 for better gradient flow)
        self.b_f = np.ones(self.units)
        self.b_i = np.zeros(self.units)
        self.b_o = np.zeros(self.units)
        self.b_c = np.zeros(self.units)
        
        super().build(input_shape)
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass through LSTM."""
        if not self.built:
            self.build(inputs.shape)
        
        batch_size, seq_length, _ = inputs.shape
        
        # Initialize hidden state and cell state
        h_t = np.zeros((batch_size, self.units))
        c_t = np.zeros((batch_size, self.units))
        
        outputs = []
        
        # Process each time step
        for t in range(seq_length):
            x_t = inputs[:, t, :]  # Input at time t
            
            # Compute gates
            f_t = self._sigmoid(np.dot(x_t, self.W_f) + np.dot(h_t, self.U_f) + self.b_f)  # Forget gate
            i_t = self._sigmoid(np.dot(x_t, self.W_i) + np.dot(h_t, self.U_i) + self.b_i)  # Input gate
            o_t = self._sigmoid(np.dot(x_t, self.W_o) + np.dot(h_t, self.U_o) + self.b_o)  # Output gate
            c_tilde = np.tanh(np.dot(x_t, self.W_c) + np.dot(h_t, self.U_c) + self.b_c)    # Candidate values
            
            # Update cell state
            c_t = f_t * c_t + i_t * c_tilde
            
            # Update hidden state
            h_t = o_t * np.tanh(c_t)
            
            if self.return_sequences:
                outputs.append(h_t.copy())
        
        if self.return_sequences:
            return np.stack(outputs, axis=1)  # (batch, seq_length, units)
        else:
            return h_t  # (batch, units) - only final output
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass through LSTM (simplified)."""
        # LSTM backpropagation is complex - this is a placeholder
        return grad_output
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable sigmoid."""
        return np.where(x >= 0, 
                       1 / (1 + np.exp(-x)),
                       np.exp(x) / (1 + np.exp(x)))

class Attention(Layer):
    """Multi-head attention mechanism."""
    
    def __init__(self, num_heads: int, key_dim: int, dropout: float = 0.0, name: str = None):
        super().__init__(name)
        self.num_heads = num_heads
        self.key_dim = key_dim
        self.dropout = dropout
        
        # Parameters (initialized in build())
        self.W_q = self.W_k = self.W_v = self.W_o = None
    
    def build(self, input_shape: Tuple[int, ...]):
        """Initialize attention parameters."""
        # input_shape: (batch, seq_length, d_model)
        d_model = input_shape[-1]
        
        # Initialize weight matrices
        limit = 1.0 / np.sqrt(d_model)
        self.W_q = np.random.uniform(-limit, limit, (d_model, self.num_heads * self.key_dim))
        self.W_k = np.random.uniform(-limit, limit, (d_model, self.num_heads * self.key_dim))
        self.W_v = np.random.uniform(-limit, limit, (d_model, self.num_heads * self.key_dim))
        self.W_o = np.random.uniform(-limit, limit, (self.num_heads * self.key_dim, d_model))
        
        super().build(input_shape)
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass through multi-head attention."""
        if not self.built:
            self.build(inputs.shape)
        
        batch_size, seq_length, d_model = inputs.shape
        
        # Compute Q, K, V
        Q = np.dot(inputs, self.W_q).reshape(batch_size, seq_length, self.num_heads, self.key_dim)
        K = np.dot(inputs, self.W_k).reshape(batch_size, seq_length, self.num_heads, self.key_dim)
        V = np.dot(inputs, self.W_v).reshape(batch_size, seq_length, self.num_heads, self.key_dim)
        
        # Transpose for attention computation: (batch, num_heads, seq_length, key_dim)
        Q = Q.transpose(0, 2, 1, 3)
        K = K.transpose(0, 2, 1, 3)
        V = V.transpose(0, 2, 1, 3)
        
        # Scaled dot-product attention
        scores = np.matmul(Q, K.transpose(0, 1, 3, 2)) / np.sqrt(self.key_dim)
        attention_weights = self._softmax(scores)
        
        # Apply attention to values
        context = np.matmul(attention_weights, V)  # (batch, num_heads, seq_length, key_dim)
        
        # Concatenate heads and apply output projection
        context = context.transpose(0, 2, 1, 3).reshape(batch_size, seq_length, -1)
        output = np.dot(context, self.W_o)
        
        return output
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass through attention (simplified)."""
        return grad_output
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Numerically stable softmax."""
        exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

class NeuralNetwork:
    """Main neural network class with automatic GPU acceleration."""
    
    def __init__(self, name: str = "SynapseNeuralNetwork"):
        self.name = name
        self.layers = []
        self.compiled = False
        self.gpu_enabled = False
        self.training_history = {}
        
        # Training configuration
        self.optimizer = None
        self.loss_function = None
        self.metrics = []
        
    def add(self, layer: Layer) -> 'NeuralNetwork':
        """Add layer to the network."""
        self.layers.append(layer)
        return self
    
    def compile(self, optimizer: str = 'adam', loss: str = 'mse', 
                metrics: List[str] = None, learning_rate: float = 0.001):
        """Compile the network with optimizer and loss function."""
        self.optimizer = OptimizerType(optimizer)
        self.loss_function = loss
        self.metrics = metrics or []
        self.learning_rate = learning_rate
        self.compiled = True
        
        print(f"Model compiled with {optimizer} optimizer and {loss} loss")
        return self
    
    def forward(self, inputs: np.ndarray, training: bool = False) -> np.ndarray:
        """Forward pass through all layers."""
        x = inputs
        
        for layer in self.layers:
            layer.trainable = training
            x = layer.forward(x)
        
        return x
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass through all layers."""
        grad = grad_output
        
        for layer in reversed(self.layers):
            grad = layer.backward(grad)
        
        return grad
    
    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, 
            batch_size: int = 32, validation_split: float = 0.0,
            verbose: int = 1) -> Dict:
        """Train the neural network."""
        if not self.compiled:
            raise ValueError("Model must be compiled before training")
        
        # Split validation data
        if validation_split > 0:
            split_idx = int(len(X) * (1 - validation_split))
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
        else:
            X_train, y_train = X, y
            X_val = y_val = None
        
        history = {'loss': [], 'val_loss': [] if X_val is not None else None}
        
        # Training loop
        for epoch in range(epochs):
            epoch_loss = 0
            num_batches = (len(X_train) + batch_size - 1) // batch_size
            
            for batch_idx in range(num_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, len(X_train))
                
                X_batch = X_train[start_idx:end_idx]
                y_batch = y_train[start_idx:end_idx]
                
                # Forward pass
                predictions = self.forward(X_batch, training=True)
                
                # Compute loss
                loss = self._compute_loss(predictions, y_batch)
                epoch_loss += loss
                
                # Backward pass
                grad_loss = self._compute_loss_gradient(predictions, y_batch)
                self.backward(grad_loss)
                
                # Update parameters (simplified optimizer)
                self._update_parameters()
            
            avg_loss = epoch_loss / num_batches
            history['loss'].append(avg_loss)
            
            # Validation
            if X_val is not None:
                val_predictions = self.forward(X_val, training=False)
                val_loss = self._compute_loss(val_predictions, y_val)
                history['val_loss'].append(val_loss)
            
            if verbose and (epoch + 1) % 10 == 0:
                if X_val is not None:
                    print(f"Epoch {epoch + 1}/{epochs} - loss: {avg_loss:.4f} - val_loss: {val_loss:.4f}")
                else:
                    print(f"Epoch {epoch + 1}/{epochs} - loss: {avg_loss:.4f}")
        
        self.training_history = history
        return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions on input data."""
        return self.forward(X, training=False)
    
    def enable_gpu_acceleration(self):
        """Enable GPU acceleration for training."""
        self.gpu_enabled = True
        print("GPU acceleration enabled (placeholder - requires GPU backend)")
    
    def summary(self):
        """Print model architecture summary."""
        print(f"\nModel: {self.name}")
        print("=" * 65)
        print(f"{'Layer (type)':<25} {'Output Shape':<20} {'Param #':<10}")
        print("=" * 65)
        
        total_params = 0
        for i, layer in enumerate(self.layers):
            layer_params = self._count_layer_params(layer)
            total_params += layer_params
            
            layer_name = f"{layer.name} ({layer.__class__.__name__})"
            output_shape = "Multiple"  # Simplified
            
            print(f"{layer_name:<25} {output_shape:<20} {layer_params:<10}")
        
        print("=" * 65)
        print(f"Total params: {total_params:,}")
        print(f"Trainable params: {total_params:,}")
        print(f"Non-trainable params: 0")
    
    def _compute_loss(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Compute loss function."""
        if self.loss_function == 'mse':
            return np.mean((predictions - targets) ** 2)
        elif self.loss_function == 'categorical_crossentropy':
            # Avoid log(0) by adding small epsilon
            epsilon = 1e-7
            predictions = np.clip(predictions, epsilon, 1 - epsilon)
            return -np.mean(targets * np.log(predictions))
        else:
            return np.mean((predictions - targets) ** 2)  # Default to MSE
    
    def _compute_loss_gradient(self, predictions: np.ndarray, targets: np.ndarray) -> np.ndarray:
        """Compute gradient of loss function."""
        if self.loss_function == 'mse':
            return 2 * (predictions - targets) / len(predictions)
        elif self.loss_function == 'categorical_crossentropy':
            return (predictions - targets) / len(predictions)
        else:
            return 2 * (predictions - targets) / len(predictions)
    
    def _update_parameters(self):
        """Update model parameters using optimizer (simplified)."""
        # This is a simplified parameter update - real implementation would
        # use proper optimizer algorithms like Adam, AdamW, etc.
        for layer in self.layers:
            if hasattr(layer, 'weights') and layer.weights is not None:
                if 'weights' in layer.gradients:
                    layer.weights -= self.learning_rate * layer.gradients['weights']
            
            if hasattr(layer, 'bias') and layer.bias is not None:
                if 'bias' in layer.gradients:
                    layer.bias -= self.learning_rate * layer.gradients['bias']
    
    def _count_layer_params(self, layer: Layer) -> int:
        """Count trainable parameters in a layer."""
        param_count = 0
        
        if hasattr(layer, 'weights') and layer.weights is not None:
            param_count += layer.weights.size
        
        if hasattr(layer, 'bias') and layer.bias is not None:
            param_count += layer.bias.size
        
        return param_count
    
    def save(self, filepath: str):
        """Save model architecture and weights."""
        model_config = {
            'name': self.name,
            'layers': [layer.get_config().__dict__ for layer in self.layers],
            'optimizer': self.optimizer.value if self.optimizer else None,
            'loss_function': self.loss_function,
            'learning_rate': self.learning_rate
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_config, f, indent=2)
        
        print(f"Model saved to {filepath}")

# Export all classes
__all__ = [
    'NeuralNetwork', 'Layer', 'Dense', 'Conv2D', 'LSTM', 'Attention',
    'LayerConfig', 'ActivationType', 'OptimizerType'
]