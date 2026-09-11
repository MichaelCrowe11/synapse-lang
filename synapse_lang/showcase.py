"""Bounded interpreter demonstrations and explicit nonlinear research analysis."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import Decimal

from . import __version__, execute

CASES = {
    "concentration": {
        "title": "Research concentration",
        "fields": {
            "mass": (10.0, 0.0, 1e6),
            "mass_uncertainty": (0.1, 0.0, 1e5),
            "volume": (2.0, 1e-6, 1e6),
            "volume_uncertainty": (0.02, 0.0, 1e5),
            "target_relative_sd_percent": (5.0, 0.1, 100.0),
        },
    },
    "spend": {
        "title": "Inference spend forecast",
        "fields": {
            "requests": (10000.0, 0.0, 1e9),
            "requests_uncertainty": (1000.0, 0.0, 1e8),
            "input_tokens": (2000.0, 0.0, 1e6),
            "output_tokens": (500.0, 0.0, 1e6),
            "input_rate": (1.0, 0.0, 1e4),
            "output_rate": (4.0, 0.0, 1e4),
        },
    },
    "bell": {
        "title": "Bell-state simulation",
        "fields": {"shots": (1024, 64, 8192), "seed": (42, 0, 2147483647)},
    },
}


def evaluate(case: str, parameters: dict) -> dict:
    """Evaluate one fixed example, never caller-supplied code or callables."""
    if not isinstance(case, str) or case not in CASES or not isinstance(parameters, dict):
        raise ValueError("Choose a supported example and numeric parameters")
    fields = CASES[case]["fields"]
    method = parameters.get("method", "first_order") if case == "concentration" else None
    if case == "concentration" and method not in ("first_order", "lognormal"):
        raise ValueError("Choose first_order or lognormal concentration analysis")
    allowed = set(fields) | ({"method"} if case == "concentration" else set())
    if set(parameters) - allowed:
        raise ValueError("Unknown parameter")
    values = {}
    for name, (default, lower, upper) in fields.items():
        value = parameters.get(name, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")
        if not math.isfinite(value) or not lower <= value <= upper:
            raise ValueError(f"{name} must be between {lower} and {upper}")
        if case == "bell" and int(value) != value:
            raise ValueError(f"{name} must be an integer")
        values[name] = value

    # Fixed decimal literals avoid unsupported exponent notation in the DSL lexer.
    literals = {name: format(Decimal(str(value)), "f") for name, value in values.items()}
    if case == "concentration":
        values["method"] = method
        if method == "first_order" and values["volume_uncertainty"] > 0.1 * values["volume"]:
            raise ValueError(
                "First-order propagation requires volume uncertainty at most 10%. "
                "Choose lognormal analysis only if independent positive lognormal inputs fit your data; "
                "do not reduce the measured uncertainty."
            )
        source = (
            f"uncertain mass = {literals['mass']} +/- {literals['mass_uncertainty']}\n"
            f"uncertain volume = {literals['volume']} +/- {literals['volume_uncertainty']}\n"
            "concentration = mass / volume\nconcentration"
        )
        assumptions = [
            "Mass in mg and volume in mL; inputs must already use these units.",
            "Independent input errors; uncertainties interpreted as standard deviations.",
            "First-order propagation, not a confidence interval or clinical validation.",
            "Research demonstration only, not for diagnosis, treatment, or dosing.",
        ]
        if method == "lognormal":
            if values["mass"] < 1e-6:
                raise ValueError("Lognormal analysis requires a mean mass of at least 0.000001 mg")
            source = (
                f"mass = {literals['mass']}\nvolume = {literals['volume']}\n"
                "concentration = mass / volume\nconcentration"
            )
            assumptions = [
                "Mass in mg and volume in mL; inputs must already use these units.",
                "Independent positive lognormal inputs, specified by arithmetic means and standard deviations.",
                "Zero input uncertainty denotes a constant. No negative values are clipped or discarded.",
                "The lognormal distribution is a modeling choice, not established by a mean and SD alone.",
                "Exact ratio-distribution moments and equal-tail 95% coverage interval under this model, "
                "not a confidence interval for an estimated mean.",
                "Correlated inputs, detection limits, and other distributions require a different analysis.",
                "Research demonstration only, not for diagnosis, treatment, or dosing.",
            ]
        unit = "mg/mL"
    elif case == "spend":
        source = (
            f"uncertain requests = {literals['requests']} +/- {literals['requests_uncertainty']}\n"
            f"input_tokens = {literals['input_tokens']}\noutput_tokens = {literals['output_tokens']}\n"
            f"input_rate = {literals['input_rate']}\noutput_rate = {literals['output_rate']}\n"
            "per_request = (input_tokens * input_rate + output_tokens * output_rate) / 1000000\n"
            "forecast = requests * per_request\nforecast"
        )
        assumptions = [
            "Illustrative user-entered USD rates per million tokens, not a live provider rate card.",
            "Token lengths and rates are fixed; only request volume is uncertain.",
            "Excludes cache discounts, retries, taxes, tools, and other provider charges.",
            "A forecast, not an invoice ledger; no billing or routing changes.",
        ]
        unit = "USD"
    else:
        source = (
            "quantum circuit bell(2) {\n    h(0)\n    cnot(0,1)\n}\n"
            f"run bell {{ shots: {int(values['shots'])} }}"
        )
        assumptions = [
            "Two-qubit software simulation, not quantum hardware or quantum advantage.",
            "Ideal Bell state: expected probabilities 00 = 0.5 and 11 = 0.5.",
            "Sampled frequencies vary; the seed is recorded for same-runtime reproducibility.",
        ]
        unit = "shots"

    if case == "bell":
        import numpy as np

        state = np.random.get_state()
        try:
            np.random.seed(int(values["seed"]))
            result = execute(source)
        finally:
            np.random.set_state(state)
        output = {"counts": result["counts"], "shots": result["shots"]}
    elif case == "concentration" and method == "lognormal":
        # The interpreter computes the nominal ratio; this helper computes the distribution.
        output = _lognormal_ratio(values)
        output["nominal_ratio"] = float(execute(source))
    else:
        result = execute(source)
        output = {"nominal": result.nominal, "uncertainty": result.uncertainty}
    report = {
        "engine": "synapse-lang", "version": __version__, "case": case,
        "inputs": values, "source": source, "result": output, "unit": unit,
        "method": method or ("ideal_statevector_sampling" if case == "bell" else "first_order"),
        "analysis": (
            "Synapse computes the nominal ratio. Python math and SciPy compute exact lognormal "
            "ratio statistics: s_i² = log1p((SD_i / mean_i)²); mu_i = log(mean_i) - s_i²/2; "
            "mu_ratio = mu_mass - mu_volume; s_ratio² = s_mass² + s_volume²; "
            "mean = exp(mu_ratio + s_ratio²/2); SD = mean * sqrt(expm1(s_ratio²)); "
            "quantile(p) = exp(mu_ratio + s_ratio * norm.ppf(p))."
            if method == "lognormal" else "Executed with the Synapse interpreter."
        ),
        "assumptions": assumptions, "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if case == "concentration":
        report["insights"] = _concentration_insights(values, output)
    return report


def _lognormal_ratio(values: dict) -> dict:
    """Exact independent lognormal ratio, with deterministic inputs as limiting cases."""
    from scipy.special import ndtri

    mass, volume = values["mass"], values["volume"]
    mass_s2 = math.log1p((values["mass_uncertainty"] / mass) ** 2)
    volume_s2 = math.log1p((values["volume_uncertainty"] / volume) ** 2)
    mu = math.log(mass) - mass_s2 / 2 - math.log(volume) + volume_s2 / 2
    variance = mass_s2 + volume_s2
    sigma = math.sqrt(variance)
    mean = math.exp(mu + variance / 2)
    return {
        "mean": mean,
        "standard_deviation": mean * math.sqrt(math.expm1(variance)),
        "median": math.exp(mu),
        "interval": {
            "probability": 0.95,
            "lower": math.exp(mu + sigma * float(ndtri(0.025))),
            "upper": math.exp(mu + sigma * float(ndtri(0.975))),
            "kind": "equal_tail_model_coverage",
        },
    }


def _concentration_insights(values: dict, output: dict) -> dict:
    """Explain uncertainty and solve bounded single-measurement design targets."""
    mass, volume = values["mass"], values["volume"]
    dm, dv = values["mass_uncertainty"], values["volume_uncertainty"]
    lognormal = values["method"] == "lognormal"
    target = values["target_relative_sd_percent"] / 100
    # At a zero nominal mass, relative precision has no finite interpretation.
    if mass < 1e-6:
        return {
            "available": False,
            "summary": "Relative precision planning is unavailable at zero or near-zero nominal mass. "
            "The absolute first-order uncertainty is still shown; use an absolute-error target.",
        }
    rm, rv = dm / mass, dv / volume
    relative_sd = (
        math.sqrt(rm * rm + rv * rv + (rm * rv) ** 2) if lognormal else math.hypot(rm, rv)
    )
    if lognormal:
        mass_term, volume_term = math.log1p(rm * rm), math.log1p(rv * rv)
        basis = "variance of log(concentration), not shares of raw concentration variance"
    else:
        mass_term, volume_term = rm * rm, rv * rv
        basis = "first-order concentration variance under independent input errors"
    total = mass_term + volume_term
    shares = {"mass": mass_term / total if total else 0.0,
              "volume": volume_term / total if total else 0.0}
    dominant = None if not total else ("balanced" if math.isclose(mass_term, volume_term, rel_tol=1e-9)
                                     else "mass" if mass_term > volume_term else "volume")
    met = relative_sd <= target or math.isclose(relative_sd, target, rel_tol=1e-12)
    summary = (
        f"The modeled relative standard deviation is {relative_sd:.3%}; "
        f"your design target is {target:.3%}. "
        + ("This meets the numerical target, not a safety or clinical acceptance criterion. " if met
           else "The current measurements do not meet that numerical target. ")
    )
    if dominant in ("mass", "volume"):
        summary += f"{dominant.capitalize()} is the larger uncertainty contributor on the stated variance basis."
    elif dominant == "balanced":
        summary += "Mass and volume contribute equally on the stated variance basis."
    else:
        summary += "No measurement uncertainty was supplied; this does not establish perfect accuracy."

    requirements = []
    for name, mean, sd, other in [("mass", mass, dm, rv), ("volume", volume, dv, rm)]:
        # For lognormal ratios, CV² = (1 + CV_mass²)(1 + CV_volume²) - 1.
        remaining = target * target - other * other
        max_sd = None if remaining < 0 else mean * math.sqrt(
            remaining / (1 + other * other) if lognormal else remaining
        )
        requirements.append({
            "input": name, "unit": "mg" if name == "mass" else "mL",
            "current_sd": sd, "max_sd": max_sd,
            "status": "unreachable_alone" if max_sd is None else
                      "already_sufficient" if sd <= max_sd or math.isclose(sd, max_sd, rel_tol=1e-12)
                      else "reduce_uncertainty",
            "first_order_guard_max_sd": 0.1 * volume if not lognormal and name == "volume" else None,
        })

    scenarios = []
    scenario_specs = [
        ("Current measurements", 1, 1), ("Half the mass SD", 0.5, 1),
        ("Half the volume SD", 1, 0.5), ("One tenth the volume SD", 1, 0.1),
    ]
    for requirement in requirements:
        if requirement["status"] == "reduce_uncertainty" and requirement["input"] == dominant:
            factor = requirement["max_sd"] / requirement["current_sd"]
            scenario_specs.append((f"{dominant.capitalize()} SD at target",
                                   factor if dominant == "mass" else 1,
                                   factor if dominant == "volume" else 1))
    for name, mass_factor, volume_factor in scenario_specs:
        changed = {**values, "mass_uncertainty": dm * mass_factor,
                   "volume_uncertainty": dv * volume_factor}
        cm, cv = rm * mass_factor, rv * volume_factor
        scenario_cv = math.sqrt(cm * cm + cv * cv + (cm * cv) ** 2) if lognormal else math.hypot(cm, cv)
        result = _lognormal_ratio(changed) if lognormal else {
            "mean": output["nominal"],
            "standard_deviation": math.hypot(changed["mass_uncertainty"] / volume,
                                              mass / volume * (changed["volume_uncertainty"] / volume)),
        }
        scenarios.append({
            "label": name, "mass_sd": changed["mass_uncertainty"],
            "volume_sd": changed["volume_uncertainty"], "relative_sd": scenario_cv,
            "meets_target": scenario_cv <= target or math.isclose(scenario_cv, target, rel_tol=1e-12),
            "result": result,
        })
    return {
        "available": True, "summary": summary, "relative_sd": relative_sd,
        "target_relative_sd": target, "meets_target": met,
        "contributions": {"basis": basis, "shares": shares, "dominant": dominant},
        "requirements": requirements, "scenarios": scenarios,
        "planning_note": "Hypothetical measurement improvements, not corrected observations. "
        "Input means, independence, and the selected model stay fixed. "
        "A lower SD must be justified by measurement evidence; repeating measurements does not "
        "automatically remove calibration bias or other shared errors. "
        "The chosen precision target is not an accuracy, safety, or clinical threshold.",
        "target_equation": "CV_out² = (1 + CV_mass²)(1 + CV_volume²) - 1" if lognormal
                           else "CV_out² = CV_mass² + CV_volume² (first-order)",
    }
