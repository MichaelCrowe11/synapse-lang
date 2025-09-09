# Getting Started with Quantum-Net

Welcome to Quantum-Net - the distributed quantum computing and networking language that enables the quantum internet. As part of the Quantum Trinity, Quantum-Net handles quantum communication, distributed quantum computing, and quantum network protocols.

## What is Quantum-Net?

Quantum-Net is designed for the quantum internet era, providing:
- **Quantum Communication Protocols**: Teleportation, QKD, superdense coding
- **Distributed Quantum Computing**: Network-wide quantum algorithms
- **Entanglement Routing**: Optimize quantum network topologies
- **Quantum Internet Stack**: Complete protocol stack for quantum networks
- **Multi-Node Coordination**: Synchronize quantum operations across nodes

## Installation

```bash
# Install the complete Quantum Trinity
pip install synapse-lang synapse-qubit-flow synapse-quantum-net

# Or install just Quantum-Net
pip install synapse-quantum-net

# Install with visualization tools
pip install synapse-quantum-net[visualization]
```

## Your First Quantum Network

Let's create a simple quantum network and perform quantum teleportation:

```quantum-net
# hello_quantum_network.qnet
# Define quantum network nodes
node alice {
    position: [0, 0, 0]
    qubits: 2
    capabilities: ["teleportation", "measurement"]
}

node bob {
    position: [100, 0, 0]  # 100 km away
    qubits: 2  
    capabilities: ["teleportation", "measurement"]
}

# Connect nodes with quantum channel
connect alice <-> bob {
    channel_type: "fiber_optic"
    distance: 100  # km
    fidelity: 0.95
    loss_rate: 0.2  # dB/km
}

# Quantum teleportation protocol
protocol teleportation(sender: alice, receiver: bob) {
    # Step 1: Create entangled pair
    entangled_pair = create_bell_pair()
    send entangled_pair.qubit1 -> alice
    send entangled_pair.qubit2 -> bob
    
    # Step 2: Alice prepares state to teleport
    state_to_teleport = |ψ⟩ = 0.6|0⟩ + 0.8|1⟩
    
    # Step 3: Bell measurement at Alice
    bell_measurement = measure_bell_basis(state_to_teleport, entangled_pair.qubit1)
    
    # Step 4: Send classical information
    classical_message = {
        measurement_x: bell_measurement.x_result,
        measurement_z: bell_measurement.z_result
    }
    send classical_message -> bob
    
    # Step 5: Bob applies correction
    if classical_message.measurement_x == 1:
        X[bob.qubit]
    if classical_message.measurement_z == 1:
        Z[bob.qubit]
        
    # Verify teleportation
    fidelity = verify_state_fidelity(bob.qubit, state_to_teleport)
    return fidelity
}

# Execute teleportation
result = execute teleportation(alice, bob)
print("Teleportation fidelity:", result)
```

Run your program:
```bash
quantum-net hello_quantum_network.qnet
```

Output:
```
Quantum Network Initialized:
- Nodes: 2 (alice, bob)
- Connections: 1 quantum channel
- Network diameter: 1 hop

Executing quantum teleportation...
Bell pair established: ✓
Classical communication: 2 bits sent
Quantum correction applied: ✓

Teleportation fidelity: 0.943
Success rate: 94.3%
```

## Core Concepts

### 1. Network Topology

Define quantum network nodes and connections:

```quantum-net
# Network node definition
node quantum_processor {
    node_id: "lab_quantum_1"
    position: [40.7128, -74.0060, 0]  # NYC coordinates
    
    # Quantum capabilities
    qubits: 20
    coherence_time: 100µs
    gate_fidelity: 0.999
    readout_fidelity: 0.97
    
    # Classical capabilities  
    processing_power: 1e12  # FLOPS
    memory: "32GB"
    
    # Supported protocols
    capabilities: [
        "teleportation",
        "qkd_bb84", 
        "superdense_coding",
        "entanglement_swapping",
        "distributed_grover"
    ]
}

# Quantum repeater node
node quantum_repeater {
    node_id: "repeater_1"
    position: [41.8781, -87.6298, 0]  # Chicago
    
    # Specialized for entanglement distribution
    qubits: 5
    quantum_memory_time: 10ms  # Long coherence for storage
    
    capabilities: [
        "entanglement_swapping",
        "entanglement_purification"
    ]
}
```

