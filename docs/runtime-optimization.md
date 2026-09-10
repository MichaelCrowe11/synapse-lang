# Runtime optimization and verification

## Scope

This change optimizes the implemented interpreter, not the roadmap language.
It preserves sequential branch execution by default. No release is published
and existing global installations are not upgraded by local verification.
The package remains version 2.4.0; installed-wheel metadata is checked against
its runtime version. Python support is declared as 3.10+ to match existing syntax.

## Parse once

```python
from synapse_lang import parse, execute_program

program = parse("result = x * 2\nresult")
assert execute_program(program, context={"x": 3}) == 6
assert execute_program(program, context={"x": 9}) == 18
```

Each API execution gets a fresh interpreter. Execution does not mutate the AST;
callers must not mutate a shared AST during execution. Trusted context objects
are not security-isolated. No global AST cache is introduced.

## Safety and scientific correctness

- Execution defaults to `sandbox=False`. Explicit `sandbox=True` requests and
  CLI `--sandbox` fail before execution. The REPL also refuses sandbox requests.
  External process/container isolation is still required for untrusted code.
  Existing Python security helpers are not a supported isolation boundary.
- Zero-nominal multiplication uses first-order absolute derivatives, not relative
  errors that divide by zero. Both-zero nominal products have zero first-order
  uncertainty; this does not claim to calculate second-order product variance.
- `+/-`, `+-`, and `±` uncertainty delimiters produce equivalent values. Previously,
  the benchmark's `+/-` input silently lost its uncertainty.
- Fastmath is disabled by default. Numeric JIT tests compare actual interpreter
  results; unsupported AST nodes raise rather than compiling to silent no-ops.
  Full-language JIT support is not claimed.
- The compilation benchmark measures setup (including first-call compilation),
  warmed compiled execution, and actual source interpretation separately. Its
  comparison includes parsing on the interpreter side; use `synapse-bench` for
  the separate reused-AST baseline. Constant arithmetic may be compiler-folded,
  so its JIT speedup is not a general scientific-workload speedup.

## Parallel semantics

Use `execute(source, parallel=True)` or `synapse --parallel file.syn` to opt in.

- Each branch receives a deep copy of the entry variable state.
- Branches cannot read sibling writes. Move dependencies outside the block.
- Assignments are merged after every branch succeeds, in source order.
- Multiple branches assigning the same name raise; no assignments are committed
  on a conflict or exception. Nested branch assignments use the same rule.
- Mutating a copied input is branch-local unless its value is explicitly assigned
  to an output name. Backend selection requires sequential execution.
- Context callables remain trusted: closures, globals, I/O, and external side
  effects are not isolated or rolled back. Print order is not deterministic.
- Threads benefit blocking or GIL-releasing work, not arbitrary CPU-bound Python.

The Python task API supports bounded thread/process queues using `max_pending`
and `chunk_size` in `ParallelConfig`. These bounds apply to submitted batches;
results remain materialized. Process tasks must be picklable. Per-batch timeout
limits waiting for a result, not termination of already-running tasks. The
asyncio backend retains its existing gather behavior.

Parameter sweeps no longer build all partials and futures up front. The return
value remains a dictionary keyed by parameter tuples; grid coordinates use
parameter positions, not the parameter values themselves. `parallel=False`
executes directly on the caller thread.

Monte Carlo honors `parallel` and `n_cores` using bounded threads. Samples come
from a local seeded generator before task dispatch, producing identical serial
and parallel statistics for a deterministic function without reseeding NumPy's
global RNG. Arbitrary scalar callbacks are not automatically vectorized.

## Repeatable verification

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -e '.[dev,jit]' build twine
sh scripts/verify_runtime.sh
.venv/bin/python -m pytest tests/ -o addopts='' -q
```

The first script runs the entire test suite, targeted lint, wheel/sdist build,
metadata checks, fresh installed-wheel smoke checks without JIT, and benchmarks.
Artifacts use `release-dist/`, excluding the repository's old tracked archive.
Smoke checks run outside the source import path.

For the complete local workflow, including Linux compatibility and isolation:

```sh
sh scripts/verify_release.sh
```

The publishing workflow requires the reusable CI workflow before build. Its full
suite and base-only installed-wheel checks cover Python 3.10, 3.11, 3.12, and 3.13
on Linux, macOS, and Windows, with separate Linux isolation tests. These matrix
entries are configured requirements, not evidence of remote execution. Local
results cover macOS Python 3.13 and Linux containers on 3.10, 3.12, and 3.13.
Windows and the remaining remote combinations still require an actual CI run.

## Local measurements

See `benchmarks/baseline.json`, `benchmarks/optimized.json`, and
`benchmarks/phases.json`. Times are microbenchmarks on one machine, not promised
application speedups. The baseline imported once in a fresh process; optimized
cold-import timing is the median of five fresh processes. Gate timings use the
same input and loop counts before and after. Gate correctness is independently
checked against dense matrix operations across qubits and random complex states.

The stabilization pass resolved supported-core failures and reconciled outdated
API tests. Seven strict expected failures track unimplemented roadmap contracts
in [the local issue register](release-issues.md). Skipped tests include both missing integrations and additional unsupported
features; skips and expected failures are not counted as passing features.

The basic Monte Carlo test uses an explicit seed. Additional tests independently
verify uncertainty Jacobians, signed correlation derivatives, uncertain exponents,
quantum inverse operations, normalization, and seeded measurement distributions.
The legacy in-process security helpers now fail closed; see [external isolation](isolation.md).

Paired measurements are in `benchmarks/paired-results.json`: five alternating
fresh-process baseline/candidate trials, identical interpreter/dependencies, and
single-threaded numerical libraries. Source execution is approximately unchanged;
startup, gate kernels, and sweep scheduling memory improve. Tiny-callback threaded
Monte Carlo is slower than serial and is not advertised as an optimization for
that workload. Tracemalloc reports Python allocations, not total process RSS.

## Follow-up review

See [review, implemented workflow, and next steps](review-next-steps.md) for the
current observed results, workflow corrections, and remaining release decisions.
