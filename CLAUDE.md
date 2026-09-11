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

# Run programs and the REPL (installed CLI from synapse_lang.cli)
synapse <file.syn>                           # Execute a Synapse file
synapse -c 'print(1 + 2)'                    # Run a snippet
synapse --repl                               # Interactive Synapse shell
synapse --version
```

### Publishing & Deployment
Releases are cut by pushing a `v*` tag, which runs `.github/workflows/publish.yml` (full CI matrix,
build, PyPI upload). Companion distributions are built with `python -m build` in
`qubit-flow-package/` and `quantum-net/`. Generated planning, publishing and deployment notes from
earlier passes live on the branch `archive/root-docs-2026-09`, not in the tree. The root scripts,
duplicate implementations and generated directories removed on 2026-09-10 are under
`root-2026-09-10/` on that branch. The root modules that remain (`synapse_interpreter.py`,
`synapse_parser.py`, `synapse_ast.py`, `synapse_repl.py`, `synapse_scientific.py`,
`synapse_jit.py` and their imports) stay because `setup.py` lists them in `py_modules` and
the wheel ships them; the compatibility shims (`qubit_flow_*.py`, `quantum_net_*.py`,
`synapse_qubit_bridge.py`, `synapse_cache.py`, `synapse_tensor_gpu_v2.py`) are imported by
tests, scripts and examples.

## Architecture Overview

### Core Language Implementation

The Synapse language is a domain-specific language for scientific computing with quantum and uncertainty features. The architecture follows a traditional interpreter pattern:

1. **Lexer** (`synapse_lang/synapse_lexer.py`): Tokenizes source code into tokens with special handling for:
   - Uncertainty operators (±)
   - Quantum keywords (quantum, circuit, measure)
   - Scientific operators and parallel constructs

2. **Parser** (multiple implementations under `synapse_lang/`):
   - `parser_enhanced.py` (`EnhancedParser`): the parser `synapse_interpreter.py` imports
   - `synapse_parser.py`, `synapse_parser_enhanced.py`, `synapse_parser_minimal.py`: earlier parsers still covered by tests
   - All handle INDENT/DEDENT tokens for Python-like block syntax

3. **AST** (`synapse_lang/synapse_ast.py`, used by the interpreter; `synapse_ast_enhanced.py` and
   `ast_consolidated.py`, which `synapse_lang/__init__.py` re-exports, also exist): Rich node types including:
   - `QuantumCircuitNode`, `QuantumGateNode` for quantum operations
   - `ParallelNode`, `BranchNode` for parallel execution
   - `UncertainNode` for uncertainty quantification
   - `HypothesisNode`, `ReasonChainNode` for scientific reasoning

4. **Interpreter** (`synapse_lang/synapse_interpreter.py`): Executes AST with:
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