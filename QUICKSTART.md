# Synapse-Lang Quick Start Guide

Welcome to Synapse-Lang! Get started with quantum computing in 5 minutes.

## Installation

```bash
# Install Synapse-Lang
pip install synapse-lang

# Install VS Code Extension (search in marketplace)
# Name: "Synapse-Lang"
```

## Hello Quantum World

Create a file `hello_quantum.syn`:

```synapse
// Your first quantum program
quantum circuit bell_pair {
    qubits: 2

    H(q0)        // Superposition
    CNOT(q0, q1) // Entanglement

    measure: all
}

main {
    result = run(bell_pair)
    print(f"Result: {result}")
    // Output: "00" or "11" with 50% probability each
}
```

Run it:

```bash
python -m synapse_lang.interpreter hello_quantum.syn
```

## Core Concepts

### 1. Quantum Circuits

```synapse
quantum circuit my_circuit {
    qubits: 3

    // Apply gates
    H(q0)
    CNOT(q0, q1)
    CNOT(q1, q2)

    measure: all
}
```

### 2. Parallel Execution

```synapse
parallel {
    branch quantum: quantum_algorithm()
    branch classical: classical_algorithm()
}
synthesize: compare_results(quantum, classical)
```

### 3. Uncertainty Quantification

```synapse
uncertain measurement = 42.3 ± 0.5
uncertain temperature = 300 ± 10
result = measurement * temperature  // Uncertainty propagates
```

### 4. Experiments & Pipelines

```synapse
experiment QuantumExperiment {
    hypothesis: "Quantum provides speedup"

    procedure {
        result = run_quantum_algorithm()
    }

    conclusion: verify_hypothesis(result)
}
```

## Common Quantum Gates

| Gate | Syntax | Description |
|------|--------|-------------|
| Hadamard | `H(q)` | Creates superposition |
| Pauli-X | `X(q)` | Bit flip |
| Pauli-Y | `Y(q)` | Bit and phase flip |
| Pauli-Z | `Z(q)` | Phase flip |
| CNOT | `CNOT(c, t)` | Controlled-NOT |
| Rotation | `RY(θ, q)` | Y-axis rotation |

## Quick Examples

### Grover's Search

```synapse
quantum circuit grover_search {
    qubits: 4

    // Superposition
    for q in qubits: H(q)

    // Grover iterations
    repeat(2) {
        oracle(target=5)
        diffuser()
    }

    measure: all
}
```

### Quantum Teleportation

```synapse
quantum circuit teleport {
    qubits: 3

    // Create entangled pair
    H(q1)
    CNOT(q1, q2)

    // Bell measurement
    CNOT(q0, q1)
    H(q0)

    // Classical communication would happen here
    // Apply corrections
    CNOT(q1, q2)
    CZ(q0, q2)
}
```

### VQE for H₂ Molecule

```synapse
quantum circuit vqe_h2(θ[4]) {
    qubits: 2

    RY(θ[0], q0)
    RY(θ[1], q1)
    CNOT(q0, q1)
    RY(θ[2], q0)
    RY(θ[3], q1)

    measure: expectation(H_molecule)
}

// Optimize to find ground state
energy = minimize(vqe_h2, initial_params)
```

## VS Code Features

- **Syntax Highlighting**: Automatic for `.syn` files
- **IntelliSense**: Auto-completion for quantum gates
- **Snippets**: Type `qcirc` for circuit template
- **Visualization**: `Ctrl+Shift+Q` to visualize circuits
- **REPL**: `Ctrl+Shift+R` for interactive mode

## Running Programs

```bash
# Run a Synapse program
python -m synapse_lang.interpreter program.syn

# Interactive REPL
python -m synapse_lang.repl

# Run with quantum backend
python -m synapse_lang.interpreter program.syn --backend qiskit

# Enable debugging
python -m synapse_lang.interpreter program.syn --debug
```

## Project Structure

```
my_quantum_project/
├── main.syn           # Main program
├── circuits/
│   ├── grover.syn    # Grover's algorithm
│   └── vqe.syn       # VQE implementation
├── data/
│   └── molecules.csv # Input data
└── results/
    └── output.json   # Results
```

## Next Steps

1. **Tutorials**: See `docs/quantum-tutorial.md`
2. **Examples**: Explore `examples/` directory
3. **Algorithms**: Check `synapse_lang/quantum/algorithms.py`
4. **VS Code**: Install extension for best experience

## Cheat Sheet

```synapse
// Quantum Circuit
quantum circuit name { ... }

// Parallel Execution
parallel { branch a: {...} branch b: {...} }

// Uncertainty
uncertain x = 5.0 ± 0.1

// Tensors
tensor T[3,3] = [[1,0,0],[0,1,0],[0,0,1]]

// Experiments
experiment Name { hypothesis: "..." procedure {...} }

// Pipelines
pipeline Name { stage A {...} stage B {...} }

// Measurements
measure: all
measure: [q0, q1]
measure: q0 → c0
```

## Common Patterns

### Bell State

```synapse
H(q0); CNOT(q0, q1)  // Creates (|00⟩ + |11⟩)/√2
```

### GHZ State

```synapse
H(q0)
for i in range(1, n): CNOT(q0, q[i])
```

### Quantum Fourier Transform

```synapse
QFT(qubits)  // Built-in QFT
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run `pip install synapse-lang` |
| VS Code no highlighting | Install Synapse-Lang extension |
| Quantum backend error | Check backend configuration |
| Memory error | Reduce number of qubits (<24) |

## Resources

- GitHub: [MichaelCrowe11/synapse-lang](https://github.com/MichaelCrowe11/synapse-lang)
- Documentation: [Full Docs](docs/)
- Examples: [Example Programs](examples/)
- Issues: [Report Bugs](https://github.com/MichaelCrowe11/synapse-lang/issues)

## Get Help

```bash
# Show help
python -m synapse_lang.interpreter --help

# Version info
python -m synapse_lang --version
```

Ready to build quantum applications? Start coding!