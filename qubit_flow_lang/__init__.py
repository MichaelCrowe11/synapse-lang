"""Checkout compatibility path for the canonical companion package.

This shim is excluded from the Synapse wheel.
"""
from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[1] / "qubit-flow-package" / "qubit_flow_lang")]
