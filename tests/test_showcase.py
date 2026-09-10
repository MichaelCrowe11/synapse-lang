"""Independent numerical checks and input boundaries for the in-app showcase."""
import math

import numpy as np
import pytest

from synapse_lang.showcase import evaluate


def test_concentration_matches_independent_derivative():
    report = evaluate("concentration", {})
    assert report["result"]["nominal"] == 5
    assert report["result"]["uncertainty"] == pytest.approx(math.hypot(0.1 / 2, 10 * 0.02 / 4))
    assert report["unit"] == "mg/mL"
    assert report["source"].endswith("concentration")


def test_spend_reuses_request_uncertainty_once():
    result = evaluate("spend", {})["result"]
    assert result == {"nominal": 40.0, "uncertainty": 4.0}
    changed = evaluate("spend", {"requests": 20000})["result"]
    assert changed["nominal"] == 80


def test_bell_is_correlated_seeded_and_preserves_rng():
    before = np.random.get_state()
    first = evaluate("bell", {})
    after = np.random.get_state()
    assert before[0] == after[0] and np.array_equal(before[1], after[1])
    assert before[2:] == after[2:]
    assert first["result"] == evaluate("bell", {})["result"]
    counts = first["result"]["counts"]
    assert set(counts) == {"00", "11"}
    assert sum(counts.values()) == 1024
    assert abs(counts["00"] / 1024 - 0.5) < 0.06


@pytest.mark.parametrize("case,parameters", [
    ("unknown", {}), ("spend", []), ("spend", {"code": "1 + 1"}),
    ("concentration", {"mass": "__import__('os')"}),
    ("concentration", {"mass": True}), ("concentration", {"volume": 0}),
    ("concentration", {"mass": float("nan")}),
    ("concentration", {"mass": float("inf")}),
    ("concentration", {"volume_uncertainty": 1}),
    ("bell", {"shots": 64.5}), ("bell", {"shots": 1000000}),
    ("bell", {"seed": -1}), ("spend", {"input_rate": -1}),
])
def test_rejects_invalid_inputs(case, parameters):
    with pytest.raises(ValueError):
        evaluate(case, parameters)


def test_lognormal_ratio_matches_scipy_distribution():
    from scipy.stats import lognorm

    report = evaluate("concentration", {"method": "lognormal", "volume_uncertainty": 1})
    result = report["result"]
    # Independent reference built with SciPy's distribution API.
    mass_log_variance = np.log(1 + (0.1 / 10) ** 2)
    volume_log_variance = np.log(1 + (1 / 2) ** 2)
    scale = (10 / np.exp(mass_log_variance / 2)) / (2 / np.exp(volume_log_variance / 2))
    reference = lognorm(s=np.sqrt(mass_log_variance + volume_log_variance), scale=scale)
    assert result["mean"] == pytest.approx(reference.mean())
    assert result["standard_deviation"] == pytest.approx(reference.std())
    assert result["median"] == pytest.approx(reference.median())
    assert result["interval"]["lower"] == pytest.approx(reference.ppf(0.025))
    assert result["interval"]["upper"] == pytest.approx(reference.ppf(0.975))
    assert result["nominal_ratio"] == 5
    assert result["mean"] == pytest.approx(6.25)
    assert report["inputs"]["volume_uncertainty"] == 1
    assert report["method"] == "lognormal"
    assert "Python math and SciPy" in report["analysis"]


def test_lognormal_matches_independent_seeded_sampling():
    rng = np.random.default_rng(2026)
    mass = rng.lognormal(np.log(10) - np.log(1.0001) / 2, np.sqrt(np.log(1.0001)), 200000)
    volume = rng.lognormal(np.log(2) - np.log(1.25) / 2, np.sqrt(np.log(1.25)), 200000)
    ratios = mass / volume
    result = evaluate("concentration", {"method": "lognormal", "volume_uncertainty": 1})["result"]
    assert np.mean(ratios) == pytest.approx(result["mean"], rel=0.01)
    assert np.std(ratios) == pytest.approx(result["standard_deviation"], rel=0.02)
    assert np.quantile(ratios, [0.025, 0.975]) == pytest.approx(
        [result["interval"]["lower"], result["interval"]["upper"]], rel=0.02
    )


