# Getting Started with Qubit-Flow

Welcome to Qubit-Flow - the quantum circuit design and algorithm execution language that makes quantum computing as intuitive as classical programming. Part of the Quantum Trinity, Qubit-Flow bridges the gap between quantum theory and practical quantum computation.

## What is Qubit-Flow?

Qubit-Flow is a domain-specific language designed for:
- **Quantum Circuit Design**: Intuitive syntax for building quantum circuits
- **Algorithm Implementation**: Native support for quantum algorithms (Grover's, Shor's, VQE, QAOA)
- **Hardware Abstraction**: Run on simulators or real quantum hardware seamlessly
- **Error Correction**: Built-in quantum error correction codes
- **Optimization**: Automatic circuit optimization and transpilation

## Installation

```bash
# Install Qubit-Flow as part of the Quantum Trinity
pip install synapse-lang synapse-qubit-flow synapse-quantum-net

# Or install just Qubit-Flow
pip install synapse-qubit-flow

# Install with quantum hardware support
pip install synapse-qubit-flow[hardware]
```

## Your First Quantum Circuit

Let's create a simple Bell state (quantum entanglement):

```qubit-flow
# hello_quantum.qflow
# Create two qubits
qubit alice = |0⟩
qubit bob = |0⟩

# Create Bell state circuit
circuit create_bell_state(alice, bob) {
    H[alice]           # Hadamard gate creates superposition
    CNOT[alice, bob]   # CNOT gate creates entanglement
    
    measure alice -> alice_result
    measure bob -> bob_result
}

# Execute on quantum simulator
run create_bell_state on simulator {
    shots: 1000
    backend: "statevector"
}
```

Run your program:
```bash
qubit-flow hello_quantum.qflow
```

Output:
```
Bell State Results:
|00⟩: 496 counts (49.6%)
|11⟩: 504 counts (50.4%)

Entanglement verified: ✓
Fidelity: 0.998
```

## Core Concepts

### 1. Quantum States

Qubit-Flow provides natural quantum state notation:

```qubit-flow
# Computational basis states
qubit q0 = |0⟩
qubit q1 = |1⟩

# Superposition states
qubit plus = |+⟩      # (|0⟩ + |1⟩)/√2
qubit minus = |-⟩     # (|0⟩ - |1⟩)/√2

# Custom superposition with amplitudes
qubit custom = 0.6|0⟩ + 0.8|1⟩

# Multi-qubit states
qubit q2 = |0⟩
qubit q3 = |1⟩
# Combined state is |01⟩
```

### 2. Quantum Gates

Single-qubit and multi-qubit gates with intuitive syntax:

```qubit-flow
# Pauli gates
X[q0]    # Bit flip (NOT gate)
Y[q0]    # Bit and phase flip
Z[q0]    # Phase flip

# Hadamard gate
H[q0]    # Create superposition

# Rotation gates
RX(π/4)[q0]    # X-axis rotation
RY(π/3)[q0]    # Y-axis rotation  
RZ(π/2)[q0]    # Z-axis rotation

# Phase gates
PHASE(π/4)[q0]    # Global phase
S[q0]             # Phase gate (π/2)
T[q0]             # T gate (π/4)

# Multi-qubit gates
CNOT[control, target]              # Controlled-NOT
CZ[control, target]                # Controlled-Z
TOFFOLI[control1, control2, target] # Toffoli gate
```

### 3. Quantum Circuits

Define reusable quantum circuits:

```qubit-flow
# Parameterized circuit
circuit quantum_fourier_transform(qubits[n]) {
    for i in range(n) {
        H[qubits[i]]
        
        for j in range(i+1, n) {
            controlled_phase = π / (2^(j-i))
            CP(controlled_phase)[qubits[j], qubits[i]]
        }
    }
    
    # Reverse qubit order
    for i in range(n/2) {
        SWAP[qubits[i], qubits[n-1-i]]
    }
}

# Use the circuit
qubits = [|0⟩, |0⟩, |0⟩, |0⟩]
quantum_fourier_transform(qubits)
```

### 4. Quantum Algorithms

Built-in support for major quantum algorithms:

```qubit-flow
# Grover's search algorithm
grovers_search {
    search_space: 16        # 2^4 = 16 items
    oracle: find_item_7     # Function that returns true for item 7
    iterations: 3           # Optimal number of iterations
}

# Variational Quantum Eigensolver (VQE)  
vqe {
    hamiltonian: h2_molecule_hamiltonian
    ansatz: hardware_efficient_ansatz(2)
    optimizer: "COBYLA"
    max_iterations: 100
}

# Quantum Approximate Optimization Algorithm (QAOA)
qaoa {
    cost_hamiltonian: max_cut_hamiltonian
    mixer_hamiltonian: x_mixer
    layers: 3
    optimizer: "SPSA"
}
```

