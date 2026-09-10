"""Regression coverage for runtime correctness and measured optimizations."""
import copy
import json
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path

import numpy as np
import pytest

from synapse_lang import execute, execute_program, parse
from synapse_lang.parallel import ParallelBlock, ParallelConfig, ParameterSweep, parameter_sweep
from synapse_lang.quantum.core import SimulatorBackend
from synapse_lang.synapse_interpreter import SynapseInterpreter
from synapse_lang.uncertainty import UncertainValue, monte_carlo


def square(x):
    return x * x


def branches(first, second, tail=""):
    return f"parallel {{\nbranch a: {{\n{first}\n}}\nbranch b: {{\n{second}\n}}\n}}\n{tail}"


def test_reusable_program_is_unchanged_and_has_fresh_state():
    program = parse("y = x * 2\ny + 1")
    before = copy.deepcopy(program)
    assert execute_program(program, context={"x": 3}) == 7
    assert execute_program(program, context={"x": 9}) == 19
    with pytest.raises(NameError):
        execute_program(program)
    assert program == before


def test_reuse_never_reparses(monkeypatch):
    program = parse("x + 1")
    from synapse_lang import synapse_interpreter

    def fail(*args):
        raise AssertionError("reparsed")

    monkeypatch.setattr(synapse_interpreter.Lexer, "tokenize", fail)
    assert execute_program(program, context={"x": 2}) == 3


def test_program_concurrent_reuse():
    program = parse("x * 2")
    with ThreadPoolExecutor(4) as pool:
        assert list(pool.map(lambda x: execute_program(program, context={"x": x}), range(20))) == list(range(0, 40, 2))


@pytest.mark.parametrize("operation", [execute, execute_program])
def test_sandbox_fails_before_code_or_context_runs(operation):
    with pytest.raises(NotImplementedError, match="isolation"):
        operation("invalid", sandbox=True, context={"danger": lambda: pytest.fail()})


@pytest.mark.parametrize("operator", ["±", "+-", "+/-"])
def test_uncertainty_zero_nominal_in_source(operator):
    result = execute(f"uncertain a = 0 {operator} 1\nuncertain b = 2 {operator} 0.1\na * b")
    assert result.nominal == 0
    assert result.uncertainty == 2


@pytest.mark.parametrize("x,y,sx,sy", [(0, 2, 1, .1), (2, 0, .1, 1), (-2, 3, .1, .2), (0, 0, 1, 2)])
def test_uncertain_product_first_order_derivatives(x, y, sx, sy):
    result = UncertainValue(x, sx) * UncertainValue(y, sy)
    assert result.nominal == x * y
    assert result.uncertainty == pytest.approx(np.hypot(y * sx, x * sy))


def test_correlated_product_signed_derivatives():
    result = UncertainValue(-2, 1, correlation_id="x") * UncertainValue(2, 1, correlation_id="x")
    assert result.uncertainty == 0


@pytest.mark.parametrize("n", [1, 2, 4, 8])
def test_vectorized_gates_match_dense_reference(n):
    rng = np.random.default_rng(123)
    state = rng.normal(size=2**n) + 1j * rng.normal(size=2**n)
    state /= np.linalg.norm(state)
    original = state.copy()
    backend = SimulatorBackend()
    x = np.array([[0, 1], [1, 0]])
    h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    unitary, _ = np.linalg.qr(rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)))
    for q in range(n):
        for gate, result in [(x, backend._x(state, q, n)), (h, backend._h(state, q, n)),
                             (unitary, backend._single_unitary(state, q, n, unitary))]:
            full = np.kron(np.kron(np.eye(2**q), gate), np.eye(2**(n-q-1)))
            np.testing.assert_allclose(result, full @ state, atol=1e-14)
            assert np.linalg.norm(result) == pytest.approx(1)
            assert not np.shares_memory(result, state)
    np.testing.assert_array_equal(state, original)


def test_hadamard_twice_identity_with_zeros():
    state = np.zeros(32, dtype=complex)
    state[0] = 1
    backend = SimulatorBackend()
    for q in range(5):
        np.testing.assert_allclose(backend._h(backend._h(state, q, 5), q, 5), state, atol=1e-14)


