import numpy as np
from synapse_lang.results import SynapseQuantumResult


def test_result_with_counts():
    r = SynapseQuantumResult(
        counts={"00": 512, "11": 512},
        probabilities={"00": 0.5, "11": 0.5},
    )
    assert r.counts == {"00": 512, "11": 512}
    assert r.value is None
    assert r.classification is None
    assert r.data is None
    assert r.metadata == {}


def test_result_with_classification():
    r = SynapseQuantumResult(classification=[0, 1, 0, 1])
    assert r.classification == [0, 1, 0, 1]
    assert r.counts is None


def test_result_with_data():
    arr = np.array([[1.0, 2.0], [3.0, 4.0]])
    r = SynapseQuantumResult(data=arr)
    assert np.array_equal(r.data, arr)


def test_result_with_value_and_metadata():
    r = SynapseQuantumResult(
        value=-1.234,
        metadata={"layers": 3, "optimizer": "spsa"},
    )
    assert r.value == -1.234
    assert r.metadata["layers"] == 3