## Quantum Hardware Integration

### Running on Real Quantum Computers

```qubit-flow
# Configure quantum hardware backend
backend ibm_quantum {
    provider: "IBM"
    device: "ibm_cairo"          # 27-qubit device
    optimization_level: 3        # Maximum optimization
    noise_mitigation: true
}

circuit bell_state_hardware(q0, q1) {
    H[q0]
    CNOT[q0, q1]
    measure q0 -> result0
    measure q1 -> result1
}

# Run on real quantum hardware
run bell_state_hardware on ibm_quantum {
    shots: 8192
    timeout: 300  # 5 minute timeout
}
```

### Noise Modeling

```qubit-flow
# Define noise model for realistic simulation
noise_model realistic_device {
    # Single-qubit gate errors
    depolarizing_error(0.001) -> [H, X, Y, Z, RX, RY, RZ]
    
    # Two-qubit gate errors  
    depolarizing_error(0.01) -> [CNOT, CZ]
    
    # Readout errors
    readout_error(0.02) -> measurements
    
    # Thermal relaxation
    thermal_relaxation {
        t1: 50µs    # T1 time
        t2: 70µs    # T2 time
    }
}

# Apply noise model to simulation
run my_circuit on simulator {
    noise_model: realistic_device
    shots: 10000
}
```

## Advanced Features

### Quantum Error Correction

```qubit-flow
# Surface code for quantum error correction
error_correction surface_code {
    distance: 3              # Distance-3 surface code
    logical_qubits: 1       # Encode 1 logical qubit
    syndrome_frequency: 1000 # Extract syndromes every 1000 cycles
}

# Define logical circuit
logical_circuit my_algorithm(logical_q0) {
    # Logical operations on error-corrected qubits
    logical_H[logical_q0]
    logical_RZ(π/4)[logical_q0]
    
    logical_measure logical_q0 -> result
}

# Execute with error correction
run my_algorithm with surface_code {
    error_threshold: 0.001   # Physical error rate
    shots: 1000
}
```

### Circuit Optimization

```qubit-flow
# Automatic circuit optimization
optimization_config {
    level: 3                 # Maximum optimization
    target_backend: "hardware"
    
    # Optimization strategies
    gate_fusion: true        # Combine adjacent single-qubit gates
    commutation_analysis: true
    template_matching: true
    
    # Constraints
    max_circuit_depth: 100
    gate_set: ["H", "RZ", "CNOT"]  # Native gate set
}

circuit unoptimized_circuit(q0, q1) {
    H[q0]
    X[q0]
    H[q0]        # This sequence can be simplified
    CNOT[q0, q1]
    CNOT[q0, q1] # These CNOTs cancel out
    Y[q1]
}

# Automatically optimized during compilation
optimized = optimize(unoptimized_circuit)
print("Original depth:", unoptimized_circuit.depth)      # 5
print("Optimized depth:", optimized.depth)               # 2
```

### Pulse-Level Control

```qubit-flow
# Define custom pulses for precise control
pulse gaussian_pi_pulse {
    duration: 20ns
    amplitude: 0.5
    frequency: 5.2GHz
    phase: 0
    envelope: gaussian(sigma=4ns)
}

pulse drag_pulse {
    duration: 20ns
    amplitude: 0.5 + 0.1i  # Complex amplitude
    envelope: drag(beta=0.4)
}

# Use pulses in circuits
circuit pulse_level_circuit(q0) {
    pulse gaussian_pi_pulse -> q0
    delay 10ns
    pulse drag_pulse -> q0
}
```

## Real-World Examples

### Example 1: Quantum Chemistry (VQE)

```qubit-flow
# H2 molecule ground state calculation
molecule h2_molecule {
    atoms: [["H", [0.0, 0.0, 0.0]], ["H", [0.0, 0.0, 0.74]]]
    basis: "sto-3g"
    charge: 0
    multiplicity: 1
}

# Generate molecular Hamiltonian
hamiltonian = generate_hamiltonian(h2_molecule)

# Hardware-efficient ansatz
circuit h2_ansatz(theta) {
    qubit q0 = |0⟩
    qubit q1 = |0⟩
    
    RY(theta[0])[q0]
    RY(theta[1])[q1]
    CNOT[q0, q1]
    RY(theta[2])[q1]
}

# VQE optimization
vqe_result = vqe {
    hamiltonian: hamiltonian
    ansatz: h2_ansatz
    optimizer: "COBYLA"
    initial_parameters: [0.1, 0.1, 0.1]
}

print("Ground state energy:", vqe_result.energy)
print("Optimal parameters:", vqe_result.parameters)
```

