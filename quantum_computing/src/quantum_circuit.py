"""
Quantum Circuit Construction for Synapse Language

Provides high-level quantum circuit construction with native Python syntax
and seamless integration with multiple quantum backends.
"""

import numpy as np
from typing import List, Dict, Union, Optional, Tuple
from dataclasses import dataclass
import json
from enum import Enum


class QuantumGateType(Enum):
    """Enumeration of quantum gate types."""
    PAULI_X = "X"
    PAULI_Y = "Y" 
    PAULI_Z = "Z"
    HADAMARD = "H"
    CNOT = "CNOT"
    CZ = "CZ"
    SWAP = "SWAP"
    ROTATION_X = "RX"
    ROTATION_Y = "RY"
    ROTATION_Z = "RZ"
    TOFFOLI = "TOFFOLI"
    FREDKIN = "FREDKIN"
    PHASE = "PHASE"
    T = "T"
    S = "S"


@dataclass
class QuantumGate:
    """Represents a quantum gate operation."""
    gate_type: QuantumGateType
    target_qubits: List[int]
    control_qubits: List[int] = None
    parameters: List[float] = None
    label: str = None
    
    def __post_init__(self):
        if self.control_qubits is None:
            self.control_qubits = []
        if self.parameters is None:
            self.parameters = []


class QuantumRegister:
    """Represents a quantum register (collection of qubits)."""
    
    def __init__(self, size: int, name: str = "q"):
        self.size = size
        self.name = name
        self._qubits = list(range(size))
    
    def __getitem__(self, index: Union[int, slice]) -> Union[int, List[int]]:
        """Access qubits by index."""
        if isinstance(index, int):
            if index >= self.size:
                raise IndexError(f"Qubit index {index} out of range for register of size {self.size}")
            return index
        elif isinstance(index, slice):
            return self._qubits[index]
        else:
            raise TypeError("Index must be int or slice")
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self) -> str:
        return f"QuantumRegister('{self.name}', {self.size})"


class ClassicalRegister:
    """Represents a classical register for measurement results."""
    
    def __init__(self, size: int, name: str = "c"):
        self.size = size
        self.name = name
        self._bits = list(range(size))
    
    def __getitem__(self, index: Union[int, slice]) -> Union[int, List[int]]:
        """Access classical bits by index."""
        if isinstance(index, int):
            if index >= self.size:
                raise IndexError(f"Bit index {index} out of range for register of size {self.size}")
            return index
        elif isinstance(index, slice):
            return self._bits[index]
        else:
            raise TypeError("Index must be int or slice")
    
    def __len__(self) -> int:
        return self.size
    
    def __repr__(self) -> str:
        return f"ClassicalRegister('{self.name}', {self.size})"


