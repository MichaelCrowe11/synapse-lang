"""
Quantum Machine Learning for Synapse Language

Implements quantum machine learning algorithms including variational quantum
classifiers, quantum neural networks, and quantum feature maps.
"""

from dataclasses import dataclass
from typing import Any

import numpy as np

from .quantum_circuit import ClassicalRegister, QuantumCircuit, QuantumRegister


@dataclass
class QuantumDataPoint:
    """Represents a quantum-encoded data point."""
    features: np.ndarray
    label: Any | None = None
    encoding_circuit: QuantumCircuit | None = None

class QuantumMachineLearning:
    """Quantum machine learning algorithms and utilities."""

    @staticmethod
    def amplitude_encoding(data: np.ndarray) -> QuantumCircuit:
        """
        Encode classical data into quantum amplitudes.

        Args:
            data: Classical data vector (will be normalized)

        Returns:
            QuantumCircuit that encodes data in quantum state amplitudes
        """
        # Normalize data
        normalized_data = data / np.linalg.norm(data)

        # Calculate required number of qubits
        n_qubits = int(np.ceil(np.log2(len(data))))
        data_size = 2 ** n_qubits

        # Pad data if necessary
        if len(normalized_data) < data_size:
            padded_data = np.zeros(data_size)
            padded_data[:len(normalized_data)] = normalized_data
            normalized_data = padded_data

        qreg = QuantumRegister(n_qubits)
        circuit = QuantumCircuit(qreg)

        # Initialize quantum state with data amplitudes
        # This is a simplified implementation - real amplitude encoding
        # would use more sophisticated state preparation techniques

        # For demonstration, use rotation gates to approximate amplitudes
        for i in range(n_qubits):
            if i < len(data) and abs(data[i]) > 1e-10:
                theta = 2 * np.arcsin(min(1.0, abs(normalized_data[i])))
                circuit.ry(theta, i)

        circuit.name = f"Amplitude Encoding ({len(data)} features)"
        return circuit

    @staticmethod
    def angle_encoding(data: np.ndarray) -> QuantumCircuit:
        """
        Encode classical data into rotation angles.

        Args:
            data: Classical data vector

        Returns:
            QuantumCircuit that encodes data in rotation angles
        """
        n_qubits = len(data)

        qreg = QuantumRegister(n_qubits)
        circuit = QuantumCircuit(qreg)

        # Encode each feature as rotation angle
        for i, feature in enumerate(data):
            circuit.ry(feature, i)

        circuit.name = f"Angle Encoding ({n_qubits} features)"
        return circuit

    @staticmethod
    def basis_encoding(data: np.ndarray) -> QuantumCircuit:
        """
        Encode classical data into computational basis states.

        Args:
            data: Binary data vector

        Returns:
            QuantumCircuit that encodes data in basis states
        """
        n_qubits = len(data)

        qreg = QuantumRegister(n_qubits)
        circuit = QuantumCircuit(qreg)

        # Apply X gate for each '1' in the data
        for i, bit in enumerate(data):
            if bit:
                circuit.x(i)

        circuit.name = f"Basis Encoding ({n_qubits} bits)"
        return circuit

    @staticmethod
    def create_feature_map(data: np.ndarray, map_type: str = "ZZFeatureMap",
                          reps: int = 1) -> QuantumCircuit:
        """
        Create quantum feature map for data encoding.

        Args:
            data: Input data features
            map_type: Type of feature map ('ZZFeatureMap', 'ZFeatureMap', 'PauliFeatureMap')
            reps: Number of repetitions

        Returns:
            QuantumCircuit implementing the feature map
        """
        n_features = len(data)
        n_qubits = n_features

        qreg = QuantumRegister(n_qubits)
        circuit = QuantumCircuit(qreg)

        for _rep in range(reps):
            if map_type == "ZZFeatureMap":
                # Apply Hadamard layer
                for i in range(n_qubits):
                    circuit.h(i)

                # Apply feature-dependent rotations
                for i in range(n_qubits):
                    circuit.rz(2 * data[i], i)

                # Apply entangling layer
                for i in range(n_qubits - 1):
                    circuit.cnot(i, i + 1)
                    circuit.rz(2 * data[i] * data[i + 1], i + 1)
                    circuit.cnot(i, i + 1)

            elif map_type == "ZFeatureMap":
                # Simple Z-rotation feature map
                for i in range(n_qubits):
                    circuit.h(i)
                    circuit.rz(2 * data[i], i)

            elif map_type == "PauliFeatureMap":
                # Pauli feature map with all Pauli operators
                for i in range(n_qubits):
                    circuit.h(i)
                    circuit.rx(2 * data[i], i)
                    circuit.ry(2 * data[i], i)
                    circuit.rz(2 * data[i], i)

        circuit.name = f"{map_type} ({n_features} features, {reps} reps)"
        return circuit

    @staticmethod
    def variational_classifier(n_qubits: int, n_layers: int = 1) -> QuantumCircuit:
        """
        Create variational quantum classifier ansatz.

        Args:
            n_qubits: Number of qubits
            n_layers: Number of variational layers

        Returns:
            QuantumCircuit implementing variational ansatz
        """
        qreg = QuantumRegister(n_qubits)
        circuit = QuantumCircuit(qreg)

        # Parameter counter (in real implementation, these would be optimizable)
        param_idx = 0

        for _layer in range(n_layers):
            # Rotation layer
            for qubit in range(n_qubits):
                circuit.ry(f"theta_{param_idx}", qubit)  # Parametric gate
                param_idx += 1
                circuit.rz(f"phi_{param_idx}", qubit)
                param_idx += 1

            # Entangling layer
            for qubit in range(n_qubits - 1):
                circuit.cnot(qubit, qubit + 1)

        # Final rotation layer
        for qubit in range(n_qubits):
            circuit.ry(f"theta_final_{qubit}", qubit)

        circuit.name = f"Variational Classifier ({n_layers} layers)"
        return circuit

    @staticmethod
    def quantum_neural_network(input_size: int, hidden_layers: list[int],
                              output_size: int) -> QuantumCircuit:
        """
        Create quantum neural network architecture.

        Args:
            input_size: Number of input features
            hidden_layers: List of hidden layer sizes
            output_size: Number of output classes

        Returns:
            QuantumCircuit implementing quantum neural network
        """
        # Calculate total qubits needed
        max_layer_size = max([input_size] + hidden_layers + [output_size])
        n_qubits = int(np.ceil(np.log2(max_layer_size)))

        qreg = QuantumRegister(n_qubits)
        circuit = QuantumCircuit(qreg)

        # Input encoding layer
        for i in range(min(n_qubits, input_size)):
            circuit.h(i)
            circuit.ry(f"input_{i}", i)

        # Hidden layers
        layer_idx = 0
        for hidden_size in hidden_layers:
            # Quantum layer implementation
            for qubit in range(min(n_qubits, hidden_size)):
                circuit.ry(f"hidden_{layer_idx}_{qubit}", qubit)
                circuit.rz(f"hidden_z_{layer_idx}_{qubit}", qubit)

            # Entangling gates
            for i in range(min(n_qubits - 1, hidden_size - 1)):
                circuit.cnot(i, i + 1)

            layer_idx += 1

        # Output layer
        for qubit in range(min(n_qubits, output_size)):
            circuit.ry(f"output_{qubit}", qubit)

        circuit.name = f"Quantum Neural Network ({input_size}→{hidden_layers}→{output_size})"
        return circuit

    @staticmethod
    def quantum_autoencoder(n_qubits: int, latent_dim: int) -> tuple[QuantumCircuit, QuantumCircuit]:
        """
        Create quantum autoencoder (encoder and decoder).

        Args:
            n_qubits: Number of input qubits
            latent_dim: Dimension of latent space

        Returns:
            Tuple of (encoder_circuit, decoder_circuit)
        """
        # Encoder: n_qubits -> latent_dim
        encoder_qreg = QuantumRegister(n_qubits)
        encoder = QuantumCircuit(encoder_qreg)

        # Encoder layers (compression)
        for layer in range(int(np.log2(n_qubits // latent_dim))):
            layer_qubits = n_qubits // (2 ** layer)
            for i in range(0, layer_qubits, 2):
                if i + 1 < layer_qubits:
                    encoder.ry(f"enc_theta_{layer}_{i}", i)
                    encoder.ry(f"enc_theta_{layer}_{i+1}", i + 1)
                    encoder.cnot(i, i + 1)

        encoder.name = f"Quantum Encoder ({n_qubits}→{latent_dim})"

        # Decoder: latent_dim -> n_qubits
        decoder_qreg = QuantumRegister(n_qubits)
        decoder = QuantumCircuit(decoder_qreg)

        # Decoder layers (expansion) - reverse of encoder
        for layer in range(int(np.log2(n_qubits // latent_dim)) - 1, -1, -1):
            layer_qubits = n_qubits // (2 ** layer)
            for i in range(0, layer_qubits, 2):
                if i + 1 < layer_qubits:
                    decoder.cnot(i, i + 1)
                    decoder.ry(f"dec_theta_{layer}_{i+1}", i + 1)
                    decoder.ry(f"dec_theta_{layer}_{i}", i)

        decoder.name = f"Quantum Decoder ({latent_dim}→{n_qubits})"

        return encoder, decoder

    @staticmethod
    def quantum_gan(generator_qubits: int, discriminator_qubits: int) -> tuple[QuantumCircuit, QuantumCircuit]:
        """
        Create quantum generative adversarial network.

        Args:
            generator_qubits: Number of qubits for generator
            discriminator_qubits: Number of qubits for discriminator

        Returns:
            Tuple of (generator_circuit, discriminator_circuit)
        """
        # Generator: random noise -> data
        gen_qreg = QuantumRegister(generator_qubits)
        generator = QuantumCircuit(gen_qreg)

        # Initialize noise
        for i in range(generator_qubits):
            generator.h(i)

        # Generator layers
        for layer in range(3):  # 3 layers for complexity
            for qubit in range(generator_qubits):
                generator.ry(f"gen_theta_{layer}_{qubit}", qubit)
                generator.rz(f"gen_phi_{layer}_{qubit}", qubit)

            # Entangling layer
            for i in range(generator_qubits - 1):
                generator.cnot(i, i + 1)

        generator.name = f"Quantum Generator ({generator_qubits} qubits)"

        # Discriminator: data -> real/fake classification
        disc_qreg = QuantumRegister(discriminator_qubits)
        disc_creg = ClassicalRegister(1)  # Binary classification
        discriminator = QuantumCircuit(disc_qreg, disc_creg)

        # Discriminator layers
        for layer in range(2):
            for qubit in range(discriminator_qubits):
                discriminator.ry(f"disc_theta_{layer}_{qubit}", qubit)
                discriminator.rz(f"disc_phi_{layer}_{qubit}", qubit)

            # Entangling layer
            for i in range(discriminator_qubits - 1):
                discriminator.cnot(i, i + 1)

        # Output layer - measure first qubit for classification
        discriminator.measure(0, 0)

        discriminator.name = f"Quantum Discriminator ({discriminator_qubits} qubits)"

        return generator, discriminator

    @staticmethod
    def quantum_boltzmann_machine(n_visible: int, n_hidden: int) -> QuantumCircuit:
        """
        Create quantum Boltzmann machine.

        Args:
            n_visible: Number of visible units
            n_hidden: Number of hidden units

        Returns:
            QuantumCircuit implementing quantum Boltzmann machine
        """
        total_qubits = n_visible + n_hidden

        qreg = QuantumRegister(total_qubits)
        circuit = QuantumCircuit(qreg)

        # Initialize in mixed state
        for i in range(total_qubits):
            circuit.h(i)

        # Quantum interactions between visible and hidden units
        for v in range(n_visible):
            for h in range(n_visible, total_qubits):
                # Interaction term
                circuit.rz(f"weight_{v}_{h}", v)
                circuit.cnot(v, h)
                circuit.rz(f"weight_{v}_{h}", h)
                circuit.cnot(v, h)

        # Bias terms
        for i in range(total_qubits):
            circuit.rx(f"bias_{i}", i)

        circuit.name = f"Quantum Boltzmann Machine ({n_visible}v, {n_hidden}h)"
        return circuit

    @staticmethod
    def qsvm_feature_map(data: np.ndarray, entanglement: str = "full") -> QuantumCircuit:
        """
        Create feature map for Quantum Support Vector Machine.

        Args:
            data: Input data features
            entanglement: Type of entanglement ('full', 'linear', 'circular')

        Returns:
            QuantumCircuit implementing QSVM feature map
        """
        n_features = len(data)

        qreg = QuantumRegister(n_features)
        circuit = QuantumCircuit(qreg)

        # First layer: encode data
        for i, feature in enumerate(data):
            circuit.h(i)
            circuit.rz(2 * feature, i)

        # Entangling layer
        if entanglement == "full":
            # All-to-all entanglement
            for i in range(n_features):
                for j in range(i + 1, n_features):
                    circuit.cnot(i, j)
                    circuit.rz(2 * data[i] * data[j], j)
                    circuit.cnot(i, j)

        elif entanglement == "linear":
            # Linear entanglement
            for i in range(n_features - 1):
                circuit.cnot(i, i + 1)
                circuit.rz(2 * data[i] * data[i + 1], i + 1)
                circuit.cnot(i, i + 1)

        elif entanglement == "circular":
            # Circular entanglement
            for i in range(n_features):
                next_i = (i + 1) % n_features
                circuit.cnot(i, next_i)
                circuit.rz(2 * data[i] * data[next_i], next_i)
                circuit.cnot(i, next_i)

        circuit.name = f"QSVM Feature Map ({entanglement} entanglement)"
        return circuit

    @staticmethod
    def quantum_clustering_circuit(data_points: list[np.ndarray], n_clusters: int) -> QuantumCircuit:
        """
        Create quantum clustering circuit.

        Args:
            data_points: List of data points to cluster
            n_clusters: Number of clusters

        Returns:
            QuantumCircuit for quantum clustering
        """
        n_points = len(data_points)
        n_features = len(data_points[0]) if data_points else 0

        # Need qubits for data encoding and cluster assignment
        data_qubits = n_features
        cluster_qubits = int(np.ceil(np.log2(n_clusters)))
        total_qubits = data_qubits + cluster_qubits

        qreg = QuantumRegister(total_qubits)
        creg = ClassicalRegister(cluster_qubits)
        circuit = QuantumCircuit(qreg, creg)

        # Initialize cluster assignment qubits in superposition
        for i in range(data_qubits, total_qubits):
            circuit.h(i)

        # Quantum interference for clustering
        # This is a simplified version - real implementation would be more complex
        for i in range(data_qubits):
            circuit.ry(f"cluster_param_{i}", i)

        # Measure cluster assignment
        for i in range(cluster_qubits):
            circuit.measure(data_qubits + i, i)

        circuit.name = f"Quantum Clustering ({n_points} points, {n_clusters} clusters)"
        return circuit

# Export quantum ML class
__all__ = ["QuantumMachineLearning", "QuantumDataPoint"]
