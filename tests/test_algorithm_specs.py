from synapse_lang.quantum.algorithm_specs import ALGORITHM_SPECS, AlgorithmSpec


def test_spec_exists_for_all_algorithms():
    expected = [
        "grover_search", "qaoa_solve", "qae", "qarm", "qcmp",
        "qkmeans", "qpca", "qsencode", "qsvd", "qsvm", "qsvr",
        "qubo", "qmrmr",
    ]
    for name in expected:
        assert name in ALGORITHM_SPECS, f"Missing spec for {name}"


def test_qsvm_spec():
    spec = ALGORITHM_SPECS["qsvm"]
    assert "train_data" in spec.required
    assert "train_labels" in spec.required
    assert "kernel" in spec.optional
    assert spec.min_qubits == 2


def test_grover_spec():
    spec = ALGORITHM_SPECS["grover_search"]
    assert spec.min_qubits == 2


def test_qaoa_spec():
    spec = ALGORITHM_SPECS["qaoa_solve"]
    assert "problem" in spec.required
    assert "layers" in spec.optional


def test_spec_dataclass_fields():
    spec = ALGORITHM_SPECS["qpca"]
    assert isinstance(spec.required, set)
    assert isinstance(spec.optional, dict)
    assert isinstance(spec.min_qubits, int)
    assert isinstance(spec.result_fields, list)