def test_lognormal_constant_inputs_and_small_error_limit():
    result = evaluate("concentration", {
        "method": "lognormal", "mass_uncertainty": 0, "volume_uncertainty": 0,
    })["result"]
    for field in ("mean", "median", "nominal_ratio"):
        assert result[field] == pytest.approx(5)
    assert result["standard_deviation"] == 0
    assert result["interval"]["lower"] == result["interval"]["upper"]
    small = {"mass_uncertainty": 0.001, "volume_uncertainty": 0.0002}
    first_order = evaluate("concentration", small)["result"]
    nonlinear = evaluate("concentration", {**small, "method": "lognormal"})["result"]
    assert nonlinear["mean"] == pytest.approx(first_order["nominal"], rel=1e-7)
    assert nonlinear["standard_deviation"] == pytest.approx(first_order["uncertainty"], rel=1e-7)


@pytest.mark.parametrize("mass,volume,dm,dv", [
    (1e-6, 1e-6, 1e5, 1e5), (1e6, 1e-6, 0, 1e5),
    (1e-6, 1e6, 1e5, 0), (1e6, 1e6, 1e5, 1e5),
    (10, 2, 0, 1), (10, 2, 1, 0),
])
def test_lognormal_boundaries_serialize_without_nonfinite_numbers(mass, volume, dm, dv):
    import json

    report = evaluate("concentration", {
        "method": "lognormal", "mass": mass, "volume": volume,
        "mass_uncertainty": dm, "volume_uncertainty": dv,
    })
    json.dumps(report, allow_nan=False)
    assert report["result"]["interval"]["lower"] > 0
    assert report["result"]["interval"]["upper"] >= report["result"]["interval"]["lower"]


@pytest.mark.parametrize("parameters", [
    {"method": "unknown"}, {"method": []}, {"method": None},
    {"method": "lognormal", "mass": 0}, {"method": "lognormal", "mass": 1e-20},
    {"method": "lognormal", "volume": 0},
    {"method": "lognormal", "volume_uncertainty": -1},
    {"method": "lognormal", "mass_uncertainty": float("inf")},
])
def test_lognormal_rejects_invalid_inputs(parameters):
    with pytest.raises(ValueError):
        evaluate("concentration", parameters)


def test_method_selection_does_not_weaken_first_order_guard():
    with pytest.raises(ValueError, match="do not reduce"):
        evaluate("concentration", {"method": "first_order", "volume_uncertainty": 1})
    assert evaluate("concentration", {"volume_uncertainty": 0.2})["result"]["nominal"] == 5
    with pytest.raises(ValueError, match="Unknown parameter"):
        evaluate("spend", {"method": "lognormal"})
    with pytest.raises(ValueError):
        evaluate([], {})


def test_lognormal_repeatable_and_preserves_global_rng():
    before = np.random.get_state()
    parameters = {"method": "lognormal", "volume_uncertainty": 1}
    report = evaluate("concentration", parameters)
    assert report["result"] == evaluate("concentration", parameters)["result"]
    after = np.random.get_state()
    assert before[0] == after[0] and np.array_equal(before[1], after[1])
    assert before[2:] == after[2:]


def test_precision_insights_identify_volume_and_solve_target():
    parameters = {"method": "lognormal", "volume_uncertainty": 1}
    report = evaluate("concentration", parameters)
    insights = report["insights"]
    assert parameters == {"method": "lognormal", "volume_uncertainty": 1}
    assert report["inputs"]["volume_uncertainty"] == 1
    assert insights["relative_sd"] == pytest.approx(report["result"]["standard_deviation"] / report["result"]["mean"])
    assert insights["contributions"]["dominant"] == "volume"
    assert insights["contributions"]["shares"]["volume"] == pytest.approx(0.9995520811150688)
    assert "log(concentration)" in insights["contributions"]["basis"]
    mass, volume = insights["requirements"]
    assert mass["status"] == "unreachable_alone"
    assert mass["max_sd"] is None
    assert volume["max_sd"] == pytest.approx(0.09797469109923441)
    # Verify the inverse design solution through the independently tested forward model.
    solved = evaluate("concentration", {**parameters, "volume_uncertainty": volume["max_sd"]})
    assert solved["result"]["standard_deviation"] / solved["result"]["mean"] == pytest.approx(0.05)
    assert solved["insights"]["meets_target"]
    assert insights["scenarios"][-1]["label"] == "Volume SD at target"
    assert insights["scenarios"][-1]["meets_target"]


