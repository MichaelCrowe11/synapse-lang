# Release issue register

These are local tracked issue IDs, not claims that remote GitHub issues exist.
Strict expected failures remain visible in every full-suite report. An unexpected
pass fails the suite, requiring review and removal of the marker. Other skips include missing integrations and unsupported legacy feature tests.
They are distinct from these seven known roadmap expectations and must not all
be described as optional hardware coverage.

## SL-R01

Pipeline stage/fork DSL parsing is incomplete. The existing test recovers into an
incorrect stage node. `TestLanguageIntegration.test_pipeline_processing` retains
its assertions and expects AssertionError until pipeline grammar is implemented.

## SL-R02

Stream checkpoint synchronization is not an executable language feature.
`test_stream_synchronization` expects the existing AST-shape AssertionError.

## SL-R03

Symbolic function declarations and solve/prove DSL operations are roadmap syntax.
`test_symbolic_mathematics` expects the existing empty-AST IndexError.

## SL-R04

The enhanced tensor-map DSL is unimplemented. The minimal parser's basic tensor
declaration routing was fixed and its tests now pass; this separate tensor-map
expectation remains a strict AttributeError expected failure.

## SL-R05

Adaptive parameter-sweep refinement is not implemented. The legacy test expects
record-shaped adaptive results, whereas supported fixed-grid sweeps return a
dictionary of parameter tuples to values. It remains a strict TypeError expected
failure, not a claim that adaptive sampling works.

## SL-R06

Automatic serial/parallel strategy selection is not implemented. Its test remains
a strict AttributeError expected failure for the absent optimize_strategy API.

## SL-R07

Automatic memory-budget-based scheduling is not implemented. Bounded queue depth
and explicit batch sizes are supported; the memory_limit/auto_batch contract
remains a strict TypeError expected failure. A fixed test budget avoids hiding
that missing API behind a missing psutil dependency.

## Resolved supported-core defects and test contracts

- PCG: copy NumPy's read-only diagonal before constructing the Jacobi preconditioner.
- Quantum designer: repair single-qubit indexing and CNOT permutation; execute
  supported phase/rotation gates; reject unsupported simulation gates and invalid
  arity, indices, or duplicate qubits. Tests use QuantumGate objects and returned
  probabilities, the existing public API, rather than nonexistent amplitude APIs.
- Backend validation: check directly constructed noise probabilities, including NaN.
- Minimal parser: route the TENSOR token to its implemented declaration parser.
- SVD test: reconstruct correctly using reduced columns of full U; no numeric
  tolerance is weakened and the backend's full-matrices contract is preserved.
- VQE test: allow convergence rather than requiring success after five iterations;
  optimizer success flags themselves are unchanged.
- Integration AST tests: use ProgramNode.body and AssignmentNode.value for uncertain
  declarations. Roadmap execution is not inferred from parser-only successes.
- Shared-state test: use the implemented atomic update/get API.
- Fixed parameter-sweep tests: assert tuple-keyed dictionary values, preserving
  numerical and uncertainty checks.
- Timing tests: remove universal GIL-thread speedup/overhead assertions; retain result
  equality and report timings. Performance decisions use paired benchmarks instead.
- Legacy security wrappers: fail closed instead of running a broken in-process
  pseudo-sandbox. External isolation is available as a separate opt-in runner.
- Monte Carlo convergence test: use seeded square-normal mean/variance references
  and decreasing standard error; propagated distribution standard deviation must
  not be required to decrease with sample count.
- Mock training-loop test: seed its local data/noise generator and include the
  classification-loss chain rule in the finite-difference gradient; assert loss
  reduction against the initial model as well as the original loss bound.
- Scientific arithmetic: unify interpreter arithmetic with UncertainValue; use
  signed first-order derivatives for division, correlated products, and uncertain
  exponents; handle scalar powers at zero explicitly.

## SL-Q01: legacy static analysis

The repository has pre-existing lint and typing debt beyond this patch. New
verification and isolation modules are lint-gated; the whole-package legacy audit
is retained as a visible, non-blocking CI diagnostic, not reported as clean.

## SL-Q02: remote Windows/macOS matrix

Local verification cannot prove Windows behavior. The full CI matrix must actually
run on its OS-specific runners before cross-platform release approval. No remote
run is triggered and no cross-platform success is claimed merely from editing YAML.