class QuantumCircuit:
    """
    Main quantum circuit class for Synapse Language.
    
    Provides high-level interface for quantum circuit construction
    with support for various quantum gates and measurements.
    """
    
    def __init__(self, *registers):
        """
        Initialize quantum circuit with registers.
        
        Args:
            *registers: QuantumRegister and ClassicalRegister instances
        """
        self.quantum_registers = []
        self.classical_registers = []
        self.gates = []
        self.measurements = []
        
        # Process registers
        for reg in registers:
            if isinstance(reg, QuantumRegister):
                self.quantum_registers.append(reg)
            elif isinstance(reg, ClassicalRegister):
                self.classical_registers.append(reg)
            else:
                raise TypeError(f"Unsupported register type: {type(reg)}")
        
        # Calculate total qubits and classical bits
        self.num_qubits = sum(reg.size for reg in self.quantum_registers)
        self.num_clbits = sum(reg.size for reg in self.classical_registers)
        
        # Initialize quantum state (for simulation)
        self._quantum_state = None
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize quantum state vector."""
        if self.num_qubits > 0:
            state_size = 2 ** self.num_qubits
            self._quantum_state = np.zeros(state_size, dtype=complex)
            self._quantum_state[0] = 1.0  # |000...0⟩ state
    
    # Single-qubit gates
    def h(self, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply Hadamard gate."""
        gate = QuantumGate(QuantumGateType.HADAMARD, [qubit], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def x(self, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply Pauli-X (NOT) gate."""
        gate = QuantumGate(QuantumGateType.PAULI_X, [qubit], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def y(self, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply Pauli-Y gate."""
        gate = QuantumGate(QuantumGateType.PAULI_Y, [qubit], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def z(self, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply Pauli-Z gate."""
        gate = QuantumGate(QuantumGateType.PAULI_Z, [qubit], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def rx(self, theta: float, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply X-axis rotation gate."""
        gate = QuantumGate(QuantumGateType.ROTATION_X, [qubit], parameters=[theta], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def ry(self, theta: float, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply Y-axis rotation gate."""
        gate = QuantumGate(QuantumGateType.ROTATION_Y, [qubit], parameters=[theta], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def rz(self, theta: float, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply Z-axis rotation gate."""
        gate = QuantumGate(QuantumGateType.ROTATION_Z, [qubit], parameters=[theta], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def s(self, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply S gate (phase gate)."""
        gate = QuantumGate(QuantumGateType.S, [qubit], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def t(self, qubit: int, label: str = None) -> 'QuantumCircuit':
        """Apply T gate (π/8 gate)."""
        gate = QuantumGate(QuantumGateType.T, [qubit], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    # Two-qubit gates
    def cnot(self, control: int, target: int, label: str = None) -> 'QuantumCircuit':
        """Apply CNOT (Controlled-X) gate."""
        gate = QuantumGate(QuantumGateType.CNOT, [target], [control], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def cx(self, control: int, target: int, label: str = None) -> 'QuantumCircuit':
        """Apply CNOT gate (alias)."""
        return self.cnot(control, target, label)
    
    def cz(self, control: int, target: int, label: str = None) -> 'QuantumCircuit':
        """Apply Controlled-Z gate."""
        gate = QuantumGate(QuantumGateType.CZ, [target], [control], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def swap(self, qubit1: int, qubit2: int, label: str = None) -> 'QuantumCircuit':
        """Apply SWAP gate."""
        gate = QuantumGate(QuantumGateType.SWAP, [qubit1, qubit2], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    # Multi-qubit gates
    def toffoli(self, control1: int, control2: int, target: int, label: str = None) -> 'QuantumCircuit':
        """Apply Toffoli (CCX) gate."""
        gate = QuantumGate(QuantumGateType.TOFFOLI, [target], [control1, control2], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    def ccx(self, control1: int, control2: int, target: int, label: str = None) -> 'QuantumCircuit':
        """Apply Toffoli gate (alias)."""
        return self.toffoli(control1, control2, target, label)
    
    def fredkin(self, control: int, target1: int, target2: int, label: str = None) -> 'QuantumCircuit':
        """Apply Fredkin (controlled-SWAP) gate."""
        gate = QuantumGate(QuantumGateType.FREDKIN, [target1, target2], [control], label=label)
        self.gates.append(gate)
        self._apply_gate_simulation(gate)
        return self
    
    # Measurement operations
    def measure(self, qubit: int, clbit: int) -> 'QuantumCircuit':
        """Measure a qubit and store result in classical bit."""
        self.measurements.append((qubit, clbit))
        return self
    
    def measure_all(self, register: ClassicalRegister = None) -> 'QuantumCircuit':
        """Measure all qubits."""
        if register is None and self.classical_registers:
            register = self.classical_registers[0]
        
        if register is None:
            raise ValueError("No classical register available for measurements")
        
        for i in range(min(self.num_qubits, register.size)):
            self.measurements.append((i, i))
        
        return self
    
    # Circuit analysis and properties
    def depth(self) -> int:
        """Calculate circuit depth (number of gate layers)."""
        if not self.gates:
            return 0
        
        # Simple depth calculation - can be optimized
        qubit_last_used = [0] * self.num_qubits
        current_depth = 0
        
        for gate in self.gates:
            all_qubits = gate.target_qubits + gate.control_qubits
            gate_depth = max(qubit_last_used[q] for q in all_qubits) + 1
            
            for qubit in all_qubits:
                qubit_last_used[qubit] = gate_depth
            
            current_depth = max(current_depth, gate_depth)
        
        return current_depth
    
    def width(self) -> int:
        """Get circuit width (number of qubits)."""
        return self.num_qubits
    
    def size(self) -> int:
        """Get number of gates in circuit."""
        return len(self.gates)
    
    def count_ops(self) -> Dict[str, int]:
        """Count operations by gate type."""
        counts = {}
        for gate in self.gates:
            gate_name = gate.gate_type.value
            counts[gate_name] = counts.get(gate_name, 0) + 1
        return counts
    
    # Simulation methods
    def _apply_gate_simulation(self, gate: QuantumGate):
        """Apply gate to quantum state for local simulation."""
        if self._quantum_state is None:
            return
        
        # Simple gate application - can be optimized with sparse matrices
        if gate.gate_type == QuantumGateType.HADAMARD:
            self._apply_hadamard_simulation(gate.target_qubits[0])
        elif gate.gate_type == QuantumGateType.PAULI_X:
            self._apply_pauli_x_simulation(gate.target_qubits[0])
        elif gate.gate_type == QuantumGateType.CNOT:
            self._apply_cnot_simulation(gate.control_qubits[0], gate.target_qubits[0])
        # Add more gate implementations as needed
    
    def _apply_hadamard_simulation(self, qubit: int):
        """Apply Hadamard gate to quantum state."""
        if self._quantum_state is None:
            return
        
        n_qubits = self.num_qubits
        new_state = np.zeros_like(self._quantum_state)
        
        for i in range(2**n_qubits):
            # Check if qubit is 0 or 1
            if (i >> qubit) & 1 == 0:  # Qubit is 0
                j = i | (1 << qubit)  # Set qubit to 1
                new_state[i] += self._quantum_state[i] / np.sqrt(2)
                new_state[j] += self._quantum_state[i] / np.sqrt(2)
            else:  # Qubit is 1
                j = i & ~(1 << qubit)  # Set qubit to 0
                new_state[i] += self._quantum_state[i] / np.sqrt(2)
                new_state[j] -= self._quantum_state[i] / np.sqrt(2)
        
        self._quantum_state = new_state
    
    def _apply_pauli_x_simulation(self, qubit: int):
        """Apply Pauli-X gate to quantum state."""
        if self._quantum_state is None:
            return
        
        n_qubits = self.num_qubits
        new_state = np.zeros_like(self._quantum_state)
        
        for i in range(2**n_qubits):
            j = i ^ (1 << qubit)  # Flip qubit
            new_state[j] = self._quantum_state[i]
        
        self._quantum_state = new_state
    
    def _apply_cnot_simulation(self, control: int, target: int):
        """Apply CNOT gate to quantum state."""
        if self._quantum_state is None:
            return
        
        n_qubits = self.num_qubits
        new_state = np.zeros_like(self._quantum_state)
        
        for i in range(2**n_qubits):
            if (i >> control) & 1 == 1:  # Control is 1
                j = i ^ (1 << target)  # Flip target
                new_state[j] = self._quantum_state[i]
            else:  # Control is 0
                new_state[i] = self._quantum_state[i]
        
        self._quantum_state = new_state
    
    def get_statevector(self) -> np.ndarray:
        """Get current quantum state vector."""
        return self._quantum_state.copy() if self._quantum_state is not None else None
    
    def get_probabilities(self) -> np.ndarray:
        """Get measurement probabilities for all basis states."""
        if self._quantum_state is None:
            return None
        return np.abs(self._quantum_state) ** 2
    
    # Circuit export and serialization
    def to_qasm(self) -> str:
        """Export circuit to OpenQASM format."""
        qasm_lines = [
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            f"qreg q[{self.num_qubits}];",
            f"creg c[{self.num_clbits}];" if self.num_clbits > 0 else ""
        ]
        
        # Add gates
        for gate in self.gates:
            qasm_lines.append(self._gate_to_qasm(gate))
        
        # Add measurements
        for qubit, clbit in self.measurements:
            qasm_lines.append(f"measure q[{qubit}] -> c[{clbit}];")
        
        return "\n".join(filter(None, qasm_lines))
    
    def _gate_to_qasm(self, gate: QuantumGate) -> str:
        """Convert gate to QASM string."""
        if gate.gate_type == QuantumGateType.HADAMARD:
            return f"h q[{gate.target_qubits[0]}];"
        elif gate.gate_type == QuantumGateType.PAULI_X:
            return f"x q[{gate.target_qubits[0]}];"
        elif gate.gate_type == QuantumGateType.PAULI_Y:
            return f"y q[{gate.target_qubits[0]}];"
        elif gate.gate_type == QuantumGateType.PAULI_Z:
            return f"z q[{gate.target_qubits[0]}];"
        elif gate.gate_type == QuantumGateType.CNOT:
            return f"cx q[{gate.control_qubits[0]}],q[{gate.target_qubits[0]}];"
        elif gate.gate_type == QuantumGateType.ROTATION_X:
            return f"rx({gate.parameters[0]}) q[{gate.target_qubits[0]}];"
        elif gate.gate_type == QuantumGateType.ROTATION_Y:
            return f"ry({gate.parameters[0]}) q[{gate.target_qubits[0]}];"
        elif gate.gate_type == QuantumGateType.ROTATION_Z:
            return f"rz({gate.parameters[0]}) q[{gate.target_qubits[0]}];"
        else:
            return f"// Unsupported gate: {gate.gate_type.value}"
    
    def to_dict(self) -> Dict:
        """Export circuit to dictionary format."""
        return {
            'num_qubits': self.num_qubits,
            'num_clbits': self.num_clbits,
            'gates': [
                {
                    'type': gate.gate_type.value,
                    'targets': gate.target_qubits,
                    'controls': gate.control_qubits,
                    'parameters': gate.parameters,
                    'label': gate.label
                }
                for gate in self.gates
            ],
            'measurements': self.measurements
        }
    
    def __repr__(self) -> str:
        """String representation of circuit."""
        return f"QuantumCircuit(qubits={self.num_qubits}, gates={len(self.gates)}, depth={self.depth()})"
    
    def __str__(self) -> str:
        """Detailed string representation."""
        lines = [f"QuantumCircuit with {self.num_qubits} qubits and {len(self.gates)} gates:"]
        
        for i, gate in enumerate(self.gates):
            gate_str = f"  {i+1}. {gate.gate_type.value}"
            if gate.control_qubits:
                gate_str += f" (ctrl: {gate.control_qubits})"
            gate_str += f" -> {gate.target_qubits}"
            if gate.parameters:
                gate_str += f" (params: {gate.parameters})"
            lines.append(gate_str)
        
        if self.measurements:
            lines.append("Measurements:")
            for qubit, clbit in self.measurements:
                lines.append(f"  q[{qubit}] -> c[{clbit}]")
        
        return "\n".join(lines)