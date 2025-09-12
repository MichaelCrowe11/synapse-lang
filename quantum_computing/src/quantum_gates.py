"""
Quantum Gates for Synapse Language

Defines quantum gate implementations and gate matrices for
quantum circuit simulation and hardware backend integration.
"""

import numpy as np
from typing import Dict, Callable, List
import cmath

# Define quantum gate matrices
GATE_MATRICES = {
    # Single-qubit Pauli gates
    'I': np.array([[1, 0], [0, 1]], dtype=complex),          # Identity
    'X': np.array([[0, 1], [1, 0]], dtype=complex),          # Pauli-X (NOT)
    'Y': np.array([[0, -1j], [1j, 0]], dtype=complex),       # Pauli-Y
    'Z': np.array([[1, 0], [0, -1]], dtype=complex),         # Pauli-Z
    
    # Hadamard and phase gates
    'H': np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2),    # Hadamard
    'S': np.array([[1, 0], [0, 1j]], dtype=complex),                 # Phase gate (S)
    'T': np.array([[1, 0], [0, np.exp(1j*np.pi/4)]], dtype=complex), # T gate (π/8)
    
    # Two-qubit gates (4x4 matrices)
    'CNOT': np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0], 
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=complex),
    
    'CZ': np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0], 
        [0, 0, 0, -1]
    ], dtype=complex),
    
    'SWAP': np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ], dtype=complex),
}

def rotation_x(theta: float) -> np.ndarray:
    """Create X-axis rotation gate matrix."""
    cos_half = np.cos(theta / 2)
    sin_half = np.sin(theta / 2)
    return np.array([
        [cos_half, -1j * sin_half],
        [-1j * sin_half, cos_half]
    ], dtype=complex)

def rotation_y(theta: float) -> np.ndarray:
    """Create Y-axis rotation gate matrix."""
    cos_half = np.cos(theta / 2)
    sin_half = np.sin(theta / 2)
    return np.array([
        [cos_half, -sin_half],
        [sin_half, cos_half]
    ], dtype=complex)

def rotation_z(theta: float) -> np.ndarray:
    """Create Z-axis rotation gate matrix."""
    return np.array([
        [np.exp(-1j * theta / 2), 0],
        [0, np.exp(1j * theta / 2)]
    ], dtype=complex)

def phase_gate(phi: float) -> np.ndarray:
    """Create phase gate with arbitrary angle."""
    return np.array([
        [1, 0],
        [0, np.exp(1j * phi)]
    ], dtype=complex)

def u_gate(theta: float, phi: float, lam: float) -> np.ndarray:
    """
    Create universal single-qubit gate U(θ,φ,λ).
    
    U(θ,φ,λ) = |0⟩⟨0| + e^(iλ) |1⟩⟨1| × R_z(φ) × R_y(θ) × R_z(λ)
    """
    cos_half = np.cos(theta / 2)
    sin_half = np.sin(theta / 2)
    
    return np.array([
        [cos_half, -np.exp(1j * lam) * sin_half],
        [np.exp(1j * phi) * sin_half, np.exp(1j * (phi + lam)) * cos_half]
    ], dtype=complex)

def toffoli_gate() -> np.ndarray:
    """Create Toffoli (CCX) gate matrix."""
    return np.array([
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 0]
    ], dtype=complex)

def fredkin_gate() -> np.ndarray:
    """Create Fredkin (CSWAP) gate matrix."""
    return np.array([
        [1, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1]
    ], dtype=complex)

# Convenient gate functions for circuit construction
def H(qubit: int) -> Dict:
    """Hadamard gate constructor."""
    return {'gate': 'H', 'qubits': [qubit], 'matrix': GATE_MATRICES['H']}

def X(qubit: int) -> Dict:
    """Pauli-X gate constructor."""
    return {'gate': 'X', 'qubits': [qubit], 'matrix': GATE_MATRICES['X']}

def Y(qubit: int) -> Dict:
    """Pauli-Y gate constructor.""" 
    return {'gate': 'Y', 'qubits': [qubit], 'matrix': GATE_MATRICES['Y']}

def Z(qubit: int) -> Dict:
    """Pauli-Z gate constructor."""
    return {'gate': 'Z', 'qubits': [qubit], 'matrix': GATE_MATRICES['Z']}

def CNOT(control: int, target: int) -> Dict:
    """CNOT gate constructor."""
    return {
        'gate': 'CNOT',
        'qubits': [control, target],
        'matrix': GATE_MATRICES['CNOT']
    }

def CZ(control: int, target: int) -> Dict:
    """Controlled-Z gate constructor."""
    return {
        'gate': 'CZ', 
        'qubits': [control, target],
        'matrix': GATE_MATRICES['CZ']
    }

