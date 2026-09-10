"""Line REPL. Submit complete statements or complete blocks on one line."""
import argparse
import json

from .cli import evaluate


def main(argv=None):
    parser = argparse.ArgumentParser(description="Local line REPL; :quit exits")
    parser.parse_args(argv)
    interpreter = None
    while True:
        try:
            source = input("qnet(parse-only)> ")
        except (EOFError, KeyboardInterrupt):
            return 0
        if source.strip() == ":quit":
            return 0
        if not source.strip():
            continue
        try:
            print(json.dumps(evaluate(source, interpreter)))
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
