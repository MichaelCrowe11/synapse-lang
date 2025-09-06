# Synapse-Lang + Qubit-Flow Examples

This directory contains example programs demonstrating the integration between **Synapse-Lang** (scientific reasoning) and **Qubit-Flow** (quantum computing).

## Examples Overview

### 🧬 [Quantum Chemistry Hybrid](quantum_chemistry_hybrid.py)
Demonstrates molecular simulation using hybrid classical-quantum approach:
- **Synapse-Lang**: Molecular parameters with uncertainty, scientific hypothesis
- **Qubit-Flow**: Molecular orbital qubits, VQE optimization
- **Integration**: Quantum-enhanced bond energy calculations

```bash
python examples/quantum_chemistry_hybrid.py
```

### 🤖 [Quantum Machine Learning](quantum_machine_learning.py)
Shows quantum-enhanced pattern recognition and classification:
- **Synapse-Lang**: ML performance hypothesis, uncertainty in accuracy
- **Qubit-Flow**: Quantum feature encoding, quantum SVM, variational classifier
- **Integration**: Parallel classical-quantum model comparison

```bash
python examples/quantum_machine_learning.py
```

### 🔐 [Quantum Cryptography](quantum_cryptography.py)
Implements BB84 quantum key distribution protocol:
- **Synapse-Lang**: Security analysis, eavesdropping detection hypothesis
- **Qubit-Flow**: Quantum state preparation, measurement in random bases
- **Integration**: Error rate analysis for security validation

```bash
python examples/quantum_cryptography.py
```

## Running Examples

### Prerequisites
```bash
pip install numpy
```

### Basic Usage
```python
# Import hybrid interpreter
from synapse_qubit_bridge import create_hybrid_interpreter

# Create bridge instance
bridge = create_hybrid_interpreter()

# Execute hybrid code
results = bridge.execute_hybrid(synapse_code, qubit_code)
```

### Example Output
```
==============================================================
QUANTUM CHEMISTRY HYBRID SIMULATION
==============================================================
Executing hybrid quantum chemistry simulation...

Synapse-Lang (Scientific Reasoning):
- Uncertain molecular parameters
- Quantum hypothesis formation
- Parallel analysis branches

Qubit-Flow (Quantum Computation):
- Molecular orbital qubits
- VQE ansatz circuit
- Ground state optimization

--------------------------------------------------
SIMULATION RESULTS
--------------------------------------------------

✓ Molecular orbital simulation completed
✓ Quantum correlation effects captured
✓ VQE optimization converged
✓ Hybrid classical-quantum analysis successful
```

## Key Features Demonstrated

### 🔬 Scientific Reasoning (Synapse-Lang)
- Uncertain value arithmetic with error propagation
- Hypothesis-driven programming paradigm
- Parallel thought streams for multiple approaches
- Reasoning chains with formal logic

### ⚛️ Quantum Computation (Qubit-Flow)
- Direct quantum circuit construction
- Native quantum gate operations
- Quantum algorithm implementations
- Quantum state measurement and analysis

### 🌉 Hybrid Integration (Bridge)
- Seamless variable sharing between languages
- Quantum-enhanced uncertain values
- Parallel quantum reasoning branches
- Measurement feedback to classical uncertainty

## Extending the Examples

### Add New Quantum Algorithms
```qubit-flow
# In Qubit-Flow
grovers(search_space, oracle_function, iterations)
shors(number_to_factor)
qft(qubit_list)
```

### Enhance Scientific Reasoning
```synapse
# In Synapse-Lang
hypothesis quantum_advantage {
    assume: superposition_enables_speedup
    predict: exponential_improvement
    validate: benchmark_comparison
}
```

### Bridge Integration
```python
# Quantum-enhance any uncertain value
quantum_uncertain = bridge.quantum_enhance_uncertainty("variable_name", "computational")

# Parallel quantum reasoning
branches = [("branch1", synapse_code1, qubit_code1), ...]
consensus = bridge.parallel_quantum_reasoning(branches)
```

## Next Steps

1. **Extend Examples**: Add more quantum algorithms and scientific domains
2. **Hardware Integration**: Connect to real quantum hardware (IBM Quantum, IonQ)
3. **Advanced Algorithms**: Implement QAOA, quantum chemistry, optimization
4. **Visualization**: Add quantum circuit diagrams and state visualization
5. **Performance**: Optimize for larger quantum simulations

---

*These examples showcase the power of combining scientific reasoning with quantum computation through the Synapse-Lang + Qubit-Flow hybrid architecture.*