"""Report observed verification, with explicit failures and no remote CI claims."""
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def read_suite(path):
    """Require nonempty, successful JUnit evidence before summarizing it."""
    tree = ET.parse(path).getroot()
    suites = [tree] if tree.tag == "testsuite" else tree.findall("testsuite")
    if not suites or sum(int(suite.get("tests", "0")) for suite in suites) == 0:
        raise ValueError(f"No tests recorded in {path.name}")
    if any(int(suite.get(key, "0")) for suite in suites for key in ("failures", "errors")):
        raise ValueError(f"Failed tests recorded in {path.name}")
    cases = [case for suite in suites for case in suite.findall("testcase")]
    if not any(case.find("skipped") is None for case in cases):
        raise ValueError(f"No executed tests recorded in {path.name}")
    return suites, cases


def build_report(root):
    suites, cases = read_suite(root / "benchmarks/full-suite.xml")
    roadmap = []
    skipped_tests = []
    for case in cases:
        skipped = case.find("skipped")
        if skipped is not None:
            entry = {
                "test": case.get("classname", "") + "." + case.get("name", ""),
                "reason": skipped.get("message"),
            }
            (roadmap if skipped.get("type") == "pytest.xfail" else skipped_tests).append(entry)
    expected_issues = {f"sl-r{number:02d}" for number in range(1, 8)}
    observed_issues = {
        issue for issue in expected_issues
        if any(issue in str(entry["reason"]).lower() for entry in roadmap)
    }
    if len(roadmap) != 7 or observed_issues != expected_issues:
        raise ValueError("Strict roadmap expectations changed; review docs/release-issues.md")
    required_isolation = {
        "test_isolated_source_and_uncertainty", "test_output_is_bounded",
        "test_memory_limit_terminates_workload", "test_timeout_removes_container",
        "test_os_boundary_denies_writes_network_and_privilege",
    }
    passed_isolation = {
        case.get("name") for case in cases
        if case.get("classname") == "tests.test_isolation"
        and not any(case.find(tag) is not None for tag in ("skipped", "failure", "error"))
    }
    if not required_isolation <= passed_isolation:
        raise ValueError("Required Docker isolation tests did not execute successfully")
    linux = {}
    for version in ("3.10", "3.12", "3.13"):
        linux_suites, _ = read_suite(root / f"benchmarks/linux-results-{version}.xml")
        log = (root / f"benchmarks/linux-tests-{version}.txt").read_text()
        if "Installed-wheel API, examples, Bell counts, CLI, REPL, and benchmarks passed:" not in log:
            raise ValueError(f"Linux {version} installed-wheel evidence is missing")
        linux[version] = {"suites": [suite.attrib for suite in linux_suites], "wheel_smoke": True}
    performance = json.loads((root / "benchmarks/paired-results.json").read_text())
    if not performance.get("comparisons") or any(
        len(performance.get("trials", {}).get(name, [])) != 5
        for name in ("baseline", "candidate")
    ):
        raise ValueError("Five paired benchmark trials are required")
    return {
        "status": "passed",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "branch": subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=root, text=True,
        ).strip(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "working_tree_dirty": bool(subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root, text=True,
        ).strip()),
        "local_full_suite": [suite.attrib for suite in suites],
        "strict_roadmap_expectations": roadmap,
        "skipped_tests": skipped_tests,
        "skip_note": "Skips include unsupported features and missing integrations; none count as passing features.",
        "linux_matrix": linux,
        "local_platform": f"{platform.system()} {platform.machine()}, Python {platform.python_version()}",
        "container_boundary": {"required_tests_passed": sorted(required_isolation)},
        "remote_ci": "Not executed by this workflow; OS-specific CI runners remain required",
        "published": False,
        "performance_report": "benchmarks/paired-results.json",
    }


def main():
    root = Path(__file__).resolve().parents[1]
    try:
        report = build_report(root)
    except (OSError, ValueError, ET.ParseError, subprocess.CalledProcessError) as error:
        report = {"status": "failed", "error": str(error), "published": False}
        (root / "benchmarks/verification.json").write_text(json.dumps(report, indent=2) + "\n")
        print(f"Verification report failed: {error}", file=sys.stderr)
        return 1
    (root / "benchmarks/verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print("Observed local verification recorded; remote CI remains unverified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
