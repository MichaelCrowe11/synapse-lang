# Qubit-Flow Quantum Computing Language - Abstract Syntax Tree
# Complementary to Synapse-Lang for pure quantum computation

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from enum import Enum, auto
import numpy as np

class NodeType(Enum):
    # Quantum-specific node types
    CIRCUIT = auto()
    QUBIT = auto()
    QUDIT = auto()
    QUANTUM_GATE = auto()
    MEASUREMENT = auto()
    ENTANGLEMENT = auto()
    SUPERPOSITION = auto()
    TELEPORTATION = auto()
    
    # Quantum algorithms
    GROVERS = auto()
    SHORS = auto()
    VQE = auto()
    QAOA = auto()
    QFT = auto()
    
    # Error correction
    SYNDROME = auto()
    ERROR_CORRECTION = auto()
    STABILIZER = auto()
    
    # Classical control
    IF_QUANTUM = auto()
    WHILE_QUANTUM = auto()
    FOR_QUANTUM = auto()
    
    # Basic nodes
    IDENTIFIER = auto()
    NUMBER = auto()
    COMPLEX_NUMBER = auto()
    STRING = auto()
    ASSIGNMENT = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    
    # Quantum state nodes
    KET_STATE = auto()
    BRA_STATE = auto()
    BRAKET = auto()
    TENSOR_PRODUCT = auto()
    
    # Program structure
    PROGRAM = auto()
    BLOCK = auto()

class ASTNode(ABC):
    def __init__(self, node_type: NodeType, line: int, column: int):
        self.node_type = node_type
        self.line = line
        self.column = column

@dataclass
class ProgramNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__(NodeType.PROGRAM, line, column)
        self.statements = statements

@dataclass 
class IdentifierNode(ASTNode):
    def __init__(self, name: str, line: int, column: int):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name

@dataclass
class NumberNode(ASTNode):
    def __init__(self, value: float, line: int, column: int):
        super().__init__(NodeType.NUMBER, line, column)
        self.value = value

@dataclass
class ComplexNumberNode(ASTNode):
    def __init__(self, real: float, imag: float, line: int, column: int):
        super().__init__(NodeType.COMPLEX_NUMBER, line, column)
        self.real = real
        self.imag = imag
        
    def to_complex(self) -> complex:
        return complex(self.real, self.imag)

@dataclass
class QubitNode(ASTNode):
    def __init__(self, name: str, initial_state: Optional[ASTNode] = None, line: int = 1, column: int = 1):
        super().__init__(NodeType.QUBIT, line, column)
        self.name = name
        self.initial_state = initial_state  # |0⟩, |1⟩, or superposition

@dataclass
class QuditleNode(ASTNode):
    def __init__(self, name: str, dimension: int, initial_state: Optional[ASTNode] = None, line: int = 1, column: int = 1):
        super().__init__(NodeType.QUDIT, line, column)
        self.name = name
        self.dimension = dimension
        self.initial_state = initial_state

@dataclass
class QuantumCircuitNode(ASTNode):
    def __init__(self, name: str, qubits: List[str], gates: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__(NodeType.CIRCUIT, line, column)
        self.name = name
        self.qubits = qubits
        self.gates = gates

@dataclass
class QuantumGateNode(ASTNode):
    def __init__(self, gate_type: str, qubits: List[str], parameters: List[ASTNode] = None, line: int = 1, column: int = 1):
        super().__init__(NodeType.QUANTUM_GATE, line, column)
        self.gate_type = gate_type
        self.qubits = qubits
        self.parameters = parameters or []

@dataclass
class MeasurementNode(ASTNode):
    def __init__(self, qubit: str, classical_bit: Optional[str] = None, line: int = 1, column: int = 1):
        super().__init__(NodeType.MEASUREMENT, line, column)
        self.qubit = qubit
        self.classical_bit = classical_bit

@dataclass
class KetStateNode(ASTNode):
    def __init__(self, state: str, line: int = 1, column: int = 1):
        super().__init__(NodeType.KET_STATE, line, column)
        self.state = state  # e.g., "0", "1", "+", "-", "psi"

@dataclass
class BraStateNode(ASTNode):
    def __init__(self, state: str, line: int = 1, column: int = 1):
        super().__init__(NodeType.BRA_STATE, line, column)
        self.state = state

@dataclass
class BraKetNode(ASTNode):
    def __init__(self, bra: BraStateNode, ket: KetStateNode, line: int = 1, column: int = 1):
        super().__init__(NodeType.BRAKET, line, column)
        self.bra = bra
        self.ket = ket

@dataclass
class TensorProductNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode, line: int = 1, column: int = 1):
        super().__init__(NodeType.TENSOR_PRODUCT, line, column)
        self.left = left
        self.right = right

@dataclass
class EntanglementNode(ASTNode):
    def __init__(self, qubits: List[str], entanglement_type: str = "bell", line: int = 1, column: int = 1):
        super().__init__(NodeType.ENTANGLEMENT, line, column)
        self.qubits = qubits
        self.entanglement_type = entanglement_type  # "bell", "ghz", "w", etc.

