#!/bin/sh
# Build and run Linux compatibility images locally, with no registry push.
set -eu
cd "$(dirname "$0")/.."
stage=$(.venv/bin/python scripts/prepare_matrix.py)
for version in 3.10 3.12 3.13; do
  docker build --build-arg "PYTHON_VERSION=$version" -f isolation/Matrix.Dockerfile \
    -t "synapse-matrix:py$version" "$stage" > "benchmarks/linux-build-$version.txt" 2>&1
  # Retain the container for diagnostics instead of deleting evidence.
  container=$(docker create --network=none --memory=2g --cpus=2 "synapse-matrix:py$version")
  status=0
  docker start -a "$container" > "benchmarks/linux-tests-$version.txt" 2>&1 || status=$?
  if [ "$status" = 0 ]; then
    status=$(docker inspect --format '{{.State.ExitCode}}' "$container")
  fi
  docker cp "$container:/work/linux-results.xml" "benchmarks/linux-results-$version.xml"
  if [ "$status" != 0 ]; then
    echo "Linux $version failed; see benchmarks/linux-tests-$version.txt (container $container)" >&2
    exit "$status"
  fi
  tail -3 "benchmarks/linux-tests-$version.txt"
done
