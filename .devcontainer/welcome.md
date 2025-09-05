# Welcome to Synapse Development Environment! 🚀

Created by **Michael Benjamin Crowe**

You're now in a fully configured development environment for the Synapse programming language.

## Quick Start

### 1. Test the REPL
```bash
# Start the Synapse REPL
synapse

# Try some commands:
# > uncertain x = 10 ± 0.5
# > parallel { branch A: test_1  branch B: test_2 }
```

### 2. Run Example Programs
```bash
# Run quantum simulation example
synapse examples/quantum_simulation.syn

# Run climate model
synapse examples/climate_model.syn

# Run drug discovery pipeline
synapse examples/drug_discovery.syn
```

### 3. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test
pytest tests/test_core.py
```

### 4. Start Jupyter Lab
```bash
# Launch Jupyter with Synapse kernel
jupyter lab --ip=0.0.0.0 --no-browser
# Then open the forwarded port in your browser
```

## Development Workflow

### Making Changes
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest`
4. Format code: `black .`
5. Commit: `git commit -m "Your message"`

### Code Quality
- **Format**: `black .` (auto-formats Python code)
- **Lint**: `flake8 .` (checks code style)
- **Type Check**: `mypy .` (checks type hints)

### Building Documentation
```bash
cd docs
make html
# View at docs/build/html/index.html
```

## VS Code Features

This environment includes:
- ✅ Syntax highlighting for `.syn` files
- ✅ Auto-formatting on save
- ✅ Python testing integration
- ✅ Jupyter notebook support
- ✅ Docker support for containerization

## Resources

- **Repository**: https://github.com/MichaelCrowe11/synapse-lang
- **Documentation**: Run `make -C docs html` to build
- **Language Spec**: See `LANGUAGE_SPEC.md`
- **Contributing**: See `CONTRIBUTING.md`

## Troubleshooting

If you encounter issues:

1. **Reinstall dependencies**: 
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

2. **Reset environment**:
   ```bash
   git clean -fdx
   pip install -e .
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.11+
   ```

---

Happy coding! 🎉 Feel free to explore and enhance the Synapse language.