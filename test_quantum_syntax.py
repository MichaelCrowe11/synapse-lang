#!/usr/bin/env python
"""
Test quantum syntax integration in Synapse
Validates that native quantum syntax is properly parsed and executed
"""

from synapse_interpreter import SynapseInterpreter

def test_quantum_circuit_syntax():
    """Test native quantum circuit syntax"""
    interpreter = SynapseInterpreter()
    
    # Test basic quantum circuit syntax
    quantum_code = """
    quantum circuit bell_state(2) {
        h(0)
        cnot(0, 1)
        measure(0, 1)
    }
    """
    
    print("Testing Quantum Circuit Syntax:")
    print("=" * 50)
    print("Code:")
    print(quantum_code)
    print("\nExecution:")
    
    try:
        result = interpreter.execute(quantum_code)
        print("Result:", result)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_quantum_algorithm_syntax():
    """Test quantum algorithm syntax"""
    interpreter = SynapseInterpreter()
    
    # Test quantum algorithm definition
    algorithm_code = """
    quantum algorithm vqe {
        parameters: [theta1, theta2, theta3]
        ansatz: hardware_efficient
        cost_function: energy_expectation
        optimize: gradient_descent
    }
    """
    
    print("\n\nTesting Quantum Algorithm Syntax:")
    print("=" * 50)
    print("Code:")
    print(algorithm_code)
    print("\nExecution:")
    
    try:
        result = interpreter.execute(algorithm_code)
        print("Result:", result)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_quantum_backend_syntax():
    """Test quantum backend configuration syntax"""
    interpreter = SynapseInterpreter()
    
    # Test quantum backend configuration
    backend_code = """
    quantum backend simulator {
        shots: 1024
        noise_model: ideal
        optimization_level: 3
    }
    """
    
    print("\n\nTesting Quantum Backend Syntax:")
    print("=" * 50)
    print("Code:")
    print(backend_code)
    print("\nExecution:")
    
    try:
        result = interpreter.execute(backend_code)
        print("Result:", result)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_mixed_quantum_classical():
    """Test mixed quantum and classical code"""
    interpreter = SynapseInterpreter()
    
    # Test mixed syntax
    mixed_code = """
    # Classical variables
    num_qubits = 3
    shots = 1000
    
    # Quantum circuit
    quantum circuit ghz_state(3) {
        h(0)
        cnot(0, 1)
        cnot(1, 2)
        measure(0, 1, 2)
    }
    
    # Classical processing
    result_analysis = "GHZ state prepared"
    """
    
    print("\n\nTesting Mixed Quantum-Classical Syntax:")
    print("=" * 50)
    print("Code:")
    print(mixed_code)
    print("\nExecution:")
    
    try:
        result = interpreter.execute(mixed_code)
        print("Result:", result)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_all_tests():
    """Run all quantum syntax tests"""
    print("Synapse Quantum Syntax Integration Tests")
    print("=" * 60)
    
    tests = [
        test_quantum_circuit_syntax,
        test_quantum_algorithm_syntax,
        test_quantum_backend_syntax,
        test_mixed_quantum_classical
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("[OK] PASSED")
            else:
                print("[X] FAILED")
        except Exception as e:
            print(f"[X] FAILED with exception: {e}")
    
    print(f"\n\nTest Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All quantum syntax tests passed!")
        print("[READY] Synapse now supports native quantum programming!")
    else:
        print("[WARNING] Some tests failed. Check implementation details.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
