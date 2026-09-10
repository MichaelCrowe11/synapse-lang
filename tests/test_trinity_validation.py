"""Independent numerical checks, not evidence of hardware or secure QKD."""
import subprocess
import sys

import numpy as np
import pytest
from scipy.linalg import expm

from quantum_net_interpreter import BB84Protocol
from qubit_flow_interpreter import QuantumGates, QubitFlowInterpreter
from synapse_lang.quantum.core import SimulatorBackend
from synapse_lang.uncertainty import UncertainValue


@pytest.mark.parametrize("axis", ["x", "y", "z"])
@pytest.mark.parametrize("theta", [-3.1, -0.7, 0.0, 0.4, 2.9])
def test_rotation_engines_against_matrix_exponential(axis, theta):
    pauli = {
        "x": np.array([[0, 1], [1, 0]], dtype=complex),
        "y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "z": np.diag([1, -1]).astype(complex),
    }[axis]
    expected = expm(-0.5j * theta * pauli)
    flow_gate = getattr(QuantumGates, f"rotation_{axis}")(theta)
    np.testing.assert_allclose(flow_gate, expected, atol=1e-13)
    rng = np.random.default_rng(121)
    state = rng.normal(size=8) + 1j * rng.normal(size=8)
    state /= np.linalg.norm(state)
    dense = np.kron(np.eye(2), np.kron(expected, np.eye(2)))
    actual = SimulatorBackend()._rotation(state, 1, 3, axis.upper(), theta)
    np.testing.assert_allclose(actual, dense @ state, atol=1e-13)


def test_qubit_flow_source_single_qubit_rotation():
    interpreter = QubitFlowInterpreter()
    messages = interpreter.execute("qubit q = |0>\nH[q]\nZ[q]\nH[q]")
    assert not any(message.startswith("Error:") for message in messages), messages
    np.testing.assert_allclose(abs(interpreter.qubits["q"].state.amplitudes) ** 2, [0, 1], atol=1e-13)


def test_two_qubit_gate_produces_shared_bell_state():
    interpreter = QubitFlowInterpreter()
    messages = interpreter.execute("qubit a = |0>\nqubit b = |0>\nH[a]\nCNOT[a,b]")
    assert not any(message.startswith("Error:") for message in messages), messages
    assert interpreter.qubits["a"].state is interpreter.qubits["b"].state
    np.testing.assert_allclose(interpreter.state.amplitudes, np.array([1, 0, 0, 1]) / np.sqrt(2))


def test_uncertain_rotation_probability_matches_derivative():
    angle = UncertainValue(0.8, 0.002)
    probability = (1 - angle.cos()) / 2
    assert probability.nominal == pytest.approx(np.sin(0.4) ** 2)
    assert probability.uncertainty == pytest.approx(abs(np.sin(0.8)) * 0.002 / 2)


@pytest.mark.parametrize("intercept", [False, True])
def test_bb84_sifted_errors_match_ideal_and_intercept_resend(monkeypatch, intercept):
    rng = np.random.default_rng(884)
    monkeypatch.setattr(np.random, "random", rng.random)
    n = 20000
    bits = rng.integers(0, 2, n).tolist()
    alice = rng.choice(["Z", "X"], n).tolist()
    bob = rng.choice(["Z", "X"], n).tolist()
    protocol = BB84Protocol()
    states = protocol.prepare_qubits(bits, alice)
    if intercept:
        eve = rng.choice(["Z", "X"], n).tolist()
        states = protocol.prepare_qubits(protocol.measure_qubits(states, eve), eve)
    received = protocol.measure_qubits(states, bob)
    a = protocol.sift_key(bits, alice, bob)
    b = protocol.sift_key(received, alice, bob)
    qber = protocol.estimate_error_rate(a, b, len(a))
    expected = 0.25 if intercept else 0
    tolerance = 6 * np.sqrt(expected * (1 - expected) / len(a)) + 1 / len(a)
    assert abs(qber - expected) < tolerance
    assert abs(len(a) / n - 0.5) < 0.025


@pytest.mark.parametrize("source", ["unknown[q]", "circuit c(q) { unknown[q] }"])
def test_qubit_flow_unsupported_gate_terminates(source):
    command = "from qubit_flow_interpreter import QubitFlowInterpreter; print(QubitFlowInterpreter().execute(" + repr(source) + "))"
    result = subprocess.run([sys.executable, "-c", command], capture_output=True, text=True, timeout=5, check=True)
    assert "Error:" in result.stdout