### Example 2: Quantum Machine Learning

```qubit-flow
# Quantum classifier using variational quantum circuit
circuit quantum_classifier(features, weights) {
    # Feature encoding
    for i in range(len(features)) {
        RY(features[i])[qubits[i]]
    }
    
    # Variational layers
    for layer in range(3) {
        # Entangling layer
        for i in range(len(qubits)-1) {
            CNOT[qubits[i], qubits[i+1]]
        }
        
        # Parameterized layer
        for i in range(len(qubits)) {
            RY(weights[layer][i])[qubits[i]]
        }
    }
    
    # Measurement
    measure qubits[0] -> classification
}

# Train quantum classifier
training_data = load_classification_dataset()

quantum_ml_training {
    circuit: quantum_classifier
    training_data: training_data
    optimizer: "Adam"
    learning_rate: 0.01
    epochs: 100
}
```

### Example 3: Quantum Simulation

```qubit-flow
# Simulate quantum many-body system
system ising_model {
    dimensions: [8, 8]  # 8x8 lattice
    coupling_strength: 1.0
    magnetic_field: 0.5
    boundary_conditions: "periodic"
}

# Trotterized time evolution
circuit time_evolution(dt, coupling_J, field_h) {
    # Apply coupling terms
    for i in range(lattice_size) {
        for j in neighbors(i) {
            RZZ(2*coupling_J*dt)[qubits[i], qubits[j]]
        }
    }
    
    # Apply magnetic field
    for i in range(lattice_size) {
        RX(2*field_h*dt)[qubits[i]]
    }
}

# Quantum simulation
simulation quantum_dynamics {
    initial_state: all_spins_up
    hamiltonian: ising_model
    time_steps: 1000
    dt: 0.01
    
    # Measurements at each step
    observables: ["magnetization", "energy", "correlation_function"]
}
```

## Best Practices

### 1. Circuit Design
```qubit-flow
# Good: Minimize circuit depth for NISQ devices
circuit efficient_qft(qubits[4]) {
    # Use native gates when possible
    // Optimized QFT implementation
}

# Bad: Deep circuits on NISQ hardware
circuit deep_circuit(q0) {
    for i in range(1000) {  # Too many operations
        H[q0]
        PHASE(0.001*i)[q0]  # Very small rotations
    }
}
```

### 2. Error Mitigation
```qubit-flow
# Zero-noise extrapolation
error_mitigation zne {
    noise_scaling: [1.0, 1.5, 2.0, 2.5]
    extrapolation: "linear"
}

run my_circuit with zne {
    shots: 8192
}
```

### 3. Measurement Strategy
```qubit-flow
# Efficient measurement grouping
measurement_grouping {
    # Measurements that commute can be done simultaneously
    group1: [Z[q0], Z[q1], ZZ[q0,q1]]  # All Z-basis
    group2: [X[q0], X[q1], XX[q0,q1]]  # All X-basis
    group3: [Y[q0], Y[q1], YY[q0,q1]]  # All Y-basis
}
```

## Next Steps

1. **[Tutorial 2: Quantum Algorithms](02-quantum-algorithms.md)** - Master built-in quantum algorithms
2. **[Tutorial 3: Hardware Integration](03-hardware-integration.md)** - Run on real quantum computers  
3. **[Tutorial 4: Error Correction](04-error-correction.md)** - Implement quantum error correction
4. **[Tutorial 5: Quantum Machine Learning](05-quantum-ml.md)** - Build quantum ML models

## Example Applications

- **Quantum Chemistry**: Molecular simulation and drug discovery
- **Optimization**: Solve complex combinatorial problems
- **Machine Learning**: Quantum-enhanced ML algorithms
- **Cryptography**: Quantum key distribution and post-quantum crypto
- **Simulation**: Many-body quantum systems

## Getting Help

- **Documentation**: [Qubit-Flow API Reference](../api/qubit-flow/)
- **GitHub**: [https://github.com/MichaelCrowe11/synapse-lang](https://github.com/MichaelCrowe11/synapse-lang)
- **Examples**: [Quantum Computing Examples](../examples/quantum/)
- **Community**: [Quantum Computing Discord](https://discord.gg/quantum-trinity)

Ready to build the future of quantum computing? Let's dive into quantum algorithms! ⚛️