def test_parallel_branches_really_overlap_and_merge():
    barrier = threading.Barrier(2, timeout=5)

    def wait(value):
        barrier.wait()
        return value

    assert execute(branches("x = wait(2)", "y = wait(3)", "x + y"), context={"wait": wait}, parallel=True) == 5


def test_default_parallel_syntax_remains_sequential():
    assert execute(branches("x = 2", "y = x + 1", "y")) == 3


def test_parallel_reads_use_entry_snapshot():
    source = branches("x = 10", "y = x", "y")
    assert execute(source, context={"x": 1}, parallel=True) == 1


def test_parallel_write_conflicts_do_not_commit():
    interpreter = SynapseInterpreter(parallel=True)
    interpreter.variables["x"] = 1
    with pytest.raises(ValueError, match="same names"):
        interpreter.execute(branches("x = 2", "x = 3"))
    assert interpreter.variables["x"] == 1


def test_parallel_failure_does_not_commit():
    interpreter = SynapseInterpreter(parallel=True)
    with pytest.raises(NameError):
        interpreter.execute(branches("x = 2", "y = missing"))
    assert "x" not in interpreter.variables


def test_parallel_mutable_input_is_copied():
    original = [1]

    def mutate(values):
        values.append(9)
        return len(values)

    result = execute(branches("x = mutate(values)", "y = len(values)", "x + y"),
                     context={"values": original, "mutate": mutate}, parallel=True)
    assert result == 3
    assert original == [1]


def test_nested_parallel_merge():
    nested = branches("x = 2", "y = 3")
    assert execute(branches(nested, "z = 4", "x+y+z"), parallel=True) == 9


@pytest.mark.parametrize("backend", ["threading", "multiprocessing"])
def test_bounded_batches_preserve_order(backend):
    cfg = ParallelConfig(max_workers=2, max_pending=2, chunk_size=3, backend=backend)
    assert ParallelBlock(cfg).execute(partial(square, x) for x in range(17)) == [x*x for x in range(17)]


def test_tasks_are_consumed_with_bounded_backpressure():
    consumed = 0
    started = threading.Event()
    release = threading.Event()

    def task():
        started.set()
        assert release.wait(5)
        return 1

    def tasks():
        nonlocal consumed
        for _ in range(40):
            consumed += 1
            yield task

    with ThreadPoolExecutor(1) as pool:
        future = pool.submit(ParallelBlock(ParallelConfig(max_workers=1, max_pending=2, chunk_size=3)).execute, tasks())
        try:
            assert started.wait(5)
            assert consumed <= 6
        finally:
            release.set()
        assert future.result() == [1]*40


def test_parallel_task_errors_surface():
    def fail():
        raise RuntimeError("task failed")

    with pytest.raises(RuntimeError, match="task failed"):
        ParallelBlock(ParallelConfig(max_pending=2)).execute([fail])


def test_sweep_grid_uses_positions_not_parameter_values():
    sweeper = ParameterSweep(lambda x, y: x * y)
    np.testing.assert_array_equal(sweeper.sweep_grid({"x": [10, 20], "y": [.5, 1.5]}), [[5, 15], [10, 30]])
    assert sweeper.sweep(x=[]) == {}
    assert sweeper.sweep_grid({"x": [], "y": [.5, 1.5]}).shape == (0, 2)


def test_serial_sweep_stays_on_caller_thread():
    identity = threading.get_ident()
    assert parameter_sweep(lambda x: threading.get_ident(), {"x": [1, 2]}, parallel=False) == {(1,): identity, (2,): identity}


def test_monte_carlo_seed_and_parallel_results_match():
    inputs = {"x": UncertainValue(2, .2)}
    serial = monte_carlo(square, inputs, samples=500, seed=7)
    parallel = monte_carlo(square, inputs, samples=500, seed=7, parallel=True, n_cores=2)
    assert serial.nominal == parallel.nominal
    assert serial.uncertainty == parallel.uncertainty
    assert inputs["x"].correlation_id is None


