"""Deterministic fault campaign; rates describe this injected set, not field reliability."""
import json
import math
from unittest.mock import patch

import numpy as np
from qubit_flow_lang.qubit_flow_interpreter import QuantumGates, QubitFlowInterpreter

from synapse_lang.quantum.core import QuantumCircuitBuilder, SimulatorBackend
from synapse_lang.uncertainty import UncertainValue


def campaign():
    records = []
    for category in ("gate", "indexing", "noise", "uncertainty"):
        for defective in (False, True):
            for seed in range(10):
                theta = 0.2 + seed * 0.17
                if category == "gate":
                    gate = QuantumGates.rotation_y(theta * (2 if defective else 1))
                    observed = abs((gate @ np.array([1, 0]))[1]) ** 2
                    expected = math.sin(theta / 2) ** 2
                    detected = abs(observed - expected) > 1e-12
                    ordinary_pass = np.allclose(gate.conj().T @ gate, np.eye(2))
                elif category == "indexing":
                    q = QubitFlowInterpreter()
                    q.execute("qubit a\nqubit b\nX[b]")
                    q.execute("CNOT[a,b]" if defective else "CNOT[b,a]")
                    expected = np.array([0, 0, 0, 1])
                    detected = not np.allclose(q.state.amplitudes, expected)
                    ordinary_pass = np.isclose(np.linalg.norm(q.state.amplitudes), 1)
                elif category == "noise":
                    # Tests the legacy one-random-readout-bit-flip contract, not physical depolarization.
                    np.random.seed(600 + seed)
                    p, shots = 0.2, 4000
                    counts = SimulatorBackend().execute(QuantumCircuitBuilder(1), shots,
                                                       {"model": "depolarizing", "p": 0 if defective else p})
                    observed = counts.get("1", 0) / shots
                    detected = abs(observed - p) > 6 * math.sqrt(p * (1-p) / shots)
                    ordinary_pass = sum(counts.values()) == shots
                else:
                    value = UncertainValue(theta, 0.002)
                    original = UncertainValue.cos
                    def wrong_cos(self, original=original):
                        result = original(self)
                        result.uncertainty *= 2
                        return result
                    with patch.object(UncertainValue, "cos", wrong_cos if defective else original):
                        probability = (1 - value.cos()) / 2
                    expected = abs(math.sin(theta)) * 0.002 / 2
                    detected = abs(probability.uncertainty - expected) > 1e-12
                    ordinary_pass = np.isclose(probability.nominal, math.sin(theta / 2) ** 2)
                records.append({"category": category, "seed": seed, "defect_injected": defective,
                                "detected": bool(detected), "baseline_smoke_pass": bool(ordinary_pass)})
    faults = [r for r in records if r["defect_injected"]]
    controls = [r for r in records if not r["defect_injected"]]
    return {"cases": records, "faults": len(faults), "controls": len(controls),
            "detection_rate": sum(r["detected"] for r in faults) / len(faults),
            "false_alarm_rate": sum(r["detected"] for r in controls) / len(controls),
            "baseline": "Deliberately weak norm/unitarity, count-total and nominal-value smoke checks",
            "limits": "Ten fixed cases per category; not a comparison against all existing unit tests or unseen defects"}


if __name__ == "__main__":
    result = campaign()
    print(json.dumps(result, indent=2))
    if result["detection_rate"] != 1 or result["false_alarm_rate"] != 0:
        raise SystemExit(1)
