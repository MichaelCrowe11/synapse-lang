"""Seeded event scheduler with stable ordering and resumable time horizons."""
import heapq
import math
from itertools import count

import numpy as np


class Sim:
    def __init__(self, seed=0):
        self.t = 0.0
        self.q = []
        self.rng = np.random.default_rng(seed)
        self.trace = []
        self._sequence = count()

    def schedule(self, dt, fn, *args):
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("Event delay must be finite and nonnegative")
        heapq.heappush(self.q, (self.t + dt, next(self._sequence), fn, args))

    def run(self, until=None):
        if until is not None and (not math.isfinite(until) or until < self.t):
            raise ValueError("Time horizon must be finite and not precede simulation time")
        while self.q:
            if until is not None and self.q[0][0] > until:
                break
            t, _, fn, args = heapq.heappop(self.q)
            self.t = t
            fn(*args)
            self.trace.append((t, fn.__name__))
        if until is not None:
            self.t = until
