#!/usr/bin/env python3
"""
Synapse Language - Performance Benchmarking Suite
Run micro (numeric kernels) and macro (program files) benchmarks.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict

import numpy as np

from synapse_interpreter_optimized_v2 import OptimizedInterpreter


def timer(fn, *args, repeats: int = 5, **kwargs):
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append(time.perf_counter() - t0)
    arr = np.array(times)
    return {
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "max": float(arr.max()),
        "n": repeats,
    }


def bench_micro() -> Dict:
    import math

    def kernel(n=2_000_00):  # 200k
        s = 0.0
        for i in range(n):
            s += math.sin(i * 0.001) * math.cos(i * 0.002)
        return s

    return {"numeric_trig_loop": timer(kernel)}


def bench_macro(program: Path) -> Dict:
    code = program.read_text(encoding="utf8")
    interp = OptimizedInterpreter()
    return {"interpret_program": timer(interp.run, code)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--program", type=str, help="Path to .syn program for macro bench", default="")
    ap.add_argument("--repeats", type=int, default=5)
    args = ap.parse_args()

    results = {"micro": bench_micro()}
    if args.program:
        results["macro"] = bench_macro(Path(args.program))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()