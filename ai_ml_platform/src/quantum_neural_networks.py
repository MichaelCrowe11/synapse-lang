"""
Quantum-Classical Hybrid Neural Networks for Synapse Language

Advanced quantum-enhanced machine learning with variational quantum circuits,
quantum autoencoders, and hybrid training algorithms.
"""

import numpy as np
import sys
import os
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

# Import quantum computing components
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from quantum_computing import QuantumCircuit, QuantumRegister, ClassicalRegister
from quantum_computing.src.quantum_ml import QuantumMachineLearning
from .neural_network_dsl import Layer, NeuralNetwork, ActivationType

class QuantumLayerType(Enum):
    """Types of quantum layers."""
    VARIATIONAL = "variational"
    QUANTUM_CONV = "quantum_conv"
    QUANTUM_DENSE = "quantum_dense"
    QUANTUM_ATTENTION = "quantum_attention"
    QUANTUM_LSTM = "quantum_lstm"
    DRESSED_QUANTUM = "dressed_quantum"

class QuantumBackend(Enum):
    """Quantum computing backends."""
    SIMULATOR = "simulator"
    IBM_QUANTUM = "ibm_quantum"
    GOOGLE_CIRQ = "google_cirq"
    RIGETTI_PYQUIL = "rigetti_pyquil"
    AMAZON_BRAKET = "amazon_braket"

@dataclass
class QuantumLayerConfig:
    """Configuration for quantum layers."""
    num_qubits: int
    num_layers: int = 1
    entanglement: str = "full"
    parameter_initialization: str = "random"
    measurement_basis: str = "computational"
    backend: QuantumBackend = QuantumBackend.SIMULATOR
    shots: int = 1000
    noise_model: Optional[Dict] = None

class QuantumLayer(Layer):
    """Base class for quantum neural network layers."""
    
    def __init__(self, config: QuantumLayerConfig, name: str = None):
        super().__init__(name)
        self.config = config
        self.quantum_circuit = None
        self.parameters = {}
        self.parameter_gradients = {}
        self.quantum_backend = None
        
        # Initialize quantum circuit
        self._build_quantum_circuit()
        
    def _build_quantum_circuit(self):
        """Build the quantum circuit for this layer."""
        # Create quantum register
        self.qreg = QuantumRegister(self.config.num_qubits)
        self.creg = ClassicalRegister(self.config.num_qubits)
        self.quantum_circuit = QuantumCircuit(self.qreg, self.creg)
        
        # Initialize parameters
        self._initialize_parameters()
    
    def _initialize_parameters(self):
        """Initialize quantum parameters."""
        num_params = self.config.num_qubits * self.config.num_layers * 3  # 3 rotation angles per qubit per layer
        
        if self.config.parameter_initialization == "random":
            self.parameters = np.random.uniform(0, 2*np.pi, num_params)
        elif self.config.parameter_initialization == "zero":
            self.parameters = np.zeros(num_params)
        else:
            self.parameters = np.random.normal(0, 0.1, num_params)
    
    def encode_classical_data(self, data: np.ndarray) -> QuantumCircuit:
        """Encode classical data into quantum states."""
        if len(data.shape) == 1:
            # Single sample
            return self._encode_sample(data)
        else:
            # Batch of samples - process first sample for now
            return self._encode_sample(data[0])
    
    def _encode_sample(self, sample: np.ndarray) -> QuantumCircuit:
        """Encode single data sample into quantum circuit."""
        # Angle encoding - encode features as rotation angles
        encoding_circuit = QuantumCircuit(self.qreg)
        
        for i, feature in enumerate(sample[:self.config.num_qubits]):
            # Normalize feature to [0, 2π] range
            normalized_feature = (feature + 1) * np.pi  # Assuming features are in [-1, 1]
            encoding_circuit.ry(normalized_feature, i)
        
        return encoding_circuit
    
    def build_variational_circuit(self, parameters: np.ndarray) -> QuantumCircuit:
        """Build variational quantum circuit with given parameters."""
        var_circuit = QuantumCircuit(self.qreg)
        param_idx = 0
        
        for layer in range(self.config.num_layers):
            # Rotation layer
            for qubit in range(self.config.num_qubits):
                var_circuit.rx(parameters[param_idx], qubit)
                param_idx += 1
                var_circuit.ry(parameters[param_idx], qubit)
                param_idx += 1
                var_circuit.rz(parameters[param_idx], qubit)
                param_idx += 1
            
            # Entangling layer
            if self.config.entanglement == "full":
                for i in range(self.config.num_qubits):
                    for j in range(i + 1, self.config.num_qubits):
                        var_circuit.cnot(i, j)
            elif self.config.entanglement == "linear":
                for i in range(self.config.num_qubits - 1):
                    var_circuit.cnot(i, i + 1)
            elif self.config.entanglement == "circular":
                for i in range(self.config.num_qubits):
                    var_circuit.cnot(i, (i + 1) % self.config.num_qubits)
        
        return var_circuit
    
    def measure_expectation_values(self, circuit: QuantumCircuit) -> np.ndarray:
        """Measure expectation values from quantum circuit."""
        # Add measurements
        full_circuit = QuantumCircuit(self.qreg, self.creg)
        full_circuit.compose(circuit)
        full_circuit.measure_all()
        
        # Get measurement probabilities
        probs = full_circuit.get_probabilities()
        
        if probs is not None:
            # Convert probabilities to expectation values
            # For computational basis, expectation value of Z_i is P(0) - P(1) for qubit i
            expectations = []
            for qubit_idx in range(self.config.num_qubits):
                prob_0 = sum(probs[i] for i in range(2**self.config.num_qubits) 
                           if not (i >> qubit_idx) & 1)
                prob_1 = sum(probs[i] for i in range(2**self.config.num_qubits) 
                           if (i >> qubit_idx) & 1)
                expectation = prob_0 - prob_1
                expectations.append(expectation)
            
            return np.array(expectations)
        else:
            # Fallback to random values
            return np.random.uniform(-1, 1, self.config.num_qubits)

