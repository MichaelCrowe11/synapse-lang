# Synapse Programming Language

[![PyPI version](https://badge.fury.io/py/synapse-lang.svg)](https://badge.fury.io/py/synapse-lang)
[![Python Versions](https://img.shields.io/pypi/pyversions/synapse-lang.svg)](https://pypi.org/project/synapse-lang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/michaelcrowe/synapse-lang/workflows/CI/badge.svg)](https://github.com/michaelcrowe/synapse-lang/actions)
[![codecov](https://codecov.io/gh/michaelcrowe/synapse-lang/branch/main/graph/badge.svg)](https://codecov.io/gh/michaelcrowe/synapse-lang)
[![Documentation Status](https://readthedocs.org/projects/synapse-lang/badge/?version=latest)](https://synapse-lang.readthedocs.io/en/latest/?badge=latest)

**Synapse** is a revolutionary programming language designed for scientific computing, featuring native support for parallel execution, uncertainty quantification, and quantum computing paradigms.

## 🚀 Key Features

- **🔀 Parallel Execution**: Native parallel branches and thought streams
- **📊 Uncertainty Quantification**: Built-in uncertainty propagation in calculations
- **🧠 Scientific Reasoning**: Hypothesis-driven programming with reasoning chains
- **⚛️ Quantum Computing**: Integrated quantum simulation and algorithms
- **🔢 Tensor Operations**: GPU-accelerated tensor computations
- **🎯 JIT Compilation**: Optional just-in-time compilation for performance
- **📐 Symbolic Mathematics**: Computer algebra system integration

## 📦 Installation

### Basic Installation

```bash
pip install synapse-lang
```

### With Optional Features

```bash
# With JIT compilation support
pip install synapse-lang[jit]

# With quantum computing features
pip install synapse-lang[quantum]

# With GPU acceleration (requires CUDA)
pip install synapse-lang[gpu]

# All features
pip install synapse-lang[all]
```

## 🎯 Quick Start

### Hello World

```python
import synapse_lang as syn

code = """
print("Hello from Synapse!")
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""

syn.execute(code)
```

### Uncertainty Propagation

```python
code = """
# Measurements with uncertainty
uncertain mass = 10.0 ± 0.1
uncertain velocity = 25.0 ± 0.5

# Automatic error propagation
momentum = mass * velocity
energy = 0.5 * mass * velocity * velocity

print(f"Momentum: {momentum}")
print(f"Energy: {energy}")
"""

syn.execute(code)
```

### Parallel Execution

```python
code = """
parallel {
    branch calc1: {
        result1 = expensive_computation_1()
    }
    branch calc2: {
        result2 = expensive_computation_2()
    }
    branch calc3: {
        result3 = expensive_computation_3()
    }
}

# Results available after parallel execution
final = synthesize(result1, result2, result3)
"""

syn.execute(code)
```

### Scientific Reasoning

```python
code = """
hypothesis QuantumTunneling {
    assume: particle_energy < barrier_height
    predict: transmission_probability > 0
    validate: experimental_observation
}

reason chain WaveParticle {
    premise P1: "Light exhibits interference"
    premise P2: "Light exhibits photoelectric effect"
    
    derive D1 from P1: "Light has wave properties"
    derive D2 from P2: "Light has particle properties"
    
    conclude: D1 && D2 => "Light has wave-particle duality"
}
"""

syn.execute(code)
```

## 🔧 Advanced Usage

### Using the REPL

```bash
# Start interactive REPL
synapse-repl

Synapse Language REPL v1.0.0
Type 'help' for commands, 'exit' to quit

>>> x = 10
>>> y = 20
>>> x + y
30

>>> uncertain measurement = 5.0 ± 0.1
>>> measurement * 2
10.0 ± 0.2
```

### Python API

```python
from synapse_lang import SynapseInterpreter, OptimizedInterpreter

# Basic interpreter
interp = SynapseInterpreter()
result = interp.interpret("2 + 2")

# Optimized interpreter with caching and JIT
opt_interp = OptimizedInterpreter(enable_jit=True)
result = opt_interp.run("complex_calculation()")
```

### Running Benchmarks

```bash
# Run performance benchmarks
synapse-bench --program examples/quantum_simulation.syn --repeats 5
```

## 🏗️ Language Constructs

### Data Types

- **Primitives**: `Real`, `Complex`, `Boolean`, `String`
- **Uncertain**: Values with associated uncertainty
- **Tensors**: Multi-dimensional arrays with GPU support
- **Quantum**: Quantum states and operators
- **Symbolic**: Symbolic mathematical expressions

### Control Flow

- **Parallel Blocks**: Concurrent execution branches
- **Experiments**: Scientific experiment protocols
- **Pipelines**: Data processing pipelines
- **Reasoning Chains**: Logical inference chains

### Special Features

- **Automatic Differentiation**: Gradient computation
- **Constraint Solving**: Declarative constraints
- **Pattern Matching**: Structural pattern matching
- **Lazy Evaluation**: Deferred computation

## 📈 Performance

Synapse offers multiple optimization levels:

- **Interpreted Mode**: Direct AST interpretation
- **Cached Mode**: Memoized computations and AST caching
- **JIT Mode**: Numba-accelerated execution
- **GPU Mode**: CUDA/ROCm acceleration for tensors

Benchmarks show 5-10x speedup with optimization enabled, and up to 100x with GPU acceleration for tensor operations.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/michaelcrowe/synapse-lang/blob/main/CONTRIBUTING.md) for details.

```bash
# Clone the repository
git clone https://github.com/michaelcrowe/synapse-lang.git
cd synapse-lang

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
black synapse_lang/
ruff check synapse_lang/
```

## 📚 Documentation

- [Full Documentation](https://synapse-lang.readthedocs.io)
- [Language Specification](https://github.com/michaelcrowe/synapse-lang/blob/main/LANGUAGE_SPEC.md)
- [API Reference](https://synapse-lang.readthedocs.io/api)
- [Examples](https://github.com/michaelcrowe/synapse-lang/tree/main/examples)

## 🎓 Examples

The `examples/` directory contains comprehensive examples:

- `quantum_simulation.syn` - Quantum mechanics simulations
- `climate_model.syn` - Climate modeling with uncertainty
- `drug_discovery.syn` - Molecular simulation pipeline
- `machine_learning.syn` - ML model training with hyperparameter optimization

## 📄 License

Synapse is available under the MIT License. See [LICENSE](https://github.com/michaelcrowe/synapse-lang/blob/main/LICENSE) for details.

## 🙏 Acknowledgments

Special thanks to all contributors and the scientific computing community for feedback and support.

## 📮 Contact

- **Author**: Michael Benjamin Crowe
- **Email**: michael@synapse-lang.com
- **Website**: [https://synapse-lang.com](https://synapse-lang.com)
- **GitHub**: [@michaelcrowe](https://github.com/michaelcrowe)

## 🗺️ Roadmap

- [ ] WebAssembly compilation for browser execution
- [ ] Distributed computing support (MPI/Ray)
- [ ] Direct quantum hardware integration
- [ ] Visual programming interface
- [ ] Language server protocol (LSP) implementation

---

**Created with ❤️ for the scientific computing community**