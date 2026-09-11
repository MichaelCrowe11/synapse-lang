"""Bounded validation of first-order uncertainty propagation on telemetry-shaped inputs.

Three derived quantities are computed from a sensor triple (temperature in C, relative
humidity in percent, CO2 in ppm):

  vapour-pressure deficit   Tetens saturation pressure times (1 - RH/100), kPa
  dew point                 Magnus form, C
  CO2 excess                (CO2 - ambient) / ambient, dimensionless, ambient fixed at 420 ppm

For every selected row three results are compared:

  library    UncertaintyEngine (first-order, numerical partial derivatives) applied to the
             same callable the analytic reference uses
  analytic   NumPy formulas with hand-derived partial derivatives, written independently of
             the library
  monte      Monte Carlo on the assumed input distributions

The operator-chain form of the library (building the expression from UncertainValue
arithmetic) is evaluated as a third gated column. UncertainValue tracks the sources each
result depends on, so a variable that appears twice in an expression is the same variable
and the chain must reproduce the analytic first-order sigma to rounding. Before 2026-09-10
the chain treated repeated variables as independent and overestimated by about nine percent
on the Tetens exponent alone; that defect is what this column now guards against.

Acceptance criteria are fixed in this module before any dataset is opened. Datasets never
enter the repository: the command-line entry point takes a SQLite or CSV path plus a
provenance label, and the report states plainly whether the fixture was synthetic.

Input model. The stated accuracies are treated as provisional rectangular error bounds:
temperature +/- 0.8 C, humidity +/- 6 percentage points, CO2 +/- (40 ppm + 5 percent of the
reading). Each bound becomes a standard uncertainty of bound / sqrt(3) and a uniform
Monte Carlo draw. These are assumed distributions, not calibrated standard uncertainties;
input independence is unverified, and sensor bias does not average away with more rows.
"""
from __future__ import annotations

import csv
import math
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from .uncertainty import PropagationMethod, UncertaintyConfig, UncertaintyEngine, UncertainValue

AMBIENT_CO2_PPM = 420.0
TETENS_A_KPA, TETENS_B, TETENS_C = 0.6108, 17.27, 237.3
MAGNUS_B, MAGNUS_C = 17.62, 243.12
SQRT3 = math.sqrt(3.0)

THRESHOLDS = {
    # library versus independent analytic first-order reference, in output units
    "library_vs_analytic_abs": 1e-10,
    "library_vs_analytic_rel": 1e-8,
    # operator-chain form (UncertainValue arithmetic) versus the analytic reference
    "chain_vs_analytic_abs": 1e-12,
    "chain_vs_analytic_rel": 1e-9,
    # each first-order result versus Monte Carlo
    "mc_mean_fraction_of_sd": 0.10,
    "mc_mean_standard_errors": 4.0,
    "mc_sd_fraction": 0.05,
    "mc_sd_standard_errors": 4.0,
    "mc_batches": 10,
}

ASSUMPTIONS = (
    "Rectangular error bounds from the sensor's stated accuracy: temperature 0.8 C, humidity "
    "6 percentage points, CO2 40 ppm plus 5 percent of the reading. Standard uncertainty is "
    "bound / sqrt(3); Monte Carlo draws are uniform within the bound. These are assumed "
    "distributions, not calibrated standard uncertainties; independence of the three inputs "
    "is unverified; bias does not average away. Ambient CO2 is fixed at 420 ppm by assumption."
)


def error_bound(kind: str, value: float) -> float:
    if kind == "temperature_c":
        return 0.8
    if kind == "humidity_pct":
        return 6.0
    if kind == "co2_ppm":
        return 40.0 + 0.05 * abs(value)
    raise KeyError(kind)


def standard_uncertainty(kind: str, value: float) -> float:
    return error_bound(kind, value) / SQRT3


# ── independent analytic reference (NumPy, hand-derived partials) ─────────────

def saturation_vapour_pressure_kpa(t):
    return TETENS_A_KPA * np.exp(TETENS_B * t / (t + TETENS_C))