def test_monte_carlo_parallel_uses_requested_workers():
    threads = set()
    barrier = threading.Barrier(2, timeout=5)

    def function(x):
        threads.add(threading.get_ident())
        barrier.wait()
        return x

    monte_carlo(function, {"x": UncertainValue(1, .1)}, samples=2, parallel=True, n_cores=2, seed=3)
    assert len(threads) == 2


def test_monte_carlo_does_not_reseed_global_rng():
    state = np.random.get_state()
    monte_carlo(square, {"x": UncertainValue(2, .2)}, samples=10, seed=8)
    current = np.random.get_state()
    assert current[0] == state[0]
    np.testing.assert_array_equal(current[1], state[1])
    assert current[2:] == state[2:]


@pytest.mark.parametrize("samples,cores", [(1, 2), (10, 0)])
def test_monte_carlo_invalid_configuration(samples, cores):
    with pytest.raises(ValueError):
        monte_carlo(square, {"x": 1}, samples=samples, n_cores=cores)


def test_cold_import_and_arithmetic_leave_optional_engines_unloaded():
    code = "import sys,json,synapse_lang as s; assert s.execute('1+2') == 3; print(json.dumps(sorted(sys.modules)))"
    modules = json.loads(subprocess.check_output([sys.executable, "-c", code], text=True))
    assert not set(modules) & {"numba", "numpy", "scipy", "sympy", "matplotlib", "torch", "synapse_lang.quantum"}


def test_lazy_exports_are_cached():
    import synapse_lang

    assert synapse_lang.UncertainValue is UncertainValue
    assert synapse_lang.__dict__["UncertainValue"] is UncertainValue


@pytest.mark.parametrize("code", ["1+2*3", "x = 5\ny = x * 2\nz = y + x", "x = 0\nx+7", "2**3"])
def test_numeric_jit_matches_interpreter(code):
    pytest.importorskip("numba")
    from synapse_lang import compile

    compiled = compile(code, optimize=False)
    assert compiled() == execute(code)
    assert compiled.nopython_signatures
    assert compiled() == execute(code)


def test_compilation_benchmark_measures_interpreter(monkeypatch):
    pytest.importorskip("numba")
    from synapse_lang import jit_compiler

    interpreted_calls = []
    monkeypatch.setattr(jit_compiler, "compile_synapse_code", lambda source: lambda: 3)
    monkeypatch.setattr(SynapseInterpreter, "execute", lambda self, source: interpreted_calls.append(source) or 3)
    result = jit_compiler.benchmark_compilation("1+2", iterations=7)
    assert len(interpreted_calls) == 8
    assert result["interpreted_time"] > 0
    assert result["compilation_time"] > 0


def test_cli_sandbox_request_fails_closed():
    result = subprocess.run([sys.executable, "-m", "synapse_lang.cli", "--sandbox", "-c", "1+2"], text=True, capture_output=True)
    assert result.returncode == 1
    assert "isolation" in result.stderr
    assert not result.stdout


def test_release_build_requires_tests():
    import yaml

    workflow = yaml.safe_load((Path(__file__).parents[1] / ".github/workflows/publish.yml").read_text())
    assert workflow["jobs"]["build"]["needs"] == "test"
    assert workflow["jobs"]["test"]["uses"] == "./.github/workflows/ci.yml"
    ci = yaml.safe_load((Path(__file__).parents[1] / ".github/workflows/ci.yml").read_text())
    assert any("pytest tests/" in step.get("run", "") for step in ci["jobs"]["test"]["steps"])


def test_jit_rejects_unsupported_nodes():
    pytest.importorskip("numba")
    from synapse_lang.jit_compiler import ASTTranspiler

    with pytest.raises(NotImplementedError, match="does not support"):
        ASTTranspiler().transpile(object())


def test_benchmark_cli_validates_uncertainty_and_emits_phases(capsys):
    from synapse_lang.benchmark import main

    assert main(["-n", "2", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert set(report["programs"]["uncertain"]) == {"parse", "end_to_end", "reused_program"}


def test_benchmark_rejects_nonpositive_iterations():
    from synapse_lang.benchmark import main

    with pytest.raises(SystemExit):
        main(["-n", "0"])
