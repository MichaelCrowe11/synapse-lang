# Quantum-Net: Distributed Quantum Computing & Networking Language - AST
# Essential for building next-generation quantum internet and distributed quantum systems

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Tuple, Set
from enum import Enum, auto
import numpy as np

class NodeType(Enum):
    # Network structure
    NETWORK = auto()
    NODE = auto()
    LINK = auto()
    CHANNEL = auto()
    ENDPOINT = auto()
    REPEATER = auto()
    
    # Protocols
    PROTOCOL = auto()
    QKD_PROTOCOL = auto()
    TELEPORT_PROTOCOL = auto()
    ENTANGLE_PROTOCOL = auto()
    
    # Operations
    SEND_OP = auto()
    RECEIVE_OP = auto()
    ENTANGLE_OP = auto()
    SWAP_OP = auto()
    MEASURE_OP = auto()
    PURIFY_OP = auto()
    
    # Resources
    RESOURCE = auto()
    QUBIT_RESOURCE = auto()
    CHANNEL_RESOURCE = auto()
    MEMORY_RESOURCE = auto()
    
    # Routing
    ROUTE = auto()
    PATH = auto()
    TOPOLOGY = auto()
    
    # Control flow
    IF_ELSE = auto()
    WHILE_LOOP = auto()
    FOR_LOOP = auto()
    AWAIT = auto()
    
    # Expressions
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    CALL = auto()
    ACCESS = auto()

@dataclass
class ASTNode(ABC):
    """Base class for all AST nodes"""
    node_type: NodeType
    line: int
    column: int
    
    @abstractmethod
    def accept(self, visitor):
        pass

# Network Structure Nodes

@dataclass
class NetworkNode(ASTNode):
    """Represents a quantum network"""
    name: str
    topology: str  # 'mesh', 'star', 'ring', 'tree', 'hybrid'
    nodes: List['NodeDefinition']
    links: List['LinkDefinition']
    protocols: List['ProtocolDefinition']
    settings: Dict[str, Any] = field(default_factory=dict)
    
    def accept(self, visitor):
        return visitor.visit_network(self)

@dataclass
class NodeDefinition(ASTNode):
    """Represents a quantum network node"""
    name: str
    node_type: str  # 'endpoint', 'repeater', 'router', 'server'
    capabilities: Dict[str, Any]
    qubits: int
    memory: Optional[int] = None
    position: Optional[Tuple[float, float, float]] = None  # 3D coordinates
    
    def accept(self, visitor):
        return visitor.visit_node_definition(self)

@dataclass
class LinkDefinition(ASTNode):
    """Represents a quantum link between nodes"""
    source: str
    target: str
    link_type: str  # 'fiber', 'freespace', 'satellite'
    distance: Optional[float] = None
    loss_rate: Optional[float] = None
    noise_model: Optional[str] = None
    channels: List['ChannelDefinition'] = field(default_factory=list)
    
    def accept(self, visitor):
        return visitor.visit_link_definition(self)

@dataclass
class ChannelDefinition(ASTNode):
    """Represents a quantum communication channel"""
    channel_id: str
    channel_type: str  # 'quantum', 'classical', 'hybrid'
    capacity: int
    fidelity: float
    bandwidth: Optional[float] = None
    
    def accept(self, visitor):
        return visitor.visit_channel_definition(self)

# Protocol Nodes

@dataclass
class ProtocolDefinition(ASTNode):
    """Represents a quantum network protocol"""
    name: str
    protocol_type: str
    parameters: Dict[str, Any]
    steps: List[ASTNode]
    error_handling: Optional[List[ASTNode]] = None
    
    def accept(self, visitor):
        return visitor.visit_protocol_definition(self)

@dataclass
class QKDProtocolNode(ASTNode):
    """Quantum Key Distribution protocol"""
    protocol_name: str  # 'BB84', 'E91', 'B92'
    alice: str  # Node name
    bob: str    # Node name
    key_length: int
    security_parameter: float
    authentication: Optional[str] = None
    
    def accept(self, visitor):
        return visitor.visit_qkd_protocol(self)

