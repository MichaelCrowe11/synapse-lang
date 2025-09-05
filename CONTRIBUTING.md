# Contributing to Synapse Language

Created by Michael Benjamin Crowe

Thank you for your interest in contributing to Synapse! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use issue templates when available
3. Provide clear descriptions and reproducible examples
4. Include system information (OS, Python version, etc.)

### Submitting Pull Requests

1. **Fork the repository** and create a feature branch
2. **Write tests** for new functionality
3. **Follow code style** (use black and flake8)
4. **Update documentation** as needed
5. **Sign your commits** with `git commit -s`

### Development Workflow

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/synapse-lang.git
cd synapse-lang

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest
black .
flake8 .

# Commit and push
git add .
git commit -m "feat: description of your feature"
git push origin feature/your-feature-name
```

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run only fast tests
pytest -m "not slow"
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Use descriptive test names
- Include both positive and negative test cases
- Test edge cases and error conditions

Example test:
```python
def test_uncertain_value_addition():
    val1 = UncertainValue(10, 0.5)
    val2 = UncertainValue(20, 1.0)
    result = val1 + val2
    
    assert result.value == 30
    assert result.uncertainty == pytest.approx(1.118, rel=1e-3)
```

## Code Style Guidelines

### Python Code

- Follow PEP 8
- Use black for formatting
- Maximum line length: 127 characters
- Use type hints where appropriate
- Document functions with docstrings

### Synapse Code

- Use 4 spaces for indentation
- Place opening braces on the same line
- Use descriptive names for variables and functions
- Comment complex algorithms

Example:
```synapse
hypothesis MyHypothesis {
    assume: initial_condition
    predict: expected_outcome
    validate: experimental_test
}
```

## Documentation

### Docstring Format

```python
def function_name(param1: Type, param2: Type) -> ReturnType:
    """
    Brief description of function.
    
    Longer explanation if needed, describing the algorithm,
    assumptions, and any important details.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception occurs
    
    Example:
        >>> result = function_name(value1, value2)
        >>> print(result)
        expected_output
    """
```

### Building Documentation

```bash
cd docs
make clean
make html
# View at docs/build/html/index.html
```

## Adding Language Features

When adding new language features:

1. **Update the lexer** (`synapse_interpreter.py`)
   - Add new token types
   - Update tokenization rules

2. **Update the parser** (`synapse_parser.py`)
   - Add AST node types
   - Implement parsing rules

3. **Update the interpreter** (`synapse_interpreter.py`)
   - Implement execution logic
   - Handle new constructs

4. **Add tests** (`tests/`)
   - Unit tests for each component
   - Integration tests for complete features

5. **Update documentation**
   - Language specification (`LANGUAGE_SPEC.md`)
   - Examples (`examples/`)
   - API documentation

6. **Update VS Code extension**
   - Syntax highlighting rules
   - Snippets for new constructs

## Release Process

1. Update version in:
   - `setup.py`
   - `vscode-extension/package.json`
   - `docs/source/conf.py`

2. Update CHANGELOG.md

3. Run full test suite:
   ```bash
   tox
   ```

4. Create release PR

5. After merge, create GitHub release

6. Package will be automatically published to PyPI

## Getting Help

- **GitHub Discussions**: For questions and ideas
- **Issues**: For bug reports and feature requests
- **Contact**: Michael Benjamin Crowe

## Recognition

Contributors will be:
- Listed in AUTHORS.md
- Mentioned in release notes
- Given credit in documentation

Thank you for contributing to Synapse!

---
Developed by Michael Benjamin Crowe