@dataclass
class SuperpositionNode(ASTNode):
    def __init__(self, qubit: str, amplitudes: Dict[str, ComplexNumberNode], line: int = 1, column: int = 1):
        super().__init__(NodeType.SUPERPOSITION, line, column)
        self.qubit = qubit
        self.amplitudes = amplitudes  # {"0": amplitude_0, "1": amplitude_1}

@dataclass
class QuantumTeleportationNode(ASTNode):
    def __init__(self, source: str, entangled_pair: List[str], target: str, line: int = 1, column: int = 1):
        super().__init__(NodeType.TELEPORTATION, line, column)
        self.source = source
        self.entangled_pair = entangled_pair
        self.target = target

@dataclass
class GroversAlgorithmNode(ASTNode):
    def __init__(self, search_space: int, oracle: ASTNode, iterations: Optional[int] = None, line: int = 1, column: int = 1):
        super().__init__(NodeType.GROVERS, line, column)
        self.search_space = search_space
        self.oracle = oracle
        self.iterations = iterations

@dataclass
class ShorsAlgorithmNode(ASTNode):
    def __init__(self, number_to_factor: int, line: int = 1, column: int = 1):
        super().__init__(NodeType.SHORS, line, column)
        self.number_to_factor = number_to_factor

@dataclass
class VQENode(ASTNode):
    def __init__(self, hamiltonian: ASTNode, ansatz: ASTNode, optimizer: str = "COBYLA", line: int = 1, column: int = 1):
        super().__init__(NodeType.VQE, line, column)
        self.hamiltonian = hamiltonian
        self.ansatz = ansatz
        self.optimizer = optimizer

@dataclass
class QFTNode(ASTNode):
    def __init__(self, qubits: List[str], inverse: bool = False, line: int = 1, column: int = 1):
        super().__init__(NodeType.QFT, line, column)
        self.qubits = qubits
        self.inverse = inverse

@dataclass
class AssignmentNode(ASTNode):
    def __init__(self, target: IdentifierNode, value: ASTNode, line: int = 1, column: int = 1):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.target = target
        self.value = value

@dataclass
class BinaryOpNode(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode, line: int = 1, column: int = 1):
        super().__init__(NodeType.BINARY_OP, line, column)
        self.left = left
        self.operator = operator
        self.right = right

@dataclass
class IfQuantumNode(ASTNode):
    def __init__(self, condition: ASTNode, then_block: ASTNode, else_block: Optional[ASTNode] = None, line: int = 1, column: int = 1):
        super().__init__(NodeType.IF_QUANTUM, line, column)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

@dataclass
class BlockNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__(NodeType.BLOCK, line, column)
        self.statements = statements

class ASTVisitor(ABC):
    @abstractmethod
    def visit(self, node: ASTNode) -> Any:
        pass

class ASTPrinter(ASTVisitor):
    def __init__(self, indent: int = 0):
        self.indent_level = indent
        
    def _indent(self) -> str:
        return "  " * self.indent_level
    
    def visit(self, node: ASTNode) -> str:
        method_name = f"visit_{node.node_type.name.lower()}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            return f"{self._indent()}{node.node_type.name}({getattr(node, 'name', '')})"
    
    def visit_program(self, node: ProgramNode) -> str:
        self.indent_level += 1
        statements = "\n".join(self.visit(stmt) for stmt in node.statements)
        self.indent_level -= 1
        return f"Program\n{statements}"
    
    def visit_circuit(self, node: QuantumCircuitNode) -> str:
        self.indent_level += 1
        qubits = ", ".join(node.qubits)
        gates = "\n".join(self.visit(gate) for gate in node.gates)
        self.indent_level -= 1
        return f"{self._indent()}Circuit({node.name}) qubits=[{qubits}]\n{gates}"
    
    def visit_qubit(self, node: QubitNode) -> str:
        initial = f" = {self.visit(node.initial_state)}" if node.initial_state else ""
        return f"{self._indent()}Qubit({node.name}){initial}"
    
    def visit_quantum_gate(self, node: QuantumGateNode) -> str:
        qubits = ", ".join(node.qubits)
        params = f"({', '.join(self.visit(p) for p in node.parameters)})" if node.parameters else ""
        return f"{self._indent()}{node.gate_type}{params}[{qubits}]"
    
    def visit_ket_state(self, node: KetStateNode) -> str:
        return f"|{node.state}⟩"
    
    def visit_measurement(self, node: MeasurementNode) -> str:
        classical = f" -> {node.classical_bit}" if node.classical_bit else ""
        return f"{self._indent()}Measure({node.qubit}){classical}"
    
    def visit_identifier(self, node: IdentifierNode) -> str:
        return node.name
    
    def visit_number(self, node: NumberNode) -> str:
        return str(node.value)
    
    def visit_complex_number(self, node: ComplexNumberNode) -> str:
        return f"{node.real}{'+' if node.imag >= 0 else ''}{node.imag}i"