@dataclass
class TeleportProtocolNode(ASTNode):
    """Quantum teleportation protocol"""
    source_node: str
    target_node: str
    qubit_ref: str
    entangled_pair: Optional[Tuple[str, str]] = None
    
    def accept(self, visitor):
        return visitor.visit_teleport_protocol(self)

@dataclass
class EntangleProtocolNode(ASTNode):
    """Entanglement distribution protocol"""
    nodes: List[str]
    entanglement_type: str  # 'bell', 'ghz', 'w', 'cluster'
    fidelity_threshold: float
    purification: bool = False
    
    def accept(self, visitor):
        return visitor.visit_entangle_protocol(self)

# Operation Nodes

@dataclass
class SendOperation(ASTNode):
    """Send quantum/classical data"""
    data: ASTNode
    destination: str
    channel: Optional[str] = None
    protocol: Optional[str] = None
    
    def accept(self, visitor):
        return visitor.visit_send_operation(self)

@dataclass
class ReceiveOperation(ASTNode):
    """Receive quantum/classical data"""
    source: str
    variable: str
    channel: Optional[str] = None
    timeout: Optional[float] = None
    
    def accept(self, visitor):
        return visitor.visit_receive_operation(self)

@dataclass
class EntangleOperation(ASTNode):
    """Create entanglement between qubits"""
    qubits: List[str]
    entanglement_type: str
    
    def accept(self, visitor):
        return visitor.visit_entangle_operation(self)

@dataclass
class SwapOperation(ASTNode):
    """Entanglement swapping"""
    qubit1: str
    qubit2: str
    measure: bool = True
    
    def accept(self, visitor):
        return visitor.visit_swap_operation(self)

@dataclass
class PurifyOperation(ASTNode):
    """Entanglement purification"""
    pairs: List[Tuple[str, str]]
    protocol: str  # 'DEJMPS', 'BBPSSW', 'recurrence'
    rounds: int = 1
    
    def accept(self, visitor):
        return visitor.visit_purify_operation(self)

# Resource Management Nodes

@dataclass
class ResourceAllocation(ASTNode):
    """Resource allocation request"""
    resource_type: str  # 'qubit', 'channel', 'memory'
    amount: int
    node: str
    priority: int = 0
    duration: Optional[float] = None
    
    def accept(self, visitor):
        return visitor.visit_resource_allocation(self)

@dataclass
class ResourceRelease(ASTNode):
    """Resource release"""
    resource_ref: str
    
    def accept(self, visitor):
        return visitor.visit_resource_release(self)

# Routing Nodes

@dataclass
class RouteDefinition(ASTNode):
    """Define a routing path"""
    name: str
    source: str
    destination: str
    path: List[str]  # List of node names
    metrics: Dict[str, float] = field(default_factory=dict)
    
    def accept(self, visitor):
        return visitor.visit_route_definition(self)

@dataclass
class PathSelection(ASTNode):
    """Path selection strategy"""
    strategy: str  # 'shortest', 'highest_fidelity', 'lowest_latency'
    constraints: Dict[str, Any] = field(default_factory=dict)
    
    def accept(self, visitor):
        return visitor.visit_path_selection(self)

# Control Flow Nodes

@dataclass
class IfElseNode(ASTNode):
    """Conditional execution"""
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None
    
    def accept(self, visitor):
        return visitor.visit_if_else(self)

@dataclass
class WhileLoopNode(ASTNode):
    """While loop"""
    condition: ASTNode
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_while_loop(self)

@dataclass
class ForLoopNode(ASTNode):
    """For loop"""
    variable: str
    iterable: ASTNode
    body: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_for_loop(self)

@dataclass
class AwaitNode(ASTNode):
    """Await asynchronous operation"""
    operation: ASTNode
    timeout: Optional[float] = None
    
    def accept(self, visitor):
        return visitor.visit_await(self)

# Expression Nodes

