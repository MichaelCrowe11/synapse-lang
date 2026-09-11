"""Source-tracked first-order propagation: repeated variables, covariance, builtins."""
import math

import numpy as np
import pytest

from synapse_lang import execute
from synapse_lang.uncertainty import (
    UncertaintyEngine,
    UncertainValue,
    correlation,
    covariance,
    covariance_matrix,
    monte_carlo,
)


def test_a_variable_used_twice_is_the_same_variable():
    x = UncertainValue(3.0, 0.2)
    assert (x - x).nominal == 0.0 and (x - x).uncertainty == 0.0
    assert (x / x).nominal == 1.0 and (x / x).uncertainty == 0.0
    assert (x + x).uncertainty == pytest.approx(0.4)           # not 0.2 * sqrt(2)
    assert (x * x).uncertainty == pytest.approx(2 * 3.0 * 0.2)  # d(x^2) = 2x dx, not sqrt(2) x dx
    assert (x * x).uncertainty == pytest.approx((x ** 2).uncertainty)


def test_two_declarations_are_independent():
    a = UncertainValue(3.0, 0.2)
    b = UncertainValue(3.0, 0.2)
    assert (a - b).uncertainty == pytest.approx(0.2 * math.sqrt(2))
    assert covariance(a, b) == 0.0 and correlation(a, b) == 0.0


@pytest.mark.parametrize("t0", [5.0, 21.0, 34.5])
def test_repeated_variable_matches_exact_derivative(t0):
    B, C = 17.27, 237.3
    t = UncertainValue(t0, 0.8 / math.sqrt(3))
    chain = t * B / (t + C)
    exact = B * C / (t0 + C) ** 2 * t.uncertainty
    assert chain.uncertainty == pytest.approx(exact, rel=1e-12)
    assert chain.derivative_wrt(t) == pytest.approx(B * C / (t0 + C) ** 2, rel=1e-12)


def test_repeated_variable_agrees_with_monte_carlo():
    B, C = 17.27, 237.3
    t = UncertainValue(21.0, 0.5)
    chain = t * B / (t + C)
    rng = np.random.default_rng(11)
    draws = 21.0 + 0.5 * rng.standard_normal(400_000)
    mc_sd = (draws * B / (draws + C)).std(ddof=1)
    assert chain.uncertainty == pytest.approx(mc_sd, rel=0.01)
    # the old independent-variable form would be about nine percent high here
    independent = math.hypot(B / (21.0 + C) * 0.5, -21.0 * B / (21.0 + C) ** 2 * 0.5)
    assert independent > mc_sd * 1.05


def test_covariance_and_correlation_of_derived_results():
    a = UncertainValue(2.0, 0.1)
    b = UncertainValue(3.0, 0.2)
    s, d = a + b, a - b
    assert covariance(s, d) == pytest.approx(0.1 ** 2 - 0.2 ** 2)
    assert correlation(s, a) == pytest.approx(0.1 / math.hypot(0.1, 0.2))
    assert correlation(a, -a) == pytest.approx(-1.0)
    assert correlation(a, a) == pytest.approx(1.0)
    m = covariance_matrix([s, d, a])
    assert m.shape == (3, 3) and np.allclose(m, m.T)
    assert m[0, 0] == pytest.approx(s.uncertainty ** 2)
    assert m[2, 2] == pytest.approx(0.1 ** 2)
    # a linear combination built from covariances equals the tracked result
    combo = 2 * s - d
    assert combo.uncertainty ** 2 == pytest.approx(4 * m[0, 0] + m[1, 1] - 4 * m[0, 1])


def test_legacy_correlation_id_is_perfect_correlation():
    a = UncertainValue(-2.0, 1.0, correlation_id="k")
    b = UncertainValue(2.0, 1.0, correlation_id="k")
    assert (a * b).uncertainty == 0.0
    assert (a + b).uncertainty == pytest.approx(2.0)
    assert correlation(a, b) == pytest.approx(1.0)
    c = UncertainValue(1.0, 0.5)
    c.correlation_id = "k"           # re-keyed onto the shared source
    assert correlation(a, c) == pytest.approx(1.0)


