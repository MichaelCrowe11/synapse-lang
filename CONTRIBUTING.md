# Contributing to Synapse Language

First off, thank you for considering contributing to Synapse Language! It's people like you that make Synapse such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by the [Synapse Code of Conduct](.github/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, please include as many details as possible using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml).

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml) to provide:

- A clear and descriptive title
- A detailed description of the proposed feature
- Examples of how it would be used
- Why this enhancement would be useful

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:

- `good first issue` - Simple issues perfect for beginners
- `help wanted` - Issues where we need community help
- `documentation` - Help improve our docs

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows our style guidelines
5. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/synapse-lang.git
cd synapse-lang

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
ruff check synapse_lang/

# Run type checking
mypy synapse_lang/
```

## Style Guidelines

### Python Style

We use:
- `black` for code formatting (line length: 100)
- `ruff` for linting
- `mypy` for type checking

Run formatting before committing:
```bash
black synapse_lang/
ruff check --fix synapse_lang/
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally after the first line

Example:
```
Add quantum state visualization feature

- Implement Bloch sphere representation
- Add real-time state updates
- Include measurement probabilities

Fixes #123
```

### Documentation

- Use docstrings for all public functions and classes
- Follow NumPy docstring style
- Update README.md if adding new features
- Add examples for complex functionality

## Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Test on multiple Python versions if possible

## Project Structure

```
synapse-lang/
├── synapse_lang/          # Main package
│   ├── quantum/           # Quantum computing modules
│   ├── backends/          # Computation backends
│   ├── pharmkit/          # Drug discovery toolkit
│   └── ...
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Example scripts
└── scripts/               # Utility scripts
```

## Community

- **Discord**: Join our [Discord server](https://discord.gg/synapse-lang)
- **Forums**: Visit [community.synapse-lang.org](https://community.synapse-lang.org)
- **Twitter**: Follow [@SynapseLang](https://twitter.com/SynapseLang)

## Recognition

Contributors are recognized in:
- AUTHORS.md file
- GitHub contributors page
- Release notes

## Questions?

Feel free to open an issue with the `question` label or reach out on Discord!

Thank you for contributing! 🚀
