"""Local companion command-line interface for trusted source."""
import argparse
import json
import sys
from pathlib import Path

from .lexer import tokenize
from .parser import Parser


def evaluate(source, interpreter=None):
    program = Parser(tokenize(source)).parse()
    return {"mode": "parse-only", "statements": len(program.statements),
            "names": [node.name for node in program.statements]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Quantum Net grammar validation only, not protocol execution")
    parser.add_argument("file", help="Source file or - for stdin")
    args = parser.parse_args(argv)
    try:
        source = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        print(json.dumps(evaluate(source)))
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
