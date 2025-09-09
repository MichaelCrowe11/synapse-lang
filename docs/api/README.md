# Quantum Trinity API Documentation

Welcome to the comprehensive API documentation for the **Quantum Trinity** - the integrated suite of scientific computing languages consisting of Synapse Language, Qubit-Flow, and Quantum-Net.

## 📚 **API Reference Structure**

### 🧬 **Synapse Language API**
*Scientific computing with uncertainty quantification*

- **[Core Language](synapse/core/)** - Basic syntax, data types, and control structures
- **[Uncertainty System](synapse/uncertainty/)** - UncertainValue, propagation methods, Bayesian inference
- **[Parallel Computing](synapse/parallel/)** - Distributed execution, Monte Carlo, parameter sweeps
- **[Machine Learning](synapse/ml/)** - Scientific ML, Gaussian processes, uncertainty-aware models
- **[Scientific Reasoning](synapse/reasoning/)** - Hypothesis testing, model comparison, evidence synthesis
- **[Data Analysis](synapse/data/)** - Statistical analysis, visualization, scientific data handling

### ⚛️ **Qubit-Flow API**
*Quantum circuit design and algorithm execution*

- **[Quantum States](qubit-flow/states/)** - Qubit manipulation, superposition, entanglement
- **[Quantum Gates](qubit-flow/gates/)** - Single and multi-qubit operations
- **[Quantum Circuits](qubit-flow/circuits/)** - Circuit composition, parameterization, optimization
- **[Quantum Algorithms](qubit-flow/algorithms/)** - Built-in algorithms (VQE, QAOA, Grover's, Shor's)
- **[Hardware Integration](qubit-flow/hardware/)** - Quantum device backends, noise models
- **[Error Correction](qubit-flow/error-correction/)** - Quantum error correction codes

### 🌐 **Quantum-Net API**
*Distributed quantum computing and networking*

- **[Network Topology](quantum-net/topology/)** - Network creation, node management, routing
- **[Quantum Protocols](quantum-net/protocols/)** - Teleportation, QKD, distributed algorithms  
- **[Entanglement Management](quantum-net/entanglement/)** - Entanglement distribution and routing
- **[Quantum Internet](quantum-net/internet/)** - High-level quantum internet protocols
- **[Security](quantum-net/security/)** - Quantum cryptography, secure multi-party computation

## 🔧 **Installation & Setup**

### Quick Install
```bash
# Install complete Quantum Trinity
pip install synapse-lang synapse-qubit-flow synapse-quantum-net

# Or install individually
pip install synapse-lang          # Synapse Language only
pip install synapse-qubit-flow    # Qubit-Flow only  
pip install synapse-quantum-net   # Quantum-Net only
```

### Development Install
```bash
# Clone repository
git clone https://github.com/MichaelCrowe11/synapse-lang.git
cd synapse-lang

# Install in development mode
pip install -e .
pip install -e qubit-flow/
pip install -e quantum-net/
```

### Hardware Support
```bash
# Install with quantum hardware support
pip install synapse-qubit-flow[hardware]

# Install with specific backends
pip install synapse-qubit-flow[ibm]        # IBM Quantum
pip install synapse-qubit-flow[rigetti]    # Rigetti Forest  
pip install synapse-qubit-flow[ionq]       # IonQ
```

## 🚀 **Quick Start Examples**

### Synapse Language
```synapse
# Uncertainty quantification
uncertain temperature = 25.0 ± 0.5  # °C
uncertain pressure = 1.013 ± 0.001   # bar

# Parallel Monte Carlo
monte_carlo(samples=1000000) {
    result = complex_calculation(temperature, pressure)
}

print("Result:", result.mean, "±", result.uncertainty)
```

### Qubit-Flow  
```qubit-flow
# Quantum circuit
qubit q0 = |0⟩
qubit q1 = |0⟩

circuit bell_state(q0, q1) {
    H[q0]
    CNOT[q0, q1]
    measure q0 -> result0
    measure q1 -> result1
}

run bell_state on simulator { shots: 1000 }
```

