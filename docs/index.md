# Synapse Language

## Quantum-Enhanced Programming for Scientific Computing

Welcome to **Synapse**, a revolutionary programming language designed for the next generation of scientific computing. Synapse seamlessly integrates quantum computing, uncertainty quantification, and parallel processing into an intuitive syntax designed for researchers and scientists.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    Install Synapse and write your first quantum-enhanced program in minutes

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-atom:{ .lg .middle } **Quantum Computing**

    ---

    Build quantum circuits and algorithms with native language support

    [:octicons-arrow-right-24: Quantum Guide](quantum/basics.md)

-   :material-chart-bell-curve:{ .lg .middle } **Uncertainty Quantification**

    ---

    Propagate uncertainties through complex calculations automatically

    [:octicons-arrow-right-24: Learn More](scientific/uncertainty.md)

-   :material-cpu-64-bit:{ .lg .middle } **Parallel Processing**

    ---

    Express parallel computations naturally with built-in constructs

    [:octicons-arrow-right-24: Parallel Guide](language/parallel.md)

</div>

## Why Synapse?

### 🚀 Built for Science

Synapse is designed from the ground up for scientific computing, with first-class support for:

- **Hypothesis Testing**: Express and validate scientific hypotheses directly in code
- **Experimental Design**: Define and run experiments with automatic parallelization
- **Uncertainty Propagation**: Track measurement uncertainties through calculations
- **Symbolic Mathematics**: Seamlessly mix symbolic and numeric computation

### ⚛️ Quantum-Native

Quantum computing is not an afterthought—it's built into the language:

```synapse
quantum circuit bell_state(2) {
    H(0)
    CNOT(0, 1)
    measure(0, 1)
}

result = run bell_state with shots: 1000
```

### 🔬 Real-World Applications

Synapse is already being used for:

- **Drug Discovery**: Molecular dynamics and quantum chemistry
- **Climate Modeling**: Large-scale simulations with uncertainty quantification
- **Financial Modeling**: Risk analysis with quantum algorithms
- **Machine Learning**: Quantum-enhanced neural networks

## Quick Example

Here's a complete Synapse program that demonstrates key features:

```synapse
# Scientific hypothesis testing with uncertainty
hypothesis water_phase {
    assume: temperature > 273.15 ± 0.5  # Kelvin with uncertainty
    predict: phase == "liquid"
    validate: experimental_data
}

# Parallel experimental execution
experiment measure_properties {
    setup: initialize_conditions()
    
    parallel {
        branch density: measure_density()
        branch viscosity: measure_viscosity()
        branch heat_capacity: measure_heat_capacity()
    }
    
    synthesize: analyze_results(density, viscosity, heat_capacity)
}

# Quantum algorithm for optimization
quantum algorithm QAOA {
    parameters: [gamma, beta]
    ansatz: hardware_efficient
    cost: expectation_value(H)
    optimizer: COBYLA
}

# Run everything with automatic optimization
results = run experiment with quantum acceleration
```

## Key Features

### 🧠 Intelligent Type System
- Automatic type inference
- Uncertainty-aware types
- Tensor dimensions tracking
- Quantum state types

### ⚡ High Performance
- JIT compilation with Numba
- GPU acceleration
- Distributed computing
- Quantum hardware integration

### 🛡️ Security First
- Sandboxed execution
- Resource limits
- Access controls
- Audit logging

### 🔧 Developer Friendly
- VS Code extension
- Jupyter integration
- Interactive REPL
- Rich debugging tools

## Installation

Install Synapse using pip:

```bash
pip install synapse-lang
```

Or using conda:

```bash
conda install -c synapse synapse-lang
```

For quantum features, install with extras:

```bash
pip install synapse-lang[quantum,ml,scientific]
```

## Next Steps

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } **Read the Tutorial**

    ---

    Learn Synapse step-by-step with our comprehensive tutorial

    [:octicons-arrow-right-24: Start Tutorial](getting-started/quickstart.md)

-   :material-flask:{ .lg .middle } **Explore Examples**

    ---

    See real-world applications and code samples

    [:octicons-arrow-right-24: View Examples](examples/scientific.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete API documentation with examples

    [:octicons-arrow-right-24: API Docs](api/core.md)

-   :material-account-group:{ .lg .middle } **Join Community**

    ---

    Connect with other Synapse developers

    [:octicons-arrow-right-24: Discord](https://discord.gg/synapse-lang)

</div>

## Latest News

!!! tip "Version 2.0 Released!"
    Major update with enhanced parser, JIT compilation, and security sandboxing.
    [Read the changelog →](https://github.com/MichaelCrowe11/synapse-lang/releases)

!!! info "Upcoming Workshop"
    Join our online workshop on Quantum Computing with Synapse - March 15, 2024
    [Register now →](https://events.synapse-lang.org)

## Contributing

Synapse is open source and welcomes contributions! Whether you're fixing bugs, adding features, or improving documentation, we'd love your help.

[View on GitHub](https://github.com/MichaelCrowe11/synapse-lang){ .md-button .md-button--primary }
[Contributing Guide](development/contributing.md){ .md-button }

---

<center>
Made with ❤️ by the Synapse Community

[GitHub](https://github.com/MichaelCrowe11/synapse-lang) · 
[Discord](https://discord.gg/synapse-lang) · 
[Twitter](https://twitter.com/synapselang)
</center>