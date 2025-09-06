"""
Quantum Circuit Abstraction Layer for Synapse
Foundation for true quantum computing language leadership
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import cmath
from abc import ABC, abstractmethod

class QuantumGate(Enum):
    """Standard quantum gate types"""
    # Single qubit gates
    I = "I"          # Identity
    X = "X"          # Pauli-X (NOT)
    Y = "Y"          # Pauli-Y  
    Z = "Z"          # Pauli-Z
    H = "H"          # Hadamard
    S = "S"          # Phase gate
    T = "T"          # T gate
    RX = "RX"        # Rotation around X
    RY = "RY"        # Rotation around Y
    RZ = "RZ"        # Rotation around Z
    
    # Two qubit gates
    CNOT = "CNOT"    # Controlled-NOT
    CZ = "CZ"        # Controlled-Z
    SWAP = "SWAP"    # Swap gate
    
    # Three qubit gates
    TOFFOLI = "TOFFOLI"  # Controlled-controlled-NOT
    FREDKIN = "FREDKIN"  # Controlled-SWAP

@dataclass
class QuantumOperation:
    """Represents a quantum gate operation"""
    gate: QuantumGate
    qubits: List[int]
    parameters: List[float] = None
    label: str = ""
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []

class QuantumCircuitBuilder:
    """Advanced quantum circuit builder with optimization"""
    
    def __init__(self, num_qubits: int, name: str = "circuit"):
        self.num_qubits = num_qubits
        self.name = name
        self.operations: List[QuantumOperation] = []
        self.measurements: Dict[int, int] = {}  # qubit -> classical bit
        self.classical_bits = 0
        self.barriers: List[int] = []  # Operation indices where barriers occur
        
    def add_gate(self, gate: QuantumGate, qubits: Union[int, List[int]], 
                 parameters: List[float] = None, label: str = "") -> 'QuantumCircuitBuilder':
        """Add a quantum gate to the circuit"""
        if isinstance(qubits, int):
            qubits = [qubits]
            
        # Validate qubit indices
        for q in qubits:
            if q >= self.num_qubits or q < 0:
                raise ValueError(f"Qubit index {q} out of range [0, {self.num_qubits-1}]")
        
        # Validate gate-qubit compatibility
        self._validate_gate(gate, qubits, parameters)
        
        operation = QuantumOperation(gate, qubits, parameters or [], label)
        self.operations.append(operation)
        return self
    
    def _validate_gate(self, gate: QuantumGate, qubits: List[int], parameters: List[float]):
        """Validate gate operations"""
        single_qubit_gates = {QuantumGate.I, QuantumGate.X, QuantumGate.Y, QuantumGate.Z,
                             QuantumGate.H, QuantumGate.S, QuantumGate.T, 
                             QuantumGate.RX, QuantumGate.RY, QuantumGate.RZ}
        
        two_qubit_gates = {QuantumGate.CNOT, QuantumGate.CZ, QuantumGate.SWAP}
        three_qubit_gates = {QuantumGate.TOFFOLI, QuantumGate.FREDKIN}
        
        if gate in single_qubit_gates and len(qubits) != 1:
            raise ValueError(f"Gate {gate} requires exactly 1 qubit, got {len(qubits)}")
        elif gate in two_qubit_gates and len(qubits) != 2:
            raise ValueError(f"Gate {gate} requires exactly 2 qubits, got {len(qubits)}")
        elif gate in three_qubit_gates and len(qubits) != 3:
            raise ValueError(f"Gate {gate} requires exactly 3 qubits, got {len(qubits)}")
            
        # Validate parameters for parameterized gates
        rotation_gates = {QuantumGate.RX, QuantumGate.RY, QuantumGate.RZ}
        if gate in rotation_gates:
            if not parameters or len(parameters) != 1:
                raise ValueError(f"Rotation gate {gate} requires exactly 1 parameter")
    
    # Convenience methods for common gates
    def x(self, qubit: int) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.X, qubit)
    
    def y(self, qubit: int) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.Y, qubit)
    
    def z(self, qubit: int) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.Z, qubit)
    
    def h(self, qubit: int) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.H, qubit)
    
    def cnot(self, control: int, target: int) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.CNOT, [control, target])
    
    def rx(self, qubit: int, angle: float) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.RX, qubit, [angle])
    
    def ry(self, qubit: int, angle: float) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.RY, qubit, [angle])
    
    def rz(self, qubit: int, angle: float) -> 'QuantumCircuitBuilder':
        return self.add_gate(QuantumGate.RZ, qubit, [angle])
    
    def measure(self, qubit: int, classical_bit: int = None) -> 'QuantumCircuitBuilder':
        """Add measurement operation"""
        if classical_bit is None:
            classical_bit = self.classical_bits
            self.classical_bits += 1
        
        self.measurements[qubit] = classical_bit
        return self
    
    def measure_all(self) -> 'QuantumCircuitBuilder':
        """Measure all qubits"""
        for i in range(self.num_qubits):
            self.measure(i)
        return self
    
    def barrier(self) -> 'QuantumCircuitBuilder':
        """Add a barrier (prevents gate reordering)"""
        self.barriers.append(len(self.operations))
        return self
    
    def depth(self) -> int:
        """Calculate circuit depth"""
        # Simplified depth calculation
        qubit_times = [0] * self.num_qubits
        
        for op in self.operations:
            max_time = max(qubit_times[q] for q in op.qubits)
            for q in op.qubits:
                qubit_times[q] = max_time + 1
        
        return max(qubit_times)
    
    def count_gates(self) -> Dict[QuantumGate, int]:
        """Count gates by type"""
        counts = {}
        for op in self.operations:
            counts[op.gate] = counts.get(op.gate, 0) + 1
        return counts

class QuantumBackend(ABC):
    """Abstract base class for quantum backends"""
    
    @abstractmethod
    def execute(self, circuit: QuantumCircuitBuilder, shots: int = 1000) -> Dict[str, int]:
        """Execute a quantum circuit"""
        pass
    
    @abstractmethod
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend information"""
        pass

