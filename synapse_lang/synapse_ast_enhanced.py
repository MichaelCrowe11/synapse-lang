"""
Enhanced AST (Abstract Syntax Tree) for Synapse Language
Complete node definitions for all language constructs
"""

from enum import Enum
from typing import Optional, Union


class NodeType(Enum):
    """All node types in the Synapse language AST"""
    # Basic
    PROGRAM = "program"
    BLOCK = "block"

    # Literals
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    IDENTIFIER = "identifier"

    # Variables
    ASSIGNMENT = "assignment"
    DECLARATION = "declaration"

    # Expressions
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    FUNCTION_CALL = "function_call"
    INDEX_ACCESS = "index_access"

    # Control Flow
    IF = "if"
    WHILE = "while"
    FOR = "for"
    RETURN = "return"
    BREAK = "break"
    CONTINUE = "continue"

    # Quantum
    QUANTUM_CIRCUIT = "quantum_circuit"
    QUANTUM_GATE = "quantum_gate"
    QUANTUM_MEASUREMENT = "quantum_measurement"
    QUANTUM_ALGORITHM = "quantum_algorithm"
    QUANTUM_ANSATZ = "quantum_ansatz"
    QUANTUM_BACKEND = "quantum_backend"
    QUANTUM_NOISE = "quantum_noise"

    # Parallel
    PARALLEL = "parallel"
    BRANCH = "branch"

    # Scientific
    HYPOTHESIS = "hypothesis"
    EXPERIMENT = "experiment"
    PIPELINE = "pipeline"
    STAGE = "stage"

    # Reasoning
    REASON_CHAIN = "reason_chain"
    PREMISE = "premise"
    DERIVATION = "derivation"

    # Exploration
    EXPLORE = "explore"
    TRY_PATH = "try_path"
    FALLBACK = "fallback"

    # Symbolic
    SYMBOLIC = "symbolic"
    LET = "let"
    SOLVE = "solve"
    PROVE = "prove"

    # Advanced
    TENSOR = "tensor"
    MATRIX = "matrix"
    UNCERTAIN = "uncertain"
    CONSTRAIN = "constrain"
    EVOLVE = "evolve"
    OBSERVE = "observe"
    PROPAGATE = "propagate"
    SYNTHESIZE = "synthesize"

    # Structure
    STRUCTURE = "structure"
    THEORY = "theory"
    FORK = "fork"
    STREAM = "stream"
    RUN = "run"


class ASTNode:
    """Base class for all AST nodes"""
    def __init__(self, node_type: NodeType, line: int = 0, column: int = 0):
        self.node_type = node_type
        self.line = line
        self.column = column


class ProgramNode(ASTNode):
    """Root node of the program"""
    def __init__(self, body: list[ASTNode]):
        super().__init__(NodeType.PROGRAM)
        self.body = body


class BlockNode(ASTNode):
    """Block of statements"""
    def __init__(self, statements: list[ASTNode]):
        super().__init__(NodeType.BLOCK)
        self.statements = statements


# ============= Literal Nodes =============

class NumberNode(ASTNode):
    """Number literal"""
    value: float

    def __init__(self, value: float, line: int = 0, column: int = 0):
        super().__init__(NodeType.NUMBER, line, column)
        self.value = value


class StringNode(ASTNode):
    """String literal"""
    value: str

    def __init__(self, value: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.STRING, line, column)
        self.value = value


class BooleanNode(ASTNode):
    """Boolean literal"""
    value: bool

    def __init__(self, value: bool, line: int = 0, column: int = 0):
        super().__init__(NodeType.BOOLEAN, line, column)
        self.value = value


class IdentifierNode(ASTNode):
    """Identifier/variable reference"""
    name: str

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name


# ============= Expression Nodes =============

class BinaryOpNode(ASTNode):
    """Binary operation"""
    left: ASTNode
    operator: str
    right: ASTNode

    def __init__(self, left: ASTNode, operator: str, right: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.BINARY_OP, line, column)
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOpNode(ASTNode):
    """Unary operation"""
    operator: str
    operand: ASTNode

    def __init__(self, operator: str, operand: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.UNARY_OP, line, column)
        self.operator = operator
        self.operand = operand


