"""Tests for the per-module coverage gate."""

import importlib.util
import json
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).parents[1] / "scripts" / "check_module_coverage.py"
_SPEC = importlib.util.spec_from_file_location("check_module_coverage", _SCRIPT)
assert _SPEC is not None
assert _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def test_only_integration_modules_not_above_target_are_reported() -> None:
    """External files are ignored and the strict boundary is enforced."""
    report = {
        "files": {
            "custom_components/stiebel_eltron_isg/good.py": {
                "summary": {"percent_covered": 95.01}
            },
            "custom_components/stiebel_eltron_isg/exact.py": {
                "summary": {"percent_covered": 95.0}
            },
            "custom_components/stiebel_eltron_isg/low.py": {
                "summary": {"percent_covered": 94.99}
            },
            "tests/test_example.py": {"summary": {"percent_covered": 0.0}},
        }
    }

    assert _MODULE.modules_failing_target(report, 95) == [
        ("custom_components/stiebel_eltron_isg/exact.py", 95.0),
        ("custom_components/stiebel_eltron_isg/low.py", 94.99),
    ]


def test_empty_integration_match_fails_closed() -> None:
    """A path or report-format change must not turn the gate green."""
    report = {
        "files": {"tests/test_example.py": {"summary": {"percent_covered": 100.0}}}
    }

    with pytest.raises(ValueError, match="contains no files with prefix"):
        _MODULE.modules_failing_target(report, 95)


def test_main_fails_closed_for_missing_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The command exits non-zero and explains an unreadable report."""
    report = tmp_path / "missing.json"
    monkeypatch.setattr(
        _MODULE.sys,
        "argv",
        ["check_module_coverage.py", str(report)],
    )

    assert _MODULE.main() == 1
    assert f"Cannot check module coverage for {report}:" in capsys.readouterr().err


def test_main_accepts_a_readable_report_above_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The command succeeds silently when every integration module passes."""
    report = tmp_path / "coverage.json"
    report.write_text(
        json.dumps({
            "files": {
                "custom_components/stiebel_eltron_isg/good.py": {
                    "summary": {"percent_covered": 95.01}
                }
            }
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        _MODULE.sys,
        "argv",
        ["check_module_coverage.py", str(report)],
    )

    assert _MODULE.main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_main_reports_every_module_not_above_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The command exits non-zero with actionable lines for failing modules."""
    report = tmp_path / "coverage.json"
    report.write_text(
        json.dumps({
            "files": {
                "custom_components/stiebel_eltron_isg/exact.py": {
                    "summary": {"percent_covered": 95.0}
                },
                "custom_components/stiebel_eltron_isg/low.py": {
                    "summary": {"percent_covered": 94.99}
                },
            }
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        _MODULE.sys,
        "argv",
        ["check_module_coverage.py", str(report)],
    )

    assert _MODULE.main() == 1
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        (
            "custom_components/stiebel_eltron_isg/exact.py: 95.00% "
            "(required: more than 95.00%)"
        ),
        (
            "custom_components/stiebel_eltron_isg/low.py: 94.99% "
            "(required: more than 95.00%)"
        ),
    ]
    assert captured.err == ""