### 2. Quantum Channels

Configure quantum communication channels:

```quantum-net
# Fiber optic quantum channel
connect node1 <-> node2 {
    channel_type: "fiber_optic"
    distance: 500  # km
    
    # Channel properties
    fidelity: 0.92
    transmission_rate: 1000  # Hz  
    loss_rate: 0.2  # dB/km
    decoherence_time: 1ms
    
    # Security properties
    security_level: "unconditional"
    eavesdropping_detection: true
}

# Satellite quantum channel  
connect ground_station <-> satellite {
    channel_type: "free_space"
    distance: 400  # km (LEO satellite)
    
    atmospheric_loss: 3  # dB
    beam_divergence: 10µrad
    weather_dependence: true
    
    # Orbital mechanics
    contact_windows: calculate_visibility(ground_station, satellite)
}

# Quantum repeater chain
connect node_a <-> repeater1 <-> repeater2 <-> node_b {
    # Automatic entanglement swapping
    entanglement_swapping: true
    purification_threshold: 0.8
}
```

### 3. Quantum Protocols

Built-in quantum communication protocols:

```quantum-net
# BB84 Quantum Key Distribution
protocol qkd_bb84(alice, bob) {
    key_length: 256  # bits
    
    # Alice prepares random qubits
    alice_bits = random_bits(key_length * 2)  # Extra for sifting
    alice_bases = random_bases(key_length * 2)
    
    quantum_states = prepare_bb84_states(alice_bits, alice_bases)
    send quantum_states -> bob
    
    # Bob measures in random bases
    bob_bases = random_bases(key_length * 2)  
    bob_measurements = measure_states(quantum_states, bob_bases)
    
    # Public basis comparison
    matching_bases = compare_bases(alice_bases, bob_bases)
    sifted_key = extract_matching_bits(alice_bits, bob_measurements, matching_bases)
    
    # Error correction and privacy amplification
    error_rate = estimate_error_rate(sifted_key)
    
    if error_rate < 0.11:  # Security threshold
        secure_key = privacy_amplification(sifted_key)
        return secure_key
    else:
        abort("Channel compromised - error rate too high")
}

# Superdense coding
protocol superdense_coding(sender, receiver, message) {
    # Requires pre-shared entanglement
    entangled_pair = get_shared_entanglement(sender, receiver)
    
    # Encode 2 classical bits into 1 qubit
    if message == "00":
        # Do nothing (I operation)
        pass
    elif message == "01":
        X[sender.qubit]  # Bit flip
    elif message == "10": 
        Z[sender.qubit]  # Phase flip
    elif message == "11":
        Y[sender.qubit]  # Both flips
    
    # Send qubit to receiver
    send sender.qubit -> receiver
    
    # Receiver performs Bell measurement
    decoded_message = bell_measurement(receiver.qubit1, receiver.qubit2)
    return decoded_message
}
```

### 4. Distributed Quantum Computing

Execute quantum algorithms across the network:

```quantum-net
# Distributed Grover search
distributed_algorithm grover_search {
    participants: [node1, node2, node3, node4]
    search_space_size: 1024  # Total items to search
    target_item: 723
    
    # Divide search space among nodes
    local_search_space = search_space_size / len(participants)
    
    # Each node searches its partition in parallel
    parallel {
        for node in participants {
            local_result = node.execute_grover(
                search_space: local_search_space,
                oracle: create_oracle(target_item),
                iterations: optimal_iterations(local_search_space)
            )
        }
    }
    
    # Combine results using quantum amplitude amplification
    global_result = quantum_combine(local_results)
    return global_result
}

# Distributed quantum sensing
distributed_algorithm quantum_sensing {
    participants: [sensor1, sensor2, sensor3]
    parameter_to_sense: magnetic_field
    
    # Create GHZ entanglement across sensors
    ghz_state = create_ghz_state(participants)
    
    # Each sensor performs local sensing
    parallel {
        for sensor in participants {
            local_phase = sensor.sense_parameter(parameter_to_sense)
            apply_phase(local_phase, sensor.qubit)
        }
    }
    
    # Collective measurement for enhanced sensitivity
    measurement = collective_measurement(participants)
    
    # Heisenberg-limited sensitivity: σ ∝ 1/N
    sensitivity_enhancement = sqrt(len(participants))
    estimated_parameter = extract_parameter(measurement, sensitivity_enhancement)
    
    return estimated_parameter
}
```

