"""Quantum Circuit Designer for Synapse Language
Visual and programmatic quantum circuit design with simulation capabilities
"""

import math
import cmath
import json
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import random


class GateType(Enum):
    """Types of quantum gates"""
    # Single qubit gates
    I = auto()      # Identity
    X = auto()      # Pauli-X (NOT)
    Y = auto()      # Pauli-Y
    Z = auto()      # Pauli-Z
    H = auto()      # Hadamard
    S = auto()      # S gate (phase)
    T = auto()      # T gate
    RX = auto()     # Rotation around X
    RY = auto()     # Rotation around Y
    RZ = auto()     # Rotation around Z
    U = auto()      # Universal single-qubit gate

    # Two qubit gates
    CNOT = auto()   # Controlled-NOT
    CZ = auto()     # Controlled-Z
    SWAP = auto()   # SWAP gate
    CRX = auto()    # Controlled rotation X
    CRY = auto()    # Controlled rotation Y
    CRZ = auto()    # Controlled rotation Z

    # Three qubit gates
    CCNOT = auto()  # Toffoli gate
    CSWAP = auto()  # Fredkin gate

    # Measurement
    MEASURE = auto()


@dataclass
class QuantumGate:
    """Quantum gate representation"""
    gate_type: GateType
    qubits: List[int]
    parameters: List[float] = field(default_factory=list)
    label: str = ""

    def __post_init__(self):
        if not self.label:
            self.label = self.gate_type.name

    def get_matrix(self) -> List[List[complex]]:
        """Get matrix representation of gate"""
        if self.gate_type == GateType.I:
            return [[1, 0], [0, 1]]
        elif self.gate_type == GateType.X:
            return [[0, 1], [1, 0]]
        elif self.gate_type == GateType.Y:
            return [[0, -1j], [1j, 0]]
        elif self.gate_type == GateType.Z:
            return [[1, 0], [0, -1]]
        elif self.gate_type == GateType.H:
            return [[1/math.sqrt(2), 1/math.sqrt(2)],
                    [1/math.sqrt(2), -1/math.sqrt(2)]]
        elif self.gate_type == GateType.S:
            return [[1, 0], [0, 1j]]
        elif self.gate_type == GateType.T:
            return [[1, 0], [0, cmath.exp(1j * math.pi / 4)]]
        elif self.gate_type == GateType.RX:
            theta = self.parameters[0] if self.parameters else 0
            cos_half = math.cos(theta / 2)
            sin_half = math.sin(theta / 2)
            return [[cos_half, -1j * sin_half],
                    [-1j * sin_half, cos_half]]
        elif self.gate_type == GateType.RY:
            theta = self.parameters[0] if self.parameters else 0
            cos_half = math.cos(theta / 2)
            sin_half = math.sin(theta / 2)
            return [[cos_half, -sin_half],
                    [sin_half, cos_half]]
        elif self.gate_type == GateType.RZ:
            theta = self.parameters[0] if self.parameters else 0
            return [[cmath.exp(-1j * theta / 2), 0],
                    [0, cmath.exp(1j * theta / 2)]]

        # Default identity for unknown gates
        return [[1, 0], [0, 1]]

    def to_dict(self) -> dict:
        return {
            'type': self.gate_type.name,
            'qubits': self.qubits,
            'parameters': self.parameters,
            'label': self.label
        }


