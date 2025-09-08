import pytest
from synapse_lang.quantum import (
    QuantumSemanticError,
    validate_circuit,
    BackendConfig,
    NoiseConfig,
)

def _ops(seq):
    return [{"gate": g, "qubits": qs, "params": ps} for (g, qs, ps) in seq]

def test_unknown_gate():
    with pytest.raises(QuantumSemanticError, match="E1001"):
        validate_circuit(n_qubits=2, ops=_ops([("rzx", [0, 1], [])]))

def test_arity_mismatch():
    with pytest.raises(QuantumSemanticError, match="E1004"):
        validate_circuit(n_qubits=2, ops=_ops([("h", [0,1], [])]))

def test_duplicate_qubits_for_2q():
    with pytest.raises(QuantumSemanticError, match="E1003"):
        validate_circuit(n_qubits=2, ops=_ops([("cx", [0,0], [])]))

def test_index_out_of_range():
    with pytest.raises(QuantumSemanticError, match="E1002"):
        validate_circuit(n_qubits=2, ops=_ops([("h", [2], [])]))

def test_non_integer_qubit_index():
    with pytest.raises(QuantumSemanticError, match="E1101"):
        validate_circuit(n_qubits=2, ops=[{"gate":"h","qubits":[0.5],"params":[]}])

def test_params_count():
    with pytest.raises(QuantumSemanticError, match="E1005"):
        validate_circuit(n_qubits=1, ops=_ops([("rx", [0], [])]))

def test_backend_config_ok():
    cfg = BackendConfig(shots=1024, seed=123, noise=NoiseConfig(kind="ideal"))
    validate_circuit(n_qubits=2, ops=_ops([("h",[0],[]), ("cx",[0,1],[])]), backend=cfg)

def test_backend_shots_invalid():
    with pytest.raises(QuantumSemanticError, match="E1301"):
        validate_circuit(n_qubits=2, ops=[], backend=BackendConfig(shots=0))

def test_measurement_duplicate():
    with pytest.raises(QuantumSemanticError, match="E1011"):
        validate_circuit(n_qubits=2, ops=[], measurements=[[0],[0]])

def test_noise_model_dict_valid():
    backend = BackendConfig(shots=16, noise=NoiseConfig(kind="depolarizing", p1q=0.01, p2q=0.02, readout=0.03))
    validate_circuit(n_qubits=2, ops=_ops([("h", [0], []), ("cx", [0,1], [])]), backend=backend)

def test_noise_model_invalid_prob():
    with pytest.raises(QuantumSemanticError, match="E1202"):
        # construct manually to trip range check via direct validation of backend
        bad_noise = NoiseConfig(kind="depolarizing", p1q=1.5, p2q=0.0, readout=0.0)
        backend = BackendConfig(shots=10, noise=bad_noise)
        validate_circuit(n_qubits=1, ops=_ops([("h", [0], [])]), backend=backend)

def test_alias_gate_name():
    # cnot alias maps to cx and should pass
    validate_circuit(n_qubits=2, ops=_ops([("cnot", [0,1], [])]))
