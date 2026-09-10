"""Executable examples parse; roadmap examples are rejected, so promotion is deliberate."""
from pathlib import Path

import pytest

from qnet_lang.cli import evaluate

ROOT = Path(__file__).resolve().parents[1]
EXECUTABLE = sorted((ROOT / "examples").glob("*.qnet"))
ROADMAP = sorted((ROOT / "examples" / "roadmap").glob("*.qnet"))


def test_example_sets_are_present():
    assert EXECUTABLE, "no executable examples beside the roadmap folder"
    assert ROADMAP, "roadmap examples were expected under examples/roadmap"


@pytest.mark.parametrize("path", EXECUTABLE, ids=lambda p: p.name)
def test_executable_examples_parse_and_say_parse_only(path):
    result = evaluate(path.read_text(encoding="utf-8"))
    assert result["mode"] == "parse-only"
    assert result["statements"] >= 1
    assert result["names"]


@pytest.mark.parametrize("path", ROADMAP, ids=lambda p: p.name)
def test_roadmap_examples_are_rejected_by_the_current_grammar(path):
    with pytest.raises((SyntaxError, ValueError)):
        evaluate(path.read_text(encoding="utf-8"))
