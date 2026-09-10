"""Offline use-case experiments with analytical references, not hardware validation."""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "quantum-net"))

from qnet_runtime.channels import Fiber  # noqa: E402
from qnet_runtime.entanglement import Entangler  # noqa: E402
from qnet_runtime.sim_core import Sim  # noqa: E402

from qubit_flow_interpreter import QuantumGates  # noqa: E402
from synapse_lang.uncertainty import UncertainValue  # noqa: E402


def main():
    rng = np.random.default_rng(2026)
    calibration = []
    for theta in (0.2, 0.8, 1.5, 2.6):
        sigma = 0.002
        angle = UncertainValue(theta, sigma)
        propagated = (1 - angle.cos()) / 2
        gate = QuantumGates.rotation_y(theta)
        reference = expm(-0.5j * theta * np.array([[0, -1j], [1j, 0]]))
        samples = np.sin(rng.normal(theta, sigma, 100000) / 2) ** 2
        observed_sd = float(samples.std(ddof=1))
        assert np.allclose(gate, reference, atol=1e-13)
        assert abs(propagated.nominal - abs((gate @ np.array([1, 0]))[1]) ** 2) < 1e-13
        assert abs(observed_sd / propagated.uncertainty - 1) < 0.03
        calibration.append({
            "rotation_radians": theta, "angle_uncertainty": sigma,
            "probability": propagated.nominal,
            "first_order_probability_uncertainty": propagated.uncertainty,
            "synthetic_monte_carlo_sd": observed_sd,
        })
    links = []
    for distance in (0, 10, 50, 100):
        sim = Sim(seed=2026)
        channel = Fiber(distance, 0.2)
        entangler = Entangler(sim, channel)
        successes = []
        trials = 12000
        for _ in range(trials):
            entangler.attempt("alice", "bob", successes.append)
        reference = math.exp(-math.log(10) * distance * 0.2 / 10)
        frequency = len(successes) / trials
        assert abs(frequency - reference) <= 6 * math.sqrt(reference * (1 - reference) / trials) + 1 / trials
        links.append({"distance_km": distance, "trials": trials,
                      "observed_success_fraction": frequency, "attenuation_reference": reference})
    report = {
        "evidence_level": "seeded software simulation plus independent analytical and SciPy references",
        "hardware_validated": False, "real_dataset_validated": False,
        "quantum_advantage_demonstrated": False,
        "rotation_sensitivity": calibration, "fiber_transmission": links,
        "limits": [
            "Small-angle uncertainty uses first-order propagation, not arbitrary correlated inference",
            "Fiber checks cover attenuation only, not the heuristic entanglement fidelity",
            "No claim of hardware entanglement, secure QKD, or working network teleportation",
        ],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