def vpd_kpa(t, rh):
    return saturation_vapour_pressure_kpa(t) * (1.0 - rh / 100.0)


def vpd_partials(t, rh):
    es = saturation_vapour_pressure_kpa(t)
    des_dt = es * TETENS_B * TETENS_C / (t + TETENS_C) ** 2
    return des_dt * (1.0 - rh / 100.0), -es / 100.0


def dew_point_c(t, rh):
    gamma = np.log(rh / 100.0) + MAGNUS_B * t / (MAGNUS_C + t)
    return MAGNUS_C * gamma / (MAGNUS_B - gamma)


def dew_partials(t, rh):
    gamma = np.log(rh / 100.0) + MAGNUS_B * t / (MAGNUS_C + t)
    dgamma_dt = MAGNUS_B * MAGNUS_C / (MAGNUS_C + t) ** 2
    dgamma_drh = 1.0 / rh
    dtd_dgamma = MAGNUS_C * MAGNUS_B / (MAGNUS_B - gamma) ** 2
    return dtd_dgamma * dgamma_dt, dtd_dgamma * dgamma_drh


def co2_excess(c):
    return (c - AMBIENT_CO2_PPM) / AMBIENT_CO2_PPM


def co2_partials(c):
    return (np.ones_like(np.asarray(c, dtype=float)) / AMBIENT_CO2_PPM,)


# Scalar callables shared by the library engine and the analytic reference. They use the
# math module so the engine's finite differences run on plain floats.
def _vpd_scalar(t: float, rh: float) -> float:
    return TETENS_A_KPA * math.exp(TETENS_B * t / (t + TETENS_C)) * (1.0 - rh / 100.0)


def _dew_scalar(t: float, rh: float) -> float:
    gamma = math.log(rh / 100.0) + MAGNUS_B * t / (MAGNUS_C + t)
    return MAGNUS_C * gamma / (MAGNUS_B - gamma)


def _co2_scalar(c: float) -> float:
    return (c - AMBIENT_CO2_PPM) / AMBIENT_CO2_PPM


QUANTITIES = {
    # name: (scalar callable, vector formula, vector partials, input kinds)
    "vpd_kpa": (_vpd_scalar, vpd_kpa, vpd_partials, ("temperature_c", "humidity_pct")),
    "dew_point_c": (_dew_scalar, dew_point_c, dew_partials, ("temperature_c", "humidity_pct")),
    "co2_excess": (_co2_scalar, co2_excess, co2_partials, ("co2_ppm",)),
}


# ── the three legs ───────────────────────────────────────────────────────────

def analytic_first_order(name: str, values: dict[str, float]) -> tuple[float, float]:
    _, formula, partials, kinds = QUANTITIES[name]
    args = [values[k] for k in kinds]
    nominal = float(formula(*args))
    grads = partials(*args)
    sigma = math.sqrt(sum((float(g) * standard_uncertainty(k, values[k])) ** 2 for g, k in zip(grads, kinds, strict=True)))
    return nominal, sigma


def library_first_order(name: str, values: dict[str, float]) -> tuple[float, float]:
    scalar, _, _, kinds = QUANTITIES[name]
    engine = UncertaintyEngine(UncertaintyConfig(method=PropagationMethod.LINEAR, cache_results=False))
    variables = {k: UncertainValue(values[k], standard_uncertainty(k, values[k])) for k in kinds}
    result = engine.propagate(scalar, variables)
    return float(result.nominal), float(result.uncertainty)


