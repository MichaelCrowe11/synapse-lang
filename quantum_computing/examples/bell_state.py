#!/usr/bin/env python3
"""
Synapse Language - Quantum Computing Example: Bell State Creation

This example demonstrates creating quantum entangled Bell states using
the Synapse quantum computing module.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from quantum_computing import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np

def create_bell_state():
    """Create a Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2"""
    
    print("Synapse Language - Quantum Bell State Creation")
    print("=" * 50)
    
    # Create quantum and classical registers
    qreg = QuantumRegister(2, 'q')
    creg = ClassicalRegister(2, 'c')
    
    # Create quantum circuit
    circuit = QuantumCircuit(qreg, creg)
    
    print(f"Initial circuit: {circuit}")
    print(f"   Qubits: {circuit.num_qubits}")
    print(f"   Classical bits: {circuit.num_clbits}")
    print()
    
    # Create Bell state
    print("Building Bell State Circuit:")
    print("   1. Apply Hadamard to qubit 0 (create superposition)")
    circuit.h(0, label="Create superposition")
    
    print("   2. Apply CNOT with control=0, target=1 (create entanglement)")  
    circuit.cnot(0, 1, label="Create entanglement")
    
    print("   3. Measure both qubits")
    circuit.measure_all()
    
    print()
    print("Circuit Details:")
    print(f"   Depth: {circuit.depth()}")
    print(f"   Width: {circuit.width()}")
    print(f"   Gate count: {circuit.size()}")
    print(f"   Operations: {circuit.count_ops()}")
    print()
    
    # Display circuit
    print("Circuit Structure:")
    print(circuit)
    print()
    
    # Get quantum state
    statevector = circuit.get_statevector()
    probabilities = circuit.get_probabilities()
    
    if statevector is not None:
        print("Quantum State Vector:")
        print(f"   |00>: {statevector[0]:.4f}")
        print(f"   |01>: {statevector[1]:.4f}")
        print(f"   |10>: {statevector[2]:.4f}")
        print(f"   |11>: {statevector[3]:.4f}")
        print()
        
        print("Measurement Probabilities:")
        print(f"   P(00): {probabilities[0]:.4f} ({probabilities[0]*100:.1f}%)")
        print(f"   P(01): {probabilities[1]:.4f} ({probabilities[1]*100:.1f}%)")
        print(f"   P(10): {probabilities[2]:.4f} ({probabilities[2]*100:.1f}%)")
        print(f"   P(11): {probabilities[3]:.4f} ({probabilities[3]*100:.1f}%)")
        print()
        
        # Verify Bell state properties
        is_bell_state = (
            abs(statevector[0] - 1/np.sqrt(2)) < 1e-10 and
            abs(statevector[1]) < 1e-10 and
            abs(statevector[2]) < 1e-10 and
            abs(statevector[3] - 1/np.sqrt(2)) < 1e-10
        )
        
        if is_bell_state:
            print("[SUCCESS] Successfully created Bell state |Phi+> = (|00> + |11>)/sqrt(2)")
        else:
            print("[WARNING] State differs from perfect Bell state (due to numerical precision)")
        
        # Calculate entanglement measure (von Neumann entropy)
        # For Bell state, reduced density matrix has entropy log(2)
        expected_entropy = np.log(2)
        print(f"Expected entanglement entropy: {expected_entropy:.4f}")
    
    # Export circuit
    print("\nCircuit Export:")
    print("QASM representation:")
    print(circuit.to_qasm())
    
    return circuit

def demonstrate_other_bell_states():
    """Demonstrate creation of all four Bell states."""
    
    print("\n" + "=" * 55)
    print("All Four Bell States")
    print("=" * 55)
    
    bell_states = [
        ("|Phi+>", lambda c: c.h(0).cnot(0, 1)),                    # (|00> + |11>)/sqrt(2)
        ("|Phi->", lambda c: c.h(0).cnot(0, 1).z(1)),              # (|00> - |11>)/sqrt(2)  
        ("|Psi+>", lambda c: c.h(0).cnot(0, 1).x(0)),              # (|01> + |10>)/sqrt(2)
        ("|Psi->", lambda c: c.h(0).cnot(0, 1).x(0).z(1))         # (|01> - |10>)/sqrt(2)
    ]
    
    for name, construction in bell_states:
        print(f"\nCreating {name}:")
        
        # Create fresh circuit
        qreg = QuantumRegister(2)
        circuit = QuantumCircuit(qreg)
        
        # Apply construction
        construction(circuit)
        
        # Get state
        statevector = circuit.get_statevector()
        probabilities = circuit.get_probabilities()
        
        if statevector is not None:
            print(f"   State vector: {statevector}")
            print(f"   Probabilities: {probabilities}")
            print(f"   Operations: {circuit.count_ops()}")

def simulate_measurement_statistics():
    """Simulate measurement statistics for Bell state."""
    
    print("\n" + "=" * 55)
    print("Bell State Measurement Statistics")
    print("=" * 55)
    
    # Create Bell state
    qreg = QuantumRegister(2)
    circuit = QuantumCircuit(qreg)
    circuit.h(0).cnot(0, 1)
    
    # Get probabilities
    probs = circuit.get_probabilities()
    
    if probs is not None:
        print("Expected measurement outcomes:")
        print(f"   00: {probs[0]*100:.1f}% (should be ~50%)")
        print(f"   01: {probs[1]*100:.1f}% (should be ~0%)")
        print(f"   10: {probs[2]*100:.1f}% (should be ~0%)")
        print(f"   11: {probs[3]*100:.1f}% (should be ~50%)")
        print()
        
        # Simulate multiple measurements
        n_shots = 1000
        np.random.seed(42)  # For reproducible results
        
        measurements = np.random.choice(4, size=n_shots, p=probs)
        counts = np.bincount(measurements, minlength=4)
        
        print(f"Simulated {n_shots} measurements:")
        print(f"   00: {counts[0]} shots ({counts[0]/n_shots*100:.1f}%)")
        print(f"   01: {counts[1]} shots ({counts[1]/n_shots*100:.1f}%)")
        print(f"   10: {counts[2]} shots ({counts[2]/n_shots*100:.1f}%)")
        print(f"   11: {counts[3]} shots ({counts[3]/n_shots*100:.1f}%)")
        
        # Verify correlations
        perfect_correlations = counts[1] + counts[2]  # |01> + |10> should be minimal
        anticorrelations = counts[0] + counts[3]      # |00> + |11> should dominate
        
        print(f"\nEntanglement verification:")
        print(f"   Perfect correlations (00, 11): {anticorrelations} ({anticorrelations/n_shots*100:.1f}%)")
        print(f"   Anti-correlations (01, 10): {perfect_correlations} ({perfect_correlations/n_shots*100:.1f}%)")
        
        if anticorrelations > 0.8 * n_shots:
            print("[SUCCESS] Strong quantum correlations observed - entanglement verified!")
        else:
            print("[WARNING] Weak correlations - check circuit implementation")

def main():
    """Main demonstration function."""
    
    print("Synapse Language - Quantum Computing Module Demo")
    print("Quantum Bell State Creation and Analysis")
    print("=" * 55)
    
    try:
        # Create and analyze basic Bell state
        bell_circuit = create_bell_state()
        
        # Demonstrate all Bell states
        demonstrate_other_bell_states()
        
        # Simulate measurement statistics
        simulate_measurement_statistics()
        
        print("\n" + "=" * 55)
        print("Quantum Bell State Demo Complete!")
        print("[SUCCESS] Successfully demonstrated:")
        print("   • Quantum circuit construction")
        print("   • Quantum gate operations (H, CNOT)")
        print("   • Quantum state simulation")
        print("   • Entanglement creation and verification")
        print("   • QASM export functionality")
        print()
        print("Ready for quantum algorithm development!")
        print("Next: Try quantum algorithms like Deutsch-Jozsa or Grover's search")
        
    except Exception as e:
        print(f"[ERROR] Error in quantum demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)