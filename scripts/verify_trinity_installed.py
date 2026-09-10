"""Build all three distributions and verify them in fresh isolated environments."""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from datetime import datetime, timezone
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "benchmarks" / "trinity-implementation"
    output.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="installed-", dir=output))
    report_path = output / "installed.json"
    report = {"status": "running", "run": str(run), "published": False,
              "platform": platform.platform(), "python": platform.python_version(),
              "timestamp": datetime.now(timezone.utc).isoformat(), "wheels": [], "checks": []}
    report_path.write_text(json.dumps(report, indent=2) + "\n")

    def command(args, *, cwd=run, data=None, expected=0):
        result = subprocess.run([str(a) for a in args], cwd=cwd, input=data,
                                capture_output=True, text=True, timeout=240)
        with (run / "commands.log").open("a") as log:
            log.write("\n$ " + " ".join(map(str, args)) + "\n" + result.stdout + result.stderr)
        if result.returncode != expected:
            raise RuntimeError(f"Command failed ({result.returncode}): {args[0]}; see {run / 'commands.log'}")
        return result.stdout

    def environment(name, wheels):
        location = run / name
        venv.EnvBuilder(with_pip=True, symlinks=os.name != "nt").create(location)
        python = location / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        command([python, "-m", "pip", "install", *wheels])
        return python

    try:
        wheels = []
        for name, source in (("synapse", root), ("qflow", root / "qubit-flow-package"),
                             ("qnet", root / "quantum-net")):
            dist = run / name
            command([sys.executable, "-m", "build", "--outdir", dist, source])
            command([sys.executable, "-m", "twine", "check", *sorted(dist.iterdir())])
            wheel, = dist.glob("*.whl")
            wheels.append(wheel)
            report["wheels"].append({"path": str(wheel), "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest()})
        for index, module in ((1, "qubit_flow_lang"), (2, "qnet_lang")):
            python = environment(f"{module}-only", [wheels[index]])
            code = ("import importlib.util; import " + module + "; "
                    "assert importlib.util.find_spec('synapse_lang') is None; print(" + module + ".__file__)")
            command([python, "-I", "-c", code])
            if index == 1:
                command([python, "-I", "-m", module + ".cli", "-"], data="qubit a\nqubit b\nH[a]\nCNOT[a,b]")
            else:
                command([python, "-I", "-m", module + ".cli", "-"], data="network demo { node alice; node bob; fiber(length=10) alice bob; }")
            report["checks"].append(module + " standalone wheel")
        python = environment("combined", wheels)
        smoke = """import json, numpy as np
import qubit_flow_lang, qnet_lang, synapse_lang
from qubit_flow_lang.bridge import SynapseQubitBridge
from qubit_flow_lang.cli import evaluate
q = evaluate("qubit a\\nqubit b\\nH[a]\\nCNOT[a,b]")
assert np.allclose(q['probabilities'], [0.5,0,0,0.5])
b = SynapseQubitBridge()
r = b.execute_hybrid("uncertain theta = 0.8 ± 0.002", "qubit q\\nRY(theta)[q]")
assert np.isclose(r['shared_context']['quantum_q'].nominal, np.sin(0.4)**2)
for module in (qubit_flow_lang, qnet_lang, synapse_lang):
    assert 'site-packages' in module.__file__, module.__file__
print(json.dumps(q))
"""
        report["bell"] = json.loads(command([python, "-I", "-c", smoke]))
        for name in ("synapse-qflow", "synapse-qubit-flow", "synapse-qnet", "synapse-quantum-net"):
            executable = python.parent / (name + (".exe" if os.name == "nt" else ""))
            command([executable, "--help"])
        for module in ("qubit_flow_lang", "qnet_lang"):
            command([python, "-I", "-m", module + ".cli", "-"], data="invalid!", expected=1)
            command([python, "-I", "-m", module + ".repl"], data=("qubit a\nH[a]\n" if module == "qubit_flow_lang" else "network demo {}\n") + ":quit\n")
        report["checks"].extend(["combined wheel imports", "Bell probabilities", "supported bridge",
                                 "four console entry points", "both REPLs", "nonzero error exits"])
        entry_smoke = """import importlib.metadata as metadata
for name in ('synapse-lang', 'synapse-qubit-flow', 'synapse-quantum-net'):
    for entry in metadata.distribution(name).entry_points:
        if entry.group == 'console_scripts':
            assert 'placeholder' not in entry.value, entry
            assert callable(entry.load()), entry
print('All advertised console entry points resolve')
"""
        command([python, "-I", "-c", entry_smoke])
        report["checks"].append("all distribution console entry points resolve")
        command([python, "-m", "pip", "install", "pytest"])
        installed_tests = run / "tests-installed"
        installed_tests.mkdir()
        shutil.copyfile(root / "tests" / "test_trinity_implementation.py",
                        installed_tests / "test_trinity_implementation.py")
        test_output = command([python, "-I", "-m", "pytest", "-p", "no:cacheprovider", "-q",
                               "--junitxml=" + str(run / "installed-tests.xml"), str(installed_tests)])
        report["installed_regressions"] = test_output.strip().splitlines()[-1]
        report["checks"].append("state and bridge regressions against installed wheels")
        fault_output = command([python, "-I", root / "scripts" / "trinity_fault_injection.py"])
        report["fault_campaign"] = json.loads(fault_output)
        (output / "fault-injection.json").write_text(fault_output)
        report["status"] = "passed"
        report["combined_python"] = str(python)
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = str(exc)
        raise
    finally:
        report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("status", "run", "checks")}, indent=2))


if __name__ == "__main__":
    main()