## Advanced Network Features

### Entanglement Routing

```quantum-net
# Optimal entanglement routing
routing_algorithm shortest_entanglement_path {
    metric: "fidelity_weighted_distance"
    
    # Custom cost function
    edge_cost(node_a, node_b) = {
        distance: physical_distance(node_a, node_b),
        fidelity: channel_fidelity(node_a, node_b),
        availability: entanglement_availability(node_a, node_b)
        
        # Combined cost favors high fidelity, short distance
        return distance / (fidelity^2 * availability)
    }
}

# Dynamic routing with network state
dynamic_routing {
    update_frequency: 100ms
    
    # Adapt to network conditions
    monitor network_state {
        congestion_levels: measure_traffic()
        channel_fidelities: measure_channel_quality()  
        node_availability: check_node_status()
    }
    
    # Reroute if needed
    if network_conditions_changed():
        update_routing_tables()
        reroute_active_connections()
}
```

### Network Security

```quantum-net
# Quantum network security
security_config {
    # Intrusion detection
    eavesdropping_detection: true
    anomaly_threshold: 0.05  # 5% error rate threshold
    
    # Key management
    key_refresh_interval: 3600  # 1 hour
    key_hierarchy: "hierarchical"
    
    # Authentication
    quantum_authentication: true
    classical_fallback: "post_quantum_crypto"
}

# Secure multi-party quantum computation
secure_protocol quantum_millionaires {
    participants: [alice, bob, charlie]
    
    # Each participant encodes their value
    for participant in participants {
        private_value = participant.get_secret_value()
        encoded_state = encode_value(private_value)
        participant.prepare_state(encoded_state)
    }
    
    # Quantum comparison without revealing values
    comparison_circuit = build_comparison_circuit(len(participants))
    result = execute_secure_comparison(comparison_circuit)
    
    # Only the comparison result is revealed, not individual values
    return result.maximum_holder
}
```

### Network Monitoring and Analytics

```quantum-net
# Network performance monitoring
monitor quantum_network {
    metrics: [
        "entanglement_distribution_rate",
        "average_fidelity", 
        "network_connectivity",
        "protocol_success_rates",
        "latency_distribution"
    ]
    
    # Real-time dashboards
    dashboard network_overview {
        update_frequency: 1s
        
        plot entanglement_fidelity vs time
        plot network_throughput vs time
        show active_protocols
        show node_status_map
    }
    
    # Anomaly detection
    anomaly_detection {
        baseline_period: 24h
        sensitivity: 3  # 3-sigma threshold
        
        alert_conditions: [
            "fidelity_drop > 0.05",
            "success_rate < 0.9", 
            "unusual_traffic_patterns"
        ]
    }
}

# Performance optimization
optimization {
    # Automatic parameter tuning
    adaptive_parameters {
        purification_threshold: optimize_for("fidelity")
        routing_weights: optimize_for("latency")
        buffer_sizes: optimize_for("throughput")
    }
    
    # Predictive scaling
    predictive_scaling {
        forecast_horizon: 1h
        scale_triggers: [
            "predicted_congestion > 0.8",
            "demand_spike_detected"
        ]
    }
}
```

## Real-World Applications

### Example 1: Quantum Internet Backbone

