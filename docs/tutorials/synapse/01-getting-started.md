# Getting Started with Synapse Language

Welcome to Synapse Language - the revolutionary programming language designed for scientific computing with built-in uncertainty quantification, parallel execution, and quantum computing support.

## What is Synapse Language?

Synapse Language is designed to solve the fundamental challenges scientists face when working with uncertain measurements, complex reasoning chains, and parallel hypothesis testing. Unlike traditional programming languages, Synapse treats uncertainty as a first-class citizen and enables natural expression of scientific thought processes.

## Installation

```bash
# Install the complete Quantum Trinity
pip install synapse-lang synapse-qubit-flow synapse-quantum-net

# Or just Synapse Language
pip install synapse-lang
```

## Your First Synapse Program

Let's start with a simple example that demonstrates Synapse's unique approach to uncertainty:

```synapse
# hello_science.syn
uncertain temperature = 298.15 ± 2.0  # Kelvin
uncertain pressure = 1.01325 ± 0.001   # bar

# Synapse automatically propagates uncertainty
gas_constant = 8.314  # J/(mol·K)
pv_ratio = pressure / temperature

print("PV/T ratio:", pv_ratio)
print("Uncertainty bounds:", pv_ratio.bounds(0.95))
```

Run your program:
```bash
synapse hello_science.syn
```

Output:
```
PV/T ratio: 0.003398 ± 0.000025
Uncertainty bounds: [0.003349, 0.003447] (95% confidence)
```

## Core Concepts

### 1. Uncertain Values

Synapse treats measurement uncertainty as fundamental to scientific computing:

```synapse
# Different ways to express uncertainty
uncertain mass = 5.4 ± 0.1        # Gaussian uncertainty
uncertain length = 2.3 ± 0.05      # Standard deviation
uncertain voltage = 12.0 ± 0.2     # Measurement error

# Uncertainty propagates through calculations
density = mass / (length^3)
print("Density:", density)  # Automatically includes propagated uncertainty
```

### 2. Parallel Execution

Synapse enables natural parallel hypothesis testing:

```synapse
parallel {
    branch high_temp: {
        temperature = 350.0
        reaction_rate = calculate_arrhenius(temperature)
        result_high = run_simulation(reaction_rate)
    }
    
    branch medium_temp: {
        temperature = 300.0
        reaction_rate = calculate_arrhenius(temperature)
        result_medium = run_simulation(reaction_rate)
    }
    
    branch low_temp: {
        temperature = 250.0
        reaction_rate = calculate_arrhenius(temperature)
        result_low = run_simulation(temperature)
    }
}

# All branches execute simultaneously
compare_results(result_high, result_medium, result_low)
```

### 3. Reasoning Chains

Express logical reasoning directly in code:

```synapse
reason chain HypothesisTest {
    premise P1: "Observed unusual reaction rate"
    premise P2: "Temperature sensor reading 305K ± 3K"
    
    derive D1: "If catalyst contamination, then rate decrease expected"
    derive D2: "If temperature fluctuation, then rate variation expected"
    
    test T1: analyze_catalyst_purity()
    test T2: check_temperature_stability()
    
    conclude: select_most_likely_explanation(T1, T2)
}
```

## Key Features

### Uncertainty Propagation
- **Automatic**: All mathematical operations preserve uncertainty
- **Methods**: Monte Carlo, symbolic differentiation, Bayesian inference
- **Correlation**: Handle correlated measurements correctly

### Parallel Computing
- **Built-in**: Parallel blocks execute automatically
- **Scalable**: From multi-core to distributed clusters
- **Smart**: Automatic load balancing and resource management

### Scientific Reasoning
- **Hypothesis Testing**: Built-in support for scientific method
- **Evidence Integration**: Combine multiple data sources
- **Uncertainty Quantification**: Rigorous statistical foundations

## Next Steps

1. **[Tutorial 2: Uncertainty Quantification](02-uncertainty-quantification.md)** - Deep dive into uncertainty handling
2. **[Tutorial 3: Parallel Computing](03-parallel-computing.md)** - Master parallel execution patterns
3. **[Tutorial 4: Scientific Reasoning](04-scientific-reasoning.md)** - Learn reasoning chains and hypothesis testing
4. **[Tutorial 5: Integration with ML](05-machine-learning.md)** - Combine with machine learning workflows

## Example Applications

- **Experimental Physics**: Analyze measurements with proper error propagation
- **Chemistry**: Model reaction kinetics with uncertain parameters  
- **Climate Science**: Handle measurement uncertainties in climate models
- **Finance**: Risk analysis with uncertainty quantification
- **Engineering**: Design optimization under uncertainty

## Getting Help

- **Documentation**: [https://synapse-lang.com/docs](https://synapse-lang.com/docs)
- **GitHub**: [https://github.com/MichaelCrowe11/synapse-lang](https://github.com/MichaelCrowe11/synapse-lang)
- **Examples**: [Real-world Examples Gallery](../examples/)
- **Community**: Join our [Discord](https://discord.gg/synapse-lang)

Ready to revolutionize your scientific computing? Let's dive deeper! 🚀