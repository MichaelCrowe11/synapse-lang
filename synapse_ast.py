"""Deprecated root AST wrapper. Use synapse_lang.synapse_ast instead."""
from synapse_lang.synapse_ast import *  # type: ignore


class NodeType(Enum):
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    IDENTIFIER = "IDENTIFIER"
    UNCERTAIN = "UNCERTAIN"

    # Expressions
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    ASSIGNMENT = "ASSIGNMENT"
    FUNCTION_CALL = "FUNCTION_CALL"
    TENSOR_ACCESS = "TENSOR_ACCESS"
    LIST = "LIST"
    MATRIX = "MATRIX"
    TENSOR = "TENSOR"

    # Statements
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT = "EXPERIMENT"
    PARALLEL = "PARALLEL"
    BRANCH = "BRANCH"
    STREAM = "STREAM"
    REASON_CHAIN = "REASON_CHAIN"
    PREMISE = "PREMISE"
    DERIVE = "DERIVE"
    CONCLUDE = "CONCLUDE"
    PIPELINE = "PIPELINE"
    STAGE = "STAGE"
    FORK = "FORK"
    PATH = "PATH"
    EXPLORE = "EXPLORE"
    TRY = "TRY"
    FALLBACK = "FALLBACK"
    SYMBOLIC = "SYMBOLIC"
    LET = "LET"
    SOLVE = "SOLVE"
    PROVE = "PROVE"
    PROPAGATE = "PROPAGATE"
    CONSTRAIN = "CONSTRAIN"
    EVOLVE = "EVOLVE"
    OBSERVE = "OBSERVE"
    SYNTHESIZE = "SYNTHESIZE"

    # Quantum computing nodes
    QUANTUM_CIRCUIT = "QUANTUM_CIRCUIT"
    QUANTUM_GATE = "QUANTUM_GATE"
    QUANTUM_MEASURE = "QUANTUM_MEASURE"
    QUANTUM_BACKEND = "QUANTUM_BACKEND"
    QUANTUM_ALGORITHM = "QUANTUM_ALGORITHM"
    QUANTUM_ANSATZ = "QUANTUM_ANSATZ"

    # Control flow
    IF = "IF"
    WHILE = "WHILE"
    FOR = "FOR"
    RETURN = "RETURN"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"

    # Compound
    BLOCK = "BLOCK"
    PROGRAM = "PROGRAM"

@dataclass
class ASTNode:
    """Base class for all AST nodes"""
    node_type: NodeType
    line: int
    column: int

@dataclass
class NumberNode(ASTNode):
    """Numeric literal"""
    value: float

    def __init__(self, value: float, line: int, column: int):
        super().__init__(NodeType.NUMBER, line, column)
        self.value = value

@dataclass
class StringNode(ASTNode):
    """String literal"""
    value: str

    def __init__(self, value: str, line: int, column: int):
        super().__init__(NodeType.STRING, line, column)
        self.value = value

@dataclass
class IdentifierNode(ASTNode):
    """Variable or function identifier"""
    name: str

    def __init__(self, name: str, line: int, column: int):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name

@dataclass
class UncertainNode(ASTNode):
    """Uncertain value with error bounds"""
    value: float
    uncertainty: float

    def __init__(self, value: float, uncertainty: float, line: int, column: int):
        super().__init__(NodeType.UNCERTAIN, line, column)
        self.value = value
        self.uncertainty = uncertainty

@dataclass
class ListNode(ASTNode):
    """List literal (1-D tensor)"""
    elements: List[ASTNode]
    def __init__(self, elements: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.LIST, line, column)
        self.elements = elements

@dataclass
class MatrixNode(ASTNode):
    """Matrix literal (2-D tensor)"""
    rows: List[List[ASTNode]]
    def __init__(self, rows: List[List[ASTNode]], line: int, column: int):
        super().__init__(NodeType.MATRIX, line, column)
        self.rows = rows

@dataclass
class TensorNode(ASTNode):
    """N-D Tensor literal"""
    dimensions: List[int]
    values: List[ASTNode]
    def __init__(self, dimensions: List[int], values: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.TENSOR, line, column)
        self.dimensions = dimensions
        self.values = values

@dataclass
class QuantumCircuitNode(ASTNode):
    """Quantum circuit definition"""
    name: str
    qubits: int
    gates: List["QuantumGateNode"]
    measurements: List["QuantumMeasureNode"]

    def __init__(self, name: str, qubits: int, gates: List["QuantumGateNode"],
                 measurements: List["QuantumMeasureNode"], line: int, column: int):
        super().__init__(NodeType.QUANTUM_CIRCUIT, line, column)
        self.name = name
        self.qubits = qubits
        self.gates = gates
        self.measurements = measurements