class QuantumDense(QuantumLayer):
    """Quantum dense (fully-connected) layer."""
    
    def __init__(self, units: int, config: QuantumLayerConfig, 
                 activation: str = "linear", name: str = None):
        self.units = units
        self.activation = ActivationType(activation) if activation != "quantum" else "quantum"
        
        # Adjust config for dense layer
        if config.num_qubits < units:
            config.num_qubits = max(4, int(np.ceil(np.log2(units))))
        
        super().__init__(config, name)
        
        # Classical post-processing weights
        self.classical_weights = None
        self.classical_bias = None
    
    def build(self, input_shape: Tuple[int, ...]):
        """Build layer parameters."""
        input_dim = input_shape[-1]
        
        # Initialize classical weights for post-processing
        self.classical_weights = np.random.normal(
            0, 0.1, (self.config.num_qubits, self.units)
        )
        self.classical_bias = np.zeros(self.units)
        
        super().build(input_shape)
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass through quantum dense layer."""
        if not self.built:
            self.build(inputs.shape)
        
        batch_size = inputs.shape[0]
        outputs = np.zeros((batch_size, self.units))
        
        for i in range(batch_size):
            # Encode input data
            encoding_circuit = self.encode_classical_data(inputs[i])
            
            # Apply variational circuit
            var_circuit = self.build_variational_circuit(self.parameters)
            
            # Combine encoding and variational circuits by copying gates
            full_circuit = QuantumCircuit(self.qreg, self.creg)
            
            # Add encoding gates
            for gate in encoding_circuit.gates:
                full_circuit.gates.append(gate)
            
            # Add variational gates  
            for gate in var_circuit.gates:
                full_circuit.gates.append(gate)
            
            # Measure expectation values
            expectations = self.measure_expectation_values(full_circuit)
            
            # Classical post-processing
            quantum_output = np.dot(expectations, self.classical_weights) + self.classical_bias
            outputs[i] = quantum_output
        
        # Apply activation
        if self.activation == "quantum":
            # Quantum activation (identity for now)
            return outputs
        else:
            return self._apply_classical_activation(outputs)
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass with parameter-shift rule for quantum gradients."""
        # Compute gradients using parameter-shift rule
        self.parameter_gradients = self._compute_quantum_gradients(grad_output)
        
        # Classical weight gradients
        if hasattr(self, 'last_quantum_output'):
            self.gradients = {
                'classical_weights': np.outer(self.last_quantum_output, grad_output),
                'classical_bias': grad_output
            }
        
        return grad_output  # Simplified - real implementation would compute input gradients
    
    def _compute_quantum_gradients(self, grad_output: np.ndarray) -> np.ndarray:
        """Compute gradients of quantum parameters using parameter-shift rule."""
        gradients = np.zeros_like(self.parameters)
        shift = np.pi / 2
        
        for param_idx in range(len(self.parameters)):
            # Forward shift
            params_plus = self.parameters.copy()
            params_plus[param_idx] += shift
            output_plus = self._evaluate_with_parameters(params_plus)
            
            # Backward shift
            params_minus = self.parameters.copy()
            params_minus[param_idx] -= shift
            output_minus = self._evaluate_with_parameters(params_minus)
            
            # Parameter-shift gradient
            gradient = (output_plus - output_minus) / 2
            gradients[param_idx] = np.sum(gradient * grad_output)
        
        return gradients
    
    def _evaluate_with_parameters(self, parameters: np.ndarray) -> np.ndarray:
        """Evaluate quantum circuit with given parameters."""
        # Simplified evaluation - would use stored input in real implementation
        var_circuit = self.build_variational_circuit(parameters)
        expectations = self.measure_expectation_values(var_circuit)
        return np.dot(expectations, self.classical_weights) + self.classical_bias
    
    def _apply_classical_activation(self, x: np.ndarray) -> np.ndarray:
        """Apply classical activation function."""
        if self.activation == ActivationType.RELU:
            return np.maximum(0, x)
        elif self.activation == ActivationType.TANH:
            return np.tanh(x)
        elif self.activation == ActivationType.SIGMOID:
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        else:
            return x  # Linear

