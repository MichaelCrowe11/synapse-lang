# Qubit Flow

A small language for writing qubit circuits as text and running them on a state-vector simulator, for people learning circuits without hardware.

## Status

early stage. The parser and simulator run single-qubit gates `H`, `X`, `Y`, `Z`, `RX`, `RY`, `RZ`, `PHASE`, two-qubit `CNOT` and `CZ`, `measure`, and Bell or GHZ `entangle`. The grammar also has keywords for `TOFFOLI`, `superpose`, `teleport`, `grovers`, `shors`, `qft`, `vqe`, `qaoa`, error correction and qudits; the interpreter refuses each of them with an error instead of pretending. The two `.qflow` files that used to sit in `examples/` (a teleportation protocol and a VQE ansatz) use a syntax the parser does not accept; they now live in `examples/roadmap/`. There is no hardware backend and no noise model.

The distribution name is `synapse-qubit-flow`. PyPI holds a 1.0.0 from 2025-09-09 built from older code; the version number in this repository is also 1.0.0, so install from the repository until the next release bumps it.

## Install and first run

Run on 2026-09-10 on macOS in a fresh virtual environment (Python 3.12), from a clone of `MichaelCrowe11/synapse-lang`:

```bash
pip install ./qubit-flow-package
synapse-qflow --help
```

```
usage: synapse-qflow [-h] file

Qubit Flow statevector execution

positional arguments:
  file        Source file or - for stdin

options:
  -h, --help  show this help message and exit
```

A Bell pair, read from standard input:

```bash
printf 'qubit a\nqubit b\nH[a]\nCNOT[a,b]\n' | synapse-qflow -
```

```
{"messages": ["qubit a = QuantumState(1 qubits): [1.+0.j 0.+0.j]", "qubit b = QuantumState(1 qubits): [1.+0.j 0.+0.j]", "Applied gate to a", "Applied gate to a, b"], "probabilities": [0.4999999999999999, 0.0, 0.0, 0.4999999999999999], "qubit_order": ["a", "b"], "measurements": {}}
```

Add a measurement and the state collapses; which branch you get varies from run to run:

```bash
printf 'qubit a\nqubit b\nH[a]\nCNOT[a,b]\nmeasure a -> m\n' | synapse-qflow -
```

```
{"messages": ["qubit a = QuantumState(1 qubits): [1.+0.j 0.+0.j]", "qubit b = QuantumState(1 qubits): [1.+0.j 0.+0.j]", "Applied gate to a", "Applied gate to a, b", "Measured a: 1"], "probabilities": [0.0, 0.0, 0.0, 1.0], "qubit_order": ["a", "b"], "measurements": {"m": 1}}
```

`synapse-qubit-flow` starts a read-eval-print loop over the same interpreter; `:quit` leaves it. A file with a syntax error exits with status 1.

## What runs today

- Qubit declarations, with an optional initial state (`qubit a = |1>`).
- The gates listed under Status, applied to a shared dense state vector, so entangled qubits share one state object (`tests/test_trinity_implementation.py`, `test_bell_sequential_collapse`).
- `measure q -> name`: collapses the state, records the outcome under `name`.
- `entangle(a,b) bell` and `entangle(a,b,c) ghz` on zero-state inputs (`test_ghz_append_inverse_and_marginals`).
- A bridge to Synapse (`qubit_flow_lang.bridge`) that the Synapse interpreter uses when both packages are installed.
- Two console scripts, `synapse-qflow` and `synapse-qubit-flow`; the repository's `scripts/verify_trinity_installed.py` checks both from a built wheel.

## Roadmap (not built)

Algorithm keywords (`grovers`, `shors`, `qft`, `vqe`, `qaoa`), `teleport`, `superpose`, `TOFFOLI`, error-correction blocks, qudits, and the programs in `examples/roadmap/*.qflow`.

## Limits

This is a dense state-vector simulator: memory grows as 2^n complex amplitudes, so it is for a handful of qubits. Measurement uses Python's `random` module and is not seeded by the CLI. Results are checked against analytic expectations in the tests (Bell and GHZ marginals), not against another simulator. Nothing here has run on quantum hardware, and nothing here is a claim about quantum advantage.

## License and contact

Proprietary; see the repository `LICENSE`. michael@crowelogic.com
