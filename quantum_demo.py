#!/usr/bin/env python3
"""
Quantum Circuit Demo for Synapse Language
Demonstrates the quantum computing capabilities that position Synapse as a leader
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np

from synapse_quantum_core import (
    QuantumAlgorithms,
    QuantumCircuitBuilder,
    SimulatorBackend,
    create_bell_state,
    create_ghz_state,
)


def demo_basic_quantum_operations():
    print("="*60)
    print("QUANTUM CIRCUIT DEMO: Basic Operations")
    print("="*60)

    # Create a 3-qubit circuit
    circuit = QuantumCircuitBuilder(3, "basic_demo")

    # Build a simple quantum circuit
    circuit.h(0)                    # Hadamard on qubit 0
    circuit.cnot(0, 1)              # CNOT: 0 control, 1 target
    circuit.ry(2, np.pi/4)          # Y-rotation on qubit 2
    circuit.cnot(1, 2)              # CNOT: 1 control, 2 target
    circuit.measure_all()           # Measure all qubits

    print(f"Circuit: {circuit.name}")
    print(f"Qubits: {circuit.num_qubits}")
    print(f"Depth: {circuit.depth()}")
    print(f"Gate counts: {circuit.count_gates()}")

    # Execute on simulator
    backend = SimulatorBackend()
    results = backend.execute(circuit, shots=1000)

    print("\nMeasurement Results (1000 shots):")
    for bitstring, count in sorted(results.items()):
        probability = count / 1000
        print(f"  |{bitstring}⟩: {count:4d} ({probability:.3f})")

def demo_bell_state():
    print("\n" + "="*60)
    print("QUANTUM CIRCUIT DEMO: Bell State (Quantum Entanglement)")
    print("="*60)

    # Create Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    circuit = create_bell_state()

    print("Bell State Circuit:")
    print("  H ──── ●")
    print("          │")
    print("  ──── ──X")
    print("\nExpected: 50% |00⟩, 50% |11⟩")

    backend = SimulatorBackend()
    results = backend.execute(circuit, shots=1000)

    print("\nActual Results:")
    for bitstring, count in sorted(results.items()):
        probability = count / 1000
        if count > 10:  # Only show significant results
            print(f"  |{bitstring}⟩: {count:4d} ({probability:.3f})")

def demo_ghz_state():
    print("\n" + "="*60)
    print("QUANTUM CIRCUIT DEMO: GHZ State (3-Qubit Entanglement)")
    print("="*60)

    # Create 3-qubit GHZ state |GHZ⟩ = (|000⟩ + |111⟩)/√2
    circuit = create_ghz_state(3)

    print("GHZ State Circuit:")
    print("  H ──── ●─────●")
    print("          │     │")
    print("  ─────── X ─── │")
    print("                │")
    print("  ─────────────── X")
    print("\nExpected: 50% |000⟩, 50% |111⟩")

    backend = SimulatorBackend()
    results = backend.execute(circuit, shots=1000)

    print("\nActual Results:")
    for bitstring, count in sorted(results.items()):
        probability = count / 1000
        if count > 10:  # Only show significant results
            print(f"  |{bitstring}⟩: {count:4d} ({probability:.3f})")

def demo_quantum_fourier_transform():
    print("\n" + "="*60)
    print("QUANTUM CIRCUIT DEMO: Quantum Fourier Transform")
    print("="*60)

    # 3-qubit QFT demo
    circuit = QuantumCircuitBuilder(3, "qft_demo")

    # Prepare initial state |101⟩
    circuit.x(0).x(2)
    circuit.barrier()

    # Apply QFT
    qubits = [0, 1, 2]
    QuantumAlgorithms.quantum_fourier_transform(circuit, qubits)
    circuit.measure_all()

    print("3-qubit QFT on initial state |101⟩")
    print(f"Circuit depth: {circuit.depth()}")
    print(f"Total gates: {sum(circuit.count_gates().values())}")

    backend = SimulatorBackend()
    results = backend.execute(circuit, shots=1000)

    print("\nQFT Output Distribution:")
    for bitstring, count in sorted(results.items()):
        probability = count / 1000
        if count > 20:  # Only show significant results
            print(f"  |{bitstring}⟩: {count:4d} ({probability:.3f})")

def demo_variational_circuit():
    print("\n" + "="*60)
    print("QUANTUM CIRCUIT DEMO: Variational Quantum Circuit")
    print("="*60)

    # Simple variational ansatz for optimization
    circuit = QuantumCircuitBuilder(2, "variational_ansatz")

    # Parameterized circuit (would be optimized in real VQE)
    params = [np.pi/3, np.pi/6, np.pi/4]

    # Layer 1
    circuit.ry(0, params[0])
    circuit.ry(1, params[1])
    circuit.cnot(0, 1)

    # Layer 2
    circuit.ry(0, params[2])
    circuit.cnot(1, 0)

    circuit.measure_all()

    print(f"Variational circuit with parameters: {[f'{p:.3f}' for p in params]}")
    print("This type of circuit is used in:")
    print("  - Variational Quantum Eigensolver (VQE)")
    print("  - Quantum Approximate Optimization Algorithm (QAOA)")
    print("  - Quantum Machine Learning")

    backend = SimulatorBackend()
    results = backend.execute(circuit, shots=1000)

    print("\nOutput Distribution:")
    for bitstring, count in sorted(results.items()):
        probability = count / 1000
        print(f"  |{bitstring}⟩: {count:4d} ({probability:.3f})")

def demo_backend_info():
    print("\n" + "="*60)
    print("QUANTUM BACKEND INFORMATION")
    print("="*60)

    backend = SimulatorBackend()
    info = backend.get_backend_info()

    print(f"Backend: {info['name']}")
    print(f"Type: {info['type']}")
    print(f"Max Qubits: {info['max_qubits']}")
    print(f"Max Shots: {info['max_shots']}")
    print(f"Supported Gates: {len(info['gates'])}")
    print(f"Noise Model: {info['noise_model']}")

    print("\nSupported Quantum Gates:")
    for i, gate in enumerate(info["gates"]):
        if i % 6 == 0:
            print("  ", end="")
        print(f"{gate.value:8}", end="")
        if (i + 1) % 6 == 0:
            print()
    print()

def main():
    print("############################################################")
    print("# SYNAPSE QUANTUM COMPUTING DEMONSTRATION")
    print("# Showcasing Leadership in Quantum Programming Languages")
    print("############################################################")

    demo_basic_quantum_operations()
    demo_bell_state()
    demo_ghz_state()
    demo_quantum_fourier_transform()
    demo_variational_circuit()
    demo_backend_info()

    print("\n" + "="*60)
    print("QUANTUM COMPUTING CAPABILITIES SUMMARY")
    print("="*60)
    print("✅ Quantum Circuit Abstraction")
    print("✅ Gate-Level Programming")
    print("✅ Quantum State Simulation")
    print("✅ Entanglement Generation")
    print("✅ Quantum Algorithms (QFT, VQE, QAOA)")
    print("✅ Measurement and Classical Output")
    print("✅ Extensible Backend Architecture")
    print("✅ Educational Demonstrations")
    print("\nSynapse is ready for quantum computing leadership!")
    print("############################################################")

if __name__ == "__main__":
    main()
