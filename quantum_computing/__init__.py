"""
Synapse Language - Quantum Computing Module
Advanced quantum circuit construction and simulation

This module provides:
- Quantum circuit construction with native syntax
- Hardware backend integrations (IBM, Google, AWS)
- Quantum algorithm implementations
- Error correction and noise modeling
- Quantum machine learning primitives
"""

from .src.quantum_algorithms import QuantumAlgorithms
from .src.quantum_backends import GoogleBackend, IBMBackend, LocalSimulator
from .src.quantum_circuit import ClassicalRegister, QuantumCircuit, QuantumRegister
from .src.quantum_gates import *
from .src.quantum_ml import QuantumMachineLearning

__version__ = "3.0.0"
__author__ = "Synapse Language Team"

# Export main classes
__all__ = [
    # Core circuit construction
    "QuantumCircuit",
    "QuantumRegister",
    "ClassicalRegister",

    # Quantum gates
    "H", "X", "Y", "Z",           # Pauli gates
    "CNOT", "CZ", "SWAP",         # Two-qubit gates
    "Rx", "Ry", "Rz",            # Rotation gates
    "Toffoli", "Fredkin",         # Multi-qubit gates

    # Backends
    "IBMBackend",
    "GoogleBackend",
    "LocalSimulator",

    # Algorithms
    "QuantumAlgorithms",

    # Quantum ML
    "QuantumMachineLearning"
]

# Quantum computing constants
QUANTUM_BACKENDS = {
    "local": LocalSimulator,
    "ibm": IBMBackend,
    "google": GoogleBackend
}

def create_circuit(num_qubits: int, num_classical: int = None) -> QuantumCircuit:
    """
    Convenient function to create a quantum circuit.

    Args:
        num_qubits: Number of quantum bits
        num_classical: Number of classical bits (default: same as qubits)

    Returns:
        QuantumCircuit instance
    """
    if num_classical is None:
        num_classical = num_qubits

    qreg = QuantumRegister(num_qubits, "q")
    creg = ClassicalRegister(num_classical, "c")

    return QuantumCircuit(qreg, creg)