def operator_chain_first_order(name: str, values: dict[str, float]) -> tuple[float, float]:
    """The library's arithmetic form: the formula written with UncertainValue operators.

    Gated: with source tracking the repeated variable t is one variable, so this must
    match the analytic first-order sigma to rounding.
    """
    if name == "co2_excess":
        c = UncertainValue(values["co2_ppm"], standard_uncertainty("co2_ppm", values["co2_ppm"]))
        r = (c - AMBIENT_CO2_PPM) / AMBIENT_CO2_PPM
        return float(r.nominal), float(r.uncertainty)
    t = UncertainValue(values["temperature_c"], standard_uncertainty("temperature_c", values["temperature_c"]))
    rh = UncertainValue(values["humidity_pct"], standard_uncertainty("humidity_pct", values["humidity_pct"]))
    if name == "vpd_kpa":
        es = (t * TETENS_B / (t + TETENS_C)).exp() * TETENS_A_KPA
        r = es * (1.0 - rh / 100.0)
    else:
        gamma = (rh / 100.0).log() + t * MAGNUS_B / (t + MAGNUS_C)
        r = gamma * MAGNUS_C / (MAGNUS_B - gamma)
    return float(r.nominal), float(r.uncertainty)


@dataclass
class MonteCarlo:
    mean: float
    sd: float
    se_mean: float
    se_sd: float
    draws: int
    invalid_draws: int


def monte_carlo(name: str, values: dict[str, float], draws: int, seed: int) -> MonteCarlo:
    _, formula, _, kinds = QUANTITIES[name]
    rng = np.random.default_rng(seed)
    samples = []
    for k in kinds:
        b = error_bound(k, values[k])
        samples.append(rng.uniform(values[k] - b, values[k] + b, size=draws))
    invalid = 0
    if "humidity_pct" in kinds:
        rh = samples[kinds.index("humidity_pct")]
        bad = rh <= 0.0
        invalid = int(bad.sum())
        if invalid:
            # never clip: drop the invalid draws and report them
            keep = ~bad
            samples = [s[keep] for s in samples]
    out = np.asarray(formula(*samples), dtype=float)
    batches = THRESHOLDS["mc_batches"]
    parts = np.array_split(out, batches)
    means = np.array([p.mean() for p in parts])
    sds = np.array([p.std(ddof=1) for p in parts])
    return MonteCarlo(
        mean=float(out.mean()), sd=float(out.std(ddof=1)),
        se_mean=float(means.std(ddof=1) / math.sqrt(batches)),
        se_sd=float(sds.std(ddof=1) / math.sqrt(batches)),
        draws=int(out.size), invalid_draws=invalid,
    )


# ── comparison ───────────────────────────────────────────────────────────────

def _within(err: float, ref: float) -> bool:
    return abs(err) <= THRESHOLDS["library_vs_analytic_abs"] + THRESHOLDS["library_vs_analytic_rel"] * abs(ref)


def _chain_within(err: float, ref: float) -> bool:
    return abs(err) <= THRESHOLDS["chain_vs_analytic_abs"] + THRESHOLDS["chain_vs_analytic_rel"] * abs(ref)


def compare_row(values: dict[str, float], draws: int, seed: int) -> dict:
    row: dict = {"inputs": dict(values), "quantities": {}}
    for q_index, name in enumerate(QUANTITIES):
        a_nom, a_sig = analytic_first_order(name, values)
        l_nom, l_sig = library_first_order(name, values)
        c_nom, c_sig = operator_chain_first_order(name, values)
        mc = monte_carlo(name, values, draws, seed * 1000 + q_index)
        mean_tol = THRESHOLDS["mc_mean_fraction_of_sd"] * mc.sd + THRESHOLDS["mc_mean_standard_errors"] * mc.se_mean
        sd_tol = THRESHOLDS["mc_sd_fraction"] * mc.sd + THRESHOLDS["mc_sd_standard_errors"] * mc.se_sd
        checks = {
            "library_nominal_matches_analytic": _within(l_nom - a_nom, a_nom),
            "library_sigma_matches_analytic": _within(l_sig - a_sig, a_sig),
            "chain_nominal_matches_analytic": _chain_within(c_nom - a_nom, a_nom),
            "chain_sigma_matches_analytic": _chain_within(c_sig - a_sig, a_sig),
            "analytic_mean_within_mc": abs(a_nom - mc.mean) <= mean_tol,
            "analytic_sigma_within_mc": abs(a_sig - mc.sd) <= sd_tol,
            "library_mean_within_mc": abs(l_nom - mc.mean) <= mean_tol,
            "library_sigma_within_mc": abs(l_sig - mc.sd) <= sd_tol,
        }
        row["quantities"][name] = {
            "analytic": {"nominal": a_nom, "sigma": a_sig},
            "library": {"nominal": l_nom, "sigma": l_sig},
            "operator_chain": {"nominal": c_nom, "sigma": c_sig},
            "monte_carlo": asdict(mc),
            "tolerances": {"mean": mean_tol, "sd": sd_tol},
            "errors": {"library_minus_analytic_nominal": l_nom - a_nom, "library_minus_analytic_sigma": l_sig - a_sig,
                       "chain_minus_analytic_sigma": c_sig - a_sig,
                       "analytic_minus_mc_mean": a_nom - mc.mean, "analytic_sigma_minus_mc_sd": a_sig - mc.sd},
            "checks": checks,
        }
    return row


