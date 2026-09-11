# Quantum Net

A grammar for describing small quantum networks (nodes and links) as text, with a checker that reports whether a file parses, for people sketching network layouts before any protocol code exists.

## Status

early stage, parse-only. `synapse-qnet` reads a `.qnet` file, validates it against the current grammar and prints a JSON summary. It does not execute a networking protocol. The `qnet_runtime.protocols` modules for BB84, E91, teleportation, entanglement swapping and purification exist as stubs that say so when called. Three older example programs (backbone, QKD, teleportation) describe where the grammar is headed; they live in `examples/roadmap/` and are rejected by the parser today, and `tests/test_examples_and_roadmap.py` asserts that rejection so a file can only be promoted deliberately.

The distribution name is `synapse-quantum-net`. PyPI holds a 1.0.0 from 2025-09-09 built from older code; the version in this repository is also 1.0.0, so install from the repository until the next release bumps it.

## Install and first run

Run on 2026-09-10 on macOS in a fresh virtual environment (Python 3.12), from a clone of `MichaelCrowe11/synapse-lang`:

```bash
pip install ./quantum-net
cd quantum-net
synapse-qnet --help
```

```
usage: synapse-qnet [-h] file

Quantum Net grammar validation only, not protocol execution

positional arguments:
  file        Source file or - for stdin

options:
  -h, --help  show this help message and exit
```

```bash
synapse-qnet examples/validated-flat.qnet
synapse-qnet examples/two-hop.qnet
```

```
{"mode": "parse-only", "statements": 1, "names": ["demo"]}
{"mode": "parse-only", "statements": 1, "names": ["two_hop"]}
```

```bash
pip install pytest
python -m pytest tests -o addopts='' -q
```

```
30 passed in 3.76s
```

## What runs today

- Lexer and parser for the flat network grammar (`tests/test_parser.py`).
- The two examples above, and the roadmap files rejected on purpose (`tests/test_examples_and_roadmap.py`).
- Simulator invariants for the state objects in `qnet_runtime` (`tests/test_sim_invariants.py`, `tests/test_sim_teleport.py`); these test the linear algebra, not a network protocol.
- Protocol stubs that raise a clear error instead of returning a fake result (`tests/test_protocol_stubs.py`).
- Two console scripts, `synapse-qnet` and `synapse-quantum-net` (a read-eval-print loop; `:quit` leaves it).

## Roadmap (not built)

Typed nodes with memory parameters, protocol blocks with per-node code, entanglement distribution with repeaters, application blocks with trial runs and reports, and execution of any key-distribution or teleportation protocol. See `examples/roadmap/README.md`.

## Limits

Nothing here distributes keys, teleports states, or models a real channel. No security property is claimed or tested. The package does not talk to hardware or to any network.

## License and contact

Proprietary; see the repository `LICENSE`. michael@crowelogic.com