@dataclass
class QuantumGateNode(ASTNode):
    """Quantum gate operation"""
    gate_type: str
    qubits: List[ASTNode]
    parameters: List[ASTNode]

    def __init__(self, gate_type: str, qubits: List[ASTNode], parameters: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.QUANTUM_GATE, line, column)
        self.gate_type = gate_type
        self.qubits = qubits
        self.parameters = parameters

@dataclass
class QuantumMeasureNode(ASTNode):
    """Quantum measurement operation"""
    qubits: List[ASTNode]
    classical_bits: List[ASTNode]

    def __init__(self, qubits: List[ASTNode], classical_bits: List[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.QUANTUM_MEASURE, line, column)
        self.qubits = qubits
        self.classical_bits = classical_bits

@dataclass
class QuantumBackendNode(ASTNode):
    """Quantum backend configuration"""
    name: str
    config: Dict[str, ASTNode]

    def __init__(self, name: str, config: Dict[str, ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_BACKEND, line, column)
        self.name = name
        self.config = config

@dataclass
class QuantumAlgorithmNode(ASTNode):
    """Quantum algorithm definition"""
    name: str
    parameters: List[ASTNode]
    ansatz: "QuantumAnsatzNode"
    cost_function: ASTNode
    optimizer: ASTNode

    def __init__(self, name: str, parameters: List[ASTNode], ansatz: "QuantumAnsatzNode",
                 cost_function: ASTNode, optimizer: ASTNode, line: int, column: int):
        super().__init__(NodeType.QUANTUM_ALGORITHM, line, column)
        self.name = name
        self.parameters = parameters
        self.ansatz = ansatz
        self.cost_function = cost_function
        self.optimizer = optimizer

@dataclass
class QuantumAnsatzNode(ASTNode):
    """Quantum ansatz (parameterized circuit)"""
    name: str
    layers: List[ASTNode]

    def __init__(self, name: str, layers: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_ANSATZ, line, column)
        self.name = name
        self.layers = layers

@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation"""
    operator: str
    left: ASTNode
    right: ASTNode

    def __init__(self, operator: str, left: ASTNode, right: ASTNode, line: int, column: int):
        super().__init__(NodeType.BINARY_OP, line, column)
        self.operator = operator
        self.left = left
        self.right = right

@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation"""
    operator: str
    operand: ASTNode

    def __init__(self, operator: str, operand: ASTNode, line: int, column: int):
        super().__init__(NodeType.UNARY_OP, line, column)
        self.operator = operator
        self.operand = operand

@dataclass
class AssignmentNode(ASTNode):
    """Variable assignment"""
    target: IdentifierNode
    value: ASTNode
    is_uncertain: bool = False
    is_constrained: bool = False
    is_evolving: bool = False

    def __init__(self, target: IdentifierNode, value: ASTNode, line: int, column: int,
                 is_uncertain: bool = False, is_constrained: bool = False, is_evolving: bool = False):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.target = target
        self.value = value
        self.is_uncertain = is_uncertain
        self.is_constrained = is_constrained
        self.is_evolving = is_evolving

@dataclass
class FunctionCallNode(ASTNode):
    """Function invocation"""
    function: IdentifierNode
    arguments: List[ASTNode]

    def __init__(self, function: IdentifierNode, arguments: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.FUNCTION_CALL, line, column)
        self.function = function
        self.arguments = arguments

@dataclass
class ParallelNode(ASTNode):
    """Parallel execution block"""
    branches: List["BranchNode"]
    num_workers: Optional[int] = None

    def __init__(self, branches: List["BranchNode"], line: int, column: int, num_workers: Optional[int] = None):
        super().__init__(NodeType.PARALLEL, line, column)
        self.branches = branches
        self.num_workers = num_workers

@dataclass
class BranchNode(ASTNode):
    """Branch in parallel execution"""
    name: str
    body: ASTNode

    def __init__(self, name: str, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.BRANCH, line, column)
        self.name = name
        self.body = body

@dataclass
class StreamNode(ASTNode):
    """Thought stream"""
    name: str
    body: "BlockNode"

    def __init__(self, name: str, body: "BlockNode", line: int, column: int):
        super().__init__(NodeType.STREAM, line, column)
        self.name = name
        self.body = body

@dataclass
class HypothesisNode(ASTNode):
    """Hypothesis definition"""
    name: str
    assumptions: List[ASTNode]
    predictions: List[ASTNode]
    validations: List[ASTNode]

    def __init__(self, name: str, assumptions: List[ASTNode], predictions: List[ASTNode],
                 validations: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.HYPOTHESIS, line, column)
        self.name = name
        self.assumptions = assumptions
        self.predictions = predictions
        self.validations = validations

@dataclass
class ExperimentNode(ASTNode):
    """Experiment definition"""
    name: str
    setup: Optional[ASTNode]
    procedure: ASTNode
    analysis: Optional[ASTNode]

    def __init__(self, name: str, procedure: ASTNode, line: int, column: int,
                 setup: Optional[ASTNode] = None, analysis: Optional[ASTNode] = None):
        super().__init__(NodeType.EXPERIMENT, line, column)
        self.name = name
        self.setup = setup
        self.procedure = procedure
        self.analysis = analysis

@dataclass
class ReasonChainNode(ASTNode):
    """Logical reasoning chain"""
    name: str
    premises: List["PremiseNode"]
    derivations: List["DeriveNode"]
    conclusion: "ConcludeNode"

    def __init__(self, name: str, premises: List["PremiseNode"], derivations: List["DeriveNode"],
                 conclusion: "ConcludeNode", line: int, column: int):
        super().__init__(NodeType.REASON_CHAIN, line, column)
        self.name = name
        self.premises = premises
        self.derivations = derivations
        self.conclusion = conclusion

@dataclass
class PremiseNode(ASTNode):
    """Logical premise"""
    name: str
    statement: ASTNode

    def __init__(self, name: str, statement: ASTNode, line: int, column: int):
        super().__init__(NodeType.PREMISE, line, column)
        self.name = name
        self.statement = statement

@dataclass
class DeriveNode(ASTNode):
    """Logical derivation"""
    name: str
    from_premise: str
    statement: ASTNode

    def __init__(self, name: str, from_premise: str, statement: ASTNode, line: int, column: int):
        super().__init__(NodeType.DERIVE, line, column)
        self.name = name
        self.from_premise = from_premise
        self.statement = statement

@dataclass
class ConcludeNode(ASTNode):
    """Logical conclusion"""
    condition: ASTNode
    result: ASTNode

    def __init__(self, condition: ASTNode, result: ASTNode, line: int, column: int):
        super().__init__(NodeType.CONCLUDE, line, column)
        self.condition = condition
        self.result = result

@dataclass
class PipelineNode(ASTNode):
    """Processing pipeline"""
    name: str
    stages: List["StageNode"]

    def __init__(self, name: str, stages: List["StageNode"], line: int, column: int):
        super().__init__(NodeType.PIPELINE, line, column)
        self.name = name
        self.stages = stages

@dataclass
class StageNode(ASTNode):
    """Pipeline stage"""
    name: str
    parallel_count: Optional[int]
    body: ASTNode

    def __init__(self, name: str, body: ASTNode, line: int, column: int, parallel_count: Optional[int] = None):
        super().__init__(NodeType.STAGE, line, column)
        self.name = name
        self.parallel_count = parallel_count
        self.body = body

@dataclass
class ForkNode(ASTNode):
    """Fork in pipeline"""
    paths: List["PathNode"]

    def __init__(self, paths: List["PathNode"], line: int, column: int):
        super().__init__(NodeType.FORK, line, column)
        self.paths = paths

@dataclass
class PathNode(ASTNode):
    """Path in fork"""
    name: str
    body: ASTNode

    def __init__(self, name: str, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.PATH, line, column)
        self.name = name
        self.body = body

@dataclass
class ExploreNode(ASTNode):
    """Exploration with backtracking"""
    name: str
    tries: List["TryNode"]
    fallbacks: List["FallbackNode"]
    accept_condition: Optional[ASTNode]
    reject_condition: Optional[ASTNode]

    def __init__(self, name: str, tries: List["TryNode"], fallbacks: List["FallbackNode"],
                 line: int, column: int, accept_condition: Optional[ASTNode] = None,
                 reject_condition: Optional[ASTNode] = None):
        super().__init__(NodeType.EXPLORE, line, column)
        self.name = name
        self.tries = tries
        self.fallbacks = fallbacks
        self.accept_condition = accept_condition
        self.reject_condition = reject_condition

@dataclass
class TryNode(ASTNode):
    """Try path in exploration"""
    name: str
    body: ASTNode

    def __init__(self, name: str, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.TRY, line, column)
        self.name = name
        self.body = body

@dataclass
class FallbackNode(ASTNode):
    """Fallback path in exploration"""
    name: str
    body: ASTNode

    def __init__(self, name: str, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.FALLBACK, line, column)
        self.name = name
        self.body = body

@dataclass
class PropagateNode(ASTNode):
    """Uncertainty propagation"""
    uncertainty_var: str
    through_body: ASTNode

    def __init__(self, uncertainty_var: str, through_body: ASTNode, line: int, column: int):
        super().__init__(NodeType.PROPAGATE, line, column)
        self.uncertainty_var = uncertainty_var
        self.through_body = through_body

@dataclass
class ProveNode(ASTNode):
    """Proof statement"""
    statement: ASTNode
    method: Optional[ASTNode]

    def __init__(self, statement: ASTNode, method: Optional[ASTNode], line: int, column: int):
        super().__init__(NodeType.PROVE, line, column)
        self.statement = statement
        self.method = method

@dataclass
class BlockNode(ASTNode):
    """Block of statements"""
    statements: List[ASTNode]

    def __init__(self, statements: List[ASTNode], line: int, column: int):
        super().__init__(NodeType.BLOCK, line, column)
        self.statements = statements

@dataclass
class ProgramNode(ASTNode):
    """Root node of the AST"""
    body: List[ASTNode]

    def __init__(self, body: List[ASTNode]):
        super().__init__(NodeType.PROGRAM, 0, 0)
        self.body = body

class ASTVisitor:
    """Base class for AST visitors"""

    def visit(self, node: ASTNode) -> Any:
        """Dispatch visit to appropriate method"""
        method_name = f"visit_{node.node_type.value.lower()}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> Any:
        """Default visitor for unhandled node types"""
        raise NotImplementedError(f"No visitor for {node.node_type}")

class ASTPrinter(ASTVisitor):
    """Pretty printer for AST"""

    def __init__(self):
        self.indent_level = 0

    def indent(self) -> str:
        return "  " * self.indent_level

    def visit_program(self, node: ProgramNode) -> str:
        results = []
        for stmt in node.body:
            results.append(self.visit(stmt))
        return "\n".join(results)

    def visit_number(self, node: NumberNode) -> str:
        return f"{self.indent()}Number({node.value})"

    def visit_string(self, node: StringNode) -> str:
        return f"{self.indent()}String('{node.value}')"

    def visit_identifier(self, node: IdentifierNode) -> str:
        return f"{self.indent()}Identifier({node.name})"

    def visit_uncertain(self, node: UncertainNode) -> str:
        return f"{self.indent()}Uncertain({node.value} ± {node.uncertainty})"

    def visit_list(self, node: ListNode) -> str:
        self.indent_level += 1
        elems = [self.visit(e) for e in node.elements]
        self.indent_level -= 1
        return f"{self.indent()}List[\n" + "\n".join(elems) + f"\n{self.indent()}]"

    def visit_matrix(self, node: MatrixNode) -> str:
        self.indent_level += 1
        row_strs = []
        for row in node.rows:
            self.indent_level += 1
            elems = [self.visit(e) for e in row]
            self.indent_level -= 1
            row_strs.append(f"{self.indent()}Row(\n" + "\n".join(elems) + f"\n{self.indent()})")
        self.indent_level -= 1
        return f"{self.indent()}Matrix[\n" + "\n".join(row_strs) + f"\n{self.indent()}]"

    def visit_tensor(self, node: TensorNode) -> str:
        self.indent_level += 1
        vals = [self.visit(v) for v in node.values]
        self.indent_level -= 1
        return f"{self.indent()}Tensor(dims={node.dimensions})[\n" + "\n".join(vals) + f"\n{self.indent()}]"

    def visit_binary_op(self, node: BinaryOpNode) -> str:
        self.indent_level += 1
        left = self.visit(node.left)
        right = self.visit(node.right)
        self.indent_level -= 1
        return f"{self.indent()}BinaryOp({node.operator})\n{left}\n{right}"

    def visit_assignment(self, node: AssignmentNode) -> str:
        self.indent_level += 1
        value = self.visit(node.value)
        self.indent_level -= 1
        prefix = ""
        if node.is_uncertain:
            prefix = "uncertain "
        elif node.is_constrained:
            prefix = "constrain "
        elif node.is_evolving:
            prefix = "evolve "
        return f"{self.indent()}{prefix}Assignment({node.target.name})\n{value}"

    def visit_parallel(self, node: ParallelNode) -> str:
        self.indent_level += 1
        branches = []
        for branch in node.branches:
            branches.append(self.visit(branch))
        self.indent_level -= 1
        branches_str = "\n".join(branches)
        workers = f"({node.num_workers})" if node.num_workers else ""
        return f"{self.indent()}Parallel{workers}\n{branches_str}"

    def visit_branch(self, node: BranchNode) -> str:
        self.indent_level += 1
        body = self.visit(node.body)
        self.indent_level -= 1
        return f"{self.indent()}Branch({node.name})\n{body}"

    def visit_block(self, node: BlockNode) -> str:
        self.indent_level += 1
        statements = []
        for stmt in node.statements:
            statements.append(self.visit(stmt))
        self.indent_level -= 1
        stmts_str = "\n".join(statements)
        return f"{self.indent()}Block\n{stmts_str}"
