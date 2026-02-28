import os
import tempfile

import numpy as np

from synapse_lang.data.loader import resolve_data


def test_resolve_list_to_ndarray():
    params = {"data": [[1.0, 2.0], [3.0, 4.0]]}
    resolved = resolve_data(params)
    assert isinstance(resolved["data"], np.ndarray)
    assert resolved["data"].shape == (2, 2)


def test_resolve_leaves_non_data_keys_alone():
    params = {"kernel": "quantum", "layers": 3}
    resolved = resolve_data(params)
    assert resolved["kernel"] == "quantum"
    assert resolved["layers"] == 3


def test_resolve_csv_file():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False
    ) as f:
        f.write("a,b\n1.0,2.0\n3.0,4.0\n")
        path = f.name
    try:
        params = {"train_data": path}
        resolved = resolve_data(params)
        assert isinstance(resolved["train_data"], np.ndarray)
        assert resolved["train_data"].shape == (2, 2)
    finally:
        os.unlink(path)


def test_resolve_npy_file():
    arr = np.array([[1.0, 2.0], [3.0, 4.0]])
    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        np.save(f, arr)
        path = f.name
    try:
        params = {"data": path}
        resolved = resolve_data(params)
        assert np.array_equal(resolved["data"], arr)
    finally:
        os.unlink(path)


def test_resolve_already_ndarray():
    arr = np.array([1, 2, 3])
    params = {"labels": arr}
    resolved = resolve_data(params)
    assert np.array_equal(resolved["labels"], arr)
