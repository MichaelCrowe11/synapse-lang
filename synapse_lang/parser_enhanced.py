"""Enhanced Synapse Parser - Complete implementation matching language specification."""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum, auto
from .synapse_lexer import Token, TokenType, Lexer
from .synapse_ast import *
from .ast_consolidated import *


class ParseError(Exception):
    """Enhanced parse error with context."""
    def __init__(self, message: str, token: Token, context: Optional[str] = None):
        self.message = message
        self.token = token
        self.context = context
        error_msg = f"{message} at line {token.line}, column {token.column}"
        if context:
            error_msg += f"\nContext: {context}"
        super().__init__(error_msg)


# Enhanced AST Nodes for complete language features
@dataclass
class HypothesisNode(ASTNode):
    """Hypothesis construct with assumptions, predictions, and validation."""
    name: str
    assumptions: List[ASTNode]
    predictions: List[ASTNode]
    validations: List[ASTNode]
    
    def __init__(self, name: str, assumptions: List[ASTNode], 
                 predictions: List[ASTNode], validations: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.HYPOTHESIS, line, column)
        self.name = name
        self.assumptions = assumptions
        self.predictions = predictions
        self.validations = validations


@dataclass
class ExperimentNode(ASTNode):
    """Experiment with setup, parallel branches, and synthesis."""
    name: str
    setup: Optional[ASTNode]
    branches: List['BranchNode']
    synthesize: Optional[ASTNode]
    
    def __init__(self, name: str, setup: Optional[ASTNode],
                 branches: List['BranchNode'], synthesize: Optional[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.EXPERIMENT, line, column)
        self.name = name
        self.setup = setup
        self.branches = branches
        self.synthesize = synthesize


@dataclass 
class BranchNode(ASTNode):
    """Parallel execution branch."""
    name: str
    body: List[ASTNode]
    
    def __init__(self, name: str, body: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.BRANCH, line, column)
        self.name = name
        self.body = body


@dataclass
class ReasonChainNode(ASTNode):
    """Reasoning chain with premises, derivations, and conclusions."""
    name: str
    premises: List['PremiseNode']
    derivations: List['DeriveNode']
    conclusions: List['ConcludeNode']
    
    def __init__(self, name: str, premises: List['PremiseNode'],
                 derivations: List['DeriveNode'], conclusions: List['ConcludeNode'],
                 line: int, column: int):
        super().__init__(NodeType.REASON_CHAIN, line, column)
        self.name = name
        self.premises = premises
        self.derivations = derivations
        self.conclusions = conclusions


@dataclass
class PremiseNode(ASTNode):
    """Logical premise in reasoning chain."""
    name: str
    statement: str
    
    def __init__(self, name: str, statement: str, line: int, column: int):
        super().__init__(NodeType.PREMISE, line, column)
        self.name = name
        self.statement = statement


@dataclass
class DeriveNode(ASTNode):
    """Derivation from premises."""
    name: str
    from_premise: str
    statement: str
    
    def __init__(self, name: str, from_premise: str, statement: str,
                 line: int, column: int):
        super().__init__(NodeType.DERIVE, line, column)
        self.name = name
        self.from_premise = from_premise
        self.statement = statement


@dataclass
class ConcludeNode(ASTNode):
    """Conclusion from reasoning."""
    expression: ASTNode
    
    def __init__(self, expression: ASTNode, line: int, column: int):
        super().__init__(NodeType.CONCLUDE, line, column)
        self.expression = expression


@dataclass
class UncertaintyNode(ASTNode):
    """Uncertainty quantification with value and error."""
    value: float
    uncertainty: float
    distribution: Optional[str]
    
    def __init__(self, value: float, uncertainty: float, 
                 distribution: Optional[str], line: int, column: int):
        super().__init__(NodeType.UNCERTAIN, line, column)
        self.value = value
        self.uncertainty = uncertainty
        self.distribution = distribution


@dataclass
class PropagateNode(ASTNode):
    """Uncertainty propagation through calculations."""
    uncertainty_vars: List[str]
    body: List[ASTNode]
    
    def __init__(self, uncertainty_vars: List[str], body: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.PROPAGATE, line, column)
        self.uncertainty_vars = uncertainty_vars
        self.body = body


@dataclass
class PipelineNode(ASTNode):
    """Data processing pipeline with stages."""
    name: str
    stages: List['StageNode']
    
    def __init__(self, name: str, stages: List['StageNode'],
                 line: int, column: int):
        super().__init__(NodeType.PIPELINE, line, column)
        self.name = name
        self.stages = stages


@dataclass
class StageNode(ASTNode):
    """Pipeline stage with parallel execution."""
    name: str
    parallelism: Optional[int]
    operations: Dict[str, ASTNode]
    fork_paths: Optional[Dict[str, ASTNode]]
    
    def __init__(self, name: str, parallelism: Optional[int],
                 operations: Dict[str, ASTNode], fork_paths: Optional[Dict[str, ASTNode]],
                 line: int, column: int):
        super().__init__(NodeType.STAGE, line, column)
        self.name = name
        self.parallelism = parallelism
        self.operations = operations
        self.fork_paths = fork_paths


@dataclass
class ExploreNode(ASTNode):
    """Solution space exploration with backtracking."""
    name: str
    try_paths: List['TryNode']
    fallback_paths: List['FallbackNode']
    accept_condition: Optional[ASTNode]
    reject_condition: Optional[ASTNode]
    
    def __init__(self, name: str, try_paths: List['TryNode'],
                 fallback_paths: List['FallbackNode'],
                 accept_condition: Optional[ASTNode],
                 reject_condition: Optional[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.EXPLORE, line, column)
        self.name = name
        self.try_paths = try_paths
        self.fallback_paths = fallback_paths
        self.accept_condition = accept_condition
        self.reject_condition = reject_condition


@dataclass
class TryNode(ASTNode):
    """Try path in exploration."""
    name: str
    expression: ASTNode
    
    def __init__(self, name: str, expression: ASTNode, line: int, column: int):
        super().__init__(NodeType.TRY, line, column)
        self.name = name
        self.expression = expression


@dataclass
class FallbackNode(ASTNode):
    """Fallback path in exploration."""
    name: str
    expression: ASTNode
    
    def __init__(self, name: str, expression: ASTNode, line: int, column: int):
        super().__init__(NodeType.FALLBACK, line, column)
        self.name = name
        self.expression = expression


@dataclass
class StreamNode(ASTNode):
    """Thought stream for parallel processing."""
    name: str
    expression: ASTNode
    
    def __init__(self, name: str, expression: ASTNode, line: int, column: int):
        super().__init__(NodeType.STREAM, line, column)
        self.name = name
        self.expression = expression


@dataclass
class SymbolicNode(ASTNode):
    """Symbolic mathematics block."""
    declarations: List[ASTNode]
    operations: List[ASTNode]
    
    def __init__(self, declarations: List[ASTNode], operations: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.PROVE, line, column)
        self.declarations = declarations
        self.operations = operations


@dataclass
class ConstraintNode(ASTNode):
    """Variable constraint definition."""
    variable: str
    var_type: str
    constraints: List[ASTNode]
    
    def __init__(self, variable: str, var_type: str, constraints: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.variable = variable
        self.var_type = var_type
        self.constraints = constraints


@dataclass
class ParallelNode(ASTNode):
    """Parallel execution block."""
    branches: List[BranchNode]
    num_workers: Optional[int]
    
    def __init__(self, branches: List[BranchNode], num_workers: Optional[int],
                 line: int, column: int):
        super().__init__(NodeType.PARALLEL, line, column)
        self.branches = branches
        self.num_workers = num_workers


@dataclass
class TensorNode(ASTNode):
    """Tensor with dimensions and operations."""
    name: str
    dimensions: List[int]
    initializer: Optional[ASTNode]
    
    def __init__(self, name: str, dimensions: List[int], 
                 initializer: Optional[ASTNode], line: int, column: int):
        super().__init__(NodeType.TENSOR, line, column)
        self.name = name
        self.dimensions = dimensions
        self.initializer = initializer


@dataclass
class ChannelNode(ASTNode):
    """Message passing channel."""
    name: str
    data_type: str
    
    def __init__(self, name: str, data_type: str, line: int, column: int):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name
        self.data_type = data_type


@dataclass
class AsyncNode(ASTNode):
    """Async execution block."""
    name: str
    body: List[ASTNode]
    parallel_count: Optional[int]
    
    def __init__(self, name: str, body: List[ASTNode], 
                 parallel_count: Optional[int], line: int, column: int):
        super().__init__(NodeType.PARALLEL, line, column)
        self.name = name
        self.body = body
        self.parallel_count = parallel_count


class EnhancedParser:
    """Complete Synapse parser with all language features."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.error_recovery = True
        self.max_errors = 10
        self.errors: List[ParseError] = []
    
    def peek(self) -> Token:
        """Look at current token without consuming."""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]  # EOF token
    
    def peek_ahead(self, n: int = 1) -> Token:
        """Look ahead n tokens."""
        pos = self.current + n
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self) -> Token:
        """Consume and return current token."""
        token = self.peek()
        if token.type != TokenType.EOF:
            self.current += 1
        return token
    
    def check(self, token_type: TokenType) -> bool:
        """Check if current token matches type."""
        return self.peek().type == token_type
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        return any(self.check(t) for t in token_types)
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume token of expected type or raise/recover from error."""
        if self.check(token_type):
            return self.advance()
        
        error = ParseError(message, self.peek())
        if self.error_recovery:
            self.errors.append(error)
            if len(self.errors) > self.max_errors:
                raise error
            # Try to recover by synchronizing
            self.synchronize()
            return self.peek()  # Return current token after sync
        raise error
    
    def synchronize(self):
        """Synchronize parser after error for recovery."""
        while not self.check(TokenType.EOF):
            # Stop at statement boundaries
            if self.match(TokenType.NEWLINE, TokenType.SEMICOLON):
                self.advance()
                return
            
            # Stop at keywords that start statements
            if self.match(TokenType.HYPOTHESIS, TokenType.EXPERIMENT,
                         TokenType.PARALLEL, TokenType.STREAM,
                         TokenType.REASON, TokenType.PIPELINE,
                         TokenType.EXPLORE, TokenType.QUANTUM):
                return
            
            self.advance()
    
    def skip_newlines(self):
        """Skip newline tokens."""
        while self.check(TokenType.NEWLINE):
            self.advance()
    
    def parse(self) -> ASTNode:
        """Parse tokens into complete AST."""
        statements = []
        
        while not self.check(TokenType.EOF):
            self.skip_newlines()
            if not self.check(TokenType.EOF):
                try:
                    stmt = self.parse_statement()
                    if stmt:
                        statements.append(stmt)
                except ParseError as e:
                    if not self.error_recovery:
                        raise
                    # Continue parsing after error
            self.skip_newlines()
        
        # Report collected errors if any
        if self.errors:
            print(f"Parsing completed with {len(self.errors)} error(s)")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"  - {error}")
        
        return ProgramNode(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement with all language constructs."""
        self.skip_newlines()
        
        # Hypothesis construct
        if self.check(TokenType.HYPOTHESIS):
            return self.parse_hypothesis()
        
        # Experiment construct
        if self.check(TokenType.EXPERIMENT):
            return self.parse_experiment()
        
        # Parallel execution
        if self.check(TokenType.PARALLEL):
            return self.parse_parallel()
        
        # Stream definition
        if self.check(TokenType.STREAM):
            return self.parse_stream()
        
        # Reasoning chain
        if self.check(TokenType.REASON):
            return self.parse_reason_chain()
        
        # Pipeline definition
        if self.check(TokenType.PIPELINE):
            return self.parse_pipeline()
        
        # Exploration with backtracking
        if self.check(TokenType.EXPLORE):
            return self.parse_explore()
        
        # Quantum constructs
        if self.check(TokenType.QUANTUM):
            return self.parse_quantum()
        
        # Symbolic mathematics
        if self.check(TokenType.SYMBOLIC):
            return self.parse_symbolic()
        
        # Uncertainty propagation
        if self.check(TokenType.PROPAGATE):
            return self.parse_propagate()
        
        # Constraint definition
        if self.check(TokenType.CONSTRAIN):
            return self.parse_constraint()
        
        # Note: Tensor, Channel, and Async syntax currently handled through identifiers
        # Future versions may add dedicated tokens for these constructs
        
        # Run statement
        if self.check(TokenType.RUN):
            return self.parse_run()
        
        # Variable declarations
        if self.check(TokenType.UNCERTAIN):
            return self.parse_uncertain_declaration()
        
        if self.check(TokenType.EVOLVE):
            return self.parse_evolve_declaration()
        
        if self.check(TokenType.OBSERVE):
            return self.parse_observe_declaration()
        
        # Expression or assignment
        return self.parse_expression_statement()
    
    def parse_hypothesis(self) -> HypothesisNode:
        """Parse hypothesis construct."""
        hyp_tok = self.advance()  # consume 'hypothesis'
        name = self.consume(TokenType.IDENTIFIER, "Expected hypothesis name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after hypothesis name")
        self.skip_newlines()
        
        assumptions = []
        predictions = []
        validations = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.ASSUME):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'assume'")
                assumptions.append(self.parse_expression())
            
            elif self.check(TokenType.PREDICT):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'predict'")
                predictions.append(self.parse_expression())
            
            elif self.check(TokenType.VALIDATE):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'validate'")
                validations.append(self.parse_expression())
            
            else:
                # Skip unknown tokens in hypothesis body
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close hypothesis")
        
        return HypothesisNode(name, assumptions, predictions, validations,
                            hyp_tok.line, hyp_tok.column)
    
    def parse_experiment(self) -> ExperimentNode:
        """Parse experiment construct."""
        exp_tok = self.advance()  # consume 'experiment'
        name = self.consume(TokenType.IDENTIFIER, "Expected experiment name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after experiment name")
        self.skip_newlines()
        
        setup = None
        branches = []
        synthesize = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.SETUP):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'setup'")
                setup = self.parse_expression()
            
            elif self.check(TokenType.PARALLEL):
                self.advance()
                self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'parallel'")
                self.skip_newlines()
                
                while not self.check(TokenType.RIGHT_BRACE):
                    self.skip_newlines()
                    if self.check(TokenType.BRANCH):
                        branches.append(self.parse_branch())
                    else:
                        self.advance()
                    self.skip_newlines()
                
                self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close parallel")
            
            elif self.check(TokenType.SYNTHESIZE):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'synthesize'")
                synthesize = self.parse_expression()
            
            else:
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close experiment")
        
        return ExperimentNode(name, setup, branches, synthesize,
                            exp_tok.line, exp_tok.column)
    
    def parse_branch(self) -> BranchNode:
        """Parse branch in parallel block."""
        branch_tok = self.advance()  # consume 'branch'
        name = self.consume(TokenType.IDENTIFIER, "Expected branch name").value
        self.consume(TokenType.COLON, "Expected ':' after branch name")
        
        body = []
        # Parse either single expression or block
        if self.check(TokenType.LEFT_BRACE):
            self.advance()
            self.skip_newlines()
            while not self.check(TokenType.RIGHT_BRACE):
                body.append(self.parse_statement())
                self.skip_newlines()
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close branch")
        else:
            body.append(self.parse_expression())
        
        return BranchNode(name, body, branch_tok.line, branch_tok.column)
    
    def parse_parallel(self) -> ParallelNode:
        """Parse parallel execution block."""
        par_tok = self.advance()  # consume 'parallel'
        
        num_workers = None
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            if self.check(TokenType.NUMBER):
                num_workers = int(self.advance().value)
            elif self.check(TokenType.AUTO):
                self.advance()
                num_workers = -1  # Auto-detect
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parallel workers")
        
        branches = []
        if self.check(TokenType.MAP):
            # Parallel map operation
            self.advance()
            source = self.parse_expression()
            self.consume(TokenType.LEFT_BRACE, "Expected '{' for map body")
            self.skip_newlines()
            
            map_var = self.consume(TokenType.IDENTIFIER, "Expected map variable").value
            self.consume(TokenType.ARROW, "Expected '=>' in map")
            map_expr = self.parse_expression()
            
            self.skip_newlines()
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close map")
            
            if self.check(TokenType.INTO):
                self.advance()
                target = self.parse_expression()
            else:
                target = None
            
            # Create synthetic branch for map
            branch = BranchNode("map", [map_expr], par_tok.line, par_tok.column)
            branches.append(branch)
        
        else:
            # Regular parallel block
            self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'parallel'")
            self.skip_newlines()
            
            while not self.check(TokenType.RIGHT_BRACE):
                self.skip_newlines()
                if self.check(TokenType.BRANCH):
                    branches.append(self.parse_branch())
                else:
                    # Allow inline expressions
                    expr = self.parse_expression()
                    branches.append(BranchNode(f"branch_{len(branches)}", [expr],
                                              expr.line, expr.column))
                self.skip_newlines()
            
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close parallel")
        
        return ParallelNode(branches, num_workers, par_tok.line, par_tok.column)
    
    def parse_stream(self) -> StreamNode:
        """Parse thought stream definition."""
        stream_tok = self.advance()  # consume 'stream'
        name = self.consume(TokenType.IDENTIFIER, "Expected stream name").value
        self.consume(TokenType.COLON, "Expected ':' after stream name")
        expression = self.parse_expression()
        
        return StreamNode(name, expression, stream_tok.line, stream_tok.column)
    
    def parse_reason_chain(self) -> ReasonChainNode:
        """Parse reasoning chain."""
        reason_tok = self.advance()  # consume 'reason'
        
        if self.check(TokenType.CHAIN):
            self.advance()
        
        name = self.consume(TokenType.IDENTIFIER, "Expected chain name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after chain name")
        self.skip_newlines()
        
        premises = []
        derivations = []
        conclusions = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.PREMISE):
                self.advance()
                p_name = self.consume(TokenType.IDENTIFIER, "Expected premise name").value
                self.consume(TokenType.COLON, "Expected ':' after premise name")
                statement = self.consume(TokenType.STRING, "Expected premise statement").value
                premises.append(PremiseNode(p_name, statement, 
                                          self.peek().line, self.peek().column))
            
            elif self.check(TokenType.DERIVE):
                self.advance()
                d_name = self.consume(TokenType.IDENTIFIER, "Expected derivation name").value
                self.consume(TokenType.FROM, "Expected 'from' in derivation")
                from_premise = self.consume(TokenType.IDENTIFIER, "Expected premise reference").value
                self.consume(TokenType.COLON, "Expected ':' after derivation")
                statement = self.consume(TokenType.STRING, "Expected derivation statement").value
                derivations.append(DeriveNode(d_name, from_premise, statement,
                                             self.peek().line, self.peek().column))
            
            elif self.check(TokenType.CONCLUDE):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'conclude'")
                expr = self.parse_expression()
                conclusions.append(ConcludeNode(expr, expr.line, expr.column))
            
            else:
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close reason chain")
        
        return ReasonChainNode(name, premises, derivations, conclusions,
                              reason_tok.line, reason_tok.column)
    
    def parse_pipeline(self) -> PipelineNode:
        """Parse data processing pipeline."""
        pipe_tok = self.advance()  # consume 'pipeline'
        name = self.consume(TokenType.IDENTIFIER, "Expected pipeline name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after pipeline name")
        self.skip_newlines()
        
        stages = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.STAGE):
                stages.append(self.parse_stage())
            else:
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close pipeline")
        
        return PipelineNode(name, stages, pipe_tok.line, pipe_tok.column)
    
    def parse_stage(self) -> StageNode:
        """Parse pipeline stage."""
        stage_tok = self.advance()  # consume 'stage'
        name = self.consume(TokenType.IDENTIFIER, "Expected stage name").value
        
        parallelism = None
        if self.check(TokenType.PARALLEL):
            self.advance()
            self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'parallel'")
            if self.check(TokenType.NUMBER):
                parallelism = int(self.advance().value)
            elif self.check(TokenType.AUTO):
                self.advance()
                parallelism = -1
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parallelism")
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after stage name")
        self.skip_newlines()
        
        operations = {}
        fork_paths = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.FORK):
                self.advance()
                self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'fork'")
                self.skip_newlines()
                
                fork_paths = {}
                while not self.check(TokenType.RIGHT_BRACE):
                    self.skip_newlines()
                    if self.check(TokenType.PATH):
                        self.advance()
                        path_name = self.consume(TokenType.IDENTIFIER, "Expected path name").value
                        self.consume(TokenType.COLON, "Expected ':' after path name")
                        fork_paths[path_name] = self.parse_expression()
                    else:
                        self.advance()
                    self.skip_newlines()
                
                self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close fork")
            
            elif self.check(TokenType.IDENTIFIER):
                op_name = self.advance().value
                self.consume(TokenType.COLON, "Expected ':' after operation name")
                operations[op_name] = self.parse_expression()
            
            else:
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close stage")
        
        return StageNode(name, parallelism, operations, fork_paths,
                        stage_tok.line, stage_tok.column)
    
    def parse_explore(self) -> ExploreNode:
        """Parse solution space exploration."""
        explore_tok = self.advance()  # consume 'explore'
        name = self.consume(TokenType.IDENTIFIER, "Expected exploration name").value
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after exploration name")
        self.skip_newlines()
        
        try_paths = []
        fallback_paths = []
        accept_condition = None
        reject_condition = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.TRY):
                self.advance()
                path_name = self.consume(TokenType.IDENTIFIER, "Expected try path name").value
                self.consume(TokenType.COLON, "Expected ':' after path name")
                expr = self.parse_expression()
                try_paths.append(TryNode(path_name, expr, explore_tok.line, explore_tok.column))
            
            elif self.check(TokenType.FALLBACK):
                self.advance()
                path_name = self.consume(TokenType.IDENTIFIER, "Expected fallback path name").value
                self.consume(TokenType.COLON, "Expected ':' after path name")
                expr = self.parse_expression()
                fallback_paths.append(FallbackNode(path_name, expr, 
                                                  explore_tok.line, explore_tok.column))
            
            elif self.check(TokenType.ACCEPT):
                self.advance()
                self.consume(TokenType.WHEN, "Expected 'when' after 'accept'")
                self.consume(TokenType.COLON, "Expected ':' after 'when'")
                accept_condition = self.parse_expression()
            
            elif self.check(TokenType.REJECT):
                self.advance()
                self.consume(TokenType.WHEN, "Expected 'when' after 'reject'")
                self.consume(TokenType.COLON, "Expected ':' after 'when'")
                reject_condition = self.parse_expression()
            
            else:
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close exploration")
        
        return ExploreNode(name, try_paths, fallback_paths,
                         accept_condition, reject_condition,
                         explore_tok.line, explore_tok.column)
    
    def parse_symbolic(self) -> SymbolicNode:
        """Parse symbolic mathematics block."""
        sym_tok = self.advance()  # consume 'symbolic'
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after 'symbolic'")
        self.skip_newlines()
        
        declarations = []
        operations = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.LET):
                self.advance()
                # Parse function or variable declaration
                name = self.consume(TokenType.IDENTIFIER, "Expected identifier").value
                
                if self.check(TokenType.LEFT_PAREN):
                    # Function declaration
                    self.advance()
                    params = []
                    if not self.check(TokenType.RIGHT_PAREN):
                        params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter").value)
                        while self.check(TokenType.COMMA):
                            self.advance()
                            params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter").value)
                    self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
                    self.consume(TokenType.EQUAL, "Expected '=' in function definition")
                    expr = self.parse_expression()
                    declarations.append(expr)  # Store as function declaration
                else:
                    # Variable declaration
                    self.consume(TokenType.EQUAL, "Expected '=' in variable declaration")
                    expr = self.parse_expression()
                    declarations.append(expr)
            
            elif self.check(TokenType.SOLVE):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'solve'")
                operations.append(self.parse_expression())
            
            elif self.check(TokenType.PROVE):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'prove'")
                operations.append(self.parse_expression())
            
            else:
                # Regular expression
                operations.append(self.parse_expression())
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close symbolic block")
        
        return SymbolicNode(declarations, operations, sym_tok.line, sym_tok.column)
    
    def parse_propagate(self) -> PropagateNode:
        """Parse uncertainty propagation."""
        prop_tok = self.advance()  # consume 'propagate'
        self.consume(TokenType.UNCERTAINTY, "Expected 'uncertainty' after 'propagate'")
        self.consume(TokenType.THROUGH, "Expected 'through' after 'uncertainty'")
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' for propagation body")
        self.skip_newlines()
        
        body = []
        uncertainty_vars = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
                # Extract uncertainty variables (simplified)
                if hasattr(stmt, 'variable'):
                    uncertainty_vars.append(stmt.variable)
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close propagation")
        
        return PropagateNode(uncertainty_vars, body, prop_tok.line, prop_tok.column)
    
    def parse_constraint(self) -> ConstraintNode:
        """Parse variable constraint."""
        const_tok = self.advance()  # consume 'constrain'
        variable = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':' after variable")
        
        var_type = self.consume(TokenType.IDENTIFIER, "Expected type").value
        
        constraints = []
        if self.check(TokenType.WHERE):
            self.advance()
            constraints.append(self.parse_expression())
        
        return ConstraintNode(variable, var_type, constraints,
                            const_tok.line, const_tok.column)
    
    def parse_tensor_declaration(self) -> TensorNode:
        """Parse tensor declaration."""
        tensor_tok = self.advance()  # consume 'tensor'
        name = self.consume(TokenType.IDENTIFIER, "Expected tensor name").value
        
        dimensions = []
        if self.check(TokenType.LEFT_BRACKET):
            self.advance()
            dimensions.append(int(self.consume(TokenType.NUMBER, "Expected dimension").value))
            while self.check(TokenType.COMMA):
                self.advance()
                dimensions.append(int(self.consume(TokenType.NUMBER, "Expected dimension").value))
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after dimensions")
        
        initializer = None
        if self.check(TokenType.EQUAL):
            self.advance()
            initializer = self.parse_expression()
        
        return TensorNode(name, dimensions, initializer,
                        tensor_tok.line, tensor_tok.column)
    
    def parse_channel(self) -> ChannelNode:
        """Parse message passing channel."""
        channel_tok = self.advance()  # consume 'channel'
        
        data_type = "Any"
        if self.check(TokenType.LESS_THAN):
            self.advance()
            data_type = self.consume(TokenType.IDENTIFIER, "Expected channel type").value
            self.consume(TokenType.GREATER_THAN, "Expected '>' after channel type")
        
        name = self.consume(TokenType.IDENTIFIER, "Expected channel name").value
        
        return ChannelNode(name, data_type, channel_tok.line, channel_tok.column)
    
    def parse_async(self) -> AsyncNode:
        """Parse async execution block."""
        async_tok = self.advance()  # consume 'async'
        name = self.consume(TokenType.IDENTIFIER, "Expected async block name").value
        
        parallel_count = None
        if self.check(TokenType.PARALLEL):
            self.advance()
            self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'parallel'")
            parallel_count = int(self.consume(TokenType.NUMBER, "Expected parallel count").value)
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after count")
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after async name")
        self.skip_newlines()
        
        body = []
        while not self.check(TokenType.RIGHT_BRACE):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close async block")
        
        return AsyncNode(name, body, parallel_count, async_tok.line, async_tok.column)
    
    def parse_uncertain_declaration(self) -> UncertaintyNode:
        """Parse uncertain value declaration."""
        unc_tok = self.advance()  # consume 'uncertain'
        
        if self.check(TokenType.VALUE):
            self.advance()
        
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.EQUAL, "Expected '=' after variable")
        
        value = float(self.consume(TokenType.NUMBER, "Expected value").value)
        
        uncertainty = 0.0
        distribution = None
        
        if self.check(TokenType.PLUS_MINUS):
            self.advance()
            uncertainty = float(self.consume(TokenType.NUMBER, "Expected uncertainty").value)
        
        elif self.check(TokenType.TILDE):
            self.advance()
            distribution = self.consume(TokenType.IDENTIFIER, "Expected distribution").value
            # Parse distribution parameters
            if self.check(TokenType.LEFT_PAREN):
                self.advance()
                # Parse parameters (simplified)
                while not self.check(TokenType.RIGHT_PAREN):
                    self.advance()
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        
        return UncertaintyNode(value, uncertainty, distribution,
                             unc_tok.line, unc_tok.column)
    
    def parse_evolve_declaration(self) -> ASTNode:
        """Parse evolving variable declaration."""
        evolve_tok = self.advance()  # consume 'evolve'
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':' after variable")
        
        var_type = "Dynamic"
        if self.check(TokenType.IDENTIFIER):
            var_type = self.advance().value
        
        initial = None
        if self.check(TokenType.EQUAL):
            self.advance()
            initial = self.parse_expression()
        
        # Return as special assignment node
        return ConstraintNode(name, var_type, [initial] if initial else [],
                            evolve_tok.line, evolve_tok.column)
    
    def parse_observe_declaration(self) -> ASTNode:
        """Parse quantum observation variable."""
        observe_tok = self.advance()  # consume 'observe'
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        self.consume(TokenType.COLON, "Expected ':' after variable")
        
        var_type = "Quantum"
        if self.check(TokenType.IDENTIFIER):
            var_type = self.advance().value
        
        collapse_condition = None
        if self.check(TokenType.UNTIL):
            self.advance()
            collapse_condition = self.parse_expression()
        
        # Return as special quantum observation node
        return ConstraintNode(name, var_type, 
                            [collapse_condition] if collapse_condition else [],
                            observe_tok.line, observe_tok.column)
    
    def parse_quantum(self) -> ASTNode:
        """Parse quantum constructs."""
        quantum_tok = self.advance()  # consume 'quantum'
        
        if self.check(TokenType.CIRCUIT):
            return self.parse_quantum_circuit()
        elif self.check(TokenType.BACKEND):
            return self.parse_quantum_backend()
        elif self.check(TokenType.ALGORITHM):
            return self.parse_quantum_algorithm()
        else:
            # Quantum block
            return self.parse_block()
    
    def parse_quantum_circuit(self) -> QuantumCircuitNode:
        """Parse quantum circuit definition."""
        from .synapse_ast import QuantumCircuitNode, QuantumGateNode, QuantumMeasureNode
        
        circ_tok = self.advance()  # consume 'circuit'
        name = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value
        
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
            
            # Parse quantum gates
            if self.match(TokenType.H, TokenType.X, TokenType.Y, TokenType.Z,
                         TokenType.CNOT, TokenType.CX, TokenType.RX, 
                         TokenType.RY, TokenType.RZ):
                gate_tok = self.advance()
                self.consume(TokenType.LEFT_PAREN, "Expected '(' after gate")
                
                qubits_list = []
                params = []
                
                if not self.check(TokenType.RIGHT_PAREN):
                    qubits_list.append(self.parse_expression())
                    
                    while self.check(TokenType.COMMA):
                        self.advance()
                        expr = self.parse_expression()
                        # Rotation gates take angle as second parameter
                        if gate_tok.value.lower() in {"rx", "ry", "rz"} and len(qubits_list) == 1:
                            params.append(expr)
                        else:
                            qubits_list.append(expr)
                
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after gate arguments")
                
                gates.append(QuantumGateNode(gate_tok.value, qubits_list, params,
                                            gate_tok.line, gate_tok.column))
            
            # Parse measurements
            elif self.check(TokenType.MEASURE):
                meas_tok = self.advance()
                self.consume(TokenType.LEFT_PAREN, "Expected '(' after measure")
                
                qubits_list = []
                classical_bits = []
                
                if not self.check(TokenType.RIGHT_PAREN):
                    qubits_list.append(self.parse_expression())
                    
                    while self.check(TokenType.COMMA):
                        self.advance()
                        qubits_list.append(self.parse_expression())
                
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after measure arguments")
                
                # Optional classical bit assignment
                if self.check(TokenType.ARROW):
                    self.advance()
                    classical_bits.append(self.parse_expression())
                
                measurements.append(QuantumMeasureNode(qubits_list, classical_bits,
                                                      meas_tok.line, meas_tok.column))
            
            else:
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close circuit")
        
        return QuantumCircuitNode(name, qubits, gates, measurements,
                                circ_tok.line, circ_tok.column)
    
    def parse_quantum_backend(self) -> ASTNode:
        """Parse quantum backend configuration."""
        from .synapse_ast import QuantumBackendNode, NumberNode, StringNode, IdentifierNode
        
        backend_tok = self.advance()  # consume 'backend'
        name = self.consume(TokenType.IDENTIFIER, "Expected backend name").value
        
        config = {}
        if self.check(TokenType.LEFT_BRACE):
            self.advance()
            self.skip_newlines()
            
            while not self.check(TokenType.RIGHT_BRACE):
                self.skip_newlines()
                
                key = self.consume(TokenType.IDENTIFIER, "Expected configuration key").value
                self.consume(TokenType.COLON, "Expected ':' after key")
                
                # Parse configuration value
                if self.check(TokenType.NUMBER):
                    num_tok = self.advance()
                    config[key] = NumberNode(float(num_tok.value), num_tok.line, num_tok.column)
                elif self.check(TokenType.STRING):
                    str_tok = self.advance()
                    config[key] = StringNode(str_tok.value, str_tok.line, str_tok.column)
                elif self.check(TokenType.IDENTIFIER):
                    id_tok = self.advance()
                    config[key] = IdentifierNode(id_tok.value, id_tok.line, id_tok.column)
                else:
                    config[key] = self.parse_expression()
                
                self.skip_newlines()
            
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close backend config")
        
        return QuantumBackendNode(name, config, backend_tok.line, backend_tok.column)
    
    def parse_quantum_algorithm(self) -> ASTNode:
        """Parse quantum algorithm definition."""
        from .synapse_ast import QuantumAlgorithmNode, QuantumAnsatzNode, IdentifierNode
        
        algo_tok = self.advance()  # consume 'algorithm'
        name = self.consume(TokenType.IDENTIFIER, "Expected algorithm name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after algorithm name")
        self.skip_newlines()
        
        parameters = []
        ansatz = None
        cost_function = None
        optimizer = None
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.PARAMETERS):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'parameters'")
                
                if self.check(TokenType.LEFT_BRACKET):
                    self.advance()
                    if not self.check(TokenType.RIGHT_BRACKET):
                        param_tok = self.consume(TokenType.IDENTIFIER, "Expected parameter")
                        parameters.append(IdentifierNode(param_tok.value, 
                                                        param_tok.line, param_tok.column))
                        
                        while self.check(TokenType.COMMA):
                            self.advance()
                            param_tok = self.consume(TokenType.IDENTIFIER, "Expected parameter")
                            parameters.append(IdentifierNode(param_tok.value,
                                                            param_tok.line, param_tok.column))
                    
                    self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after parameters")
            
            elif self.check(TokenType.ANSATZ):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'ansatz'")
                ansatz_name = self.consume(TokenType.IDENTIFIER, "Expected ansatz name").value
                ansatz = QuantumAnsatzNode(ansatz_name, [], algo_tok.line, algo_tok.column)
            
            elif self.check(TokenType.COST):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'cost'")
                cost_function = self.parse_expression()
            
            elif self.check(TokenType.OPTIMIZER):
                self.advance()
                self.consume(TokenType.COLON, "Expected ':' after 'optimizer'")
                optimizer = self.consume(TokenType.IDENTIFIER, "Expected optimizer name").value
            
            else:
                self.advance()
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close algorithm")
        
        return QuantumAlgorithmNode(name, parameters, ansatz, cost_function, optimizer,
                                   algo_tok.line, algo_tok.column)
    
    def parse_run(self) -> ASTNode:
        """Parse run statement for circuit execution."""
        from .synapse_ast import RunNode, NumberNode, StringNode, IdentifierNode
        
        run_tok = self.advance()  # consume 'run'
        circuit = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value
        
        backend = None
        options = {}
        
        if self.check(TokenType.WITH):
            self.advance()
            if self.check(TokenType.BACKEND):
                self.advance()
            backend = self.consume(TokenType.IDENTIFIER, "Expected backend name").value
        
        if self.check(TokenType.LEFT_BRACE):
            self.advance()
            self.skip_newlines()
            
            while not self.check(TokenType.RIGHT_BRACE):
                self.skip_newlines()
                
                key = self.consume(TokenType.IDENTIFIER, "Expected option key").value
                self.consume(TokenType.COLON, "Expected ':' after key")
                
                # Parse option value
                if self.check(TokenType.NUMBER):
                    num_tok = self.advance()
                    options[key] = NumberNode(float(num_tok.value), num_tok.line, num_tok.column)
                elif self.check(TokenType.STRING):
                    str_tok = self.advance()
                    options[key] = StringNode(str_tok.value, str_tok.line, str_tok.column)
                elif self.check(TokenType.IDENTIFIER):
                    id_tok = self.advance()
                    options[key] = IdentifierNode(id_tok.value, id_tok.line, id_tok.column)
                else:
                    options[key] = self.parse_expression()
                
                self.skip_newlines()
            
            self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close run options")
        
        return RunNode(circuit, backend, options, run_tok.line, run_tok.column)
    
    def parse_block(self) -> ASTNode:
        """Parse generic block statement."""
        from .synapse_ast import BlockNode
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{'")
        self.skip_newlines()
        
        statements = []
        while not self.check(TokenType.RIGHT_BRACE):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        
        return BlockNode(statements, self.peek().line, self.peek().column)
    
    def parse_expression_statement(self) -> ASTNode:
        """Parse expression or assignment statement."""
        expr = self.parse_expression()
        
        # Check for assignment
        if self.check(TokenType.EQUAL):
            self.advance()
            value = self.parse_expression()
            # Create assignment node
            from .synapse_ast import AssignmentNode
            if hasattr(expr, 'name'):
                return AssignmentNode(expr.name, value, expr.line, expr.column)
        
        return expr
    
    def parse_expression(self) -> ASTNode:
        """Parse expression with all operators."""
        return self.parse_ternary()
    
    def parse_ternary(self) -> ASTNode:
        """Parse ternary conditional expression."""
        expr = self.parse_logical_or()
        
        if self.check(TokenType.QUESTION):
            self.advance()
            true_expr = self.parse_expression()
            self.consume(TokenType.COLON, "Expected ':' in ternary expression")
            false_expr = self.parse_expression()
            
            # Create conditional expression node
            from .synapse_ast import BinaryOpNode
            return BinaryOpNode("?:", expr, [true_expr, false_expr],
                              expr.line, expr.column)
        
        return expr
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR expression."""
        left = self.parse_logical_and()
        
        while self.check(TokenType.OR):
            op_tok = self.advance()
            right = self.parse_logical_and()
            from .synapse_ast import BinaryOpNode
            left = BinaryOpNode("||", left, right, op_tok.line, op_tok.column)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND expression."""
        left = self.parse_equality()
        
        while self.check(TokenType.AND):
            op_tok = self.advance()
            right = self.parse_equality()
            from .synapse_ast import BinaryOpNode
            left = BinaryOpNode("&&", left, right, op_tok.line, op_tok.column)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """Parse equality expression."""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL):
            op_tok = self.advance()
            right = self.parse_comparison()
            from .synapse_ast import BinaryOpNode
            left = BinaryOpNode(op_tok.value, left, right, op_tok.line, op_tok.column)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison expression."""
        left = self.parse_additive()
        
        while self.match(TokenType.LESS_THAN, TokenType.LESS_EQUAL,
                         TokenType.GREATER_THAN, TokenType.GREATER_EQUAL):
            op_tok = self.advance()
            right = self.parse_additive()
            from .synapse_ast import BinaryOpNode
            left = BinaryOpNode(op_tok.value, left, right, op_tok.line, op_tok.column)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        """Parse addition/subtraction expression."""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.advance()
            right = self.parse_multiplicative()
            from .synapse_ast import BinaryOpNode
            left = BinaryOpNode(op_tok.value, left, right, op_tok.line, op_tok.column)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplication/division expression."""
        left = self.parse_exponential()
        
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self.advance()
            right = self.parse_exponential()
            from .synapse_ast import BinaryOpNode
            left = BinaryOpNode(op_tok.value, left, right, op_tok.line, op_tok.column)
        
        return left
    
    def parse_exponential(self) -> ASTNode:
        """Parse exponential expression."""
        left = self.parse_unary()
        
        if self.check(TokenType.POWER):
            op_tok = self.advance()
            right = self.parse_exponential()  # Right-associative
            from .synapse_ast import BinaryOpNode
            return BinaryOpNode("**", left, right, op_tok.line, op_tok.column)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary expression."""
        if self.match(TokenType.NOT, TokenType.MINUS):
            op_tok = self.advance()
            expr = self.parse_unary()
            from .synapse_ast import UnaryOpNode
            return UnaryOpNode(op_tok.value, expr, op_tok.line, op_tok.column)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """Parse postfix expression (function calls, indexing)."""
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
                
                self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
                
                from .synapse_ast import FunctionCallNode
                expr = FunctionCallNode(expr, args, expr.line, expr.column)
            
            elif self.check(TokenType.LEFT_BRACKET):
                # Array/tensor indexing
                self.advance()
                index = self.parse_expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after index")
                
                from .synapse_ast import BinaryOpNode
                expr = BinaryOpNode("[]", expr, index, expr.line, expr.column)
            
            elif self.check(TokenType.DOT):
                # Member access
                self.advance()
                member = self.consume(TokenType.IDENTIFIER, "Expected member name").value
                
                from .synapse_ast import BinaryOpNode, IdentifierNode
                member_node = IdentifierNode(member, self.peek().line, self.peek().column)
                expr = BinaryOpNode(".", expr, member_node, expr.line, expr.column)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expression."""
        from .synapse_ast import (NumberNode, StringNode, IdentifierNode,
                                 ListNode, MatrixNode)
        
        # Numbers
        if self.check(TokenType.NUMBER):
            num_tok = self.advance()
            
            # Check for uncertainty
            if self.check(TokenType.PLUS_MINUS):
                self.advance()
                unc_tok = self.consume(TokenType.NUMBER, "Expected uncertainty value")
                return UncertaintyNode(float(num_tok.value), float(unc_tok.value),
                                     None, num_tok.line, num_tok.column)
            
            return NumberNode(float(num_tok.value), num_tok.line, num_tok.column)
        
        # Strings
        if self.check(TokenType.STRING):
            str_tok = self.advance()
            return StringNode(str_tok.value, str_tok.line, str_tok.column)
        
        # Identifiers
        if self.check(TokenType.IDENTIFIER):
            id_tok = self.advance()
            return IdentifierNode(id_tok.value, id_tok.line, id_tok.column)
        
        # Parenthesized expression
        if self.check(TokenType.LEFT_PAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return expr
        
        # List literal
        if self.check(TokenType.LEFT_BRACKET):
            bracket_tok = self.advance()
            elements = []
            
            if not self.check(TokenType.RIGHT_BRACKET):
                elements.append(self.parse_expression())
                while self.check(TokenType.COMMA):
                    self.advance()
                    elements.append(self.parse_expression())
            
            self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after list elements")
            return ListNode(elements, bracket_tok.line, bracket_tok.column)
        
        # Matrix literal
        if self.check(TokenType.LEFT_BRACE):
            brace_tok = self.advance()
            
            # Check if this is a matrix by looking for nested brackets
            if self.check(TokenType.LEFT_BRACKET):
                rows = []
                
                while self.check(TokenType.LEFT_BRACKET):
                    self.advance()
                    row = []
                    
                    if not self.check(TokenType.RIGHT_BRACKET):
                        row.append(self.parse_expression())
                        while self.check(TokenType.COMMA):
                            self.advance()
                            row.append(self.parse_expression())
                    
                    self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after row")
                    rows.append(row)
                    
                    if self.check(TokenType.COMMA):
                        self.advance()
                    else:
                        break
                
                self.consume(TokenType.RIGHT_BRACE, "Expected '}' after matrix")
                return MatrixNode(rows, brace_tok.line, brace_tok.column)
            
            # Otherwise parse as block
            self.current -= 1  # Put back the brace
            return self.parse_block()
        
        # Error: unexpected token
        raise ParseError(f"Unexpected token: {self.peek().value}", self.peek())


# Missing AST nodes that need to be added
@dataclass
class ProgramNode(ASTNode):
    """Root program node."""
    statements: List[ASTNode]
    
    def __init__(self, statements: List[ASTNode]):
        super().__init__(NodeType.PROGRAM, 0, 0)
        self.statements = statements


@dataclass
class BlockNode(ASTNode):
    """Block of statements."""
    statements: List[ASTNode]
    
    def __init__(self, statements: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.BLOCK, line, column)
        self.statements = statements


@dataclass
class AssignmentNode(ASTNode):
    """Variable assignment."""
    variable: str
    value: ASTNode
    
    def __init__(self, variable: str, value: ASTNode, line: int, column: int):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.variable = variable
        self.value = value


@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation."""
    operator: str
    left: ASTNode
    right: Union[ASTNode, List[ASTNode]]  # Right can be list for ternary
    
    def __init__(self, operator: str, left: ASTNode, right: Union[ASTNode, List[ASTNode]],
                 line: int, column: int):
        super().__init__(NodeType.BINARY_OP, line, column)
        self.operator = operator
        self.left = left
        self.right = right


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation."""
    operator: str
    operand: ASTNode
    
    def __init__(self, operator: str, operand: ASTNode, line: int, column: int):
        super().__init__(NodeType.UNARY_OP, line, column)
        self.operator = operator
        self.operand = operand


@dataclass
class FunctionCallNode(ASTNode):
    """Function call."""
    function: ASTNode
    arguments: List[ASTNode]
    
    def __init__(self, function: ASTNode, arguments: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.FUNCTION_CALL, line, column)
        self.function = function
        self.arguments = arguments


@dataclass
class RunNode(ASTNode):
    """Run statement for circuit execution."""
    circuit: str
    backend: Optional[str]
    options: Dict[str, ASTNode]
    
    def __init__(self, circuit: str, backend: Optional[str],
                 options: Dict[str, ASTNode], line: int, column: int):
        super().__init__(NodeType.RUN, line, column)
        self.circuit = circuit
        self.backend = backend
        self.options = options


@dataclass
class QuantumAlgorithmNode(ASTNode):
    """Quantum algorithm definition."""
    name: str
    parameters: List[ASTNode]
    ansatz: Optional['QuantumAnsatzNode']
    cost_function: Optional[ASTNode]
    optimizer: Optional[str]
    
    def __init__(self, name: str, parameters: List[ASTNode],
                 ansatz: Optional['QuantumAnsatzNode'],
                 cost_function: Optional[ASTNode],
                 optimizer: Optional[str],
                 line: int, column: int):
        super().__init__(NodeType.QUANTUM_ALGORITHM, line, column)
        self.name = name
        self.parameters = parameters
        self.ansatz = ansatz
        self.cost_function = cost_function
        self.optimizer = optimizer


@dataclass
class QuantumBackendNode(ASTNode):
    """Quantum backend configuration."""
    name: str
    config: Dict[str, ASTNode]
    
    def __init__(self, name: str, config: Dict[str, ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.QUANTUM_BACKEND, line, column)
        self.name = name
        self.config = config


@dataclass
class QuantumAnsatzNode(ASTNode):
    """Quantum ansatz definition."""
    name: str
    parameters: List[ASTNode]
    
    def __init__(self, name: str, parameters: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.QUANTUM_ANSATZ, line, column)
        self.name = name
        self.parameters = parameters