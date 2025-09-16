#!/usr/bin/env python3
"""
Quantum Cryptography Example
Demonstrates quantum key distribution and cryptographic protocols
"""

def run_quantum_cryptography_example():
    """Run quantum cryptography simulation using BB84 protocol"""

    try:
        import random

        from synapse_qubit_bridge import create_hybrid_interpreter

        print("=" * 60)
        print("QUANTUM CRYPTOGRAPHY - BB84 PROTOCOL")
        print("=" * 60)

        # Create hybrid interpreter
        bridge = create_hybrid_interpreter()

        # Synapse-Lang: Security analysis and uncertainty quantification
        synapse_code = """
        # Security parameters with uncertainty
        uncertain key_length = 256 ± 0
        uncertain channel_noise = 0.05 ± 0.01
        uncertain eavesdropping_probability = 0.12 ± 0.03
        uncertain detection_efficiency = 0.85 ± 0.05

        # Cryptographic security hypothesis
        hypothesis quantum_key_security {
            assume: no_cloning_theorem_holds
            assume: measurement_disturbs_quantum_state
            predict: eavesdropping_detection_possible
            predict: information_theoretic_security
            validate: key_error_rate_analysis
        }

        # Parallel security analysis
        parallel {
            branch alice: prepare_quantum_states
            branch bob: measure_quantum_states
            branch eve: eavesdropping_analysis
            branch security: error_rate_estimation
        }
        """

        # Qubit-Flow: BB84 quantum key distribution protocol
        qubit_code = """
        # Alice's qubits for key distribution
        qubit bit0 = |0⟩
        qubit bit1 = |0⟩
        qubit bit2 = |0⟩
        qubit bit3 = |0⟩

        # Alice's preparation circuit (random bases)
        circuit alice_prepare(bit0, bit1, bit2, bit3) {
            # Bit 0: |0⟩ in computational basis
            # (no operations needed)

            # Bit 1: |1⟩ in computational basis
            X[bit1]

            # Bit 2: |+⟩ in Hadamard basis
            H[bit2]

            # Bit 3: |−⟩ in Hadamard basis
            X[bit3]
            H[bit3]
        }

        # Bob's measurement circuit (random bases)
        circuit bob_measure(bit0, bit1, bit2, bit3) {
            # Measure bit0 and bit1 in computational basis
            measure bit0 -> result0
            measure bit1 -> result1

            # Measure bit2 and bit3 in Hadamard basis
            H[bit2]
            H[bit3]
            measure bit2 -> result2
            measure bit3 -> result3
        }

        # Eavesdropping detection circuit
        circuit eve_intercept(bit0, bit1, bit2, bit3) {
            # Eve measures in random bases (introduces errors)
            measure bit0 -> eve_bit0
            measure bit2 -> eve_bit2

            # Eve's measurements disturb the quantum states
            # This will be detected through increased error rate
        }
        """

        print("Simulating BB84 quantum key distribution protocol...")
        print("\nAlice: Preparing quantum states in random bases")
        print("Bob: Measuring quantum states in random bases")
        print("Security: Analyzing eavesdropping detection")

        # Execute quantum cryptography simulation
        results = bridge.execute_hybrid(synapse_code, qubit_code)

        print("\n" + "-" * 50)
        print("BB84 PROTOCOL RESULTS")
        print("-" * 50)

        # Display cryptographic analysis
        print("\nCryptographic Security Analysis:")
        for i, result in enumerate(results.get("synapse_results", [])[:5]):
            print(f"  {i+1}. {result}")

        print("\nQuantum Key Distribution:")
        for i, result in enumerate(results.get("qubit_results", [])[:5]):
            print(f"  {i+1}. {result}")

        # Simulate key generation process
        print("\n" + "=" * 60)
        print("KEY GENERATION SIMULATION")
        print("=" * 60)

        # Simulate Alice's random bit and basis choices
        alice_bits = [random.randint(0, 1) for _ in range(8)]
        alice_bases = [random.choice(["Z", "X"]) for _ in range(8)]  # Z=computational, X=Hadamard

        # Simulate Bob's random basis choices
        bob_bases = [random.choice(["Z", "X"]) for _ in range(8)]

        print("Alice's preparation:")
        for i, (bit, basis) in enumerate(zip(alice_bits, alice_bases, strict=False)):
            state = "|0⟩" if bit == 0 else "|1⟩" if basis == "Z" else "|+⟩" if bit == 0 else "|−⟩"
            print(f"  Qubit {i}: bit={bit}, basis={basis}, state={state}")

        print("\nBob's measurement:")
        for i, basis in enumerate(bob_bases):
            print(f"  Qubit {i}: measurement_basis={basis}")

        # Key sifting - keep bits where Alice and Bob used same basis
        shared_key = []
        for i, (a_basis, b_basis, bit) in enumerate(zip(alice_bases, bob_bases, alice_bits, strict=False)):
            if a_basis == b_basis:
                shared_key.append(bit)
                print(f"  ✓ Qubit {i}: bases match, key bit = {bit}")
            else:
                print(f"  ✗ Qubit {i}: bases don't match, discard")

        print(f"\nShared key after sifting: {''.join(map(str, shared_key))}")
        print(f"Key length: {len(shared_key)} bits")

        # Error rate analysis for eavesdropping detection
        print("\n" + "=" * 60)
        print("SECURITY ANALYSIS")
        print("=" * 60)

        # Simulate error rates
        baseline_error = 0.05  # Channel noise
        eavesdropping_error = 0.12  # Additional error from eavesdropping

        print(f"Channel noise error rate: {baseline_error:.1%}")
        print(f"Eavesdropping error rate: {eavesdropping_error:.1%}")

        if eavesdropping_error > 0.11:  # BB84 threshold
            print("⚠️  SECURITY ALERT: High error rate detected!")
            print("   Possible eavesdropping - abort key distribution")
        else:
            print("✓ Error rate within acceptable limits")
            print("   Key distribution secure")

        print("\nQuantum Cryptography Advantages:")
        print("✓ Information-theoretic security (not computational)")
        print("✓ Eavesdropping detection through quantum mechanics")
        print("✓ No-cloning theorem prevents perfect key copying")
        print("✓ Measurement disturbance reveals eavesdropper")

        # Quantum-enhanced security metrics
        if results.get("quantum_enhanced"):
            print("\nQuantum-Enhanced Security Metrics:")
            for var, value in results.get("quantum_enhanced", {}).items():
                print(f"  {var}: {value}")

        return results

    except Exception as e:
        print(f"Error in quantum cryptography simulation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_quantum_cryptography_example()
