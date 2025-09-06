#!/usr/bin/env python
"""
Simple test to validate quantum syntax parsing
"""

from synapse_parser import parse
from synapse_interpreter import SynapseInterpreter

def test_simple_parsing():
    """Test simple quantum circuit parsing"""
    print("Testing simple quantum circuit parsing...")
    
    # Simple quantum code
    code = """
    x = 5
    """
    
    try:
        interpreter = SynapseInterpreter()
        result = interpreter.execute(code)
        print("Basic parsing works:", result)
        return True
    except Exception as e:
        print(f"Basic parsing error: {e}")
        return False

def test_quantum_keyword():
    """Test quantum keyword recognition"""
    print("\nTesting quantum keyword recognition...")
    
    # Just the quantum keyword
    code = """
    quantum circuit test {
    }
    """
    
    try:
        ast = parse(code)
        print("Quantum keyword parsed successfully")
        print("AST:", ast)
        return True
    except Exception as e:
        print(f"Quantum keyword error: {e}")
        return False

if __name__ == "__main__":
    print("Simple Quantum Syntax Test")
    print("=" * 30)
    
    test_simple_parsing()
    test_quantum_keyword()
