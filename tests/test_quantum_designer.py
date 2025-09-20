"""
Test suite for Quantum Circuit Designer
"""

import unittest
import math
from synapse_lang.quantum_designer import QuantumCircuit, QuantumSimulator


class TestQuantumCircuit(unittest.TestCase):
    def setUp(self):
        self.circuit = QuantumCircuit(2)
        self.simulator = QuantumSimulator()

    def test_circuit_creation(self):
        """Test basic circuit creation"""
        self.assertEqual(self.circuit.num_qubits, 2)
        self.assertEqual(len(self.circuit.gates), 0)

    def test_add_gates(self):
        """Test adding gates to circuit"""
        self.circuit.add_gate("H", [0])
        self.circuit.add_gate("CNOT", [0, 1])

        self.assertEqual(len(self.circuit.gates), 2)
        self.assertEqual(self.circuit.gates[0]["name"], "H")
        self.assertEqual(self.circuit.gates[1]["name"], "CNOT")

    def test_hadamard_gate(self):
        """Test Hadamard gate creates superposition"""
        circuit = QuantumCircuit(1)
        circuit.add_gate("H", [0])

        result = self.simulator.simulate(circuit)

        # Check for equal superposition
        self.assertAlmostEqual(abs(result['0']), 1/math.sqrt(2), places=5)
        self.assertAlmostEqual(abs(result['1']), 1/math.sqrt(2), places=5)

    def test_cnot_gate(self):
        """Test CNOT gate creates entanglement"""
        circuit = QuantumCircuit(2)
        circuit.add_gate("H", [0])
        circuit.add_gate("CNOT", [0, 1])

        result = self.simulator.simulate(circuit)

        # Check for Bell state
        self.assertAlmostEqual(abs(result.get('00', 0)), 1/math.sqrt(2), places=5)
        self.assertAlmostEqual(abs(result.get('11', 0)), 1/math.sqrt(2), places=5)
        self.assertAlmostEqual(abs(result.get('01', 0)), 0, places=5)
        self.assertAlmostEqual(abs(result.get('10', 0)), 0, places=5)

    def test_pauli_gates(self):
        """Test Pauli gates"""
        # X gate (bit flip)
        circuit = QuantumCircuit(1)
        circuit.add_gate("X", [0])
        result = self.simulator.simulate(circuit)
        self.assertAlmostEqual(abs(result.get('1', 0)), 1, places=5)

        # Y gate
        circuit = QuantumCircuit(1)
        circuit.add_gate("Y", [0])
        result = self.simulator.simulate(circuit)
        self.assertAlmostEqual(abs(result.get('1', 0)), 1, places=5)

        # Z gate (phase flip)
        circuit = QuantumCircuit(1)
        circuit.add_gate("H", [0])
        circuit.add_gate("Z", [0])
        circuit.add_gate("H", [0])
        result = self.simulator.simulate(circuit)
        self.assertAlmostEqual(abs(result.get('1', 0)), 1, places=5)

    def test_measure(self):
        """Test measurement"""
        circuit = QuantumCircuit(2)
        circuit.add_gate("H", [0])
        circuit.add_gate("CNOT", [0, 1])

        # Measure multiple times
        measurements = []
        for _ in range(100):
            result = self.simulator.measure(circuit)
            measurements.append(result)

        # Should only get '00' or '11' for Bell state
        self.assertTrue(all(m in ['00', '11'] for m in measurements))

        # Roughly equal distribution (statistical test)
        count_00 = measurements.count('00')
        count_11 = measurements.count('11')
        self.assertGreater(count_00, 20)  # At least 20% chance
        self.assertGreater(count_11, 20)  # At least 20% chance

    def test_circuit_to_dict(self):
        """Test circuit serialization"""
        self.circuit.add_gate("H", [0])
        self.circuit.add_gate("CNOT", [0, 1])

        circuit_dict = self.circuit.to_dict()

        self.assertEqual(circuit_dict['num_qubits'], 2)
        self.assertEqual(len(circuit_dict['gates']), 2)
        self.assertEqual(circuit_dict['gates'][0]['name'], 'H')

    def test_invalid_gate_placement(self):
        """Test error handling for invalid gate placement"""
        with self.assertRaises(ValueError):
            # Try to add gate to non-existent qubit
            self.circuit.add_gate("H", [5])

        with self.assertRaises(ValueError):
            # Try to add CNOT with wrong number of qubits
            self.circuit.add_gate("CNOT", [0])

    def test_three_qubit_circuit(self):
        """Test larger circuit with 3 qubits"""
        circuit = QuantumCircuit(3)
        circuit.add_gate("H", [0])
        circuit.add_gate("H", [1])
        circuit.add_gate("CNOT", [0, 2])
        circuit.add_gate("CNOT", [1, 2])

        result = self.simulator.simulate(circuit)

        # Should have 4 possible states with equal probability
        # |000⟩, |011⟩, |101⟩, |110⟩
        self.assertEqual(len(result), 4)

    def test_phase_gates(self):
        """Test phase rotation gates"""
        circuit = QuantumCircuit(1)
        circuit.add_gate("H", [0])
        circuit.add_gate("S", [0])  # S = √Z gate
        circuit.add_gate("T", [0])  # T = ∜Z gate

        result = self.simulator.simulate(circuit)
        self.assertEqual(len(result), 2)  # Still in superposition


if __name__ == '__main__':
    unittest.main()