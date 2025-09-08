"""Synapse packaged core.

Public surface:
- parse: parse source to AST
- SynapseInterpreter: execute code
- run(source: str) helper
"""
from .synapse_parser import parse
from .synapse_interpreter import SynapseInterpreter

def run(source: str):
	return SynapseInterpreter().execute(source)

__all__ = ["parse", "SynapseInterpreter", "run"]

