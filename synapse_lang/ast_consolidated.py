"""Consolidated and cleaned AST for Synapse language."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class NodeType(Enum):
    """All AST node types."""
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    UNCERTAIN = auto()

    # Operations
    BINARY_OP = auto()
    UNARY_OP = auto()
    ASSIGNMENT = auto()
    FUNCTION_CALL = auto()

    # Collections
    LIST = auto()
    MATRIX = auto()
    TENSOR = auto()

    # Scientific constructs
    HYPOTHESIS = auto()
    EXPERIMENT = auto()
    PARALLEL = auto()
    BRANCH = auto()
    STREAM = auto()

    # Reasoning
    REASON_CHAIN = auto()
    PREMISE = auto()
    DERIVE = auto()
    CONCLUDE = auto()

    # Pipeline
    PIPELINE = auto()
    STAGE = auto()

    # Exploration
    EXPLORE = auto()
    TRY = auto()
    FALLBACK = auto()

    # Uncertainty
    PROPAGATE = auto()

    # Symbolic
    PROVE = auto()
    SYMBOLIC = auto()

    # Quantum
    QUANTUM_CIRCUIT = auto()
    QUANTUM_GATE = auto()
    QUANTUM_MEASURE = auto()
    QUANTUM_BACKEND = auto()
    QUANTUM_ALGORITHM = auto()
    QUANTUM_ANSATZ = auto()
    RUN = auto()

    # Control flow
    BLOCK = auto()
    PROGRAM = auto()
    IF = auto()
    WHILE = auto()
    FOR = auto()

    # Constraints
    CONSTRAINT = auto()
    EVOLVE = auto()
    OBSERVE = auto()

    # Channels
    CHANNEL = auto()
    ASYNC = auto()
    SYNCHRONIZE = auto()


@dataclass
class ASTNode:
    """Base AST node."""
    node_type: NodeType
    line: int
    column: int

    def accept(self, visitor):
        """Visitor pattern support."""
        method_name = f"visit_{self.__class__.__name__}"
        visitor_method = getattr(visitor, method_name, visitor.generic_visit)
        return visitor_method(self)


# Literal nodes
@dataclass
class NumberNode(ASTNode):
    """Numeric literal."""
    value: float

    def __init__(self, value: float, line: int, column: int):
        super().__init__(NodeType.NUMBER, line, column)
        self.value = value


@dataclass
class StringNode(ASTNode):
    """String literal."""
    value: str

    def __init__(self, value: str, line: int, column: int):
        super().__init__(NodeType.STRING, line, column)
        self.value = value


@dataclass
class IdentifierNode(ASTNode):
    """Identifier/variable reference."""
    name: str

    def __init__(self, name: str, line: int, column: int):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name


@dataclass
class UncertainNode(ASTNode):
    """Uncertain value with error bounds."""
    value: float
    uncertainty: float
    distribution: str | None = None

    def __init__(self, value: float, uncertainty: float, line: int, column: int,
                 distribution: str | None = None):
        super().__init__(NodeType.UNCERTAIN, line, column)
        self.value = value
        self.uncertainty = uncertainty
        self.distribution = distribution


# Collection nodes
@dataclass
class ListNode(ASTNode):
    """List literal."""
    elements: list[ASTNode]

    def __init__(self, elements: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.LIST, line, column)
        self.elements = elements


@dataclass
class MatrixNode(ASTNode):
    """Matrix literal."""
    rows: list[list[ASTNode]]

    def __init__(self, rows: list[list[ASTNode]], line: int, column: int):
        super().__init__(NodeType.MATRIX, line, column)
        self.rows = rows


@dataclass
class TensorNode(ASTNode):
    """Tensor declaration."""
    name: str
    dimensions: list[int]
    initializer: ASTNode | None = None

    def __init__(self, name: str, dimensions: list[int], line: int, column: int,
                 initializer: ASTNode | None = None):
        super().__init__(NodeType.TENSOR, line, column)
        self.name = name
        self.dimensions = dimensions
        self.initializer = initializer


# Operation nodes
@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation."""
    operator: str
    left: ASTNode
    right: ASTNode | list[ASTNode]  # List for ternary operator

    def __init__(self, operator: str, left: ASTNode,
                 right: ASTNode | list[ASTNode], line: int, column: int):
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
class AssignmentNode(ASTNode):
    """Variable assignment."""
    target: str | IdentifierNode
    value: ASTNode
    is_uncertain: bool = False
    is_constrained: bool = False
    is_evolving: bool = False

    def __init__(self, target: str | IdentifierNode, value: ASTNode,
                 line: int, column: int, is_uncertain: bool = False,
                 is_constrained: bool = False, is_evolving: bool = False):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.target = target if isinstance(target, str) else target.name
        self.value = value
        self.is_uncertain = is_uncertain
        self.is_constrained = is_constrained
        self.is_evolving = is_evolving


