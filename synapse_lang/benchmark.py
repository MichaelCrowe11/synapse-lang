"""Measured parse, end-to-end, and reusable-program execution benchmarks."""
from __future__ import annotations

import argparse
import json
import statistics
import time

from synapse_lang import execute, execute_program, parse

_PROGRAMS = [
    ("arithmetic", "1 + 2 * 3 - 4 / 2", 5.0),
    ("assignment", "x = 5\ny = x * 2\nz = y + x", 15.0),
    ("uncertain", "uncertain a = 10 +/- 0.5\nb = a * 2", (20.0, 1.0)),
]


def measure(function, iterations):
    function()  # Warm up imports and caches before timing execution.
    times = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        function()
        times.append((time.perf_counter_ns() - start) / 1000)
    return {"median_us": statistics.median(times), "min_us": min(times)}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="synapse-bench")
    parser.add_argument("-n", "--iterations", type=int, default=100)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable measurements")
    args = parser.parse_args(argv)
    if args.iterations < 1:
        parser.error("iterations must be positive")
    results = {}
    for name, code, expected in _PROGRAMS:
        program = parse(code)
        actual = execute_program(program)
        value = (actual.nominal, actual.uncertainty) if isinstance(expected, tuple) else actual
        if value != expected:
            raise AssertionError(f"{name} returned {value!r}, expected {expected!r}")
        results[name] = {
            "parse": measure(lambda code=code: parse(code), args.iterations),
            "end_to_end": measure(lambda code=code: execute(code), args.iterations),
            "reused_program": measure(lambda program=program: execute_program(program), args.iterations),
        }
    if args.json:
        print(json.dumps({"iterations": args.iterations, "programs": results}, indent=2))
    else:
        print("Microseconds per operation (warmed median; fresh execution state)")
        print(f"{'program':<14}{'parse':>12}{'end-to-end':>14}{'reuse AST':>12}")
        for name, phases in results.items():
            print(f"{name:<14}{phases['parse']['median_us']:>12.3f}"
                  f"{phases['end_to_end']['median_us']:>14.3f}"
                  f"{phases['reused_program']['median_us']:>12.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
