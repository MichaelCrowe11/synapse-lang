"""Local companion command-line interface for trusted source."""
import argparse
import json
import sys
from pathlib import Path

from .qubit_flow_interpreter import QubitFlowInterpreter


def evaluate(source, interpreter=None):
    interpreter = interpreter or QubitFlowInterpreter()
    messages = interpreter.execute(source)
    if any(message.startswith("Error:") for message in messages):
        raise ValueError("; ".join(messages))
    return {"messages": messages, "probabilities": (abs(interpreter.state.amplitudes) ** 2).tolist(),
            "qubit_order": list(interpreter.qubits), "measurements": interpreter.classical_bits}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Qubit Flow statevector execution")
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
