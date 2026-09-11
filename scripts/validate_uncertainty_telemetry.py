#!/usr/bin/env python3
"""Run the bounded uncertainty-propagation validation on a telemetry dataset kept outside the repository.

    validate_uncertainty_telemetry.py --sqlite /private/path/readings.sqlite --node NODE \
        --provenance "where the rows came from" --fixture-status synthetic|real --out /private/report/dir

    validate_uncertainty_telemetry.py --csv /private/path/rows.csv ...   (columns: ts,temperature_c,humidity_pct,co2_ppm)

Writes report.json and report.md into --out. The acceptance criteria and input assumptions live in
synapse_lang.telemetry_validation and are not adjustable from the command line.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from synapse_lang import telemetry_validation as tv  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--sqlite", help="SQLite file with a readings table")
    src.add_argument("--csv", help="CSV with ts,temperature_c,humidity_pct,co2_ppm")
    ap.add_argument("--node", help="restrict a SQLite readings table to one node id")
    ap.add_argument("--schema", default="auto", choices=["auto", "relay", "rig"])
    ap.add_argument("--rows", type=int, default=128, help="deterministically selected rows (evenly spaced in time)")
    ap.add_argument("--draws", type=int, default=100_000, help="Monte Carlo draws per row")
    ap.add_argument("--seed", type=int, default=20260910)
    ap.add_argument("--provenance", required=True, help="free-text statement of where the rows came from")
    ap.add_argument("--fixture-status", required=True, choices=["synthetic", "real"])
    ap.add_argument("--out", required=True, help="directory for report.json and report.md (keep it outside the repository)")
    a = ap.parse_args(argv)

    rows = tv.load_csv(a.csv) if a.csv else tv.load_sqlite(a.sqlite, node=a.node, schema=a.schema)
    if not rows:
        print("no aligned rows found", file=sys.stderr)
        return 2
    report = tv.run(rows, draws=a.draws, seed=a.seed, provenance=a.provenance, fixture_status=a.fixture_status, sample=a.rows)
    report["recorded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    (out / "report.md").write_text(tv.to_markdown(report))
    print(tv.to_markdown(report))
    print(f"written: {out / 'report.json'}")
    return 0 if all(report["verdicts"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
