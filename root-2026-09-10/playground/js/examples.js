/**
 * Examples Database for Quantum Trinity Playground
 * 
 * Comprehensive collection of examples for Synapse, Qubit-Flow, and Quantum-Net
 */

const EXAMPLES = {
    synapse: [
        {
            id: 'basic-uncertainty',
            title: 'Basic Uncertainty',
            description: 'Introduction to uncertain values and automatic propagation',
            difficulty: 'beginner',
            code: `# Basic Uncertainty Quantification
# Synapse Language makes uncertainty a first-class citizen

# Define measurements with uncertainty
uncertain temperature = 25.3 ± 0.2  # Celsius
uncertain pressure = 1013.25 ± 1.5  # mbar
uncertain humidity = 65 ± 3          # percentage

print("Environmental Measurements:")
print(f"Temperature: {temperature}°C")
print(f"Pressure: {pressure} mbar")
print(f"Humidity: {humidity}%")

# Uncertainty propagates automatically
heat_index = temperature + 0.5 * humidity
print(f"\\nHeat Index: {heat_index}")

# More complex calculations
dew_point = temperature - (100 - humidity) / 5
print(f"Dew Point: {dew_point}°C")

# Check if significantly different
baseline_temp = 20.0 ± 0.5
is_warmer = temperature.significantly_different_from(baseline_temp)
print(f"\\nSignificantly warmer than baseline? {is_warmer}")`
        },
        {
            id: 'monte-carlo',
            title: 'Monte Carlo Simulation',
            description: 'Parallel Monte Carlo with automatic uncertainty',
            difficulty: 'intermediate',
            code: `# Monte Carlo Simulation for Complex Calculations
import math

# Physical constants with measurement uncertainty
uncertain g = 9.81 ± 0.01           # m/s² (local gravity)
uncertain air_density = 1.225 ± 0.01 # kg/m³
uncertain drag_coeff = 0.47 ± 0.02   # sphere drag coefficient

# Object parameters
uncertain mass = 0.145 ± 0.001      # kg (baseball)
uncertain radius = 0.037 ± 0.0005    # m

# Calculate terminal velocity with Monte Carlo
monte_carlo(samples=100000) {
    # Terminal velocity: v = sqrt(2mg / (ρ * Cd * A))
    area = math.pi * radius ** 2
    
    terminal_velocity = math.sqrt(
        (2 * mass * g) / (air_density * drag_coeff * area)
    )
}

print(f"Terminal Velocity: {terminal_velocity:.2f} m/s")
print(f"Uncertainty: ±{terminal_velocity.uncertainty:.2f} m/s")
print(f"Relative uncertainty: {terminal_velocity.relative_uncertainty:.1%}")

# Compare with analytical propagation
analytical_result = math.sqrt(
    (2 * mass * g) / (air_density * drag_coeff * math.pi * radius ** 2)
)

print(f"\\nAnalytical: {analytical_result:.2f} m/s")
print(f"Difference: {abs(terminal_velocity - analytical_result):.3f} m/s")`
        },
        {
            id: 'parallel-sweep',
            title: 'Parallel Parameter Sweep',
            description: 'Explore parameter space with parallel execution',
            difficulty: 'intermediate',
            code: `# Parallel Parameter Sweep for Reaction Kinetics
import numpy as np

# Arrhenius equation parameters with uncertainty
uncertain activation_energy = 75000 ± 2000  # J/mol
uncertain pre_exponential = 1.2e10 ± 0.1e10 # 1/s
R = 8.314  # Gas constant (J/mol/K)

# Parallel sweep over temperatures and pressures
parallel parameter_sweep {
    temperature: [273, 298, 323, 348, 373]  # K
    pressure: [0.5, 1.0, 1.5, 2.0]          # atm
    
    # Calculate rate constant at each condition
    k = pre_exponential * exp(-activation_energy / (R * temperature))
    
    # Pressure correction (simplified)
    k_corrected = k * pressure ** 0.5
    
    # Calculate half-life
    half_life = 0.693 / k_corrected  # First-order reaction
    
    emit {
        "T": temperature,
        "P": pressure,
        "k": k_corrected,
        "t_half": half_life
    }
}

print("Reaction Rate Analysis:")
print("T(K)  P(atm)  k(1/s)         t½(s)")
print("-" * 40)

for result in parameter_sweep_results:
    print(f"{result['T']:3.0f}   {result['P']:3.1f}    "
          f"{result['k']:.3e}    {result['t_half']:.3e}")

# Find optimal conditions
optimal = min(parameter_sweep_results, key=lambda r: r['t_half'].value)
print(f"\\nFastest reaction at T={optimal['T']}K, P={optimal['P']}atm")`
        },
        {
            id: 'scientific-reasoning',
            title: 'Scientific Reasoning Chain',
            description: 'Hypothesis testing and model comparison',
            difficulty: 'advanced',
            code: `# Scientific Reasoning: Model Comparison
import numpy as np

# Experimental data with measurement errors
experimental_data = [
    {"x": 1.0 ± 0.05, "y": 2.1 ± 0.1},
    {"x": 2.0 ± 0.05, "y": 4.3 ± 0.15},
    {"x": 3.0 ± 0.05, "y": 9.2 ± 0.2},
    {"x": 4.0 ± 0.05, "y": 15.8 ± 0.3},
    {"x": 5.0 ± 0.05, "y": 25.1 ± 0.4}
]

reasoning_chain {
    hypothesis linear: "y = ax + b"
    hypothesis quadratic: "y = ax² + bx + c"
    hypothesis exponential: "y = a * exp(bx)"
    
    evidence linear_fit: {
        # Fit linear model
        model = fit_linear(experimental_data)
        chi2 = calculate_chi_squared(model, experimental_data)
        aic = 2 * 2 + chi2  # 2 parameters
        
        emit {"model": "linear", "chi2": chi2, "aic": aic}
    }
    
    evidence quadratic_fit: {
        # Fit quadratic model
        model = fit_quadratic(experimental_data)
        chi2 = calculate_chi_squared(model, experimental_data)
        aic = 2 * 3 + chi2  # 3 parameters
        
        emit {"model": "quadratic", "chi2": chi2, "aic": aic}
    }
    
    evidence exponential_fit: {
        # Fit exponential model
        model = fit_exponential(experimental_data)
        chi2 = calculate_chi_squared(model, experimental_data)
        aic = 2 * 2 + chi2  # 2 parameters
        
        emit {"model": "exponential", "chi2": chi2, "aic": aic}
    }
    
    conclusion: {
        # Compare models using AIC
        best_model = min(evidence, key=lambda e: e['aic'])
        
        print("Model Comparison Results:")
        for e in evidence:
            print(f"{e['model']:12} χ²={e['chi2']:.2f}  AIC={e['aic']:.2f}")
        
        print(f"\\nBest model: {best_model['model']}")
        
        # Calculate evidence ratios
        for e in evidence:
            if e != best_model:
                ratio = exp((best_model['aic'] - e['aic']) / 2)
                print(f"Evidence ratio {best_model['model']}/{e['model']}: {ratio:.1f}")
    }
}`
        },
        {
            id: 'machine-learning',
            title: 'ML with Uncertainty',
            description: 'Machine learning with uncertainty quantification',
            difficulty: 'advanced',
            code: `# Gaussian Process Regression with Uncertainty
import numpy as np
from ml_integration import GaussianProcessUncertainty

# Training data with measurement uncertainty
X_train = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])
y_train = [
    UncertainValue(2.5, 0.1),
    UncertainValue(3.8, 0.15),
    UncertainValue(4.2, 0.1),
    UncertainValue(5.1, 0.2),
    UncertainValue(6.3, 0.15)
]

# Create and train GP model
gp_model = GaussianProcessUncertainty(
    kernel='rbf',
    length_scale=1.0 ± 0.1,
    noise_level=0.1 ± 0.02
)

gp_model.fit(X_train, y_train)

# Make predictions with uncertainty
X_test = np.linspace(0, 6, 50).reshape(-1, 1)
predictions = gp_model.predict(X_test, return_uncertainty=True)

print("Gaussian Process Predictions:")
print("X     Mean    Uncertainty   95% CI")
print("-" * 40)

for i in [0, 10, 20, 30, 40, 49]:
    x = X_test[i, 0]
    pred = predictions[i]
    ci_lower = pred.value - 1.96 * pred.uncertainty
    ci_upper = pred.value + 1.96 * pred.uncertainty
    
    print(f"{x:.2f}  {pred.value:.3f}  ±{pred.uncertainty:.3f}     "
          f"[{ci_lower:.3f}, {ci_upper:.3f}]")

# Model validation
validation_score = gp_model.cross_validate(cv=5)
print(f"\\nCross-validation score: {validation_score:.3f}")`
        }
    ],
    
    'qubit-flow': [
        {
            id: 'bell-state',
            title: 'Bell State Creation',
            description: 'Create quantum entanglement',
            difficulty: 'beginner',
            code: `// Bell State - The "Hello World" of Quantum Computing
// Creates maximum entanglement between two qubits

// Initialize two qubits in |0⟩ state
qubit alice = |0⟩
qubit bob = |0⟩

print("Initial state: |00⟩")

// Create Bell state circuit
circuit create_bell_state(q1, q2) {
    // Step 1: Put first qubit in superposition
    H[q1]  // Now: (|0⟩ + |1⟩)/√2 ⊗ |0⟩
    
    // Step 2: Entangle qubits with CNOT
    CNOT[q1, q2]  // Now: (|00⟩ + |11⟩)/√2
    
    print("Bell state created: (|00⟩ + |11⟩)/√2")
    
    // Measure both qubits
    measure q1 -> result1
    measure q2 -> result2
}

// Execute the circuit
run create_bell_state(alice, bob) on simulator {
    shots: 1000
    backend: "statevector"
}

// Analyze results
print("\\nMeasurement Results (1000 shots):")
print("State  Count  Probability")
print("-" * 30)
for state, count in measurement_results:
    prob = count / 1000
    print(f"|{state}⟩   {count:4d}   {prob:.3f}")

// Verify entanglement
entanglement_measure = calculate_entanglement(alice, bob)
print(f"\\nEntanglement measure: {entanglement_measure:.3f}")
print(f"Perfect entanglement = 1.0")`
        },
        {
            id: 'grovers-algorithm',
            title: "Grover's Search Algorithm",
            description: 'Quantum database search',
            difficulty: 'intermediate',
            code: `// Grover's Algorithm - Quantum Search
// Finds marked item in unsorted database with O(√N) queries

// Search space configuration
grovers_config {
    database_size: 16  // 2^4 = 16 items
    marked_item: 10    // We're looking for item 10 (1010 in binary)
    n_qubits: 4
}

// Oracle circuit - marks the target item
circuit grovers_oracle(qubits[4], target) {
    // Flip phase of target state
    // For target = 10 = 1010 in binary
    X[qubits[1]]  // Flip qubits that should be 0
    X[qubits[3]]
    
    // Multi-controlled Z gate
    controlled_Z[qubits[0], qubits[1], qubits[2], qubits[3]]
    
    // Uncompute
    X[qubits[1]]
    X[qubits[3]]
}

// Diffusion operator (inversion about average)
circuit grovers_diffusion(qubits[4]) {
    // Apply H gates
    for q in qubits:
        H[q]
    
    // Apply X gates
    for q in qubits:
        X[q]
    
    // Multi-controlled Z
    controlled_Z[qubits[0], qubits[1], qubits[2], qubits[3]]
    
    // Undo X gates
    for q in qubits:
        X[q]
    
    // Undo H gates
    for q in qubits:
        H[q]
}

// Main Grover's algorithm
circuit grovers_search() {
    // Initialize qubits
    qubits = [|0⟩, |0⟩, |0⟩, |0⟩]
    
    // Create uniform superposition
    for q in qubits:
        H[q]
    
    print("Initial superposition created")
    
    // Calculate optimal number of iterations
    n_iterations = floor(π/4 * sqrt(16))  // ≈ 3 for 16 items
    print(f"Running {n_iterations} Grover iterations")
    
    // Grover iterations
    for i in range(n_iterations):
        grovers_oracle(qubits, marked_item)
        grovers_diffusion(qubits)
        
        print(f"Iteration {i+1} complete")
    
    // Measure all qubits
    for i, q in enumerate(qubits):
        measure q -> results[i]
    
    // Convert to decimal
    found_item = binary_to_decimal(results)
    return found_item
}

// Run the search
result = run grovers_search() on simulator {
    shots: 100
    show_histogram: true
}

print(f"\\nSearch Results:")
print(f"Target item: {marked_item}")
print(f"Found item: {result} (Success rate: {success_rate}%)")
print(f"Classical would need avg {database_size/2} queries")
print(f"Grover's used {n_iterations} iterations")`
        },
        {
            id: 'vqe-h2',
            title: 'VQE for H₂ Molecule',
            description: 'Variational Quantum Eigensolver for molecular simulation',
            difficulty: 'advanced',
            code: `// Variational Quantum Eigensolver (VQE)
// Find ground state energy of H₂ molecule

// Define H₂ molecule
molecule h2 {
    atoms: [
        ["H", [0.0, 0.0, 0.0]],
        ["H", [0.0, 0.0, 0.74]]  // Angstroms
    ]
    basis: "sto-3g"
    charge: 0
    multiplicity: 1
}

// Molecular Hamiltonian (simplified 2-qubit representation)
hamiltonian h2_hamiltonian {
    // H = c₀I + c₁Z₀ + c₂Z₁ + c₃Z₀Z₁ + c₄X₀X₁ + c₅Y₀Y₁
    terms: [
        {coeff: -1.0523, operator: "II"},
        {coeff:  0.3979, operator: "ZI"},
        {coeff: -0.3979, operator: "IZ"},
        {coeff: -0.0113, operator: "ZZ"},
        {coeff:  0.1809, operator: "XX"},
        {coeff:  0.1809, operator: "YY"}
    ]
}

// Hardware-efficient ansatz circuit
circuit vqe_ansatz(theta[4]) {
    qubit q0 = |0⟩
    qubit q1 = |0⟩
    
    // Layer 1: Single-qubit rotations
    RY(theta[0])[q0]
    RY(theta[1])[q1]
    
    // Entangling layer
    CNOT[q0, q1]
    
    // Layer 2: More rotations
    RY(theta[2])[q0]
    RY(theta[3])[q1]
    
    return [q0, q1]
}

// Cost function: expectation value of Hamiltonian
function compute_energy(theta) {
    energy = 0.0
    
    for term in h2_hamiltonian.terms:
        // Prepare quantum state
        qubits = vqe_ansatz(theta)
        
        // Measure in appropriate basis
        if term.operator == "XX":
            RY(-π/2)[qubits[0]]
            RY(-π/2)[qubits[1]]
        elif term.operator == "YY":
            RX(π/2)[qubits[0]]
            RX(π/2)[qubits[1]]
        // ZZ and II need no basis change
        
        // Measure and get expectation
        expectation = measure_expectation(qubits, term.operator)
        energy += term.coeff * expectation
    
    return energy
}

// VQE optimization loop
vqe_optimization {
    // Initial parameters (random)
    theta = [0.0, 0.0, 0.0, 0.0]
    
    optimizer = "COBYLA"
    max_iterations = 100
    tolerance = 1e-6
    
    print("Starting VQE optimization...")
    print("Iter  Energy (Hartree)  Convergence")
    print("-" * 40)
    
    for iteration in range(max_iterations):
        // Compute energy
        current_energy = compute_energy(theta)
        
        // Compute gradients (parameter shift rule)
        gradients = []
        for i in range(4):
            theta_plus = theta.copy()
            theta_plus[i] += π/4
            energy_plus = compute_energy(theta_plus)
            
            theta_minus = theta.copy()
            theta_minus[i] -= π/4
            energy_minus = compute_energy(theta_minus)
            
            gradient = (energy_plus - energy_minus) / 2
            gradients.append(gradient)
        
        // Update parameters
        learning_rate = 0.1
        theta -= learning_rate * gradients
        
        // Check convergence
        if iteration % 10 == 0:
            print(f"{iteration:4d}  {current_energy:14.6f}  {max(abs(g) for g in gradients):.6f}")
        
        if max(abs(g) for g in gradients) < tolerance:
            print(f"\\nConverged at iteration {iteration}")
            break
    }
    
    return current_energy, theta
}

// Run VQE
ground_state_energy, optimal_params = run vqe_optimization on simulator {
    shots: 8192
    noise_model: none  // Ideal simulation
}

print(f"\\nRESULTS:")
print(f"VQE Ground State Energy: {ground_state_energy:.6f} Hartree")
print(f"Exact Energy (classical): -1.137270 Hartree")
print(f"Error: {abs(ground_state_energy - (-1.137270)):.6f} Hartree")
print(f"Chemical Accuracy: < 0.0016 Hartree")
print(f"\\nOptimal parameters: {optimal_params}")
print(f"Circuit depth: {calculate_circuit_depth(vqe_ansatz)}")`
        },
        {
            id: 'quantum-teleportation',
            title: 'Quantum Teleportation',
            description: 'Transfer quantum state without moving particles',
            difficulty: 'intermediate',
            code: `// Quantum Teleportation Protocol
// Transfer unknown quantum state using entanglement + classical bits

// The quantum state to teleport (unknown to us)
qubit mystery = 0.6|0⟩ + 0.8|1⟩  // Some arbitrary quantum state

print("Quantum Teleportation Protocol")
print("==============================")
print(f"Mystery state to teleport: {mystery}")

// Step 1: Create entangled pair (Bell state)
circuit create_entangled_pair() {
    qubit epr_a = |0⟩  // Alice's half
    qubit epr_b = |0⟩  // Bob's half
    
    H[epr_a]
    CNOT[epr_a, epr_b]
    
    print("✓ Entangled pair created and distributed")
    
    return [epr_a, epr_b]
}

// Step 2: Bell measurement by Alice
circuit bell_measurement(mystery_qubit, epr_half) {
    // Entangle mystery qubit with EPR half
    CNOT[mystery_qubit, epr_half]
    H[mystery_qubit]
    
    // Measure both qubits
    measure mystery_qubit -> bit1
    measure epr_half -> bit2
    
    print(f"✓ Alice's measurement: {bit1}{bit2}")
    
    return [bit1, bit2]
}

// Step 3: Bob applies corrections
circuit apply_corrections(bob_qubit, classical_bits) {
    bit1, bit2 = classical_bits
    
    // Apply corrections based on classical bits
    if bit2 == 1:
        X[bob_qubit]  // Bit flip
        print("  Applied X gate")
    
    if bit1 == 1:
        Z[bob_qubit]  // Phase flip
        print("  Applied Z gate")
    
    return bob_qubit
}

// Main teleportation protocol
circuit teleportation_protocol() {
    print("\\nSTEP 1: Entanglement Distribution")
    [alice_epr, bob_epr] = create_entangled_pair()
    
    print("\\nSTEP 2: Alice performs Bell measurement")
    classical_bits = bell_measurement(mystery, alice_epr)
    
    print("\\nSTEP 3: Send classical bits to Bob")
    print(f"  Classical channel: {classical_bits[0]}{classical_bits[1]}")
    
    print("\\nSTEP 4: Bob applies corrections")
    bob_final = apply_corrections(bob_epr, classical_bits)
    
    return bob_final
}

// Run the protocol
bob_state = run teleportation_protocol() on simulator {
    shots: 1  // Single shot for demonstration
}

// Verify teleportation
print("\\n" + "="*40)
print("VERIFICATION:")
print(f"Original state: {mystery}")
print(f"Bob's state:    {bob_state}")

fidelity = calculate_fidelity(mystery, bob_state)
print(f"\\nTeleportation fidelity: {fidelity:.4f}")
print(f"Perfect fidelity = 1.0000")

// Statistical verification with multiple runs
print("\\nStatistical Verification (1000 runs):")
run teleportation_protocol() on simulator {
    shots: 1000
    measure_fidelity: true
}

print(f"Average fidelity: {average_fidelity:.4f}")
print(f"Success rate: {success_rate:.1%}")`
        }
    ],
    
    'quantum-net': [
        {
            id: 'basic-network',
            title: 'Basic Quantum Network',
            description: 'Create a simple quantum network',
            difficulty: 'beginner',
            code: `// Basic Quantum Network Setup
// Create a 3-node quantum network with quantum channels

// Define network topology
network quantum_triangle {
    // Network nodes (quantum computers)
    nodes: ["Alice", "Bob", "Charlie"]
    
    // Quantum channels between nodes
    quantum_channel Alice <-> Bob {
        distance: 50         // km
        fidelity: 0.95      // Channel quality
        capacity: 1000      // Qubits/second
    }
    
    quantum_channel Bob <-> Charlie {
        distance: 75
        fidelity: 0.92
        capacity: 800
    }
    
    quantum_channel Charlie <-> Alice {
        distance: 60
        fidelity: 0.93
        capacity: 900
    }
}

print("Quantum Network Created:")
print(f"Nodes: {quantum_triangle.nodes}")
print(f"Total channels: {quantum_triangle.num_channels}")
print(f"Network diameter: {quantum_triangle.diameter} km")

// Test network connectivity
connectivity_test {
    for source in quantum_triangle.nodes:
        for target in quantum_triangle.nodes:
            if source != target:
                path = find_quantum_path(source, target)
                fidelity = calculate_path_fidelity(path)
                
                print(f"\\n{source} -> {target}:")
                print(f"  Path: {' -> '.join(path)}")
                print(f"  End-to-end fidelity: {fidelity:.3f}")
}

// Distribute entanglement across network
entanglement_distribution {
    // Generate Bell pairs at each link
    for channel in quantum_triangle.channels:
        bell_pairs = generate_bell_pairs(
            count=10,
            fidelity=channel.fidelity
        )
        
        distribute bell_pairs via channel
        
        print(f"\\nDistributed {len(bell_pairs)} Bell pairs")
        print(f"  Link: {channel.source} <-> {channel.target}")
        print(f"  Average fidelity: {average_fidelity(bell_pairs):.3f}")
}

// Network statistics
print("\\nNetwork Statistics:")
print(f"Total entanglement distributed: {total_bell_pairs} pairs")
print(f"Network efficiency: {network_efficiency:.1%}")
print(f"Average link fidelity: {avg_link_fidelity:.3f}")`
        },
        {
            id: 'qkd-bb84',
            title: 'BB84 Quantum Key Distribution',
            description: 'Secure key distribution using quantum mechanics',
            difficulty: 'intermediate',
            code: `// BB84 Quantum Key Distribution Protocol
// Generate secure encryption keys using quantum mechanics

protocol BB84_QKD {
    participants: ["Alice", "Bob"]
    key_length: 256  // Target key length in bits
    
    print("BB84 Quantum Key Distribution")
    print("="*40)
    
    // STEP 1: Alice prepares random qubits
    alice_preparation {
        alice_bits = generate_random_bits(key_length * 4)  // Oversample
        alice_bases = generate_random_bases(key_length * 4)  // + or ×
        
        alice_qubits = []
        for i in range(len(alice_bits)):
            qubit q = |0⟩
            
            // Encode bit
            if alice_bits[i] == 1:
                X[q]  // |0⟩ -> |1⟩
            
            // Choose basis
            if alice_bases[i] == "×":
                H[q]  // Rotate to × basis
            
            alice_qubits.append(q)
        
        print(f"Alice prepared {len(alice_qubits)} qubits")
        
        // Send qubits through quantum channel
        send alice_qubits to Bob via quantum_channel
    }
    
    // STEP 2: Bob measures qubits
    bob_measurement {
        bob_bases = generate_random_bases(len(alice_qubits))  // Random bases
        bob_results = []
        
        for i, qubit in enumerate(received_qubits):
            // Choose measurement basis
            if bob_bases[i] == "×":
                H[qubit]  // Rotate to × basis
            
            // Measure
            measure qubit -> result
            bob_results.append(result)
        
        print(f"Bob measured {len(bob_results)} qubits")
    }
    
    // STEP 3: Basis reconciliation (public channel)
    basis_reconciliation {
        // Alice and Bob share their basis choices publicly
        send alice_bases to Bob via classical_channel
        send bob_bases to Alice via classical_channel
        
        // Keep only matching bases
        matching_indices = []
        for i in range(len(alice_bases)):
            if alice_bases[i] == bob_bases[i]:
                matching_indices.append(i)
        
        print(f"\\nBasis reconciliation:")
        print(f"  Matching bases: {len(matching_indices)}/{len(alice_bases)}")
        
        // Extract sifted key
        alice_sifted = [alice_bits[i] for i in matching_indices]
        bob_sifted = [bob_results[i] for i in matching_indices]
        
        print(f"  Sifted key length: {len(alice_sifted)} bits")
    }
    
    // STEP 4: Error estimation (check for eavesdropping)
    error_estimation {
        // Publicly compare subset of bits
        sample_size = len(alice_sifted) // 4
        sample_indices = random_sample(range(len(alice_sifted)), sample_size)
        
        errors = 0
        for i in sample_indices:
            send alice_sifted[i] to Bob via classical_channel
            if alice_sifted[i] != bob_sifted[i]:
                errors += 1
        
        error_rate = errors / sample_size
        print(f"\\nError estimation:")
        print(f"  Sample size: {sample_size} bits")
        print(f"  Errors found: {errors}")
        print(f"  Error rate: {error_rate:.2%}")
        
        // Check threshold (11% for BB84)
        if error_rate > 0.11:
            print("  ⚠️ HIGH ERROR RATE - Possible eavesdropping!")
            abort protocol
        else:
            print("  ✓ Error rate acceptable - Channel secure")
        
        // Remove tested bits from key
        for i in sorted(sample_indices, reverse=True):
            del alice_sifted[i]
            del bob_sifted[i]
    }
    
    // STEP 5: Error correction
    error_correction {
        // Use CASCADE or LDPC for error correction
        print(f"\\nError correction:")
        
        // Simplified parity check
        parity_blocks = divide_into_blocks(alice_sifted, block_size=8)
        
        for block in parity_blocks:
            alice_parity = sum(block) % 2
            send alice_parity to Bob via classical_channel
            
            // Bob checks and corrects
            bob_block = corresponding_block(bob_sifted)
            bob_parity = sum(bob_block) % 2
            
            if alice_parity != bob_parity:
                // Binary search to find error
                correct_error(bob_block)
        
        print(f"  Corrected {total_corrections} errors")
    }
    
    // STEP 6: Privacy amplification
    privacy_amplification {
        // Reduce key to remove Eve's information
        print(f"\\nPrivacy amplification:")
        
        // Calculate how much to compress
        eve_information = estimate_eve_information(error_rate)
        final_length = len(alice_sifted) - eve_information - safety_margin
        
        // Apply universal hash function
        final_key = universal_hash(alice_sifted, final_length)
        
        print(f"  Initial key: {len(alice_sifted)} bits")
        print(f"  Final secure key: {final_length} bits")
        print(f"  Compression ratio: {final_length/len(alice_sifted):.1%}")
    }
    
    return final_key
}

// Run the protocol
secure_key = run BB84_QKD between Alice and Bob

print("\\n" + "="*40)
print("QKD PROTOCOL COMPLETE")
print(f"Secure key generated: {len(secure_key)} bits")
print(f"Key sample (first 32 bits): {secure_key[:32]}")
print(f"Theoretical security: Information-theoretic")
print(f"Can now use key for one-time pad encryption")`
        },
        {
            id: 'distributed-quantum',
            title: 'Distributed Quantum Computing',
            description: 'Run quantum algorithms across network',
            difficulty: 'advanced',
            code: `// Distributed Quantum Computing
// Execute quantum algorithms across multiple nodes

network quantum_cloud {
    nodes: [
        {name: "QNode-1", qubits: 20, type: "superconducting"},
        {name: "QNode-2", qubits: 16, type: "ion_trap"},
        {name: "QNode-3", qubits: 12, type: "photonic"}
    ]
    
    topology: "star"  // Central coordinator
    coordinator: "QNode-1"
}

// Distributed Grover's algorithm
distributed_algorithm distributed_grover {
    problem_size: 256  // Search space of 2^8
    target_item: 173   // Item we're searching for
    
    print("Distributed Grover's Search")
    print("="*40)
    print(f"Search space: {problem_size} items")
    print(f"Nodes available: {quantum_cloud.nodes}")
    
    // Partition search space
    partition_strategy {
        partitions = []
        items_per_node = problem_size / len(quantum_cloud.nodes)
        
        for i, node in enumerate(quantum_cloud.nodes):
            start = i * items_per_node
            end = (i + 1) * items_per_node
            
            partitions.append({
                node: node.name,
                range: [start, end],
                qubits_needed: log2(items_per_node)
            })
            
            print(f"\\n{node.name}:")
            print(f"  Search range: [{start}, {end})")
            print(f"  Qubits needed: {log2(items_per_node)}")
        
        return partitions
    }
    
    // Execute on each node
    parallel distributed_execution {
        partition: partitions
        
        // Local Grover's search
        local_result = run_local_grover(
            node=partition.node,
            search_range=partition.range,
            target=target_item
        )
        
        // Check if found locally
        if local_result.found:
            print(f"✓ {partition.node} found item at index {local_result.index}")
            
            // Notify other nodes to stop
            broadcast stop_signal to quantum_cloud.nodes
            
            return local_result.index
        else:
            print(f"  {partition.node}: Not found in local partition")
        
        emit local_result
    }
    
    // Aggregate results
    aggregation {
        all_results = collect(distributed_execution.results)
        
        for result in all_results:
            if result.found:
                global_index = result.partition_offset + result.local_index
                
                print(f"\\nSUCCESS!")
                print(f"Item found at global index: {global_index}")
                print(f"Found by node: {result.node}")
                print(f"Total iterations: {result.iterations}")
                
                return global_index
        
        print("\\nItem not found in search space")
        return null
    }
}

// Distributed VQE for large molecules
distributed_algorithm distributed_vqe {
    molecule: "caffeine"  // C₈H₁₀N₄O₂
    qubits_required: 40   // Too large for single quantum computer
    
    print("\\nDistributed VQE for Caffeine")
    print("="*40)
    
    // Fragment molecule for distributed computation
    fragmentation {
        fragments = fragment_molecule(molecule, method="DMET")
        
        print(f"Molecule fragmented into {len(fragments)} parts:")
        for i, fragment in enumerate(fragments):
            print(f"  Fragment {i}: {fragment.atoms} ({fragment.qubits} qubits)")
        
        // Assign fragments to nodes
        assignments = assign_fragments_to_nodes(fragments, quantum_cloud.nodes)
        
        return assignments
    }
    
    // Distributed VQE execution
    vqe_execution {
        iteration = 0
        converged = false
        energy = 0.0
        
        while not converged and iteration < 100:
            // Compute local energies
            local_energies = []
            
            parallel fragment_computation {
                assignment: assignments
                
                // Run VQE on fragment
                fragment_energy = compute_fragment_vqe(
                    fragment=assignment.fragment,
                    node=assignment.node,
                    parameters=current_parameters
                )
                
                // Share quantum correlations
                correlations = extract_quantum_correlations(fragment)
                
                teleport correlations to coordinator
                
                emit fragment_energy
            }
            
            // Combine fragment energies
            total_energy = combine_fragment_energies(
                local_energies,
                correlation_corrections
            )
            
            print(f"Iteration {iteration}: E = {total_energy:.6f} Hartree")
            
            // Check convergence
            if abs(total_energy - previous_energy) < 1e-6:
                converged = true
            
            // Update parameters
            gradients = compute_distributed_gradients()
            current_parameters = update_parameters(gradients)
            
            iteration += 1
        }
        
        return total_energy
    }
}

// Network performance monitoring
monitor network_performance {
    metrics = {
        "total_qubits": sum(node.qubits for node in quantum_cloud.nodes),
        "entanglement_distributed": count_bell_pairs(),
        "fidelity_average": average_fidelity(),
        "computation_speedup": distributed_time / sequential_time
    }
    
    print("\\nNetwork Performance Metrics:")
    print(f"Total quantum capacity: {metrics.total_qubits} qubits")
    print(f"Entanglement resources: {metrics.entanglement_distributed} pairs")
    print(f"Average fidelity: {metrics.fidelity_average:.3f}")
    print(f"Speedup vs single node: {metrics.computation_speedup:.2f}x")
}

// Execute distributed algorithms
run distributed_grover on quantum_cloud
run distributed_vqe on quantum_cloud
run network_performance`
        }
    ]
};