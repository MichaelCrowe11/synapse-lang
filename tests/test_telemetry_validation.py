"""The telemetry validation harness: library against an independent analytic reference and Monte Carlo.

Uses a small built-in fixture so CI needs no dataset. Thresholds are the module's predeclared ones.
"""
import math

import numpy as np
import pytest

from synapse_lang import telemetry_validation as tv

FIXTURE = [
    {"ts": 1.0, "temperature_c": 17.4, "humidity_pct": 94.3, "co2_ppm": 550.0},
    {"ts": 2.0, "temperature_c": 19.6, "humidity_pct": 78.1, "co2_ppm": 634.0},
    {"ts": 3.0, "temperature_c": 21.0, "humidity_pct": 86.0, "co2_ppm": 956.0},
    {"ts": 4.0, "temperature_c": 22.8, "humidity_pct": 80.5, "co2_ppm": 1200.0},
    {"ts": 5.0, "temperature_c": 24.5, "humidity_pct": 75.6, "co2_ppm": 1600.0},
    {"ts": 6.0, "temperature_c": 20.2, "humidity_pct": 90.0, "co2_ppm": 420.0},
]


def test_hand_derived_partials_match_finite_differences():
    t, rh, c, h = 21.0, 86.0, 956.0, 1e-5
    dt, drh = tv.vpd_partials(t, rh)
    assert dt == pytest.approx((tv.vpd_kpa(t + h, rh) - tv.vpd_kpa(t - h, rh)) / (2 * h), rel=1e-6)
    assert drh == pytest.approx((tv.vpd_kpa(t, rh + h) - tv.vpd_kpa(t, rh - h)) / (2 * h), rel=1e-6)
    dt, drh = tv.dew_partials(t, rh)
    assert dt == pytest.approx((tv.dew_point_c(t + h, rh) - tv.dew_point_c(t - h, rh)) / (2 * h), rel=1e-6)
    assert drh == pytest.approx((tv.dew_point_c(t, rh + h) - tv.dew_point_c(t, rh - h)) / (2 * h), rel=1e-6)
    (dc,) = tv.co2_partials(c)
    assert float(dc) == pytest.approx(1.0 / tv.AMBIENT_CO2_PPM)


def test_standard_uncertainty_is_bound_over_root_three():
    assert tv.standard_uncertainty("temperature_c", 21.0) == pytest.approx(0.8 / math.sqrt(3))
    assert tv.standard_uncertainty("co2_ppm", 1000.0) == pytest.approx((40 + 50) / math.sqrt(3))


@pytest.mark.parametrize("name", list(tv.QUANTITIES))
def test_library_engine_matches_analytic_reference_on_fixture(name):
    for row in FIXTURE:
        values = {k: row[k] for k in ("temperature_c", "humidity_pct", "co2_ppm")}
        a_nom, a_sig = tv.analytic_first_order(name, values)
        l_nom, l_sig = tv.library_first_order(name, values)
        assert abs(l_nom - a_nom) <= tv.THRESHOLDS["library_vs_analytic_abs"] + tv.THRESHOLDS["library_vs_analytic_rel"] * abs(a_nom), (name, row)
        assert abs(l_sig - a_sig) <= tv.THRESHOLDS["library_vs_analytic_abs"] + tv.THRESHOLDS["library_vs_analytic_rel"] * abs(a_sig), (name, row, l_sig, a_sig)


def test_first_order_is_adequate_against_monte_carlo_on_fixture():
    report = tv.run(FIXTURE, draws=40_000, seed=7, provenance="built-in fixture", fixture_status="synthetic", sample=6)
    assert report["rows_evaluated"] == 6
    assert report["verdicts"]["library_matches_analytic_reference"], report["summary"]
    assert report["verdicts"]["first_order_adequate_against_monte_carlo"], report["summary"]
    assert report["label"].startswith("synthetic-fixture")
    assert "real-data gate unmet" in report["label"]


def test_operator_chain_overestimates_when_a_variable_repeats():
    # The Tetens exponent B*t/(t+C) uses t twice. The arithmetic form treats the two
    # occurrences as independent, so its sigma exceeds the exact first-order sigma
    # (about nine percent here). In the full VPD the humidity term dominates, so the
    # effect on the final number is small; that is why it is reported, not gated.
    from synapse_lang.uncertainty import UncertainValue
    t = UncertainValue(21.0, tv.standard_uncertainty("temperature_c", 21.0))
    chain = t * tv.TETENS_B / (t + tv.TETENS_C)
    exact = tv.TETENS_B * tv.TETENS_C / (21.0 + tv.TETENS_C) ** 2 * t.uncertainty
    assert chain.uncertainty > exact * 1.05
    values = {"temperature_c": 21.0, "humidity_pct": 86.0, "co2_ppm": 956.0}
    _, a_sig = tv.analytic_first_order("vpd_kpa", values)
    _, c_sig = tv.operator_chain_first_order("vpd_kpa", values)
    assert c_sig > a_sig, "the arithmetic form should not understate"
    _, a_sig = tv.analytic_first_order("co2_excess", values)
    _, c_sig = tv.operator_chain_first_order("co2_excess", values)
    assert c_sig == pytest.approx(a_sig, rel=1e-12), "no repeated variable, so the chain must agree"


def test_monte_carlo_never_clips_and_reports_invalid_draws():
    values = {"temperature_c": 21.0, "humidity_pct": 3.0, "co2_ppm": 956.0}   # humidity bound of 6 reaches below zero
    mc = tv.monte_carlo("dew_point_c", values, draws=20_000, seed=3)
    assert mc.invalid_draws > 0
    assert mc.draws + mc.invalid_draws == 20_000
    assert np.isfinite(mc.mean) and np.isfinite(mc.sd)


def test_select_rows_is_deterministic_and_time_ordered():
    rows = [{"ts": float(t)} for t in range(1000, 0, -1)]
    picked = tv.select_rows(rows, 10)
    assert [r["ts"] for r in picked] == sorted(r["ts"] for r in picked)
    assert picked == tv.select_rows(rows, 10)
    assert picked[0]["ts"] == 1.0 and picked[-1]["ts"] == 1000.0
