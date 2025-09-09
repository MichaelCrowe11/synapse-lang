from dataclasses import dataclass
@dataclass
class Fiber:
    length_km: float; loss_db_km: float; dark_hz: float=0.0; latency_ms: float=0.5
    def success_prob(self):
        return 10 ** (-(self.length_km*self.loss_db_km)/10)
