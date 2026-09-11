"""Uncertain literals must never lose their uncertainty, with or without the keyword."""
import io
from contextlib import redirect_stdout

import pytest

from synapse_lang import execute
from synapse_lang.uncertainty import UncertainValue


@pytest.mark.parametrize("op", ["±", "+/-", "+-"])
def test_plain_assignment_keeps_the_uncertainty(op):
    result = execute(f"x = 3 {op} 0.2\nx")
    assert isinstance(result, UncertainValue), f"{op!r} produced {result!r}"
    assert result.nominal == 3.0 and result.uncertainty == pytest.approx(0.2)


@pytest.mark.parametrize("op", ["±", "+/-"])
def test_arithmetic_on_a_plain_uncertain_literal_propagates(op):
    result = execute(f"x = 3 {op} 0.2\nx * 2")
    assert isinstance(result, UncertainValue)
    assert result.nominal == 6.0 and result.uncertainty == pytest.approx(0.4)


def test_keyword_form_is_unchanged():
    result = execute("uncertain x = 3 ± 0.2\nx * 2")
    assert isinstance(result, UncertainValue) and result.uncertainty == pytest.approx(0.4)


def test_print_shows_the_uncertainty():
    buf = io.StringIO()
    with redirect_stdout(buf):
        execute("x = 3 ± 0.2\nprint(x * 2)")
    assert "6.0" in buf.getvalue() and "0.4" in buf.getvalue(), buf.getvalue()


def test_literal_inside_an_expression():
    result = execute("y = (10 ± 1) / 2")
    result = execute("y = (10 ± 1) / 2\ny")
    assert isinstance(result, UncertainValue) and result.nominal == 5.0 and result.uncertainty == pytest.approx(0.5)
