"""Visual Programming Interface for Synapse Language
Node-based visual editor for creating Synapse programs
"""

import uuid
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import math


class NodeType(Enum):
    """Types of visual nodes"""
    # Data nodes
    CONSTANT = auto()
    VARIABLE = auto()
    INPUT = auto()
    OUTPUT = auto()

    # Operations
    ARITHMETIC = auto()
    COMPARISON = auto()
    LOGICAL = auto()

    # Scientific nodes
    UNCERTAIN = auto()
    TENSOR = auto()
    QUANTUM = auto()

    # Control flow
    IF_ELSE = auto()
    FOR_LOOP = auto()
    WHILE_LOOP = auto()
    PARALLEL = auto()

    # Functions
    FUNCTION_DEF = auto()
    FUNCTION_CALL = auto()

    # Scientific operations
    MATRIX_OP = auto()
    FFT = auto()
    OPTIMIZATION = auto()
    HYPOTHESIS = auto()


class PortType(Enum):
    """Types of node ports"""
    INPUT = auto()
    OUTPUT = auto()
    CONTROL_IN = auto()
    CONTROL_OUT = auto()


@dataclass
class Port:
    """Connection port on a node"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    port_type: PortType = PortType.INPUT
    data_type: str = "any"
    position: Tuple[float, float] = (0, 0)
    connected_to: List[str] = field(default_factory=list)  # Port IDs

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.port_type.name,
            'data_type': self.data_type,
            'position': self.position,
            'connected_to': self.connected_to
        }


@dataclass
class Node:
    """Visual programming node"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: NodeType = NodeType.CONSTANT
    name: str = ""
    position: Tuple[float, float] = (0, 0)
    size: Tuple[float, float] = (150, 80)
    inputs: List[Port] = field(default_factory=list)
    outputs: List[Port] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    color: str = "#4a90e2"

    def __post_init__(self):
        """Initialize node based on type"""
        if not self.name:
            self.name = self.node_type.name.replace('_', ' ').title()

        # Set up ports based on node type
        self._setup_ports()

        # Set color based on category
        self._set_color()

    def _setup_ports(self):
        """Setup default ports based on node type"""
        if self.node_type == NodeType.CONSTANT:
            self.outputs = [Port(name="value", port_type=PortType.OUTPUT)]

        elif self.node_type == NodeType.VARIABLE:
            self.inputs = [Port(name="value", port_type=PortType.INPUT)]
            self.outputs = [Port(name="value", port_type=PortType.OUTPUT)]

        elif self.node_type == NodeType.INPUT:
            self.outputs = [Port(name="value", port_type=PortType.OUTPUT)]

        elif self.node_type == NodeType.OUTPUT:
            self.inputs = [Port(name="value", port_type=PortType.INPUT)]

        elif self.node_type == NodeType.ARITHMETIC:
            self.inputs = [
                Port(name="a", port_type=PortType.INPUT, data_type="number"),
                Port(name="b", port_type=PortType.INPUT, data_type="number")
            ]
            self.outputs = [Port(name="result", port_type=PortType.OUTPUT, data_type="number")]

        elif self.node_type == NodeType.UNCERTAIN:
            self.inputs = [
                Port(name="value", port_type=PortType.INPUT),
                Port(name="error", port_type=PortType.INPUT, data_type="number")
            ]
            self.outputs = [Port(name="uncertain", port_type=PortType.OUTPUT, data_type="uncertain")]

        elif self.node_type == NodeType.IF_ELSE:
            self.inputs = [
                Port(name="control", port_type=PortType.CONTROL_IN),
                Port(name="condition", port_type=PortType.INPUT, data_type="bool")
            ]
            self.outputs = [
                Port(name="then", port_type=PortType.CONTROL_OUT),
                Port(name="else", port_type=PortType.CONTROL_OUT),
                Port(name="done", port_type=PortType.CONTROL_OUT)
            ]

        elif self.node_type == NodeType.PARALLEL:
            self.inputs = [Port(name="control", port_type=PortType.CONTROL_IN)]
            self.outputs = [
                Port(name=f"branch_{i}", port_type=PortType.CONTROL_OUT)
                for i in range(self.properties.get('branches', 2))
            ]

        elif self.node_type == NodeType.QUANTUM:
            self.inputs = [
                Port(name="qubits", port_type=PortType.INPUT, data_type="int"),
                Port(name="circuit", port_type=PortType.INPUT, data_type="circuit")
            ]
            self.outputs = [Port(name="state", port_type=PortType.OUTPUT, data_type="quantum")]

    def _set_color(self):
        """Set node color based on category"""
        color_map = {
            NodeType.CONSTANT: "#95a5a6",
            NodeType.VARIABLE: "#3498db",
            NodeType.ARITHMETIC: "#e74c3c",
            NodeType.COMPARISON: "#e67e22",
            NodeType.LOGICAL: "#f39c12",
            NodeType.UNCERTAIN: "#9b59b6",
            NodeType.TENSOR: "#1abc9c",
            NodeType.QUANTUM: "#8e44ad",
            NodeType.IF_ELSE: "#2ecc71",
            NodeType.FOR_LOOP: "#27ae60",
            NodeType.PARALLEL: "#16a085",
            NodeType.FUNCTION_DEF: "#34495e",
            NodeType.FUNCTION_CALL: "#2c3e50"
        }
        self.color = color_map.get(self.node_type, "#4a90e2")

    def add_input(self, name: str, data_type: str = "any") -> Port:
        """Add input port"""
        port = Port(name=name, port_type=PortType.INPUT, data_type=data_type)
        self.inputs.append(port)
        self._update_port_positions()
        return port

    def add_output(self, name: str, data_type: str = "any") -> Port:
        """Add output port"""
        port = Port(name=name, port_type=PortType.OUTPUT, data_type=data_type)
        self.outputs.append(port)
        self._update_port_positions()
        return port

    def _update_port_positions(self):
        """Update port positions on node"""
        # Input ports on left side
        for i, port in enumerate(self.inputs):
            y = (i + 1) * self.size[1] / (len(self.inputs) + 1)
            port.position = (0, y)

        # Output ports on right side
        for i, port in enumerate(self.outputs):
            y = (i + 1) * self.size[1] / (len(self.outputs) + 1)
            port.position = (self.size[0], y)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.node_type.name,
            'name': self.name,
            'position': self.position,
            'size': self.size,
            'inputs': [p.to_dict() for p in self.inputs],
            'outputs': [p.to_dict() for p in self.outputs],
            'properties': self.properties,
            'color': self.color
        }


