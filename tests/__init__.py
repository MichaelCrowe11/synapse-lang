"""
Quantum Trinity Test Suite

Comprehensive testing infrastructure for Synapse Language, Qubit-Flow, and Quantum-Net.
Ensures code quality, validates examples, and maintains reliability.
"""

__version__ = "1.0.0"
__all__ = ["run_all_tests", "validate_examples", "benchmark_performance"]

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run complete test suite."""
    import pytest
    return pytest.main(["-v", "--cov=synapse_lang", "--cov-report=html"])

def validate_examples():
    """Validate all documentation examples."""
    from .examples import validate_all_examples
    return validate_all_examples()

def benchmark_performance():
    """Run performance benchmarks."""
    from .benchmarks import run_benchmarks
    return run_benchmarks()