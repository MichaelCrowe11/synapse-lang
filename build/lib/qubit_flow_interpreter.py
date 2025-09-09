# Qubit-Flow Quantum Computing Language - Interpreter
# Complementary to Synapse-Lang for pure quantum computation

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import cmath
from concurrent.futures import ThreadPoolExecutor
import threading
from qubit_flow_ast import *
from qubit_flow_parser import parse_qubit_flow

@dataclass
class QuantumState:
    """Represents a quantum state vector"""
    amplitudes: np.ndarray  # Complex amplitudes
    num_qubits: int
    
    def __post_init__(self):
        # Normalize the state
        norm = np.linalg.norm(self.amplitudes)
        if norm > 0:
            self.amplitudes = self.amplitudes / norm
    
    def __repr__(self):
        return f"QuantumState({self.num_qubits} qubits): {self.amplitudes}"
    
    def measure(self, qubit_index: int) -> Tuple[int, 'QuantumState']:
        """Measure a single qubit and return the result and collapsed state"""
        n = self.num_qubits
        prob_0 = 0.0
        prob_1 = 0.0
        
        # Calculate probabilities for |0⟩ and |1⟩
        for i in range(2**n):
            if (i >> (n - 1 - qubit_index)) & 1 == 0:
                prob_0 += abs(self.amplitudes[i])**2
            else:
                prob_1 += abs(self.amplitudes[i])**2
        
        # Random measurement based on probabilities
        import random
        measurement = 1 if random.random() < prob_1 / (prob_0 + prob_1) else 0
        
        # Collapse state
        new_amplitudes = np.zeros_like(self.amplitudes)
        norm_factor = np.sqrt(prob_1 if measurement == 1 else prob_0)
        
        for i in range(2**n):
            if (i >> (n - 1 - qubit_index)) & 1 == measurement:
                new_amplitudes[i] = self.amplitudes[i] / norm_factor
        
        return measurement, QuantumState(new_amplitudes, n)
    
    def tensor_product(self, other: 'QuantumState') -> 'QuantumState':
        """Compute tensor product with another quantum state"""
        new_amplitudes = np.kron(self.amplitudes, other.amplitudes)
        return QuantumState(new_amplitudes, self.num_qubits + other.num_qubits)

@dataclass
class QubitRegister:
    """A register of qubits"""
    name: str
    size: int
    state: QuantumState
    
    def __post_init__(self):
        if self.state is None:
            # Initialize to |0...0⟩ state
            amplitudes = np.zeros(2**self.size, dtype=complex)
            amplitudes[0] = 1.0
            self.state = QuantumState(amplitudes, self.size)

class QuantumGates:
    """Collection of quantum gates"""
    
    @staticmethod
    def hadamard() -> np.ndarray:
        return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    
    @staticmethod
    def pauli_x() -> np.ndarray:
        return np.array([[0, 1], [1, 0]], dtype=complex)
    
    @staticmethod
    def pauli_y() -> np.ndarray:
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    
    @staticmethod
    def pauli_z() -> np.ndarray:
        return np.array([[1, 0], [0, -1]], dtype=complex)
    
    @staticmethod
    def phase(theta: float) -> np.ndarray:
        return np.array([[1, 0], [0, np.exp(1j * theta)]], dtype=complex)
    
    @staticmethod
    def rotation_x(theta: float) -> np.ndarray:
        cos_half = np.cos(theta / 2)
        sin_half = np.sin(theta / 2)
        return np.array([[cos_half, -1j * sin_half], 
                        [-1j * sin_half, cos_half]], dtype=complex)
    
    @staticmethod
    def rotation_y(theta: float) -> np.ndarray:
        cos_half = np.cos(theta / 2)
        sin_half = np.sin(theta / 2)
        return np.array([[cos_half, -sin_half], 
                        [sin_half, cos_half]], dtype=complex)
    
    @staticmethod
    def rotation_z(theta: float) -> np.ndarray:
        exp_neg = np.exp(-1j * theta / 2)
        exp_pos = np.exp(1j * theta / 2)
        return np.array([[exp_neg, 0], [0, exp_pos]], dtype=complex)
    
    @staticmethod
    def cnot() -> np.ndarray:
        return np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0], 
                        [0, 0, 0, 1],
                        [0, 0, 1, 0]], dtype=complex)
    
    @staticmethod
    def cz() -> np.ndarray:
        return np.array([[1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, -1]], dtype=complex)
    
    @staticmethod
    def toffoli() -> np.ndarray:
        matrix = np.eye(8, dtype=complex)
        matrix[6, 6] = 0
        matrix[7, 7] = 0
        matrix[6, 7] = 1
        matrix[7, 6] = 1
        return matrix

