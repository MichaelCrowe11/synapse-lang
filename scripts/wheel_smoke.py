"""Validate the installed distribution without importing the source checkout."""
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from importlib.metadata import version
from importlib.util import find_spec
from pathlib import Path

import synapse_lang as synapse

root = Path(__file__).resolve().parents[1]
assert Path(synapse.__file__).resolve() != root / "synapse_lang" / "__init__.py"
assert version("synapse_lang") == synapse.__version__
if "--without-jit" in sys.argv:
    assert find_spec("numba") is None
    assert not synapse.JIT_AVAILABLE
    try:
        synapse.compile("1+2")
    except ImportError:
        pass
    else:
        raise AssertionError("Compilation silently accepted missing optional JIT")
assert synapse.execute("1+2") == 3
program = synapse.parse("x*2")
assert synapse.execute_program(program, context={"x": 5}) == 10
assert synapse.execute_program(program, context={"x": 9}) == 18
uncertain = synapse.execute("uncertain a = 0 +/- 1\nuncertain b = 2 +/- 0.1\na*b")
assert uncertain.nominal == 0 and uncertain.uncertainty == 2
try:
    synapse.execute("1+2", sandbox=True)
except NotImplementedError:
    pass
else:
    raise AssertionError("Isolation request silently accepted")
examples = sorted((root / "examples").glob("*.syn"))
assert {"hello.syn", "uncertainty.syn", "parallel.syn", "quantum_bell.syn"} <= {path.name for path in examples}
for example in examples:
    with redirect_stdout(io.StringIO()) as output:
        result = synapse.run_file(example)
    assert output.getvalue()
    if example.name == "quantum_bell.syn":
        assert set(result["counts"]) <= {"00", "11"}
        assert sum(result["counts"].values()) == 256
cli = subprocess.check_output([sys.executable, "-I", "-m", "synapse_lang.cli", "-c", "1+2"], text=True)
assert cli.strip() == "3.0"
repl = subprocess.run([sys.executable, "-I", "-m", "synapse_lang.repl"], input="x = 2\nx*3\n.exit\n",
                      text=True, capture_output=True, check=True)
assert "6.0" in repl.stdout
benchmark = subprocess.check_output([sys.executable, "-I", "-m", "synapse_lang.benchmark", "-n", "5", "--json"], text=True)
assert "uncertain" in json.loads(benchmark)["programs"]
print(f"Installed-wheel API, examples, Bell counts, CLI, REPL, and benchmarks passed: {synapse.__version__}")
