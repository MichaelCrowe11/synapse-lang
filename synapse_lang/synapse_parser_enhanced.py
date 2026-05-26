"""
Enhanced Parser for Synapse Language
Phase 1, Week 1, Day 1-2
Implements complete parsing for all language constructs
"""

from typing import Optional, List
from synapse_lang.synapse_ast_enhanced import *  # noqa: F403
from synapse_lang.synapse_ast import (  # noqa: F401
    QuantumAlgorithmNode,
    QuantumAnsatzNode,
    QuantumBackendNode,
    QuantumNoiseNode,
    StreamNode,
    UncertainNode,
)
from synapse_lang.synapse_lexer import Lexer, Token, TokenType


class ParserError(Exception):
    """Parser error with line and column information"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.line = token.line
        self.column = token.column
        super().__init__(f"Parser error at line {self.line}, column {self.column}: {message}")


class EnhancedParser:
    """Complete recursive descent parser for Synapse language"""

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = []
        self.current = 0
        self.errors = []

    def parse(self) -> ProgramNode:
        """Parse entire program"""
        self.tokens = self.lexer.tokenize()
        statements = []

        while not self.is_at_end():
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParserError as e:
                self.errors.append(e)
                self.synchronize()

        return ProgramNode(statements)

    # ========== Statement Parsing ==========

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        # Skip newlines
        while self.match(TokenType.NEWLINE):
            pass

        if self.is_at_end():
            return None

        # Quantum constructs
        if self.match(TokenType.QUANTUM):
            return self.parse_quantum_statement()

        # Scientific computing constructs
        if self.match(TokenType.HYPOTHESIS):
            return self.parse_hypothesis()
        if self.match(TokenType.EXPERIMENT):
            return self.parse_experiment()
        if self.match(TokenType.PARALLEL):
            return self.parse_parallel()
        if self.match(TokenType.STREAM):
            return self.parse_stream()

        # Reasoning constructs
        if self.match(TokenType.REASON):
            return self.parse_reason_chain()
        if self.check(TokenType.IDENTIFIER) and self.peek().value == "reason_chain":
            self.advance()
            return self.parse_reason_chain()

        # Pipeline constructs
        if self.match(TokenType.PIPELINE):
            return self.parse_pipeline()

        # Exploration constructs
        if self.match(TokenType.EXPLORE):
            return self.parse_explore()

        # Symbolic math
        if self.match(TokenType.SYMBOLIC):
            return self.parse_symbolic()

        # Variable declarations
        if self.match(TokenType.TENSOR):
            return self.parse_tensor_declaration()
        if self.match(TokenType.UNCERTAIN):
            return self.parse_uncertain_declaration()
        if self.match(TokenType.CONSTRAIN):
            return self.parse_constrain()
        if self.match(TokenType.EVOLVE):
            return self.parse_evolve()
        if self.match(TokenType.OBSERVE):
            return self.parse_observe()

        # Control flow
        if self.match(TokenType.IF):
            return self.parse_if()
        if self.match(TokenType.WHILE):
            return self.parse_while()
        if self.match(TokenType.FOR):
            return self.parse_for()
        if self.match(TokenType.RETURN):
            return self.parse_return()
        if self.match(TokenType.BREAK):
            return self.parse_break()
        if self.match(TokenType.CONTINUE):
            return self.parse_continue()

        # Run statement
        if self.match(TokenType.RUN):
            return self.parse_run()

        if self.is_at_end():
            return None

        # Expression statement or assignment
        return self.parse_expression_statement()

    # ========== Quantum Parsing ==========

    def parse_quantum_statement(self) -> ASTNode:
        """Parse quantum constructs"""
        if self.match(TokenType.CIRCUIT):
            return self.parse_quantum_circuit()
        elif self.match(TokenType.ALGORITHM):
            return self.parse_quantum_algorithm()
        elif self.match(TokenType.BACKEND):
            return self.parse_quantum_backend()
        elif self.match(TokenType.NOISE):
            return self.parse_quantum_noise()
        else:
            raise ParserError("Expected quantum construct", self.peek())

    def parse_quantum_circuit(self) -> QuantumCircuitNode:
        """Parse quantum circuit definition"""
        name = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value
        self.consume(TokenType.COLON, "Expected ':' after circuit name")

        qubits = 0
        gates = []
        measurements = []

        # Parse indented block
        self.consume(TokenType.NEWLINE, "Expected newline after ':'")
        self.consume(TokenType.INDENT, "Expected indent after circuit declaration")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.MEASURE):
                measurements.append(self.parse_quantum_measure())
            elif self.match(TokenType.IDENTIFIER):
                keyword = self.previous().value

                if keyword == "qubits":
                    self.consume(TokenType.COLON, "Expected ':' after 'qubits'")
                    qubits = int(self.consume(TokenType.NUMBER, "Expected number of qubits").value)

                elif keyword == "gates":
                    self.consume(TokenType.COLON, "Expected ':' after 'gates'")
                    self.consume(TokenType.NEWLINE, "Expected newline after 'gates:'")
                    self.consume(TokenType.INDENT, "Expected indent after 'gates:'")

                    while not self.check(TokenType.DEDENT):
                        gates.append(self.parse_quantum_gate())
                        self.skip_newlines()

                    self.consume(TokenType.DEDENT, "Expected dedent after gates")

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent after circuit body")

        return QuantumCircuitNode(name, qubits, gates, measurements,
                                 self.previous().line, self.previous().column)

    _GATE_TOKEN_TYPES = (
        TokenType.IDENTIFIER,
        TokenType.H,
        TokenType.X,
        TokenType.Y,
        TokenType.Z,
        TokenType.CX,
        TokenType.CNOT,
        TokenType.SWAP,
        TokenType.RX,
        TokenType.RY,
        TokenType.RZ,
    )

    def _consume_gate_name(self) -> str:
        """Consume a gate name token (identifier or built-in gate keyword)."""
        tok = self.peek()
        if tok.type not in self._GATE_TOKEN_TYPES:
            raise ParserError("Expected gate type", tok)
        self.advance()
        name = tok.value
        if tok.type != TokenType.IDENTIFIER:
            return name.upper()
        return name

    def parse_quantum_gate(self) -> QuantumGateNode:
        """Parse quantum gate operation"""
        gate_type = self._consume_gate_name()
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after gate name")

        qubits = []
        parameters = []

        # Parse arguments
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arg = self.parse_expression()
                if isinstance(arg, NumberNode):
                    qubits.append(int(arg.value))
                else:
                    parameters.append(arg)

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after gate arguments")

        return QuantumGateNode(gate_type, qubits, parameters,
                              self.previous().line, self.previous().column)

    def parse_quantum_measure(self) -> QuantumMeasurementNode:
        """Parse quantum measurement"""
        qubits = "all"

        if self.match(TokenType.LEFT_PAREN):
            if self.check(TokenType.STRING) and self.peek().value == "all":
                self.advance()
                qubits = "all"
            else:
                qubits = []
                while True:
                    qubits.append(int(self.consume(TokenType.NUMBER, "Expected qubit index").value))
                    if not self.match(TokenType.COMMA):
                        break

            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after measure arguments")

        return QuantumMeasurementNode(
            qubits, None, self.previous().line, self.previous().column
        )

    def parse_quantum_algorithm(self) -> QuantumAlgorithmNode:
        """Parse quantum algorithm definition"""
        name = self.consume(TokenType.IDENTIFIER, "Expected algorithm name").value
        self.consume(TokenType.COLON, "Expected ':' after algorithm name")

        parameters = []
        ansatz = None
        cost_function = None
        optimizer = None

        # Parse algorithm body
        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.IDENTIFIER):
                keyword = self.previous().value

                if keyword == "parameters":
                    self.consume(TokenType.COLON, "Expected ':'")
                    # Parse parameter list
                    parameters = self.parse_expression_list()

                elif keyword == "ansatz":
                    self.consume(TokenType.COLON, "Expected ':'")
                    ansatz = self.parse_quantum_ansatz()

                elif keyword == "cost":
                    self.consume(TokenType.COLON, "Expected ':'")
                    cost_function = self.parse_expression()

                elif keyword == "optimizer":
                    self.consume(TokenType.COLON, "Expected ':'")
                    optimizer = self.parse_expression()

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return QuantumAlgorithmNode(name, parameters, ansatz, cost_function, optimizer,
                                   self.previous().line, self.previous().column)

    def parse_quantum_ansatz(self) -> QuantumAnsatzNode:
        """Parse quantum ansatz"""
        name = self.consume(TokenType.IDENTIFIER, "Expected ansatz name").value
        layers = 1
        gates = []

        if self.match(TokenType.LEFT_PAREN):
            layers = int(self.consume(TokenType.NUMBER, "Expected number of layers").value)
            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")

        return QuantumAnsatzNode(name, layers, gates,
                                self.previous().line, self.previous().column)

    def parse_quantum_backend(self) -> QuantumBackendNode:
        """Parse quantum backend configuration"""
        name = self.consume(TokenType.IDENTIFIER, "Expected backend name").value
        config = {}

        if self.match(TokenType.LEFT_PAREN):
            # Parse configuration parameters
            while not self.check(TokenType.RIGHT_PAREN):
                key = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
                self.consume(TokenType.ASSIGN, "Expected '='")
                value = self.parse_expression()
                config[key] = value

                if not self.match(TokenType.COMMA):
                    break

            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")

        return QuantumBackendNode(name, config,
                                 self.previous().line, self.previous().column)

    def parse_quantum_noise(self) -> QuantumNoiseNode:
        """Parse quantum noise model"""
        noise_type = self.consume(TokenType.IDENTIFIER, "Expected noise type").value
        parameters = {}

        if self.match(TokenType.LEFT_PAREN):
            # Parse noise parameters
            while not self.check(TokenType.RIGHT_PAREN):
                key = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
                self.consume(TokenType.ASSIGN, "Expected '='")
                value = self.parse_expression()
                parameters[key] = value

                if not self.match(TokenType.COMMA):
                    break

            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")

        return QuantumNoiseNode(noise_type, parameters,
                               self.previous().line, self.previous().column)

    # ========== Scientific Computing Parsing ==========

    def parse_hypothesis(self) -> HypothesisNode:
        """Parse hypothesis block"""
        name = self.consume(TokenType.IDENTIFIER, "Expected hypothesis name").value
        self.consume(TokenType.COLON, "Expected ':'")

        assumptions = []
        predictions = []
        validations = []

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.ASSUME):
                self.consume(TokenType.COLON, "Expected ':'")
                assumptions.append(self.parse_expression())

            elif self.match(TokenType.PREDICT):
                self.consume(TokenType.COLON, "Expected ':'")
                predictions.append(self.parse_expression())

            elif self.match(TokenType.VALIDATE):
                self.consume(TokenType.COLON, "Expected ':'")
                validations.append(self.parse_expression())

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        validation = validations[0] if validations else None
        return HypothesisNode(
            name, assumptions, predictions, validation,
            self.previous().line, self.previous().column,
        )

    def _statements_from_block(self, block: BlockNode | None) -> list:
        if block is None:
            return []
        return list(block.statements)

    def parse_experiment(self) -> ExperimentNode:
        """Parse experiment block"""
        name = self.consume(TokenType.IDENTIFIER, "Expected experiment name").value
        self.consume(TokenType.COLON, "Expected ':'")

        setup: list = []
        parallel = None
        analyze: list = []

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.SETUP):
                self.consume(TokenType.COLON, "Expected ':'")
                setup = self._statements_from_block(self.parse_block())

            elif self.match(TokenType.ANALYZE):
                self.consume(TokenType.COLON, "Expected ':'")
                analyze = self._statements_from_block(self.parse_block())

            elif self.match(TokenType.PARALLEL):
                parallel = self.parse_parallel()

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return ExperimentNode(
            name, setup, parallel, analyze,
            self.previous().line, self.previous().column,
        )

    def parse_parallel(self) -> ParallelNode:
        """Parse parallel execution block"""
        self.consume(TokenType.COLON, "Expected ':'")

        branches = []
        synthesize = None

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.BRANCH):
                name = self.consume(TokenType.IDENTIFIER, "Expected branch name").value
                self.consume(TokenType.COLON, "Expected ':'")
                body = self.parse_expression()
                branches.append(BranchNode(name, body,
                                          self.previous().line, self.previous().column))

            elif self.match(TokenType.SYNTHESIZE):
                self.consume(TokenType.COLON, "Expected ':'")
                synthesize = self.parse_expression()

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return ParallelNode(branches, synthesize,
                           self.previous().line, self.previous().column)

    def parse_stream(self) -> StreamNode:
        """Parse stream definition"""
        name = self.consume(TokenType.IDENTIFIER, "Expected stream name").value
        self.consume(TokenType.COLON, "Expected ':'")
        body = self.parse_block()

        return StreamNode(name, body,
                         self.previous().line, self.previous().column)

    # ========== Reasoning Parsing ==========

    def parse_reason_chain(self) -> ReasonChainNode:
        """Parse reasoning chain"""
        name = self.consume(TokenType.IDENTIFIER, "Expected chain name").value
        self.consume(TokenType.COLON, "Expected ':'")

        premises = []
        derivations = []
        conclusion = None

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.PREMISE):
                premise_name = self.consume(TokenType.IDENTIFIER, "Expected premise name").value
                self.consume(TokenType.COLON, "Expected ':'")
                statement = self.parse_expression()
                premises.append((premise_name, statement))

            elif self.match(TokenType.DERIVE):
                derive_name = self.consume(TokenType.IDENTIFIER, "Expected derivation name").value
                self.consume(TokenType.FROM, "Expected 'from'")
                from_premises = []
                while True:
                    from_premises.append(self.consume(TokenType.IDENTIFIER, "Expected premise name").value)
                    if not self.match(TokenType.COMMA):
                        break
                self.consume(TokenType.COLON, "Expected ':'")
                statement = self.parse_expression()
                derivations.append((derive_name, from_premises, statement))

            elif self.match(TokenType.CONCLUDE):
                self.consume(TokenType.COLON, "Expected ':'")
                conclusion = self.parse_expression()

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        if not conclusion:
            raise ParserError("Reasoning chain must have a conclusion", self.previous())

        return ReasonChainNode(name, premises, derivations, conclusion,
                              self.previous().line, self.previous().column)

    # ========== Pipeline Parsing ==========

    def parse_pipeline(self) -> PipelineNode:
        """Parse pipeline definition"""
        name = self.consume(TokenType.IDENTIFIER, "Expected pipeline name").value
        self.consume(TokenType.COLON, "Expected ':'")

        stages = []

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.STAGE):
                stages.append(self.parse_stage())
            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return PipelineNode(name, stages,
                           self.previous().line, self.previous().column)

    def parse_stage(self) -> StageNode:
        """Parse pipeline stage"""
        name = self.consume(TokenType.IDENTIFIER, "Expected stage name").value

        parallel_factor = None
        if self.match(TokenType.LEFT_BRACKET):
            parallel_factor = int(self.consume(TokenType.NUMBER, "Expected parallel factor").value)
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")

        self.consume(TokenType.COLON, "Expected ':'")

        operations = []
        fork = None

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.FORK):
                fork = self.parse_fork()
            else:
                stmt = self.parse_statement()
                if stmt:
                    operations.append(stmt)
            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return StageNode(name, operations, parallel_factor, fork,
                        self.previous().line, self.previous().column)

    def parse_fork(self) -> ForkNode:
        """Parse pipeline fork"""
        self.consume(TokenType.COLON, "Expected ':'")

        paths = []

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.PATH):
                name = self.consume(TokenType.IDENTIFIER, "Expected path name").value
                self.consume(TokenType.COLON, "Expected ':'")

                operations = []
                self.consume(TokenType.NEWLINE, "Expected newline")
                self.consume(TokenType.INDENT, "Expected indent")

                while not self.check(TokenType.DEDENT):
                    stmt = self.parse_statement()
                    if stmt:
                        operations.append(stmt)
                    self.skip_newlines()

                self.consume(TokenType.DEDENT, "Expected dedent")

                paths.append((name, BlockNode(operations)))

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return ForkNode(paths, self.previous().line, self.previous().column)

    # ========== Exploration Parsing ==========

    def parse_explore(self) -> ExploreNode:
        """Parse exploration block"""
        target = self.consume(TokenType.IDENTIFIER, "Expected target name").value
        self.consume(TokenType.COLON, "Expected ':'")

        attempts = []
        fallbacks = []
        accept_condition = None
        reject_condition = None

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.TRY):
                name = self.consume(TokenType.IDENTIFIER, "Expected attempt name").value
                self.consume(TokenType.COLON, "Expected ':'")
                attempts.append((name, self.parse_expression()))

            elif self.match(TokenType.FALLBACK):
                name = self.consume(TokenType.IDENTIFIER, "Expected fallback name").value
                self.consume(TokenType.COLON, "Expected ':'")
                fallbacks.append((name, self.parse_expression()))

            elif self.match(TokenType.ACCEPT):
                self.consume(TokenType.IF, "Expected 'if' after 'accept'")
                accept_condition = self.parse_expression()

            elif self.match(TokenType.REJECT):
                self.consume(TokenType.IF, "Expected 'if' after 'reject'")
                reject_condition = self.parse_expression()

            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return ExploreNode(
            target, attempts, fallbacks, accept_condition,
            self.previous().line, self.previous().column,
        )

    # ========== Symbolic Math Parsing ==========

    def parse_symbolic(self) -> SymbolicNode:
        """Parse symbolic math block"""
        self.consume(TokenType.COLON, "Expected ':'")

        statements = []

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            if self.match(TokenType.LET):
                statements.append(self.parse_let())
            elif self.match(TokenType.SOLVE):
                statements.append(self.parse_solve())
            elif self.match(TokenType.PROVE):
                statements.append(self.parse_prove())
            else:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return SymbolicNode(statements,
                           self.previous().line, self.previous().column)

    def parse_let(self) -> LetNode:
        """Parse symbolic let binding"""
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value

        parameters = None
        if self.match(TokenType.LEFT_PAREN):
            parameters = []
            while not self.check(TokenType.RIGHT_PAREN):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
                if not self.match(TokenType.COMMA):
                    break
            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")

        self.consume(TokenType.ASSIGN, "Expected '='")
        expression = self.parse_expression()

        return LetNode(name, parameters, expression,
                      self.previous().line, self.previous().column)

    def parse_solve(self) -> SolveNode:
        """Parse solve statement"""
        equation = self.parse_expression()
        self.consume(TokenType.FOR, "Expected 'for'")
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value

        domain = None
        if self.match(TokenType.IN):
            domain = self.consume(TokenType.IDENTIFIER, "Expected domain name").value

        return SolveNode(equation, variable, domain,
                        self.previous().line, self.previous().column)

    def parse_prove(self) -> ProveNode:
        """Parse prove statement"""
        statement = self.parse_expression()

        domain = None
        if self.match(TokenType.IN):
            domain = self.consume(TokenType.IDENTIFIER, "Expected domain name").value

        return ProveNode(statement, domain,
                        self.previous().line, self.previous().column)

    # ========== Variable Declaration Parsing ==========

    def parse_tensor_declaration(self) -> TensorNode:
        """Parse tensor declaration"""
        name = self.consume(TokenType.IDENTIFIER, "Expected tensor name").value

        dimensions = None
        if self.match(TokenType.LEFT_BRACKET):
            dimensions = []
            while not self.check(TokenType.RIGHT_BRACKET):
                dimensions.append(int(self.consume(TokenType.NUMBER, "Expected dimension").value))
                if not self.match(TokenType.COMMA):
                    break
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")

        values = None
        if self.match(TokenType.ASSIGN):
            values = self.parse_expression()

        return TensorNode(name, dimensions or [], values,
                         self.previous().line, self.previous().column)

    def parse_uncertain_declaration(self) -> AssignmentNode:
        """Parse uncertain variable declaration"""
        if self.check(TokenType.IDENTIFIER) or self.check(TokenType.VALUE):
            name = self.advance().value
        else:
            raise ParserError("Expected variable name", self.peek())
        self.consume(TokenType.ASSIGN, "Expected '='")
        value = self.parse_expression()

        constraint = None
        if self.match(TokenType.WHERE):
            constraint = self.parse_expression()

        return AssignmentNode(
            name, value, True, self.previous().line, self.previous().column
        )

    def parse_constrain(self) -> ConstrainNode:
        """Parse constrain statement"""
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':'")
        var_type = self.consume(TokenType.IDENTIFIER, "Expected type").value
        self.consume(TokenType.WHERE, "Expected 'where'")
        constraint = self.parse_expression()

        return ConstrainNode(variable, var_type, constraint,
                            self.previous().line, self.previous().column)

    def parse_evolve(self) -> EvolveNode:
        """Parse evolve statement"""
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':'")
        var_type = self.consume(TokenType.IDENTIFIER, "Expected type").value
        self.consume(TokenType.ASSIGN, "Expected '='")
        initial_value = self.parse_expression()

        return EvolveNode(variable, var_type, initial_value,
                         self.previous().line, self.previous().column)

    def _consume_type_name(self) -> str:
        """Consume a type name (identifier or type keyword)."""
        tok = self.peek()
        type_tokens = (
            TokenType.IDENTIFIER,
            TokenType.QUANTUM,
        )
        if tok.type not in type_tokens:
            raise ParserError("Expected type name", tok)
        self.advance()
        return tok.value

    def parse_observe(self) -> ObserveNode:
        """Parse observe statement"""
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':'")
        var_type = self._consume_type_name()

        condition = None
        if self.match(TokenType.WHEN):
            condition = self.parse_expression()

        return ObserveNode(variable, var_type, condition,
                          self.previous().line, self.previous().column)

    # ========== Control Flow Parsing ==========

    def parse_if(self) -> IfNode:
        """Parse if statement"""
        condition = self.parse_expression()
        self.consume(TokenType.COLON, "Expected ':'")

        then_body = []
        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        else_body = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.COLON, "Expected ':'")
            else_body = []

            self.consume(TokenType.NEWLINE, "Expected newline")
            self.consume(TokenType.INDENT, "Expected indent")

            while not self.check(TokenType.DEDENT):
                stmt = self.parse_statement()
                if stmt:
                    else_body.append(stmt)
                self.skip_newlines()

            self.consume(TokenType.DEDENT, "Expected dedent")

        return IfNode(condition, then_body, else_body,
                     self.previous().line, self.previous().column)

    def parse_while(self) -> WhileNode:
        """Parse while loop"""
        condition = self.parse_expression()
        self.consume(TokenType.COLON, "Expected ':'")

        body = []
        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return WhileNode(condition, body,
                        self.previous().line, self.previous().column)

    def parse_for(self) -> ForNode:
        """Parse for loop"""
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.IN, "Expected 'in'")
        iterable = self.parse_expression()
        self.consume(TokenType.COLON, "Expected ':'")

        body = []
        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return ForNode(variable, iterable, body,
                      self.previous().line, self.previous().column)

    def parse_return(self) -> ReturnNode:
        """Parse return statement"""
        value = None
        if not self.check(TokenType.NEWLINE) and not self.is_at_end():
            value = self.parse_expression()

        return ReturnNode(value, self.previous().line, self.previous().column)

    def parse_break(self) -> BreakNode:
        """Parse break statement"""
        return BreakNode(self.previous().line, self.previous().column)

    def parse_continue(self) -> ContinueNode:
        """Parse continue statement"""
        return ContinueNode(self.previous().line, self.previous().column)

    def parse_run(self) -> RunNode:
        """Parse run statement"""
        circuit = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value

        backend = None
        options = {}

        if self.match(TokenType.ON):
            backend = self.consume(TokenType.IDENTIFIER, "Expected backend name").value

        if self.match(TokenType.WITH):
            _option_tokens = (
                TokenType.IDENTIFIER,
                TokenType.SHOTS,
                TokenType.NOISE,
                TokenType.BACKEND,
            )
            while True:
                tok = self.peek()
                if tok.type not in _option_tokens:
                    break
                key = self.advance().value
                self.consume(TokenType.ASSIGN, "Expected '='")
                value = self.parse_expression()
                options[key] = value

                if not self.match(TokenType.COMMA):
                    break

        return RunNode(circuit, backend, options,
                      self.previous().line, self.previous().column)

    # ========== Expression Parsing ==========

    def parse_expression_statement(self) -> ASTNode:
        """Parse expression or assignment statement"""
        expr = self.parse_expression()

        # Check for assignment
        if self.match(TokenType.ASSIGN):
            if isinstance(expr, IdentifierNode):
                value = self.parse_expression()
                return AssignmentNode(
                    expr.name, value, False, expr.line, expr.column
                )

        return expr

    def parse_expression(self) -> ASTNode:
        """Parse expression with operator precedence"""
        return self.parse_logical_or()

    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR expression"""
        left = self.parse_logical_and()

        while self.match(TokenType.OR):
            op = self.previous().value
            right = self.parse_logical_and()
            left = BinaryOpNode(op, left, right,
                               self.previous().line, self.previous().column)

        return left

    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND expression"""
        left = self.parse_equality()

        while self.match(TokenType.AND):
            op = self.previous().value
            right = self.parse_equality()
            left = BinaryOpNode(op, left, right,
                               self.previous().line, self.previous().column)

        return left

    def parse_equality(self) -> ASTNode:
        """Parse equality expression"""
        left = self.parse_comparison()

        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            op = self.previous().value
            right = self.parse_comparison()
            left = BinaryOpNode(op, left, right,
                               self.previous().line, self.previous().column)

        return left

    def parse_comparison(self) -> ASTNode:
        """Parse comparison expression"""
        left = self.parse_addition()

        while self.match(TokenType.LESS_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_THAN, TokenType.GREATER_EQUAL):
            op = self.previous().value
            right = self.parse_addition()
            left = BinaryOpNode(op, left, right,
                               self.previous().line, self.previous().column)

        return left

    def parse_addition(self) -> ASTNode:
        """Parse addition/subtraction expression"""
        left = self.parse_multiplication()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.previous().value
            right = self.parse_multiplication()
            left = BinaryOpNode(op, left, right,
                               self.previous().line, self.previous().column)

        return left

    def parse_multiplication(self) -> ASTNode:
        """Parse multiplication/division expression"""
        left = self.parse_power()

        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.PERCENT):
            op = self.previous().value
            right = self.parse_power()
            left = BinaryOpNode(op, left, right,
                               self.previous().line, self.previous().column)

        return left

    def parse_power(self) -> ASTNode:
        """Parse exponentiation expression"""
        left = self.parse_unary()

        while self.match(TokenType.POWER):
            op = self.previous().value
            right = self.parse_unary()
            left = BinaryOpNode(op, left, right,
                               self.previous().line, self.previous().column)

        return left

    def parse_unary(self) -> ASTNode:
        """Parse unary expression"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.previous().value
            operand = self.parse_unary()
            return UnaryOpNode(op, operand,
                              self.previous().line, self.previous().column)

        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        """Parse postfix expression (function calls, indexing)"""
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                # Function call
                arguments = []
                kwargs = {}

                _kwarg_tokens = (
                    TokenType.IDENTIFIER,
                    TokenType.PARALLEL,
                    TokenType.NOISE,
                    TokenType.SHOTS,
                )
                if not self.check(TokenType.RIGHT_PAREN):
                    while True:
                        # Check for keyword argument
                        if (
                            self.peek().type in _kwarg_tokens
                            and self.peek_next()
                            and self.peek_next().type == TokenType.ASSIGN
                        ):
                            key = self.advance().value
                            self.advance()  # consume '='
                            kwargs[key] = self.parse_expression()
                        else:
                            arguments.append(self.parse_expression())

                        if not self.match(TokenType.COMMA):
                            break

                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")

                call = FunctionCallNode(
                    expr, arguments, self.previous().line, self.previous().column
                )
                if kwargs:
                    call.kwargs = kwargs  # type: ignore[attr-defined]
                expr = call

            elif self.match(TokenType.LEFT_BRACKET):
                # Indexing/slicing
                indices = []
                while not self.check(TokenType.RIGHT_BRACKET):
                    indices.append(self.parse_expression())
                    if not self.match(TokenType.COMMA):
                        break

                self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after indices")

                expr = TensorAccessNode(expr, indices,
                                       self.previous().line, self.previous().column)
            else:
                break

        return expr

    def parse_primary(self) -> ASTNode:
        """Parse primary expression"""
        # Numbers
        if self.match(TokenType.NUMBER):
            value = float(self.previous().value)

            # Check for uncertain value
            if self.match(TokenType.PLUS_MINUS, TokenType.UNCERTAINTY_OP):
                uncertainty = float(self.consume(TokenType.NUMBER, "Expected uncertainty value").value)
                return UncertainNode(value, uncertainty,
                                   self.previous().line, self.previous().column)

            return NumberNode(value, self.previous().line, self.previous().column)

        # Strings
        if self.match(TokenType.STRING):
            return StringNode(self.previous().value,
                            self.previous().line, self.previous().column)

        # Booleans
        if self.match(TokenType.TRUE):
            return BooleanNode(True, self.previous().line, self.previous().column)
        if self.match(TokenType.FALSE):
            return BooleanNode(False, self.previous().line, self.previous().column)

        # Identifiers (VALUE is a keyword used as a variable name in tests)
        if self.match(TokenType.IDENTIFIER, TokenType.VALUE):
            return IdentifierNode(self.previous().value,
                                 self.previous().line, self.previous().column)

        # Lists
        if self.match(TokenType.LEFT_BRACKET):
            elements = []

            # Check for matrix (list of lists)
            is_matrix = False
            if not self.check(TokenType.RIGHT_BRACKET):
                # Peek to see if first element is a list
                save_pos = self.current
                if self.check(TokenType.LEFT_BRACKET):
                    is_matrix = True
                self.current = save_pos

            if is_matrix:
                rows = []
                while not self.check(TokenType.RIGHT_BRACKET):
                    if self.match(TokenType.LEFT_BRACKET):
                        row = []
                        while not self.check(TokenType.RIGHT_BRACKET):
                            row.append(self.parse_expression())
                            if not self.match(TokenType.COMMA):
                                break
                        self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
                        rows.append(row)

                    if not self.match(TokenType.COMMA):
                        break

                self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
                return MatrixNode(rows, self.previous().line, self.previous().column)
            else:
                # Regular list
                while not self.check(TokenType.RIGHT_BRACKET):
                    elements.append(self.parse_expression())
                    if not self.match(TokenType.COMMA):
                        break

                self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
                return ListNode(elements, self.previous().line, self.previous().column)

        # Parenthesized expression
        if self.match(TokenType.LEFT_PAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        # Distributions
        if self.check(TokenType.IDENTIFIER) and self.peek().value.lower() in (
            "normal",
            "uniform",
            "poisson",
            "gaussian",
        ):
            self.advance()
            dist_type = self.previous().value
            self.consume(TokenType.LEFT_PAREN, "Expected '(' after distribution")

            parameters = {}
            while not self.check(TokenType.RIGHT_PAREN):
                key = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
                self.consume(TokenType.ASSIGN, "Expected '='")
                value = self.parse_expression()
                parameters[key] = value

                if not self.match(TokenType.COMMA):
                    break

            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")

            return DistributionNode(dist_type, parameters,
                                   self.previous().line, self.previous().column)

        raise ParserError(f"Unexpected token: {self.peek()}", self.peek())

    def parse_block(self) -> BlockNode:
        """Parse indented block of statements"""
        statements = []

        self.consume(TokenType.NEWLINE, "Expected newline")
        self.consume(TokenType.INDENT, "Expected indent")

        while not self.check(TokenType.DEDENT):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()

        self.consume(TokenType.DEDENT, "Expected dedent")

        return BlockNode(statements)

    def parse_expression_list(self) -> List[ASTNode]:
        """Parse comma-separated expression list"""
        expressions = []

        while True:
            expressions.append(self.parse_expression())
            if not self.match(TokenType.COMMA):
                break

        return expressions

    # ========== Helper Methods ==========

    def match(self, *types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> Token:
        """Consume current token and return it"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """Check if we're at end of tokens"""
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        """Return current token without consuming"""
        return self.tokens[self.current]

    def peek_next(self) -> Optional[Token]:
        """Return next token without consuming"""
        if self.current + 1 < len(self.tokens):
            return self.tokens[self.current + 1]
        return None

    def previous(self) -> Token:
        """Return previous token"""
        return self.tokens[self.current - 1]

    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of given type or raise error"""
        if self.check(token_type):
            return self.advance()

        raise ParserError(message, self.peek())

    def skip_newlines(self):
        """Skip any newline tokens"""
        while self.match(TokenType.NEWLINE):
            pass

    def synchronize(self):
        """Recover from parser error"""
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.NEWLINE:
                return

            # Synchronize on statement keywords
            if self.peek().type in [
                TokenType.IF, TokenType.WHILE, TokenType.FOR,
                TokenType.QUANTUM, TokenType.HYPOTHESIS, TokenType.EXPERIMENT,
                TokenType.PARALLEL, TokenType.PIPELINE, TokenType.EXPLORE,
                TokenType.SYMBOLIC, TokenType.TENSOR, TokenType.UNCERTAIN
            ]:
                return

            self.advance()


# Export enhanced parser as default
Parser = EnhancedParser
