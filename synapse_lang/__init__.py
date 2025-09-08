"""Synapse packaged core minimal exports.

Lazy imports keep heavy / optional deps (e.g. cryptography) from triggering
when only parsing or basic interpretation is needed (like tests).
"""
from __future__ import annotations
from .synapse_parser import parse  # direct safe import
from .synapse_interpreter import SynapseInterpreter

def run(source: str):
	return SynapseInterpreter().execute(source)

__all__ = ["parse", "SynapseInterpreter", "run"]

