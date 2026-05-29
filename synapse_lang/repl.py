"""Interactive REPL for the Synapse language (the ``synapse-repl`` command).

This module was declared in ``[project.scripts]`` (``synapse-repl =
synapse_lang.repl:main``) but never shipped, so the command crashed with
ModuleNotFoundError. It is also imported by ``synapse_lang.cli`` for the
``--repl`` flag and by ``synapse_lang.__init__.main``.

The REPL keeps a single ``SynapseInterpreter`` so variables persist across
input lines (``x = 5`` then ``x * 2`` -> ``10``).
"""
from __future__ import annotations

import sys

from synapse_lang import __version__
from synapse_lang.synapse_interpreter import SynapseInterpreter

_BANNER = "Synapse {ver} REPL  -  .help for commands, .exit to quit"
_HELP = "  .help    show this help\n  .vars    list variables\n  .reset   clear interpreter state\n  .exit    quit"


class REPL:
    """A line-oriented read-eval-print loop over a persistent interpreter."""

    def __init__(self, sandbox: bool = True):
        # `sandbox` is accepted for parity with the CLI; the interpreter runs
        # in-process either way. Kept so callers (cli, __init__.main) have a
        # stable signature.
        self.sandbox = sandbox
        self.interpreter = SynapseInterpreter()

    def run(self) -> int:
        print(_BANNER.format(ver=__version__))
        while True:
            try:
                line = input("synapse> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            stripped = line.strip()
            if not stripped:
                continue
            if stripped in (".exit", ".quit"):
                break
            if stripped == ".help":
                print(_HELP)
                continue
            if stripped == ".vars":
                variables = getattr(self.interpreter, "variables", {})
                if not variables:
                    print("  (no variables)")
                for name, value in variables.items():
                    print(f"  {name} = {value}")
                continue
            if stripped == ".reset":
                self.interpreter = SynapseInterpreter()
                continue
            try:
                result = self.interpreter.execute(line)
                if result is not None:
                    print(result)
            except Exception as exc:  # surface, don't crash the session
                print(f"error: {exc}", file=sys.stderr)
        return 0


def main(argv=None) -> int:
    return REPL().run()


if __name__ == "__main__":
    raise SystemExit(main())
