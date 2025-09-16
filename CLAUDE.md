# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Commands

### Development & Testing
```bash
# Run tests (from synapse-lang directory)
python -m pytest tests/ -v                    # Run all tests
python -m pytest tests/test_minimal_parser.py # Run specific test file
python -m pytest -k "test_quantum"           # Run tests matching pattern

# Linting and code quality
python -m ruff check . --fix                 # Auto-fix linting issues
python -m ruff check . --statistics          # View linting statistics
python -m bandit -r synapse_lang/            # Security analysis

# Build and install locally
pip install -e .                             # Install in development mode
python setup.py build                        # Build distribution
python -m build                              # Build wheel and source distribution

# Run the REPL
python synapse_repl.py                       # Interactive Synapse shell
python run_synapse.py <file.syn>             # Execute Synapse file
```

### Publishing & Deployment
```bash
# PyPI publishing (requires credentials)
python publish.py                            # Interactive publishing
python publish_all.py                        # Publish all packages

# Google Cloud deployment
./deploy-to-gcp.sh                          # Deploy to GCP App Engine
```

## Architecture Overview

### Core Language Implementation

The Synapse language is a domain-specific language for scientific computing with quantum and uncertainty features. The architecture follows a traditional interpreter pattern:

1. **Lexer** (`synapse_lang/synapse_lexer.py`): Tokenizes source code into tokens with special handling for:
   - Uncertainty operators (±)
   - Quantum keywords (quantum, circuit, measure)
   - Scientific operators and parallel constructs

2. **Parser** (multiple implementations):
   - `synapse_parser_minimal.py`: Lightweight parser for basic constructs
   - `synapse_parser_enhanced.py`: Full-featured parser with all language features
   - Both parsers handle INDENT/DEDENT tokens for Python-like block syntax

3. **AST** (`synapse_ast_enhanced.py`): Rich node types including:
   - `QuantumCircuitNode`, `QuantumGateNode` for quantum operations
   - `ParallelNode`, `BranchNode` for parallel execution
   - `UncertainNode` for uncertainty quantification
   - `HypothesisNode`, `ReasonChainNode` for scientific reasoning

4. **Interpreter** (`synapse_interpreter.py`): Executes AST with:
   - Quantum circuit simulation via optional quantum backends
   - Parallel execution using ThreadPoolExecutor
   - Uncertainty propagation through calculations

### Package Structure

The codebase consists of three integrated languages:

- **synapse_lang/**: Main language implementation with quantum support
- **qubit_flow_lang/**: Low-level quantum circuit language
- **quantum_net_lang/**: Quantum networking protocols

### Key Architectural Patterns

1. **Dual-Mode Execution**:
   - Local interpreter for basic operations
   - Cloud executor for quantum simulations and heavy computation

2. **Parser Indentation Handling**:
   - The parser must handle INDENT/DEDENT tokens for block structures
   - Common issue: Parser expects identifier after INDENT in quantum/parallel blocks
   - Solution: Skip INDENT tokens when parsing block contents

3. **Quantum Integration**:
   - Optional quantum backends (Qiskit, Cirq, PennyLane)
   - Fallback to simulation when hardware unavailable
   - Noise models for realistic quantum simulation

4. **Type System** (`type_system.py`):
   - Primitive types with uncertainty support
   - Quantum types (Qubit, QuantumRegister)
   - Type inference and checking

### Common Parser Issues & Solutions

When modifying the parser, be aware of:

1. **Indentation Sensitivity**: Always handle INDENT/DEDENT tokens in block structures
2. **Forward References**: Use string literals for type hints (e.g., `list["ClassName"]`)
3. **Token Lookahead**: Parser uses single-token lookahead, design grammar accordingly

### Test Structure

- `tests/test_minimal_parser.py`: Core parsing functionality
- `tests/test_quantum_circuits.py`: Quantum-specific features
- `tests/test_comprehensive.py`: Integration and edge cases

Tests often fail on indented block parsing - ensure `skip_newlines()` handles INDENT/DEDENT tokens.

### Dependencies & Extras

The project uses `pyproject.toml` for modern Python packaging with optional dependencies:
- `[gpu]`: CUDA/GPU acceleration
- `[quantum]`: Quantum computing frameworks
- `[cloud]`: Cloud deployment tools
- `[enterprise]`: Enterprise features (Stripe, monitoring)

### Security Considerations

- The codebase has known vulnerabilities tracked by Dependabot
- Run `python -m bandit -r synapse_lang/` to check for security issues
- Avoid executing user code directly without sandboxing

### Mobile App Integration

A companion React Native app exists at `synapse-mobile/` repository for mobile execution of Synapse code. The mobile app connects to the cloud API for quantum simulations.

## Language-Specific Gotchas

1. **Uncertainty Propagation**: The ± operator creates `UncertainValue` objects that automatically propagate uncertainty through calculations

2. **Parallel Blocks**: Use ThreadPoolExecutor with configurable worker count, defaults to min(branches, cpu_count, 8)

3. **Quantum Circuits**: Circuits must specify qubit count upfront, gates are validated against circuit size

4. **Import Structure**: The package uses star imports extensively - be cautious about namespace pollution