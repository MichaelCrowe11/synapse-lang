"""
Synapse Language - Enhanced Error Handling
Provides human-friendly diagnostics with source excerpts and carets.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceLoc:
    line: int
    col: int
    line_text: Optional[str] = None


class SynapseError(Exception):
    def __init__(self, message: str, loc: Optional[SourceLoc] = None):
        super().__init__(message)
        self.loc = loc

    def pretty(self) -> str:
        if not self.loc or not self.loc.line_text:
            return str(self)
        pointer = " " * max(0, self.loc.col - 1) + "^"
        return f"{self}\nLine {self.loc.line}: {self.loc.line_text}\n       {pointer}"


class ParseError(SynapseError):
    pass


class RuntimeErrorSynapse(SynapseError):
    pass


class TypeErrorSynapse(SynapseError):
    pass


class UndefinedSymbolError(SynapseError):
    pass