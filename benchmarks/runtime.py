"""Run with the project interpreter: python benchmarks/runtime.py.

Gate and execute timings use the same loops as baseline.json. Cold import and
CLI timings additionally include separate fresh interpreter processes.
"""
import json
import platform
import statistics
import subprocess
import sys
from timeit import repeat

import numpy as np

import synapse_lang as synapse
from synapse_lang.quantum.core import SimulatorBackend

code = "x = 5\ny = x * 2\nz = y + x"
program = synapse.parse(code)
backend = SimulatorBackend()
state = np.ones(2**14, dtype=complex) / 128
assert synapse.execute_program(program) == synapse.execute(code) == 15


def cold(snippet):
    return statistics.median(float(subprocess.check_output(
        [sys.executable, "-c", "import time; t=time.perf_counter(); " + snippet + "; print(time.perf_counter()-t)"],
        text=True,
    )) for _ in range(5))


result = {
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "numpy": np.__version__,
    "import_seconds": cold("import synapse_lang"),
    "cli_startup_seconds": cold("import synapse_lang.cli"),
    "execute_us": min(repeat(lambda: synapse.execute(code), number=1000, repeat=5)) * 1000,
    "reused_program_us": min(repeat(lambda: synapse.execute_program(program), number=1000, repeat=5)) * 1000,
    "x_14qubits_us": min(repeat(lambda: backend._x(state, 7, 14), number=10, repeat=5)) * 100000,
    "h_14qubits_us": min(repeat(lambda: backend._h(state, 7, 14), number=10, repeat=5)) * 100000,
}
print(json.dumps(result, indent=2))
