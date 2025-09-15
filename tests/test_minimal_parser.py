"""
Test suite for Minimal Parser
Basic functionality verification
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang.synapse_lexer import Lexer
from synapse_lang.synapse_parser_minimal import MinimalParser, ParserError
from synapse_lang.synapse_ast_enhanced import *


class TestMinimalParser:
    """Basic parser functionality tests"""

    def parse_source(self, source: str):
        """Helper to parse source code"""
        lexer = Lexer(source)
        parser = MinimalParser(lexer)
        return parser.parse()

    def test_empty_program(self):
        """Empty program should parse successfully"""
        ast = self.parse_source("")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 0

    def test_simple_assignment(self):
        """Parse simple assignment"""
        ast = self.parse_source("x = 42")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert ast.body[0].target == "x"
        assert isinstance(ast.body[0].value, NumberNode)
        assert ast.body[0].value.value == 42.0

    def test_string_assignment(self):
        """Parse string assignment"""
        ast = self.parse_source('name = "hello"')
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert ast.body[0].target == "name"
        assert isinstance(ast.body[0].value, StringNode)
        assert ast.body[0].value.value == "hello"

    def test_boolean_assignment(self):
        """Parse boolean assignment"""
        ast = self.parse_source("flag = true")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, BooleanNode)
        assert ast.body[0].value.value == True

    def test_uncertain_value(self):
        """Parse uncertain value"""
        ast = self.parse_source("uncertain temp = 300 ± 10")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert ast.body[0].is_uncertain == True
        assert ast.body[0].target == "temp"
        # Value should be a BinaryOpNode representing "300 ± 10"
        assert isinstance(ast.body[0].value, BinaryOpNode)
        assert ast.body[0].value.operator == "±"

    def test_function_call(self):
        """Parse function call in assignment"""
        ast = self.parse_source("result = compute(x, y)")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, FunctionCallNode)
        func_call = ast.body[0].value
        assert isinstance(func_call.function, IdentifierNode)
        assert func_call.function.name == "compute"
        assert len(func_call.arguments) == 2

    def test_binary_expression(self):
        """Parse binary expression"""
        ast = self.parse_source("result = x + y")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, BinaryOpNode)
        binary_op = ast.body[0].value
        assert isinstance(binary_op.left, IdentifierNode)
        assert binary_op.operator == "+"
        assert isinstance(binary_op.right, IdentifierNode)

    def test_quantum_circuit_basic(self):
        """Parse basic quantum circuit"""
        source = """quantum circuit bell:
    qubits: 2"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], QuantumCircuitNode)
        circuit = ast.body[0]
        assert circuit.name == "bell"
        assert circuit.qubits == 2

    def test_parallel_basic(self):
        """Parse basic parallel block"""
        source = """parallel:
    branch A: compute_a()
    branch B: compute_b()"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], ParallelNode)
        parallel = ast.body[0]
        assert len(parallel.branches) == 2
        assert parallel.branches[0].name == "A"
        assert parallel.branches[1].name == "B"

    def test_hypothesis_basic(self):
        """Parse basic hypothesis"""
        source = """hypothesis H1:
    assume: temperature > 273
    predict: state == "liquid" """
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], HypothesisNode)
        hypothesis = ast.body[0]
        assert hypothesis.name == "H1"
        assert len(hypothesis.assumptions) == 1
        assert len(hypothesis.predictions) == 1

    def test_multiple_statements(self):
        """Parse multiple statements"""
        source = """x = 42
y = "hello"
z = true"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 3
        assert all(isinstance(stmt, AssignmentNode) for stmt in ast.body)
        assert ast.body[0].target == "x"
        assert ast.body[1].target == "y"
        assert ast.body[2].target == "z"

    def test_single_letter_variables(self):
        """Test that single letter variables work correctly"""
        source = """x = 1
y = 2
z = 3
h = 4
result = x + y * z - h"""
        ast = self.parse_source(source)
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 5
        # All should parse as assignments
        for i in range(4):
            assert isinstance(ast.body[i], AssignmentNode)

        # Last statement should be complex expression
        assert isinstance(ast.body[4], AssignmentNode)
        assert ast.body[4].target == "result"

    def test_invalid_syntax(self):
        """Test that invalid syntax raises ParserError"""
        with pytest.raises(ParserError):
            self.parse_source("x = ")  # Incomplete assignment

        with pytest.raises(ParserError):
            self.parse_source("42 = x")  # Invalid left-hand side

    def test_nested_function_calls(self):
        """Test nested function calls"""
        ast = self.parse_source("result = outer(inner(x))")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, FunctionCallNode)

        outer_call = ast.body[0].value
        assert outer_call.function.name == "outer"
        assert len(outer_call.arguments) == 1
        assert isinstance(outer_call.arguments[0], FunctionCallNode)

        inner_call = outer_call.arguments[0]
        assert inner_call.function.name == "inner"

    def test_expressions_with_parentheses(self):
        """Test expressions with parentheses"""
        ast = self.parse_source("result = (x + y) * z")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        # Should parse as a binary operation
        assert isinstance(ast.body[0].value, BinaryOpNode)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])