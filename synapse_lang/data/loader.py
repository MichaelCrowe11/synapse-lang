"""Data loading and normalization for quantum ML algorithms."""
from __future__ import annotations

import numpy as np

DATA_KEYS = frozenset({
    "train_data", "train_labels", "test_data",
    "data", "matrix", "labels",
})


def resolve_data(params: dict) -> dict:
    """Resolve data parameters to numpy arrays."""
    resolved = dict(params)
    for key in DATA_KEYS:
        if key not in resolved:
            continue
        value = resolved[key]
        if isinstance(value, np.ndarray):
            continue
        elif isinstance(value, list):
            resolved[key] = np.array(value)
        elif isinstance(value, str) and value.endswith(".csv"):
            resolved[key] = _load_csv(value)
        elif isinstance(value, str) and value.endswith(".npy"):
            resolved[key] = np.load(value)
    return resolved


def _load_csv(path: str) -> np.ndarray:
    import pandas as pd
    return pd.read_csv(path).values
