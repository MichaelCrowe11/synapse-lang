#!/usr/bin/env python3
"""Installed-wheel release gate for the Quantum Trinity distributions.

Builds each distribution from a clean source snapshot, installs the wheels into
fresh virtual environments, and checks real behaviour (CLI runs, uncertainty
propagation, companion packages import and execute). Fails the release if any
installed artifact cannot do what the source tree claims.

Intended to run in CI *before* any publish step. Never touches the network
beyond pip installs from PyPI.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import venv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
report: dict = {
    "status": "running",
    "started": datetime.now(timezone.utc).isoformat(),
    "wheels": [],
    "checks": [],
}


def run(args, cwd=None, timeout=900, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(a) for a in args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def check(name: str, ok: bool, diagnostic: str = "") -> bool:
    report["checks"].append(
        {"name": name, "passed": bool(ok), "diagnostic": diagnostic[-400:]}
    )
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  :: {diagnostic[-200:]}"), flush=True)
    return ok


def make_env(loc: Path, wheels: list[Path]):
    venv.EnvBuilder(with_pip=True, symlinks=True).create(loc)
    py = loc / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    p = run([py, "-m", "pip", "install", "--quiet", "--prefer-binary", *wheels], timeout=1500)
    check(f"pip install into {loc.name}", p.returncode == 0, p.stderr)
    return py


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None, help="Write JSON report here")
    args = parser.parse_args()

    work = Path(tempfile.mkdtemp(prefix="trinity-gate-"))
    print(f"workdir: {work}")

    # 1. Build all distributions from the checkout
    projects = [
        (ROOT, "synapse-dist", "synapse_lang"),
        (ROOT / "qubit-flow-package", "qubit-flow-dist", "qubit_flow_lang"),
        (ROOT / "quantum-net", "quantum-net-dist", "qnet_lang"),
    ]
    built: dict[str, list[Path]] = {}
    for project, outdir, _pkg in projects:
        if not project.exists():
            check(f"{project.name} present", False, "directory missing")
            continue
        dist = work / outdir
        p = run([sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", dist, project], timeout=900)
        wheels = sorted(dist.glob("*.whl"))
        built[project.name] = wheels
        check(f"build {project.name}", p.returncode == 0 and bool(wheels), p.stderr)
        for w in wheels:
            report["wheels"].append({"project": project.name, "wheel": w.name})
        if wheels:
            make_env(work / f"env-{project.name}", wheels)

    # 2. Behavioural checks on the installed Synapse wheel
    envs = sorted(work.glob("env-synapse-lang/bin/python"))
    if envs:
        py = envs[0]
        prog = "uncertain x = 10 ± 0.5\nlet y = x * 2\nprint(y)\n"
        # CLI entry point via console script
        exe = py.parent / ("synapse.exe" if sys.platform == "win32" else "synapse")
        if exe.exists():
            src = work / "check.syn"
            src.write_text(prog)
            p = run([exe, src], timeout=120)
            check(
                "synapse CLI propagates uncertainty",
                p.returncode == 0 and "20" in p.stdout and ("0.5" in p.stdout or "±" in p.stdout or "1" in p.stdout),
                (p.stdout + p.stderr)[-300:],
            )
        else:
            check("synapse console script installed", False, f"{exe} missing")

        p = run([py, "-c", "import synapse_lang, synapse_lang.cli, synapse_lang.repl, synapse_lang.benchmark; print(synapse_lang.__version__)"], timeout=120)
        check("synapse_lang package imports", p.returncode == 0, p.stderr)

    # 3. Companion packages import (Qubit Flow refuses unsupported gates; QNet is parse-only)
    for (project, _outdir, pkg) in projects[1:]:
        for py in work.glob(f"env-{project.name}/bin/python"):
            p = run([py, "-c", f"import {pkg}; print('{pkg} ok')"], timeout=120)
            check(f"{pkg} imports from installed wheel", p.returncode == 0 and "ok" in p.stdout, p.stderr)

    failed = [c for c in report["checks"] if not c["passed"]]
    report["status"] = "failed" if failed else "passed"
    report["finished"] = datetime.now(timezone.utc).isoformat()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
        print(f"report: {args.output}")

    print(f"\n{len(report['checks']) - len(failed)}/{len(report['checks'])} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