class FunctionCallNode(ASTNode):
    """Function call"""
    function: ASTNode
    arguments: list[ASTNode]

    def __init__(self, function: ASTNode, arguments: list[ASTNode], line: int = 0, column: int = 0):
        super().__init__(NodeType.FUNCTION_CALL, line, column)
        self.function = function
        self.arguments = arguments


class AssignmentNode(ASTNode):
    """Variable assignment"""
    target: str
    value: ASTNode
    is_uncertain: bool = False

    def __init__(self, target: str, value: ASTNode, is_uncertain: bool = False, line: int = 0, column: int = 0):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.target = target
        self.value = value
        self.is_uncertain = is_uncertain


# ============= Quantum Nodes =============

class QuantumCircuitNode(ASTNode):
    """Quantum circuit definition"""
    name: str
    qubits: int
    gates: list["QuantumGateNode"]
    measurements: list["QuantumMeasurementNode"]

    def __init__(self, name: str, qubits: int, gates: list = None, measurements: list = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.QUANTUM_CIRCUIT, line, column)
        self.name = name
        self.qubits = qubits
        self.gates = gates or []
        self.measurements = measurements or []


class QuantumGateNode(ASTNode):
    """Quantum gate application"""
    gate_type: str
    qubits: list[int]
    parameters: list[ASTNode]

    def __init__(self, gate_type: str, qubits: list[int], parameters: list[ASTNode] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.QUANTUM_GATE, line, column)
        self.gate_type = gate_type
        self.qubits = qubits
        self.parameters = parameters or []


class QuantumMeasurementNode(ASTNode):
    """Quantum measurement"""
    qubits: str | list[int]
    basis: str | None

    def __init__(self, qubits: str | list[int], basis: str | None = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.QUANTUM_MEASUREMENT, line, column)
        self.qubits = qubits
        self.basis = basis


class QuantumAlgorithmNode(ASTNode):
    """Quantum algorithm definition"""
    name: str
    parameters: list[ASTNode]
    ansatz: ASTNode | None
    cost_function: ASTNode | None
    optimizer: ASTNode | None

    def __init__(self, name: str, parameters: list[ASTNode], ansatz: ASTNode | None = None,
                 cost_function: ASTNode | None = None, optimizer: ASTNode | None = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.QUANTUM_ALGORITHM, line, column)
        self.name = name
        self.parameters = parameters
        self.ansatz = ansatz
        self.cost_function = cost_function
        self.optimizer = optimizer


class QuantumAnsatzNode(ASTNode):
    """Quantum ansatz (parameterized circuit)"""
    name: str
    circuit: QuantumCircuitNode | None
    parameters: list[str]

    def __init__(self, name: str, circuit: QuantumCircuitNode | None = None,
                 parameters: list[str] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.QUANTUM_ANSATZ, line, column)
        self.name = name
        self.circuit = circuit
        self.parameters = parameters or []


class QuantumBackendNode(ASTNode):
    """Quantum backend specification"""
    backend_type: str
    provider: str | None
    options: dict

    def __init__(self, backend_type: str, provider: str | None = None,
                 options: dict = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.QUANTUM_BACKEND, line, column)
        self.backend_type = backend_type
        self.provider = provider
        self.options = options or {}


class QuantumNoiseNode(ASTNode):
    """Quantum noise model"""
    noise_type: str
    parameters: dict

    def __init__(self, noise_type: str, parameters: dict = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.QUANTUM_NOISE, line, column)
        self.noise_type = noise_type
        self.parameters = parameters or {}


# ============= Parallel Execution Nodes =============

class ParallelNode(ASTNode):
    """Parallel execution block"""
    branches: list["BranchNode"]
    synthesize: ASTNode | None

    def __init__(self, branches: list["BranchNode"], synthesize: ASTNode | None = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.PARALLEL, line, column)
        self.branches = branches
        self.synthesize = synthesize


class BranchNode(ASTNode):
    """Branch in parallel execution"""
    name: str
    body: ASTNode

    def __init__(self, name: str, body: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.BRANCH, line, column)
        self.name = name
        self.body = body


# ============= Scientific Constructs =============

