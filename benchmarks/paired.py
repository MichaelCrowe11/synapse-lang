"""Alternating baseline/candidate trials using the same interpreter and dependencies.

Run: .venv/bin/python benchmarks/paired.py > benchmarks/paired-results.json
The baseline export is retained inside benchmarks/ for inspection.
"""
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "benchmarks" / "baseline-source"
REVISION = "c41c9f6242"
ENV = {**os.environ, "OPENBLAS_NUM_THREADS":"1", "OMP_NUM_THREADS":"1", "MKL_NUM_THREADS":"1"}


def export_baseline():
    files = subprocess.check_output(["git","ls-tree","-r","--name-only",REVISION,"synapse_lang"],cwd=ROOT,text=True).splitlines()
    for name in files:
        path = BASE / name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(subprocess.check_output(["git","show",f"{REVISION}:{name}"],cwd=ROOT))


WORKER = r"""
import json,time,tracemalloc
from timeit import repeat
start=time.perf_counter()
import synapse_lang as s
cold=time.perf_counter()-start
import numpy as np
from synapse_lang.synapse_interpreter import SynapseInterpreter
from synapse_lang.quantum.core import SimulatorBackend,QuantumCircuitBuilder
from synapse_lang.parallel import ParameterSweep
from synapse_lang.uncertainty import UncertainValue,monte_carlo
code='x = 5\ny = x * 2\nz = y + x'
code=code.replace('\\n','\n')
i=SynapseInterpreter(); program=s.parse(code)
assert i.execute(code)==15
b=SimulatorBackend()
out={'import_seconds':cold}
def timing(f,n=100):
    f()
    return min(repeat(f,number=n,repeat=3))/n
out['execute_seconds']=timing(lambda:s.execute(code,sandbox=False),500)
out['reuse_seconds']=timing(lambda:SynapseInterpreter().interpret(program),500)
for n in [8,12,16]:
    rng=np.random.default_rng(72)
    state=rng.normal(size=2**n)+1j*rng.normal(size=2**n)
    state/=np.linalg.norm(state)
    for q in [0,n//2,n-1]:
        for gate in ['_x','_h']:
            out[f'{gate}_{n}_{q}_seconds']=timing(lambda:getattr(b,gate)(state,q,n),3)
for n in [4,8]:
    c=QuantumCircuitBuilder(n)
    for q in range(n): c.h(q)
    for q in range(n-1): c.cnot(q,q+1)
    out[f'circuit_{n}_seconds']=timing(lambda:b.execute(c,shots=128),3)
def sweep():
    result=ParameterSweep(lambda x:x*x).sweep(x=range(5000))
    assert result[(4999,)]==4999**2
tracemalloc.start(); sweep(); out['sweep_peak_bytes']=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
for parallel in [False,True]:
    def mc():
        return monte_carlo(lambda x:x*x,{'x':UncertainValue(2,.1)},samples=1000,seed=42,parallel=parallel,n_cores=2)
    result=mc(); assert abs(result.nominal-4)<.1
    out[f'monte_carlo_{parallel}_seconds']=timing(mc,3)
print(json.dumps(out))
"""


def main():
    export_baseline()
    trials={"baseline":[],"candidate":[]}
    for trial in range(5):
        order=("baseline","candidate") if trial%2==0 else ("candidate","baseline")
        for version in order:
            working=BASE if version=="baseline" else ROOT
            result=subprocess.run([sys.executable,"-c",WORKER],cwd=working,env=ENV,text=True,capture_output=True,check=True)
            trials[version].append(json.loads(result.stdout))
    comparisons={}
    for key in trials["baseline"][0]:
        before=[r[key] for r in trials["baseline"]]
        after=[r[key] for r in trials["candidate"]]
        comparisons[key]={"baseline_median":statistics.median(before),"candidate_median":statistics.median(after),
                          "paired_ratios":[b/a for b,a in zip(before,after,strict=True)],
                          "median_ratio":statistics.median(b/a for b,a in zip(before,after,strict=True))}
    print(json.dumps({"base_commit":REVISION,"python":sys.version,"trials":trials,"comparisons":comparisons,
                      "notes":["Fresh processes; alternating order; numerical library threads fixed at one",
                               "Baseline Monte Carlo ignores parallel=True; not an equivalent parallel implementation",
                               "Ratios above one favor candidate; memory uses Python tracemalloc, not total RSS"]},indent=2))


if __name__=="__main__":
    main()
