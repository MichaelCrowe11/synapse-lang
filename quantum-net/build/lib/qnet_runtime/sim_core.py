import heapq, math, numpy as np
class Sim:
    def __init__(self, seed=0):
        self.t=0.0; self.q=[]; self.rng=np.random.default_rng(seed); self.trace=[]
    def schedule(self, dt, fn, *args):
        heapq.heappush(self.q, (self.t+dt, fn, args))
    def run(self, until=None):
        while self.q:
            t, fn, args = heapq.heappop(self.q)
            if until and t>until: break
            self.t=t; fn(*args); self.trace.append((t, fn.__name__))