@dataclass
class QuantumCircuit:
    """Quantum circuit representation"""
    num_qubits: int
    gates: List[QuantumGate] = field(default_factory=list)
    classical_bits: int = 0
    measurements: Dict[int, int] = field(default_factory=dict)  # qubit -> classical bit
    name: str = "Circuit"

    def add_gate(self, gate: QuantumGate):
        """Add gate to circuit"""
        # Validate qubit indices
        for qubit in gate.qubits:
            if qubit >= self.num_qubits:
                raise ValueError(f"Qubit index {qubit} out of range")

        self.gates.append(gate)

    def h(self, qubit: int):
        """Add Hadamard gate"""
        self.add_gate(QuantumGate(GateType.H, [qubit]))

    def x(self, qubit: int):
        """Add Pauli-X gate"""
        self.add_gate(QuantumGate(GateType.X, [qubit]))

    def y(self, qubit: int):
        """Add Pauli-Y gate"""
        self.add_gate(QuantumGate(GateType.Y, [qubit]))

    def z(self, qubit: int):
        """Add Pauli-Z gate"""
        self.add_gate(QuantumGate(GateType.Z, [qubit]))

    def cnot(self, control: int, target: int):
        """Add CNOT gate"""
        self.add_gate(QuantumGate(GateType.CNOT, [control, target]))

    def cz(self, control: int, target: int):
        """Add CZ gate"""
        self.add_gate(QuantumGate(GateType.CZ, [control, target]))

    def rx(self, qubit: int, theta: float):
        """Add RX rotation gate"""
        self.add_gate(QuantumGate(GateType.RX, [qubit], [theta]))

    def ry(self, qubit: int, theta: float):
        """Add RY rotation gate"""
        self.add_gate(QuantumGate(GateType.RY, [qubit], [theta]))

    def rz(self, qubit: int, theta: float):
        """Add RZ rotation gate"""
        self.add_gate(QuantumGate(GateType.RZ, [qubit], [theta]))

    def measure(self, qubit: int, classical_bit: Optional[int] = None):
        """Add measurement"""
        if classical_bit is None:
            classical_bit = len(self.measurements)

        self.measurements[qubit] = classical_bit
        self.add_gate(QuantumGate(GateType.MEASURE, [qubit]))

        # Update classical bits count
        self.classical_bits = max(self.classical_bits, classical_bit + 1)

    def measure_all(self):
        """Measure all qubits"""
        for i in range(self.num_qubits):
            self.measure(i, i)

    def depth(self) -> int:
        """Calculate circuit depth"""
        # Simple depth calculation - actual implementation would need gate scheduling
        return len(self.gates)

    def gate_count(self, gate_type: Optional[GateType] = None) -> int:
        """Count gates of specific type or all gates"""
        if gate_type is None:
            return len(self.gates)
        return sum(1 for gate in self.gates if gate.gate_type == gate_type)

    def to_qasm(self) -> str:
        """Convert circuit to OpenQASM format"""
        qasm = f"OPENQASM 2.0;\n"
        qasm += f"include \"qelib1.inc\";\n"
        qasm += f"qreg q[{self.num_qubits}];\n"

        if self.classical_bits > 0:
            qasm += f"creg c[{self.classical_bits}];\n"

        qasm += "\n"

        for gate in self.gates:
            if gate.gate_type == GateType.H:
                qasm += f"h q[{gate.qubits[0]}];\n"
            elif gate.gate_type == GateType.X:
                qasm += f"x q[{gate.qubits[0]}];\n"
            elif gate.gate_type == GateType.Y:
                qasm += f"y q[{gate.qubits[0]}];\n"
            elif gate.gate_type == GateType.Z:
                qasm += f"z q[{gate.qubits[0]}];\n"
            elif gate.gate_type == GateType.CNOT:
                qasm += f"cx q[{gate.qubits[0]}],q[{gate.qubits[1]}];\n"
            elif gate.gate_type == GateType.RX:
                qasm += f"rx({gate.parameters[0]}) q[{gate.qubits[0]}];\n"
            elif gate.gate_type == GateType.RY:
                qasm += f"ry({gate.parameters[0]}) q[{gate.qubits[0]}];\n"
            elif gate.gate_type == GateType.RZ:
                qasm += f"rz({gate.parameters[0]}) q[{gate.qubits[0]}];\n"
            elif gate.gate_type == GateType.MEASURE:
                qubit = gate.qubits[0]
                if qubit in self.measurements:
                    classical_bit = self.measurements[qubit]
                    qasm += f"measure q[{qubit}] -> c[{classical_bit}];\n"

        return qasm

    def to_synapse(self) -> str:
        """Convert circuit to Synapse code"""
        code = f"quantum[{self.num_qubits}] {{\n"

        for gate in self.gates:
            if gate.gate_type == GateType.H:
                code += f"    H(q{gate.qubits[0]})\n"
            elif gate.gate_type == GateType.X:
                code += f"    X(q{gate.qubits[0]})\n"
            elif gate.gate_type == GateType.Y:
                code += f"    Y(q{gate.qubits[0]})\n"
            elif gate.gate_type == GateType.Z:
                code += f"    Z(q{gate.qubits[0]})\n"
            elif gate.gate_type == GateType.CNOT:
                code += f"    CNOT(q{gate.qubits[0]}, q{gate.qubits[1]})\n"
            elif gate.gate_type == GateType.RX:
                code += f"    RX(q{gate.qubits[0]}, {gate.parameters[0]})\n"
            elif gate.gate_type == GateType.RY:
                code += f"    RY(q{gate.qubits[0]}, {gate.parameters[0]})\n"
            elif gate.gate_type == GateType.RZ:
                code += f"    RZ(q{gate.qubits[0]}, {gate.parameters[0]})\n"
            elif gate.gate_type == GateType.MEASURE:
                code += f"    measure(q{gate.qubits[0]})\n"

        code += "}"
        return code

    def draw(self) -> str:
        """Draw ASCII representation of circuit"""
        # Create wire representation
        wires = []
        for i in range(self.num_qubits):
            wire = f"q{i} ───"
            wires.append(wire)

        # Add gates to wires
        for gate in self.gates:
            if gate.gate_type in [GateType.H, GateType.X, GateType.Y, GateType.Z]:
                qubit = gate.qubits[0]
                wires[qubit] += f"─[{gate.gate_type.name}]─"
            elif gate.gate_type == GateType.CNOT:
                control, target = gate.qubits
                wires[control] += "─●─"
                wires[target] += "─⊕─"
            elif gate.gate_type in [GateType.RX, GateType.RY, GateType.RZ]:
                qubit = gate.qubits[0]
                angle = gate.parameters[0] if gate.parameters else 0
                wires[qubit] += f"─[{gate.gate_type.name}({angle:.2f})]─"
            elif gate.gate_type == GateType.MEASURE:
                qubit = gate.qubits[0]
                wires[qubit] += "─[M]─"

        # Close wires
        for i in range(self.num_qubits):
            wires[i] += "───"

        return "\n".join(wires)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'num_qubits': self.num_qubits,
            'classical_bits': self.classical_bits,
            'gates': [gate.to_dict() for gate in self.gates],
            'measurements': self.measurements
        }


