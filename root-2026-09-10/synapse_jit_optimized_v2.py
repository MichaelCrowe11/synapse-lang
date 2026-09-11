"""
Synapse Language - Optimized JIT Compiler Helpers
Applies Numba JIT where available with graceful fallback.
"""
from __future__ import annotations

try:
    from numba import njit, prange, vectorize
    _have_numba = True
except Exception:
    _have_numba = False


def maybe_njit(signature=None, **kwargs):
    """Decorator: njit if available, else identity."""
    if not _have_numba:
        def identity(fn):
            return fn
        return identity
    return njit(signature, **kwargs)


def maybe_parallel_range():
    """Return prange if available, else range."""
    return prange if _have_numba else range


def maybe_vectorize(*args, **kwargs):
    if not _have_numba:
        def deco(fn):
            return fn
        return deco
    return vectorize(*args, **kwargs)
