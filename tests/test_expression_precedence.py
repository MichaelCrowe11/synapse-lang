"""
Test suite for Expression Parser with Operator Precedence
Tests proper handling of mathematical operator precedence
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang.synapse_lexer import Lexer
from synapse_lang.synapse_parser_minimal import MinimalParser, ParserError
from synapse_lang.synapse_ast_enhanced import *


class TestExpressionPrecedence:
    """Test operator precedence in expressions"""

    def parse_expression(self, source: str):
        """Helper to parse an expression and return the assignment value"""
        lexer = Lexer(f"result = {source}")
        parser = MinimalParser(lexer)
        ast = parser.parse()
        return ast.body[0].value

    def test_arithmetic_precedence(self):
        """Test arithmetic operator precedence"""
        # 1 + 2 * 3 should be 1 + (2 * 3), not (1 + 2) * 3
        expr = self.parse_expression("1 + 2 * 3")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "+"
        assert isinstance(expr.left, NumberNode)
        assert expr.left.value == 1.0
        assert isinstance(expr.right, BinaryOpNode)
        assert expr.right.operator == "*"

    def test_parentheses_override_precedence(self):
        """Test that parentheses override precedence"""
        # (1 + 2) * 3 should be parsed as a multiplication where left is (1 + 2)
        expr = self.parse_expression("(1 + 2) * 3")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "*"
        assert isinstance(expr.left, BinaryOpNode)  # This should be the (1 + 2) part
        assert expr.left.operator == "+"
        assert isinstance(expr.right, NumberNode)
        assert expr.right.value == 3.0

    def test_exponentiation_precedence(self):
        """Test exponentiation has highest precedence"""
        # 2 + 3 ^ 2 should be 2 + (3 ^ 2)
        expr = self.parse_expression("2 + 3 ^ 2")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "+"
        assert isinstance(expr.left, NumberNode)
        assert expr.left.value == 2.0
        assert isinstance(expr.right, BinaryOpNode)
        assert expr.right.operator == "^"

    def test_exponentiation_right_associative(self):
        """Test exponentiation is right associative"""
        # 2 ^ 3 ^ 2 should be 2 ^ (3 ^ 2), not (2 ^ 3) ^ 2
        expr = self.parse_expression("2 ^ 3 ^ 2")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "^"
        assert isinstance(expr.left, NumberNode)
        assert expr.left.value == 2.0
        assert isinstance(expr.right, BinaryOpNode)
        assert expr.right.operator == "^"
        assert expr.right.left.value == 3.0
        assert expr.right.right.value == 2.0

    def test_unary_operators(self):
        """Test unary operators"""
        # -x should be parsed as unary minus
        expr = self.parse_expression("-x")
        assert isinstance(expr, UnaryOpNode)
        assert expr.operator == "-"
        assert isinstance(expr.operand, IdentifierNode)
        assert expr.operand.name == "x"

    def test_unary_precedence(self):
        """Test unary operators have high precedence"""
        # -2 ^ 3 should be (-2) ^ 3
        expr = self.parse_expression("-2 ^ 3")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "^"
        assert isinstance(expr.left, UnaryOpNode)
        assert expr.left.operator == "-"

    def test_comparison_operators(self):
        """Test comparison operators"""
        # x > y should be parsed correctly
        expr = self.parse_expression("x > y")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == ">"
        assert isinstance(expr.left, IdentifierNode)
        assert isinstance(expr.right, IdentifierNode)

    def test_logical_operators_precedence(self):
        """Test logical operators have correct precedence"""
        # x > 5 && y < 10 should be (x > 5) && (y < 10)
        expr = self.parse_expression("x > 5 && y < 10")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "&&"
        assert isinstance(expr.left, BinaryOpNode)
        assert expr.left.operator == ">"
        assert isinstance(expr.right, BinaryOpNode)
        assert expr.right.operator == "<"

    def test_function_calls_in_expressions(self):
        """Test function calls within expressions"""
        # sin(x) + cos(y) should parse correctly
        expr = self.parse_expression("sin(x) + cos(y)")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "+"
        assert isinstance(expr.left, FunctionCallNode)
        assert isinstance(expr.right, FunctionCallNode)

    def test_nested_function_calls(self):
        """Test nested function calls"""
        # f(g(x)) should parse correctly
        expr = self.parse_expression("f(g(x))")
        assert isinstance(expr, FunctionCallNode)
        assert isinstance(expr.function, IdentifierNode)
        assert expr.function.name == "f"
        assert len(expr.arguments) == 1
        assert isinstance(expr.arguments[0], FunctionCallNode)

    def test_complex_expression(self):
        """Test complex expression with multiple operators"""
        # -a + b * c ^ d / e > f && g should parse with correct precedence
        expr = self.parse_expression("-a + b * c ^ d / e > f && g")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "&&"
        # Left side should be the comparison
        assert isinstance(expr.left, BinaryOpNode)
        assert expr.left.operator == ">"
        # Right side should be g
        assert isinstance(expr.right, IdentifierNode)
        assert expr.right.name == "g"

    def test_division_and_multiplication_left_associative(self):
        """Test that multiplication and division are left associative"""
        # a / b * c should be (a / b) * c
        expr = self.parse_expression("a / b * c")
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "*"
        assert isinstance(expr.left, BinaryOpNode)
        assert expr.left.operator == "/"

    def test_array_access(self):
        """Test array access syntax"""
        # arr[index] should parse correctly
        expr = self.parse_expression("arr[5]")
        assert isinstance(expr, FunctionCallNode)
        assert expr.function.name == "__getitem__"
        assert len(expr.arguments) == 2

    def test_chained_array_access(self):
        """Test chained array access"""
        # matrix[i][j] should parse correctly
        expr = self.parse_expression("matrix[i][j]")
        assert isinstance(expr, FunctionCallNode)
        assert expr.function.name == "__getitem__"
        # The first argument should be another array access
        assert isinstance(expr.arguments[0], FunctionCallNode)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])