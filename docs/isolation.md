# External execution isolation

The ordinary interpreter API remains trusted and in-process. `sandbox=True` and
the legacy `ExecutionSandbox`/`ProcessSandbox` wrappers fail closed. They do not
silently delegate to Docker or assume that Docker is installed.

## Opt-in runner

```sh
.venv/bin/python -m build --wheel --outdir release-dist
docker build -f isolation/Dockerfile -t synapse-runtime-validation:local release-dist
IMAGE=$(docker image inspect synapse-runtime-validation:local --format '{{.Id}}')
.venv/bin/python -m synapse_lang.isolation --image "$IMAGE" --code '1+2'
SYNAPSE_TEST_IMAGE="$IMAGE" .venv/bin/python -m pytest tests/test_isolation.py -q
```

Use only an operator-reviewed image built from this Dockerfile and wheel. An
immutable image ID prevents a moving tag from changing between invocations; it
does not establish that an arbitrary image is safe. Runtime image pulls are
forbidden. The build uses a pinned Python base digest and resolves dependencies
at build time. Freeze dependency hashes before claiming bit-reproducible builds.

## Enforced boundaries

- One ephemeral container per request; no host bind mounts or Docker socket.
- Non-root UID/GID 65534; no Linux capabilities; no privilege escalation.
- No external network; read-only root filesystem; bounded 32 MiB temporary space.
- One CPU, configurable memory and equal memory+swap cap, 64 PIDs, and 64 open files.
- Host-enforced wall timeout with explicit daemon-side container removal.
- Source-only JSON requests limited to 64 KiB; no callable/context deserialization.
- Captured program output limited to 64 KiB, JSON responses limited to 1 MiB.
- Nonzero exit status and container OOM termination are errors, never normal results.

The boundary tests exercise filesystem writes, network denial, privilege changes,
absence of host environment and Docker socket, cgroup CPU/PID/memory controls,
output limits, actual OOM exit 137, and timeout cleanup. Host environment tests use
an artificial sentinel, not a real credential.

## Limits

This is a tested container boundary, not a guarantee against kernel or Docker
vulnerabilities, denial of service against the daemon, or malicious operator-built
images. The Docker daemon and host remain trusted. Run Docker in a dedicated VM
for hostile multi-tenant deployments and commission a security review before
public untrusted execution. No public execution service is deployed by this patch.

PID and CPU quotas are inspected in the tests; process-fork exhaustion and all
possible kernel escape techniques are not exhaustively tested. On timeout, output
is discarded and failure is surfaced. Environment-specific cgroup support is
required; there is no unprotected execution fallback.