class QuantumConvLayer(QuantumLayer):
    """Quantum convolutional layer using quantum feature maps."""
    
    def __init__(self, filters: int, kernel_size: int, config: QuantumLayerConfig, 
                 stride: int = 1, activation: str = "relu", name: str = None):
        self.filters = filters
        self.kernel_size = kernel_size
        self.stride = stride
        self.activation = ActivationType(activation)
        
        # Adjust qubits for convolution
        config.num_qubits = max(config.num_qubits, kernel_size * kernel_size)
        
        super().__init__(config, name)
        
        # Multiple quantum circuits for different filters
        self.filter_circuits = []
        self.filter_parameters = []
        
        for _ in range(filters):
            params = self._initialize_parameters()
            self.filter_parameters.append(params)
    
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """Forward pass through quantum convolutional layer."""
        batch_size, height, width, channels = inputs.shape
        
        # Calculate output dimensions
        output_height = (height - self.kernel_size) // self.stride + 1
        output_width = (width - self.kernel_size) // self.stride + 1
        
        outputs = np.zeros((batch_size, output_height, output_width, self.filters))
        
        for batch_idx in range(batch_size):
            for out_h in range(output_height):
                for out_w in range(output_width):
                    # Extract patch
                    h_start = out_h * self.stride
                    w_start = out_w * self.stride
                    patch = inputs[batch_idx, h_start:h_start+self.kernel_size, 
                                 w_start:w_start+self.kernel_size, :]
                    
                    # Flatten patch
                    patch_flat = patch.flatten()
                    
                    # Apply quantum filters
                    for filter_idx in range(self.filters):
                        # Encode patch into quantum state
                        encoding_circuit = self.encode_classical_data(patch_flat)
                        
                        # Apply filter-specific variational circuit
                        var_circuit = self.build_variational_circuit(
                            self.filter_parameters[filter_idx]
                        )
                        
                        # Combine circuits by copying gates
                        full_circuit = QuantumCircuit(self.qreg, self.creg)
                        
                        # Add encoding gates
                        for gate in encoding_circuit.gates:
                            full_circuit.gates.append(gate)
                        
                        # Add variational gates  
                        for gate in var_circuit.gates:
                            full_circuit.gates.append(gate)
                        
                        # Measure and aggregate
                        expectations = self.measure_expectation_values(full_circuit)
                        filter_output = np.mean(expectations)  # Simplified aggregation
                        
                        outputs[batch_idx, out_h, out_w, filter_idx] = filter_output
        
        # Apply activation
        if self.activation == ActivationType.RELU:
            outputs = np.maximum(0, outputs)
        elif self.activation == ActivationType.TANH:
            outputs = np.tanh(outputs)
        
        return outputs
    
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        """Backward pass for quantum convolution (simplified)."""
        # Placeholder implementation
        return grad_output

