"""Every shipped (top-level) example must run cleanly and produce output.

Examples under examples/roadmap/ are aspirational and intentionally excluded.
"""
import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from synapse_lang.synapse_interpreter import SynapseInterpreter

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.syn"))  # top-level only, not roadmap/


def test_examples_present():
    names = {p.name for p in EXAMPLE_FILES}
    assert {"hello.syn", "uncertainty.syn", "parallel.syn", "quantum_bell.syn"} <= names


@pytest.mark.parametrize("example", EXAMPLE_FILES, ids=lambda p: p.name)
def test_example_runs_and_prints(example):
    source = example.read_text(encoding="utf-8")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        SynapseInterpreter().execute(source)
    assert buffer.getvalue().strip(), f"{example.name} produced no output"


def test_uncertainty_propagation_output():
    source = (EXAMPLES_DIR / "uncertainty.syn").read_text(encoding="utf-8")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        SynapseInterpreter().execute(source)
    # Propagated result should carry an uncertainty (the "value ± uncertainty" form).
    assert "±" in buffer.getvalue()
