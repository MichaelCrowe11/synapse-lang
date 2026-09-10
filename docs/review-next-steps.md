# Synapse review and next steps

## Recommendation

Stabilize and release the implemented scientific core before adding more language
syntax or compiler backends. The current candidate has useful measured improvements,
but its release evidence and public claims must remain narrower than the roadmap.

This review examined the local `optimize-runtime-e2e` working tree based on
`c41c9f624254e87ee45465fed9c3eb9b3f7e5d2d`. Substantial runtime changes already
existed before this review; this pass preserved them and completed verification
workflow fixes. Nothing was committed, pushed, published, or deployed.

## Review of the pasted assessment

- Correct priority: correctness and distribution consistency precede aggressive
  optimization. That remains the recommendation.
- Outdated local-state observation: the formerly empty directory now contains a
  Git checkout and an existing runtime optimization implementation.
- Historical version claims: the pasted source/PyPI/local version comparison is
  not a fresh registry check. This pass verified source and built-wheel version
  2.4.0, not the current public PyPI version or global installations.
- Correct scope: README runnable examples are a better supported-feature contract
  than older comprehensive review documents. Pipeline, symbolic DSL, adaptive
  scheduling, and other roadmap expectations are not passing implementations.

## Findings and actions

| Priority | Finding | Action in this pass or release requirement |
| --- | --- | --- |
| P0 | Verification could report success with missing Linux success evidence, hard-coded platform claims, and incomplete isolation checks. | Replaced text-summary inference with validated JUnit results, required actual isolation test cases, checked benchmark trials, and invalidated old success before each run. |
| P0 | Wheel verification reused a virtual environment and hard-coded version 2.4.0. | Fresh retained base-only environment on every run; exactly one candidate wheel required; version-neutral Dockerfile inputs. |
| P1 | Matrix staging reused files from earlier runs. | Fresh retained staging directory, including workflow test inputs; Linux JUnit copied from retained containers. |
| P1 | Skipped unsupported features were labeled optional integrations. | Report now lists unclassified skips explicitly and states that unsupported features are among them. |
| P1 | Public license statements conflict. | Before release, reconcile MIT README/project metadata with the proprietary classifier and bundled license documents; this pass does not choose legal terms. |
| P1 | Existing v2.4.0 tag already points to earlier code; sandbox behavior and parallel execution contracts change. | Choose a new release version and document compatibility impact before tagging. Do not republish changed code as the old artifact. |
| P1 | Remote OS matrix is configured, not executed here. | Run required CI on the approved repository/branch before release approval. |
| P2 | Whole-package lint/type debt and roadmap gaps remain. | Keep these visible; do not describe targeted lint success as repository-wide cleanliness. |

## End-to-end workflow implemented and executed

From the project root:

```sh
sh scripts/verify_release.sh
```

The existing `.venv` must have the project's runtime/JIT dependencies plus pytest,
PyYAML, Ruff, build, and Twine. Docker must be available. Dependency installation
and base-image builds require network access; Linux test containers run offline.

Sequence:

1. Mark the verification record running, with failure status on an unsuccessful exit.
2. Run the complete source suite and targeted lint, including 13 new workflow tests.
3. Build wheel and sdist; run Twine metadata checks.
4. Install the wheel with only base dependencies into a fresh environment.
5. Check installed API, uncertainty arithmetic, AST reuse, CLI, REPL, examples,
   Bell measurement counts, and benchmark output outside the source import path.
6. Measure local runtime phases.
7. Build Linux Python 3.10, 3.12, and 3.13 images from a fresh source stage;
   run suites and installed-wheel smoke checks, then collect JUnit evidence.
8. Build the separate isolation image and run the full suite with its immutable ID.
9. Run five alternating baseline/candidate benchmark trials.
10. Validate evidence and write `benchmarks/verification.json`.

Outputs include `benchmarks/review-e2e.txt`, `benchmarks/full-suite.xml`,
`benchmarks/linux-results-*.xml`, `benchmarks/linux-tests-*.txt`,
`benchmarks/paired-results.json`, and `release-dist/` artifacts. Fresh wheel
environments and matrix containers are retained for inspection. No cleanup is
performed automatically by the workflow scripts; review candidates before removal.
The isolation tests separately exercise the runner's temporary-container lifecycle.

This is a local release-readiness gate, not a publishing command. The reusable CI
workflow remains required by the publishing workflow. No remote action was triggered.
A generated report summarizes observed files; standalone report generation does not
rerun tests or cryptographically attest that the current tree matches those files.
Rerun the full workflow after candidate code changes.

## Observed verification

| Environment | Result |
| --- | --- |
| macOS arm64, Python 3.13.11, with isolation image | 487 passed, 51 skipped, 7 strict expected failures |
| Linux arm64 container, Python 3.10 | 482 passed, 56 skipped, 7 strict expected failures |
| Linux arm64 container, Python 3.12 | 482 passed, 56 skipped, 7 strict expected failures |
| Linux arm64 container, Python 3.13 | 482 passed, 56 skipped, 7 strict expected failures |
| Installed-wheel smoke checks | Passed locally without JIT and in all three Linux images with JIT |
| Targeted lint, shell syntax, distribution metadata | Passed |
| Remote Windows/macOS/Linux CI matrix | Not executed |

Each suite additionally reported 47 passing subtests. The Linux suites skip the
five Docker-boundary cases because the Docker socket is intentionally unavailable
inside those containers; those cases pass from the host against the isolation image.
Skipped tests and strict expected failures are not implemented-feature successes.

## Measured optimization outcome

Fresh five-pair local microbenchmarks against the base commit:

| Measurement | Baseline median | Candidate median | Interpretation |
| --- | --- | --- | --- |
| Package import | 1.251 s | 0.0168 s | About 74x paired improvement; lazy loading defers engine import cost |
| Source execution | 188.0 microseconds | 187.8 microseconds | Essentially unchanged |
| Reused AST execution | 5.36 microseconds | 4.69 microseconds | About 1.14x paired improvement |
| 8-qubit circuit workload | 4.28 ms | 1.06 ms | About 3.90x paired improvement |
| Sweep Python peak allocation | 10.47 MB | 0.805 MB | About 13x lower; not total process RSS |

Tiny-callback threaded Monte Carlo measured about 10.44 ms versus a roughly
0.676 ms baseline whose parallel flag did not actually parallelize the work.
This is not an equivalent parallel baseline and is not a performance win.
Prefer serial execution for such callbacks; benchmark blocking or GIL-releasing
work before recommending threads. Kernel and import improvements do not establish
a general application speedup.

## Proposed next steps, in order

1. **Release review:** choose a new version, reconcile licensing metadata, document
   sandbox/parallel compatibility changes, and review the existing uncommitted diff.
   Builds also regenerate tracked `synapse_lang.egg-info` files; review that noise
   separately instead of including it blindly in a commit.
2. **Remote evidence:** run the configured OS/Python CI matrix after an explicitly
   authorized push or PR. Address actual failures before treating support as proven.
3. **Supported-feature contract:** keep seven roadmap expected failures tracked;
   audit the additional exception-driven skips and classify each as an optional
   dependency, unsupported feature, or defect. Add regressions before fixing defects.
4. **Targeted optimization:** profile first useful execution as well as package import,
   representative multi-gate circuits, and realistic sweep/Monte Carlo callbacks.
   Prioritize measured bottlenecks rather than a JIT rewrite or new execution engine.
5. **Release only after approval:** publish the reviewed, newly versioned artifact after
   required CI passes, then verify registry installation and upgrade local environments
   separately. No global installations were changed in this pass.
