"""Regression tests for release evidence and fresh wheel verification."""
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("report_verification", ROOT / "scripts/report_verification.py")
reporting = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reporting)


def write_suite(path, *, roadmap=False, isolation=False):
    suite = ET.Element("testsuite", tests="1", errors="0", failures="0")
    ET.SubElement(suite, "testcase", classname="tests.test_core", name="test_core")
    if roadmap:
        for number in range(1, 8):
            case = ET.SubElement(suite, "testcase", classname="tests.test_roadmap", name=f"test_{number}")
            ET.SubElement(case, "skipped", type="pytest.xfail", message=f"docs/release-issues.md#sl-r{number:02d}")
    if isolation:
        for name in (
            "test_isolated_source_and_uncertainty", "test_output_is_bounded",
            "test_memory_limit_terminates_workload", "test_timeout_removes_container",
            "test_os_boundary_denies_writes_network_and_privilege",
        ):
            ET.SubElement(suite, "testcase", classname="tests.test_isolation", name=name)
    suite.set("tests", str(len(suite)))
    ET.ElementTree(suite).write(path)


@pytest.fixture

def evidence(tmp_path, monkeypatch):
    bench = tmp_path / "benchmarks"
    bench.mkdir()
    write_suite(bench / "full-suite.xml", roadmap=True, isolation=True)
    for version in ("3.10", "3.12", "3.13"):
        write_suite(bench / f"linux-results-{version}.xml")
        (bench / f"linux-tests-{version}.txt").write_text(
            "Installed-wheel API, examples, Bell counts, CLI, REPL, and benchmarks passed: 2.4.0\n"
        )
    (bench / "paired-results.json").write_text(json.dumps({
        "comparisons": {"execute_seconds": {}},
        "trials": {"baseline": [{}] * 5, "candidate": [{}] * 5},
    }))
    monkeypatch.setattr(reporting.subprocess, "check_output", lambda *args, **kwargs: "test\n")
    return tmp_path


def test_report_uses_observed_evidence(evidence):
    report = reporting.build_report(evidence)
    assert report["status"] == "passed"
    assert len(report["container_boundary"]["required_tests_passed"]) == 5
    assert len(report["linux_matrix"]) == 3
    assert "Not executed" in report["remote_ci"]
    assert not report["published"]


@pytest.mark.parametrize("xml", [
    "<testsuites/>",
    '<testsuite tests="0" failures="0" errors="0"/>',
    '<testsuite tests="1" failures="1" errors="0"><testcase><failure/></testcase></testsuite>',
    '<testsuite tests="1" failures="0" errors="1"><testcase><error/></testcase></testsuite>',
    '<testsuite tests="1" failures="0" errors="0"><testcase><skipped/></testcase></testsuite>',
])
def test_report_rejects_invalid_test_evidence(tmp_path, xml):
    path = tmp_path / "suite.xml"
    path.write_text(xml)
    with pytest.raises(ValueError):
        reporting.read_suite(path)


def test_report_requires_actual_isolation_tests(evidence):
    write_suite(evidence / "benchmarks/full-suite.xml", roadmap=True)
    with pytest.raises(ValueError, match="Docker isolation"):
        reporting.build_report(evidence)


def test_report_rejects_failed_linux_even_with_smoke_success(evidence):
    path = evidence / "benchmarks/linux-results-3.12.xml"
    tree = ET.parse(path)
    tree.getroot().set("failures", "1")
    tree.write(path)
    with pytest.raises(ValueError, match="Failed tests"):
        reporting.build_report(evidence)


def test_report_requires_linux_smoke(evidence):
    (evidence / "benchmarks/linux-tests-3.10.txt").write_text("test suite passed\n")
    with pytest.raises(ValueError, match="installed-wheel evidence"):
        reporting.build_report(evidence)


def test_report_requires_benchmark_trials(evidence):
    (evidence / "benchmarks/paired-results.json").write_text('{"comparisons": {}}')
    with pytest.raises(ValueError, match="Five paired"):
        reporting.build_report(evidence)


def test_failed_report_overwrites_previous_success(evidence, monkeypatch):
    monkeypatch.setattr(reporting, "__file__", str(evidence / "scripts/report_verification.py"))
    path = evidence / "benchmarks/verification.json"
    path.write_text('{"status": "passed"}')
    write_suite(evidence / "benchmarks/full-suite.xml")
    assert reporting.main() == 1
    assert json.loads(path.read_text())["status"] == "failed"


def test_unsupported_skip_is_not_called_optional(evidence):
    path = evidence / "benchmarks/full-suite.xml"
    tree = ET.parse(path)
    case = ET.SubElement(tree.getroot(), "testcase", classname="tests.test_legacy", name="test_feature")
    ET.SubElement(case, "skipped", message="Feature not implemented")
    tree.write(path)
    report = reporting.build_report(evidence)
    assert "optional_skips" not in report
    assert report["skipped_tests"][0]["reason"] == "Feature not implemented"


def test_matrix_and_wheel_scripts_have_no_release_version_literal():
    for name in ("scripts/verify_installed.py", "isolation/Dockerfile", "isolation/Matrix.Dockerfile"):
        assert "2.4.0" not in (ROOT / name).read_text()


def test_distribution_metadata_has_no_placeholder_commands():
    for name in ("pyproject.toml", "setup.py"):
        assert ":placeholder" not in (ROOT / name).read_text()


def test_companion_gate_runs_installed_regressions_and_entry_points():
    source = (ROOT / "scripts/verify_trinity_installed.py").read_text()
    assert "test_trinity_implementation.py" in source
    assert "entry.load()" in source
    assert 'python, "-I", "-m", "pytest"' in source