# ── data access (datasets stay outside the repository) ───────────────────────

def select_rows(rows: list[dict], n: int) -> list[dict]:
    """Deterministic: sort by timestamp and take evenly spaced rows."""
    rows = sorted(rows, key=lambda r: r["ts"])
    if len(rows) <= n:
        return rows
    idx = np.linspace(0, len(rows) - 1, n).round().astype(int)
    return [rows[i] for i in idx]


def load_sqlite(path: str | Path, node: str | None = None, schema: str = "auto") -> list[dict]:
    """Read aligned temperature, humidity and CO2 rows from a readings table.

    schema "relay": readings(node_id, ts, metric, value)   schema "rig": readings(node, epoch, metric, value)
    """
    con = sqlite3.connect(f"file:{Path(path)}?mode=ro", uri=True)
    cols = {r[1] for r in con.execute("PRAGMA table_info(readings)")}
    if schema == "auto":
        schema = "relay" if "node_id" in cols else "rig"
    node_col, ts_col = ("node_id", "ts") if schema == "relay" else ("node", "epoch")
    where = f"WHERE {node_col} = ?" if node else ""
    params = (node,) if node else ()
    sql = (f"SELECT t.{ts_col} AS ts, t.value AS temperature_c, h.value AS humidity_pct, c.value AS co2_ppm "
           f"FROM readings t JOIN readings h ON h.{node_col} = t.{node_col} AND h.{ts_col} = t.{ts_col} AND h.metric = 'humidity_pct' "
           f"LEFT JOIN readings c ON c.{node_col} = t.{node_col} AND c.{ts_col} = t.{ts_col} AND c.metric = 'co2_ppm' "
           f"{where.replace(node_col, 't.' + node_col)} {'AND' if where else 'WHERE'} t.metric = 'temperature_c' ORDER BY t.{ts_col}")
    rows = [dict(ts=float(r[0]), temperature_c=float(r[1]), humidity_pct=float(r[2]), co2_ppm=(float(r[3]) if r[3] is not None else None))
            for r in con.execute(sql, params)]
    con.close()
    return [r for r in rows if r["co2_ppm"] is not None]


