"""
Synapse Quantum Language Extensions
Created by Michael Benjamin Crowe

Extends the Synapse language with native quantum computing constructs
that integrate seamlessly with classical computing paradigms.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from synapse_interpreter import Token, TokenType, Lexer
from synapse_ast import ASTNode, NodeType
from synapse_parser import Parser

# Extend TokenType for quantum operations
class QuantumTokenType(Enum):
    """Quantum-specific token types for Synapse"""
    QUANTUM = "quantum"
    QUBIT = "qubit"
    QUANTUM_REGISTER = "QuantumRegister"
    CLASSICAL_REGISTER = "ClassicalRegister"
    CIRCUIT = "circuit"
    GATE = "gate"
    MEASURE = "measure"
    ENTANGLE = "entangle"
    SUPERPOSITION = "superposition"
    ORACLE = "oracle"
    ALGORITHM = "algorithm"
    HADAMARD = "H"
    PAULI_X = "X"
    PAULI_Y = "Y"
    PAULI_Z = "Z"
    CNOT = "CNOT"
    TOFFOLI = "Toffoli"
    PHASE = "phase"
    ROTATE = "rotate"
    BELL = "bell"
    GHZ = "ghz"
    VQE = "VQE"
    QAOA = "QAOA"

# Quantum AST nodes
@dataclass
class QuantumRegisterNode(ASTNode):
    """AST node for quantum register declaration"""
    name: str
    size: int
    
    def __init__(self, name: str, size: int, line: int, column: int):
        super().__init__(NodeType.IDENTIFIER, line, column)
        self.name = name
        self.size = size

@dataclass
class QuantumCircuitNode(ASTNode):
    """AST node for quantum circuit definition"""
    name: str
    gates: List['QuantumGateNode']
    measurements: Optional[List['MeasurementNode']] = None
    
    def __init__(self, name: str, gates: List['QuantumGateNode'], 
                 line: int, column: int, measurements=None):
        super().__init__(NodeType.BLOCK, line, column)
        self.name = name
        self.gates = gates
        self.measurements = measurements or []

@dataclass
class QuantumGateNode(ASTNode):
    """AST node for quantum gate application"""
    gate_type: str
    qubits: List[int]
    parameters: Optional[List[float]] = None
    
    def __init__(self, gate_type: str, qubits: List[int], 
                 line: int, column: int, parameters=None):
        super().__init__(NodeType.FUNCTION_CALL, line, column)
        self.gate_type = gate_type
        self.qubits = qubits
        self.parameters = parameters or []

@dataclass
class EntanglementNode(ASTNode):
    """AST node for quantum entanglement operation"""
    source: str
    target: str
    entanglement_type: str  # bell, ghz, custom
    
    def __init__(self, source: str, target: str, entanglement_type: str,
                 line: int, column: int):
        super().__init__(NodeType.BINARY_OP, line, column)
        self.source = source
        self.target = target
        self.entanglement_type = entanglement_type

@dataclass
class MeasurementNode(ASTNode):
    """AST node for quantum measurement"""
    quantum_register: str
    classical_register: str
    basis: str = "computational"  # computational, hadamard, custom
    
    def __init__(self, quantum_register: str, classical_register: str,
                 line: int, column: int, basis: str = "computational"):
        super().__init__(NodeType.ASSIGNMENT, line, column)
        self.quantum_register = quantum_register
        self.classical_register = classical_register
        self.basis = basis

class QuantumLexer(Lexer):
    """Extended lexer for quantum constructs in Synapse"""
    
    def __init__(self, source: str):
        super().__init__(source)
        
        # Add quantum keywords
        self.quantum_keywords = {
            "quantum": QuantumTokenType.QUANTUM,
            "qubit": QuantumTokenType.QUBIT,
            "QuantumRegister": QuantumTokenType.QUANTUM_REGISTER,
            "ClassicalRegister": QuantumTokenType.CLASSICAL_REGISTER,
            "circuit": QuantumTokenType.CIRCUIT,
            "measure": QuantumTokenType.MEASURE,
            "entangle": QuantumTokenType.ENTANGLE,
            "oracle": QuantumTokenType.ORACLE,
            "algorithm": QuantumTokenType.ALGORITHM,
            "H": QuantumTokenType.HADAMARD,
            "X": QuantumTokenType.PAULI_X,
            "Y": QuantumTokenType.PAULI_Y,
            "Z": QuantumTokenType.PAULI_Z,
            "CNOT": QuantumTokenType.CNOT,
            "Toffoli": QuantumTokenType.TOFFOLI,
            "bell": QuantumTokenType.BELL,
            "ghz": QuantumTokenType.GHZ,
            "VQE": QuantumTokenType.VQE,
            "QAOA": QuantumTokenType.QAOA,
        }
        
        # Merge with existing keywords
        self.keywords.update(self.quantum_keywords)
    
    def tokenize_quantum_state(self) -> Token:
        """Tokenize quantum state notation like |0⟩ or |101⟩"""
        start = self.position
        self.advance()  # Skip |
        
        while self.current_char() and self.current_char() not in '⟩>':
            self.advance()
        
        if self.current_char() in '⟩>':
            self.advance()  # Skip ⟩ or >
        
        value = self.source[start:self.position]
        return Token(TokenType.STRING, value, self.line, self.column)

class QuantumParser(Parser):
    """Extended parser for quantum constructs in Synapse"""
    
    def parse_quantum_register(self) -> QuantumRegisterNode:
        """Parse quantum register declaration"""
        token = self.advance()  # consume 'QuantumRegister'
        
        self.consume(TokenType.LEFT_BRACKET, "Expected '[' after QuantumRegister")
        size = int(self.advance().value)  # Get size
        self.consume(TokenType.RIGHT_BRACKET, "Expected ']' after size")
        
        # Generate a name if needed
        name = f"qreg_{size}"
        
        return QuantumRegisterNode(name, size, token.line, token.column)
    
    def parse_quantum_circuit(self) -> QuantumCircuitNode:
        """Parse quantum circuit definition"""
        token = self.advance()  # consume 'circuit'
        name = self.consume(TokenType.IDENTIFIER, "Expected circuit name").value
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' after circuit name")
        self.skip_newlines()
        
        gates = []
        measurements = []
        
        while not self.check(TokenType.RIGHT_BRACE):
            self.skip_newlines()
            
            if self.check(TokenType.IDENTIFIER):
                field = self.peek().value
                
                if field == "apply":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'apply'")
                    gate = self.parse_quantum_gate()
                    gates.append(gate)
                    
                elif field == "measure":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'measure'")
                    measurement = self.parse_measurement()
                    measurements.append(measurement)
            
            self.skip_newlines()
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' to close circuit")
        
        return QuantumCircuitNode(name, gates, token.line, token.column, measurements)
    
    def parse_quantum_gate(self) -> QuantumGateNode:
        """Parse quantum gate application"""
        token = self.peek()
        
        # Check for gate type
        gate_name = self.advance().value
        
        # Parse qubit targets
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after gate {gate_name}")
        
        qubits = []
        while not self.check(TokenType.RIGHT_PAREN):
            if self.check(TokenType.IDENTIFIER):
                # Parse qubit reference like qubits[0]
                reg_name = self.advance().value
                if self.check(TokenType.LEFT_BRACKET):
                    self.advance()
                    idx = int(self.advance().value)
                    self.consume(TokenType.RIGHT_BRACKET, "Expected ']'")
                    qubits.append(idx)
            elif self.check(TokenType.NUMBER):
                qubits.append(int(self.advance().value))
            
            if self.check(TokenType.COMMA):
                self.advance()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after gate qubits")
        
        return QuantumGateNode(gate_name, qubits, token.line, token.column)
    
    def parse_entanglement(self) -> EntanglementNode:
        """Parse entanglement operation"""
        token = self.advance()  # consume 'entangle'
        
        source = self.consume(TokenType.IDENTIFIER, "Expected source register").value
        self.consume(TokenType.IDENTIFIER, "Expected 'with'")  # 'with' keyword
        target = self.consume(TokenType.IDENTIFIER, "Expected target register").value
        
        # Optional entanglement type
        entanglement_type = "bell"  # default
        if self.check(TokenType.LEFT_BRACE):
            self.advance()
            self.skip_newlines()
            
            if self.check(TokenType.IDENTIFIER):
                field = self.peek().value
                if field == "state":
                    self.advance()
                    self.consume(TokenType.COLON, "Expected ':' after 'state'")
                    # Parse state specification
                    if self.peek().value in ["bell", "ghz"]:
                        entanglement_type = self.advance().value
            
            while not self.check(TokenType.RIGHT_BRACE):
                self.advance()
            self.consume(TokenType.RIGHT_BRACE, "Expected '}'")
        
        return EntanglementNode(source, target, entanglement_type, 
                               token.line, token.column)
    
    def parse_measurement(self) -> MeasurementNode:
        """Parse quantum measurement"""
        token = self.peek()
        
        # Parse: quantum_reg -> classical_reg
        quantum_reg = self.consume(TokenType.IDENTIFIER, "Expected quantum register").value
        
        # Check for arrow operator
        if self.peek().value == "->":
            self.advance()
        else:
            self.consume(TokenType.ARROW, "Expected '->' in measurement")
        
        classical_reg = self.consume(TokenType.IDENTIFIER, "Expected classical register").value
        
        return MeasurementNode(quantum_reg, classical_reg, token.line, token.column)

class QuantumInterpreter:
    """Interpreter for quantum operations in Synapse"""
    
    def __init__(self):
        self.quantum_registers = {}
        self.classical_registers = {}
        self.circuits = {}
        self.measurement_results = {}
        
        # Import quantum processor
        from synapse_quantum_core import SynapseQuantumProcessor, QuantumBackend
        self.processor = SynapseQuantumProcessor(backend=QuantumBackend.NUMPY)
    
    def execute_quantum_register(self, node: QuantumRegisterNode):
        """Execute quantum register creation"""
        register = self.processor.create_quantum_register(node.name, node.size)
        self.quantum_registers[node.name] = register
        return f"Created quantum register '{node.name}' with {node.size} qubits"
    
    def execute_quantum_circuit(self, node: QuantumCircuitNode):
        """Execute quantum circuit"""
        results = []
        
        # Apply gates
        for gate in node.gates:
            result = self.execute_quantum_gate(gate)
            results.append(result)
        
        # Perform measurements
        for measurement in node.measurements:
            result = self.execute_measurement(measurement)
            results.append(result)
        
        self.circuits[node.name] = node
        return f"Circuit '{node.name}' executed with {len(node.gates)} gates"
    
    def execute_quantum_gate(self, node: QuantumGateNode):
        """Execute a quantum gate operation"""
        gate_type = node.gate_type.upper()
        
        if gate_type == "H":
            # Hadamard gate
            for qubit in node.qubits:
                self.processor._apply_hadamard_numpy(qubit)
            return f"Applied Hadamard gate to qubits {node.qubits}"
            
        elif gate_type == "X":
            # Pauli-X gate
            for qubit in node.qubits:
                self._apply_pauli_x(qubit)
            return f"Applied Pauli-X gate to qubits {node.qubits}"
            
        elif gate_type == "CNOT":
            # CNOT gate
            if len(node.qubits) >= 2:
                control, target = node.qubits[0], node.qubits[1]
                self._apply_cnot(control, target)
                return f"Applied CNOT gate: control={control}, target={target}"
            
        return f"Applied {gate_type} gate"
    
    def _apply_pauli_x(self, qubit: int):
        """Apply Pauli-X (NOT) gate"""
        n = self.processor.n_qubits
        for i in range(2**(n-1)):
            idx0 = (i // (2**qubit)) * (2**(qubit+1)) + (i % (2**qubit))
            idx1 = idx0 + 2**qubit
            
            # Swap amplitudes
            self.processor.state_vector[idx0], self.processor.state_vector[idx1] = \
                self.processor.state_vector[idx1], self.processor.state_vector[idx0]
    
    def _apply_cnot(self, control: int, target: int):
        """Apply CNOT gate"""
        n = self.processor.n_qubits
        for i in range(2**n):
            if (i >> control) & 1:  # If control qubit is |1⟩
                # Flip target qubit
                target_mask = 1 << target
                j = i ^ target_mask
                if i < j:
                    self.processor.state_vector[i], self.processor.state_vector[j] = \
                        self.processor.state_vector[j], self.processor.state_vector[i]
    
    def execute_entanglement(self, node: EntanglementNode):
        """Execute entanglement operation"""
        result = self.processor.entangle(node.source, node.target, 
                                        node.entanglement_type)
        return f"Entangled {node.source} with {node.target} ({node.entanglement_type})"
    
    def execute_measurement(self, node: MeasurementNode):
        """Execute quantum measurement"""
        result = self.processor.measure(node.quantum_register, n_shots=1024)
        self.measurement_results[node.classical_register] = result
        
        # Get most probable outcome
        max_outcome = max(result.measurement.items(), key=lambda x: x[1])
        
        return f"Measured {node.quantum_register} -> {node.classical_register}: {max_outcome[0]} (p={max_outcome[1]:.3f})"

def demonstrate_quantum_language():
    """Demonstrate quantum language features in Synapse"""
    print("=" * 60)
    print("Synapse Quantum Language Features")
    print("Created by Michael Benjamin Crowe")
    print("=" * 60)
    print()
    
    # Example quantum Synapse code
    quantum_code = """
    // Create quantum registers
    qreg = QuantumRegister[4]
    creg = ClassicalRegister[4]
    
    // Define quantum circuit
    circuit BellStateCircuit {
        apply: H(qubits[0])
        apply: CNOT(qubits[0], qubits[1])
        measure: qreg -> creg
    }
    
    // Entangle two registers
    entangle qreg with auxiliary_qreg {
        state: bell
    }
    """
    
    print("Quantum Synapse Code:")
    print("-" * 40)
    print(quantum_code)
    print("-" * 40)
    
    # Initialize quantum interpreter
    interpreter = QuantumInterpreter()
    
    # Create quantum registers
    qreg = interpreter.processor.create_quantum_register("qreg", 4)
    creg = {"size": 4, "values": None}
    interpreter.quantum_registers["qreg"] = qreg
    interpreter.classical_registers["creg"] = creg
    
    print("\n1. Created quantum registers:")
    print(f"   - qreg: {qreg.n_qubits} qubits")
    print(f"   - creg: {creg['size']} classical bits")
    
    # Apply quantum gates
    print("\n2. Applying quantum gates:")
    interpreter.processor._apply_hadamard_numpy(0)
    print("   - Applied H gate to qubit 0")
    
    interpreter._apply_cnot(0, 1)
    print("   - Applied CNOT(0,1)")
    
    # Measure
    print("\n3. Quantum measurement:")
    result = interpreter.processor.measure("qreg", n_shots=100)
    
    print("   Results (100 shots):")
    for outcome, prob in sorted(result.measurement.items())[:4]:
        print(f"     {outcome}: {prob:.2%}")
    
    print("\n" + "=" * 60)
    print("Quantum language features successfully integrated!")

if __name__ == "__main__":
    demonstrate_quantum_language()