# Trinity validation and private rollout gates

> Historical review snapshot. The continuation repairs the companion foundation;
> see [implementation blueprint](trinity-implementation-blueprint.md) and
> `benchmarks/trinity-implementation/final-summary.json` for current evidence.
> Hardware, remote CI and product rollout remain unverified.

## Decision

Continue development privately. Do not publish the three-language stack or integrate
it into products yet. Synapse's local gate passes, but isolated companion-wheel
checks fail and no real-device or real-dataset validation has been performed.
No external publication, product modification, or announcement occurred in this pass.

## Agent team

Three independent Crowe console agents ran with read-only tool autonomy:

- Synapse reviewer: uncertainty propagation, calibration use cases, noise semantics.
- Qubit Flow reviewer: joint-state storage, gate execution, package imports and CLI.
- Quantum Net reviewer: parser coverage, event ordering, BB84, entanglement placeholders.

Logs are retained under `benchmarks/trinity-review/`. Reports were incomplete in
places and are treated as leads, not proof. The lead independently reproduced
selected findings and ran tests. In particular, a proposed agent calibration
formula had a factor-of-two error: for theta = 2 asin(sqrt(p)), the derivative is
1 / sqrt(p(1-p)), not 2 / sqrt(p(1-p)). It was not adopted.

## Implemented fixes

1. Quantum Net lexer emits named tuple tokens, retaining tuple compatibility while
   providing parser `.type` and `.value` attributes. Repeated lexing no longer
   duplicates tokens.
2. Quantum Net parsing no longer consumes the network/protocol keyword twice;
   link parameters accept the tested prefix syntax and existing postfix syntax;
   malformed or incomplete input raises SyntaxError instead of attribute errors.
3. Quantum Net events use stable sequence numbers for equal-time ordering. A time
   horizon preserves future events, handles zero explicitly, and supports resuming.
   Negative or non-finite event delays are rejected. `run(until=t)` advances the
   simulation clock to t even when the queue empties earlier.
4. Both legacy Qubit Flow parser copies dispatch gate tokens correctly and reject
   unsupported statements/gates instead of hanging without consuming input.
5. Both legacy Qubit Flow interpreter copies now refuse two-qubit gates explicitly
   rather than discard their computed state and return a success message.
   This is a correctness safeguard, not an implementation of entanglement.
6. Added 23 cross-component numerical/source tests and 17 Quantum Net tests.
7. Added executable rotation-sensitivity and fiber-attenuation experiments plus a
   repeatable software-only verification command.

## Commands

```sh
sh scripts/verify_trinity_simulations.sh
sh scripts/verify_release.sh
```

The first command validates software simulations. The second is the existing
Synapse local gate with Linux compatibility, base-only wheel checks, isolation,
and benchmarks. Neither command validates the complete companion distributions
or authorizes publication. The main CI still needs an explicit companion-package
release gate before the three languages can be shipped together.

## Observed results

- Synapse suite without Docker boundary image: 505 passed, 56 skipped, 7 expected
  failures, plus 47 passing subtests.
- Synapse suite with Docker boundary image: 510 passed, 51 skipped, 7 expected
  failures, plus 47 passing subtests.
- Quantum Net source suite: 19 passed.
- Targeted lint and simulation-script syntax checks passed.
- Both companion wheels and sdists build; Twine metadata checks pass.
- A fresh environment installed the companion wheels and their dependencies.
  Quantum Net's flat network parser passed from that installed wheel.
- Qubit Flow installed runtime import failed: absolute `qubit_flow_ast` import
  cannot resolve outside the checkout.
- Both advertised companion CLI imports failed: corresponding `cli.py` modules
  do not exist. Advertised REPL modules are also absent by source inspection.
- The legacy root `test_qubit_flow.py` suite fails collection through
  `synapse_qubit_bridge` because legacy `synapse_ast.py` refers to undefined `List`.
  This failure is not hidden with an expected-failure marker.
- Full current Synapse gate was rerun after source changes. Its success is not a
  release approval for Qubit Flow or Quantum Net.

Artifacts: `benchmarks/trinity-review/simulations.json`,
`benchmarks/trinity-review/installed-validation.json`, test XML and logs in that
directory, plus `benchmarks/verification.json` for the Synapse gate.
Builds regenerate tracked egg-info metadata, including pre-existing documentation
whitespace. That generated diff needs review rather than a blind commit.

## High-value use-case candidates

These are development hypotheses, not demonstrated breakthroughs or quantum advantage.

### A. Uncertainty-aware rotation calibration

