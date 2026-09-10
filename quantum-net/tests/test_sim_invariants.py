"""Scheduling, grammar, and attenuation invariants with analytical references."""
import math

import pytest

from qnet_lang.lexer import Lexer
from qnet_lang.parser import Parser
from qnet_lang.tokens import Tok
from qnet_runtime.channels import Fiber
from qnet_runtime.entanglement import Entangler
from qnet_runtime.sim_core import Sim


def test_equal_time_events_keep_submission_order():
    sim = Sim()
    seen = []
    sim.schedule(1, lambda: seen.append("first"))
    sim.schedule(1, lambda: seen.append("second"))
    sim.run()
    assert seen == ["first", "second"]


def test_zero_horizon_and_resume_preserve_future_events():
    sim = Sim()
    seen = []
    sim.schedule(0, seen.append, 0)
    sim.schedule(2, seen.append, 2)
    sim.run(until=0)
    assert seen == [0]
    assert len(sim.q) == 1
    sim.run(until=1)
    sim.schedule(0.5, seen.append, 1.5)
    sim.run()
    assert seen == [0, 1.5, 2]
    assert sim.t == 2


@pytest.mark.parametrize("delay", [-1, float("inf"), float("nan")])
def test_invalid_delay_rejected(delay):
    with pytest.raises(ValueError):
        Sim().schedule(delay, lambda: None)


@pytest.mark.parametrize("source", [
    "network n { node", "network n { fiber(length=", "network n { node a(x=1",
    "network n { unexpected; }", "protocol p { send a; }",
])
def test_invalid_or_unsupported_syntax_fails_explicitly(source):
    with pytest.raises(SyntaxError):
        Parser(Lexer(source).lex()).parse()


def test_lexer_repeatability_and_tuple_compatibility():
    lexer = Lexer("node alice;")
    first = lexer.lex()
    assert lexer.lex() == first
    assert first[0].type == Tok.NODE
    assert tuple(first[0]) == (Tok.NODE, "node")


@pytest.mark.parametrize("declaration", ["fiber(length=10) a b;", "fiber a b(length=10);"])
def test_link_parameter_placement(declaration):
    ast = Parser(Lexer(f"network n {{ node a; node b; {declaration} }}").lex()).parse()
    link = ast.statements[0].body[2]
    assert link.nodes == ["a", "b"]
    assert link.params[0].value == 10


@pytest.mark.parametrize("length", [0, 10, 50, 100])
def test_seeded_link_success_matches_analytical_attenuation(length):
    trials = 12000
    expected = math.exp(-math.log(10) * length * 0.2 / 10)
    sim = Sim(seed=2026)
    entangler = Entangler(sim, Fiber(length_km=length, loss_db_km=0.2))
    successes = []
    for _ in range(trials):
        entangler.attempt("alice", "bob", successes.append)
    # Six binomial standard errors, with one-count allowance at the endpoints.
    tolerance = 6 * math.sqrt(expected * (1 - expected) / trials) + 1 / trials
    assert abs(len(successes) / trials - expected) <= tolerance
    # Fidelity is deliberately not validated: the implementation uses a heuristic.
