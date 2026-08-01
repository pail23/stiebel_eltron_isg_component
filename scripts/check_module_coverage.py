"""Fail unless every integration module exceeds the coverage target."""

import argparse
import json
from pathlib import Path
import sys

INTEGRATION_PREFIX = "custom_components/stiebel_eltron_isg/"


def modules_failing_target(report: dict, target: float) -> list[tuple[str, float]]:
    """Return integration modules that do not exceed target."""
    modules = sorted(
        (filename, details["summary"]["percent_covered"])
        for filename, details in report["files"].items()
        if filename.startswith(INTEGRATION_PREFIX)
    )
    if not modules:
        raise ValueError(
            f"coverage report contains no files with prefix {INTEGRATION_PREFIX}"
        )
    return [
        (filename, coverage) for filename, coverage in modules if coverage <= target
    ]


def main() -> int:
    """Check a coverage.py JSON report."""
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--target", type=float, default=95)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        failures = modules_failing_target(report, args.target)
    except (OSError, KeyError, TypeError, ValueError) as err:
        print(  # noqa: T201
            f"Cannot check module coverage for {args.report}: {err}",
            file=sys.stderr,
        )
        return 1

    for filename, coverage in failures:
        print(  # noqa: T201
            f"{filename}: {coverage:.2f}% (required: more than {args.target:.2f}%)"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