class QuantumSimulator:
    """Basic quantum circuit simulator"""

    def __init__(self):
        self.state = None
        self.num_qubits = 0

    def initialize(self, num_qubits: int):
        """Initialize quantum state to |0...0⟩"""
        self.num_qubits = num_qubits
        self.state = [0.0] * (2 ** num_qubits)
        self.state[0] = 1.0  # |0...0⟩ state

    def apply_gate(self, gate: QuantumGate):
        """Apply quantum gate to state"""
        if gate.gate_type == GateType.H:
            self._apply_single_qubit_gate(gate.qubits[0], gate.get_matrix())
        elif gate.gate_type == GateType.X:
            self._apply_single_qubit_gate(gate.qubits[0], gate.get_matrix())
        elif gate.gate_type == GateType.CNOT:
            self._apply_cnot(gate.qubits[0], gate.qubits[1])

    def _apply_single_qubit_gate(self, qubit: int, matrix: List[List[complex]]):
        """Apply single qubit gate"""
        new_state = [0.0] * len(self.state)

        for i in range(len(self.state)):
            # Extract qubit state
            bit_val = (i >> qubit) & 1

            # Apply gate matrix
            for j in range(2):
                if bit_val == 0:
                    new_i = i
                    coeff = matrix[j][0]
                else:
                    new_i = i ^ (1 << qubit)
                    coeff = matrix[j][1]

                new_state[new_i] += coeff * self.state[i]

        self.state = new_state

    def _apply_cnot(self, control: int, target: int):
        """Apply CNOT gate"""
        new_state = self.state.copy()

        for i in range(len(self.state)):
            control_bit = (i >> control) & 1
            if control_bit == 1:
                # Flip target bit
                new_i = i ^ (1 << target)
                new_state[new_i] = self.state[i]
                new_state[i] = 0

        self.state = new_state

    def measure(self, qubit: int) -> int:
        """Measure specific qubit"""
        prob_0 = 0.0
        prob_1 = 0.0

        for i in range(len(self.state)):
            bit_val = (i >> qubit) & 1
            prob = abs(self.state[i]) ** 2

            if bit_val == 0:
                prob_0 += prob
            else:
                prob_1 += prob

        # Random measurement outcome
        if random.random() < prob_0:
            result = 0
            # Collapse state
            norm = math.sqrt(prob_0)
            for i in range(len(self.state)):
                if (i >> qubit) & 1 == 1:
                    self.state[i] = 0
                else:
                    self.state[i] /= norm
        else:
            result = 1
            # Collapse state
            norm = math.sqrt(prob_1)
            for i in range(len(self.state)):
                if (i >> qubit) & 1 == 0:
                    self.state[i] = 0
                else:
                    self.state[i] /= norm

        return result

    def get_probabilities(self) -> Dict[str, float]:
        """Get measurement probabilities for all basis states"""
        probs = {}
        for i in range(len(self.state)):
            prob = abs(self.state[i]) ** 2
            if prob > 1e-10:  # Only show non-zero probabilities
                binary = format(i, f'0{self.num_qubits}b')
                probs[binary] = prob
        return probs

    def simulate_circuit(self, circuit: QuantumCircuit) -> Dict[str, float]:
        """Simulate entire circuit and return final probabilities"""
        self.initialize(circuit.num_qubits)

        for gate in circuit.gates:
            if gate.gate_type != GateType.MEASURE:
                self.apply_gate(gate)

        return self.get_probabilities()


