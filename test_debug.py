#!/usr/bin/env python
"""
Debug parsing issue
"""

from synapse_lexer import Lexer
from synapse_parser import parse  # Use the global parse function

def test_basic_lexing():
    """Test basic lexing"""
    print("Testing basic lexing...")
    
    code = "x = 5"
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    print("Tokens:")
    for token in tokens:
        print(f"  {token}")
    
    return tokens

def test_basic_parsing():
    """Test basic parsing"""
    print("\nTesting basic parsing...")
    
    code = "x = 5"
    try:
        ast = parse(code)  # Use the global parse function
        print("AST:", ast)
        return ast
    except Exception as e:
        print(f"Parsing error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_basic_lexing()
    test_basic_parsing()