Implementation: Synapse carries angle uncertainty through p = (1 - cos(theta))/2;
Qubit Flow supplies the one-qubit rotation matrix. A SciPy matrix exponential is
an independent numerical reference. Seeded synthetic Monte Carlo checks local
first-order propagation at four angles. Cross-engine tests cover X/Y/Z rotations
on a three-qubit state against dense matrix operators.

Potential use: flag sensitivity and choose calibration sampling points for a
scientific application. This does not yet fit a hardware calibration or implement
a production shot allocator. The current uncertainty API does not track general
covariance through arbitrary expression chains.

Next evidence: obtain a named dataset with actual device counts, shot counts,
measurement bases, timestamps, backend calibration records and units; fit on one
split and assess predictions/interval coverage on a held-out split against a
classical baseline. Predeclare acceptance metrics before examining holdout data.

### B. Quantum-network loss budgeting

Implementation: 12,000 seeded Bernoulli attempts at each of 0/10/50/100 km are
compared with independent analytical attenuation. Scheduler tests cover tied
arrivals, time-zero execution and pause/resume without dropped events.

Potential use: a transmission-budget sandbox. Current `Entangler.attempt` is
synchronous and ignores channel latency/dark counts; fidelity is heuristic.
This is not yet a network latency planner or a validated entanglement simulator.

Next evidence: integrate an explicit delayed-arrival/detector model, then compare
against named laboratory loss/count/timestamp traces at held-out distances.
Do not equate optical survival probability with entanglement fidelity.

### C. QKD error-injection test harness

Implementation: a seeded test-only intercept/resend experiment uses the primitive
BB84 preparation, measurement and sifting methods. With 20,000 transmissions,
sifted ideal errors are zero and intercept/resend errors agree with the theoretical
25% rate within a six-standard-error allowance. Both keys are sifted using the
same index mask in this test.

Potential use: detect protocol implementation regressions and teach the effects
of interception. These primitive checks do not validate the legacy interpreter's
end-to-end QKD orchestration or create secure keys.

Next evidence: repair the orchestration's mismatched sifting, reject insufficient
error samples, specify authenticated classical communication, error correction,
privacy amplification and a finite-key security argument. E91, teleportation and
purification paths contain placeholders and must not make security claims.

## Remaining engineering gates

1. Select the canonical companion source layout and remove wheel import ambiguity.
   Implement the advertised CLI/REPL or stop advertising nonexistent entry points.
2. Implement shared joint-state ownership and qubit-index mapping before enabling
   Qubit Flow CNOT/CZ/entanglement. Test Bell/GHZ states, reversed controls, sequential
   collapse, inverse operations and dense-reference agreement.
3. Repair or retire the broken legacy bridge in favor of the supported Synapse API.
4. Separate executable Quantum Net grammar examples from roadmap examples. Empty
   protocol modules and heuristic E91/teleportation paths are not validated features.
5. Add independent, installed-wheel gates for all companion distributions and run
   the actual remote OS/Python matrix. Reconcile version and licensing decisions.
6. Supply a hardware backend or real dataset with a clear target, budget and scope.
   No hardware job was submitted and no real-world validation is claimed.

## Private product rollout, after the gates pass

The requested registry/version, product repositories and staging environments are
not yet specified. Do not infer them. Prefer a private candidate artifact and an
internal staging environment before public registry publication, because public
publication exposes the release even without an announcement.

For each explicitly approved product, define an owner, feature flag defaulting off,
synthetic/test tenant, data boundaries, error/latency/correctness acceptance metrics,
rollback action and observation window. First run shadow comparisons without
changing customer-visible decisions. Enable only for approved internal testers
once those comparisons pass. No customer-facing announcement until validation
and rollout are reviewed separately.

## Status update, 2026-09-10 06:45 MST (handoff from the console agent)

Gates 1 to 3 are done and verified twice: the console agent's installed checks (passed, 8 checks) and a second runtime's 27 of 27 checks from a copy of the tree in fresh environments (`benchmarks/trinity-implementation/independent-verification.json`, rerun after the final parser fix; the 06:15 snapshot is kept beside it). Local release gate: 556 passed, 51 skipped, 7 xfailed, 47 subtests passed in 8.71s. Trinity tests in the checkout: 69 passed in 1.20s. Legacy `test_qubit_flow.py`: 12 passed, 1 warning in 0.98s. Fault injection: 40 of 40 injected defects detected, 0 false alarms in 40 controls, ten fixed cases per category.

