import re
from synapse_lang.synapse_interpreter import SynapseInterpreter

BELL_SRC = """
quantum circuit bell(2) {
    h(0)
    cnot(0,1)
}
run bell { shots: 256 }
"""

ROT_SRC = """
quantum circuit rot(1) {
    h(0)
    rx(0, 1.57079632679)
    ry(0, 1.57079632679)
    rz(0, 1.57079632679)
}
run rot { shots: 128 }
"""

def _find_counts(result_list):
    for item in result_list:
        if isinstance(item, dict) and 'counts' in item:
            return item['counts']
    return None

def test_bell_circuit_counts():
    intr = SynapseInterpreter()
    out = intr.execute(BELL_SRC)
    counts = _find_counts(out)
    assert counts is not None, f"No counts in output: {out}"
    # Expect only 00 / 11 ideally
    keys = set(counts.keys())
    assert keys.issubset({"00", "11"}), keys
    total = sum(counts.values())
    assert abs(total - 256) < 5  # allow minor deviation


def test_rotation_circuit_runs():
    intr = SynapseInterpreter()
    out = intr.execute(ROT_SRC)
    counts = _find_counts(out)
    assert counts is not None
    total = sum(counts.values())
    assert total == 128