def load_csv(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return [dict(ts=float(r["ts"]), temperature_c=float(r["temperature_c"]), humidity_pct=float(r["humidity_pct"]), co2_ppm=float(r["co2_ppm"]))
                for r in csv.DictReader(fh)]


# ── the run ──────────────────────────────────────────────────────────────────

def run(rows: list[dict], *, draws: int, seed: int, provenance: str, fixture_status: str, sample: int = 128) -> dict:
    selected = select_rows(rows, sample)
    results = [compare_row({k: r[k] for k in ("temperature_c", "humidity_pct", "co2_ppm")}, draws, seed + i) for i, r in enumerate(selected)]
    summary: dict = {}
    for name in QUANTITIES:
        checks = {k: 0 for k in results[0]["quantities"][name]["checks"]} if results else {}
        maxima = {"library_minus_analytic_nominal": 0.0, "library_minus_analytic_sigma": 0.0, "chain_minus_analytic_sigma": 0.0, "analytic_minus_mc_mean": 0.0, "analytic_sigma_minus_mc_sd": 0.0}
        invalid = 0
        for r in results:
            q = r["quantities"][name]
            for k, ok in q["checks"].items():
                checks[k] += 0 if ok else 1
            for k in maxima:
                maxima[k] = max(maxima[k], abs(q["errors"][k]))
            invalid += q["monte_carlo"]["invalid_draws"]
        summary[name] = {"violations": checks, "max_abs_errors": maxima, "invalid_monte_carlo_draws": invalid}
    library_ok = all(v["violations"]["library_nominal_matches_analytic"] == 0 and v["violations"]["library_sigma_matches_analytic"] == 0 for v in summary.values())
    chain_ok = all(v["violations"]["chain_nominal_matches_analytic"] == 0 and v["violations"]["chain_sigma_matches_analytic"] == 0 for v in summary.values())
    first_order_ok = all(all(v["violations"][k] == 0 for k in ("analytic_mean_within_mc", "analytic_sigma_within_mc", "library_mean_within_mc", "library_sigma_within_mc")) for v in summary.values())
    label = ("synthetic-fixture software-correctness validation; real-data gate unmet"
             if fixture_status.lower().startswith("synth") else "candidate real-data validation; see provenance")
    return {
        "label": label, "fixture_status": fixture_status, "provenance": provenance, "assumptions": ASSUMPTIONS,
        "thresholds": THRESHOLDS, "rows_available": len(rows), "rows_evaluated": len(selected), "monte_carlo_draws_per_row": draws, "seed": seed,
        "verdicts": {"library_matches_analytic_reference": library_ok, "operator_chain_matches_analytic_reference": chain_ok,
                     "first_order_adequate_against_monte_carlo": first_order_ok},
        "summary": summary, "rows": results,
    }


def to_markdown(report: dict) -> str:
    lines = [f"# Uncertainty propagation validation: {report['label']}", "",
             f"Provenance: {report['provenance']}", "", f"Assumptions: {report['assumptions']}", "",
             f"Rows evaluated: {report['rows_evaluated']} of {report['rows_available']} available; {report['monte_carlo_draws_per_row']} Monte Carlo draws per row; seed {report['seed']}.", "",
             "| quantity | library vs analytic (nominal, sigma violations) | chain vs analytic (nominal, sigma violations) | first-order vs Monte Carlo (mean, sd violations; analytic / library) | max abs error library-analytic sigma | max abs error chain-analytic sigma | max abs error analytic sigma - MC sd | invalid draws |",
             "|---|---|---|---|---|---|---|---|"]
    for name, s in report["summary"].items():
        v = s["violations"]
        m = s["max_abs_errors"]
        cells = [
            name,
            f"{v['library_nominal_matches_analytic']}, {v['library_sigma_matches_analytic']}",
            f"{v['chain_nominal_matches_analytic']}, {v['chain_sigma_matches_analytic']}",
            f"{v['analytic_mean_within_mc']}, {v['analytic_sigma_within_mc']} / "
            f"{v['library_mean_within_mc']}, {v['library_sigma_within_mc']}",
            f"{m['library_minus_analytic_sigma']:.3e}",
            f"{m['chain_minus_analytic_sigma']:.3e}",
            f"{m['analytic_sigma_minus_mc_sd']:.3e}",
            str(s["invalid_monte_carlo_draws"]),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    v = report["verdicts"]
    lines += ["", f"Library engine matches the independent analytic reference: {v['library_matches_analytic_reference']}.",
              f"Operator-chain form (UncertainValue arithmetic, repeated variables tracked) matches the analytic reference: {v['operator_chain_matches_analytic_reference']}.",
              f"First-order propagation adequate against Monte Carlo at these inputs: {v['first_order_adequate_against_monte_carlo']}.", ""]
    return "\n".join(lines)
