"""Install exactly one candidate wheel into a fresh, retained base-only environment."""
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    wheels = sorted((root / "release-dist").glob("synapse_lang-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Expected exactly one candidate wheel in release-dist; review its contents")
    working = root / "benchmarks" / "wheel-smoke"
    working.mkdir(parents=True, exist_ok=True)
    environment = Path(tempfile.mkdtemp(prefix="base-", dir=working))
    venv.EnvBuilder(with_pip=True, symlinks=sys.platform != "win32").create(environment)
    python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.run([str(python), "-m", "pip", "install", str(wheels[0])], check=True)
    subprocess.run(
        [str(python), "-I", str(root / "scripts" / "wheel_smoke.py"), "--without-jit"],
        cwd=working, check=True,
    )
    print(f"Fresh wheel environment retained at {environment}")


if __name__ == "__main__":
    main()
