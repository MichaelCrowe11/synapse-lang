# Qubit-Flow Quantum Computing Language

**A complementary quantum computing language designed to work seamlessly with Synapse-Lang**

## Overview

Qubit-Flow is a specialized quantum computing language that complements Synapse-Lang's scientific reasoning capabilities. While Synapse-Lang excels at parallel hypothesis testing, uncertainty quantification, and scientific reasoning chains, Qubit-Flow provides direct quantum circuit manipulation, quantum algorithm implementation, and hardware-agnostic quantum execution.

## Key Features

### 🔬 **Complementary to Synapse-Lang**
- **Synapse-Lang**: Scientific reasoning, uncertainty propagation, parallel thought streams
- **Qubit-Flow**: Pure quantum computation, circuit design, quantum algorithm execution
- **Bridge Layer**: Seamless interoperability and quantum-enhanced scientific reasoning

### ⚛️ **Quantum-First Design**
```qubit-flow
# Direct quantum circuit construction
qubit q0 = |0⟩
qubit q1 = |+⟩

circuit bell_state(q0, q1) {
    H[q0]
    CNOT[q0, q1]
    measure q0 -> result0
    measure q1 -> result1
}
```

### 🧮 **Native Quantum Algorithms**
```qubit-flow
# Grover's search
grovers(16, oracle_function, 3)

# Shor's factoring  
shors(15)

# Variational Quantum Eigensolver
vqe(hamiltonian, ansatz, "COBYLA")

# Quantum Fourier Transform
qft(q0, q1, q2, q3)
```

### 🔗 **Advanced Quantum Operations**
```qubit-flow
# Quantum entanglement
entangle(alice, bob) bell

# Quantum superposition with custom amplitudes
superpose charlie {
    "0" = 0.6+0.0i
    "1" = 0.8+0.0i
}

# Quantum teleportation
teleport source -> (entangled1, entangled2) -> target
```

## Hybrid Execution with Synapse-Lang

The real power comes from combining both languages for quantum-enhanced scientific reasoning:

### Example: Quantum Chemistry Simulation

**Synapse-Lang (Hypothesis and Uncertainty)**:
```synapse
uncertain bond_length = 1.54 ± 0.02
uncertain bond_energy = 348 ± 5

hypothesis molecular_structure {
    assume: quantum_superposition_effects
    predict: enhanced_stability
    validate: vqe_ground_state
}

parallel {
    branch classical: molecular_dynamics_simulation
    branch quantum: quantum_chemistry_vqe
    branch hybrid: quantum_classical_coupling
}
```

**Qubit-Flow (Quantum Computation)**:
```qubit-flow
# VQE for molecular ground state
qubit h1 = |0⟩
qubit h2 = |0⟩

# Prepare trial wavefunction
circuit molecular_ansatz(h1, h2) {
    RY(theta1)[h1]
    RY(theta2)[h2] 
    CNOT[h1, h2]
    RY(theta3)[h2]
}

# Execute VQE
vqe(molecular_hamiltonian, molecular_ansatz, "COBYLA")
```

**Bridge Integration**:
```python
from synapse_qubit_bridge import create_hybrid_interpreter

bridge = create_hybrid_interpreter()
results = bridge.execute_hybrid(synapse_code, qubit_code)

# Quantum-enhanced uncertain values
quantum_bond_energy = bridge.quantum_enhance_uncertainty("bond_energy", "computational")
```

## Language Architecture

### Core Components

1. **Qubit-Flow Lexer** (`qubit_flow_lexer.py`)
   - Quantum-specific tokens (H, X, Y, Z, CNOT, etc.)
   - Scientific notation for quantum states (|ψ⟩, ⟨φ|)
   - Complex number support (1+2i)

2. **Qubit-Flow AST** (`qubit_flow_ast.py`)
   - Quantum circuit nodes
   - Gate operation nodes  
   - Measurement and entanglement nodes
   - Quantum algorithm nodes

3. **Qubit-Flow Parser** (`qubit_flow_parser.py`)
   - Circuit definition parsing
   - Quantum gate sequence parsing
   - Algorithm parameter parsing

4. **Qubit-Flow Interpreter** (`qubit_flow_interpreter.py`)
   - Quantum state simulation
   - Gate operation execution
   - Measurement simulation
   - Algorithm implementations

5. **Synapse-Qubit Bridge** (`synapse_qubit_bridge.py`)
   - Variable sharing between languages
   - Quantum-enhanced uncertain values
   - Parallel quantum reasoning
   - Measurement feedback loops

## Quantum Operations Reference

