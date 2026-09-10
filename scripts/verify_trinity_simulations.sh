#!/bin/sh
# Software simulation checks only. Not a publication or hardware-validation gate.
set -eu
cd "$(dirname "$0")/.."
mkdir -p benchmarks/trinity-review
.venv/bin/python -m pytest tests/ -o addopts='' -q --junitxml=benchmarks/trinity-review/synapse-tests.xml
.venv/bin/python -m pytest quantum-net/tests -o addopts='' -q --junitxml=benchmarks/trinity-review/network-tests.xml
.venv/bin/python -m ruff check tests/test_trinity_validation.py quantum-net/tests/test_sim_invariants.py quantum-net/qnet_runtime/sim_core.py scripts/trinity_simulations.py
.venv/bin/python scripts/trinity_simulations.py > benchmarks/trinity-review/simulations.json
printf '%s\n' 'Simulation checks passed. Run scripts/verify_trinity_installed.py for companion wheels and bridge. Hardware gates remain separate.'
