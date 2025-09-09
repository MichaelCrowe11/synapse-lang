"""Packaged parser with run/noise additions."""
from typing import List, Optional, Dict
from .synapse_lexer import Token, TokenType, Lexer
from .synapse_ast import *


class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        super().__init__(f"{message} at line {token.line}, column {token.column}")
        self.token = token


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def peek(self) -> Token:
        return self.tokens[self.current]

    def advance(self) -> Token:
        tok = self.peek()
        if tok.type != TokenType.EOF:
            self.current += 1
        return tok

    def check(self, t: TokenType) -> bool:
        return self.peek().type == t

    def match(self, *types: TokenType) -> bool:
        return any(self.check(t) for t in types)

    def consume(self, t: TokenType, msg: str) -> Token:
        if self.check(t):
            return self.advance()
        raise ParseError(msg, self.peek())

    def skip_newlines(self):
        while self.check(TokenType.NEWLINE):
            self.advance()

    def parse(self) -> ProgramNode:
        body = []
        while not self.check(TokenType.EOF):
            self.skip_newlines()
            if self.check(TokenType.EOF):
                break
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        return ProgramNode(body)

    def parse_statement(self):  # subset focusing on quantum+run
        if self.check(TokenType.QUANTUM):
            return self.parse_quantum()
        if self.check(TokenType.RUN):
            return self.parse_run()
        # Fallback expression only (reuse primary for now)
        return self.parse_expression()

    # --- RUN ---
    def parse_run(self) -> RunNode:
        run_tok = self.advance()
        circuit = self.consume(TokenType.IDENTIFIER, "Expected circuit name after 'run'").value
        backend_name = None
        options: Dict[str, ASTNode] = {}
        if self.match(TokenType.WITH):
            self.advance()
            if self.match(TokenType.BACKEND):
                self.advance()
            backend_name = self.consume(TokenType.IDENTIFIER, "Expected backend name").value
        if self.match(TokenType.LEFT_BRACE):
            self.advance()
            self.skip_newlines()
            while not self.check(TokenType.RIGHT_BRACE):
                self.skip_newlines()
                key_tok = self.consume(TokenType.IDENTIFIER, "Expected option key")
                self.consume(TokenType.COLON, "Expected ':' after option key")
                # Accept numbers/identifiers/strings simplest
                if self.check(TokenType.NUMBER):
                    num = self.advance()
                    options[key_tok.value] = NumberNode(num.value, num.line, num.column)
                elif self.check(TokenType.STRING):
                    s = self.advance()
                    options[key_tok.value] = StringNode(s.value, s.line, s.column)
                elif self.check(TokenType.IDENTIFIER):
                    ident = self.advance()
                    options[key_tok.value] = IdentifierNode(ident.value, ident.line, ident.column)
                self.skip_newlines()
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close run options")
        return RunNode(circuit, backend_name, options, run_tok.line, run_tok.column)

    # --- Quantum constructs (minimal subset reused) ---
    def parse_quantum(self):
        self.advance()  # consume 'quantum'
        if self.check(TokenType.CIRCUIT):
            return self.parse_quantum_circuit()
        if self.check(TokenType.BACKEND):
            return self.parse_quantum_backend()
        if self.check(TokenType.ALGORITHM):
            return self.parse_quantum_algorithm()
        return self.parse_block()

    def parse_quantum_circuit(self):
        circ_tok = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value
        qubits = 1
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            if self.check(TokenType.NUMBER):
                qubits = int(self.advance().value)
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after qubit count")
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after circuit name")
        gates = []
        measures = []
        self.skip_newlines()
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            if self.match(TokenType.H, TokenType.X, TokenType.Y, TokenType.Z, TokenType.CNOT, TokenType.CX, TokenType.RX, TokenType.RY, TokenType.RZ):
                gates.append(self.parse_quantum_gate())
            elif self.check(TokenType.MEASURE):
                measures.append(self.parse_quantum_measure())
            else:
                self.advance()
            self.skip_newlines()
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close circuit")
        return QuantumCircuitNode(name, qubits, gates, measures, circ_tok.line, circ_tok.column)

    def parse_quantum_gate(self):
        gate_tok = self.advance()
        gate_name = gate_tok.value
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after gate")
        qubits = []
        params = []
        if not self.check(TokenType.RIGHT_PAREN):
            qubits.append(self.parse_expression())
            while self.check(TokenType.COMMA):
                self.advance()
                # treat rotations parameter wise
                expr = self.parse_expression()
                if gate_name in {"rx", "ry", "rz"} and len(qubits) == 1:
                    params.append(expr)
                else:
                    qubits.append(expr)
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after gate args")
        return QuantumGateNode(gate_name, qubits, params, gate_tok.line, gate_tok.column)

    def parse_quantum_measure(self):
        m_tok = self.advance()
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after measure")
        qubits = []
        if not self.check(TokenType.RIGHT_PAREN):
            qubits.append(self.parse_expression())
            while self.check(TokenType.COMMA):
                self.advance(); qubits.append(self.parse_expression())
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after measure args")
        return QuantumMeasureNode(qubits, [], m_tok.line, m_tok.column)

    def parse_quantum_backend(self):
        b_tok = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected backend name").value
        cfg: Dict[str, ASTNode] = {}
        if self.match(TokenType.LEFT_BRACE):
            self.advance(); self.skip_newlines()
            while not self.check(TokenType.RIGHT_BRACE):
                self.skip_newlines()
                key = self.consume(TokenType.IDENTIFIER, "Expected key").value
                self.consume(TokenType.COLON, "Expected ':' after key")
                if self.check(TokenType.NUMBER):
                    num = self.advance(); cfg[key] = NumberNode(num.value, num.line, num.column)
                elif self.check(TokenType.STRING):
                    s = self.advance(); cfg[key] = StringNode(s.value, s.line, s.column)
                elif self.check(TokenType.IDENTIFIER):
                    i = self.advance(); cfg[key] = IdentifierNode(i.value, i.line, i.column)
                self.skip_newlines()
            self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return QuantumBackendNode(name, cfg, b_tok.line, b_tok.column)

    def parse_quantum_algorithm(self):
        a_tok = self.advance()
        name = self.consume(TokenType.IDENTIFIER, "Expected algorithm name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        params: List[ASTNode] = []
        ansatz = QuantumAnsatzNode("default", [], a_tok.line, a_tok.column)
        cost = None
        opt = None
        self.skip_newlines()
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            if self.check(TokenType.IDENTIFIER):
                field = self.peek().value
                if field == "parameters":
                    self.advance(); self.consume(TokenType.COLON, "Expected ':'")
                    if self.match(TokenType.LEFT_BRACKET):
                        self.advance()
                        if not self.check(TokenType.RIGHT_BRACKET):
                            ident_tok = self.consume(TokenType.IDENTIFIER, "Expected parameter")
                            params.append(IdentifierNode(ident_tok.value, ident_tok.line, ident_tok.column))
                            while self.check(TokenType.COMMA):
                                self.advance(); ident_tok = self.consume(TokenType.IDENTIFIER, "Expected parameter")
                                params.append(IdentifierNode(ident_tok.value, ident_tok.line, ident_tok.column))
                        self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after parameters")
                elif field == "ansatz":
                    self.advance(); self.consume(TokenType.COLON, "Expected ':'")
                    if self.check(TokenType.IDENTIFIER):
                        t = self.advance(); ansatz = QuantumAnsatzNode(t.value, [], t.line, t.column)
                elif field == "cost_function":
                    self.advance(); self.consume(TokenType.COLON, "Expected ':'")
                    cost = self.parse_expression()
                elif field == "optimize":
                    self.advance(); self.consume(TokenType.COLON, "Expected ':'")
                    opt = self.parse_expression()
                else:
                    self.advance()
            self.skip_newlines()
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return QuantumAlgorithmNode(name, params, ansatz, cost, opt, a_tok.line, a_tok.column)

    # --- blocks / expressions ---
    def parse_block(self):
        start = self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        self.skip_newlines()
        stmts = []
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            if self.check(TokenType.RIGHT_BRACE):
                break
            stmts.append(self.parse_statement())
            self.skip_newlines()
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return BlockNode(stmts, start.line, start.column)

    def parse_expression(self):
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if self.check(TokenType.NUMBER):
            self.advance(); return NumberNode(tok.value, tok.line, tok.column)
        if self.check(TokenType.STRING):
            self.advance(); return StringNode(tok.value, tok.line, tok.column)
        if self.check(TokenType.IDENTIFIER):
            self.advance(); return IdentifierNode(tok.value, tok.line, tok.column)
        if self.check(TokenType.LEFT_PAREN):
            self.advance(); expr = self.parse_expression(); self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expr"); return expr
        if self.check(TokenType.LEFT_BRACE):
            return self.parse_block()
        return IdentifierNode("<error>", tok.line, tok.column)


def parse(source: str) -> ProgramNode:
    return Parser(Lexer(source).tokenize()).parse()