### Single-Qubit Gates
```qubit-flow
H[q0]           # Hadamard gate
X[q0]           # Pauli-X (NOT gate)
Y[q0]           # Pauli-Y gate  
Z[q0]           # Pauli-Z gate
RX(π/4)[q0]     # X-rotation gate
RY(π/2)[q0]     # Y-rotation gate
RZ(π/3)[q0]     # Z-rotation gate
PHASE(π/6)[q0]  # Phase gate
```

### Multi-Qubit Gates
```qubit-flow
CNOT[control, target]        # Controlled-NOT
CZ[control, target]          # Controlled-Z
TOFFOLI[control1, control2, target]  # Toffoli gate
```

### Measurements
```qubit-flow
measure q0 -> classical_bit     # Single measurement
measure q0, q1 -> c0, c1       # Multiple measurements  
```

### Quantum Algorithms
```qubit-flow
# Grover's Algorithm
grovers(search_space_size, oracle_function, iterations)

# Shor's Algorithm  
shors(number_to_factor)

# Variational Quantum Eigensolver
vqe(hamiltonian, ansatz_circuit, optimizer)

# Quantum Approximate Optimization Algorithm
qaoa(cost_hamiltonian, mixer_hamiltonian, layers)

# Quantum Fourier Transform
qft(qubit_list) 
qft(qubit_list) inverse  # Inverse QFT
```

## Integration Patterns

### Pattern 1: Quantum-Enhanced Hypothesis Testing
```python
# Use Synapse for hypothesis formation, Qubit-Flow for quantum verification
bridge = create_hybrid_interpreter()

synapse_hypothesis = """
hypothesis quantum_advantage {
    assume: superposition_available
    predict: exponential_speedup  
    validate: quantum_measurement
}
"""

qubit_verification = """
# Implement quantum algorithm to test hypothesis
grovers(1024, search_oracle, optimal_iterations)
"""

results = bridge.execute_hybrid(synapse_hypothesis, qubit_verification)
```

### Pattern 2: Uncertainty-Quantum State Mapping
```python
# Map classical uncertainty to quantum superposition
bridge.quantum_enhance_uncertainty("measurement", "hadamard")

# Perform quantum operations and feed back to uncertainty
measurement = bridge.quantum_measurement_feedback("q0", "Z")
```

### Pattern 3: Parallel Quantum Reasoning
```python
# Run multiple quantum-enhanced reasoning branches
reasoning_branches = [
    ("path1", synapse_code1, qubit_code1),
    ("path2", synapse_code2, qubit_code2),  
    ("path3", synapse_code3, qubit_code3)
]

consensus = bridge.parallel_quantum_reasoning(reasoning_branches)
```

## Testing and Examples

Run the comprehensive test suite:
```bash
python test_qubit_flow.py
```

### Example Test Output
```
============================================================
TEST: Basic Qubit Operations
============================================================
  Created qubits: 3 operations
    qubit q0 = QuantumState(1 qubits): [1.+0.j 0.+0.j]
    qubit q1 = QuantumState(1 qubits): [0.+0.j 1.+0.j]  
    qubit q2 = QuantumState(1 qubits): [0.70710678+0.j 0.70710678+0.j]
  ✓ All qubits created successfully

  [PASSED] test_basic_qubit_operations
```

## Comparison: Synapse-Lang vs Qubit-Flow

| Feature | Synapse-Lang | Qubit-Flow |
|---------|--------------|------------|
| **Primary Focus** | Scientific reasoning | Quantum computation |
| **Uncertainty** | Built-in uncertainty propagation | Quantum superposition states |
| **Parallelism** | Thought streams & hypothesis testing | Quantum circuit parallelism |
| **Algorithms** | Scientific method, reasoning chains | Quantum algorithms (Shor's, Grover's) |
| **Hardware** | Classical computation | Quantum hardware abstraction |
| **Integration** | ✅ Seamless bridge layer | ✅ Seamless bridge layer |

## Future Extensions

- **Quantum Error Correction**: Built-in error mitigation strategies
- **Hardware Backends**: IBM Quantum, Google Quantum AI, IonQ integration
- **Advanced Algorithms**: QAOA, quantum machine learning, quantum chemistry
- **Optimization**: Circuit compilation and optimization
- **Visualization**: Quantum circuit diagrams and state visualization

## Contributing

Qubit-Flow is designed as a complementary language to enhance Synapse-Lang's scientific reasoning with quantum computational power. The bridge architecture allows both languages to leverage their respective strengths while maintaining clean separation of concerns.

---

*Quantum computing meets scientific reasoning - where uncertainty principles become computational advantages.*