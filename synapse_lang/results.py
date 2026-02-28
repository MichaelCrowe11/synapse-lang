"""Unified result type for all quantum algorithm executions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class SynapseQuantumResult:
    """Result container returned by all quantum algorithm executions.

    Different algorithms populate different fields:
    - Search/optimization: counts, probabilities, value
    - ML classification: classification
    - Linear algebra: data (matrices)
    - All algorithms: metadata (algorithm-specific extras)
    """

    counts: dict[str, int] | None = None
    probabilities: dict[str, float] | None = None
    value: float | None = None
    classification: list | None = None
    data: np.ndarray | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
