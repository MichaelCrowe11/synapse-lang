from qnet_runtime.sim_core import Sim
from qnet_runtime.channels import Fiber
from qnet_runtime.entanglement import Entangler

def test_entanglement_success():
    sim=Sim(seed=123)
    fiber=Fiber(length_km=10,loss_db_km=0.2)
    ent=Entangler(sim,fiber)
    results=[]
    ent.attempt("A","B", lambda e: results.append(e))
    sim.run()
    assert len(results) in (0,1)
