# 🐳 Synapse Language Docker Image

[![Docker Pulls](https://img.shields.io/docker/pulls/michaelcrowe11/synapse-lang)](https://hub.docker.com/r/michaelcrowe11/synapse-lang)
[![Docker Image Size](https://img.shields.io/docker/image-size/michaelcrowe11/synapse-lang)](https://hub.docker.com/r/michaelcrowe11/synapse-lang)
[![Docker Version](https://img.shields.io/docker/v/michaelcrowe11/synapse-lang)](https://hub.docker.com/r/michaelcrowe11/synapse-lang)

## Quick Start

```bash
docker pull michaelcrowe11/synapse-lang:latest
docker run -it michaelcrowe11/synapse-lang:latest
```

## What is Synapse Language?

Synapse is a revolutionary scientific programming language that combines:
- 🔬 **Quantum Computing** - Native quantum circuit design and simulation
- 🤖 **AI Assistance** - Intelligent code completion and error detection
- 👥 **Real-time Collaboration** - Google Docs-like collaborative coding
- 🔐 **Blockchain Verification** - Immutable research integrity
- 🌐 **Distributed Computing** - Scalable parallel execution
- 📱 **Mobile Development** - Cross-platform app framework
- 🎨 **Visual Programming** - Drag-and-drop interface
- 🔢 **Uncertainty Quantification** - Built-in error propagation

## Available Tags

- `latest` - Most recent stable release
- `2.3.1` - Current version with Docker Hub integration
- `2.3.0` - Previous stable release

## Usage Examples

### Interactive Python Shell
```bash
docker run -it michaelcrowe11/synapse-lang:latest
```

### Jupyter Notebook
```bash
docker run -p 8888:8888 michaelcrowe11/synapse-lang:latest \
  jupyter notebook --ip=0.0.0.0 --allow-root --no-browser
```
Access at: http://localhost:8888

### Mount Local Directory
```bash
docker run -it -v $(pwd):/workspace michaelcrowe11/synapse-lang:latest
```

### Run Synapse Script
```bash
docker run -v $(pwd):/workspace michaelcrowe11/synapse-lang:latest \
  python /workspace/my_script.py
```

## Docker Compose

```yaml
version: '3.8'

services:
  synapse:
    image: michaelcrowe11/synapse-lang:latest
    volumes:
      - ./workspace:/workspace
    ports:
      - "8888:8888"
    command: jupyter lab --ip=0.0.0.0 --allow-root --no-browser
```

## What's Included

### Core Package
- Synapse Language v2.3.1
- Python 3.10
- All 8 major enhancement modules

### Scientific Libraries
- NumPy, SciPy, Pandas
- Matplotlib, Plotly, Seaborn
- SymPy, NetworkX
- Numba JIT compiler

### Development Tools
- Jupyter Notebook & Lab
- IPython interactive shell
- Git, curl, wget

## Environment Variables

- `SYNAPSE_ENV` - Set to 'development' or 'production'
- `JUPYTER_ENABLE_LAB` - Set to 'yes' to use JupyterLab

## Examples

### Quantum Circuit
```python
from synapse_lang.quantum_designer import QuantumCircuit

circuit = QuantumCircuit(2)
circuit.add_gate("H", [0])
circuit.add_gate("CNOT", [0, 1])
print(circuit.to_qasm())
```

### Collaborative Session
```python
from synapse_lang.collaboration import CollaborationSession

session = CollaborationSession("my-project")
session.start()
```

### AI Code Assistance
```python
from synapse_lang.ai_suggestions import AICodeAssistant

assistant = AICodeAssistant()
suggestions = assistant.analyze_and_suggest(code)
```

## Multi-Container Setup

For distributed computing:

```bash
# Start master node
docker run -d --name synapse-master \
  -e ROLE=master \
  michaelcrowe11/synapse-lang:latest

# Start worker nodes
docker run -d --name synapse-worker-1 \
  -e ROLE=worker \
  -e MASTER_HOST=synapse-master \
  --link synapse-master \
  michaelcrowe11/synapse-lang:latest
```

## Building from Source

```bash
git clone https://github.com/michaelcrowe11/synapse-lang.git
cd synapse-lang
docker build -t my-synapse .
```

## Resources

- 📦 **PyPI Package**: [pypi.org/project/synapse-lang](https://pypi.org/project/synapse-lang/)
- 📚 **Documentation**: [github.com/michaelcrowe11/synapse-lang](https://github.com/michaelcrowe11/synapse-lang)
- 🐛 **Issues**: [github.com/michaelcrowe11/synapse-lang/issues](https://github.com/michaelcrowe11/synapse-lang/issues)
- 💬 **Discord**: [discord.gg/synapse-lang](https://discord.gg/synapse-lang)

## License

MIT License - See [LICENSE](https://github.com/michaelcrowe11/synapse-lang/blob/main/LICENSE) for details.

## Support

For help or questions:
- Open an issue on GitHub
- Join our Discord community
- Email: synapse-lang@outlook.com

---

**Made with ❤️ by the Synapse Team**