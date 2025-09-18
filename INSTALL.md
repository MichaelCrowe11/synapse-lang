# Synapse Language Installation Guide

## Quick Install

### From PyPI (Recommended)
```bash
pip install synapse-lang
```

### From TestPyPI (Beta)
```bash
pip install -i https://test.pypi.org/simple/ synapse-lang
```

### From Source
```bash
git clone https://github.com/synapse-lang/synapse-lang.git
cd synapse-lang
pip install -e .
```

## Platform-Specific Installation

### macOS (Homebrew)
```bash
brew tap synapse-lang/tap
brew install synapse-lang
```

### Conda
```bash
conda install -c conda-forge synapse-lang
```

### Docker
```bash
docker pull synapse-lang:latest
docker run -it synapse-lang:latest
```

### npm (Node.js wrapper)
```bash
npm install -g @synapse-lang/cli
```

## Verify Installation

```bash
python -c "import synapse_lang; print(synapse_lang.__version__)"
```

## Optional Dependencies

For full functionality:
```bash
pip install synapse-lang[all]
```

For specific features:
```bash
pip install synapse-lang[quantum]  # Quantum computing
pip install synapse-lang[gpu]      # GPU acceleration
pip install synapse-lang[ml]       # Machine learning
```

## Troubleshooting

If you encounter issues:
1. Ensure Python 3.8+ is installed
2. Update pip: `pip install --upgrade pip`
3. Clear pip cache: `pip cache purge`
4. Report issues: https://github.com/synapse-lang/synapse-lang/issues

## Links

- PyPI: https://pypi.org/project/synapse-lang/
- GitHub: https://github.com/synapse-lang/synapse-lang
- Documentation: https://docs.synapse-lang.org
- Discord: https://discord.gg/synapse-lang
