"""Opt-in Docker isolation, separate from the trusted in-process API.

Requires an operator-built, immutable local image ID. No automatic pull,
network, host mounts, credentials, or host context objects enter the container.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import uuid
from pathlib import Path


def container_command(image, name, *, memory_mb=512, cpus=1):
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", image):
        raise ValueError("An immutable local sha256 image ID is required")
    if memory_mb < 64 or cpus <= 0:
        raise ValueError("Invalid resource limits")
    return [
        "docker", "run", "--rm", "--pull=never", "--name", name,
        "--network=none", "--read-only", "--cap-drop=ALL",
        "--security-opt=no-new-privileges:true", "--user=65534:65534",
        f"--memory={memory_mb}m", f"--memory-swap={memory_mb}m", f"--cpus={cpus}",
        "--pids-limit=64", "--ulimit=nofile=64:64", "--ulimit=core=0:0",
        "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=32m,mode=1777",
        "--env=OPENBLAS_NUM_THREADS=1", "--env=OMP_NUM_THREADS=1",
        "--env=PYTHONDONTWRITEBYTECODE=1", "--interactive",
        image, "python", "-I", "-m", "synapse_lang._container_worker",
    ]


def run_isolated(source, image, *, timeout=10, memory_mb=512):
    """Run source with a wall timeout; return JSON result and captured output."""
    if not isinstance(source, str) or timeout <= 0:
        raise ValueError("source must be text and timeout must be positive")
    payload = json.dumps({"source": source}).encode()
    if len(payload) > 65536:
        raise ValueError("Request exceeds 64 KiB")
    name = f"synapse-isolated-{uuid.uuid4().hex}"
    command = container_command(image, name, memory_mb=memory_mb)
    try:
        completed = subprocess.run(command, input=payload, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        # Killing the Docker client does not terminate the daemon-owned container.
        cleanup = subprocess.run(["docker", "rm", "--force", name], capture_output=True, timeout=10)
        if cleanup.returncode and b"No such container" not in cleanup.stderr:
            raise RuntimeError("Timed out and container cleanup failed; inspect Docker") from exc
        raise TimeoutError("Isolated execution exceeded its wall timeout") from exc
    if len(completed.stdout) > 1024 * 1024:
        raise RuntimeError("Isolated response exceeds output limit")
    if completed.returncode:
        raise RuntimeError(f"Isolated execution failed (exit {completed.returncode}); "
                           f"{completed.stdout[:1024].decode(errors='replace')}")
    return json.loads(completed.stdout)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Synapse in a restricted local Docker container")
    parser.add_argument("--image", required=True, help="Operator-built sha256 image ID")
    parser.add_argument("--timeout", type=float, default=10)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--code", "-c")
    source.add_argument("--file", type=Path)
    args = parser.parse_args(argv)
    code = args.code if args.code is not None else args.file.read_text(encoding="utf-8")
    print(json.dumps(run_isolated(code, args.image, timeout=args.timeout)))


if __name__ == "__main__":
    main()