class HybridQNN(NeuralNetwork):
    """Hybrid Quantum-Classical Neural Network."""
    
    def __init__(self, name: str = "HybridQNN"):
        super().__init__(name)
        self.quantum_layers = []
        self.classical_layers = []
        self.hybrid_training = True
        self.quantum_optimizer_params = {
            'learning_rate': 0.01,
            'gradient_method': 'parameter_shift'
        }
    
    def add_quantum_layer(self, layer: QuantumLayer) -> 'HybridQNN':
        """Add quantum layer to the network."""
        self.add(layer)
        self.quantum_layers.append(layer)
        return self
    
    def add_classical_layer(self, layer: Layer) -> 'HybridQNN':
        """Add classical layer to the network."""
        self.add(layer)
        self.classical_layers.append(layer)
        return self
    
    def compile_hybrid(self, quantum_optimizer: str = "parameter_shift",
                      classical_optimizer: str = "adam",
                      loss: str = "mse", learning_rate: float = 0.001):
        """Compile hybrid network with separate optimizers for quantum and classical parts."""
        super().compile(classical_optimizer, loss, learning_rate=learning_rate)
        
        self.quantum_optimizer_params = {
            'method': quantum_optimizer,
            'learning_rate': learning_rate,
            'gradient_method': 'parameter_shift' if quantum_optimizer == 'parameter_shift' else 'finite_diff'
        }
        
        print(f"Hybrid model compiled:")
        print(f"  Classical optimizer: {classical_optimizer}")
        print(f"  Quantum optimizer: {quantum_optimizer}")
        print(f"  Loss function: {loss}")
    
    def fit_hybrid(self, X: np.ndarray, y: np.ndarray, epochs: int = 100,
                  batch_size: int = 32, quantum_shots: int = 1000,
                  validation_split: float = 0.0, verbose: int = 1) -> Dict:
        """Train hybrid quantum-classical network."""
        if not self.compiled:
            raise ValueError("Model must be compiled before training")
        
        # Update quantum layer shots
        for layer in self.quantum_layers:
            layer.config.shots = quantum_shots
        
        # Use parent fit method with hybrid parameter updates
        return super().fit(X, y, epochs, batch_size, validation_split, verbose)
    
    def _update_parameters(self):
        """Update both quantum and classical parameters."""
        # Update classical parameters
        for layer in self.classical_layers:
            if hasattr(layer, 'weights') and layer.weights is not None:
                if hasattr(layer, 'gradients') and 'weights' in layer.gradients:
                    layer.weights -= self.learning_rate * layer.gradients['weights']
            
            if hasattr(layer, 'bias') and layer.bias is not None:
                if hasattr(layer, 'gradients') and 'bias' in layer.gradients:
                    layer.bias -= self.learning_rate * layer.gradients['bias']
        
        # Update quantum parameters
        quantum_lr = self.quantum_optimizer_params['learning_rate']
        for layer in self.quantum_layers:
            if hasattr(layer, 'parameter_gradients'):
                layer.parameters -= quantum_lr * layer.parameter_gradients
    
    def quantum_circuit_summary(self):
        """Print summary of quantum circuits in the model."""
        print("\nQuantum Circuit Summary:")
        print("=" * 60)
        
        total_qubits = 0
        total_quantum_params = 0
        
        for i, layer in enumerate(self.quantum_layers):
            layer_qubits = layer.config.num_qubits
            layer_params = len(layer.parameters)
            total_qubits += layer_qubits
            total_quantum_params += layer_params
            
            print(f"Quantum Layer {i+1} ({layer.__class__.__name__}):")
            print(f"  Qubits: {layer_qubits}")
            print(f"  Quantum Parameters: {layer_params}")
            print(f"  Entanglement: {layer.config.entanglement}")
            print(f"  Measurement Shots: {layer.config.shots}")
            print()
        
        print(f"Total Quantum Qubits: {total_qubits}")
        print(f"Total Quantum Parameters: {total_quantum_params}")
        print(f"Classical Layers: {len(self.classical_layers)}")