@dataclass
class Connection:
    """Connection between nodes"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_node: str = ""  # Node ID
    from_port: str = ""  # Port ID
    to_node: str = ""    # Node ID
    to_port: str = ""    # Port ID
    path: List[Tuple[float, float]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'from_node': self.from_node,
            'from_port': self.from_port,
            'to_node': self.to_node,
            'to_port': self.to_port,
            'path': self.path
        }


class VisualProgram:
    """Visual program representation"""

    def __init__(self, name: str = "Untitled"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.nodes: Dict[str, Node] = {}
        self.connections: Dict[str, Connection] = {}
        self.selected_nodes: Set[str] = set()
        self.viewport = {"x": 0, "y": 0, "zoom": 1.0}

    def add_node(self, node: Node) -> Node:
        """Add node to program"""
        self.nodes[node.id] = node
        return node

    def remove_node(self, node_id: str):
        """Remove node and its connections"""
        if node_id in self.nodes:
            # Remove connections
            to_remove = []
            for conn_id, conn in self.connections.items():
                if conn.from_node == node_id or conn.to_node == node_id:
                    to_remove.append(conn_id)

            for conn_id in to_remove:
                del self.connections[conn_id]

            # Remove node
            del self.nodes[node_id]
            self.selected_nodes.discard(node_id)

    def connect(self, from_node_id: str, from_port_id: str,
                to_node_id: str, to_port_id: str) -> Optional[Connection]:
        """Create connection between nodes"""
        # Validate nodes exist
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            return None

        # Validate ports exist
        from_node = self.nodes[from_node_id]
        to_node = self.nodes[to_node_id]

        from_port = None
        for port in from_node.outputs:
            if port.id == from_port_id:
                from_port = port
                break

        to_port = None
        for port in to_node.inputs:
            if port.id == to_port_id:
                to_port = port
                break

        if not from_port or not to_port:
            return None

        # Check data type compatibility
        if to_port.data_type != "any" and from_port.data_type != "any":
            if from_port.data_type != to_port.data_type:
                return None  # Type mismatch

        # Create connection
        conn = Connection(
            from_node=from_node_id,
            from_port=from_port_id,
            to_node=to_node_id,
            to_port=to_port_id
        )

        # Calculate path (bezier curve)
        conn.path = self._calculate_connection_path(from_node, from_port, to_node, to_port)

        self.connections[conn.id] = conn

        # Update port connections
        from_port.connected_to.append(to_port_id)
        to_port.connected_to.append(from_port_id)

        return conn

    def _calculate_connection_path(self, from_node: Node, from_port: Port,
                                  to_node: Node, to_port: Port) -> List[Tuple[float, float]]:
        """Calculate bezier curve path for connection"""
        start = (
            from_node.position[0] + from_port.position[0],
            from_node.position[1] + from_port.position[1]
        )
        end = (
            to_node.position[0] + to_port.position[0],
            to_node.position[1] + to_port.position[1]
        )

        # Control points for bezier curve
        control_distance = abs(end[0] - start[0]) / 2
        control1 = (start[0] + control_distance, start[1])
        control2 = (end[0] - control_distance, end[1])

        # Generate path points
        path = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            # Cubic bezier formula
            x = (1-t)**3 * start[0] + 3*(1-t)**2*t * control1[0] + \
                3*(1-t)*t**2 * control2[0] + t**3 * end[0]
            y = (1-t)**3 * start[1] + 3*(1-t)**2*t * control1[1] + \
                3*(1-t)*t**2 * control2[1] + t**3 * end[1]
            path.append((x, y))

        return path

    def to_synapse_code(self) -> str:
        """Convert visual program to Synapse code"""
        code_lines = []
        code_lines.append("# Generated from Visual Programming Interface")
        code_lines.append("")

        # Topological sort for execution order
        sorted_nodes = self._topological_sort()

        # Generate code for each node
        for node_id in sorted_nodes:
            node = self.nodes[node_id]
            node_code = self._node_to_code(node)
            if node_code:
                code_lines.append(node_code)

        return "\n".join(code_lines)

    def _topological_sort(self) -> List[str]:
        """Topological sort of nodes for execution order"""
        in_degree = {node_id: 0 for node_id in self.nodes}

        # Calculate in-degrees
        for conn in self.connections.values():
            in_degree[conn.to_node] += 1

        # Start with nodes that have no inputs
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        sorted_nodes = []

        while queue:
            node_id = queue.pop(0)
            sorted_nodes.append(node_id)

            # Reduce in-degree of connected nodes
            for conn in self.connections.values():
                if conn.from_node == node_id:
                    in_degree[conn.to_node] -= 1
                    if in_degree[conn.to_node] == 0:
                        queue.append(conn.to_node)

        return sorted_nodes

    def _node_to_code(self, node: Node) -> str:
        """Convert node to Synapse code"""
        if node.node_type == NodeType.CONSTANT:
            value = node.properties.get('value', 0)
            return f"let {node.name.lower().replace(' ', '_')} = {value}"

        elif node.node_type == NodeType.VARIABLE:
            var_name = node.properties.get('name', 'var')
            return f"let {var_name} = {self._get_input_value(node, 0)}"

        elif node.node_type == NodeType.ARITHMETIC:
            op = node.properties.get('operation', '+')
            a = self._get_input_value(node, 0)
            b = self._get_input_value(node, 1)
            return f"let result_{node.id[:8]} = {a} {op} {b}"

        elif node.node_type == NodeType.UNCERTAIN:
            value = self._get_input_value(node, 0)
            error = self._get_input_value(node, 1)
            return f"let uncertain_{node.id[:8]} = {value} ± {error}"

        elif node.node_type == NodeType.IF_ELSE:
            condition = self._get_input_value(node, 0)
            return f"if {condition} then"

        elif node.node_type == NodeType.PARALLEL:
            branches = node.properties.get('branches', 2)
            return f"parallel {{{branches} branches}}"

        elif node.node_type == NodeType.QUANTUM:
            qubits = self._get_input_value(node, 0)
            return f"quantum[{qubits}]"

        return f"# {node.name}"

    def _get_input_value(self, node: Node, port_index: int) -> str:
        """Get input value for node port"""
        if port_index >= len(node.inputs):
            return "null"

        port = node.inputs[port_index]

        # Find connected node
        for conn in self.connections.values():
            if conn.to_port == port.id:
                source_node = self.nodes.get(conn.from_node)
                if source_node:
                    return f"node_{conn.from_node[:8]}_output"

        return "null"

    def save(self, filename: str):
        """Save visual program to file"""
        data = {
            'id': self.id,
            'name': self.name,
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'connections': [conn.to_dict() for conn in self.connections.values()],
            'viewport': self.viewport
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filename: str):
        """Load visual program from file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        self.id = data['id']
        self.name = data['name']
        self.viewport = data['viewport']

        # Load nodes
        self.nodes.clear()
        for node_data in data['nodes']:
            node = Node(
                id=node_data['id'],
                node_type=NodeType[node_data['type']],
                name=node_data['name'],
                position=tuple(node_data['position']),
                size=tuple(node_data['size']),
                properties=node_data['properties'],
                color=node_data['color']
            )
            self.nodes[node.id] = node

        # Load connections
        self.connections.clear()
        for conn_data in data['connections']:
            conn = Connection(
                id=conn_data['id'],
                from_node=conn_data['from_node'],
                from_port=conn_data['from_port'],
                to_node=conn_data['to_node'],
                to_port=conn_data['to_port'],
                path=[tuple(p) for p in conn_data['path']]
            )
            self.connections[conn.id] = conn


