"""
Complete Abstract Syntax Tree (AST) nodes for Synapse language
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Union
from enum import Enum

class ASTNode:
    """Base class for all AST nodes"""
    pass

class ExpressionNode(ASTNode):
    """Base class for expression nodes"""
    pass

class StatementNode(ASTNode):
    """Base class for statement nodes"""
    pass

class TypeNode(ASTNode):
    """Base class for type nodes"""
    pass

@dataclass
class ProgramNode(ASTNode):
    """Root node of the AST"""
    statements: List[ASTNode]

@dataclass
class HypothesisNode(StatementNode):
    """Hypothesis construct"""
    name: str
    assume: Optional[ExpressionNode]
    predict: Optional[ExpressionNode]
    validate: Optional[ExpressionNode]

@dataclass
class ExperimentNode(StatementNode):
    """Experiment construct"""
    name: str
    setup: Optional[ExpressionNode]
    parallel_block: Optional['ParallelNode']
    synthesize: Optional[ExpressionNode]

@dataclass
class ParallelNode(StatementNode):
    """Parallel execution block"""
    branches: List['BranchNode']
    factor: Optional[Union[int, str]]  # Can be number or "auto"

@dataclass
class BranchNode(ASTNode):
    """Branch within parallel block"""
    name: str
    body: ASTNode

@dataclass
class StreamNode(StatementNode):
    """Stream declaration"""
    name: str
    body: ExpressionNode

@dataclass
class PipelineNode(StatementNode):
    """Pipeline construct"""
    name: str
    stages: List['StageNode']

@dataclass
class StageNode(ASTNode):
    """Pipeline stage"""
    name: str
    operations: List[ASTNode]
    parallel_factor: Optional[Union[int, str]]

@dataclass
class StageOperationNode(ASTNode):
    """Operation within a stage"""
    name: str
    value: ExpressionNode

@dataclass
class ForkNode(ASTNode):
    """Fork construct for parallel paths"""
    paths: List['PathNode']

@dataclass
class PathNode(ASTNode):
    """Path within fork"""
    name: str
    body: ASTNode

@dataclass
class ReasonChainNode(StatementNode):
    """Reasoning chain"""
    name: str
    premises: List['PremiseNode']
    derivations: List['DerivationNode']
    conclusion: Optional[ExpressionNode]

@dataclass
class PremiseNode(ASTNode):
    """Premise in reasoning chain"""
    id: str
    text: ExpressionNode

@dataclass
class DerivationNode(ASTNode):
    """Derivation in reasoning chain"""
    id: str
    source_ids: List[str]
    text: ExpressionNode

@dataclass
class ExploreNode(StatementNode):
    """Explore construct with backtracking"""
    space_name: str
    tries: List['TryPathNode']
    fallbacks: List['FallbackPathNode']
    accept_condition: Optional[ExpressionNode]
    reject_condition: Optional[ExpressionNode]

@dataclass
class TryPathNode(ASTNode):
    """Try path in explore"""
    name: str
    body: ExpressionNode

@dataclass
class FallbackPathNode(ASTNode):
    """Fallback path in explore"""
    name: str
    body: ExpressionNode

@dataclass
class SymbolicNode(StatementNode):
    """Symbolic mathematics block"""
    bindings: List['LetBindingNode']
    operations: List[ASTNode]

@dataclass
class LetBindingNode(ASTNode):
    """Let binding for symbolic math"""
    name: str
    params: List[str]
    expression: ExpressionNode

@dataclass
class SolveNode(ASTNode):
    """Solve operation"""
    equation: ExpressionNode
    variable: Optional[str]

@dataclass
class ProveNode(ASTNode):
    """Prove operation"""
    statement: ExpressionNode
    domain: Optional[ExpressionNode]

@dataclass
class UncertainDeclarationNode(StatementNode):
    """Uncertain value declaration"""
    name: str
    value: ExpressionNode
    uncertainty: Optional[ExpressionNode]
    value_type: Optional[str]

@dataclass
class ConstrainNode(StatementNode):
    """Constrain declaration"""
    variable: str
    var_type: str
    constraint: Optional[ExpressionNode]

@dataclass
class EvolveNode(StatementNode):
    """Evolve declaration"""
    variable: str
    var_type: str
    initial: Optional[ExpressionNode]

@dataclass
class ObserveNode(StatementNode):
    """Observe declaration"""
    variable: str
    var_type: str
    condition: Optional[ExpressionNode]

@dataclass
class TensorDeclarationNode(StatementNode):
    """Tensor declaration"""
    name: str
    dimensions: List[ExpressionNode]
    initializer: Optional[ExpressionNode]

@dataclass
class PropagateNode(StatementNode):
    """Propagate uncertainty block"""
    operations: List[ASTNode]

@dataclass
class StructureNode(StatementNode):
    """Structure definition"""
    name: str
    fields: List['FieldNode']
    invariants: List[ExpressionNode]

@dataclass
class FieldNode(ASTNode):
    """Field in structure"""
    name: str
    field_type: TypeNode

@dataclass
class TheoryNode(StatementNode):
    """Theory definition"""
    name: str
    components: List['ComponentNode']
    invariants: List[ExpressionNode]

@dataclass
class ComponentNode(ASTNode):
    """Component in theory"""
    name: str
    comp_type: TypeNode

@dataclass
class AssignmentNode(StatementNode):
    """Variable assignment"""
    name: str
    value: ExpressionNode

@dataclass
class ChannelSendNode(StatementNode):
    """Channel send operation"""
    channel: str
    value: ExpressionNode

@dataclass
class BlockNode(ExpressionNode):
    """Block of statements"""
    statements: List[ASTNode]

@dataclass
class BinaryOpNode(ExpressionNode):
    """Binary operation"""
    left: ExpressionNode
    operator: Any  # TokenType
    right: ExpressionNode

@dataclass
class UnaryOpNode(ExpressionNode):
    """Unary operation"""
    operator: Any  # TokenType
    operand: ExpressionNode

@dataclass
class ImplicationNode(ExpressionNode):
    """Logical implication (=>)"""
    antecedent: ExpressionNode
    consequent: ExpressionNode

@dataclass
class FunctionCallNode(ExpressionNode):
    """Function call"""
    function: ExpressionNode
    arguments: List[ExpressionNode]

@dataclass
class IndexAccessNode(ExpressionNode):
    """Array/tensor index access"""
    object: ExpressionNode
    indices: List[ExpressionNode]

@dataclass
class NumberNode(ExpressionNode):
    """Number literal"""
    value: float

@dataclass
class StringNode(ExpressionNode):
    """String literal"""
    value: str

@dataclass
class IdentifierNode(ExpressionNode):
    """Identifier/variable reference"""
    name: str

@dataclass
class SimpleTypeNode(TypeNode):
    """Simple type"""
    name: str

@dataclass
class ParameterizedTypeNode(TypeNode):
    """Parameterized type (e.g., Graph<Atom>)"""
    name: str
    parameters: List[TypeNode]

@dataclass
class TensorTypeNode(TypeNode):
    """Tensor type with dimensions"""
    base_type: str
    dimensions: List[ExpressionNode]

class ASTVisitor:
    """Visitor pattern for traversing AST"""
    
    def visit(self, node: ASTNode) -> Any:
        """Visit a node and dispatch to appropriate method"""
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode) -> Any:
        """Default visitor for unhandled nodes"""
        raise NotImplementedError(f"No visitor method for {node.__class__.__name__}")

class ASTTransformer(ASTVisitor):
    """Transformer for modifying AST"""
    
    def generic_visit(self, node: ASTNode) -> ASTNode:
        """Default transformer - returns node unchanged"""
        return node

def print_ast(node: ASTNode, indent: int = 0) -> None:
    """Pretty print AST structure"""
    prefix = "  " * indent
    
    if isinstance(node, ProgramNode):
        print(f"{prefix}Program:")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    
    elif isinstance(node, HypothesisNode):
        print(f"{prefix}Hypothesis '{node.name}':")
        if node.assume:
            print(f"{prefix}  Assume:")
            print_ast(node.assume, indent + 2)
        if node.predict:
            print(f"{prefix}  Predict:")
            print_ast(node.predict, indent + 2)
        if node.validate:
            print(f"{prefix}  Validate:")
            print_ast(node.validate, indent + 2)
    
    elif isinstance(node, ExperimentNode):
        print(f"{prefix}Experiment '{node.name}':")
        if node.setup:
            print(f"{prefix}  Setup:")
            print_ast(node.setup, indent + 2)
        if node.parallel_block:
            print_ast(node.parallel_block, indent + 1)
        if node.synthesize:
            print(f"{prefix}  Synthesize:")
            print_ast(node.synthesize, indent + 2)
    
    elif isinstance(node, ParallelNode):
        factor_str = f" (factor={node.factor})" if node.factor else ""
        print(f"{prefix}Parallel{factor_str}:")
        for branch in node.branches:
            print_ast(branch, indent + 1)
    
    elif isinstance(node, BranchNode):
        print(f"{prefix}Branch '{node.name}':")
        print_ast(node.body, indent + 1)
    
    elif isinstance(node, PipelineNode):
        print(f"{prefix}Pipeline '{node.name}':")
        for stage in node.stages:
            print_ast(stage, indent + 1)
    
    elif isinstance(node, StageNode):
        factor_str = f" (parallel={node.parallel_factor})" if node.parallel_factor else ""
        print(f"{prefix}Stage '{node.name}'{factor_str}:")
        for op in node.operations:
            print_ast(op, indent + 1)
    
    elif isinstance(node, ReasonChainNode):
        print(f"{prefix}ReasonChain '{node.name}':")
        for premise in node.premises:
            print(f"{prefix}  Premise {premise.id}:")
            print_ast(premise.text, indent + 2)
        for deriv in node.derivations:
            print(f"{prefix}  Derive {deriv.id} from {', '.join(deriv.source_ids)}:")
            print_ast(deriv.text, indent + 2)
        if node.conclusion:
            print(f"{prefix}  Conclude:")
            print_ast(node.conclusion, indent + 2)
    
    elif isinstance(node, UncertainDeclarationNode):
        print(f"{prefix}Uncertain '{node.name}':")
        print(f"{prefix}  Value:")
        print_ast(node.value, indent + 2)
        if node.uncertainty:
            print(f"{prefix}  Uncertainty:")
            print_ast(node.uncertainty, indent + 2)
    
    elif isinstance(node, BinaryOpNode):
        print(f"{prefix}BinaryOp ({node.operator}):")
        print(f"{prefix}  Left:")
        print_ast(node.left, indent + 2)
        print(f"{prefix}  Right:")
        print_ast(node.right, indent + 2)
    
    elif isinstance(node, NumberNode):
        print(f"{prefix}Number: {node.value}")
    
    elif isinstance(node, StringNode):
        print(f"{prefix}String: '{node.value}'")
    
    elif isinstance(node, IdentifierNode):
        print(f"{prefix}Identifier: {node.name}")
    
    else:
        print(f"{prefix}{node.__class__.__name__}")