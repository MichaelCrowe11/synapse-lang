# Changelog

All notable changes to the Synapse Programming Language will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-01-10

### Added
- Complete parallel computing module with multiprocessing and threading support
- Parameter sweep functionality for scientific computing
- Thought streams for parallel hypothesis testing
- SharedState for thread-safe parallel computations
- Monte Carlo simulation capabilities
- Distributed compute functions
- Backend stubs for Dask, MPI, and Ray integration
- Comprehensive quantum computing demo with working examples
- GaussianProcessUncertainty for ML uncertainty quantification

### Fixed
- Import errors for UncertainValue and parallel modules
- NumPy/SciPy version compatibility issues
- Missing monte_carlo and propagate_uncertainty functions
- Unicode encoding issues in demo files
- Test suite import errors

### Changed
- Updated to NumPy 2.2.6 for compatibility
- Enhanced uncertainty propagation with Monte Carlo support
- Improved parallel execution optimization

## [1.0.0] - 2024-01-07

### 🎉 Initial Release

#### Added
- **Core Language Features**
  - Parallel execution with `parallel` blocks and branches
  - Uncertainty quantification with `uncertain` values and automatic error propagation
  - Scientific reasoning with `hypothesis` and `reason chain` constructs
  - Quantum computing support with quantum states and operators
  - Tensor operations with NumPy backend
  - Symbolic mathematics with SymPy integration

- **Performance Optimizations**
  - Multi-level caching system (AST, computation, result caches)
  - JIT compilation support via Numba (optional)
  - GPU acceleration for tensor operations (CuPy/PyTorch)
  - Optimized interpreter with lazy evaluation
  - Parallel execution with thread pools

- **Developer Tools**
  - Interactive REPL with syntax highlighting
  - Comprehensive test suite
  - Performance benchmarking suite
  - Docker container support
  - VS Code extension (basic)

- **Package Features**
  - PyPI package with extras for gpu, jit, quantum features
  - Comprehensive documentation
  - CI/CD pipeline with GitHub Actions
  - Pre-commit hooks for code quality

#### Language Constructs
- `parallel {...}` - Parallel execution blocks
- `uncertain x = value ± error` - Values with uncertainty
- `hypothesis {...}` - Scientific hypotheses
- `experiment {...}` - Experimental protocols
- `reason chain {...}` - Logical reasoning chains
- `pipeline {...}` - Data processing pipelines
- `tensor[dims]` - Multi-dimensional arrays
- `symbolic {...}` - Symbolic mathematics

#### Examples
- Quantum simulation demonstrations
- Climate modeling with uncertainty
- Drug discovery pipeline
- Machine learning workflows

### Performance
- 5-10x speedup with optimizations enabled
- Up to 100x speedup for GPU-accelerated tensor operations
- Sub-millisecond startup time with cached ASTs

### Known Issues
- Windows readline support requires pyreadline3
- GPU support requires manual CUDA/ROCm setup
- Some quantum features are experimental

### Contributors
- Michael Benjamin Crowe (Author)

---

## [Unreleased]

### Planned Features
- WebAssembly compilation for browser execution
- Distributed computing support (MPI/Ray)
- Direct quantum hardware integration (IBM, Google, IonQ)
- Language Server Protocol (LSP) implementation
- Visual programming interface
- Jupyter kernel support
- Package manager for Synapse libraries
- Advanced debugging tools

### Under Consideration
- Native compilation via LLVM
- Rust-based interpreter core
- Mobile app support
- Cloud-based execution environment
- Integration with popular ML frameworks

---

## Version History

### Pre-release Development
- 2023-12: Initial concept and design
- 2024-01: Core interpreter implementation
- 2024-01: Optimization and enhancement patchsets
- 2024-01: Package preparation and publication

---

## Upgrade Guide

### From Development Versions to 1.0.0

If you were using pre-release development versions:

1. **Update imports**: Change from individual module imports to package imports
   ```python
   # Old
   from synapse_interpreter import SynapseInterpreter
   
   # New
   from synapse_lang import SynapseInterpreter
   ```

2. **Update file extensions**: Use `.syn` for all Synapse source files

3. **Update CLI commands**: Use new entry points
   ```bash
   # Old
   python synapse_repl.py
   
   # New
   synapse-repl
   ```

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/michaelcrowe/synapse-lang/issues
- Email: michael@synapse-lang.com
- Documentation: https://synapse-lang.readthedocs.io