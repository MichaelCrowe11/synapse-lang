"""Console entry point for the ``synapse`` command.

Declared as ``synapse = synapse_lang.cli:main`` in ``[project.scripts]`` but
never shipped, so ``synapse`` crashed with ModuleNotFoundError on every install.
Wraps the existing package runtime (``run_file`` / ``execute``) and delegates
the interactive loop to ``synapse_lang.repl``.
"""
from __future__ import annotations

import argparse
import sys

from synapse_lang import __version__, execute, run_file


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="synapse", description="Synapse Language interpreter")
    parser.add_argument("file", nargs="?", help="Synapse source file (.syn) to run")
    parser.add_argument("-c", "--code", help="Run a snippet of Synapse source instead of a file")
    parser.add_argument("--repl", action="store_true", help="Start the interactive REPL")
    parser.add_argument("--no-sandbox", action="store_true", help="Disable the security sandbox")
    parser.add_argument("--version", action="version", version=f"Synapse {__version__}")
    args = parser.parse_args(argv)

    # No file and no snippet -> interactive REPL.
    if args.repl or (not args.file and not args.code):
        from synapse_lang.repl import REPL

        return REPL(sandbox=not args.no_sandbox).run()

    try:
        if args.code:
            result = execute(args.code, sandbox=not args.no_sandbox)
        else:
            result = run_file(args.file, sandbox=not args.no_sandbox)
        if result is not None:
            print(result)
        return 0
    except FileNotFoundError:
        print(f"synapse: file not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"synapse: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