class HypothesisNode(ASTNode):
    """Hypothesis definition"""
    name: str
    assumptions: list[ASTNode]
    predictions: list[ASTNode]
    validation: ASTNode | None

    def __init__(self, name: str, assumptions: list[ASTNode], predictions: list[ASTNode],
                 validation: ASTNode | None = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.HYPOTHESIS, line, column)
        self.name = name
        self.assumptions = assumptions
        self.predictions = predictions
        self.validation = validation


class ExperimentNode(ASTNode):
    """Experiment definition"""
    name: str
    setup: list[ASTNode]
    parallel: ParallelNode | None
    analyze: list[ASTNode]

    def __init__(self, name: str, setup: list[ASTNode], parallel: ParallelNode | None = None,
                 analyze: list[ASTNode] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.EXPERIMENT, line, column)
        self.name = name
        self.setup = setup
        self.parallel = parallel
        self.analyze = analyze or []


class PipelineNode(ASTNode):
    """Pipeline definition"""
    name: str
    stages: list["StageNode"]

    def __init__(self, name: str, stages: list["StageNode"], line: int = 0, column: int = 0):
        super().__init__(NodeType.PIPELINE, line, column)
        self.name = name
        self.stages = stages


class StageNode(ASTNode):
    """Pipeline stage"""
    name: str
    operations: list[ASTNode]
    parallel_factor: int | None
    fork: Optional["ForkNode"]

    def __init__(self, name: str, operations: list[ASTNode], parallel_factor: int | None = None,
                 fork: Optional["ForkNode"] = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.STAGE, line, column)
        self.name = name
        self.operations = operations
        self.parallel_factor = parallel_factor
        self.fork = fork


class ForkNode(ASTNode):
    """Fork for parallel paths"""
    paths: list[tuple[str, ASTNode]]

    def __init__(self, paths: list[tuple[str, ASTNode]], line: int = 0, column: int = 0):
        super().__init__(NodeType.FORK, line, column)
        self.paths = paths


class StreamNode(ASTNode):
    """Stream processing definition"""
    name: str
    body: ASTNode

    def __init__(self, name: str, body: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.STREAM, line, column)
        self.name = name
        self.body = body


# ============= Reasoning Nodes =============

class ReasonChainNode(ASTNode):
    """Reasoning chain"""
    name: str
    premises: list[tuple[str, ASTNode]]
    derivations: list[tuple[str, list[str], ASTNode]]
    conclusion: ASTNode

    def __init__(self, name: str, premises: list[tuple[str, ASTNode]],
                 derivations: list[tuple[str, list[str], ASTNode]],
                 conclusion: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.REASON_CHAIN, line, column)
        self.name = name
        self.premises = premises
        self.derivations = derivations
        self.conclusion = conclusion


# ============= Exploration Nodes =============

class ExploreNode(ASTNode):
    """Explore block with backtracking"""
    target: str
    attempts: list[tuple[str, ASTNode]]
    fallbacks: list[tuple[str, ASTNode]]
    accept_condition: ASTNode | None

    def __init__(self, target: str, attempts: list[tuple[str, ASTNode]],
                 fallbacks: list[tuple[str, ASTNode]],
                 accept_condition: ASTNode | None = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.EXPLORE, line, column)
        self.target = target
        self.attempts = attempts
        self.fallbacks = fallbacks
        self.accept_condition = accept_condition


# ============= Symbolic Math Nodes =============

class SymbolicNode(ASTNode):
    """Symbolic mathematics block"""
    statements: list[ASTNode]

    def __init__(self, statements: list[ASTNode], line: int = 0, column: int = 0):
        super().__init__(NodeType.SYMBOLIC, line, column)
        self.statements = statements


class LetNode(ASTNode):
    """Symbolic let binding"""
    name: str
    parameters: list[str] | None
    expression: ASTNode

    def __init__(self, name: str, parameters: list[str] | None,
                 expression: ASTNode, line: int = 0, column: int = 0):
        super().__init__(NodeType.LET, line, column)
        self.name = name
        self.parameters = parameters
        self.expression = expression


class SolveNode(ASTNode):
    """Symbolic solve statement"""
    equation: ASTNode
    variable: str
    domain: str | None

    def __init__(self, equation: ASTNode, variable: str, domain: str | None = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.SOLVE, line, column)
        self.equation = equation
        self.variable = variable
        self.domain = domain


