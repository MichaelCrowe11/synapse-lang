# Synapse-Lang Quantum Computing Tutorial

## Introduction

Synapse-Lang is a quantum-first programming language designed for scientific computing, featuring native support for quantum algorithms, uncertainty quantification, and parallel thought processing. This tutorial will guide you through the quantum computing features.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Quantum Basics](#quantum-basics)
3. [Quantum Circuits](#quantum-circuits)
4. [Quantum Algorithms](#quantum-algorithms)
5. [Parallel Execution](#parallel-execution)
6. [Uncertainty Handling](#uncertainty-handling)
7. [Advanced Topics](#advanced-topics)

## Getting Started

### Installation

```bash
pip install synapse-lang
```

### VS Code Extension

Install the Synapse-Lang extension from the VS Code marketplace for syntax highlighting, IntelliSense, and quantum circuit visualization.

### Your First Quantum Program

```synapse
// hello_quantum.syn
quantum circuit bell_pair {
    qubits: 2

    H(q0)        // Create superposition
    CNOT(q0, q1) // Entangle qubits

    measure: all
}

main {
    result = run(bell_pair)
    print(f"Bell pair measurement: {result}")
}
```

## Quantum Basics

### Qubits and Quantum States

In Synapse-Lang, qubits are the fundamental unit of quantum computation:

```synapse
// Single qubit in superposition
quantum circuit superposition {
    qubits: 1

    H(q0)  // |0⟩ → (|0⟩ + |1⟩)/√2

    measure: q0
}
```

### Quantum Gates

Synapse-Lang supports all standard quantum gates:

#### Single-Qubit Gates

```synapse
// Pauli gates
X(q0)  // Bit flip: |0⟩ → |1⟩, |1⟩ → |0⟩
Y(q0)  // Bit and phase flip
Z(q0)  // Phase flip: |1⟩ → -|1⟩

// Hadamard gate
H(q0)  // Creates superposition

// Phase gates
S(q0)  // √Z gate
T(q0)  // π/8 gate

// Rotation gates
RX(θ, q0)  // Rotation around X-axis
RY(θ, q0)  // Rotation around Y-axis
RZ(θ, q0)  // Rotation around Z-axis
```

#### Two-Qubit Gates

```synapse
CNOT(control, target)  // Controlled-NOT
CZ(control, target)    // Controlled-Z
SWAP(q0, q1)          // Swap qubits
```

#### Three-Qubit Gates

```synapse
TOFFOLI(c1, c2, target)  // Controlled-controlled-NOT
FREDKIN(c, q1, q2)       // Controlled-SWAP
```

## Quantum Circuits

### Basic Circuit Structure

```synapse
quantum circuit my_circuit {
    qubits: 4
    classical_bits: 4

    // Initialize qubits
    initialize: |0000⟩

    // Apply gates
    H(q0)
    CNOT(q0, q1)
    CNOT(q1, q2)
    CNOT(q2, q3)

    // Measure
    measure: all → classical_bits
}
```

### Parameterized Circuits

```synapse
quantum circuit variational(θ[4]) {
    qubits: 2

    RY(θ[0], q0)
    RY(θ[1], q1)
    CNOT(q0, q1)
    RY(θ[2], q0)
    RY(θ[3], q1)

    measure: all
}

// Optimize parameters
parameters = optimize_circuit(variational, target_state)
```

## Quantum Algorithms

### Grover's Search Algorithm

```synapse
experiment GroverSearch {
    // Search for item in unsorted database
    n_items: 16
    target: 10

    quantum circuit grover {
        qubits: 4  // log2(16)

        // Initialize superposition
        for q in qubits {
            H(q)
        }

        // Grover iterations
        iterations: floor(π/4 * sqrt(n_items))

        repeat(iterations) {
            // Oracle marks target
            oracle(target)

            // Diffusion operator
            diffuser()
        }

        measure: all
    }

    result = run(grover)
    print(f"Found item at index: {result}")
}
```

### Quantum Fourier Transform

```synapse
quantum circuit QFT(n) {
    qubits: n

    for j in range(n) {
        H(qubits[j])

        for k in range(j+1, n) {
            controlled_phase(π/2^(k-j), qubits[k], qubits[j])
        }
    }

    // Swap for correct ordering
    for i in range(n/2) {
        SWAP(qubits[i], qubits[n-1-i])
    }
}
```

### Variational Quantum Eigensolver (VQE)

```synapse
experiment VQE_H2 {
    // Find ground state of H2 molecule

    hamiltonian H {
        terms: [
            -0.81261 * I,
            0.17120 * Z0,
            0.16893 * Z1,
            0.17120 * Z0*Z1,
            0.04532 * X0*X1*Y2*Y3
        ]
    }

    quantum circuit ansatz(θ[8]) {
        qubits: 4

        // UCC ansatz
        for i in range(4) {
            RY(θ[i], qubits[i])
        }

        CNOT(q0, q1)
        CNOT(q2, q3)
        CNOT(q1, q2)

        for i in range(4) {
            RY(θ[i+4], qubits[i])
        }
    }

    // Optimization loop
    energy = minimize_expectation(H, ansatz)
    print(f"Ground state energy: {energy}")
}
```

## Parallel Execution

Synapse-Lang's unique parallel execution model allows simultaneous exploration of multiple computational paths:

```synapse
experiment ParallelQuantumClassical {
    parallel {
        branch quantum: {
            // Quantum algorithm
            circuit = grover_search(1000)
            result = run(circuit)
            return: result
        }

        branch classical: {
            // Classical algorithm
            result = linear_search(1000)
            return: result
        }

        branch hybrid: {
            // Hybrid approach
            reduced = classical_preprocess()
            circuit = quantum_search(reduced)
            result = run(circuit)
            return: result
        }
    }

    // Synthesize results
    synthesize: {
        compare_performance(quantum, classical, hybrid)
        select_best_approach()
    }
}
```

## Uncertainty Handling

Synapse-Lang natively handles uncertainty in quantum measurements:

```synapse
// Uncertain values with automatic error propagation
uncertain energy = 13.6 ± 0.2  // eV
uncertain temperature = 300 ± 5  // K

// Operations propagate uncertainty
uncertain result = energy * k_B * temperature
print(f"Result: {result.value} ± {result.error}")

// Quantum measurements with statistical uncertainty
quantum circuit noisy_measurement {
    qubits: 3
    noise_model: depolarizing(p=0.01)

    H(q0)
    CNOT(q0, q1)
    CNOT(q1, q2)

    measure: all
    shots: 1000
}

statistics = analyze_measurements(noisy_measurement)
print(f"Fidelity: {statistics.fidelity} ± {statistics.std_error}")
```

## Advanced Topics

### Quantum Machine Learning

```synapse
// Quantum Neural Network
quantum circuit qnn(x[4], W[16]) {
    qubits: 4

    // Encode input
    for i in range(4) {
        RY(arcsin(x[i]), qubits[i])
    }

    // Variational layers
    for layer in range(2) {
        // Rotation layer
        for i in range(4) {
            RY(W[layer*8 + i*2], qubits[i])
            RZ(W[layer*8 + i*2 + 1], qubits[i])
        }

        // Entangling layer
        for i in range(3) {
            CNOT(qubits[i], qubits[i+1])
        }
    }

    measure: all
    output: expectation(Z)
}

// Training loop
train_quantum_model(qnn, training_data, labels)
```

### Quantum Error Correction

```synapse
quantum circuit three_qubit_code {
    logical: q0
    ancilla: [q1, q2]

    // Encoding
    CNOT(q0, q1)
    CNOT(q0, q2)

    // Error channel
    error_model: bit_flip(p=0.1)

    // Syndrome measurement and correction
    syndrome = measure_syndrome()
    correct_errors(syndrome)

    // Decoding
    CNOT(q0, q2)
    CNOT(q0, q1)
}
```

### Quantum Simulation

```synapse
// Simulate quantum systems
experiment IsingModel {
    hamiltonian H {
        J: 1.0  // Coupling
        h: 0.5  // Field

        H = -J * Σ(Z_i * Z_{i+1}) - h * Σ(X_i)
    }

    quantum circuit time_evolution(t) {
        qubits: 10

        // Trotterization
        dt = 0.01
        steps = t / dt

        for step in range(steps) {
            // ZZ interactions
            for i in range(9) {
                RZZ(-J * dt, i, i+1)
            }

            // X field
            for i in range(10) {
                RX(-h * dt, i)
            }
        }

        measure: all
    }
}
```

## Best Practices

### 1. Circuit Optimization

```synapse
// Use native gates when possible
// Bad: Multiple single-qubit gates
RY(π/2, q0)
RZ(π, q0)
RY(-π/2, q0)

// Good: Single two-qubit gate
X(q0)
```

### 2. Error Mitigation

```synapse
// Use error mitigation techniques
quantum circuit with_mitigation {
    error_mitigation: {
        technique: "zero_noise_extrapolation"
        noise_factors: [1.0, 1.5, 2.0]
    }

    // Circuit implementation
}
```

### 3. Resource Estimation

```synapse
// Estimate quantum resources before execution
circuit_depth = estimate_depth(my_circuit)
gate_count = count_gates(my_circuit)
connectivity = check_connectivity(my_circuit, backend)

if circuit_depth > backend.max_depth {
    my_circuit = optimize_circuit(my_circuit)
}
```

## Debugging Quantum Circuits

### State Vector Inspection

```synapse
debug quantum_circuit {
    breakpoint: after_gate(H, q0)
    inspect: state_vector

    breakpoint: after_gate(CNOT, q0, q1)
    inspect: entanglement_entropy
}
```

### Circuit Visualization

In VS Code with Synapse extension:
- Use `Ctrl+Shift+Q` to visualize circuit
- Use `Ctrl+Shift+S` to show state vector
- Use `Ctrl+Shift+E` to analyze entanglement

## Examples Repository

Find more examples at:
- Basic quantum algorithms: `examples/quantum_algorithms_demo.syn`
- Quantum finance: `examples/quantum_finance_portfolio.syn`
- Drug discovery: `examples/quantum_drug_discovery.syn`

## Next Steps

1. Explore the quantum algorithms library
2. Build your own quantum applications
3. Contribute to the Synapse-Lang ecosystem

## Resources

- [Synapse-Lang GitHub](https://github.com/MichaelCrowe11/synapse-lang)
- [Quantum Algorithm Zoo](https://quantumalgorithmzoo.org)
- [Qiskit Textbook](https://qiskit.org/textbook)

## Support

For questions and support:
- GitHub Issues: [Report bugs or request features](https://github.com/MichaelCrowe11/synapse-lang/issues)
- Documentation: [Full API Reference](https://synapse-lang.readthedocs.io)