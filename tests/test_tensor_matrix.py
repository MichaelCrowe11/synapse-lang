"""
Test suite for Tensor and Matrix Literal Parsing
Tests parsing of tensor declarations and matrix literals
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_lang.synapse_lexer import Lexer
from synapse_lang.synapse_parser_minimal import MinimalParser, ParserError
from synapse_lang.synapse_ast_enhanced import *


class TestTensorMatrixParsing:
    """Test tensor and matrix parsing functionality"""

    def parse_source(self, source: str):
        """Helper to parse source code"""
        lexer = Lexer(source)
        parser = MinimalParser(lexer)
        return parser.parse()

    def test_simple_vector(self):
        """Test parsing simple vector literal"""
        ast = self.parse_source("vec = [1, 2, 3]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert ast.body[0].target == "vec"
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 1  # Single row (vector)
        assert len(matrix.rows[0]) == 3  # Three elements

        # Check the values
        assert isinstance(matrix.rows[0][0], NumberNode)
        assert matrix.rows[0][0].value == 1.0
        assert isinstance(matrix.rows[0][1], NumberNode)
        assert matrix.rows[0][1].value == 2.0
        assert isinstance(matrix.rows[0][2], NumberNode)
        assert matrix.rows[0][2].value == 3.0

    def test_empty_list(self):
        """Test parsing empty list"""
        ast = self.parse_source("empty = []")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 0

    def test_matrix_literal(self):
        """Test parsing 2D matrix literal"""
        ast = self.parse_source("matrix = [[1, 2], [3, 4]]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 2  # Two rows
        assert len(matrix.rows[0]) == 2  # Two columns in first row
        assert len(matrix.rows[1]) == 2  # Two columns in second row

        # Check values
        assert matrix.rows[0][0].value == 1.0
        assert matrix.rows[0][1].value == 2.0
        assert matrix.rows[1][0].value == 3.0
        assert matrix.rows[1][1].value == 4.0

    def test_mixed_matrix(self):
        """Test matrix with expressions"""
        ast = self.parse_source("matrix = [[x + 1, y], [3, z * 2]]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 2

        # First row, first element should be x + 1
        assert isinstance(matrix.rows[0][0], BinaryOpNode)
        assert matrix.rows[0][0].operator == "+"

        # First row, second element should be y
        assert isinstance(matrix.rows[0][1], IdentifierNode)
        assert matrix.rows[0][1].name == "y"

    def test_tensor_declaration_basic(self):
        """Test basic tensor declaration"""
        ast = self.parse_source("tensor T[3, 3]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], TensorNode)

        tensor = ast.body[0]
        assert tensor.name == "T"
        assert tensor.dimensions == [3, 3]
        assert tensor.initializer is None

    def test_tensor_declaration_with_initializer(self):
        """Test tensor declaration with initializer"""
        ast = self.parse_source("tensor T[2, 2] = [[1, 2], [3, 4]]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], TensorNode)

        tensor = ast.body[0]
        assert tensor.name == "T"
        assert tensor.dimensions == [2, 2]
        assert isinstance(tensor.initializer, MatrixNode)

    def test_tensor_3d(self):
        """Test 3D tensor declaration"""
        ast = self.parse_source("tensor volume[10, 20, 30]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], TensorNode)

        tensor = ast.body[0]
        assert tensor.name == "volume"
        assert tensor.dimensions == [10, 20, 30]

    def test_vector_with_function_calls(self):
        """Test vector containing function calls"""
        ast = self.parse_source("values = [sin(x), cos(y), tan(z)]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 1
        assert len(matrix.rows[0]) == 3

        # All elements should be function calls
        for element in matrix.rows[0]:
            assert isinstance(element, FunctionCallNode)

    def test_matrix_access_in_expression(self):
        """Test matrix element access"""
        ast = self.parse_source("result = matrix[i][j] + 5")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)

        # Should be a binary operation
        expr = ast.body[0].value
        assert isinstance(expr, BinaryOpNode)
        assert expr.operator == "+"

        # Left side should be matrix access
        assert isinstance(expr.left, FunctionCallNode)
        assert expr.left.function.name == "__getitem__"

    def test_nested_lists_complex(self):
        """Test more complex nested list structures"""
        ast = self.parse_source("data = [[1, 2, 3], [4, 5], [6]]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 3
        assert len(matrix.rows[0]) == 3  # First row has 3 elements
        assert len(matrix.rows[1]) == 2  # Second row has 2 elements
        assert len(matrix.rows[2]) == 1  # Third row has 1 element

    def test_string_vector(self):
        """Test vector with string elements"""
        ast = self.parse_source('names = ["Alice", "Bob", "Charlie"]')
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 1
        assert len(matrix.rows[0]) == 3

        # Check that all elements are strings
        for element in matrix.rows[0]:
            assert isinstance(element, StringNode)

    def test_single_element_list(self):
        """Test single element list"""
        ast = self.parse_source("single = [42]")
        assert isinstance(ast, ProgramNode)
        assert len(ast.body) == 1
        assert isinstance(ast.body[0], AssignmentNode)
        assert isinstance(ast.body[0].value, MatrixNode)

        matrix = ast.body[0].value
        assert len(matrix.rows) == 1
        assert len(matrix.rows[0]) == 1
        assert matrix.rows[0][0].value == 42.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])