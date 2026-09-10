#!/bin/sh
# End-to-end local release gate, including Linux matrix and container isolation.
set -eu
cd "$(dirname "$0")/.."
# Invalidate the previous success record before any stage can fail.
printf '%s\n' '{"status":"running","published":false}' > benchmarks/verification.json
trap 'printf "%s\n" "{\"status\":\"failed\",\"published\":false}" > benchmarks/verification.json' 0
sh scripts/verify_runtime.sh
sh scripts/verify_linux_matrix.sh
docker build -f isolation/Dockerfile -t synapse-runtime-validation:local release-dist
SYNAPSE_TEST_IMAGE=$(docker image inspect synapse-runtime-validation:local --format '{{.Id}}')
export SYNAPSE_TEST_IMAGE
.venv/bin/python -m pytest tests/ -o addopts='' -q --junitxml=benchmarks/full-suite.xml
.venv/bin/python benchmarks/paired.py > benchmarks/paired-results.json

.venv/bin/python scripts/report_verification.py
trap - 0
