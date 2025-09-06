from dataclasses import dataclass
@dataclass
class EPR:
    a: str; b: str; fidelity: float
class Entangler:
    def __init__(self, sim, fiber): self.sim=sim; self.fiber=fiber
    def attempt(self, A, B, cb):
        p = self.fiber.success_prob()
        if self.sim.rng.random() < p:
            # naive fidelity as function of loss
            f = 0.9 * p + 0.1
            cb(EPR(A,B,f))