def test_elementary_functions_and_unary_operators():
    x = UncertainValue(3.0, 0.2)
    assert x.sqrt().uncertainty == pytest.approx(0.2 / (2 * math.sqrt(3.0)))
    assert (x.sqrt() * x.sqrt() - x).uncertainty == pytest.approx(0.0, abs=1e-15)
    assert x.exp().log().uncertainty == pytest.approx(0.2)
    assert x.tan().uncertainty == pytest.approx(0.2 / math.cos(3.0) ** 2)
    assert x.log10().uncertainty == pytest.approx(0.2 / (3.0 * math.log(10)))
    assert (-x).uncertainty == 0.2 and (-x).nominal == -3.0
    assert abs(-x).nominal == 3.0 and abs(-x).uncertainty == 0.2
    assert (2 ** x).uncertainty == pytest.approx(8.0 * math.log(2) * 0.2)
    assert (10 / x).uncertainty == pytest.approx(10 / 9.0 * 0.2)
    assert float(x) == 3.0 and int(x) == 3 and round(x, 1) == 3.0
    assert x > 2 and x >= UncertainValue(3.0, 1.0) and not x < 1


def test_uncertainty_setter_and_zero_handling():
    x = UncertainValue(3.0, 0.2)
    y = x * 2
    x.uncertainty = 0.4
    assert x.uncertainty == 0.4 and y.uncertainty == pytest.approx(0.4)  # y keeps its own map
    z = UncertainValue(1.0, 0.0)
    assert z.sources == 0 and (z + x).sources == 1
    z.uncertainty = 0.3
    assert z.sources == 1 and z.uncertainty == 0.3
    with pytest.raises(ValueError):
        UncertainValue(1.0, float("nan"))


def test_engine_propagate_result_composes_with_its_inputs():
    engine = UncertaintyEngine()
    x = UncertainValue(2.0, 0.1)
    y = engine.propagate(lambda x: x * x, {"x": x})
    assert y.uncertainty == pytest.approx(2 * 2.0 * 0.1, rel=1e-6)
    # y depends on x, so y - x*x is exact to numerical differentiation error
    assert (y - x * x).uncertainty == pytest.approx(0.0, abs=1e-6)
    assert correlation(y, x) == pytest.approx(1.0, abs=1e-6)


def test_engine_explicit_correlation_still_uses_matrix():
    engine = UncertaintyEngine()
    engine.create_uncertain(1.0, 0.1, name="a")
    engine.create_uncertain(1.0, 0.1, name="b")
    engine.set_correlation("a", "b", 1.0)
    r = engine.propagate(lambda a, b: a + b, ["a", "b"])
    assert r.uncertainty == pytest.approx(0.2, rel=1e-6)
    assert r.sources == 1  # flattened: matrix correlations are not shared sources


def test_significantly_different_from_respects_shared_sources():
    x = UncertainValue(10.0, 1.0)
    assert not x.significantly_different_from(x)
    assert (x + 0.5).significantly_different_from(x)      # exact shift, zero spread
    assert not x.significantly_different_from(UncertainValue(11.0, 1.0))


def test_monte_carlo_helper_still_runs():
    r = monte_carlo(lambda x: x * x, {"x": UncertainValue(2.0, 0.1)}, samples=2000, seed=3)
    assert r.nominal == pytest.approx(4.0, abs=0.05)


def test_language_level_program():
    program = """x = 3 ± 0.2
y = x - x
z = sqrt(x) * sqrt(x) - x
w = exp(log(x))
"""
    from synapse_lang.synapse_interpreter import SynapseInterpreter
    interp = SynapseInterpreter()
    from synapse_lang import parse
    interp.interpret(parse(program))
    v = interp.variables
    assert v["y"].nominal == 0.0 and v["y"].uncertainty == 0.0
    assert v["z"].uncertainty == pytest.approx(0.0, abs=1e-15)
    assert v["w"].uncertainty == pytest.approx(0.2)
    assert str(v["x"] * 2) == "6.0 ± 0.4"


def test_language_builtins_read_uncertainty_back_out():
    a = UncertainValue(2.0, 0.1)
    b = UncertainValue(3.0, 0.2)
    assert execute("sigma(a + b)", context={"a": a, "b": b}) == pytest.approx(math.hypot(0.1, 0.2))
    assert execute("nominal(a * b)", context={"a": a, "b": b}) == 6.0
    assert execute("covariance(a + b, a - b)", context={"a": a, "b": b}) == pytest.approx(0.1 ** 2 - 0.2 ** 2)
    assert execute("correlation(a, a + b)", context={"a": a, "b": b}) == pytest.approx(0.1 / math.hypot(0.1, 0.2))
    assert execute("sigma(2.5)", context={}) == 0.0
    assert execute("sigma(sqrt(a))", context={"a": a}) == pytest.approx(0.1 / (2 * math.sqrt(2.0)))
