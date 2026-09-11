#!/usr/bin/env python
"""
Test quantum syntax step by step
"""

from synapse_interpreter import SynapseInterpreter
from synapse_parser import parse


def test_quantum_keyword():
    """Test quantum keyword parsing"""
    print("Testing quantum keyword...")

    code = """
quantum circuit test {
}
"""

    try:
        ast = parse(code)
        print("✓ Quantum circuit parsed successfully!")
        print("AST:", ast)
        return True
    except Exception as e:
        print(f"✗ Quantum parsing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quantum_execution():
    """Test quantum execution"""
    print("\nTesting quantum execution...")

    code = """
quantum circuit bell(2) {
    h(0)
    cnot(0, 1)
}
"""

    try:
        interpreter = SynapseInterpreter()
        result = interpreter.execute(code)
        print("✓ Quantum execution successful!")
        print("Result:", result)
        return True
    except Exception as e:
        print(f"✗ Quantum execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Quantum Syntax Step-by-Step Test")
    print("=" * 40)

    success1 = test_quantum_keyword()
    success2 = test_quantum_execution()

    if success1 and success2:
        print("\n🎉 All quantum tests passed!")
    else:
        print("\n⚠️ Some quantum tests failed")