@pytest.mark.parametrize("method", ["first_order", "lognormal"])
def test_precision_scenarios_match_fresh_calculations(method):
    parameters = {"method": method, "mass_uncertainty": 1, "volume_uncertainty": 0.1,
                  "target_relative_sd_percent": 8}
    report = evaluate("concentration", parameters)
    for scenario in report["insights"]["scenarios"]:
        fresh = evaluate("concentration", {**parameters, "mass_uncertainty": scenario["mass_sd"],
                                           "volume_uncertainty": scenario["volume_sd"]})
        assert scenario["relative_sd"] == pytest.approx(fresh["insights"]["relative_sd"])
        if method == "lognormal":
            assert scenario["result"]["interval"] == fresh["result"]["interval"]
        else:
            assert scenario["result"]["standard_deviation"] == pytest.approx(fresh["result"]["uncertainty"])
    assert report["insights"]["contributions"]["dominant"] == "mass"
    requirement = report["insights"]["requirements"][0]
    assert requirement["status"] == "reduce_uncertainty"
    at_target = evaluate("concentration", {**parameters, "mass_uncertainty": requirement["max_sd"]})
    assert at_target["insights"]["relative_sd"] == pytest.approx(0.08)


def test_target_changes_planning_not_observed_result():
    parameters = {"method": "lognormal", "volume_uncertainty": 1}
    strict = evaluate("concentration", {**parameters, "target_relative_sd_percent": 1})
    loose = evaluate("concentration", {**parameters, "target_relative_sd_percent": 60})
    assert strict["result"] == loose["result"]
    assert not strict["insights"]["meets_target"]
    assert loose["insights"]["meets_target"]
    assert strict["insights"]["requirements"][1]["max_sd"] == 0


@pytest.mark.parametrize("method", ["first_order", "lognormal"])
def test_deterministic_measurements_do_not_claim_perfect_accuracy(method):
    report = evaluate("concentration", {"method": method, "mass_uncertainty": 0, "volume_uncertainty": 0})
    insights = report["insights"]
    assert insights["contributions"]["dominant"] is None
    assert insights["contributions"]["shares"] == {"mass": 0, "volume": 0}
    assert insights["meets_target"]
    assert "does not establish perfect accuracy" in insights["summary"]


@pytest.mark.parametrize("mass", [0, 1e-10])
def test_zero_and_near_zero_mass_disable_relative_planning(mass):
    import json

    report = evaluate("concentration", {"mass": mass})
    assert not report["insights"]["available"]
    assert "absolute" in report["insights"]["summary"]
    json.dumps(report, allow_nan=False)


def test_balanced_contributors_and_unreachable_single_input_targets():
    report = evaluate("concentration", {"mass_uncertainty": 1, "volume_uncertainty": 0.2})
    assert report["insights"]["contributions"]["dominant"] == "balanced"
    assert report["insights"]["contributions"]["shares"] == {"mass": 0.5, "volume": 0.5}
    assert all(r["status"] == "unreachable_alone" for r in report["insights"]["requirements"])


@pytest.mark.parametrize("target", [0, -1, 101, True, "5", float("nan"), float("inf")])
def test_precision_target_input_validation(target):
    with pytest.raises(ValueError):
        evaluate("concentration", {"target_relative_sd_percent": target})


def test_small_literals_preserve_actual_numerical_values():
    result = evaluate("concentration", {"mass": 1e-10, "mass_uncertainty": 1e-12})["result"]
    assert result["nominal"] == pytest.approx(5e-11, rel=1e-12, abs=0)
    assert result["uncertainty"] == pytest.approx(math.hypot(1e-12 / 2, 1e-10 * 0.02 / 4), rel=1e-12, abs=0)
    lognormal = evaluate("concentration", {"method": "lognormal", "mass": 1e-6, "volume": 1e-6})
    assert lognormal["result"]["nominal_ratio"] == 1
    spend = evaluate("spend", {"input_rate": 1e-8, "output_rate": 0})
    assert spend["result"]["nominal"] == pytest.approx(2e-7, rel=1e-12, abs=0)
