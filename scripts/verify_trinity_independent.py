#!/usr/bin/env python3
"""Independent installed-wheel verification of the Quantum Trinity companion milestone.

Runs from a COPY of the checkout (never writes into the agent's tree), builds the three
distributions, installs them into fresh virtual environments, and checks behaviour by
executing programs and comparing against dense-matrix references. Records pass/fail with
diagnostics. This is a second runtime checking the console agent's claims, not a rerun of
its own verifier.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, time, venv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("TRINITY_ROOT", Path(__file__).resolve().parents[1]))
EVID = Path(os.environ.get("TRINITY_EVIDENCE_DIR", Path(__file__).resolve().parents[1] / "benchmarks/trinity-implementation/independent"))
EVID.mkdir(parents=True, exist_ok=True)
WORK = Path(tempfile.mkdtemp(prefix="trinity-indep-", dir="/tmp"))
PY = sys.executable
report = {"status": "running", "started": datetime.now(timezone.utc).isoformat(), "work": str(WORK),
          "source_snapshot": None, "wheels": [], "checks": []}
LOG = WORK / "commands.log"

def log(text):
    with LOG.open("a") as f: f.write(text + "\n")

def run(args, cwd=None, data=None, timeout=900, env=None):
    t0 = time.time()
    p = subprocess.run([str(a) for a in args], cwd=cwd, input=data, capture_output=True, text=True, timeout=timeout, env=env)
    log(f"\n$ {' '.join(map(str, args))}  [rc={p.returncode} {time.time()-t0:.1f}s]\n{p.stdout}{p.stderr}")
    return p

def check(name, ok, diagnostic="", **extra):
    report["checks"].append({"name": name, "passed": bool(ok), "diagnostic": diagnostic[-400:], **extra})
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  :: {diagnostic[-160:]}"), flush=True)

def make_env(name, wheels, extras=()):
    loc = WORK / name
    venv.EnvBuilder(with_pip=True, symlinks=True).create(loc)
    py = loc / "bin/python"
    p = run([py, "-m", "pip", "install", "--quiet", "--prefer-binary", *wheels, *extras], timeout=1500)
    check(f"{name}: pip install", p.returncode == 0, p.stderr)
    return py

# 1. snapshot the source (excluding envs, caches, benchmarks, metadata that builds regenerate)
src = WORK / "src"
rs = run(["rsync", "-a", "--exclude", ".git", "--exclude", ".venv", "--exclude", "benchmarks", "--exclude", "node_modules",
          "--exclude", "__pycache__", "--exclude", "*.egg-info", "--exclude", ".pytest_cache", "--exclude", "*.pyc",
          "--exclude", "dist", "--exclude", "build", f"{ROOT}/", f"{src}/"])
check("source snapshot copied", rs.returncode == 0, rs.stderr)
report["source_snapshot"] = {"path": str(src), "git_head": run(["git", "-C", ROOT, "rev-parse", "--short", "HEAD"]).stdout.strip(),
                             "dirty_tracked": int(run(["git", "-C", ROOT, "diff", "--name-only"]).stdout.count("\n"))}

# 2. build the three distributions from the copy
wheels = {}
for name, sub in (("synapse", ""), ("qflow", "qubit-flow-package"), ("qnet", "quantum-net")):
    out = WORK / "dist" / name
    p = run([PY, "-m", "build", "--outdir", out, src / sub], timeout=900)
    whl = sorted(out.glob("*.whl"))
    check(f"build {name}", p.returncode == 0 and len(whl) == 1, p.stderr or p.stdout)
    if whl:
        wheels[name] = whl[0]
        report["wheels"].append({"name": name, "file": whl[0].name, "sha256": hashlib.sha256(whl[0].read_bytes()).hexdigest()})
        t = run([PY, "-m", "twine", "check", *sorted(out.iterdir())])
        check(f"twine check {name}", t.returncode == 0, t.stdout + t.stderr)

BELL = "qubit a\nqubit b\nH[a]\nCNOT[a,b]"
GHZ = "qubit a\nqubit b\nqubit c\nentangle(a,b,c) ghz"

# 3. Qubit Flow alone
if "qflow" in wheels:
    py = make_env("env-qflow", [wheels["qflow"]])
    p = run([py, "-I", "-c", "import importlib.util, qubit_flow_lang, qubit_flow_lang.qubit_flow_interpreter as i; "
             "assert importlib.util.find_spec('synapse_lang') is None; assert 'site-packages' in i.__file__; print(i.__file__)"])
    check("qflow: installed runtime import (no checkout, no synapse_lang)", p.returncode == 0, p.stderr, path=p.stdout.strip())
    p = run([py, "-I", "-m", "qubit_flow_lang.cli", "-"], data=BELL)
    try:
        probs = json.loads(p.stdout)["probabilities"]; ok = all(abs(a-b) < 1e-9 for a, b in zip(probs, [0.5, 0, 0, 0.5]))
    except Exception as e: probs, ok = str(e), False
    check("qflow: Bell state via CLI = [0.5,0,0,0.5]", p.returncode == 0 and ok, p.stderr, probabilities=probs)
    p = run([py, "-I", "-m", "qubit_flow_lang.cli", "-"], data=GHZ)
    try:
        probs = json.loads(p.stdout)["probabilities"]; ok = abs(probs[0]-0.5) < 1e-9 and abs(probs[7]-0.5) < 1e-9 and abs(sum(probs)-1) < 1e-9
    except Exception as e: probs, ok = str(e), False
    check("qflow: GHZ via CLI = 0.5|000> + 0.5|111>", p.returncode == 0 and ok, p.stderr)
    code = '''
import numpy as np
from qubit_flow_lang.qubit_flow_interpreter import QubitFlowInterpreter, QuantumGates
# reversed control: b=1, control b target a -> |11>
q = QubitFlowInterpreter(); q.execute("qubit a\\nqubit b\\nX[b]\\nCNOT[b,a]")
assert np.allclose(q.state.amplitudes, [0,0,0,1]), q.state.amplitudes
# forward control with a=0 leaves b alone
q = QubitFlowInterpreter(); q.execute("qubit a\\nqubit b\\nX[b]\\nCNOT[a,b]")
assert np.allclose(q.state.amplitudes, [0,1,0,0]), q.state.amplitudes
# CZ on |11> flips sign, dense reference
q = QubitFlowInterpreter(); q.execute("qubit a\\nqubit b\\nX[a]\\nX[b]\\nCZ[a,b]")
assert np.allclose(q.state.amplitudes, [0,0,0,-1]), q.state.amplitudes
# unitarity of every single-qubit rotation
for ax in ("x","y","z"):
    g = getattr(QuantumGates, f"rotation_{ax}")(0.37); assert np.allclose(g.conj().T @ g, np.eye(2))
# shared joint state after entangling
q = QubitFlowInterpreter(); q.execute("qubit a\\nqubit b\\nH[a]\\nCNOT[a,b]")
assert q.qubits["a"].state is q.qubits["b"].state
print("ok")'''
    p = run([py, "-I", "-c", code])
    check("qflow: reversed-control CNOT, CZ sign, rotation unitarity, shared joint state", p.returncode == 0 and p.stdout.strip() == "ok", p.stderr)
    p = run([py, "-I", "-m", "qubit_flow_lang.cli", "-"], data="qubit a\nCNOT[a,a]")
    check("qflow: invalid program exits 1", p.returncode == 1, p.stdout + p.stderr)
    for exe in ("synapse-qflow", "synapse-qubit-flow"):
        p = run([py.parent / exe, "--help"]); check(f"qflow: entry point {exe} --help", p.returncode == 0, p.stderr)
    p = run([py.parent / "synapse-qubit-flow"], data="qubit a\n:quit\n")
    check("qflow: REPL accepts a statement and :quit", p.returncode == 0 and '"probabilities"' in p.stdout, p.stdout + p.stderr)

# 4. Quantum Net alone
if "qnet" in wheels:
    py = make_env("env-qnet", [wheels["qnet"]])
    p = run([py, "-I", "-c", "import importlib.util, qnet_lang, qnet_lang.parser as m; assert importlib.util.find_spec('synapse_lang') is None; assert 'site-packages' in m.__file__; print(m.__file__)"])
    check("qnet: installed import (no checkout)", p.returncode == 0, p.stderr, path=p.stdout.strip())
    p = run([py, "-I", "-m", "qnet_lang.cli", "-"], data="network demo { node alice; node bob; fiber(length=10) alice bob; }")
    try: d = json.loads(p.stdout); ok = d.get("mode") == "parse-only" and d.get("statements", 0) >= 1
    except Exception as e: d, ok = str(e), False
    check("qnet: CLI parses a network and reports parse-only", p.returncode == 0 and ok, p.stderr, result=d)
    p = run([py, "-I", "-m", "qnet_lang.cli", "-"], data="network { broken")
    check("qnet: malformed input exits 1 (SyntaxError, not AttributeError)", p.returncode == 1 and "AttributeError" not in p.stdout + p.stderr, p.stdout + p.stderr)
    for exe in ("synapse-qnet", "synapse-quantum-net"):
        p = run([py.parent / exe, "--help"]); check(f"qnet: entry point {exe} --help", p.returncode == 0, p.stderr)
    p = run([py.parent / "synapse-quantum-net"], data=":quit\n"); check("qnet: REPL :quit exits 0", p.returncode == 0, p.stderr)

# 5. all three together: bridge + the agent's own test file against the INSTALLED modules
if len(wheels) == 3:
    py = make_env("env-all", list(wheels.values()), extras=["pytest", "scipy"])
    smoke = '''
import numpy as np, qubit_flow_lang, qnet_lang, synapse_lang
from qubit_flow_lang.bridge import SynapseQubitBridge
for m in (qubit_flow_lang, qnet_lang, synapse_lang): assert "site-packages" in m.__file__, m.__file__
b = SynapseQubitBridge()
r = b.execute_hybrid("uncertain theta = 0.8 ± 0.002", "qubit q\\nRY(theta)[q]")
v = r["shared_context"]["quantum_q"]; p = np.sin(0.4)**2
assert abs(v.nominal - p) < 1e-9, v.nominal
assert abs(v.uncertainty - np.sqrt(p*(1-p))) < 1e-9, v.uncertainty
print("ok")'''
    p = run([py, "-I", "-c", smoke]); check("all: Synapse+QubitFlow bridge from installed wheels (RY(0.8) -> p=sin^2(0.4))", p.returncode == 0 and p.stdout.strip() == "ok", p.stderr)
    tdir = WORK / "tests-installed"; tdir.mkdir()
    shutil.copy(ROOT / "tests/test_trinity_implementation.py", tdir / "test_trinity_implementation.py")
    p = run([py, "-I", "-m", "pytest", "-p", "no:cacheprovider", "-q", str(tdir)], cwd=tdir, timeout=900)
    tail = "\n".join(p.stdout.strip().splitlines()[-2:])
    check("all: agent's test_trinity_implementation.py passes against INSTALLED wheels", p.returncode == 0, p.stdout[-600:] + p.stderr[-300:], summary=tail)

# 6. legacy root suite collection (read-only look at the checkout)
p = run([ROOT / ".venv/bin/python", "-m", "pytest", "-p", "no:cacheprovider", "--collect-only", "-q", str(ROOT / "test_qubit_flow.py")], cwd=ROOT)
check("checkout: legacy test_qubit_flow.py collects (bridge import repaired)", p.returncode == 0, p.stdout[-400:] + p.stderr[-300:])

passed = sum(c["passed"] for c in report["checks"]); total = len(report["checks"])
report.update(status="passed" if passed == total else "failed", passed=passed, total=total,
              finished=datetime.now(timezone.utc).isoformat(), commands_log=str(LOG))
out = EVID / "independent-verification.json"; out.write_text(json.dumps(report, indent=2) + "\n")
shutil.copy(LOG, EVID / "independent-verification-commands.log")
print(f"\n{passed}/{total} checks passed -> {out}")
