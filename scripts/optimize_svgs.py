"""Batch optimize SVG assets using optional external 'svgo' CLI if present.
Falls back to simple whitespace trimming.
Run: python scripts/optimize_svgs.py [--check]
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRANDING = ROOT / "branding"

SVG_WHITESPACE_RE = re.compile(rb">\s+<")

def svgo_available() -> bool:
    return shutil.which("svgo") is not None

def optimize_with_svgo(path: pathlib.Path) -> bool:
    try:
        subprocess.run([
            "svgo", str(path), "--multipass", "--quiet"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def light_trim(data: bytes) -> bytes:
    # remove extra inter-tag spaces
    return SVG_WHITESPACE_RE.sub(b"><", data).strip()

def process(svg: pathlib.Path, check: bool=False) -> tuple[bool,str]:
    before = svg.read_bytes()
    if svgo_available() and not check:
        success = optimize_with_svgo(svg)
        if not success:  # fallback
            after = light_trim(before)
            if after != before and not check:
                svg.write_bytes(after)
            return success, "svgo-fallback" if after!=before else "no-change"
        return True, "svgo"
    else:
        after = light_trim(before)
        changed = after != before
        if changed and not check:
            svg.write_bytes(after)
        return changed, "trim" if changed else "no-change"


def main(argv):
    check = "--check" in argv
    svgs = list(BRANDING.glob("*.svg"))
    if not svgs:
        print("No SVGs found in branding/")
        return 0
    total_saved = 0
    for s in svgs:
        orig_size = s.stat().st_size
        changed, mode = process(s, check=check)
        new_size = s.stat().st_size
        delta = orig_size - new_size
        if changed:
            total_saved += max(delta,0)
        print(f"{s.name}: {mode} (saved {delta} bytes)")
    print(f"Total saved: {total_saved} bytes")
    if check and total_saved>0:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