@dataclass
class FunctionCallNode(ASTNode):
    """Function call."""
    function: str | ASTNode
    arguments: list[ASTNode]

    def __init__(self, function: str | ASTNode, arguments: list[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.FUNCTION_CALL, line, column)
        self.function = function
        self.arguments = arguments


# Scientific computing nodes
@dataclass
class HypothesisNode(ASTNode):
    """Hypothesis with assumptions, predictions, and validation."""
    name: str
    assumptions: list[ASTNode]
    predictions: list[ASTNode]
    validations: list[ASTNode]

    def __init__(self, name: str, assumptions: list[ASTNode],
                 predictions: list[ASTNode], validations: list[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.HYPOTHESIS, line, column)
        self.name = name
        self.assumptions = assumptions
        self.predictions = predictions
        self.validations = validations


@dataclass
class ExperimentNode(ASTNode):
    """Experiment with setup, procedure, and synthesis."""
    name: str
    setup: ASTNode | None
    branches: list["BranchNode"]
    synthesize: ASTNode | None

    def __init__(self, name: str, setup: ASTNode | None,
                 branches: list["BranchNode"], synthesize: ASTNode | None,
                 line: int, column: int):
        super().__init__(NodeType.EXPERIMENT, line, column)
        self.name = name
        self.setup = setup
        self.branches = branches
        self.synthesize = synthesize


@dataclass
class ParallelNode(ASTNode):
    """Parallel execution block."""
    branches: list["BranchNode"]
    num_workers: int | None = None

    def __init__(self, branches: list["BranchNode"], line: int, column: int,
                 num_workers: int | None = None):
        super().__init__(NodeType.PARALLEL, line, column)
        self.branches = branches
        self.num_workers = num_workers


@dataclass
class BranchNode(ASTNode):
    """Execution branch."""
    name: str
    body: ASTNode | list[ASTNode]

    def __init__(self, name: str, body: ASTNode | list[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.BRANCH, line, column)
        self.name = name
        self.body = body if isinstance(body, list) else [body]


@dataclass
class StreamNode(ASTNode):
    """Thought stream for parallel processing."""
    name: str
    expression: ASTNode

    def __init__(self, name: str, expression: ASTNode, line: int, column: int):
        super().__init__(NodeType.STREAM, line, column)
        self.name = name
        self.expression = expression


# Reasoning nodes
@dataclass
class ReasonChainNode(ASTNode):
    """Reasoning chain with premises and conclusions."""
    name: str
    premises: list["PremiseNode"]
    derivations: list["DeriveNode"]
    conclusions: list["ConcludeNode"]

    def __init__(self, name: str, premises: list["PremiseNode"],
                 derivations: list["DeriveNode"], conclusions: list["ConcludeNode"],
                 line: int, column: int):
        super().__init__(NodeType.REASON_CHAIN, line, column)
        self.name = name
        self.premises = premises
        self.derivations = derivations
        self.conclusions = conclusions


@dataclass
class PremiseNode(ASTNode):
    """Logical premise."""
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


# Pipeline nodes
@dataclass
class PipelineNode(ASTNode):
    """Data processing pipeline."""
    name: str
    stages: list["StageNode"]

    def __init__(self, name: str, stages: list["StageNode"], line: int, column: int):
        super().__init__(NodeType.PIPELINE, line, column)
        self.name = name
        self.stages = stages


@dataclass
class StageNode(ASTNode):
    """Pipeline stage."""
    name: str
    parallelism: int | None
    operations: dict[str, ASTNode]
    fork_paths: dict[str, ASTNode] | None = None

    def __init__(self, name: str, parallelism: int | None,
                 operations: dict[str, ASTNode], line: int, column: int,
                 fork_paths: dict[str, ASTNode] | None = None):
        super().__init__(NodeType.STAGE, line, column)
        self.name = name
        self.parallelism = parallelism
        self.operations = operations
        self.fork_paths = fork_paths


# Exploration nodes
@dataclass
class ExploreNode(ASTNode):
    """Solution space exploration."""
    name: str
    try_paths: list["TryNode"]
    fallback_paths: list["FallbackNode"]
    accept_condition: ASTNode | None
    reject_condition: ASTNode | None

    def __init__(self, name: str, try_paths: list["TryNode"],
                 fallback_paths: list["FallbackNode"],
                 accept_condition: ASTNode | None,
                 reject_condition: ASTNode | None,
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


# Uncertainty nodes
@dataclass
class PropagateNode(ASTNode):
    """Uncertainty propagation."""
    uncertainty_vars: list[str]
    body: list[ASTNode]

    def __init__(self, uncertainty_vars: list[str], body: list[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.PROPAGATE, line, column)
        self.uncertainty_vars = uncertainty_vars
        self.body = body


# Symbolic nodes
@dataclass
class SymbolicNode(ASTNode):
    """Symbolic mathematics block."""
    declarations: list[ASTNode]
    operations: list[ASTNode]

    def __init__(self, declarations: list[ASTNode], operations: list[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.SYMBOLIC, line, column)
        self.declarations = declarations
        self.operations = operations


@dataclass
class ProveNode(ASTNode):
    """Mathematical proof."""
    statement: ASTNode
    proof: ASTNode | None = None

    def __init__(self, statement: ASTNode, line: int, column: int,
                 proof: ASTNode | None = None):
        super().__init__(NodeType.PROVE, line, column)
        self.statement = statement
        self.proof = proof


# Quantum nodes
@dataclass
class QuantumCircuitNode(ASTNode):
    """Quantum circuit definition."""
    name: str
    qubits: int
    gates: list["QuantumGateNode"]
    measurements: list["QuantumMeasureNode"]

    def __init__(self, name: str, qubits: int, gates: list["QuantumGateNode"],
                 measurements: list["QuantumMeasureNode"], line: int, column: int):
        super().__init__(NodeType.QUANTUM_CIRCUIT, line, column)
        self.name = name
        self.qubits = qubits
        self.gates = gates
        self.measurements = measurements


@dataclass
class QuantumGateNode(ASTNode):
    """Quantum gate application."""
    gate_type: str
    qubits: list[ASTNode]
    parameters: list[ASTNode]

    def __init__(self, gate_type: str, qubits: list[ASTNode],
                 parameters: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_GATE, line, column)
        self.gate_type = gate_type
        self.qubits = qubits
        self.parameters = parameters


@dataclass
class QuantumMeasureNode(ASTNode):
    """Quantum measurement."""
    qubits: list[ASTNode]
    classical_bits: list[ASTNode]

    def __init__(self, qubits: list[ASTNode], classical_bits: list[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.QUANTUM_MEASURE, line, column)
        self.qubits = qubits
        self.classical_bits = classical_bits


@dataclass
class QuantumBackendNode(ASTNode):
    """Quantum backend configuration."""
    name: str
    config: dict[str, ASTNode]

    def __init__(self, name: str, config: dict[str, ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_BACKEND, line, column)
        self.name = name
        self.config = config


@dataclass
class QuantumAlgorithmNode(ASTNode):
    """Quantum algorithm definition."""
    name: str
    parameters: list[ASTNode]
    ansatz: Optional["QuantumAnsatzNode"]
    cost_function: ASTNode | None
    optimizer: str | None

    def __init__(self, name: str, parameters: list[ASTNode],
                 ansatz: Optional["QuantumAnsatzNode"],
                 cost_function: ASTNode | None,
                 optimizer: str | None, line: int, column: int):
        super().__init__(NodeType.QUANTUM_ALGORITHM, line, column)
        self.name = name
        self.parameters = parameters
        self.ansatz = ansatz
        self.cost_function = cost_function
        self.optimizer = optimizer


@dataclass
class QuantumAnsatzNode(ASTNode):
    """Quantum ansatz definition."""
    name: str
    layers: list[ASTNode]

    def __init__(self, name: str, layers: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.QUANTUM_ANSATZ, line, column)
        self.name = name
        self.layers = layers


@dataclass
class RunNode(ASTNode):
    """Circuit/algorithm execution."""
    circuit: str
    backend: str | None
    options: dict[str, ASTNode]

    def __init__(self, circuit: str, backend: str | None,
                 options: dict[str, ASTNode], line: int, column: int):
        super().__init__(NodeType.RUN, line, column)
        self.circuit = circuit
        self.backend = backend
        self.options = options


# Control flow nodes
@dataclass
class BlockNode(ASTNode):
    """Block of statements."""
    statements: list[ASTNode]

    def __init__(self, statements: list[ASTNode], line: int, column: int):
        super().__init__(NodeType.BLOCK, line, column)
        self.statements = statements


@dataclass
class ProgramNode(ASTNode):
    """Root program node."""
    statements: list[ASTNode]

    def __init__(self, statements: list[ASTNode]):
        super().__init__(NodeType.PROGRAM, 0, 0)
        self.statements = statements


@dataclass
class IfNode(ASTNode):
    """Conditional statement."""
    condition: ASTNode
    then_branch: ASTNode
    else_branch: ASTNode | None = None

    def __init__(self, condition: ASTNode, then_branch: ASTNode,
                 line: int, column: int, else_branch: ASTNode | None = None):
        super().__init__(NodeType.IF, line, column)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


@dataclass
class WhileNode(ASTNode):
    """While loop."""
    condition: ASTNode
    body: ASTNode

    def __init__(self, condition: ASTNode, body: ASTNode, line: int, column: int):
        super().__init__(NodeType.WHILE, line, column)
        self.condition = condition
        self.body = body


@dataclass
class ForNode(ASTNode):
    """For loop."""
    variable: str
    iterable: ASTNode
    body: ASTNode

    def __init__(self, variable: str, iterable: ASTNode, body: ASTNode,
                 line: int, column: int):
        super().__init__(NodeType.FOR, line, column)
        self.variable = variable
        self.iterable = iterable
        self.body = body


# Constraint nodes
@dataclass
class ConstraintNode(ASTNode):
    """Variable constraint."""
    variable: str
    var_type: str
    constraints: list[ASTNode]

    def __init__(self, variable: str, var_type: str, constraints: list[ASTNode],
                 line: int, column: int):
        super().__init__(NodeType.CONSTRAINT, line, column)
        self.variable = variable
        self.var_type = var_type
        self.constraints = constraints


@dataclass
class EvolveNode(ASTNode):
    """Evolving variable."""
    variable: str
    initial: ASTNode
    evolution_rule: ASTNode | None = None

    def __init__(self, variable: str, initial: ASTNode, line: int, column: int,
                 evolution_rule: ASTNode | None = None):
        super().__init__(NodeType.EVOLVE, line, column)
        self.variable = variable
        self.initial = initial
        self.evolution_rule = evolution_rule


@dataclass
class ObserveNode(ASTNode):
    """Quantum observation."""
    variable: str
    quantum_state: ASTNode
    collapse_condition: ASTNode | None = None

    def __init__(self, variable: str, quantum_state: ASTNode, line: int, column: int,
                 collapse_condition: ASTNode | None = None):
        super().__init__(NodeType.OBSERVE, line, column)
        self.variable = variable
        self.quantum_state = quantum_state
        self.collapse_condition = collapse_condition


# Channel and async nodes
@dataclass
class ChannelNode(ASTNode):
    """Message passing channel."""
    name: str
    data_type: str

    def __init__(self, name: str, data_type: str, line: int, column: int):
        super().__init__(NodeType.CHANNEL, line, column)
        self.name = name
        self.data_type = data_type


@dataclass
class AsyncNode(ASTNode):
    """Async execution block."""
    name: str
    body: list[ASTNode]
    parallel_count: int | None = None

    def __init__(self, name: str, body: list[ASTNode], line: int, column: int,
                 parallel_count: int | None = None):
        super().__init__(NodeType.ASYNC, line, column)
        self.name = name
        self.body = body
        self.parallel_count = parallel_count


@dataclass
class SynchronizeNode(ASTNode):
    """Synchronization point."""
    streams: list[str]
    condition: ASTNode | None = None

    def __init__(self, streams: list[str], line: int, column: int,
                 condition: ASTNode | None = None):
        super().__init__(NodeType.SYNCHRONIZE, line, column)
        self.streams = streams
        self.condition = condition


# Backwards compatibility aliases
QuantumRunNode = RunNode  # For legacy code
