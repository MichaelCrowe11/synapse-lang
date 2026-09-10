"""Stage the current candidate in a fresh directory, without deleting prior evidence."""
import shutil
import tempfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    wheels = sorted((root / "release-dist").glob("synapse_lang-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Expected exactly one candidate wheel in release-dist; review its contents")
    parent = root / "benchmarks" / "matrix-context"
    parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    for directory in ["synapse_lang", "tests", "examples", "qubit_flow_lang", "quantum_net_lang", "scripts", ".github", "docs", "isolation", "quantum-net", "qubit-flow-package"]:
        shutil.copytree(
            root / directory, stage / directory,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".env*", "build", "dist", "*.egg-info", ".venv"),
        )
    for source in root.glob("*.py"):
        shutil.copy2(source, stage / source.name)
    for name in ["pyproject.toml", "README.md"]:
        shutil.copy2(root / name, stage / name)
    shutil.copy2(wheels[0], stage / wheels[0].name)
    print(stage)


if __name__ == "__main__":
    main()
