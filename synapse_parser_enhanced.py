"""
Enhanced Parser for Synapse Language
Complete implementation with all language constructs
"""

from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
from enum import Enum
from synapse_interpreter import Token, TokenType, Lexer
from synapse_ast_complete import *

class ParseError(Exception):
    """Parse error exception"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.column}")

class Parser:
    """Complete recursive descent parser for Synapse language"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
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
        raise ParseError(message, self.peek())
    
    def skip_newlines(self):
        """Skip newline tokens"""
        while self.check(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> ProgramNode:
        """Parse tokens into complete AST"""
        statements = []
        
        while not self.check(TokenType.EOF):
            self.skip_newlines()
            if not self.check(TokenType.EOF):
                stmt = self.parse_top_level()
                if stmt:
                    statements.append(stmt)
            self.skip_newlines()
        
        return ProgramNode(statements)
    
    def parse_top_level(self) -> Optional[ASTNode]:
        """Parse top-level constructs"""
        self.skip_newlines()
        
        # Structure definition
        if self.match(TokenType.IDENTIFIER) and self.peek().value == "structure":
            return self.parse_structure()
        
        # Theory definition
        if self.match(TokenType.IDENTIFIER) and self.peek().value == "theory":
            return self.parse_theory()
        
        # Hypothesis
        if self.check(TokenType.HYPOTHESIS):
            return self.parse_hypothesis()
        
        # Experiment
        if self.check(TokenType.EXPERIMENT):
            return self.parse_experiment()
        
        # Pipeline
        if self.check(TokenType.PIPELINE):
            return self.parse_pipeline()
        
        # Reason chain
        if self.check(TokenType.REASON):
            return self.parse_reason_chain()
        
        # Symbolic block
        if self.check(TokenType.SYMBOLIC):
            return self.parse_symbolic()
        
        # Regular statement
        return self.parse_statement()
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        self.skip_newlines()
        
        # Parallel block
        if self.check(TokenType.PARALLEL):
            return self.parse_parallel()
        
        # Stream
        if self.check(TokenType.STREAM):
            return self.parse_stream()
        
        # Explore block
        if self.check(TokenType.EXPLORE):
            return self.parse_explore()
        
        # Fork block
        if self.check(TokenType.FORK):
            return self.parse_fork()
        
        # Variable declaration/assignment
        if self.check(TokenType.UNCERTAIN):
            return self.parse_uncertain_declaration()
        
        if self.check(TokenType.CONSTRAIN):
            return self.parse_constrain()
        
        if self.check(TokenType.EVOLVE):
            return self.parse_evolve()
        
        if self.check(TokenType.OBSERVE):
            return self.parse_observe()
        
        # Tensor declaration
        if self.match(TokenType.IDENTIFIER) and self.peek().value == "tensor":
            return self.parse_tensor_declaration()
        
        # Propagate block
        if self.check(TokenType.PROPAGATE):
            return self.parse_propagate()
        
        # Let binding (for symbolic)
        if self.check(TokenType.LET):
            return self.parse_let_binding()
        
        # Generic identifier (variable assignment or function call)
        if self.check(TokenType.IDENTIFIER):
            return self.parse_identifier_statement()
        
        # Expression statement
        return self.parse_expression()
    
    def parse_hypothesis(self) -> HypothesisNode:
        """Parse hypothesis construct"""
        self.consume(TokenType.HYPOTHESIS, "Expected 'hypothesis'")
        name = self.consume(TokenType.IDENTIFIER, "Expected hypothesis name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        assume = None
        predict = None
        validate = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.match(TokenType.IDENTIFIER):
                field = self.peek().value
                if field == "assume":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':'")
                    assume = self.parse_expression()
                elif field == "predict":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':'")
                    predict = self.parse_expression()
                elif field == "validate":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':'")
                    validate = self.parse_expression()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return HypothesisNode(name, assume, predict, validate)
    
    def parse_experiment(self) -> ExperimentNode:
        """Parse experiment construct"""
        self.consume(TokenType.EXPERIMENT, "Expected 'experiment'")
        name = self.consume(TokenType.IDENTIFIER, "Expected experiment name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        setup = None
        parallel_block = None
        synthesize = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.match(TokenType.IDENTIFIER):
                field = self.peek().value
                if field == "setup":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':'")
                    setup = self.parse_expression()
                elif field == "synthesize":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':'")
                    synthesize = self.parse_expression()
            elif self.check(TokenType.PARALLEL):
                parallel_block = self.parse_parallel()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return ExperimentNode(name, setup, parallel_block, synthesize)
    
    def parse_parallel(self) -> ParallelNode:
        """Parse parallel execution block"""
        self.consume(TokenType.PARALLEL, "Expected 'parallel'")
        
        # Optional parallelism factor
        factor = None
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            if self.check(TokenType.NUMBER):
                factor = self.advance().value
            elif self.match(TokenType.IDENTIFIER) and self.peek().value == "auto":
                factor = "auto"
                self.advance()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        branches = []
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.BRANCH):
                self.advance()
                branch_name = self.consume(TokenType.IDENTIFIER, "Expected branch name").value
                self.consume(TokenType.COLON, "Expected ':'")
                branch_body = self.parse_branch_body()
                branches.append(BranchNode(branch_name, branch_body))
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return ParallelNode(branches, factor)
    
    def parse_pipeline(self) -> PipelineNode:
        """Parse pipeline construct"""
        self.consume(TokenType.PIPELINE, "Expected 'pipeline'")
        name = self.consume(TokenType.IDENTIFIER, "Expected pipeline name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        stages = []
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.STAGE):
                stages.append(self.parse_stage())
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return PipelineNode(name, stages)
    
    def parse_stage(self) -> StageNode:
        """Parse pipeline stage"""
        self.consume(TokenType.STAGE, "Expected 'stage'")
        name = self.consume(TokenType.IDENTIFIER, "Expected stage name").value
        
        # Optional parallelism
        parallel_factor = None
        if self.check(TokenType.PARALLEL):
            self.advance()
            if self.check(TokenType.LEFT_PAREN):
                self.advance()
                if self.check(TokenType.NUMBER):
                    parallel_factor = self.advance().value
                elif self.match(TokenType.IDENTIFIER) and self.peek().value == "auto":
                    parallel_factor = "auto"
                    self.advance()
                self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        operations = []
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.FORK):
                operations.append(self.parse_fork())
            elif self.check(TokenType.IDENTIFIER):
                op_name = self.advance().value
                self.consume(TokenType.COLON, "Expected ':'")
                op_value = self.parse_expression()
                operations.append(StageOperationNode(op_name, op_value))
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return StageNode(name, operations, parallel_factor)
    
    def parse_fork(self) -> ForkNode:
        """Parse fork construct for parallel paths"""
        self.consume(TokenType.FORK, "Expected 'fork'")
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        paths = []
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.PATH):
                self.advance()
                path_name = self.consume(TokenType.IDENTIFIER, "Expected path name").value
                self.consume(TokenType.COLON, "Expected ':'")
                path_body = self.parse_block_or_expression()
                paths.append(PathNode(path_name, path_body))
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return ForkNode(paths)
    
    def parse_reason_chain(self) -> ReasonChainNode:
        """Parse reasoning chain"""
        self.consume(TokenType.REASON, "Expected 'reason'")
        self.consume(TokenType.CHAIN, "Expected 'chain'")
        name = self.consume(TokenType.IDENTIFIER, "Expected chain name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        premises = []
        derivations = []
        conclusion = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.PREMISE):
                self.advance()
                premise_id = self.consume(TokenType.IDENTIFIER, "Expected premise ID").value
                self.consume(TokenType.COLON, "Expected ':'")
                premise_text = self.parse_expression()
                premises.append(PremiseNode(premise_id, premise_text))
            
            elif self.check(TokenType.DERIVE):
                self.advance()
                derive_id = self.consume(TokenType.IDENTIFIER, "Expected derivation ID").value
                self.consume(TokenType.IDENTIFIER, "Expected 'from'")  # 'from' keyword
                source_ids = []
                source_ids.append(self.consume(TokenType.IDENTIFIER, "Expected source ID").value)
                while self.check(TokenType.COMMA):
                    self.advance()
                    source_ids.append(self.consume(TokenType.IDENTIFIER, "Expected source ID").value)
                self.consume(TokenType.COLON, "Expected ':'")
                derive_text = self.parse_expression()
                derivations.append(DerivationNode(derive_id, source_ids, derive_text))
            
            elif self.check(TokenType.CONCLUDE):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':'")
                conclusion = self.parse_expression()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return ReasonChainNode(name, premises, derivations, conclusion)
    
    def parse_explore(self) -> ExploreNode:
        """Parse explore construct with backtracking"""
        self.consume(TokenType.EXPLORE, "Expected 'explore'")
        space_name = self.consume(TokenType.IDENTIFIER, "Expected space name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        tries = []
        fallbacks = []
        accept_condition = None
        reject_condition = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.TRY):
                self.advance()
                path_name = self.consume(TokenType.IDENTIFIER, "Expected path name").value
                self.consume(TokenType.COLON, "Expected ':'")
                path_body = self.parse_expression()
                tries.append(TryPathNode(path_name, path_body))
            
            elif self.check(TokenType.FALLBACK):
                self.advance()
                path_name = self.consume(TokenType.IDENTIFIER, "Expected path name").value
                self.consume(TokenType.COLON, "Expected ':'")
                path_body = self.parse_expression()
                fallbacks.append(FallbackPathNode(path_name, path_body))
            
            elif self.check(TokenType.ACCEPT):
                self.advance()
                self.consume(TokenType.IDENTIFIER, "Expected 'when'")
                self.consume(TokenType.COLON, "Expected ':'")
                accept_condition = self.parse_expression()
            
            elif self.check(TokenType.REJECT):
                self.advance()
                self.consume(TokenType.IDENTIFIER, "Expected 'when'")
                self.consume(TokenType.COLON, "Expected ':'")
                reject_condition = self.parse_expression()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return ExploreNode(space_name, tries, fallbacks, accept_condition, reject_condition)
    
    def parse_symbolic(self) -> SymbolicNode:
        """Parse symbolic mathematics block"""
        self.consume(TokenType.SYMBOLIC, "Expected 'symbolic'")
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        bindings = []
        operations = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.LET):
                bindings.append(self.parse_let_binding())
            elif self.check(TokenType.SOLVE):
                operations.append(self.parse_solve())
            elif self.check(TokenType.PROVE):
                operations.append(self.parse_prove())
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return SymbolicNode(bindings, operations)
    
    def parse_let_binding(self) -> LetBindingNode:
        """Parse let binding for symbolic math"""
        self.consume(TokenType.LET, "Expected 'let'")
        
        # Parse function or variable name
        name = self.consume(TokenType.IDENTIFIER, "Expected name").value
        
        # Check for function parameters
        params = []
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            if not self.check(TokenType.RIGHT_PAREN):
                params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter").value)
                while self.check(TokenType.COMMA):
                    self.advance()
                    params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter").value)
            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
        
        self.consume(TokenType.ASSIGN, "Expected '='")
        
        # Parse the expression - collect all tokens until newline or next statement
        expr_tokens = []
        depth = 0
        while not (self.check(TokenType.NEWLINE) and depth == 0) and not self.check(TokenType.RIGHT_BRACE):
            if self.check(TokenType.LEFT_PAREN):
                depth += 1
            elif self.check(TokenType.RIGHT_PAREN):
                depth -= 1
                if depth < 0:
                    break
            
            # Check for next let/solve/prove
            if depth == 0 and self.match(TokenType.LET, TokenType.SOLVE, TokenType.PROVE):
                break
            
            token = self.advance()
            expr_tokens.append(token.value if token.value else str(token.type))
        
        # Create simplified expression node
        expr_str = ' '.join(str(t) for t in expr_tokens)
        expression = IdentifierNode(expr_str)
        
        return LetBindingNode(name, params, expression)
    
    def parse_solve(self) -> SolveNode:
        """Parse solve operation"""
        self.consume(TokenType.SOLVE, "Expected 'solve'")
        self.consume(TokenType.COLON, "Expected ':'")
        
        # Parse equation
        equation = self.parse_expression()
        
        # Parse 'for' variable
        variable = None
        if self.match(TokenType.IDENTIFIER) and self.peek().value == "for":
            self.advance()
            variable = self.consume(TokenType.IDENTIFIER, "Expected variable").value
        
        return SolveNode(equation, variable)
    
    def parse_prove(self) -> ProveNode:
        """Parse prove operation"""
        self.consume(TokenType.PROVE, "Expected 'prove'")
        self.consume(TokenType.COLON, "Expected ':'")
        
        # Save position to parse statement
        statement_parts = []
        
        # Parse until we hit 'for' or end of statement
        while not self.check(TokenType.NEWLINE) and not self.check(TokenType.RIGHT_BRACE):
            if self.match(TokenType.IDENTIFIER) and self.peek().value == "for":
                break
            
            # Collect tokens for the statement
            token = self.advance()
            statement_parts.append(token.value if token.value else str(token.type))
        
        # Reconstruct statement
        statement_str = ' '.join(str(p) for p in statement_parts)
        statement = IdentifierNode(statement_str)  # Simplified for now
        
        # Parse optional domain
        domain = None
        if self.match(TokenType.IDENTIFIER) and self.peek().value == "for":
            self.advance()
            if self.match(TokenType.IDENTIFIER) and self.peek().value == "all":
                self.advance()
            variable = self.consume(TokenType.IDENTIFIER, "Expected variable").value
            if self.match(TokenType.IDENTIFIER) and self.peek().value == "in":
                self.advance()
            domain_type = self.consume(TokenType.IDENTIFIER, "Expected domain").value
            domain = IdentifierNode(domain_type)
        
        return ProveNode(statement, domain)
    
    def parse_uncertain_declaration(self) -> UncertainDeclarationNode:
        """Parse uncertain value declaration"""
        self.consume(TokenType.UNCERTAIN, "Expected 'uncertain'")
        
        # Optional type
        value_type = None
        if self.match(TokenType.IDENTIFIER) and self.peek().value in ["value", "distribution"]:
            value_type = self.advance().value
        
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.ASSIGN, "Expected '='")
        
        # Parse value with uncertainty
        value = self.parse_expression()
        uncertainty = None
        
        if self.check(TokenType.UNCERTAINTY):
            self.advance()
            uncertainty = self.parse_expression()
        
        return UncertainDeclarationNode(name, value, uncertainty, value_type)
    
    def parse_constrain(self) -> ConstrainNode:
        """Parse constrain declaration"""
        self.consume(TokenType.CONSTRAIN, "Expected 'constrain'")
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':'")
        
        # Parse type
        var_type = self.consume(TokenType.IDENTIFIER, "Expected type").value
        
        # Parse constraint
        constraint = None
        if self.match(TokenType.IDENTIFIER) and self.peek().value == "where":
            self.advance()
            constraint = self.parse_expression()
        
        return ConstrainNode(variable, var_type, constraint)
    
    def parse_evolve(self) -> EvolveNode:
        """Parse evolve declaration"""
        self.consume(TokenType.EVOLVE, "Expected 'evolve'")
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':'")
        
        # Parse type
        var_type = self.consume(TokenType.IDENTIFIER, "Expected type").value
        
        # Parse initial value
        initial = None
        if self.check(TokenType.ASSIGN):
            self.advance()
            initial = self.parse_expression()
        
        return EvolveNode(variable, var_type, initial)
    
    def parse_observe(self) -> ObserveNode:
        """Parse observe declaration"""
        self.consume(TokenType.OBSERVE, "Expected 'observe'")
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':'")
        
        # Parse type
        var_type = self.consume(TokenType.IDENTIFIER, "Expected type").value
        
        # Parse condition
        condition = None
        if self.match(TokenType.IDENTIFIER) and self.peek().value == "until":
            self.advance()
            condition = self.parse_expression()
        
        return ObserveNode(variable, var_type, condition)
    
    def parse_tensor_declaration(self) -> TensorDeclarationNode:
        """Parse tensor declaration"""
        self.advance()  # consume 'tensor'
        
        # Parse name and dimensions
        name = self.consume(TokenType.IDENTIFIER, "Expected tensor name").value
        
        dimensions = []
        if self.check(TokenType.LEFT_BRACKET):
            self.advance()
            dimensions.append(self.parse_expression())
            while self.check(TokenType.COMMA):
                self.advance()
                dimensions.append(self.parse_expression())
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
        
        # Parse initialization
        initializer = None
        if self.check(TokenType.ASSIGN):
            self.advance()
            initializer = self.parse_expression()
        
        return TensorDeclarationNode(name, dimensions, initializer)
    
    def parse_propagate(self) -> PropagateNode:
        """Parse propagate uncertainty block"""
        self.consume(TokenType.PROPAGATE, "Expected 'propagate'")
        self.consume(TokenType.IDENTIFIER, "Expected 'uncertainty'")
        self.consume(TokenType.IDENTIFIER, "Expected 'through'")
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        operations = []
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            operations.append(self.parse_statement())
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return PropagateNode(operations)
    
    def parse_stream(self) -> StreamNode:
        """Parse stream declaration"""
        self.consume(TokenType.STREAM, "Expected 'stream'")
        name = self.consume(TokenType.IDENTIFIER, "Expected stream name").value
        self.consume(TokenType.COLON, "Expected ':'")
        body = self.parse_expression()
        return StreamNode(name, body)
    
    def parse_structure(self) -> StructureNode:
        """Parse structure definition"""
        self.advance()  # consume 'structure'
        name = self.consume(TokenType.IDENTIFIER, "Expected structure name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        fields = []
        invariants = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.match(TokenType.IDENTIFIER):
                if self.peek().value == "invariant":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':'")
                    invariants.append(self.parse_expression())
                else:
                    field_name = self.advance().value
                    self.consume(TokenType.COLON, "Expected ':'")
                    field_type = self.parse_type_expression()
                    fields.append(FieldNode(field_name, field_type))
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return StructureNode(name, fields, invariants)
    
    def parse_theory(self) -> TheoryNode:
        """Parse theory definition"""
        self.advance()  # consume 'theory'
        name = self.consume(TokenType.IDENTIFIER, "Expected theory name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        components = []
        invariants = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.match(TokenType.IDENTIFIER):
                if self.peek().value == "invariant":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':'")
                    invariants.append(self.parse_expression())
                else:
                    comp_name = self.advance().value
                    self.consume(TokenType.COLON, "Expected ':'")
                    comp_type = self.parse_type_expression()
                    components.append(ComponentNode(comp_name, comp_type))
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return TheoryNode(name, components, invariants)
    
    def parse_identifier_statement(self) -> ASTNode:
        """Parse statement starting with identifier"""
        name = self.advance().value
        
        # Check for assignment
        if self.check(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
            return AssignmentNode(name, value)
        
        # Check for channel send
        elif self.check(TokenType.CHANNEL_SEND):
            self.advance()
            value = self.parse_expression()
            return ChannelSendNode(name, value)
        
        # Function call
        else:
            return self.parse_function_call(name)
    
    def parse_expression(self) -> ExpressionNode:
        """Parse expression with operator precedence"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ExpressionNode:
        """Parse logical OR expression"""
        left = self.parse_logical_and()
        
        while self.check(TokenType.OR):
            op = self.advance()
            right = self.parse_logical_and()
            left = BinaryOpNode(left, op.type, right)
        
        return left
    
    def parse_logical_and(self) -> ExpressionNode:
        """Parse logical AND expression"""
        left = self.parse_equality()
        
        while self.check(TokenType.AND):
            op = self.advance()
            right = self.parse_equality()
            left = BinaryOpNode(left, op.type, right)
        
        return left
    
    def parse_equality(self) -> ExpressionNode:
        """Parse equality expression"""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            op = self.advance()
            right = self.parse_comparison()
            left = BinaryOpNode(left, op.type, right)
        
        return left
    
    def parse_comparison(self) -> ExpressionNode:
        """Parse comparison expression"""
        left = self.parse_implication()
        
        while self.match(TokenType.LESS_THAN, TokenType.GREATER_THAN):
            op = self.advance()
            right = self.parse_implication()
            left = BinaryOpNode(left, op.type, right)
        
        return left
    
    def parse_implication(self) -> ExpressionNode:
        """Parse implication (=>) expression"""
        left = self.parse_addition()
        
        if self.check(TokenType.ARROW):
            self.advance()
            right = self.parse_implication()
            return ImplicationNode(left, right)
        
        return left
    
    def parse_addition(self) -> ExpressionNode:
        """Parse addition/subtraction expression"""
        left = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_multiplication()
            left = BinaryOpNode(left, op.type, right)
        
        return left
    
    def parse_multiplication(self) -> ExpressionNode:
        """Parse multiplication/division expression"""
        left = self.parse_exponentiation()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.advance()
            right = self.parse_exponentiation()
            left = BinaryOpNode(left, op.type, right)
        
        return left
    
    def parse_exponentiation(self) -> ExpressionNode:
        """Parse exponentiation expression"""
        left = self.parse_unary()
        
        if self.check(TokenType.POWER):
            self.advance()
            right = self.parse_exponentiation()  # Right associative
            return BinaryOpNode(left, TokenType.POWER, right)
        
        return left
    
    def parse_unary(self) -> ExpressionNode:
        """Parse unary expression"""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance()
            expr = self.parse_unary()
            return UnaryOpNode(op.type, expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ExpressionNode:
        """Parse postfix expressions (function calls, array access, etc.)"""
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
                # Array/tensor access
                self.advance()
                indices = []
                indices.append(self.parse_expression())
                while self.check(TokenType.COMMA):
                    self.advance()
                    indices.append(self.parse_expression())
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
                expr = IndexAccessNode(expr, indices)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ExpressionNode:
        """Parse primary expression"""
        # Number literal
        if self.check(TokenType.NUMBER):
            value = self.advance().value
            return NumberNode(value)
        
        # String literal
        if self.check(TokenType.STRING):
            value = self.advance().value
            return StringNode(value)
        
        # Identifier
        if self.check(TokenType.IDENTIFIER):
            name = self.advance().value
            return IdentifierNode(name)
        
        # Grouped expression
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
            return expr
        
        # Block expression
        if self.check(TokenType.LEFT_BRACE):
            return self.parse_block()
        
        raise ParseError(f"Unexpected token: {self.peek()}", self.peek())
    
    def parse_block(self) -> BlockNode:
        """Parse block of statements"""
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        
        statements = []
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            if not self.check(TokenType.RIGHT_BRACE):
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        return BlockNode(statements)
    
    def parse_block_or_expression(self) -> ASTNode:
        """Parse either a block or an expression"""
        if self.check(TokenType.LEFT_BRACE):
            return self.parse_block()
        return self.parse_expression()
    
    def parse_branch_body(self) -> ASTNode:
        """Parse the body of a branch"""
        if self.check(TokenType.LEFT_BRACE):
            return self.parse_block()
        return self.parse_expression()
    
    def parse_type_expression(self) -> TypeNode:
        """Parse type expression"""
        # Basic implementation - can be extended
        if self.check(TokenType.IDENTIFIER):
            type_name = self.advance().value
            
            # Check for parameterized types
            if self.check(TokenType.LESS_THAN):
                self.advance()
                params = []
                params.append(self.parse_type_expression())
                while self.check(TokenType.COMMA):
                    self.advance()
                    params.append(self.parse_type_expression())
                self.consume(TokenType.GREATER_THAN, "Expected '>'")
                return ParameterizedTypeNode(type_name, params)
            
            # Check for tensor dimensions
            if self.check(TokenType.LEFT_BRACKET):
                self.advance()
                dimensions = []
                if not self.check(TokenType.RIGHT_BRACKET):
                    dimensions.append(self.parse_expression())
                    while self.check(TokenType.COMMA):
                        self.advance()
                        dimensions.append(self.parse_expression())
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
                return TensorTypeNode(type_name, dimensions)
            
            return SimpleTypeNode(type_name)
        
        raise ParseError("Expected type expression", self.peek())
    
    def parse_function_call(self, name: str) -> FunctionCallNode:
        """Parse function call"""
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            args = []
            if not self.check(TokenType.RIGHT_PAREN):
                args.append(self.parse_expression())
                while self.check(TokenType.COMMA):
                    self.advance()
                    args.append(self.parse_expression())
            self.consume(TokenType.RIGHT_PAREN, "Expected ')'")
            return FunctionCallNode(IdentifierNode(name), args)
        
        return IdentifierNode(name)


def parse_synapse_code(source: str) -> ProgramNode:
    """Helper function to parse Synapse source code"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()