"""Micro-benchmark for the Synapse interpreter (the ``synapse-bench`` command).

Declared as ``synapse-bench = synapse_lang.benchmark:main`` in
``[project.scripts]`` but never shipped. Runs a handful of representative
programs through ``execute`` and reports per-program timing, so users can sanity
check interpreter performance on their machine.
"""
from __future__ import annotations

import argparse
import time

from synapse_lang import execute

_PROGRAMS = [
    ("arithmetic", "1 + 2 * 3 - 4 / 2"),
    ("assignment", "x = 5\ny = x * 2\nz = y + x"),
    ("uncertain", "uncertain a = 10 +/- 0.5\nb = a * 2"),
]


def _time_once(code: str) -> tuple[object, float]:
    start = time.perf_counter()
    result = execute(code, sandbox=False)
    return result, (time.perf_counter() - start) * 1000.0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="synapse-bench", description="Benchmark the Synapse interpreter")
    parser.add_argument("-n", "--iterations", type=int, default=50, help="iterations per program (default 50)")
    args = parser.parse_args(argv)

    print(f"Synapse interpreter benchmark ({args.iterations} iterations/program)")
    print(f"{'program':<14}{'mean ms':>10}{'min ms':>10}")
    for name, code in _PROGRAMS:
        times = []
        result = None
        for _ in range(max(1, args.iterations)):
            result, ms = _time_once(code)
            times.append(ms)
        mean = sum(times) / len(times)
        print(f"{name:<14}{mean:>10.3f}{min(times):>10.3f}   -> {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