class NodeLibrary:
    """Library of available node templates"""

    @staticmethod
    def get_templates() -> Dict[str, List[Dict[str, Any]]]:
        """Get categorized node templates"""
        return {
            "Basic": [
                {"type": NodeType.CONSTANT, "name": "Constant", "icon": "📊"},
                {"type": NodeType.VARIABLE, "name": "Variable", "icon": "📝"},
                {"type": NodeType.INPUT, "name": "Input", "icon": "📥"},
                {"type": NodeType.OUTPUT, "name": "Output", "icon": "📤"},
            ],
            "Math": [
                {"type": NodeType.ARITHMETIC, "name": "Add", "properties": {"operation": "+"}, "icon": "➕"},
                {"type": NodeType.ARITHMETIC, "name": "Subtract", "properties": {"operation": "-"}, "icon": "➖"},
                {"type": NodeType.ARITHMETIC, "name": "Multiply", "properties": {"operation": "*"}, "icon": "✖️"},
                {"type": NodeType.ARITHMETIC, "name": "Divide", "properties": {"operation": "/"}, "icon": "➗"},
            ],
            "Scientific": [
                {"type": NodeType.UNCERTAIN, "name": "Uncertain", "icon": "≈"},
                {"type": NodeType.TENSOR, "name": "Tensor", "icon": "🔢"},
                {"type": NodeType.QUANTUM, "name": "Quantum", "icon": "⚛️"},
                {"type": NodeType.FFT, "name": "FFT", "icon": "〰️"},
                {"type": NodeType.OPTIMIZATION, "name": "Optimize", "icon": "📈"},
            ],
            "Control": [
                {"type": NodeType.IF_ELSE, "name": "If/Else", "icon": "🔀"},
                {"type": NodeType.FOR_LOOP, "name": "For Loop", "icon": "🔁"},
                {"type": NodeType.WHILE_LOOP, "name": "While Loop", "icon": "🔄"},
                {"type": NodeType.PARALLEL, "name": "Parallel", "icon": "⚡"},
            ],
            "Functions": [
                {"type": NodeType.FUNCTION_DEF, "name": "Function", "icon": "📦"},
                {"type": NodeType.FUNCTION_CALL, "name": "Call", "icon": "📞"},
            ],
            "Hypothesis": [
                {"type": NodeType.HYPOTHESIS, "name": "Hypothesis", "icon": "🔬"},
            ]
        }


