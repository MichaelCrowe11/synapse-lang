"""Tests for QPandaBackend search & optimization algorithm wrappers.

Covers: run_grover(), run_qaoa(), run_qae(), run_qubo()
"""
import math

import pytest

try:
    import pyqpanda3
    HAS_QPANDA = True
except ImportError:
    HAS_QPANDA = False

pytestmark = pytest.mark.skipif(not HAS_QPANDA, reason="pyqpanda3 not installed")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset QPandaBackend singleton before each test."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    QPandaBackend._instance = None
    yield
    QPandaBackend._instance = None


@pytest.fixture
def backend():
    """Create a fresh QPandaBackend for testing."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    return QPandaBackend(config={"shots": 1024})


# ---------------------------------------------------------------------------
# Method existence checks
# ---------------------------------------------------------------------------

def test_run_grover_method_exists(backend):
    """QPandaBackend exposes a run_grover() method."""
    assert hasattr(backend, "run_grover")
    assert callable(backend.run_grover)


def test_run_qaoa_method_exists(backend):
    """QPandaBackend exposes a run_qaoa() method."""
    assert hasattr(backend, "run_qaoa")
    assert callable(backend.run_qaoa)


def test_run_qae_method_exists(backend):
    """QPandaBackend exposes a run_qae() method."""
    assert hasattr(backend, "run_qae")
    assert callable(backend.run_qae)


def test_run_qubo_method_exists(backend):
    """QPandaBackend exposes a run_qubo() method."""
    assert hasattr(backend, "run_qubo")
    assert callable(backend.run_qubo)


# ---------------------------------------------------------------------------
# Grover search tests
# ---------------------------------------------------------------------------

def test_grover_marked_state_search(backend):
    """Grover search finds marked states with high probability."""
    from synapse_lang.results import SynapseQuantumResult

    result = backend.run_grover(
        n_qubits=3,
        marked_states=["101", "001"],
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.probabilities is not None
    # The marked states should dominate probabilities
    marked_prob = sum(
        result.probabilities.get(s, 0.0) for s in ["101", "001"]
    )
    assert marked_prob > 0.8, f"Marked states prob too low: {marked_prob}"
    assert result.metadata.get("algorithm") == "grover"


def test_grover_single_marked_state(backend):
    """Grover search with a single marked state concentrates probability."""
    from synapse_lang.results import SynapseQuantumResult

    result = backend.run_grover(
        n_qubits=2,
        marked_states=["11"],
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.probabilities is not None
    # Single marked state should get high probability
    assert result.probabilities.get("11", 0.0) > 0.5


def test_grover_returns_counts(backend):
    """Grover search includes measurement counts when shots > 0."""
    from synapse_lang.results import SynapseQuantumResult

    result = backend.run_grover(
        n_qubits=2,
        marked_states=["10"],
        shots=1000,
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.counts is not None
    total_counts = sum(result.counts.values())
    assert total_counts == 1000


def test_grover_custom_iterations(backend):
    """Grover search respects custom iteration count."""
    from synapse_lang.results import SynapseQuantumResult

    result = backend.run_grover(
        n_qubits=3,
        marked_states=["101"],
        iterations=2,
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.metadata.get("iterations") == 2


def test_grover_metadata(backend):
    """Grover result metadata includes algorithm details."""
    result = backend.run_grover(
        n_qubits=3,
        marked_states=["101"],
    )

    assert result.metadata["algorithm"] == "grover"
    assert result.metadata["n_qubits"] == 3
    assert result.metadata["marked_states"] == ["101"]


# ---------------------------------------------------------------------------
# QAOA tests
# ---------------------------------------------------------------------------

def test_qaoa_simple_maxcut(backend):
    """QAOA solves a simple 2-variable optimization problem."""
    from synapse_lang.results import SynapseQuantumResult
    import sympy as sp

    x0, x1 = sp.symbols("x0 x1")
    problem = x0 + x1 - 2 * x0 * x1  # MaxCut-like: optimal at 01 or 10

    result = backend.run_qaoa(
        problem=problem,
        layers=1,
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.metadata.get("algorithm") == "qaoa"
    # Should have energy dict in metadata
    assert "energy_dict" in result.metadata
    assert result.metadata["problem_dimension"] == 2


def test_qaoa_returns_probabilities(backend):
    """QAOA result includes probability distribution."""
    from synapse_lang.results import SynapseQuantumResult
    import sympy as sp

    x0, x1 = sp.symbols("x0 x1")
    problem = x0 + x1 - 2 * x0 * x1

    result = backend.run_qaoa(problem=problem, layers=1)

    assert isinstance(result, SynapseQuantumResult)
    assert result.probabilities is not None
    assert len(result.probabilities) > 0
    # Probabilities should sum to approximately 1
    total = sum(result.probabilities.values())
    assert abs(total - 1.0) < 0.05


def test_qaoa_value_is_optimal_energy(backend):
    """QAOA result value field contains the best energy found."""
    from synapse_lang.results import SynapseQuantumResult
    import sympy as sp

    x0, x1 = sp.symbols("x0 x1")
    problem = x0 + x1 - 2 * x0 * x1

    result = backend.run_qaoa(problem=problem, layers=1)

    assert isinstance(result, SynapseQuantumResult)
    assert result.value is not None
    # The minimum energy for this problem is 0 (at x0=x1=0 or x0=x1=1)
    assert isinstance(result.value, (int, float))


def test_qaoa_custom_optimizer(backend):
    """QAOA accepts custom optimizer parameter."""
    import sympy as sp

    x0, x1 = sp.symbols("x0 x1")
    problem = x0 + x1

    result = backend.run_qaoa(
        problem=problem,
        layers=1,
        optimizer="COBYLA",
    )

    assert result.metadata.get("optimizer") == "COBYLA"


def test_qaoa_multiple_layers(backend):
    """QAOA with multiple layers produces valid results."""
    import sympy as sp

    x0, x1 = sp.symbols("x0 x1")
    problem = x0 + x1 - 2 * x0 * x1

    result = backend.run_qaoa(problem=problem, layers=2)

    assert result.metadata.get("layers") == 2
    assert result.probabilities is not None


# ---------------------------------------------------------------------------
# QAE (Quantum Amplitude Estimation) tests
# ---------------------------------------------------------------------------

def test_qae_basic_estimation(backend):
    """QAE estimates amplitude of a simple state preparation circuit."""
    from synapse_lang.results import SynapseQuantumResult
    import numpy as np
    from pyqpanda3.core import QCircuit, RY, X

    def state_prep(qlist):
        cir = QCircuit()
        cir << RY(qlist[0], np.pi / 3) << X(qlist[1]).control(qlist[0])
        return cir

    result = backend.run_qae(
        operator=state_prep,
        n_qubits=2,
        res_index=[0, 1],
        target_state="11",
        epsilon=0.01,
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.value is not None
    # Expected: sin^2(pi/6) * 1 = 0.25 (approximately)
    assert abs(result.value - 0.25) < 0.05
    assert result.metadata.get("algorithm") == "qae"


def test_qae_single_qubit_estimation(backend):
    """QAE works with single qubit estimation."""
    from synapse_lang.results import SynapseQuantumResult
    import numpy as np
    from pyqpanda3.core import QCircuit, RY

    def state_prep(qlist):
        cir = QCircuit()
        cir << RY(qlist[0], np.pi / 4)
        return cir

    result = backend.run_qae(
        operator=state_prep,
        n_qubits=1,
        res_index=0,
        target_state="1",
        epsilon=0.01,
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.value is not None
    # sin^2(pi/8) ~ 0.1464
    expected = math.sin(math.pi / 8) ** 2
    assert abs(result.value - expected) < 0.05


def test_qae_metadata(backend):
    """QAE result metadata includes algorithm parameters."""
    import numpy as np
    from pyqpanda3.core import QCircuit, RY

    def state_prep(qlist):
        cir = QCircuit()
        cir << RY(qlist[0], np.pi / 3)
        return cir

    result = backend.run_qae(
        operator=state_prep,
        n_qubits=1,
        res_index=0,
        epsilon=0.01,
    )

    assert result.metadata["algorithm"] == "qae"
    assert result.metadata["n_qubits"] == 1
    assert result.metadata["epsilon"] == 0.01


# ---------------------------------------------------------------------------
# QUBO (Quadratic Unconstrained Binary Optimization) tests
# ---------------------------------------------------------------------------

def test_qubo_simple_problem(backend):
    """QUBO solves a simple quadratic binary optimization."""
    from synapse_lang.results import SynapseQuantumResult
    import sympy as sp

    x0, x1, x2 = sp.symbols("x0 x1 x2")
    problem = -0.5 * x0 * x1 + 0.9 * x1 * x2 + 1.3 * x0 - x1 - 0.5 * x2

    result = backend.run_qubo(
        problem=problem,
        layers=2,
    )

    assert isinstance(result, SynapseQuantumResult)
    assert result.probabilities is not None
    assert result.metadata.get("algorithm") == "qubo"


def test_qubo_returns_probabilities(backend):
    """QUBO result includes normalized probability distribution."""
    import sympy as sp

    x0, x1 = sp.symbols("x0 x1")
    problem = x0 - x1

    result = backend.run_qubo(problem=problem, layers=1)

    assert result.probabilities is not None
    total = sum(result.probabilities.values())
    assert abs(total - 1.0) < 0.05


def test_qubo_best_solution_in_value(backend):
    """QUBO result value contains optimal objective value."""
    import sympy as sp

    x0, x1, x2 = sp.symbols("x0 x1 x2")
    problem = -0.5 * x0 * x1 + 0.9 * x1 * x2 + 1.3 * x0 - x1 - 0.5 * x2

    result = backend.run_qubo(problem=problem, layers=2)

    assert result.value is not None
    assert isinstance(result.value, (int, float))


def test_qubo_custom_optimizer(backend):
    """QUBO respects custom optimizer parameter."""
    import sympy as sp

    x0, x1 = sp.symbols("x0 x1")
    problem = x0 + x1

    result = backend.run_qubo(
        problem=problem,
        layers=1,
        optimizer="COBYLA",
    )

    assert result.metadata.get("optimizer") == "COBYLA"


def test_qubo_dict_format(backend):
    """QUBO accepts dict-format problem specification."""
    from synapse_lang.results import SynapseQuantumResult
    import numpy as np

    # Q(x) = x^T A x + b^T x + c
    problem_dict = {
        "quadratic": np.array([[0.0, -0.5], [-0.5, 0.0]]),
        "linear": np.array([1.0, -1.0]),
        "constant": 0.0,
    }

    result = backend.run_qubo(problem=problem_dict, layers=1)

    assert isinstance(result, SynapseQuantumResult)
    assert result.metadata.get("algorithm") == "qubo"


# ---------------------------------------------------------------------------
# Error handling / robustness tests
# ---------------------------------------------------------------------------

def test_grover_never_crashes(backend):
    """run_grover never raises; returns error info in metadata if needed."""
    from synapse_lang.results import SynapseQuantumResult

    # Even with edge-case inputs, should not crash
    result = backend.run_grover(n_qubits=1, marked_states=["0"])
    assert isinstance(result, SynapseQuantumResult)


def test_qaoa_never_crashes(backend):
    """run_qaoa never raises; returns error info in metadata if needed."""
    from synapse_lang.results import SynapseQuantumResult
    import sympy as sp

    x0 = sp.symbols("x0")
    result = backend.run_qaoa(problem=x0, layers=1)
    assert isinstance(result, SynapseQuantumResult)


def test_qae_never_crashes(backend):
    """run_qae never raises; returns error info in metadata if needed."""
    from synapse_lang.results import SynapseQuantumResult
    from pyqpanda3.core import QCircuit, H

    def simple_op(qlist):
        cir = QCircuit()
        cir << H(qlist[0])
        return cir

    result = backend.run_qae(
        operator=simple_op,
        n_qubits=1,
        res_index=0,
        epsilon=0.01,
    )
    assert isinstance(result, SynapseQuantumResult)


def test_qubo_never_crashes(backend):
    """run_qubo never raises; returns error info in metadata if needed."""
    from synapse_lang.results import SynapseQuantumResult
    import sympy as sp

    x0 = sp.symbols("x0")
    result = backend.run_qubo(problem=x0, layers=1)
    assert isinstance(result, SynapseQuantumResult)


# ---------------------------------------------------------------------------
# Helper method tests
# ---------------------------------------------------------------------------

def test_build_grover_oracle_helper(backend):
    """_build_grover_oracle creates a valid oracle callable."""
    assert hasattr(backend, "_build_grover_oracle")
    oracle = backend._build_grover_oracle(["101", "001"])
    assert callable(oracle)


def test_normalize_probabilities_helper(backend):
    """_normalize_probabilities ensures values sum to 1."""
    assert hasattr(backend, "_normalize_probabilities")
    raw = {"00": 0.3, "01": 0.2, "10": 0.1, "11": 0.4}
    normalized = backend._normalize_probabilities(raw)
    assert abs(sum(normalized.values()) - 1.0) < 1e-9
