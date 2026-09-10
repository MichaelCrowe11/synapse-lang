"""Independent first-order uncertainty references and quantum invariants."""
import math

import numpy as np
import pytest

from synapse_lang import execute
from synapse_lang.quantum.core import QuantumCircuitBuilder, SimulatorBackend
from synapse_lang.uncertainty import UncertainValue


@pytest.mark.parametrize("x,y", [(0, 2), (-2, 3), (2, -3), (-2, -3), (.01, 1)])
@pytest.mark.parametrize("correlated", [False, True])
@pytest.mark.parametrize("operator", ["+", "-", "*", "/"])
def test_uncertainty_matches_numerical_jacobian(x, y, correlated, operator):
    functions = {"+": lambda x,y:x+y, "-": lambda x,y:x-y,
                 "*": lambda x,y:x*y, "/": lambda x,y:x/y}
    function = functions[operator]
    h = 1e-5
    dx = (function(x+h, y)-function(x-h, y))/(2*h)
    dy = (function(x, y+h)-function(x, y-h))/(2*h)
    covariance = np.array([[.02**2, .02*.03 if correlated else 0],
                           [.02*.03 if correlated else 0, .03**2]])
    expected = math.sqrt(max(0, np.array([dx,dy]) @ covariance @ np.array([dx,dy])))
    a = UncertainValue(x, .02, correlation_id="shared" if correlated else None)
    b = UncertainValue(y, .03, correlation_id="shared" if correlated else None)
    result = execute(f"a {operator} b", context={"a":a,"b":b})
    assert result.nominal == pytest.approx(function(x,y))
    assert result.uncertainty == pytest.approx(expected, abs=1e-8, rel=1e-6)


@pytest.mark.parametrize("operator", ["/", "**"])
def test_uncertain_zero_denominator_fails(operator):
    with pytest.raises((ZeroDivisionError, ValueError)):
        execute(f"a {operator} b", context={"a":UncertainValue(0,1),"b":UncertainValue(0,1)})


@pytest.mark.parametrize("x,y", [(2, 3), (.5, -2), (1, .2)])
@pytest.mark.parametrize("correlated", [False, True])
def test_uncertain_exponent_includes_both_derivatives(x, y, correlated):
    a = UncertainValue(x,.02,correlation_id="same" if correlated else None)
    b = UncertainValue(y,.03,correlation_id="same" if correlated else None)
    dx = y*x**(y-1)*.02
    dy = x**y*math.log(x)*.03
    expected = abs(dx+dy) if correlated else math.hypot(dx,dy)
    result = execute("a ** b",context={"a":a,"b":b})
    assert result.uncertainty == pytest.approx(expected)


@pytest.mark.parametrize("x,p,sigma", [(0,1,.2),(0,2,0),(0,0,0),(-2,2,.8)])
def test_scalar_powers(x,p,sigma):
    result = UncertainValue(x,.2)**p
    assert result.nominal == x**p
    assert result.uncertainty == pytest.approx(sigma)


@pytest.mark.parametrize("n", [1,2,4])
def test_gate_inverse_and_normalization(n):
    rng = np.random.default_rng(2026)
    state = rng.normal(size=2**n) + 1j*rng.normal(size=2**n)
    state /= np.linalg.norm(state)
    backend = SimulatorBackend()
    for q in range(n):
        for axis in ("X","Y","Z"):
            rotated = backend._rotation(state,q,n,axis,.73)
            assert np.linalg.norm(rotated) == pytest.approx(1)
            np.testing.assert_allclose(backend._rotation(rotated,q,n,axis,-.73),state,atol=1e-14)
        for gate in (backend._x, backend._h):
            np.testing.assert_allclose(gate(gate(state,q,n),q,n),state,atol=1e-14)
    for c in range(n):
        for t in range(n):
            if c != t:
                np.testing.assert_allclose(backend._cnot(backend._cnot(state,c,t,n),c,t,n),state,atol=1e-14)


def test_seeded_bell_measurements_and_shot_conservation():
    previous = np.random.get_state()
    try:
        np.random.seed(123)
        circuit = QuantumCircuitBuilder(2).h(0).cnot(0,1)
        counts = SimulatorBackend().execute(circuit, shots=10000)
    finally:
        np.random.set_state(previous)
    assert set(counts) == {"00","11"}
    assert sum(counts.values()) == 10000
    assert abs(counts["00"]-5000) < 5*math.sqrt(10000*.5*.5)


def test_direct_noise_validation_rejects_nan():
    from synapse_lang.quantum.semantics import (
        BackendConfig,
        NoiseConfig,
        QuantumSemanticError,
        validate_backend_config,
    )

    with pytest.raises(QuantumSemanticError):
        validate_backend_config(BackendConfig(noise=NoiseConfig(kind="depolarizing",p1q=float("nan"))))