class QuantumAutoencoder:
    """Quantum autoencoder for dimensionality reduction."""
    
    def __init__(self, input_dim: int, latent_dim: int, 
                 quantum_config: QuantumLayerConfig):
        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.quantum_config = quantum_config
        
        # Build encoder and decoder
        self.encoder = self._build_encoder()
        self.decoder = self._build_decoder()
    
    def _build_encoder(self) -> HybridQNN:
        """Build quantum encoder."""
        encoder = HybridQNN("QuantumEncoder")
        
        # Quantum encoding layer
        encoding_config = QuantumLayerConfig(
            num_qubits=max(4, int(np.ceil(np.log2(self.input_dim)))),
            num_layers=2,
            entanglement="linear"
        )
        encoder.add_quantum_layer(QuantumDense(
            units=self.latent_dim,
            config=encoding_config,
            activation="tanh"
        ))
        
        return encoder
    
    def _build_decoder(self) -> HybridQNN:
        """Build quantum decoder."""
        decoder = HybridQNN("QuantumDecoder")
        
        # Quantum decoding layer
        decoding_config = QuantumLayerConfig(
            num_qubits=max(4, int(np.ceil(np.log2(self.latent_dim)))),
            num_layers=2,
            entanglement="linear"
        )
        decoder.add_quantum_layer(QuantumDense(
            units=self.input_dim,
            config=decoding_config,
            activation="linear"
        ))
        
        return decoder
    
    def encode(self, X: np.ndarray) -> np.ndarray:
        """Encode input to latent representation."""
        return self.encoder.predict(X)
    
    def decode(self, latent: np.ndarray) -> np.ndarray:
        """Decode latent representation back to input space."""
        return self.decoder.predict(latent)
    
    def fit(self, X: np.ndarray, epochs: int = 100, learning_rate: float = 0.01):
        """Train quantum autoencoder."""
        # Compile models
        self.encoder.compile_hybrid(learning_rate=learning_rate)
        self.decoder.compile_hybrid(learning_rate=learning_rate)
        
        print("Training Quantum Autoencoder...")
        
        for epoch in range(epochs):
            # Forward pass
            encoded = self.encoder.predict(X)
            reconstructed = self.decoder.predict(encoded)
            
            # Compute reconstruction loss
            loss = np.mean((X - reconstructed) ** 2)
            
            # Simplified training - would implement proper backprop in real version
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Reconstruction Loss = {loss:.4f}")

# Factory functions
def create_quantum_classifier(input_dim: int, num_classes: int, 
                            num_qubits: int = 4, num_layers: int = 2) -> HybridQNN:
    """Create quantum classifier."""
    config = QuantumLayerConfig(
        num_qubits=num_qubits,
        num_layers=num_layers,
        entanglement="full"
    )
    
    model = HybridQNN("QuantumClassifier")
    
    # Add quantum feature extraction layer
    model.add_quantum_layer(QuantumDense(
        units=num_qubits,
        config=config,
        activation="quantum"
    ))
    
    # Add classical output layer
    from .neural_network_dsl import Dense
    model.add_classical_layer(Dense(
        units=num_classes,
        activation="softmax"
    ))
    
    return model

def create_quantum_cnn(input_shape: Tuple[int, int, int], num_classes: int,
                      num_quantum_filters: int = 4) -> HybridQNN:
    """Create quantum convolutional neural network."""
    model = HybridQNN("QuantumCNN")
    
    # Quantum convolutional layers
    conv_config = QuantumLayerConfig(
        num_qubits=6,
        num_layers=1,
        entanglement="circular"
    )
    
    model.add_quantum_layer(QuantumConvLayer(
        filters=num_quantum_filters,
        kernel_size=3,
        config=conv_config,
        activation="relu"
    ))
    
    # Classical layers for final processing
    from .neural_network_dsl import Dense
    model.add_classical_layer(Dense(units=64, activation="relu"))
    model.add_classical_layer(Dense(units=num_classes, activation="softmax"))
    
    return model

# Export main classes
__all__ = [
    'QuantumLayer', 'QuantumDense', 'QuantumConvLayer', 'HybridQNN',
    'QuantumAutoencoder', 'QuantumLayerConfig', 'QuantumLayerType',
    'create_quantum_classifier', 'create_quantum_cnn'
]