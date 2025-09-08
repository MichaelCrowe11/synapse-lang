"""Deprecated root parser wrapper. Use synapse_lang.synapse_parser instead."""
from synapse_lang.synapse_parser import *  # type: ignore

class ParseError(Exception):
    """Parse error exception"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.column}")

class Parser:
    """Recursive descent parser for Synapse language"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def peek(self) -> Token:
        """Look at current token without consuming"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
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
        raise ParseError(message, self.peek())
    
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
        
        # Hypothesis
        if self.check(TokenType.HYPOTHESIS):
            return self.parse_hypothesis()
        
        # Experiment
        if self.check(TokenType.EXPERIMENT):
            return self.parse_experiment()
        
        # Parallel block
        if self.check(TokenType.PARALLEL):
            return self.parse_parallel()
        
        # Stream
        if self.check(TokenType.STREAM):
            return self.parse_stream()
        
        # Reason chain
        if self.check(TokenType.REASON):
            return self.parse_reason_chain()
        
        # Pipeline
        if self.check(TokenType.PIPELINE):
            return self.parse_pipeline()
        
        # Explore
        if self.check(TokenType.EXPLORE):
            return self.parse_explore()
        
        # Quantum circuit
        if self.check(TokenType.QUANTUM):
            return self.parse_quantum()
        
        # Symbolic block
        if self.check(TokenType.SYMBOLIC):
            return self.parse_symbolic()
        
        # Uncertain assignment
        if self.check(TokenType.UNCERTAIN):
            return self.parse_uncertain_assignment()
        
        # Constrain assignment
        if self.check(TokenType.CONSTRAIN):
            return self.parse_constrain_assignment()
        
        # Evolve assignment
        if self.check(TokenType.EVOLVE):
            return self.parse_evolve_assignment()
        
        # Propagate
        if self.check(TokenType.PROPAGATE):
            return self.parse_propagate()
        
        # Prove statement
        if self.check(TokenType.PROVE):
            return self.parse_prove()
        
        # Regular assignment or expression
        if self.check(TokenType.IDENTIFIER):
            # Look ahead for assignment
            if self.tokens[self.current + 1].type == TokenType.ASSIGN:
                return self.parse_assignment()
        
        # Expression statement
        expr = self.parse_expression()
        return expr
    
    def parse_hypothesis(self) -> HypothesisNode:
        """Parse hypothesis block"""
        token = self.advance()  # consume 'hypothesis'
        name = self.consume(TokenType.IDENTIFIER, "Expected hypothesis name").value

        # Shorthand form: hypothesis H1: expression
        if self.check(TokenType.COLON):
            self.advance()
            prediction_expr = self.parse_expression()
            return HypothesisNode(name, [], [prediction_expr], [], token.line, token.column)

        self.consume(TokenType.LEFT_BRACE, "Expected '{' after hypothesis name")
        self.skip_newlines()

        assumptions = []
        predictions = []
        validations = []

        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()

            if self.check(TokenType.IDENTIFIER):
                field_name = self.peek().value

                if field_name == "assume":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'assume'")
                    assumptions.append(self.parse_expression())

                elif field_name == "predict":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'predict'")
                    predictions.append(self.parse_expression())

                elif field_name == "validate":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'validate'")
                    validations.append(self.parse_expression())

            self.skip_newlines()

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close hypothesis")

        return HypothesisNode(name, assumptions, predictions, validations, token.line, token.column)
    
    def parse_experiment(self) -> ExperimentNode:
        """Parse experiment block"""
        token = self.advance()  # consume 'experiment'
        name = self.consume(TokenType.IDENTIFIER, "Expected experiment name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after experiment name")
        self.skip_newlines()
        
        setup = None
        procedure = None
        analysis = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.IDENTIFIER):
                field_name = self.peek().value
                
                if field_name == "setup":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'setup'")
                    setup = self.parse_expression()
                    
                elif field_name == "procedure" or self.check(TokenType.PARALLEL):
                    if field_name == "procedure":
                        self.advance()
                        self.consume(TokenType.COLON, "Expected ':' after 'procedure'")
                    procedure = self.parse_statement()
                    
                elif field_name == "synthesize" or field_name == "analysis":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after field name")
                    analysis = self.parse_expression()
            
            elif self.check(TokenType.PARALLEL):
                procedure = self.parse_parallel()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close experiment")
        
        if not procedure:
            procedure = BlockNode([], token.line, token.column)
        
        return ExperimentNode(name, procedure, token.line, token.column, setup, analysis)
    
    def parse_parallel(self) -> ParallelNode:
        """Parse parallel execution block"""
        token = self.advance()  # consume 'parallel'
        
        num_workers = None
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            if self.check(TokenType.NUMBER):
                num_workers = int(self.advance().value)
            elif self.check(TokenType.IDENTIFIER) and self.peek().value == "auto":
                self.advance()
                num_workers = None  # auto
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parallel worker count")
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after parallel")
        self.skip_newlines()
        
        branches = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.BRANCH):
                self.advance()
                branch_name = self.consume(TokenType.IDENTIFIER, "Expected branch name").value
                self.consume(TokenType.COLON, "Expected ':' after branch name")
                branch_body = self.parse_expression()
                branches.append(BranchNode(branch_name, branch_body, token.line, token.column))
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close parallel block")
        
        return ParallelNode(branches, token.line, token.column, num_workers)
    
    def parse_stream(self) -> StreamNode:
        """Parse stream definition"""
        token = self.advance()  # consume 'stream'
        name = self.consume(TokenType.IDENTIFIER, "Expected stream name").value
        
        self.consume(TokenType.COLON, "Expected ':' after stream name")
        body = self.parse_block()
        
        return StreamNode(name, body, token.line, token.column)
    
    def parse_reason_chain(self) -> ReasonChainNode:
        """Parse reasoning chain"""
        token = self.advance()  # consume 'reason'
        self.consume(TokenType.CHAIN, "Expected 'chain' after 'reason'")
        name = self.consume(TokenType.IDENTIFIER, "Expected chain name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after chain name")
        self.skip_newlines()
        
        premises = []
        derivations = []
        conclusion = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.PREMISE):
                self.advance()
                premise_name = self.consume(TokenType.IDENTIFIER, "Expected premise name").value
                self.consume(TokenType.COLON, "Expected ':' after premise name")
                statement = self.parse_expression()
                premises.append(PremiseNode(premise_name, statement, token.line, token.column))
                
            elif self.check(TokenType.DERIVE):
                self.advance()
                derive_name = self.consume(TokenType.IDENTIFIER, "Expected derivation name").value
                self.consume(TokenType.IDENTIFIER, "Expected 'from'")  # 'from' keyword
                from_premise = self.consume(TokenType.IDENTIFIER, "Expected premise reference").value
                self.consume(TokenType.COLON, "Expected ':' after premise reference")
                statement = self.parse_expression()
                derivations.append(DeriveNode(derive_name, from_premise, statement, token.line, token.column))
                
            elif self.check(TokenType.CONCLUDE):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'conclude'")
                condition = self.parse_expression()
                if self.check(TokenType.ARROW):
                    self.advance()
                    result = self.parse_expression()
                    conclusion = ConcludeNode(condition, result, token.line, token.column)
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close reason chain")
        
        if not conclusion:
            # Create empty conclusion if not provided
            conclusion = ConcludeNode(
                IdentifierNode("true", token.line, token.column),
                IdentifierNode("conclusion", token.line, token.column),
                token.line, token.column
            )
        
        return ReasonChainNode(name, premises, derivations, conclusion, token.line, token.column)
    
    def parse_pipeline(self) -> PipelineNode:
        """Parse pipeline definition"""
        token = self.advance()  # consume 'pipeline'
        name = self.consume(TokenType.IDENTIFIER, "Expected pipeline name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after pipeline name")
        self.skip_newlines()
        
        stages = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.STAGE):
                stages.append(self.parse_stage())
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close pipeline")
        
        return PipelineNode(name, stages, token.line, token.column)
    
    def parse_stage(self) -> StageNode:
        """Parse pipeline stage"""
        token = self.advance()  # consume 'stage'
        name = self.consume(TokenType.IDENTIFIER, "Expected stage name").value
        
        parallel_count = None
        if self.check(TokenType.PARALLEL):
            self.advance()
            if self.check(TokenType.LEFT_PAREN):
                self.advance()
                if self.check(TokenType.NUMBER):
                    parallel_count = int(self.advance().value)
                elif self.check(TokenType.IDENTIFIER) and self.peek().value == "auto":
                    self.advance()
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parallel count")
        
        body = self.parse_block()
        
        return StageNode(name, body, token.line, token.column, parallel_count)
    
    def parse_explore(self) -> ExploreNode:
        """Parse explore block"""
        token = self.advance()  # consume 'explore'
        name = self.consume(TokenType.IDENTIFIER, "Expected explore name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after explore name")
        self.skip_newlines()
        
        tries = []
        fallbacks = []
        accept_condition = None
        reject_condition = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.TRY):
                self.advance()
                try_name = self.consume(TokenType.IDENTIFIER, "Expected try name").value
                self.consume(TokenType.COLON, "Expected ':' after try name")
                try_body = self.parse_expression()
                tries.append(TryNode(try_name, try_body, token.line, token.column))
                
            elif self.check(TokenType.FALLBACK):
                self.advance()
                fallback_name = self.consume(TokenType.IDENTIFIER, "Expected fallback name").value
                self.consume(TokenType.COLON, "Expected ':' after fallback name")
                fallback_body = self.parse_expression()
                fallbacks.append(FallbackNode(fallback_name, fallback_body, token.line, token.column))
                
            elif self.check(TokenType.ACCEPT):
                self.advance()
                self.consume(TokenType.IDENTIFIER, "Expected 'when'")  # 'when' keyword
                self.consume(TokenType.COLON, "Expected ':' after 'when'")
                accept_condition = self.parse_expression()
                
            elif self.check(TokenType.REJECT):
                self.advance()
                self.consume(TokenType.IDENTIFIER, "Expected 'when'")  # 'when' keyword
                self.consume(TokenType.COLON, "Expected ':' after 'when'")
                reject_condition = self.parse_expression()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close explore block")
        
        return ExploreNode(name, tries, fallbacks, token.line, token.column, accept_condition, reject_condition)
    
    def parse_symbolic(self) -> BlockNode:
        """Parse symbolic block"""
        token = self.advance()  # consume 'symbolic'
        return self.parse_block()
    
    def parse_propagate(self) -> PropagateNode:
        """Parse uncertainty propagation"""
        token = self.advance()  # consume 'propagate'
        self.consume(TokenType.IDENTIFIER, "Expected 'uncertainty'")  # 'uncertainty' keyword
        self.consume(TokenType.IDENTIFIER, "Expected 'through'")  # 'through' keyword
        
        body = self.parse_block()
        
        return PropagateNode("uncertainty", body, token.line, token.column)
    
    def parse_prove(self) -> ASTNode:
        """Parse prove statement"""
        token = self.advance()  # consume 'prove'
        
        # Parse the statement to prove
        statement = self.parse_expression()
        
        # Optional proof method
        method = None
        if self.check(TokenType.USING):
            self.advance()  # consume 'using'
            method = self.parse_expression()
        
        from synapse_ast import ProveNode
        return ProveNode(statement, method, token.line, token.column)
    
    def parse_quantum(self) -> ASTNode:
        """Parse quantum constructs"""
        token = self.advance()  # consume 'quantum'
        
        if self.check(TokenType.CIRCUIT):
            return self.parse_quantum_circuit()
        elif self.check(TokenType.ALGORITHM):
            return self.parse_quantum_algorithm()
        elif self.check(TokenType.BACKEND):
            return self.parse_quantum_backend()
        else:
            # Quantum block
            return self.parse_quantum_block()
    
    def parse_quantum_circuit(self) -> 'QuantumCircuitNode':
        """Parse quantum circuit definition"""
        circuit_token = self.advance()  # consume 'circuit'
        name = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value
        
        # Optional qubit count
        qubits = 1
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            if self.check(TokenType.NUMBER):
                qubits = int(self.advance().value)
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after qubit count")
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after circuit name")
        self.skip_newlines()
        
        gates = []
        measurements = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check_quantum_gate():
                gates.append(self.parse_quantum_gate())
            elif self.check(TokenType.MEASURE):
                measurements.append(self.parse_quantum_measure())
            else:
                # Skip unrecognized tokens
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close circuit")
        
        from synapse_ast import QuantumCircuitNode
        return QuantumCircuitNode(name, qubits, gates, measurements, circuit_token.line, circuit_token.column)
    
    def check_quantum_gate(self) -> bool:
        """Check if current token is a quantum gate"""
        return self.check(TokenType.HADAMARD) or self.check(TokenType.CNOT) or \
               self.check(TokenType.PAULI_X) or self.check(TokenType.PAULI_Y) or \
               self.check(TokenType.PAULI_Z) or self.check(TokenType.ROTATION_X) or \
               self.check(TokenType.ROTATION_Y) or self.check(TokenType.ROTATION_Z) or \
               self.check(TokenType.IDENTIFIER)
    
    def parse_quantum_gate(self) -> 'QuantumGateNode':
        """Parse quantum gate operation"""
        gate_token = self.advance()
        gate_type = gate_token.value
        
        # Handle both keyword tokens and identifier tokens for gates
        if gate_token.type == TokenType.IDENTIFIER:
            # Common quantum gate names as identifiers
            if gate_type not in ['h', 'hadamard', 'cnot', 'cx', 'x', 'y', 'z', 'rx', 'ry', 'rz']:
                # Not a quantum gate, return None or handle error
                raise SyntaxError(f"Unknown quantum gate: {gate_type}")
        
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {gate_type}")
        
        qubits = []
        parameters = []
        
        # Parse qubits and parameters
        if not self.check(TokenType.RIGHT_PAREN):
            qubits.append(self.parse_expression())
            
            while self.check(TokenType.COMMA):
                self.advance()
                arg = self.parse_expression()
                
                # Distinguish between qubits and parameters based on gate type
                if gate_type in ['rx', 'ry', 'rz'] and len(qubits) == 1:
                    parameters.append(arg)  # Rotation angle
                else:
                    qubits.append(arg)  # Additional qubit
        
        self.consume(TokenType.RIGHT_PAREN, f"Expected ')' after {gate_type} arguments")
        
        from synapse_ast import QuantumGateNode
        return QuantumGateNode(gate_type, qubits, parameters, gate_token.line, gate_token.column)
    
    def parse_quantum_measure(self) -> 'QuantumMeasureNode':
        """Parse quantum measurement"""
        token = self.advance()  # consume 'measure'
        
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after measure")
        
        qubits = []
        classical_bits = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            qubits.append(self.parse_expression())
            
            while self.check(TokenType.COMMA):
                self.advance()
                qubits.append(self.parse_expression())
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after measure arguments")
        
        from synapse_ast import QuantumMeasureNode
        return QuantumMeasureNode(qubits, classical_bits, token.line, token.column)
    
    def parse_quantum_algorithm(self) -> 'QuantumAlgorithmNode':
        """Parse quantum algorithm definition"""
        algorithm_token = self.advance()  # consume 'algorithm'
        name = self.consume(TokenType.IDENTIFIER, "Expected algorithm name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after algorithm name")
        self.skip_newlines()
        
        parameters: List[ASTNode] = []
        ansatz = None
        cost_function = None
        optimizer = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.IDENTIFIER):
                field_name = self.peek().value
                
                if field_name == "parameters":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'parameters'")
                    # Parse parameter list: [theta1, theta2, ...]
                    if self.check(TokenType.LEFT_BRACKET):
                        self.advance()
                        if not self.check(TokenType.RIGHT_BRACKET):
                            # At least one identifier
                            ident_token = self.consume(TokenType.IDENTIFIER, "Expected parameter identifier")
                            from synapse_ast import IdentifierNode
                            parameters.append(IdentifierNode(ident_token.value, ident_token.line, ident_token.column))
                            while self.check(TokenType.COMMA):
                                self.advance()
                                ident_token = self.consume(TokenType.IDENTIFIER, "Expected parameter identifier")
                                parameters.append(IdentifierNode(ident_token.value, ident_token.line, ident_token.column))
                        self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after parameter list")
                    
                elif field_name == "ansatz":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'ansatz'")
                    # Ansatz can be identifier or string literal for now
                    if self.check(TokenType.IDENTIFIER):
                        ident_tok = self.advance()
                        from synapse_ast import QuantumAnsatzNode
                        ansatz = QuantumAnsatzNode(ident_tok.value, [], ident_tok.line, ident_tok.column)
                    elif self.check(TokenType.STRING):
                        str_tok = self.advance()
                        from synapse_ast import QuantumAnsatzNode
                        ansatz = QuantumAnsatzNode(str_tok.value, [], str_tok.line, str_tok.column)
                    else:
                        # Fallback to default
                        from synapse_ast import QuantumAnsatzNode
                        ansatz = QuantumAnsatzNode("default", [], algorithm_token.line, algorithm_token.column)
                    
                elif field_name == "cost_function":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'cost_function'")
                    cost_function = self.parse_expression()
                    
                elif field_name == "optimize":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'optimize'")
                    optimizer = self.parse_expression()
                else:
                    # Unknown field - consume identifier and its value to avoid infinite loop
                    self.advance()  # consume the field name
                    if self.check(TokenType.COLON):
                        self.advance()  # consume the colon
                        # Skip the value - could be expression, list, etc.
                        self.parse_expression()
            
            self.skip_newlines()
            
            # Add safety check to prevent infinite loop
            if self.check(TokenType.EOF):
                break
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close algorithm")
        
        from synapse_ast import QuantumAlgorithmNode, QuantumAnsatzNode
        if ansatz is None:
            ansatz = QuantumAnsatzNode("default", [], algorithm_token.line, algorithm_token.column)
        
        return QuantumAlgorithmNode(name, parameters, ansatz, cost_function, optimizer, algorithm_token.line, algorithm_token.column)
    
    def parse_quantum_backend(self) -> 'QuantumBackendNode':
        """Parse quantum backend configuration"""
        backend_token = self.advance()  # consume 'backend'
        name = self.consume(TokenType.IDENTIFIER, "Expected backend name").value
        
        config = {}
        
        if self.check(TokenType.LEFT_BRACE):
            self.advance()
            self.skip_newlines()
            
            while not self.check(TokenType.RIGHT_BRACE):
                self.skip_newlines()
                
                if self.check(TokenType.IDENTIFIER):
                    key = self.advance().value
                    self.consume(TokenType.COLON, f"Expected ':' after {key}")
                    # Special handling for simple numeric literals without expression complexity
                    if self.check(TokenType.NUMBER):
                        value_token = self.advance()
                        from synapse_ast import NumberNode
                        config[key] = NumberNode(value_token.value, value_token.line, value_token.column)
                    else:
                        config[key] = self.parse_expression()
                
                self.skip_newlines()
            
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close backend config")
        
        from synapse_ast import QuantumBackendNode
        return QuantumBackendNode(name, config, backend_token.line, backend_token.column)
    
    def parse_quantum_block(self) -> 'BlockNode':
        """Parse quantum execution block"""
        return self.parse_block()
    
    def parse_uncertain_assignment(self) -> AssignmentNode:
        """Parse uncertain variable assignment"""
        token = self.advance()  # consume 'uncertain'
        
        if self.check(TokenType.IDENTIFIER):
            var_name = self.advance().value
            self.consume(TokenType.ASSIGN, f"Expected '=' after variable name")
            
            # Parse value and uncertainty
            value_expr = self.parse_expression()
            
            # Check for ± operator
            if self.check(TokenType.UNCERTAINTY):
                self.advance()
                uncertainty_expr = self.parse_expression()
                
                # Create uncertain node
                if isinstance(value_expr, NumberNode) and isinstance(uncertainty_expr, NumberNode):
                    uncertain_value = UncertainNode(value_expr.value, uncertainty_expr.value, token.line, token.column)
                else:
                    uncertain_value = value_expr  # Fallback to regular value
            else:
                uncertain_value = value_expr
            
            return AssignmentNode(
                IdentifierNode(var_name, token.line, token.column),
                uncertain_value,
                token.line, token.column,
                is_uncertain=True
            )
        
        raise ParseError("Expected variable name after 'uncertain'", self.peek())
    
    def parse_constrain_assignment(self) -> AssignmentNode:
        """Parse constrained variable assignment"""
        token = self.advance()  # consume 'constrain'
        var_name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':' after variable name")
        
        # Parse type/constraint (simplified for now)
        constraint = self.parse_expression()
        
        return AssignmentNode(
            IdentifierNode(var_name, token.line, token.column),
            constraint,
            token.line, token.column,
            is_constrained=True
        )
    
    def parse_evolve_assignment(self) -> AssignmentNode:
        """Parse evolving variable assignment"""
        token = self.advance()  # consume 'evolve'
        var_name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':' after variable name")
        
        # Parse initial value
        initial_value = self.parse_expression()
        
        return AssignmentNode(
            IdentifierNode(var_name, token.line, token.column),
            initial_value,
            token.line, token.column,
            is_evolving=True
        )
    
    def parse_assignment(self) -> AssignmentNode:
        """Parse regular assignment"""
        token = self.peek()
        var_name = self.advance().value
        self.consume(TokenType.ASSIGN, f"Expected '=' after variable name")
        value = self.parse_expression()
        
        return AssignmentNode(
            IdentifierNode(var_name, token.line, token.column),
            value,
            token.line, token.column
        )
    
    def parse_block(self) -> BlockNode:
        """Parse block of statements"""
        token = self.peek()
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        self.skip_newlines()
        
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            if not self.check(TokenType.RIGHT_BRACE):
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        
        return BlockNode(statements, token.line, token.column)
    
    def parse_expression(self) -> ASTNode:
        """Parse expression"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR expression"""
        left = self.parse_logical_and()
        
        while self.check(TokenType.OR):
            token = self.advance()
            right = self.parse_logical_and()
            left = BinaryOpNode("||", left, right, token.line, token.column)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND expression"""
        left = self.parse_equality()
        
        while self.check(TokenType.AND):
            token = self.advance()
            right = self.parse_equality()
            left = BinaryOpNode("&&", left, right, token.line, token.column)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """Parse equality expression"""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            token = self.advance()
            right = self.parse_comparison()
            left = BinaryOpNode(token.value, left, right, token.line, token.column)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison expression"""
        left = self.parse_addition()
        
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN):
            token = self.advance()
            right = self.parse_addition()
            left = BinaryOpNode(token.value, left, right, token.line, token.column)
        
        # Handle arrow operator separately
        if self.check(TokenType.ARROW):
            token = self.advance()
            right = self.parse_addition()
            left = BinaryOpNode("=>", left, right, token.line, token.column)
        
        return left
    
    def parse_addition(self) -> ASTNode:
        """Parse addition/subtraction expression"""
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            token = self.advance()
            right = self.parse_multiplication()
            left = BinaryOpNode(token.value, left, right, token.line, token.column)
        
        return left
    
    def parse_multiplication(self) -> ASTNode:
        """Parse multiplication/division expression"""
        left = self.parse_power()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.advance()
            right = self.parse_power()
            left = BinaryOpNode(token.value, left, right, token.line, token.column)
        
        return left
    
    def parse_power(self) -> ASTNode:
        """Parse power expression"""
        left = self.parse_unary()
        
        while self.check(TokenType.POWER):
            token = self.advance()
            right = self.parse_unary()
            left = BinaryOpNode("^", left, right, token.line, token.column)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary expression"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            token = self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(token.value, operand, token.line, token.column)
        
        return self.parse_call()
    
    def parse_call(self) -> ASTNode:
        """Parse function call"""
        expr = self.parse_primary()
        
        while self.check(TokenType.LEFT_PAREN):
            token = self.advance()
            arguments = []
            
            if not self.check(TokenType.RIGHT_PAREN):
                arguments.append(self.parse_expression())
                while self.check(TokenType.COMMA):
                    self.advance()
                    arguments.append(self.parse_expression())
            
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
            
            if isinstance(expr, IdentifierNode):
                expr = FunctionCallNode(expr, arguments, token.line, token.column)
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expression"""
        token = self.peek()
        
        # Number literal
        if self.check(TokenType.NUMBER):
            self.advance()
            return NumberNode(token.value, token.line, token.column)
        
        # String literal
        if self.check(TokenType.STRING):
            self.advance()
            return StringNode(token.value, token.line, token.column)
        
        # Identifier
        if self.check(TokenType.IDENTIFIER):
            self.advance()
            return IdentifierNode(token.value, token.line, token.column)
        
        # Parenthesized expression
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr

        # List literal: [a, b, c] or Matrix literal: [[a,b], [c,d]]
        if self.check(TokenType.LEFT_BRACKET):
            start = self.advance()
            elements = []
            
            if not self.check(TokenType.RIGHT_BRACKET):
                first_elem = self.parse_expression()
                elements.append(first_elem)
                
                while self.check(TokenType.COMMA):
                    self.advance()
                    elements.append(self.parse_expression())
            
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after literal")
            
            # Check if this is a matrix (all elements are lists of same length)
            from synapse_ast import ListNode, MatrixNode
            if elements and all(isinstance(e, ListNode) for e in elements):
                if len(set(len(e.elements) for e in elements)) == 1:  # Same row length
                    rows = [e.elements for e in elements]
                    return MatrixNode(rows, start.line, start.column)
            
            # Regular list
            return ListNode(elements, start.line, start.column)
        
        # Block expression
        if self.check(TokenType.LEFT_BRACE):
            return self.parse_block()
        
        raise ParseError(f"Unexpected token: {token.type}", token)

def parse(source: str):  # backward compatibility
    from synapse_lang.synapse_parser import parse as _p
    return _p(source)