```quantum-net
# Continental quantum network
network quantum_internet_backbone {
    # Major cities as quantum nodes
    node new_york {
        position: [40.7128, -74.0060, 0]
        qubits: 100
        role: "major_hub"
    }
    
    node chicago {
        position: [41.8781, -87.6298, 0] 
        qubits: 50
        role: "regional_hub"
    }
    
    node los_angeles {
        position: [34.0522, -118.2437, 0]
        qubits: 100
        role: "major_hub"
    }
    
    # Quantum repeater network
    repeaters: generate_repeater_chain([new_york, chicago, los_angeles])
    
    # High-capacity quantum channels
    connect new_york <-> chicago {
        channel_type: "fiber_optic"
        capacity: 10000  # entangled pairs/second
        redundancy: 3    # Triple redundant paths
    }
    
    # Transcontinental connection
    connect chicago <-> los_angeles {
        channel_type: "hybrid"  # Fiber + satellite backup
        primary: "fiber_optic"
        backup: "satellite"
        automatic_failover: true
    }
}

# Network service: Distributed quantum computing as a service
service distributed_qc_service {
    # Resource allocation
    resource_scheduler {
        algorithms: ["first_fit", "best_fit", "quantum_aware"]
        load_balancing: true
        fault_tolerance: true
    }
    
    # API for quantum computing requests
    api quantum_computation_request {
        circuit: user_quantum_circuit,
        resources: {
            qubits_required: 50,
            circuit_depth: 100, 
            fidelity_requirement: 0.95,
            deadline: 300s
        }
    }
    
    # Automatic resource provisioning
    allocate_resources(quantum_computation_request) {
        available_nodes = find_available_nodes(resources.qubits_required)
        optimal_allocation = optimize_allocation(available_nodes, resources)
        
        return execute_distributed_circuit(
            circuit=circuit,
            allocation=optimal_allocation
        )
    }
}
```

### Example 2: Quantum Sensor Network

```quantum-net
# Distributed quantum sensing for gravitational wave detection
network quantum_gravitational_wave_array {
    # Geographically distributed quantum sensors
    sensor_locations = [
        [46.4512, -119.4078, 0],  # Hanford, WA
        [30.5628, -90.7742, 0],   # Livingston, LA
        [43.6308, 10.5047, 0],    # Virgo, Italy
        [36.4119, 137.3006, 0]   # KAGRA, Japan
    ]
    
    # High-precision quantum sensors
    for location in sensor_locations {
        node quantum_sensor {
            position: location
            sensor_type: "quantum_interferometer"
            sensitivity: 1e-21  # Strain sensitivity
            bandwidth: [10, 1000]  # Hz
            
            capabilities: [
                "distributed_sensing",
                "clock_synchronization",
                "phase_correlation"
            ]
        }
    }
    
    # Quantum clock network for synchronization
    quantum_clock_sync {
        precision: 1e-18  # Fractional frequency stability
        synchronization_protocol: "quantum_clock_distribution"
        
        # Entanglement-enhanced synchronization
        entangled_clock_states: create_multipartite_entanglement(sensor_locations)
    }
}

# Distributed sensing protocol
protocol gravitational_wave_detection {
    participants: all_sensors
    
    # Phase 1: Establish quantum correlations
    multipartite_entanglement = create_spin_squeezed_states(participants)
    
    # Phase 2: Distributed sensing
    parallel {
        for sensor in participants {
            local_phase_shift = sensor.measure_gravitational_strain()
            apply_phase_encoding(local_phase_shift, sensor.entangled_state)
        }
    }
    
    # Phase 3: Collective readout
    collective_measurement = quantum_collective_readout(participants)
    
    # Phase 4: Signal processing
    gravitational_wave_signal = extract_signal(
        measurement=collective_measurement,
        noise_model=detector_noise_model,
        template_bank=gravitational_wave_templates
    )
    
    # Enhanced sensitivity from quantum correlations
    sensitivity_enhancement = calculate_quantum_advantage(multipartite_entanglement)
    
    return {
        signal: gravitational_wave_signal,
        confidence: calculate_detection_confidence(),
        quantum_advantage: sensitivity_enhancement
    }
}
```

### Example 3: Quantum Financial Network