def SWAP(qubit1: int, qubit2: int) -> Dict:
    """SWAP gate constructor."""
    return {
        'gate': 'SWAP',
        'qubits': [qubit1, qubit2],
        'matrix': GATE_MATRICES['SWAP']
    }

def Rx(theta: float, qubit: int) -> Dict:
    """X-axis rotation gate constructor."""
    return {
        'gate': 'RX',
        'qubits': [qubit],
        'parameters': [theta],
        'matrix': rotation_x(theta)
    }

def Ry(theta: float, qubit: int) -> Dict:
    """Y-axis rotation gate constructor."""
    return {
        'gate': 'RY',
        'qubits': [qubit],
        'parameters': [theta],
        'matrix': rotation_y(theta)
    }

def Rz(theta: float, qubit: int) -> Dict:
    """Z-axis rotation gate constructor."""
    return {
        'gate': 'RZ',
        'qubits': [qubit],
        'parameters': [theta],
        'matrix': rotation_z(theta)
    }

def Toffoli(control1: int, control2: int, target: int) -> Dict:
    """Toffoli gate constructor."""
    return {
        'gate': 'TOFFOLI',
        'qubits': [control1, control2, target],
        'matrix': toffoli_gate()
    }

def Fredkin(control: int, target1: int, target2: int) -> Dict:
    """Fredkin gate constructor."""
    return {
        'gate': 'FREDKIN',
        'qubits': [control, target1, target2],
        'matrix': fredkin_gate()
    }

# Gate matrix utilities
def get_gate_matrix(gate_name: str, parameters: List[float] = None) -> np.ndarray:
    """Get gate matrix by name."""
    if gate_name in GATE_MATRICES:
        return GATE_MATRICES[gate_name].copy()
    elif gate_name == 'RX' and parameters:
        return rotation_x(parameters[0])
    elif gate_name == 'RY' and parameters:
        return rotation_y(parameters[0])
    elif gate_name == 'RZ' and parameters:
        return rotation_z(parameters[0])
    elif gate_name == 'PHASE' and parameters:
        return phase_gate(parameters[0])
    elif gate_name == 'U' and len(parameters) == 3:
        return u_gate(parameters[0], parameters[1], parameters[2])
    elif gate_name == 'TOFFOLI':
        return toffoli_gate()
    elif gate_name == 'FREDKIN':
        return fredkin_gate()
    else:
        raise ValueError(f"Unknown gate: {gate_name}")

def is_unitary(matrix: np.ndarray, tolerance: float = 1e-10) -> bool:
    """Check if matrix is unitary."""
    n = matrix.shape[0]
    identity = np.eye(n)
    product = matrix @ matrix.conj().T
    return np.allclose(product, identity, atol=tolerance)

def gate_fidelity(gate1: np.ndarray, gate2: np.ndarray) -> float:
    """Calculate fidelity between two gate matrices."""
    trace = np.trace(gate1.conj().T @ gate2)
    n = gate1.shape[0]
    return abs(trace) / n

def decompose_single_qubit_gate(gate: np.ndarray) -> Dict[str, float]:
    """
    Decompose arbitrary single-qubit gate into Euler angles.
    Returns parameters for U(θ,φ,λ) decomposition.
    """
    if gate.shape != (2, 2):
        raise ValueError("Gate must be 2x2 matrix")
    
    # Extract global phase
    det = np.linalg.det(gate)
    global_phase = np.angle(det) / 2
    
    # Remove global phase
    normalized_gate = gate / np.exp(1j * global_phase)
    
    # Extract Euler angles
    theta = 2 * np.arccos(min(1, abs(normalized_gate[0, 0])))
    
    if abs(np.sin(theta/2)) < 1e-10:  # Gate is diagonal
        phi = 0
        lam = np.angle(normalized_gate[1, 1]) - np.angle(normalized_gate[0, 0])
    else:
        phi = np.angle(normalized_gate[1, 0]) - np.angle(normalized_gate[0, 1])
        lam = np.angle(normalized_gate[1, 0]) + np.angle(normalized_gate[0, 1])
    
    return {
        'theta': theta,
        'phi': phi,
        'lambda': lam,
        'global_phase': global_phase
    }

# Export all gate constructors
__all__ = [
    # Basic gates
    'H', 'X', 'Y', 'Z', 'CNOT', 'CZ', 'SWAP',
    # Rotation gates
    'Rx', 'Ry', 'Rz',
    # Multi-qubit gates
    'Toffoli', 'Fredkin',
    # Matrix functions
    'rotation_x', 'rotation_y', 'rotation_z', 'phase_gate', 'u_gate',
    'toffoli_gate', 'fredkin_gate',
    # Utilities
    'get_gate_matrix', 'is_unitary', 'gate_fidelity', 'decompose_single_qubit_gate',
    # Constants
    'GATE_MATRICES'
]