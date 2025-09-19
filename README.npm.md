# @synapse-lang/core

[![npm version](https://img.shields.io/npm/v/@synapse-lang/core.svg)](https://www.npmjs.com/package/@synapse-lang/core)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🧠 Synapse Language - JavaScript/Node.js Wrapper

Revolutionary scientific programming language with quantum computing, AI assistance, real-time collaboration, and blockchain verification.

## Installation

```bash
npm install @synapse-lang/core
```

**Note**: Synapse Language requires Python 3.8+ to be installed on your system.

### Install Python Package
After installing the npm package, install the Python backend:

```bash
pip install synapse-lang
```

Or use the built-in installer:
```bash
npx synapse-lang --install
```

## Features

- 🔬 **Quantum Computing** - Native quantum circuit design and simulation
- 🤖 **AI Assistance** - Intelligent code completion and error detection
- 👥 **Real-time Collaboration** - Multi-user collaborative coding
- 🔐 **Blockchain Verification** - Immutable research integrity
- 🌐 **Distributed Computing** - Scalable parallel execution
- 📱 **Mobile Development** - Cross-platform app framework
- 🎨 **Visual Programming** - Drag-and-drop interface
- 🔢 **Type Inference** - Advanced type system with uncertainty

## Quick Start

### CLI Usage

```bash
# Show help
npx synapse-lang --help

# Run demo
npx synapse-lang --demo

# Get package info
npx synapse-lang --info

# Install Python dependencies
npx synapse-lang --install
```

### Library Usage

```javascript
const SynapseLanguage = require('@synapse-lang/core');

// Create instance
const synapse = new SynapseLanguage();

// Run Synapse code
synapse.run(`
from synapse_lang.quantum_designer import QuantumCircuit

circuit = QuantumCircuit(2)
circuit.add_gate("H", [0])
circuit.add_gate("CNOT", [0, 1])
print(circuit.to_qasm())
`, (err, output) => {
    if (err) {
        console.error('Error:', err);
    } else {
        console.log('Output:', output);
    }
});

// Get package info
console.log(synapse.info());
```

## Examples

### Quantum Computing
```javascript
const synapse = new SynapseLanguage();

synapse.run(`
from synapse_lang.quantum_designer import QuantumCircuit

# Create Bell state
circuit = QuantumCircuit(2)
circuit.add_gate("H", [0])
circuit.add_gate("CNOT", [0, 1])
circuit.measure_all()

results = circuit.simulate(shots=1000)
print(f"Results: {results}")
`, (err, output) => {
    console.log(output);
});
```

### AI Code Assistance
```javascript
synapse.run(`
from synapse_lang.ai_suggestions import AICodeAssistant

assistant = AICodeAssistant()
code = "def calculate_energy(mass):"
suggestions = assistant.analyze_and_suggest(code)

for suggestion in suggestions:
    print(f"Suggestion: {suggestion.description}")
    print(f"Code: {suggestion.code}")
`, (err, output) => {
    console.log(output);
});
```

### Blockchain Verification
```javascript
synapse.run(`
from synapse_lang.blockchain_verification import ScientificBlockchain

blockchain = ScientificBlockchain()
computation = {
    "algorithm": "quantum_vqe",
    "result": {"energy": -1.857}
}

record_hash = blockchain.add_computation_record(
    computation,
    "Dr. Smith",
    {"institution": "Research Lab"}
)

print(f"Verified: {blockchain.verify_computation(record_hash)}")
`, (err, output) => {
    console.log(output);
});
```

## API Reference

### `new SynapseLanguage()`
Creates a new Synapse Language instance.

### `synapse.run(code, callback)`
Executes Synapse code.

- `code` (string): The Synapse/Python code to execute
- `callback` (function): Callback with (error, output) parameters

### `synapse.info()`
Returns package information including version, features, and links.

### `synapse.checkPython()`
Checks if Python is installed on the system.

## Requirements

- Node.js >= 14.0.0
- Python >= 3.8
- pip (Python package manager)

## Related Packages

- **PyPI**: [synapse-lang](https://pypi.org/project/synapse-lang/)
- **Docker**: [michaelcrowe11/synapse-lang](https://hub.docker.com/r/michaelcrowe11/synapse-lang)

## Links

- **GitHub**: https://github.com/michaelcrowe11/synapse-lang
- **Documentation**: https://github.com/michaelcrowe11/synapse-lang#readme
- **Issues**: https://github.com/michaelcrowe11/synapse-lang/issues

## License

MIT License - See [LICENSE](https://github.com/michaelcrowe11/synapse-lang/blob/main/LICENSE) for details.

## Author

Michael Benjamin Crowe

---

Made with ❤️ for the scientific computing community