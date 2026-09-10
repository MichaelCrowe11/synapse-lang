"""Fixed JSON entry point inside the isolated runtime image."""
import contextlib
import io
import json
import sys

from synapse_lang import execute

LIMIT = 65536


class BoundedOutput(io.StringIO):
    def write(self, text):
        if self.tell() + len(text) > LIMIT:
            raise ValueError("Program output limit exceeded")
        return super().write(text)


def main():
    try:
        raw = sys.stdin.buffer.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError("Request exceeds 64 KiB")
        request = json.loads(raw)
        if set(request) != {"source"} or not isinstance(request["source"], str):
            raise ValueError("Request must contain only a source string")
        output = BoundedOutput()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = execute(request["source"])
        if type(result).__module__ == "synapse_lang.uncertainty":
            result = {"nominal": result.nominal, "uncertainty": result.uncertainty}
        reply = json.dumps({"result": result, "stdout": output.getvalue()}, allow_nan=False)
        if len(reply.encode()) > 1024 * 1024:
            raise ValueError("Result exceeds 1 MiB")
        print(reply)
        return 0
    except Exception as exc:
        print(json.dumps({"error": f"{type(exc).__name__}: {str(exc)[:512]}"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
