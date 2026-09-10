"""State ownership and independent reference tests for the companion milestone."""
import itertools

import numpy as np
import pytest
from qubit_flow_lang.bridge import SynapseQubitBridge
from qubit_flow_lang.cli import evaluate
from qubit_flow_lang.qubit_flow_interpreter import QuantumGates, QubitFlowInterpreter


def run(source):
    interpreter = QubitFlowInterpreter()
    messages = interpreter.execute(source)
    assert not any(message.startswith("Error:") for message in messages), messages
    return interpreter


@pytest.mark.parametrize("first", ["a", "b"])
def test_bell_sequential_collapse(monkeypatch, first):
    import random
    rng = random.Random(1729)
    monkeypatch.setattr(random, "random", rng.random)
    outcomes = []
    for _ in range(200):
        q = run("qubit a\nqubit b\nH[a]\nCNOT[a,b]")
        a = q.measure_qubit(first)
        b = q.measure_qubit("b" if first == "a" else "a")
        assert a == b
        assert q.qubits["a"].state is q.qubits["b"].state
        assert np.linalg.norm(q.state.amplitudes) == pytest.approx(1)
        outcomes.append(a)
    assert 70 < sum(outcomes) < 130


def test_ghz_append_inverse_and_marginals():
    q = run("qubit a\nqubit b\nqubit c\nentangle(a,b,c) ghz")
    expected = np.zeros(8)
    expected[[0, 7]] = 1 / np.sqrt(2)
    np.testing.assert_allclose(q.state.amplitudes, expected)
    assert [q.probability_one(n) for n in q.qubits] == pytest.approx([0.5] * 3)
    assert not q.execute("qubit d = |1>")[0].startswith("Error:")
    np.testing.assert_allclose(q.state.amplitudes, np.kron(expected, [0, 1]))
    q.execute("CNOT[a,c]\nCNOT[a,b]\nH[a]")
    assert abs(q.state.amplitudes[1]) ** 2 == pytest.approx(1)
    assert all(r.state is q.state for r in q.qubits.values())


@pytest.mark.parametrize("control,target", list(itertools.permutations(range(3), 2)))
@pytest.mark.parametrize("gate", ["cnot", "cz"])
def test_all_ordered_pairs_against_dense_basis_mapping(control, target, gate):
    q = run("qubit a\nqubit b\nqubit c")
    rng = np.random.default_rng(400)
    state = rng.normal(size=8) + 1j * rng.normal(size=8)
    state /= np.linalg.norm(state)
    q.state.amplitudes = state.copy()
    dense = np.zeros((8, 8), dtype=complex)
    for column in range(8):
        control_set = bool(column & (1 << (2 - control)))
        if gate == "cnot":
            row = column ^ (1 << (2 - target)) if control_set else column
            dense[row, column] = 1
        else:
            dense[column, column] = -1 if control_set and column & (1 << (2 - target)) else 1
    names = list(q.qubits)
    q._apply_two_qubit_gate(names[control], names[target], getattr(QuantumGates, gate)())
    np.testing.assert_allclose(q.state.amplitudes, dense @ state, atol=1e-13)
    q._apply_two_qubit_gate(names[control], names[target], getattr(QuantumGates, gate)())
    np.testing.assert_allclose(q.state.amplitudes, state, atol=1e-13)


@pytest.mark.parametrize("axis", ["x", "y", "z"])
@pytest.mark.parametrize("target", [0, 1, 2])
def test_single_gate_on_entangled_register(axis, target):
    from scipy.linalg import expm
    pauli = {"x": [[0, 1], [1, 0]], "y": [[0, -1j], [1j, 0]], "z": [[1, 0], [0, -1]]}[axis]
    gate = expm(-0.3j * np.array(pauli))
    q = run("qubit a\nqubit b\nqubit c\nentangle(a,b,c) ghz")
    state = q.state.amplitudes.copy()
    dense = np.array([1])
    for index in range(3):
        dense = np.kron(dense, gate if index == target else np.eye(2))
    q._apply_single_qubit_gate(list(q.qubits)[target], getattr(QuantumGates, f"rotation_{axis}")(0.6))
    np.testing.assert_allclose(q.state.amplitudes, dense @ state, atol=1e-13)


@pytest.mark.parametrize("source", [
    "qubit a\nqubit a", "qubit a\nCNOT[a,a]", "qubit a\nH[missing]",
    "qubit a\nRY(missing)[a]", "qubit a\nqft(a)", "shors(15)",
    "grovers(8,oracle,2)", "qudit a[3]", "qubit a\nX[a,b]",
    "qubit a = |1>\nqubit b\nentangle(a,b) bell",
])
def test_errors_are_not_success(source):
    with pytest.raises(ValueError):
        evaluate(source)


def test_supported_bridge_and_feedback():
    bridge = SynapseQubitBridge()
    result = bridge.execute_hybrid("uncertain theta = 0.8 ± 0.002", "qubit a\nRY(theta)[a]")
    p = np.sin(0.4) ** 2
    assert result["shared_context"]["theta"].uncertainty == 0.002
    assert result["shared_context"]["quantum_a"].nominal == pytest.approx(p)
    assert result["shared_context"]["quantum_a"].uncertainty == pytest.approx(np.sqrt(p * (1-p)))
    with pytest.raises(NotImplementedError):
        bridge.quantum_measurement_feedback("a", "X")
    feedback = bridge.quantum_measurement_feedback("a")
    assert feedback.nominal in (0, 1)
    assert feedback.uncertainty == pytest.approx(np.sqrt(p * (1-p)))


def test_bridge_bell_marginals_and_errors():
    bridge = SynapseQubitBridge()
    result = bridge.execute_hybrid("theta = 0.8", "qubit a\nqubit b\nH[a]\nCNOT[a,b]")
    for name in ("a", "b"):
        assert result["shared_context"][f"quantum_{name}"].nominal == pytest.approx(0.5)
    with pytest.raises(ValueError):
        bridge.execute_hybrid("x = 1", "unknown[a]")


@pytest.mark.parametrize("ket,expected", [("0", [1, 0]), ("1", [0, 1]), ("+", [0.5, 0.5]), ("-", [0.5, 0.5])])
@pytest.mark.parametrize("closing", [">", "⟩"])
def test_initial_kets(ket, expected, closing):
    q = run(f"qubit a = |{ket}{closing}")
    np.testing.assert_allclose(abs(q.state.amplitudes) ** 2, expected)


@pytest.mark.parametrize("source", ["qubit a = |0", "qubit a = |2>", "qubit a @"])
def test_invalid_kets_and_characters_fail(source):
    with pytest.raises((ValueError, SyntaxError)):
        evaluate(source)
