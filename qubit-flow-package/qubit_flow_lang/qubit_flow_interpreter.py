# Qubit-Flow Quantum Computing Language - Interpreter
# Complementary to Synapse-Lang for pure quantum computation

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np

from .qubit_flow_ast import *
from .qubit_flow_parser import parse_qubit_flow


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

    def measure(self, qubit_index: int) -> Tuple[int, "QuantumState"]:
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

    def tensor_product(self, other: "QuantumState") -> "QuantumState":
        """Compute tensor product with another quantum state"""
        new_amplitudes = np.kron(self.amplitudes, other.amplitudes)
        return QuantumState(new_amplitudes, self.num_qubits + other.num_qubits)

@dataclass
class QubitRegister:
    """A register of qubits"""
    name: str
    size: int
    state: QuantumState
    index: int = 0

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
        self.state = QuantumState(np.array([1.0], dtype=complex), 0)

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
            raise NotImplementedError(f"Unsupported node type: {node.node_type}")

    def visit_qubit(self, node: QubitNode) -> str:
        """Create a new qubit"""
        if node.name in self.qubits:
            raise ValueError(f"Qubit {node.name} already exists")
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
                    raise ValueError(f"Unsupported initial state: {node.initial_state.state}")

                initial_state = QuantumState(amplitudes, 1)

        if initial_state is None:
            # Default to |0⟩ state
            amplitudes = np.array([1.0, 0.0], dtype=complex)
            initial_state = QuantumState(amplitudes, 1)

        index = self.state.num_qubits
        self.state = self.state.tensor_product(initial_state)
        self.qubits[node.name] = QubitRegister(node.name, 1, self.state, index)
        self._share_state()
        return f"qubit {node.name} = {initial_state}"

    def visit_qudit(self, node: QuditleNode) -> str:
        raise NotImplementedError("Qudits are not supported by the qubit statevector runtime")

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
            raise ValueError(f"Unknown or invalid gate: {gate_type}")

    def _share_state(self):
        for register in self.qubits.values():
            register.state = self.state

    def _apply_gate(self, names, matrix):
        if len(set(names)) != len(names):
            raise ValueError("Gate targets must be distinct")
        indices = [self.qubits[name].index for name in names]
        n = self.state.num_qubits
        axes = indices + [i for i in range(n) if i not in indices]
        tensor = self.state.amplitudes.reshape([2] * n).transpose(axes)
        transformed = matrix @ tensor.reshape(2 ** len(names), -1)
        self.state.amplitudes = transformed.reshape([2] * n).transpose(np.argsort(axes)).reshape(-1)
        return f"Applied gate to {', '.join(names)}"

    def _apply_single_qubit_gate(self, qubit_name, gate_matrix):
        return self._apply_gate([qubit_name], gate_matrix)

    def _apply_two_qubit_gate(self, control_qubit, target_qubit, gate_matrix):
        return self._apply_gate([control_qubit, target_qubit], gate_matrix)

    def probability_one(self, name):
        index = self.qubits[name].index
        mask = (np.arange(len(self.state.amplitudes)) >> (self.state.num_qubits - 1 - index)) & 1
        return float(np.sum(abs(self.state.amplitudes[mask == 1]) ** 2))

    def measure_qubit(self, name):
        result, self.state = self.state.measure(self.qubits[name].index)
        self._share_state()
        return result

    def _evaluate_parameter(self, param_node: ASTNode) -> float:
        """Evaluate a parameter node to get a numeric value"""
        if isinstance(param_node, NumberNode):
            return param_node.value
        elif isinstance(param_node, IdentifierNode):
            if param_node.name in self.variables:
                return float(self.variables[param_node.name])
        raise ValueError("Unknown or unsupported gate parameter")

    def visit_measurement(self, node: MeasurementNode) -> str:
        """Perform a quantum measurement"""
        if node.qubit not in self.qubits:
            return f"Error: Qubit {node.qubit} not found"

        result = self.measure_qubit(node.qubit)

        if node.classical_bit:
            self.classical_bits[node.classical_bit] = result

        return f"Measured {node.qubit}: {result}"

    def visit_entanglement(self, node: EntanglementNode) -> str:
        """Bell/GHZ preparation by H and CNOT fan-out on zero inputs."""
        if node.entanglement_type not in ("bell", "ghz"):
            raise NotImplementedError(f"Unsupported entanglement: {node.entanglement_type}")
        if len(node.qubits) < 2 or len(set(node.qubits)) != len(node.qubits):
            raise ValueError("Entanglement needs at least two distinct qubits")
        if node.entanglement_type == "bell" and len(node.qubits) != 2:
            raise ValueError("Bell preparation needs exactly two qubits")
        for name in node.qubits:
            if self.probability_one(name) > 1e-12:
                raise ValueError("Entanglement preparation requires zero-state inputs")
        self._apply_single_qubit_gate(node.qubits[0], self.gates.hadamard())
        for name in node.qubits[1:]:
            self._apply_two_qubit_gate(node.qubits[0], name, self.gates.cnot())
        return f"Prepared {node.entanglement_type} state"

    def visit_superposition(self, node: SuperpositionNode) -> str:
        raise NotImplementedError("Direct state replacement is unsupported; use unitary gates")

    def visit_grovers(self, node: GroversAlgorithmNode) -> str:
        raise NotImplementedError("Grover oracle execution is not implemented")

    def visit_shors(self, node: ShorsAlgorithmNode) -> str:
        raise NotImplementedError("Shor period finding is not implemented")

    def visit_qft(self, node: QFTNode) -> str:
        raise NotImplementedError("QFT is not implemented")

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