Gate 4 (Quantum Net grammar split, placeholder protocols) and gate 6 (hardware or real dataset) remain open. Gate 5 is partial: local installed-wheel gates exist and pass; the remote matrix has not run on GitHub, and the version above 2.4.0 and the license are undecided. Nothing published, nothing announced.

The blueprint and proposal are kept with the private working notes, outside this repository. Second-runtime verifier: `scripts/verify_trinity_independent.py`. Chart and demonstration video beside the console agent's own under `benchmarks/trinity-implementation/`.

## Status update, 2026-09-10 15:25 MST (gate 4 done)

Michael committed the milestone as `50aec021` at 08:11 and chose version 2.4.1; the license files were reconciled to proprietary and are still uncommitted. Gate 4 is now done in this tree: the three roadmap Quantum Net programs moved to `quantum-net/examples/roadmap/` with a README, a second runnable example (`two-hop.qnet`) sits beside `validated-flat.qnet`, `synapse-qnet` is documented with the commands that exist, the four empty `qnet_runtime.protocols` modules now refuse explicitly (`run()` raises NotImplementedError and each declares `STATUS = "roadmap"`), the lexer raises SyntaxError instead of RuntimeError on bad characters, `SPEC.md` states the executable scope, and the repository-only legacy interpreter refuses E91, teleportation, swapping and purification while its BB84 orchestration now sifts both parties with the same mask, discards the disclosed sample bits, refuses when too few bits remain, and states that it makes no security claim. New tests: `quantum-net/tests/test_examples_and_roadmap.py`, `test_protocol_stubs.py`. CI runs the Quantum Net source tests. Quantum Net suite 30 passed; whole checkout 618 passed, 56 skipped, 7 expected failures; legacy lint debt unchanged.

Open: gate 6 (real dataset or hardware, scope and budget) and the remote half of gate 5 (a push to run the matrix on GitHub). The browser Lab under `website/lab/` is verified locally and not deployed; its hosting target has not been named.

## Status update, 2026-09-10 17:00 MST (gate 6 harness, engine fix, CI matrix)

`synapse_lang/telemetry_validation.py` and `scripts/validate_uncertainty_telemetry.py` implement the bounded
validation the review asked for: vapour-pressure deficit (Tetens), dew point (Magnus) and CO2 excess over an assumed
420 ppm ambient, each compared three ways per row (library engine, an independent NumPy reference with hand-derived
partial derivatives, and Monte Carlo on the assumed input distributions). Acceptance thresholds and the input model
(rectangular bounds from the sensor's stated accuracy, bound over root three, uniform draws) are fixed in the module
before any dataset is opened; datasets stay outside the repository; `tests/test_telemetry_validation.py` covers the
math on a built-in fixture.

First run on a synthetic telemetry fixture (128 rows, 100,000 draws per row): first-order propagation agreed with
Monte Carlo on every row, but the library's standard uncertainty missed the 1e-8 relative threshold on every row by
about one part in a million. Cause: `UncertaintyEngine._linear_propagation` differentiated with a fixed absolute step
of 1e-8, leaving roundoff in every propagated uncertainty, and silently reported a zero derivative when the expression
raised. Fixed: the step is now 1e-5 times max(1, |x|) and an undifferentiable variable raises instead of understating
the uncertainty. Rerun: every check passes; library versus analytic within 3.4e-11.

The real-data gate is still unmet: the fixture was synthetic and is labelled so in its report; the real sensor
database was unreachable during this pass. When it is reachable, run the same command on a chronological 80/20 split
and open the holdout once.

CI matrix on the pushed branch: all Linux and macOS jobs and the isolation job passed; three Windows jobs failed on
one timing test that divided by a serial time the Windows clock reports as zero. Fixed with perf_counter and a guard.
Whole checkout now 627 passed, 56 skipped, 7 expected failures.

## Status update, 2026-09-10 17:45 MST (remote matrix green, private candidate)

The remote CI matrix ran on GitHub for the pushed branch: 14 of 14 jobs passed (Ubuntu, macOS and Windows on
Python 3.10 to 3.13, plus the Docker isolation job), including the Quantum Net source tests. A draft pre-release,
`v2.4.1-rc1`, holds the three wheels and source distributions built from a clean checkout of the same commit with a
checksum file; it is a draft, visible to collaborators only, and nothing has been published to any index. The browser
Lab under `website/lab/` was deployed to a staging origin and passed its 20 browser checks there.

Gate 5 is therefore closed except for the operator's publication decision. Gate 6 remains open on real data.
