# Qubit-Flow Quantum Computing Language - Parser
# Complementary to Synapse-Lang for pure quantum computation

from typing import List, Optional, Dict, Any
from qubit_flow_lexer import QubitFlowLexer, Token, TokenType
from qubit_flow_ast import *

class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at line {token.line}, column {token.column}: {message}")

class QubitFlowParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        if self.position < len(self.tokens) - 1:
            self.position += 1
            self.current_token = self.tokens[self.position]
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        peek_pos = self.position + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def expect(self, token_type: TokenType) -> Token:
        if self.current_token.type != token_type:
            raise ParseError(f"Expected {token_type}, got {self.current_token.type}", self.current_token)
        token = self.current_token
        self.advance()
        return token
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current_token.type in token_types
    
    def skip_newlines(self):
        while self.current_token.type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> ProgramNode:
        statements = []
        
        while self.current_token.type != TokenType.EOF:
            self.skip_newlines()
            if self.current_token.type == TokenType.EOF:
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return ProgramNode(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        
        if self.match(TokenType.QUBIT):
            return self.parse_qubit_declaration()
        elif self.match(TokenType.QUDIT):
            return self.parse_qudit_declaration()
        elif self.match(TokenType.CIRCUIT):
            return self.parse_circuit_definition()
        elif self.match(TokenType.MEASURE):
            return self.parse_measurement()
        elif self.match(TokenType.ENTANGLE):
            return self.parse_entanglement()
        elif self.match(TokenType.SUPERPOSE):
            return self.parse_superposition()
        elif self.match(TokenType.TELEPORT):
            return self.parse_teleportation()
        elif self.match(TokenType.GROVERS):
            return self.parse_grovers_algorithm()
        elif self.match(TokenType.SHORS):
            return self.parse_shors_algorithm()
        elif self.match(TokenType.VQE):
            return self.parse_vqe_algorithm()
        elif self.match(TokenType.QFT):
            return self.parse_qft()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.IDENTIFIER):
            return self.parse_assignment_or_gate()
        else:
            # Skip unknown tokens
            self.advance()
            return None
    
    def parse_qubit_declaration(self) -> QubitNode:
        self.expect(TokenType.QUBIT)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        initial_state = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initial_state = self.parse_ket_state()
        
        return QubitNode(name_token.value, initial_state, name_token.line, name_token.column)
    
    def parse_qudit_declaration(self) -> QuditleNode:
        self.expect(TokenType.QUDIT)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        self.expect(TokenType.LBRACKET)
        dimension_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.RBRACKET)
        
        initial_state = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initial_state = self.parse_ket_state()
        
        return QuditleNode(name_token.value, int(dimension_token.value), 
                          initial_state, name_token.line, name_token.column)
    
    def parse_circuit_definition(self) -> QuantumCircuitNode:
        circuit_token = self.expect(TokenType.CIRCUIT)
        name_token = self.expect(TokenType.IDENTIFIER)
        
        self.expect(TokenType.LPAREN)
        qubits = []
        
        if not self.match(TokenType.RPAREN):
            qubit_token = self.expect(TokenType.IDENTIFIER)
            qubits.append(qubit_token.value)
            
            while self.match(TokenType.COMMA):
                self.advance()
                qubit_token = self.expect(TokenType.IDENTIFIER)
                qubits.append(qubit_token.value)
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        
        gates = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            
            gate = self.parse_quantum_gate()
            if gate:
                gates.append(gate)
        
        self.expect(TokenType.RBRACE)
        return QuantumCircuitNode(name_token.value, qubits, gates, 
                                circuit_token.line, circuit_token.column)
    
    def parse_quantum_gate(self) -> Optional[QuantumGateNode]:
        if not self.match(TokenType.H, TokenType.X, TokenType.Y, TokenType.Z,
                         TokenType.CNOT, TokenType.CZ, TokenType.RX, TokenType.RY,
                         TokenType.RZ, TokenType.PHASE, TokenType.TOFFOLI):
            return None
        
        gate_token = self.current_token
        gate_type = gate_token.value
        self.advance()
        
        # Parse parameters (for parameterized gates)
        parameters = []
        if self.match(TokenType.LPAREN):
            self.advance()
            if not self.match(TokenType.RPAREN):
                parameters.append(self.parse_expression())
                while self.match(TokenType.COMMA):
                    self.advance()
                    parameters.append(self.parse_expression())
            self.expect(TokenType.RPAREN)
        
        # Parse target qubits
        qubits = []
        if self.match(TokenType.LBRACKET):
            self.advance()
            qubit_token = self.expect(TokenType.IDENTIFIER)
            qubits.append(qubit_token.value)
            
            while self.match(TokenType.COMMA):
                self.advance()
                qubit_token = self.expect(TokenType.IDENTIFIER)
                qubits.append(qubit_token.value)
            
            self.expect(TokenType.RBRACKET)
        
        return QuantumGateNode(gate_type, qubits, parameters,
                             gate_token.line, gate_token.column)
    
    def parse_measurement(self) -> MeasurementNode:
        measure_token = self.expect(TokenType.MEASURE)
        qubit_token = self.expect(TokenType.IDENTIFIER)
        
        classical_bit = None
        if self.match(TokenType.ARROW):
            self.advance()
            classical_token = self.expect(TokenType.IDENTIFIER)
            classical_bit = classical_token.value
        
        return MeasurementNode(qubit_token.value, classical_bit,
                             measure_token.line, measure_token.column)
    
    def parse_entanglement(self) -> EntanglementNode:
        entangle_token = self.expect(TokenType.ENTANGLE)
        
        self.expect(TokenType.LPAREN)
        qubits = []
        
        qubit_token = self.expect(TokenType.IDENTIFIER)
        qubits.append(qubit_token.value)
        
        while self.match(TokenType.COMMA):
            self.advance()
            qubit_token = self.expect(TokenType.IDENTIFIER)
            qubits.append(qubit_token.value)
        
        self.expect(TokenType.RPAREN)
        
        # Optional entanglement type
        entanglement_type = "bell"
        if self.match(TokenType.IDENTIFIER):
            entanglement_type = self.current_token.value
            self.advance()
        
        return EntanglementNode(qubits, entanglement_type,
                              entangle_token.line, entangle_token.column)
    
    def parse_superposition(self) -> SuperpositionNode:
        superpose_token = self.expect(TokenType.SUPERPOSE)
        qubit_token = self.expect(TokenType.IDENTIFIER)
        
        self.expect(TokenType.LBRACE)
        amplitudes = {}
        
        while not self.match(TokenType.RBRACE):
            state_token = self.expect(TokenType.STRING)
            self.expect(TokenType.ASSIGN)
            amplitude = self.parse_complex_number()
            amplitudes[state_token.value] = amplitude
            
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RBRACE)
        
        return SuperpositionNode(qubit_token.value, amplitudes,
                               superpose_token.line, superpose_token.column)
    
    def parse_teleportation(self) -> QuantumTeleportationNode:
        teleport_token = self.expect(TokenType.TELEPORT)
        
        source_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ARROW)
        
        self.expect(TokenType.LPAREN)
        entangled1_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.COMMA)
        entangled2_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.ARROW)
        target_token = self.expect(TokenType.IDENTIFIER)
        
        return QuantumTeleportationNode(
            source_token.value,
            [entangled1_token.value, entangled2_token.value],
            target_token.value,
            teleport_token.line, teleport_token.column
        )
    
    def parse_grovers_algorithm(self) -> GroversAlgorithmNode:
        grovers_token = self.expect(TokenType.GROVERS)
        
        self.expect(TokenType.LPAREN)
        search_space_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.COMMA)
        oracle = self.parse_expression()
        
        iterations = None
        if self.match(TokenType.COMMA):
            self.advance()
            iterations_token = self.expect(TokenType.NUMBER)
            iterations = int(iterations_token.value)
        
        self.expect(TokenType.RPAREN)
        
        return GroversAlgorithmNode(int(search_space_token.value), oracle, iterations,
                                  grovers_token.line, grovers_token.column)
    
    def parse_shors_algorithm(self) -> ShorsAlgorithmNode:
        shors_token = self.expect(TokenType.SHORS)
        
        self.expect(TokenType.LPAREN)
        number_token = self.expect(TokenType.NUMBER)
        self.expect(TokenType.RPAREN)
        
        return ShorsAlgorithmNode(int(number_token.value),
                                shors_token.line, shors_token.column)
    
    def parse_vqe_algorithm(self) -> VQENode:
        vqe_token = self.expect(TokenType.VQE)
        
        self.expect(TokenType.LPAREN)
        hamiltonian = self.parse_expression()
        self.expect(TokenType.COMMA)
        ansatz = self.parse_expression()
        
        optimizer = "COBYLA"
        if self.match(TokenType.COMMA):
            self.advance()
            optimizer_token = self.expect(TokenType.STRING)
            optimizer = optimizer_token.value
        
        self.expect(TokenType.RPAREN)
        
        return VQENode(hamiltonian, ansatz, optimizer,
                     vqe_token.line, vqe_token.column)
    
    def parse_qft(self) -> QFTNode:
        qft_token = self.expect(TokenType.QFT)
        
        self.expect(TokenType.LPAREN)
        qubits = []
        
        qubit_token = self.expect(TokenType.IDENTIFIER)
        qubits.append(qubit_token.value)
        
        while self.match(TokenType.COMMA):
            self.advance()
            qubit_token = self.expect(TokenType.IDENTIFIER)
            qubits.append(qubit_token.value)
        
        self.expect(TokenType.RPAREN)
        
        # Check for inverse flag
        inverse = False
        if self.match(TokenType.IDENTIFIER) and self.current_token.value == "inverse":
            inverse = True
            self.advance()
        
        return QFTNode(qubits, inverse, qft_token.line, qft_token.column)
    
    def parse_assignment_or_gate(self) -> ASTNode:
        identifier_token = self.expect(TokenType.IDENTIFIER)
        
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return AssignmentNode(
                IdentifierNode(identifier_token.value, identifier_token.line, identifier_token.column),
                value,
                identifier_token.line, identifier_token.column
            )
        else:
            # Might be a gate call - backtrack and try parsing as gate
            self.position -= 1
            self.current_token = self.tokens[self.position]
            return self.parse_quantum_gate()
    
    def parse_if_statement(self) -> IfQuantumNode:
        if_token = self.expect(TokenType.IF)
        
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        
        then_block = self.parse_block()
        
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_block = self.parse_block()
        
        return IfQuantumNode(condition, then_block, else_block,
                           if_token.line, if_token.column)
    
    def parse_block(self) -> BlockNode:
        self.expect(TokenType.LBRACE)
        statements = []
        
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            self.skip_newlines()
            if self.match(TokenType.RBRACE):
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.RBRACE)
        return BlockNode(statements)
    
    def parse_expression(self) -> ASTNode:
        return self.parse_primary()
    
    def parse_primary(self) -> ASTNode:
        if self.match(TokenType.NUMBER):
            token = self.current_token
            self.advance()
            return NumberNode(float(token.value), token.line, token.column)
        
        elif self.match(TokenType.COMPLEX):
            return self.parse_complex_number()
        
        elif self.match(TokenType.IDENTIFIER):
            token = self.current_token
            self.advance()
            return IdentifierNode(token.value, token.line, token.column)
        
        elif self.match(TokenType.KET):
            return self.parse_ket_state()
        
        elif self.match(TokenType.STRING):
            token = self.current_token
            self.advance()
            return IdentifierNode(token.value, token.line, token.column)
        
        else:
            raise ParseError(f"Unexpected token: {self.current_token.type}", self.current_token)
    
    def parse_ket_state(self) -> KetStateNode:
        ket_token = self.expect(TokenType.KET)
        
        if self.match(TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.STRING):
            state_token = self.current_token
            self.advance()
            return KetStateNode(state_token.value, ket_token.line, ket_token.column)
        else:
            raise ParseError("Expected state after |", self.current_token)
    
    def parse_complex_number(self) -> ComplexNumberNode:
        token = self.expect(TokenType.COMPLEX)
        
        # Parse complex number string (e.g., "1+2i", "0.5-0.3i")
        complex_str = token.value
        
        # Simple regex-based parsing for complex numbers
        import re
        match = re.match(r'([+-]?\d*\.?\d*)[+-](\d*\.?\d*)i', complex_str)
        if match:
            real_part = float(match.group(1)) if match.group(1) else 0.0
            imag_part = float(match.group(2)) if match.group(2) else 1.0
            if '-' in complex_str.split(match.group(1))[1]:
                imag_part = -imag_part
        else:
            # Handle pure imaginary (e.g., "2i")
            if complex_str.endswith('i'):
                real_part = 0.0
                imag_part = float(complex_str[:-1]) if complex_str[:-1] else 1.0
            else:
                real_part = float(complex_str)
                imag_part = 0.0
        
        return ComplexNumberNode(real_part, imag_part, token.line, token.column)

def parse_qubit_flow(source: str) -> ProgramNode:
    lexer = QubitFlowLexer(source)
    tokens = lexer.tokenize()
    parser = QubitFlowParser(tokens)
    return parser.parse()