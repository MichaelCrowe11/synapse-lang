#!/bin/sh
# Full local release verification. No push, publication, or global installation.
set -eu
cd "$(dirname "$0")/.."
PYTHON="$PWD/.venv/bin/python"
"$PYTHON" -m pytest tests/ -o addopts='' -q --junitxml=benchmarks/full-suite.xml
"$PYTHON" -m ruff check tests/test_runtime_optimization.py tests/test_scientific_invariants.py tests/test_isolation.py synapse_lang/benchmark.py synapse_lang/isolation.py synapse_lang/_container_worker.py benchmarks/runtime.py benchmarks/paired.py scripts/wheel_smoke.py scripts/verify_installed.py scripts/prepare_matrix.py scripts/report_verification.py tests/test_release_workflow.py
"$PYTHON" -m build --outdir release-dist
"$PYTHON" -m twine check release-dist/*
"$PYTHON" scripts/verify_installed.py
"$PYTHON" benchmarks/runtime.py > benchmarks/optimized.json
"$PYTHON" -m synapse_lang.benchmark -n 500 --json > benchmarks/phases.json