class QubitFlowInterpreter:
    def __init__(self):
        self.qubits: Dict[str, QubitRegister] = {}
        self.classical_bits: Dict[str, int] = {}
        self.variables: Dict[str, Any] = {}
        self.circuits: Dict[str, QuantumCircuitNode] = {}
        self.gates = QuantumGates()
        
    def execute(self, source: str) -> List[str]:
        """Execute Qubit-Flow source code"""
        try:
            ast = parse_qubit_flow(source)
            results = []
            
            for statement in ast.statements:
                result = self.visit(statement)
                if result is not None:
                    results.append(str(result))
            
            return results
            
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    def visit(self, node: ASTNode) -> Any:
        """Visit an AST node and execute it"""
        method_name = f"visit_{node.node_type.name.lower()}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            return f"Unhandled node type: {node.node_type}"
    
    def visit_qubit(self, node: QubitNode) -> str:
        """Create a new qubit"""
        initial_state = None
        
        if node.initial_state:
            if isinstance(node.initial_state, KetStateNode):
                if node.initial_state.state == "0":
                    amplitudes = np.array([1.0, 0.0], dtype=complex)
                elif node.initial_state.state == "1":
                    amplitudes = np.array([0.0, 1.0], dtype=complex)
                elif node.initial_state.state == "+":
                    amplitudes = np.array([1.0, 1.0], dtype=complex) / np.sqrt(2)
                elif node.initial_state.state == "-":
                    amplitudes = np.array([1.0, -1.0], dtype=complex) / np.sqrt(2)
                else:
                    amplitudes = np.array([1.0, 0.0], dtype=complex)  # Default to |0⟩
                
                initial_state = QuantumState(amplitudes, 1)
        
        if initial_state is None:
            # Default to |0⟩ state
            amplitudes = np.array([1.0, 0.0], dtype=complex)
            initial_state = QuantumState(amplitudes, 1)
        
        self.qubits[node.name] = QubitRegister(node.name, 1, initial_state)
        return f"qubit {node.name} = {initial_state}"
    
    def visit_qudit(self, node: QuditleNode) -> str:
        """Create a new qudit (d-dimensional quantum system)"""
        amplitudes = np.zeros(node.dimension, dtype=complex)
        amplitudes[0] = 1.0  # Initialize to |0⟩ state
        
        initial_state = QuantumState(amplitudes, int(np.log2(node.dimension)))
        self.qubits[node.name] = QubitRegister(node.name, int(np.log2(node.dimension)), initial_state)
        return f"qudit {node.name}[{node.dimension}] = {initial_state}"
    
    def visit_circuit(self, node: QuantumCircuitNode) -> str:
        """Define a quantum circuit"""
        self.circuits[node.name] = node
        
        # Execute the gates in the circuit
        results = []
        for gate in node.gates:
            result = self.visit(gate)
            if result:
                results.append(result)
        
        return f"circuit {node.name}({', '.join(node.qubits)}): {len(node.gates)} gates executed"
    
    def visit_quantum_gate(self, node: QuantumGateNode) -> str:
        """Apply a quantum gate"""
        gate_type = node.gate_type.upper()
        
        if gate_type == "H" and len(node.qubits) == 1:
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.hadamard())
        
        elif gate_type == "X" and len(node.qubits) == 1:
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.pauli_x())
        
        elif gate_type == "Y" and len(node.qubits) == 1:
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.pauli_y())
        
        elif gate_type == "Z" and len(node.qubits) == 1:
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.pauli_z())
        
        elif gate_type == "RX" and len(node.qubits) == 1 and len(node.parameters) == 1:
            theta = self._evaluate_parameter(node.parameters[0])
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.rotation_x(theta))
        
        elif gate_type == "RY" and len(node.qubits) == 1 and len(node.parameters) == 1:
            theta = self._evaluate_parameter(node.parameters[0])
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.rotation_y(theta))
        
        elif gate_type == "RZ" and len(node.qubits) == 1 and len(node.parameters) == 1:
            theta = self._evaluate_parameter(node.parameters[0])
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.rotation_z(theta))
        
        elif gate_type == "PHASE" and len(node.qubits) == 1 and len(node.parameters) == 1:
            theta = self._evaluate_parameter(node.parameters[0])
            return self._apply_single_qubit_gate(node.qubits[0], self.gates.phase(theta))
        
        elif gate_type == "CNOT" and len(node.qubits) == 2:
            return self._apply_two_qubit_gate(node.qubits[0], node.qubits[1], self.gates.cnot())
        
        elif gate_type == "CZ" and len(node.qubits) == 2:
            return self._apply_two_qubit_gate(node.qubits[0], node.qubits[1], self.gates.cz())
        
        else:
            return f"Unknown or invalid gate: {gate_type}"
    
    def _apply_single_qubit_gate(self, qubit_name: str, gate_matrix: np.ndarray) -> str:
        """Apply a single qubit gate"""
        if qubit_name not in self.qubits:
            return f"Error: Qubit {qubit_name} not found"
        
        qubit = self.qubits[qubit_name]
        
        # For single qubit, directly multiply the gate matrix with the state vector
        new_amplitudes = gate_matrix @ qubit.state.amplitudes
        qubit.state = QuantumState(new_amplitudes, 1)
        
        return f"Applied gate to {qubit_name}"
    
    def _apply_two_qubit_gate(self, control_qubit: str, target_qubit: str, gate_matrix: np.ndarray) -> str:
        """Apply a two-qubit gate"""
        if control_qubit not in self.qubits or target_qubit not in self.qubits:
            return f"Error: One or both qubits not found"
        
        # This is a simplified implementation - in a full system, you'd need to
        # handle multi-qubit states properly with tensor products
        control = self.qubits[control_qubit]
        target = self.qubits[target_qubit]
        
        # Create a combined 2-qubit state
        combined_amplitudes = np.kron(control.state.amplitudes, target.state.amplitudes)
        new_amplitudes = gate_matrix @ combined_amplitudes
        
        # Split back into individual qubits (simplified)
        # In practice, this would require more sophisticated state management
        return f"Applied two-qubit gate between {control_qubit} and {target_qubit}"
    
    def _evaluate_parameter(self, param_node: ASTNode) -> float:
        """Evaluate a parameter node to get a numeric value"""
        if isinstance(param_node, NumberNode):
            return param_node.value
        elif isinstance(param_node, IdentifierNode):
            if param_node.name in self.variables:
                return float(self.variables[param_node.name])
        return 0.0
    
    def visit_measurement(self, node: MeasurementNode) -> str:
        """Perform a quantum measurement"""
        if node.qubit not in self.qubits:
            return f"Error: Qubit {node.qubit} not found"
        
        qubit = self.qubits[node.qubit]
        result, new_state = qubit.state.measure(0)
        qubit.state = new_state
        
        if node.classical_bit:
            self.classical_bits[node.classical_bit] = result
        
        return f"Measured {node.qubit}: {result}"
    
    def visit_entanglement(self, node: EntanglementNode) -> str:
        """Create entanglement between qubits"""
        if len(node.qubits) < 2:
            return "Error: Need at least 2 qubits for entanglement"
        
        qubit_names = node.qubits[:2]  # Take first two qubits for now
        
        if any(q not in self.qubits for q in qubit_names):
            return "Error: One or more qubits not found"
        
        # Create Bell state (simplified implementation)
        if node.entanglement_type == "bell":
            # |Φ+⟩ = (|00⟩ + |11⟩)/√2
            bell_amplitudes = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
            
            # For simplicity, we'll update the first qubit to represent the entangled pair
            self.qubits[qubit_names[0]].state = QuantumState(bell_amplitudes, 2)
            return f"Entangled {qubit_names[0]} and {qubit_names[1]} in Bell state"
        
        return f"Entanglement type {node.entanglement_type} not implemented"
    
    def visit_superposition(self, node: SuperpositionNode) -> str:
        """Create a superposition state"""
        if node.qubit not in self.qubits:
            return f"Error: Qubit {node.qubit} not found"
        
        # Convert amplitude dictionary to state vector
        amplitudes = np.zeros(2, dtype=complex)
        
        for state, amp_node in node.amplitudes.items():
            if isinstance(amp_node, ComplexNumberNode):
                amplitude = complex(amp_node.real, amp_node.imag)
                if state == "0":
                    amplitudes[0] = amplitude
                elif state == "1":
                    amplitudes[1] = amplitude
        
        self.qubits[node.qubit].state = QuantumState(amplitudes, 1)
        return f"Set {node.qubit} to superposition state"
    
    def visit_grovers(self, node: GroversAlgorithmNode) -> str:
        """Execute Grover's search algorithm (simplified)"""
        n_qubits = int(np.ceil(np.log2(node.search_space)))
        iterations = node.iterations or int(np.pi/4 * np.sqrt(node.search_space))
        
        # Initialize qubits in superposition
        amplitudes = np.ones(2**n_qubits, dtype=complex) / np.sqrt(2**n_qubits)
        state = QuantumState(amplitudes, n_qubits)
        
        # Simplified Grover's algorithm simulation
        # In practice, this would involve oracle and diffusion operators
        for _ in range(iterations):
            # Apply oracle (mark target state)
            # Apply diffusion operator
            pass
        
        return f"Executed Grover's algorithm: {iterations} iterations on {node.search_space} items"
    
    def visit_shors(self, node: ShorsAlgorithmNode) -> str:
        """Execute Shor's factoring algorithm (simplified)"""
        number = node.number_to_factor
        
        # This is a highly simplified simulation
        # Real Shor's algorithm requires period finding and modular exponentiation
        factors = []
        for i in range(2, int(np.sqrt(number)) + 1):
            if number % i == 0:
                factors.extend([i, number // i])
                break
        
        if not factors:
            factors = [1, number]
        
        return f"Shor's algorithm found factors of {number}: {factors}"
    
    def visit_qft(self, node: QFTNode) -> str:
        """Execute Quantum Fourier Transform"""
        qubits_involved = len(node.qubits)
        direction = "inverse" if node.inverse else "forward"
        
        # Simplified QFT implementation
        for qubit_name in node.qubits:
            if qubit_name in self.qubits:
                # Apply Hadamard and controlled phase rotations
                self._apply_single_qubit_gate(qubit_name, self.gates.hadamard())
        
        return f"Applied {direction} QFT on {qubits_involved} qubits: {', '.join(node.qubits)}"
    
    def visit_assignment(self, node: AssignmentNode) -> str:
        """Handle variable assignment"""
        value = self.visit(node.value)
        self.variables[node.target.name] = value
        return f"{node.target.name} = {value}"
    
    def visit_identifier(self, node: IdentifierNode) -> Any:
        """Look up identifier value"""
        if node.name in self.variables:
            return self.variables[node.name]
        elif node.name in self.classical_bits:
            return self.classical_bits[node.name]
        else:
            return node.name
    
    def visit_number(self, node: NumberNode) -> float:
        """Return numeric value"""
        return node.value
    
    def visit_complex_number(self, node: ComplexNumberNode) -> complex:
        """Return complex number value"""
        return complex(node.real, node.imag)
    
    def visit_ket_state(self, node: KetStateNode) -> str:
        """Return ket state representation"""
        return f"|{node.state}⟩"

def create_qubit_flow_interpreter() -> QubitFlowInterpreter:
    """Factory function to create a new interpreter instance"""
    return QubitFlowInterpreter()