# Example usage and testing
if __name__ == "__main__":
    print("Synapse Visual Programming Interface")
    print("=" * 40)

    # Create visual program
    program = VisualProgram("Uncertainty Calculation")

    # Add nodes
    const1 = Node(node_type=NodeType.CONSTANT, name="Value 1", position=(100, 100))
    const1.properties['value'] = 10.5
    program.add_node(const1)

    const2 = Node(node_type=NodeType.CONSTANT, name="Value 2", position=(100, 200))
    const2.properties['value'] = 5.2
    program.add_node(const2)

    error_node = Node(node_type=NodeType.CONSTANT, name="Error", position=(100, 300))
    error_node.properties['value'] = 0.3
    program.add_node(error_node)

    add_node = Node(node_type=NodeType.ARITHMETIC, name="Add", position=(300, 150))
    add_node.properties['operation'] = '+'
    program.add_node(add_node)

    uncertain_node = Node(node_type=NodeType.UNCERTAIN, name="Uncertain Result", position=(500, 200))
    program.add_node(uncertain_node)

    output_node = Node(node_type=NodeType.OUTPUT, name="Result", position=(700, 200))
    program.add_node(output_node)

    # Create connections
    conn1 = program.connect(const1.id, const1.outputs[0].id,
                           add_node.id, add_node.inputs[0].id)
    conn2 = program.connect(const2.id, const2.outputs[0].id,
                           add_node.id, add_node.inputs[1].id)
    conn3 = program.connect(add_node.id, add_node.outputs[0].id,
                           uncertain_node.id, uncertain_node.inputs[0].id)
    conn4 = program.connect(error_node.id, error_node.outputs[0].id,
                           uncertain_node.id, uncertain_node.inputs[1].id)
    conn5 = program.connect(uncertain_node.id, uncertain_node.outputs[0].id,
                           output_node.id, output_node.inputs[0].id)

    print(f"Created program: {program.name}")
    print(f"Nodes: {len(program.nodes)}")
    print(f"Connections: {len(program.connections)}")

    # Show nodes
    print("\n--- Nodes ---")
    for node in program.nodes.values():
        print(f"- {node.name} ({node.node_type.name}) at {node.position}")

    # Show connections
    print("\n--- Connections ---")
    for conn in program.connections.values():
        from_node = program.nodes[conn.from_node]
        to_node = program.nodes[conn.to_node]
        print(f"- {from_node.name} -> {to_node.name}")

    # Generate Synapse code
    print("\n--- Generated Code ---")
    code = program.to_synapse_code()
    print(code)

    # Save program
    program.save("visual_program.json")
    print("\n✅ Saved visual program to visual_program.json")

    # Show node library
    print("\n--- Node Library ---")
    library = NodeLibrary.get_templates()
    for category, templates in library.items():
        print(f"\n{category}:")
        for template in templates:
            print(f"  {template['icon']} {template['name']}")

    print("\n✅ Visual programming interface implemented!")