class ProveNode(ASTNode):
    """Symbolic prove statement"""
    statement: ASTNode
    domain: str | None

    def __init__(self, statement: ASTNode, domain: str | None = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.PROVE, line, column)
        self.statement = statement
        self.domain = domain


# ============= Advanced Types =============

class TensorNode(ASTNode):
    """Tensor declaration"""
    name: str
    dimensions: list[int]
    initializer: ASTNode | None

    def __init__(self, name: str, dimensions: list[int],
                 initializer: ASTNode | None = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.TENSOR, line, column)
        self.name = name
        self.dimensions = dimensions
        self.initializer = initializer


class MatrixNode(ASTNode):
    """Matrix literal"""
    rows: list[list[ASTNode]]

    def __init__(self, rows: list[list[ASTNode]], line: int = 0, column: int = 0):
        super().__init__(NodeType.MATRIX, line, column)
        self.rows = rows


# ============= Special Nodes =============

class ConstrainNode(ASTNode):
    """Variable constraint"""
    variable: str
    var_type: str
    constraint: ASTNode

    def __init__(self, variable: str, var_type: str, constraint: ASTNode,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.CONSTRAIN, line, column)
        self.variable = variable
        self.var_type = var_type
        self.constraint = constraint


class EvolveNode(ASTNode):
    """Evolving variable"""
    variable: str
    var_type: str
    initial_value: ASTNode

    def __init__(self, variable: str, var_type: str, initial_value: ASTNode,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.EVOLVE, line, column)
        self.variable = variable
        self.var_type = var_type
        self.initial_value = initial_value


class ObserveNode(ASTNode):
    """Quantum observation"""
    variable: str
    var_type: str
    condition: ASTNode | None

    def __init__(self, variable: str, var_type: str, condition: ASTNode | None = None,
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.OBSERVE, line, column)
        self.variable = variable
        self.var_type = var_type
        self.condition = condition


class PropagateNode(ASTNode):
    """Uncertainty propagation block"""
    body: list[ASTNode]

    def __init__(self, body: list[ASTNode], line: int = 0, column: int = 0):
        super().__init__(NodeType.PROPAGATE, line, column)
        self.body = body


class RunNode(ASTNode):
    """Run circuit statement"""
    circuit: str
    backend: str | None
    options: dict[str, ASTNode]

    def __init__(self, circuit: str, backend: str | None = None,
                 options: dict = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.RUN, line, column)
        self.circuit = circuit
        self.backend = backend
        self.options = options or {}


# ============= Control Flow Nodes =============

class IfNode(ASTNode):
    """If statement"""
    condition: ASTNode
    then_body: list[ASTNode]
    else_body: list[ASTNode] | None

    def __init__(self, condition: ASTNode, then_body: list[ASTNode],
                 else_body: list[ASTNode] | None = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.IF, line, column)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class WhileNode(ASTNode):
    """While loop"""
    condition: ASTNode
    body: list[ASTNode]

    def __init__(self, condition: ASTNode, body: list[ASTNode], line: int = 0, column: int = 0):
        super().__init__(NodeType.WHILE, line, column)
        self.condition = condition
        self.body = body


class ForNode(ASTNode):
    """For loop"""
    variable: str
    iterable: ASTNode
    body: list[ASTNode]

    def __init__(self, variable: str, iterable: ASTNode, body: list[ASTNode],
                 line: int = 0, column: int = 0):
        super().__init__(NodeType.FOR, line, column)
        self.variable = variable
        self.iterable = iterable
        self.body = body


class ReturnNode(ASTNode):
    """Return statement"""
    value: ASTNode | None

    def __init__(self, value: ASTNode | None = None, line: int = 0, column: int = 0):
        super().__init__(NodeType.RETURN, line, column)
        self.value = value


class BreakNode(ASTNode):
    """Break statement"""

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(NodeType.BREAK, line, column)


class ContinueNode(ASTNode):
    """Continue statement"""

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(NodeType.CONTINUE, line, column)


# Type alias for any expression node
ExpressionNode = Union[
    NumberNode, StringNode, BooleanNode, IdentifierNode,
    BinaryOpNode, UnaryOpNode, FunctionCallNode,
    TensorNode, MatrixNode
]