@dataclass
class IdentifierNode(ASTNode):
    """Variable or identifier reference"""
    name: str
    
    def accept(self, visitor):
        return visitor.visit_identifier(self)

@dataclass
class NumberNode(ASTNode):
    """Numeric literal"""
    value: float
    
    def accept(self, visitor):
        return visitor.visit_number(self)

@dataclass
class StringNode(ASTNode):
    """String literal"""
    value: str
    
    def accept(self, visitor):
        return visitor.visit_string(self)

@dataclass
class BinaryOpNode(ASTNode):
    """Binary operation"""
    operator: str
    left: ASTNode
    right: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)

@dataclass
class UnaryOpNode(ASTNode):
    """Unary operation"""
    operator: str
    operand: ASTNode
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)

@dataclass
class CallNode(ASTNode):
    """Function or method call"""
    function: str
    arguments: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_call(self)

@dataclass
class AccessNode(ASTNode):
    """Member access (dot notation)"""
    object: ASTNode
    member: str
    
    def accept(self, visitor):
        return visitor.visit_access(self)

# Program Root

@dataclass
class ProgramNode(ASTNode):
    """Root node of the AST"""
    networks: List[NetworkNode]
    protocols: List[ProtocolDefinition]
    statements: List[ASTNode]
    
    def accept(self, visitor):
        return visitor.visit_program(self)

# Visitor Pattern Interface

class ASTVisitor(ABC):
    """Visitor pattern for traversing the AST"""
    
    @abstractmethod
    def visit_program(self, node: ProgramNode): pass
    
    @abstractmethod
    def visit_network(self, node: NetworkNode): pass
    
    @abstractmethod
    def visit_node_definition(self, node: NodeDefinition): pass
    
    @abstractmethod
    def visit_link_definition(self, node: LinkDefinition): pass
    
    @abstractmethod
    def visit_channel_definition(self, node: ChannelDefinition): pass
    
    @abstractmethod
    def visit_protocol_definition(self, node: ProtocolDefinition): pass
    
    @abstractmethod
    def visit_qkd_protocol(self, node: QKDProtocolNode): pass
    
    @abstractmethod
    def visit_teleport_protocol(self, node: TeleportProtocolNode): pass
    
    @abstractmethod
    def visit_entangle_protocol(self, node: EntangleProtocolNode): pass
    
    @abstractmethod
    def visit_send_operation(self, node: SendOperation): pass
    
    @abstractmethod
    def visit_receive_operation(self, node: ReceiveOperation): pass
    
    @abstractmethod
    def visit_entangle_operation(self, node: EntangleOperation): pass
    
    @abstractmethod
    def visit_swap_operation(self, node: SwapOperation): pass
    
    @abstractmethod
    def visit_purify_operation(self, node: PurifyOperation): pass
    
    @abstractmethod
    def visit_resource_allocation(self, node: ResourceAllocation): pass
    
    @abstractmethod
    def visit_resource_release(self, node: ResourceRelease): pass
    
    @abstractmethod
    def visit_route_definition(self, node: RouteDefinition): pass
    
    @abstractmethod
    def visit_path_selection(self, node: PathSelection): pass
    
    @abstractmethod
    def visit_if_else(self, node: IfElseNode): pass
    
    @abstractmethod
    def visit_while_loop(self, node: WhileLoopNode): pass
    
    @abstractmethod
    def visit_for_loop(self, node: ForLoopNode): pass
    
    @abstractmethod
    def visit_await(self, node: AwaitNode): pass
    
    @abstractmethod
    def visit_identifier(self, node: IdentifierNode): pass
    
    @abstractmethod
    def visit_number(self, node: NumberNode): pass
    
    @abstractmethod
    def visit_string(self, node: StringNode): pass
    
    @abstractmethod
    def visit_binary_op(self, node: BinaryOpNode): pass
    
    @abstractmethod
    def visit_unary_op(self, node: UnaryOpNode): pass
    
    @abstractmethod
    def visit_call(self, node: CallNode): pass
    
    @abstractmethod
    def visit_access(self, node: AccessNode): pass