"""Builtin functions and constants available to every Synapse program.

These are registered into the interpreter's variable scope at startup, so
``print``, the math functions, and the basic statistics helpers resolve as
ordinary function calls. Uncertain values render through their own ``__str__``,
so ``print`` shows ``value ± uncertainty`` without special handling here.
"""
from __future__ import annotations

import math
import statistics
from typing import Any


def _to_float(x: Any) -> float:
    """Coerce a value (including an UncertainValue) to its nominal float."""
    value = getattr(x, "value", x)
    return float(value)


def _synapse_print(*args: Any) -> None:
    print(" ".join(str(a) for a in args))


def _mean(values: Any) -> float:
    return statistics.fmean(_to_float(v) for v in values)


def _std(values: Any) -> float:
    nums = [_to_float(v) for v in values]
    return statistics.pstdev(nums) if len(nums) > 1 else 0.0


def default_builtins() -> dict[str, Any]:
    """Return a fresh mapping of builtin names to callables/constants."""
    return {
        # I/O and conversion
        "print": _synapse_print,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        # sequences
        "len": len,
        "range": lambda *a: list(range(*a)),
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sum": sum,
        # math (operate on the nominal value)
        "sqrt": lambda x: math.sqrt(_to_float(x)),
        "exp": lambda x: math.exp(_to_float(x)),
        "log": lambda x, base=math.e: math.log(_to_float(x), base),
        "log10": lambda x: math.log10(_to_float(x)),
        "sin": lambda x: math.sin(_to_float(x)),
        "cos": lambda x: math.cos(_to_float(x)),
        "tan": lambda x: math.tan(_to_float(x)),
        "floor": lambda x: math.floor(_to_float(x)),
        "ceil": lambda x: math.ceil(_to_float(x)),
        # statistics
        "mean": _mean,
        "std": _std,
        # constants
        "pi": math.pi,
        "e": math.e,
    }
