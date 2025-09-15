"""
Minimal Parser for Synapse Language
Focuses on core functionality that we can test
"""

from typing import List, Optional, Union
from synapse_lang.synapse_lexer import Token, TokenType, Lexer
from synapse_lang.synapse_ast_enhanced import *

class ParserError(Exception):
    """Parser error exception"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.column}")

class MinimalParser:
    """Minimal parser implementation for core features"""

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = lexer.tokenize()
        self.current = 0

    def peek(self, offset: int = 0) -> Token:
        """Look at token at current + offset position"""
        pos = self.current + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF token

    def advance(self) -> Token:
        """Consume and return current token"""
        token = self.peek()
        if token.type != TokenType.EOF:
            self.current += 1
        return token

    def check(self, token_type: TokenType) -> bool:
        """Check if current token matches type"""
        return self.peek().type == token_type

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        for token_type in token_types:
            if self.check(token_type):
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise error"""
        if self.check(token_type):
            return self.advance()
        raise ParserError(message, self.peek())

    def skip_newlines(self):
        """Skip newline tokens"""
        while self.check(TokenType.NEWLINE):
            self.advance()

    def parse(self) -> ProgramNode:
        """Parse tokens into AST"""
        statements = []

        while not self.check(TokenType.EOF):
            self.skip_newlines()
            if not self.check(TokenType.EOF):
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.skip_newlines()

        return ProgramNode(statements)

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        self.skip_newlines()

        # Tensor declaration
        if self.check(TokenType.IDENTIFIER) and self.peek().value == "tensor":
            return self.parse_tensor_declaration()

        # Variable assignment
        if self.check(TokenType.IDENTIFIER):
            return self.parse_identifier_statement()

        # Uncertain declaration
        if self.check(TokenType.UNCERTAIN):
            return self.parse_uncertain()

        # Quantum circuit
        if self.match(TokenType.QUANTUM):
            return self.parse_quantum_circuit()

        # Parallel block
        if self.check(TokenType.PARALLEL):
            return self.parse_parallel()

        # Hypothesis
        if self.check(TokenType.HYPOTHESIS):
            return self.parse_hypothesis()

        # Expression statement
        return self.parse_expression()

    def parse_identifier_statement(self) -> ASTNode:
        """Parse statement starting with identifier"""
        name = self.advance().value

        # Check for assignment
        if self.check(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return AssignmentNode(name, value)

        # Otherwise treat as expression
        return IdentifierNode(name)

    def parse_uncertain(self) -> AssignmentNode:
        """Parse uncertain value declaration"""
        self.consume(TokenType.UNCERTAIN, "Expected 'uncertain'")
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.ASSIGN, "Expected '='")

        # Parse value
        value = self.parse_primary()

        # Check for uncertainty (±)
        if self.check(TokenType.UNCERTAINTY_OP):
            op_token = self.advance()
            uncertainty = self.parse_primary()
            # For now, combine into a BinaryOpNode
            value = BinaryOpNode(value, op_token.value, uncertainty)

        return AssignmentNode(name, value, is_uncertain=True)

    def parse_quantum_circuit(self) -> QuantumCircuitNode:
        """Parse quantum circuit with gates and measurements"""
        self.consume(TokenType.QUANTUM, "Expected 'quantum'")

        # Check for 'circuit'
        if self.check(TokenType.CIRCUIT):
            self.advance()

        name = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value
        self.consume(TokenType.COLON, "Expected ':'")

        # Parse qubits declaration
        self.skip_newlines()
        self.consume(TokenType.IDENTIFIER, "Expected 'qubits'")
        self.consume(TokenType.COLON, "Expected ':'")
        qubits = int(self.consume(TokenType.NUMBER, "Expected number of qubits").value)

        # Parse gates and measurements
        gates = []
        measurements = []

        self.skip_newlines()

        # Parse circuit body (simplified - looking for gates and measurements)
        while not self.check(TokenType.EOF) and not self.check(TokenType.QUANTUM) and not self.check(TokenType.PARALLEL) and not self.check(TokenType.HYPOTHESIS):
            self.skip_newlines()
            if self.check(TokenType.EOF):
                break

            # Check for gate calls or measurements
            if self.check(TokenType.IDENTIFIER) or self.check(TokenType.MEASURE) or self.is_gate_token():
                # Could be a gate call like H(0) or measurement like measure(0)
                if self.peek().value == "measure" or self.check(TokenType.MEASURE):
                    measurements.append(self.parse_quantum_measurement())
                elif self.check(TokenType.IDENTIFIER) and self.peek().value == "gates":
                    # Skip 'gates:' line and parse gate list
                    self.advance()  # consume 'gates'
                    self.consume(TokenType.COLON, "Expected ':'")
                    self.skip_newlines()
                    # Parse individual gates
                    while (self.check(TokenType.IDENTIFIER) and self.is_gate_name(self.peek().value)) or self.is_gate_token():
                        gates.append(self.parse_quantum_gate())
                        self.skip_newlines()
                elif (self.check(TokenType.IDENTIFIER) and self.is_gate_name(self.peek().value)) or self.is_gate_token():
                    # Direct gate call
                    gates.append(self.parse_quantum_gate())
                else:
                    # Unknown identifier, stop parsing circuit
                    break
            else:
                break

            self.skip_newlines()

        return QuantumCircuitNode(name, qubits, gates, measurements)

    def is_gate_name(self, name: str) -> bool:
        """Check if identifier is a known quantum gate name"""
        gate_names = {
            "H", "X", "Y", "Z", "S", "T", "CX", "CNOT", "CZ", "SWAP",
            "RX", "RY", "RZ", "U", "CCX", "TOFFOLI", "CSWAP"
        }
        return name.upper() in gate_names

    def is_gate_token(self) -> bool:
        """Check if current token is a gate token"""
        gate_token_types = {
            TokenType.H, TokenType.X, TokenType.Y, TokenType.Z,
            TokenType.S, TokenType.T, TokenType.CX, TokenType.CZ,
            TokenType.CCX, TokenType.SWAP, TokenType.TOFFOLI, TokenType.CSWAP,
            TokenType.RX, TokenType.RY, TokenType.RZ, TokenType.U, TokenType.CNOT
        }
        return self.peek().type in gate_token_types

    def parse_quantum_gate(self) -> QuantumGateNode:
        """Parse quantum gate like H(0) or CX(0, 1)"""
        # Handle both IDENTIFIER tokens and specific gate tokens
        if self.is_gate_token():
            gate_name = self.advance().value.upper()
        elif self.check(TokenType.IDENTIFIER) and self.is_gate_name(self.peek().value):
            gate_name = self.advance().value.upper()
        else:
            raise ParserError("Expected gate name", self.peek())

        self.consume(TokenType.LEFT_PAREN, "Expected '('")

        # Parse qubit indices
        qubits = []
        if not self.check(TokenType.RIGHT_PAREN):
            qubits.append(int(self.consume(TokenType.NUMBER, "Expected qubit index").value))
            while self.check(TokenType.COMMA):
                self.advance()
                qubits.append(int(self.consume(TokenType.NUMBER, "Expected qubit index").value))

        self.consume(TokenType.RIGHT_PAREN, "Expected ')'")

        return QuantumGateNode(gate_name, qubits)

    def parse_quantum_measurement(self) -> QuantumMeasurementNode:
        """Parse quantum measurement like measure(0) or measure("all")"""
        # Handle both IDENTIFIER 'measure' and MEASURE token
        if self.check(TokenType.MEASURE):
            self.advance()
        else:
            self.consume(TokenType.IDENTIFIER, "Expected 'measure'")

        self.consume(TokenType.LEFT_PAREN, "Expected '('")

        # Parse what to measure - can be qubit index or "all"
        if self.check(TokenType.STRING):
            qubits = self.advance().value  # "all" or similar
        elif self.check(TokenType.NUMBER):
            qubits = [int(self.advance().value)]
        else:
            qubits = "all"  # default

        self.consume(TokenType.RIGHT_PAREN, "Expected ')'")

        return QuantumMeasurementNode(qubits)

    def parse_parallel(self) -> ParallelNode:
        """Parse parallel block (simplified)"""
        self.consume(TokenType.PARALLEL, "Expected 'parallel'")
        self.consume(TokenType.COLON, "Expected ':'")

        branches = []
        self.skip_newlines()

        # Parse branches
        while self.check(TokenType.BRANCH):
            self.advance()
            branch_name = self.consume(TokenType.IDENTIFIER, "Expected branch name").value
            self.consume(TokenType.COLON, "Expected ':'")

            # For now, just parse identifier as body
            body = self.parse_expression()
            branches.append(BranchNode(branch_name, body))
            self.skip_newlines()

        return ParallelNode(branches)

    def parse_hypothesis(self) -> HypothesisNode:
        """Parse hypothesis (simplified)"""
        self.consume(TokenType.HYPOTHESIS, "Expected 'hypothesis'")
        name = self.consume(TokenType.IDENTIFIER, "Expected hypothesis name").value
        self.consume(TokenType.COLON, "Expected ':'")

        assumptions = []
        predictions = []

        self.skip_newlines()

        # Parse assume
        if self.check(TokenType.ASSUME):
            self.advance()
            self.consume(TokenType.COLON, "Expected ':'")
            assumptions.append(self.parse_expression())
            self.skip_newlines()

        # Parse predict
        if self.check(TokenType.PREDICT):
            self.advance()
            self.consume(TokenType.COLON, "Expected ':'")
            predictions.append(self.parse_expression())

        return HypothesisNode(name, assumptions, predictions)

    def parse_expression(self) -> ASTNode:
        """Parse expression with proper operator precedence"""
        return self.parse_logical_or()

    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR (lowest precedence)"""
        left = self.parse_logical_and()

        while self.check(TokenType.OR):
            op = self.advance()
            right = self.parse_logical_and()
            left = BinaryOpNode(left, op.value, right)

        return left

    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND"""
        left = self.parse_equality()

        while self.check(TokenType.AND):
            op = self.advance()
            right = self.parse_equality()
            left = BinaryOpNode(left, op.value, right)

        return left

    def parse_equality(self) -> ASTNode:
        """Parse equality operators"""
        left = self.parse_comparison()

        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            op = self.advance()
            right = self.parse_comparison()
            left = BinaryOpNode(left, op.value, right)

        return left

    def parse_comparison(self) -> ASTNode:
        """Parse comparison operators"""
        left = self.parse_addition()

        while self.match(TokenType.GREATER_THAN, TokenType.LESS_THAN,
                         TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL):
            op = self.advance()
            right = self.parse_addition()
            left = BinaryOpNode(left, op.value, right)

        return left

    def parse_addition(self) -> ASTNode:
        """Parse addition and subtraction"""
        left = self.parse_multiplication()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_multiplication()
            left = BinaryOpNode(left, op.value, right)

        return left

    def parse_multiplication(self) -> ASTNode:
        """Parse multiplication and division"""
        left = self.parse_exponentiation()

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.advance()
            right = self.parse_exponentiation()
            left = BinaryOpNode(left, op.value, right)

        return left

    def parse_exponentiation(self) -> ASTNode:
        """Parse exponentiation (right associative)"""
        left = self.parse_unary()

        if self.check(TokenType.POWER):
            op = self.advance()
            right = self.parse_exponentiation()  # Right associative
            return BinaryOpNode(left, op.value, right)

        return left

    def parse_unary(self) -> ASTNode:
        """Parse unary operators"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance()
            expr = self.parse_unary()
            return UnaryOpNode(op.value, expr)

        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        """Parse postfix expressions (function calls, array access)"""
        expr = self.parse_primary()

        while True:
            if self.check(TokenType.LEFT_PAREN):
                # Function call
                self.advance()
                args = []

                if not self.check(TokenType.RIGHT_PAREN):
                    args.append(self.parse_expression())
                    while self.check(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())

                self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
                expr = FunctionCallNode(expr, args)

            elif self.check(TokenType.LEFT_BRACKET):
                # Array/tensor access (for future implementation)
                self.advance()
                index = self.parse_expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
                # For now, create a function call node representing array access
                expr = FunctionCallNode(IdentifierNode("__getitem__"), [expr, index])

            else:
                break

        return expr

    def parse_primary(self) -> ASTNode:
        """Parse primary expression"""
        # Number literal
        if self.check(TokenType.NUMBER):
            value = self.advance().value
            return NumberNode(float(value))

        # String literal
        if self.check(TokenType.STRING):
            value = self.advance().value
            return StringNode(value)

        # Boolean literals
        if self.check(TokenType.IDENTIFIER):
            if self.peek().value in ["true", "false"]:
                value = self.advance().value == "true"
                return BooleanNode(value)

        # Identifier
        if self.check(TokenType.IDENTIFIER):
            name = self.advance().value
            return IdentifierNode(name)

        # Matrix/List literal
        if self.check(TokenType.LEFT_BRACKET):
            return self.parse_matrix_literal()

        # Grouped expression
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
            return expr

        raise ParserError(f"Unexpected token: {self.peek()}", self.peek())

    def parse_matrix_literal(self) -> MatrixNode:
        """Parse matrix/list literal like [[1, 2], [3, 4]] or [1, 2, 3]"""
        self.consume(TokenType.LEFT_BRACKET, "Expected '['")

        rows = []

        # Handle empty list
        if self.check(TokenType.RIGHT_BRACKET):
            self.advance()
            return MatrixNode([])

        # Parse first element to determine if this is a matrix or vector
        first_element = self.parse_expression()

        # If first element is another list, this is a matrix
        if isinstance(first_element, MatrixNode):
            # This is a matrix - first element is a row
            rows.append(first_element.rows[0] if first_element.rows else [])

            # Parse remaining rows
            while self.check(TokenType.COMMA):
                self.advance()
                if self.check(TokenType.RIGHT_BRACKET):
                    break
                row_element = self.parse_expression()
                if isinstance(row_element, MatrixNode) and row_element.rows:
                    rows.append(row_element.rows[0])
                else:
                    # Convert single element to row
                    rows.append([row_element])
        else:
            # This is a vector - convert to single row matrix
            row = [first_element]

            # Parse remaining elements
            while self.check(TokenType.COMMA):
                self.advance()
                if self.check(TokenType.RIGHT_BRACKET):
                    break
                row.append(self.parse_expression())

            rows.append(row)

        self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
        return MatrixNode(rows)

    def parse_tensor_declaration(self) -> TensorNode:
        """Parse tensor declaration like tensor T[3,3,3] = values"""
        # This would be called from parse_statement when we see 'tensor' keyword
        self.consume(TokenType.IDENTIFIER, "Expected 'tensor'")  # 'tensor'
        name = self.consume(TokenType.IDENTIFIER, "Expected tensor name").value

        # Parse dimensions
        self.consume(TokenType.LEFT_BRACKET, "Expected '['")
        dimensions = []

        if not self.check(TokenType.RIGHT_BRACKET):
            dimensions.append(int(self.consume(TokenType.NUMBER, "Expected dimension").value))
            while self.check(TokenType.COMMA):
                self.advance()
                dimensions.append(int(self.consume(TokenType.NUMBER, "Expected dimension").value))

        self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")

        # Optional initializer
        initializer = None
        if self.check(TokenType.ASSIGN):
            self.advance()
            initializer = self.parse_expression()

        return TensorNode(name, dimensions, initializer)