class CircuitLibrary:
    """Library of common quantum circuits"""

    @staticmethod
    def bell_state() -> QuantumCircuit:
        """Create Bell state circuit"""
        circuit = QuantumCircuit(2, name="Bell State")
        circuit.h(0)
        circuit.cnot(0, 1)
        return circuit

    @staticmethod
    def ghz_state(n: int) -> QuantumCircuit:
        """Create GHZ state circuit"""
        circuit = QuantumCircuit(n, name=f"GHZ-{n}")
        circuit.h(0)
        for i in range(1, n):
            circuit.cnot(0, i)
        return circuit

    @staticmethod
    def quantum_fourier_transform(n: int) -> QuantumCircuit:
        """Create Quantum Fourier Transform circuit"""
        circuit = QuantumCircuit(n, name=f"QFT-{n}")

        for i in range(n):
            circuit.h(i)
            for j in range(i + 1, n):
                # Controlled rotation
                angle = math.pi / (2 ** (j - i))
                circuit.rz(j, angle)  # Simplified - actual QFT needs controlled rotations

        # Reverse qubit order (swap gates)
        for i in range(n // 2):
            # Add swap gates here in full implementation
            pass

        return circuit

    @staticmethod
    def grover_oracle(n: int, marked: int) -> QuantumCircuit:
        """Create Grover oracle for marked item"""
        circuit = QuantumCircuit(n, name=f"Grover Oracle")

        # Mark the target state
        for i in range(n):
            if not (marked & (1 << i)):
                circuit.x(i)

        # Multi-controlled Z gate (simplified)
        if n > 1:
            circuit.z(n - 1)  # Simplified oracle

        # Uncompute
        for i in range(n):
            if not (marked & (1 << i)):
                circuit.x(i)

        return circuit

    @staticmethod
    def variational_ansatz(n: int, depth: int) -> QuantumCircuit:
        """Create variational quantum circuit ansatz"""
        circuit = QuantumCircuit(n, name=f"VQE Ansatz")

        for layer in range(depth):
            # Rotation layer
            for i in range(n):
                circuit.ry(i, 0.5)  # Parameter would be optimized

            # Entangling layer
            for i in range(n - 1):
                circuit.cnot(i, i + 1)

        return circuit


class QuantumCircuitBuilder:
    """Interactive quantum circuit builder"""

    def __init__(self):
        self.circuit = None
        self.simulator = QuantumSimulator()

    def new_circuit(self, num_qubits: int, name: str = "New Circuit") -> QuantumCircuit:
        """Create new circuit"""
        self.circuit = QuantumCircuit(num_qubits, name=name)
        return self.circuit

    def add_gate_by_name(self, gate_name: str, qubits: List[int],
                        parameters: List[float] = None):
        """Add gate by name"""
        if not self.circuit:
            raise ValueError("No circuit created")

        parameters = parameters or []
        gate_type = GateType[gate_name.upper()]
        gate = QuantumGate(gate_type, qubits, parameters)
        self.circuit.add_gate(gate)

    def simulate(self) -> Dict[str, float]:
        """Simulate current circuit"""
        if not self.circuit:
            raise ValueError("No circuit to simulate")

        return self.simulator.simulate_circuit(self.circuit)

    def get_circuit_info(self) -> Dict[str, Any]:
        """Get circuit information"""
        if not self.circuit:
            return {}

        return {
            'name': self.circuit.name,
            'qubits': self.circuit.num_qubits,
            'gates': len(self.circuit.gates),
            'depth': self.circuit.depth(),
            'measurements': len(self.circuit.measurements)
        }

    def save_circuit(self, filename: str):
        """Save circuit to file"""
        if not self.circuit:
            raise ValueError("No circuit to save")

        with open(filename, 'w') as f:
            json.dump(self.circuit.to_dict(), f, indent=2)

    def load_circuit(self, filename: str):
        """Load circuit from file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        circuit = QuantumCircuit(data['num_qubits'], name=data['name'])
        circuit.classical_bits = data['classical_bits']
        circuit.measurements = data['measurements']

        for gate_data in data['gates']:
            gate = QuantumGate(
                GateType[gate_data['type']],
                gate_data['qubits'],
                gate_data['parameters']
            )
            circuit.add_gate(gate)

        self.circuit = circuit


# Example usage and testing
if __name__ == "__main__":
    print("Synapse Quantum Circuit Designer")
    print("=" * 40)

    # Create circuit builder
    builder = QuantumCircuitBuilder()

    # Example 1: Bell state circuit
    print("\n--- Bell State Circuit ---")
    bell = CircuitLibrary.bell_state()
    print(f"Circuit: {bell.name}")
    print(f"Qubits: {bell.num_qubits}")
    print(f"Gates: {bell.gate_count()}")
    print(f"Depth: {bell.depth()}")
    print("\nASCII Diagram:")
    print(bell.draw())
    print("\nSynapse Code:")
    print(bell.to_synapse())

    # Simulate Bell state
    simulator = QuantumSimulator()
    probabilities = simulator.simulate_circuit(bell)
    print("\nSimulation Results:")
    for state, prob in probabilities.items():
        print(f"|{state}⟩: {prob:.3f}")

    # Example 2: GHZ state
    print("\n--- GHZ State Circuit ---")
    ghz = CircuitLibrary.ghz_state(3)
    print(f"Circuit: {ghz.name}")
    print(ghz.draw())

    # Example 3: Manual circuit building
    print("\n--- Manual Circuit Building ---")
    circuit = builder.new_circuit(2, "Custom Circuit")
    builder.add_gate_by_name("H", [0])
    builder.add_gate_by_name("RY", [1], [math.pi/4])
    builder.add_gate_by_name("CNOT", [0, 1])
    circuit.measure_all()

    print("Custom Circuit:")
    print(circuit.draw())

    # Simulate custom circuit
    results = builder.simulate()
    print("\nCustom Circuit Results:")
    for state, prob in results.items():
        print(f"|{state}⟩: {prob:.3f}")

    # Example 4: VQE ansatz
    print("\n--- VQE Ansatz ---")
    vqe = CircuitLibrary.variational_ansatz(3, 2)
    print(f"Circuit: {vqe.name}")
    print(f"Parameters: {vqe.gate_count(GateType.RY)} rotation gates")

    # Example 5: Circuit export
    print("\n--- Circuit Export ---")
    print("QASM Export:")
    print(bell.to_qasm())

    print("\n--- Circuit Library ---")
    circuits = [
        ("Bell State", CircuitLibrary.bell_state()),
        ("GHZ-3", CircuitLibrary.ghz_state(3)),
        ("QFT-3", CircuitLibrary.quantum_fourier_transform(3)),
        ("VQE Ansatz", CircuitLibrary.variational_ansatz(2, 1))
    ]

    for name, circuit in circuits:
        info = {
            'qubits': circuit.num_qubits,
            'gates': circuit.gate_count(),
            'depth': circuit.depth()
        }
        print(f"• {name}: {info['qubits']} qubits, {info['gates']} gates, depth {info['depth']}")

    print("\n✅ Quantum circuit designer implemented!")