class SimulatorBackend(QuantumBackend):
    """Quantum simulator backend"""
    
    def __init__(self, name: str = "synapse_simulator"):
        self.name = name
        self.max_qubits = 32  # Practical limit for state vector simulation
    
    def execute(self, circuit: QuantumCircuitBuilder, shots: int = 1000) -> Dict[str, int]:
        """Execute circuit on quantum simulator"""
        if circuit.num_qubits > self.max_qubits:
            raise ValueError(f"Circuit has {circuit.num_qubits} qubits, max supported: {self.max_qubits}")
        
        # Initialize state vector
        state = np.zeros(2**circuit.num_qubits, dtype=complex)
        state[0] = 1.0  # |0...0⟩ state
        
        # Apply gates sequentially
        for op in circuit.operations:
            state = self._apply_gate(state, op, circuit.num_qubits)
        
        # Simulate measurements
        results = {}
        for _ in range(shots):
            # Calculate measurement probabilities
            probabilities = np.abs(state)**2
            
            # Sample outcome
            outcome = np.random.choice(len(probabilities), p=probabilities)
            
            # Convert to bit string
            bit_string = format(outcome, f'0{circuit.num_qubits}b')
            results[bit_string] = results.get(bit_string, 0) + 1
        
        return results
    
    def _apply_gate(self, state: np.ndarray, op: QuantumOperation, num_qubits: int) -> np.ndarray:
        """Apply quantum gate to state vector"""
        # Single qubit gates
        if op.gate == QuantumGate.I:
            return state  # Identity gate
        elif op.gate == QuantumGate.X:
            return self._apply_pauli_x(state, op.qubits[0], num_qubits)
        elif op.gate == QuantumGate.Y:
            return self._apply_pauli_y(state, op.qubits[0], num_qubits)
        elif op.gate == QuantumGate.Z:
            return self._apply_pauli_z(state, op.qubits[0], num_qubits)
        elif op.gate == QuantumGate.H:
            return self._apply_hadamard(state, op.qubits[0], num_qubits)
        elif op.gate == QuantumGate.S:
            return self._apply_phase_gate(state, op.qubits[0], num_qubits, np.pi/2)
        elif op.gate == QuantumGate.T:
            return self._apply_phase_gate(state, op.qubits[0], num_qubits, np.pi/4)
        elif op.gate == QuantumGate.RX:
            return self._apply_rotation_x(state, op.qubits[0], num_qubits, op.parameters[0])
        elif op.gate == QuantumGate.RY:
            return self._apply_rotation_y(state, op.qubits[0], num_qubits, op.parameters[0])
        elif op.gate == QuantumGate.RZ:
            return self._apply_rotation_z(state, op.qubits[0], num_qubits, op.parameters[0])
        # Two qubit gates
        elif op.gate == QuantumGate.CNOT:
            return self._apply_cnot(state, op.qubits[0], op.qubits[1], num_qubits)
        elif op.gate == QuantumGate.CZ:
            return self._apply_cz(state, op.qubits[0], op.qubits[1], num_qubits)
        elif op.gate == QuantumGate.SWAP:
            return self._apply_swap(state, op.qubits[0], op.qubits[1], num_qubits)
        # Three qubit gates
        elif op.gate == QuantumGate.TOFFOLI:
            return self._apply_toffoli(state, op.qubits[0], op.qubits[1], op.qubits[2], num_qubits)
        elif op.gate == QuantumGate.FREDKIN:
            return self._apply_fredkin(state, op.qubits[0], op.qubits[1], op.qubits[2], num_qubits)
        
        raise ValueError(f"Unsupported gate: {op.gate}")
    
    def _apply_pauli_x(self, state: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
        """Apply Pauli-X gate"""
        new_state = np.copy(state)
        mask = 1 << (num_qubits - 1 - qubit)
        
        for i in range(len(state)):
            j = i ^ mask  # Flip the qubit
            new_state[i] = state[j]
        
        return new_state
    
    def _apply_hadamard(self, state: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
        """Apply Hadamard gate"""
        new_state = np.zeros_like(state)
        mask = 1 << (num_qubits - 1 - qubit)
        
        for i in range(len(state)):
            if i & mask:  # Qubit is |1⟩
                j = i ^ mask  # Corresponding |0⟩ state
                new_state[i] = (state[j] - state[i]) / np.sqrt(2)
                new_state[j] = (state[j] + state[i]) / np.sqrt(2)
            elif not new_state[i]:  # Haven't processed this |0⟩ state yet
                j = i ^ mask  # Corresponding |1⟩ state
                new_state[i] = (state[i] + state[j]) / np.sqrt(2)
                new_state[j] = (state[i] - state[j]) / np.sqrt(2)
        
        return new_state
    
    def _apply_cnot(self, state: np.ndarray, control: int, target: int, num_qubits: int) -> np.ndarray:
        """Apply CNOT gate"""
        new_state = np.copy(state)
        control_mask = 1 << (num_qubits - 1 - control)
        target_mask = 1 << (num_qubits - 1 - target)
        
        for i in range(len(state)):
            if i & control_mask:  # Control qubit is |1⟩
                j = i ^ target_mask  # Flip target qubit
                new_state[i] = state[j]
        
        return new_state
    
    def _apply_pauli_y(self, state: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
        """Apply Pauli-Y gate"""
        new_state = np.zeros_like(state)
        mask = 1 << (num_qubits - 1 - qubit)
        
        for i in range(len(state)):
            j = i ^ mask  # Flip the qubit
            if i & mask:  # Qubit is |1⟩
                new_state[i] = -1j * state[j]
            else:  # Qubit is |0⟩
                new_state[i] = 1j * state[j]
        
        return new_state
    
    def _apply_pauli_z(self, state: np.ndarray, qubit: int, num_qubits: int) -> np.ndarray:
        """Apply Pauli-Z gate"""
        new_state = np.copy(state)
        mask = 1 << (num_qubits - 1 - qubit)
        
        for i in range(len(state)):
            if i & mask:  # Qubit is |1⟩
                new_state[i] = -state[i]
        
        return new_state
    
    def _apply_phase_gate(self, state: np.ndarray, qubit: int, num_qubits: int, phase: float) -> np.ndarray:
        """Apply phase gate (S or T gate)"""
        new_state = np.copy(state)
        mask = 1 << (num_qubits - 1 - qubit)
        phase_factor = np.exp(1j * phase)
        
        for i in range(len(state)):
            if i & mask:  # Qubit is |1⟩
                new_state[i] = state[i] * phase_factor
        
        return new_state
    
    def _apply_rotation_x(self, state: np.ndarray, qubit: int, num_qubits: int, angle: float) -> np.ndarray:
        """Apply RX rotation gate"""
        new_state = np.zeros_like(state)
        mask = 1 << (num_qubits - 1 - qubit)
        cos_half = np.cos(angle / 2)
        sin_half = np.sin(angle / 2)
        
        for i in range(len(state)):
            j = i ^ mask  # Flipped qubit index
            if i & mask:  # Qubit is |1⟩
                new_state[i] = cos_half * state[i] - 1j * sin_half * state[j]
            else:  # Qubit is |0⟩
                new_state[i] = cos_half * state[i] - 1j * sin_half * state[j]
        
        return new_state
    
    def _apply_rotation_y(self, state: np.ndarray, qubit: int, num_qubits: int, angle: float) -> np.ndarray:
        """Apply RY rotation gate"""
        new_state = np.zeros_like(state)
        mask = 1 << (num_qubits - 1 - qubit)
        cos_half = np.cos(angle / 2)
        sin_half = np.sin(angle / 2)
        
        for i in range(len(state)):
            j = i ^ mask  # Flipped qubit index
            if i & mask:  # Qubit is |1⟩
                new_state[i] = cos_half * state[i] + sin_half * state[j]
            else:  # Qubit is |0⟩
                new_state[i] = cos_half * state[i] - sin_half * state[j]
        
        return new_state
    
    def _apply_rotation_z(self, state: np.ndarray, qubit: int, num_qubits: int, angle: float) -> np.ndarray:
        """Apply RZ rotation gate"""
        new_state = np.copy(state)
        mask = 1 << (num_qubits - 1 - qubit)
        
        for i in range(len(state)):
            if i & mask:  # Qubit is |1⟩
                new_state[i] = state[i] * np.exp(1j * angle / 2)
            else:  # Qubit is |0⟩
                new_state[i] = state[i] * np.exp(-1j * angle / 2)
        
        return new_state
    
    def _apply_cz(self, state: np.ndarray, control: int, target: int, num_qubits: int) -> np.ndarray:
        """Apply CZ (Controlled-Z) gate"""
        new_state = np.copy(state)
        control_mask = 1 << (num_qubits - 1 - control)
        target_mask = 1 << (num_qubits - 1 - target)
        
        for i in range(len(state)):
            if (i & control_mask) and (i & target_mask):  # Both qubits are |1⟩
                new_state[i] = -state[i]
        
        return new_state
    
    def _apply_swap(self, state: np.ndarray, qubit1: int, qubit2: int, num_qubits: int) -> np.ndarray:
        """Apply SWAP gate"""
        new_state = np.copy(state)
        mask1 = 1 << (num_qubits - 1 - qubit1)
        mask2 = 1 << (num_qubits - 1 - qubit2)
        
        for i in range(len(state)):
            bit1 = bool(i & mask1)
            bit2 = bool(i & mask2)
            if bit1 != bit2:  # Qubits have different values
                j = i ^ mask1 ^ mask2  # Swap the bits
                new_state[i] = state[j]
        
        return new_state
    
    def _apply_toffoli(self, state: np.ndarray, control1: int, control2: int, target: int, num_qubits: int) -> np.ndarray:
        """Apply Toffoli (CCNOT) gate"""
        new_state = np.copy(state)
        control1_mask = 1 << (num_qubits - 1 - control1)
        control2_mask = 1 << (num_qubits - 1 - control2)
        target_mask = 1 << (num_qubits - 1 - target)
        
        for i in range(len(state)):
            if (i & control1_mask) and (i & control2_mask):  # Both controls are |1⟩
                j = i ^ target_mask  # Flip target qubit
                new_state[i] = state[j]
        
        return new_state
    
    def _apply_fredkin(self, state: np.ndarray, control: int, target1: int, target2: int, num_qubits: int) -> np.ndarray:
        """Apply Fredkin (CSWAP) gate"""
        new_state = np.copy(state)
        control_mask = 1 << (num_qubits - 1 - control)
        target1_mask = 1 << (num_qubits - 1 - target1)
        target2_mask = 1 << (num_qubits - 1 - target2)
        
        for i in range(len(state)):
            if i & control_mask:  # Control is |1⟩
                bit1 = bool(i & target1_mask)
                bit2 = bool(i & target2_mask)
                if bit1 != bit2:  # Targets have different values
                    j = i ^ target1_mask ^ target2_mask  # Swap the target bits
                    new_state[i] = state[j]
        
        return new_state
    
    def get_backend_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": "simulator",
            "max_qubits": self.max_qubits,
            "max_shots": 1000000,
            "gates": list(QuantumGate),
            "noise_model": None
        }

# Quantum algorithm building blocks
class QuantumAlgorithms:
    """Collection of common quantum algorithms"""
    
    @staticmethod
    def quantum_fourier_transform(circuit: QuantumCircuitBuilder, qubits: List[int]) -> QuantumCircuitBuilder:
        """Add Quantum Fourier Transform to circuit"""
        n = len(qubits)
        
        for i in range(n):
            circuit.h(qubits[i])
            for j in range(i + 1, n):
                angle = np.pi / (2 ** (j - i))
                # Controlled phase rotation (simplified as RZ for demo)
                circuit.rz(qubits[j], angle)
        
        # Reverse the order (swap gates)
        for i in range(n // 2):
            # In practice, you'd add SWAP gates here
            pass
        
        return circuit
    
    @staticmethod
    def grover_operator(circuit: QuantumCircuitBuilder, qubits: List[int], oracle_qubits: List[int]) -> QuantumCircuitBuilder:
        """Add Grover operator (oracle + diffusion)"""
        # Oracle (placeholder - would be problem-specific)
        for q in oracle_qubits:
            circuit.z(q)
        
        # Diffusion operator
        for q in qubits:
            circuit.h(q)
            circuit.x(q)
        
        # Multi-controlled Z (simplified)
        if len(qubits) > 1:
            circuit.z(qubits[-1])  # Placeholder
        
        for q in qubits:
            circuit.x(q)
            circuit.h(q)
        
        return circuit

# Example usage and factory functions
def create_bell_state() -> QuantumCircuitBuilder:
    """Create a Bell state (EPR pair)"""
    circuit = QuantumCircuitBuilder(2, "bell_state")
    circuit.h(0).cnot(0, 1).measure_all()
    return circuit

def create_ghz_state(n_qubits: int) -> QuantumCircuitBuilder:
    """Create a GHZ state"""
    circuit = QuantumCircuitBuilder(n_qubits, f"ghz_{n_qubits}")
    circuit.h(0)
    for i in range(1, n_qubits):
        circuit.cnot(0, i)
    circuit.measure_all()
    return circuit