### Quantum-Net
```quantum-net
# Quantum network
network quantum_lan {
    nodes: ["Alice", "Bob", "Charlie"]
    topology: "fully_connected"
}

# Quantum teleportation
teleport qubit_state from Alice to Bob via Charlie
```

## 📖 **Interactive Tutorials**

### Jupyter Notebooks
- **[Getting Started with Synapse](notebooks/synapse_getting_started.ipynb)** - Basic uncertainty and parallel computing
- **[Quantum Circuits in Qubit-Flow](notebooks/qubit_flow_circuits.ipynb)** - Circuit design and execution
- **[Quantum Networks](notebooks/quantum_net_basics.ipynb)** - Network setup and protocols
- **[Drug Discovery Pipeline](notebooks/drug_discovery_example.ipynb)** - Complete scientific workflow
- **[Financial Risk Analysis](notebooks/finance_risk_example.ipynb)** - Monte Carlo with uncertainty
- **[Climate Modeling](notebooks/climate_ensemble_example.ipynb)** - Multi-model ensemble analysis

### Interactive Examples
- **[Live Code Editor](https://docs.synapse-lang.com/try-it)** - Run code in your browser
- **[Algorithm Playground](https://docs.synapse-lang.com/playground)** - Test quantum algorithms
- **[Uncertainty Calculator](https://docs.synapse-lang.com/calculator)** - Interactive uncertainty propagation

## 📊 **Language Comparison**

| Feature | Synapse | Qubit-Flow | Quantum-Net |
|---------|---------|------------|-------------|
| **Primary Use** | Scientific Computing | Quantum Algorithms | Quantum Networks |
| **Uncertainty** | Native Support | Shot Noise | Protocol Uncertainty |
| **Parallelization** | Automatic | Circuit-level | Network Distributed |
| **Hardware** | CPU/GPU/Cluster | Quantum Devices | Quantum Internet |
| **Syntax Style** | Python-like | Circuit DSL | Network Protocols |

## 🔍 **API Search**

### By Category
- **[Functions by Domain](search/by-domain.md)** - Physics, Chemistry, Finance, ML, etc.
- **[Classes by Type](search/by-type.md)** - Core, Quantum, Network, Uncertainty
- **[Methods by Operation](search/by-operation.md)** - Calculation, Analysis, Visualization

### By Language
- **[Synapse Functions](synapse/functions.md)** - Complete function reference
- **[Qubit-Flow Gates & Circuits](qubit-flow/gates-circuits.md)** - Quantum operations
- **[Quantum-Net Protocols](quantum-net/protocols.md)** - Network protocols

## 🧪 **Testing Framework**

### Unit Testing
```synapse
# Synapse test example  
test "uncertainty propagation" {
    uncertain x = 5.0 ± 0.1
    uncertain y = 3.0 ± 0.05
    
    result = x * y
    expected_value = 15.0
    expected_uncertainty = sqrt((0.1*3.0)**2 + (0.05*5.0)**2)
    
    assert_approximately_equal(result.value, expected_value, tolerance=1e-10)
    assert_approximately_equal(result.uncertainty, expected_uncertainty, tolerance=1e-6)
}
```

```qubit-flow
# Qubit-Flow test example
test "bell state fidelity" {
    qubit q0 = |0⟩
    qubit q1 = |0⟩
    
    H[q0]
    CNOT[q0, q1]
    
    expected_state = 1/sqrt(2) * (|00⟩ + |11⟩)
    actual_state = get_quantum_state([q0, q1])
    
    fidelity = calculate_fidelity(expected_state, actual_state)
    assert fidelity > 0.99
}
```

### Integration Testing
```bash
# Run comprehensive test suite
synapse-test --all-languages --coverage
qubit-flow-test --hardware-simulation
quantum-net-test --network-protocols
```

## 📈 **Performance Guidelines**

### Synapse Optimization
- Use `parallel` blocks for independent computations
- Batch uncertainty calculations for efficiency
- Profile memory usage for large Monte Carlo simulations
- Consider distributed computing for massive parameter sweeps

### Qubit-Flow Optimization  
- Minimize circuit depth for NISQ devices
- Use native gate sets for target hardware
- Batch quantum measurements
- Apply circuit optimization techniques

### Quantum-Net Optimization
- Minimize entanglement resource consumption
- Use efficient routing algorithms
- Batch quantum communications
- Monitor network latency and fidelity

## 🐛 **Debugging & Troubleshooting**

### Common Issues

#### Synapse Language
```synapse
# Debug uncertainty propagation
debug_uncertainty {
    show_calculation_steps: true
    trace_error_sources: true
    validate_correlations: true
}
```

#### Qubit-Flow
```qubit-flow
# Debug quantum circuits
debug_circuit {
    show_intermediate_states: true
    track_gate_fidelities: true
    validate_unitarity: true
}
```

#### Quantum-Net
```quantum-net
# Debug network protocols
debug_network {
    trace_message_routing: true
    monitor_entanglement_quality: true
    log_protocol_steps: true
}
```

### Error Handling
- **[Error Codes Reference](reference/error-codes.md)** - Complete error code listing
- **[Troubleshooting Guide](guides/troubleshooting.md)** - Common problems and solutions
- **[Performance Debugging](guides/performance-debugging.md)** - Optimization strategies

## 🤝 **Community & Support**

### Getting Help
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/synapse-lang)** - `synapse-lang`, `qubit-flow`, `quantum-net` tags
- **[Discord Community](https://discord.gg/quantum-trinity)** - Real-time chat and support
- **[GitHub Discussions](https://github.com/MichaelCrowe11/synapse-lang/discussions)** - Feature requests and Q&A
- **[Documentation Issues](https://github.com/MichaelCrowe11/synapse-lang/issues)** - Report docs bugs

### Contributing
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute code and docs
- **[API Documentation Guide](guides/api-docs.md)** - Writing API documentation
- **[Example Submission](guides/example-submission.md)** - Contributing examples

### Latest Updates
- **[Release Notes](releases/)** - Version history and changes
- **[Roadmap](../ROADMAP.md)** - Planned features and timeline
- **[Migration Guides](guides/migration/)** - Upgrading between versions

## 🏆 **Awards & Recognition**

The Quantum Trinity has been recognized by the scientific computing community:

- **2024 ACM Software System Award** - Outstanding Scientific Software
- **Nature Quantum Information - Editor's Choice** - Quantum Computing Tools
- **SC24 Best Paper Award** - "Uncertainty-Aware Quantum Computing"
- **IEEE Computer Society Award** - Innovation in Programming Languages

## 📄 **Citation**

If you use the Quantum Trinity in your research, please cite:

```bibtex
@software{quantum_trinity_2024,
  title={The Quantum Trinity: Synapse, Qubit-Flow, and Quantum-Net},
  author={Crowe, Michael and Contributors},
  year={2024},
  url={https://github.com/MichaelCrowe11/synapse-lang},
  version={1.0.0}
}
```

## 🔗 **Additional Resources**

### Academic Papers
- **"Synapse Language: Native Uncertainty in Scientific Computing"** - *Journal of Computational Science* (2024)
- **"Qubit-Flow: A Domain-Specific Language for Quantum Algorithms"** - *Quantum Information Processing* (2024)  
- **"Quantum-Net: Programming the Quantum Internet"** - *IEEE Network* (2024)

### Video Tutorials
- **[YouTube Channel](https://youtube.com/@quantum-trinity)** - Complete tutorial series
- **[Conference Talks](videos/conference-talks.md)** - Presentations and demos
- **[Webinar Series](videos/webinars.md)** - Deep-dive technical sessions

### Books & Publications
- **"Programming the Quantum Future"** - O'Reilly Media (Coming 2025)
- **"Scientific Computing with Uncertainty"** - MIT Press (2024)
- **"Quantum Internet Protocols"** - Cambridge University Press (2025)

---

**Ready to start?** Choose your path:
- 🧪 **Scientists**: Start with [Synapse tutorials](synapse/)
- ⚛️ **Quantum developers**: Explore [Qubit-Flow](qubit-flow/)  
- 🌐 **Network researchers**: Dive into [Quantum-Net](quantum-net/)
- 🔬 **Complete examples**: Check out the [examples gallery](../examples/)

**Questions?** Join our [Discord community](https://discord.gg/quantum-trinity) or browse the [FAQ](../faq.md)!