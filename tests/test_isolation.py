"""Boundary tests run with SYNAPSE_TEST_IMAGE set to a locally built image ID."""
import json
import os
import subprocess
import uuid

import pytest

from synapse_lang.isolation import container_command, run_isolated

IMAGE = os.environ.get("SYNAPSE_TEST_IMAGE")
requires_image = pytest.mark.skipif(not IMAGE, reason="External Docker image not configured")


def test_image_must_be_immutable():
    with pytest.raises(ValueError):
        container_command("python:latest", "test")


def test_all_isolation_controls_are_present():
    command = container_command("sha256:"+"0"*64, "test")
    assert {"--read-only", "--network=none", "--cap-drop=ALL", "--pids-limit=64",
            "--user=65534:65534", "--pull=never", "--security-opt=no-new-privileges:true"} <= set(command)
    assert not any(item.startswith(("--volume", "--mount", "--privileged")) for item in command)


@requires_image
def test_isolated_source_and_uncertainty():
    assert run_isolated("print(3)\n1+2", IMAGE) == {"result":3,"stdout":"3.0\n"}
    result = run_isolated("uncertain a = 0 +/- 1\nuncertain b = 2 +/- 0.1\na*b", IMAGE)
    assert result["result"] == {"nominal":0,"uncertainty":2}


@requires_image
def test_output_is_bounded():
    with pytest.raises(RuntimeError, match="output limit"):
        run_isolated("print(str(range(int(100000))))", IMAGE)


@requires_image
def test_memory_limit_terminates_workload():
    with pytest.raises(RuntimeError, match="exit 137"):
        run_isolated("range(int(1000000000))", IMAGE, memory_mb=128, timeout=20)


@requires_image
def test_timeout_removes_container(monkeypatch):
    from synapse_lang import isolation

    original = isolation.container_command
    names = []

    def sleeper(image, name, **kwargs):
        names.append(name)
        command = original(image, name, **kwargs)
        return command[:-2] + ["-c", "import time; time.sleep(60)"]

    monkeypatch.setattr(isolation, "container_command", sleeper)
    with pytest.raises(TimeoutError):
        run_isolated("1", IMAGE, timeout=1)
    result = subprocess.run(["docker", "container", "inspect", names[0]],capture_output=True)
    assert result.returncode != 0


@requires_image
def test_os_boundary_denies_writes_network_and_privilege():
    command = container_command(IMAGE, "synapse-isolated-"+uuid.uuid4().hex)
    probe = """
import json,os,socket
checks = {"uid":os.getuid(), "secret":os.environ.get("HOST_TEST_SECRET")}
try:
    open('/escape-proof','w').write('test')
    checks['root_write'] = True
except OSError:
    checks['root_write'] = False
try:
    os.setuid(0)
    checks['root'] = True
except PermissionError:
    checks['root'] = False
try:
    socket.create_connection(('1.1.1.1',443),timeout=.5)
    checks['network'] = True
except OSError:
    checks['network'] = False
checks['socket'] = os.path.exists('/var/run/docker.sock')
checks['pids'] = open('/sys/fs/cgroup/pids.max').read().strip()
checks['memory'] = open('/sys/fs/cgroup/memory.max').read().strip()
checks['cpu'] = open('/sys/fs/cgroup/cpu.max').read().strip()
print(json.dumps(checks))
"""
    result = subprocess.run(command[:-2]+["-c",probe],capture_output=True,text=True,timeout=10,
                            env={**os.environ,"HOST_TEST_SECRET":"test-sentinel-not-a-credential"},check=True)
    checks = json.loads(result.stdout)
    assert checks == {"uid":65534,"secret":None,"root_write":False,"root":False,
                      "network":False,"socket":False,"pids":"64","memory":str(512*1024*1024),"cpu":"100000 100000"}
