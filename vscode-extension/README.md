# Synapse Language Support for Visual Studio Code

This extension provides comprehensive language support for Synapse, a proprietary programming language designed for deep scientific reasoning and parallel thought processing.

## Features

### Core Features
- **Syntax Highlighting**: Full syntax highlighting for `.syn` and `.synapse` files
- **Code Snippets**: 20+ snippets for common patterns (quantum circuits, tensors, pipelines, etc.)
- **Language Configuration**: Auto-closing pairs, comment toggling, and more
- **Custom Theme**: Synapse Dark theme optimized for the language

### Advanced Features (v0.2.0)
- **Language Server Protocol (LSP)**: Full IntelliSense support
- **Auto-Completion**: Context-aware code completion for keywords, functions, and quantum gates
- **Hover Documentation**: Instant documentation on hover
- **Error Diagnostics**: Real-time syntax and semantic error checking
- **Code Formatting**: Automatic code formatting (Shift+Alt+F)
- **Run Support**: Execute Synapse files directly from VS Code (F5)
- **Status Bar Integration**: Version and status information

## Language Overview

Synapse is a next-generation programming language that combines:
- Scientific computing capabilities
- Parallel thought processing
- Uncertainty quantification
- Quantum computing integration
- Advanced tensor operations

## Installation

1. Open Visual Studio Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Synapse Language Support"
4. Click Install

## Usage

### File Extensions
- `.syn` - Synapse source files
- `.synapse` - Alternative extension for Synapse files

### Example Code

```synapse
# Define a quantum computation
quantum circuit QubitProcessor {
    input: |0⟩ ⊗ |0⟩
    gates: [
        H(0),
        CNOT(0, 1),
        measure_all()
    ]
}

# Parallel processing with uncertainty
parallel compute DataAnalysis {
    branches: [
        α -> process_dataset_1(),
        β -> process_dataset_2(),
        γ -> process_dataset_3()
    ]
    merge: weighted_average
    uncertainty: ±0.05
}

# Tensor operations
tensor T = create_tensor([3, 4, 5])
result = T.contract(axis=1).normalize()
```

## Snippets

The extension includes snippets for common patterns:
- `quantum` - Quantum circuit template
- `parallel` - Parallel computation block
- `tensor` - Tensor operation template
- `uncertainty` - Uncertainty quantification block

## Requirements

- Visual Studio Code 1.74.0 or higher

## Known Issues

Please report issues at: https://github.com/MichaelCrowe11/synapse-lang/issues

## Release Notes

### 0.2.0
- Added Language Server Protocol (LSP) support
- Implemented IntelliSense with auto-completion
- Added hover documentation for keywords and functions
- Real-time error diagnostics
- Code formatting support
- Run command (F5) to execute Synapse files
- Status bar integration
- Enhanced snippets library (20+ snippets)
- Improved Synapse Dark theme

### 0.1.0
- Initial release
- Basic syntax highlighting
- Code snippets
- Language configuration
- Synapse Dark theme

## License

This extension is part of the proprietary Synapse language ecosystem. See the [LICENSE](https://github.com/MichaelCrowe11/synapse-lang/blob/main/LICENSE-DUAL.md) for details.

## More Information

- [Synapse Language Documentation](https://github.com/MichaelCrowe11/synapse-lang)
- [Language Specification](https://github.com/MichaelCrowe11/synapse-lang/blob/main/LANGUAGE_SPEC.md)
- [Contributing Guide](https://github.com/MichaelCrowe11/synapse-lang/blob/main/CONTRIBUTING.md)

---

**Enjoy coding with Synapse!**