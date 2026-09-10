"""The protocol modules refuse explicitly and describe themselves as roadmap."""
import importlib

import pytest

from qnet_runtime import protocols


@pytest.mark.parametrize("name", protocols.ROADMAP)
def test_each_protocol_module_refuses_to_run(name):
    module = importlib.import_module(f"qnet_runtime.protocols.{name}")
    assert module.STATUS == "roadmap"
    with pytest.raises(NotImplementedError) as info:
        module.run()
    assert "no security or fidelity claim" in str(info.value)


def test_package_declares_roadmap_status_and_no_claims():
    assert protocols.STATUS == "roadmap"
    assert set(protocols.ROADMAP) == {"qkd_bb84", "teleport", "swapping", "purification"}
    doc = protocols.__doc__ or ""
    assert "no security" in doc and "parse-only" in doc
