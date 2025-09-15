"""
Test suite for Quantum Circuit Parsing
Tests parsing of quantum circuits with gates and measurements
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang.synapse_lexer import Lexer
from synapse_lang.synapse_parser_minimal import MinimalParser, ParserError
from synapse_lang.synapse_ast_enhanced import *


class TestQuantumCircuitParsing:
    """Test quantum circuit parsing functionality"""

    def parse_source(self, source: str):
        """Helper to parse source code"""
        lexer = Lexer(source)
        parser = MinimalParser(lexer)
        return parser.parse()

    def test_basic_quantum_circuit(self):
        """Test basic quantum circuit without gates"""
        source = """quantum circuit simple:
    qubits: 2"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert circuit.name == "simple"
        assert circuit.qubits == 2
        assert len(circuit.gates) == 0
        assert len(circuit.measurements) == 0

    def test_quantum_circuit_with_gates_section(self):
        """Test quantum circuit with gates section"""
        source = """quantum circuit bell:
    qubits: 2
    gates:
        H(0)
        CX(0, 1)"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert circuit.name == "bell"
        assert circuit.qubits == 2
        assert len(circuit.gates) == 2

        # Check first gate (H gate)
        h_gate = circuit.gates[0]
        assert isinstance(h_gate, QuantumGateNode)
        assert h_gate.gate_type == "H"
        assert h_gate.qubits == [0]

        # Check second gate (CX gate)
        cx_gate = circuit.gates[1]
        assert isinstance(cx_gate, QuantumGateNode)
        assert cx_gate.gate_type == "CX"
        assert cx_gate.qubits == [0, 1]

    def test_quantum_circuit_with_measurements(self):
        """Test quantum circuit with measurements"""
        source = """quantum circuit measure_test:
    qubits: 3
    measure("all")"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert circuit.name == "measure_test"
        assert circuit.qubits == 3
        assert len(circuit.measurements) == 1

        measurement = circuit.measurements[0]
        assert isinstance(measurement, QuantumMeasurementNode)
        assert measurement.qubits == "all"

    def test_quantum_circuit_single_qubit_measurement(self):
        """Test quantum circuit with single qubit measurement"""
        source = """quantum circuit single_measure:
    qubits: 2
    measure(0)"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert len(circuit.measurements) == 1

        measurement = circuit.measurements[0]
        assert isinstance(measurement, QuantumMeasurementNode)
        assert measurement.qubits == [0]

    def test_quantum_circuit_direct_gates(self):
        """Test quantum circuit with direct gate calls (no gates: section)"""
        source = """quantum circuit direct:
    qubits: 2
    H(0)
    X(1)"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert circuit.name == "direct"
        assert circuit.qubits == 2
        assert len(circuit.gates) == 2

        # Check gates
        assert circuit.gates[0].gate_type == "H"
        assert circuit.gates[0].qubits == [0]
        assert circuit.gates[1].gate_type == "X"
        assert circuit.gates[1].qubits == [1]

    def test_quantum_circuit_various_gates(self):
        """Test quantum circuit with various gate types"""
        source = """quantum circuit variety:
    qubits: 4
    gates:
        H(0)
        X(1)
        Y(2)
        Z(3)
        CX(0, 1)
        CZ(2, 3)
        SWAP(1, 2)"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert len(circuit.gates) == 7

        # Check gate types
        expected_gates = ["H", "X", "Y", "Z", "CX", "CZ", "SWAP"]
        for i, expected_gate in enumerate(expected_gates):
            assert circuit.gates[i].gate_type == expected_gate

    def test_quantum_circuit_complex(self):
        """Test complex quantum circuit with gates and measurements"""
        source = """quantum circuit complex:
    qubits: 3
    gates:
        H(0)
        CX(0, 1)
        CX(1, 2)
    measure("all")"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert circuit.name == "complex"
        assert circuit.qubits == 3
        assert len(circuit.gates) == 3
        assert len(circuit.measurements) == 1

        # Verify gate sequence
        assert circuit.gates[0].gate_type == "H"
        assert circuit.gates[1].gate_type == "CX"
        assert circuit.gates[2].gate_type == "CX"

        # Verify measurement
        assert circuit.measurements[0].qubits == "all"

    def test_gate_with_multiple_qubits(self):
        """Test gates that operate on multiple qubits"""
        source = """quantum circuit multi_qubit:
    qubits: 3
    CCX(0, 1, 2)"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert len(circuit.gates) == 1

        gate = circuit.gates[0]
        assert gate.gate_type == "CCX"
        assert gate.qubits == [0, 1, 2]

    def test_empty_quantum_circuit(self):
        """Test quantum circuit with only qubit declaration"""
        source = """quantum circuit empty:
    qubits: 5"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)

        circuit = ast.body[0]
        assert circuit.name == "empty"
        assert circuit.qubits == 5
        assert len(circuit.gates) == 0
        assert len(circuit.measurements) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])