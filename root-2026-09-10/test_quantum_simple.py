#!/usr/bin/env python
"""Simple quantum syntax test"""

from synapse_interpreter import SynapseInterpreter


def test_circuit():
    interpreter = SynapseInterpreter()
    code = """
    quantum circuit bell_state(2) {
        h(0)
        cnot(0, 1)
        measure(0, 1)
    }
    """
    print("Testing circuit...")
    result = interpreter.execute(code)
    print(f"Circuit result: {result}")
    return True

def test_algorithm():
    interpreter = SynapseInterpreter()
    code = """
    quantum algorithm vqe {
        parameters: [theta1, theta2, theta3]
        ansatz: hardware_efficient
        cost_function: energy_expectation
        optimize: gradient_descent
    }
    """
    print("Testing algorithm...")
    result = interpreter.execute(code)
    print(f"Algorithm result: {result}")
    return True

if __name__ == "__main__":
    print("=== Quantum Syntax Tests ===")
    test_circuit()
    print()
    test_algorithm()
    print("\n[DONE] Tests completed")
