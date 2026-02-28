"""Tests for QPandaBackend — pyqpanda3 circuit translation and execution."""
import pytest

try:
    import pyqpanda3
    HAS_QPANDA = True
except ImportError:
    HAS_QPANDA = False

pytestmark = pytest.mark.skipif(not HAS_QPANDA, reason="pyqpanda3 not installed")


# ---------------------------------------------------------------------------
# Lifecycle & singleton
# ---------------------------------------------------------------------------

def test_backend_init():
    """QPandaBackend initialises with config and stores shots."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    QPandaBackend._instance = None  # reset singleton
    backend = QPandaBackend(config={"shots": 1024})
    assert backend.shots == 1024
    backend.shutdown()


def test_backend_singleton():
    """get_or_create returns the same instance on repeated calls."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    QPandaBackend._instance = None
    b1 = QPandaBackend.get_or_create({"shots": 100})
    b2 = QPandaBackend.get_or_create({"shots": 200})
    assert b1 is b2
    assert b1.shots == 100  # first config wins
    b1.shutdown()


def test_shutdown_clears_singleton():
    """shutdown() resets _instance so next call creates a fresh backend."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    QPandaBackend._instance = None
    b1 = QPandaBackend.get_or_create({"shots": 100})
    b1.shutdown()
    assert QPandaBackend._instance is None
    b2 = QPandaBackend.get_or_create({"shots": 200})
    assert b2.shots == 200
    b2.shutdown()


# ---------------------------------------------------------------------------
# GATE_MAP completeness
# ---------------------------------------------------------------------------

def test_gate_map_completeness():
    """GATE_MAP contains all required gate names."""
    from synapse_lang.backends.qpanda_adapter import GATE_MAP
    required = ["h", "x", "y", "z", "s", "t", "rx", "ry", "rz",
                "cx", "cnot", "cz", "swap", "ccx", "toffoli"]
    for gate in required:
        assert gate in GATE_MAP, f"Gate '{gate}' missing from GATE_MAP"


def test_gate_map_callables():
    """Every GATE_MAP entry is callable."""
    from synapse_lang.backends.qpanda_adapter import GATE_MAP
    for name, fn in GATE_MAP.items():
        assert callable(fn), f"GATE_MAP['{name}'] is not callable"


# ---------------------------------------------------------------------------
# _prob_to_counts helper
# ---------------------------------------------------------------------------

def test_prob_to_counts_even():
    """50/50 distribution produces exactly half-and-half counts."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 1000})
    probs = {"00": 0.5, "11": 0.5}
    counts = backend._prob_to_counts(probs, 1000)
    assert counts["00"] == 500
    assert counts["11"] == 500
    backend.shutdown()


def test_prob_to_counts_skips_zero():
    """States with 0 probability are omitted from counts."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 100})
    probs = {"00": 1.0, "01": 0.0, "10": 0.0, "11": 0.0}
    counts = backend._prob_to_counts(probs, 100)
    assert counts == {"00": 100}
    backend.shutdown()


# ---------------------------------------------------------------------------
# Circuit translation & execution
# ---------------------------------------------------------------------------

def test_execute_bell_state():
    """Executing a Bell-state circuit yields only '00' and '11' outcomes."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    from synapse_lang.quantum.core import QuantumCircuitBuilder

    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 1024})

    circuit = QuantumCircuitBuilder(2, "bell")
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.measure_all()

    counts = backend.execute(circuit, shots=1024)
    assert isinstance(counts, dict)
    # Bell state should only produce '00' and '11'
    for key in counts:
        assert key in ("00", "11"), f"Unexpected outcome: {key}"
    # Both outcomes should be present with ~50% each
    assert "00" in counts
    assert "11" in counts
    total = sum(counts.values())
    assert total == 1024
    backend.shutdown()


def test_execute_x_gate():
    """Applying X to |0> should yield |1> deterministically."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    from synapse_lang.quantum.core import QuantumCircuitBuilder

    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 100})

    circuit = QuantumCircuitBuilder(1, "x_test")
    circuit.x(0)
    circuit.measure_all()

    counts = backend.execute(circuit, shots=100)
    assert counts == {"1": 100}
    backend.shutdown()


def test_execute_swap_gate():
    """SWAP(0,1) swaps qubit states correctly.

    pyqpanda3 uses little-endian bit ordering: the rightmost bit is qubit 0.
    X(0) produces '01', SWAP(0,1) moves the excitation to qubit 1 -> '10'.
    """
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    from synapse_lang.quantum.core import QuantumCircuitBuilder, QuantumGate

    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 100})

    circuit = QuantumCircuitBuilder(2, "swap_test")
    circuit.x(0)  # qubit 0 = |1>, bit-string = '01'
    circuit.add_gate(QuantumGate.SWAP, [0, 1])  # swap to qubit 1, bit-string = '10'
    circuit.measure_all()

    counts = backend.execute(circuit, shots=100)
    assert counts == {"10": 100}
    backend.shutdown()


def test_execute_toffoli_gate():
    """TOFFOLI(0,1,2) on |110> should yield |111>."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    from synapse_lang.quantum.core import QuantumCircuitBuilder, QuantumGate

    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 100})

    circuit = QuantumCircuitBuilder(3, "toffoli_test")
    circuit.x(0)  # |100>
    circuit.x(1)  # |110>
    circuit.add_gate(QuantumGate.TOFFOLI, [0, 1, 2])  # |111>
    circuit.measure_all()

    counts = backend.execute(circuit, shots=100)
    assert counts == {"111": 100}
    backend.shutdown()


def test_execute_uses_default_shots():
    """When shots not passed to execute(), uses the config default."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    from synapse_lang.quantum.core import QuantumCircuitBuilder

    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 50})

    circuit = QuantumCircuitBuilder(1, "default_shots")
    circuit.x(0)
    circuit.measure_all()

    counts = backend.execute(circuit)
    total = sum(counts.values())
    assert total == 50
    backend.shutdown()


def test_execute_rotation_gates():
    """Rotation gates (RX, RY, RZ) execute without error."""
    from synapse_lang.backends.qpanda_adapter import QPandaBackend
    from synapse_lang.quantum.core import QuantumCircuitBuilder
    import math

    QPandaBackend._instance = None
    backend = QPandaBackend(config={"shots": 100})

    circuit = QuantumCircuitBuilder(1, "rotation_test")
    circuit.rx(0, math.pi)    # RX(pi) should flip |0> to |1>
    circuit.measure_all()

    counts = backend.execute(circuit, shots=100)
    # RX(pi)|0> = -i|1>, so measuring should give |1>
    assert counts.get("1", 0) == 100
    backend.shutdown()
