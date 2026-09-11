"""Builtin functions and constants available to every Synapse program.

These are registered into the interpreter's variable scope at startup, so
``print``, the math functions, and the basic statistics helpers resolve as
ordinary function calls. Uncertain values render through their own ``__str__``,
so ``print`` shows ``value ± uncertainty`` without special handling here. The math
builtins propagate uncertainty when handed an UncertainValue; ``nominal``, ``sigma``,
``covariance`` and ``correlation`` read the pieces back out.
"""
from __future__ import annotations

import math
import statistics
from typing import Any


def _to_float(x: Any) -> float:
    """Coerce a value (including an UncertainValue) to its nominal float."""
    value = getattr(x, "value", x)
    return float(value)


def _is_uncertain(x: Any) -> bool:
    from .uncertainty import UncertainValue

    return isinstance(x, UncertainValue)


def _propagating(name: str, plain):
    """A math builtin that keeps the uncertainty when given an UncertainValue."""

    def call(x: Any):
        if _is_uncertain(x):
            return getattr(x, name)()
        return plain(float(x))

    return call


def _log(x: Any, base: float = math.e):
    if _is_uncertain(x):
        result = x.log()
        return result if base == math.e else result / math.log(_to_float(base))
    return math.log(float(x), base)


def _sigma(x: Any) -> float:
    """Standard uncertainty of a value; 0 for a plain number."""
    return float(x.uncertainty) if _is_uncertain(x) else 0.0


def _covariance(a: Any, b: Any) -> float:
    from .uncertainty import covariance

    return covariance(a, b)


def _correlation(a: Any, b: Any) -> float:
    from .uncertainty import correlation

    return correlation(a, b)


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
        # math: an UncertainValue keeps its uncertainty through these
        "sqrt": _propagating("sqrt", math.sqrt),
        "exp": _propagating("exp", math.exp),
        "log": _log,
        "log10": _propagating("log10", math.log10),
        "sin": _propagating("sin", math.sin),
        "cos": _propagating("cos", math.cos),
        "tan": _propagating("tan", math.tan),
        "floor": lambda x: math.floor(_to_float(x)),
        "ceil": lambda x: math.ceil(_to_float(x)),
        # uncertainty: read a value apart, or ask how two results move together
        "nominal": _to_float,
        "sigma": _sigma,
        "covariance": _covariance,
        "correlation": _correlation,
        # statistics
        "mean": _mean,
        "std": _std,
        # constants
        "pi": math.pi,
        "e": math.e,
    }