```quantum-net
# Secure quantum financial network
network quantum_financial_network {
    # Financial institutions as quantum nodes
    node central_bank {
        node_id: "fed_reserve"
        security_clearance: "maximum"
        qubits: 200
        
        capabilities: [
            "quantum_digital_signatures",
            "quantum_money_verification", 
            "secure_multiparty_computation"
        ]
    }
    
    node commercial_banks {
        count: 50
        security_clearance: "high"
        qubits: 20
        
        capabilities: [
            "quantum_transactions",
            "quantum_authentication",
            "quantum_audit"
        ]
    }
    
    # Ultra-secure quantum channels
    channel_security {
        encryption: "quantum"
        authentication: "quantum_digital_signatures"
        integrity: "quantum_error_detection"
        
        # Continuous monitoring for eavesdropping
        security_monitoring: continuous
        alert_threshold: 0.01  # 1% error rate
    }
}

# Quantum money protocol
protocol quantum_digital_currency {
    # Quantum money states (unforgeable due to no-cloning theorem)
    quantum_banknote = {
        serial_number: unique_id(),
        quantum_state: random_quantum_state(),
        digital_signature: central_bank.sign(quantum_state)
    }
    
    # Money transfer protocol
    transfer_money(sender, receiver, amount) {
        # Verify sender's quantum banknotes
        verified_notes = verify_quantum_money(sender.banknotes, central_bank.public_key)
        
        if sum(verified_notes.value) >= amount {
            # Quantum transaction
            transaction = create_quantum_transaction(
                sender=sender,
                receiver=receiver, 
                amount=amount,
                banknotes=select_notes(verified_notes, amount)
            )
            
            # Broadcast to network for verification
            broadcast_transaction(transaction)
            
            # Quantum consensus for validation
            consensus_result = quantum_byzantine_agreement(
                participants=all_banks,
                transaction=transaction
            )
            
            if consensus_result.approved:
                # Update quantum ledger
                update_quantum_ledger(transaction)
                return "APPROVED"
            else:
                return "REJECTED"
        } else {
            return "INSUFFICIENT_FUNDS"
        }
    }
}
```

## Best Practices

### 1. Network Design
```quantum-net
# Good: Redundant paths for reliability
network robust_design {
    topology: "mesh"  # Multiple paths between nodes
    redundancy_factor: 3
    
    # Automatic failover
    failover_policy: "immediate"
    backup_channels: "always_available"
}

# Bad: Single point of failure
network fragile_design {
    topology: "star"  # All traffic through central hub
    redundancy_factor: 1  # No backup paths
}
```

### 2. Protocol Selection
```quantum-net
# Choose appropriate protocol for use case
if security_requirement == "unconditional":
    use_protocol("qkd_bb84")  # Information-theoretic security
elif efficiency_requirement == "high":
    use_protocol("superdense_coding")  # 2 bits per qubit
elif distance_requirement == "long":
    use_protocol("quantum_repeaters")  # Extend range
```

### 3. Resource Management
```quantum-net
resource_management {
    # Monitor and optimize resource usage
    entanglement_budget: track_usage()
    
    # Prioritize critical protocols
    priority_queue: [
        "emergency_communications",
        "financial_transactions", 
        "scientific_experiments"
    ]
    
    # Dynamic resource allocation
    adaptive_allocation: true
}
```

## Next Steps

1. **[Tutorial 2: Quantum Communication Protocols](02-quantum-protocols.md)** - Master quantum communication
2. **[Tutorial 3: Distributed Quantum Computing](03-distributed-computing.md)** - Network-wide quantum algorithms
3. **[Tutorial 4: Network Security](04-quantum-security.md)** - Secure quantum communications
4. **[Tutorial 5: Performance Optimization](05-optimization.md)** - Optimize quantum network performance

## Example Applications

- **Quantum Internet**: Global quantum communication infrastructure
- **Distributed Computing**: Network-wide quantum algorithms  
- **Secure Communications**: Quantum key distribution networks
- **Quantum Sensing**: Distributed quantum sensor arrays
- **Financial Networks**: Quantum-secured financial transactions

## Getting Help

- **Documentation**: [Quantum-Net API Reference](../api/quantum-net/)  
- **GitHub**: [https://github.com/MichaelCrowe11/synapse-lang](https://github.com/MichaelCrowe11/synapse-lang)
- **Examples**: [Quantum Networking Examples](../examples/networking/)
- **Community**: [Quantum Networking Forum](https://forum.quantum-trinity.com)

Ready to build the quantum internet? Let's explore quantum communication protocols! 🌐⚛️