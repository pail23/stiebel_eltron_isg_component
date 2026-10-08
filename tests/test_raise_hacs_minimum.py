"""Tests for raising the hacs.json minimum of bundled betas."""

import json
from pathlib import Path

import pytest

from scripts.raise_hacs_minimum import raise_minimum


@pytest.mark.parametrize(
    ("current", "expected", "changed"),
    [
        ("2026.9.0", "2026.10.0", True),
        ("2026.10.0", "2026.10.0", False),
        ("2026.11.0", "2026.11.0", False),
        (None, "2026.10.0", True),
    ],
    ids=["older", "same", "newer", "missing"],
)
def test_minimum_is_raised_but_never_lowered(
    tmp_path: Path, current: str | None, expected: str, changed: bool
) -> None:
    """A branch that already requires a newer Home Assistant keeps it."""
    path = tmp_path / "hacs.json"
    hacs = {"name": "Stiebel Eltron ISG", "zip_release": True}
    if current is not None:
        hacs["homeassistant"] = current
    path.write_text(json.dumps(hacs), encoding="utf-8")

    assert raise_minimum(path, "2026.10.0") is changed
    result = json.loads(path.read_text(encoding="utf-8"))
    assert result["homeassistant"] == expected
    assert result["name"] == "Stiebel Eltron ISG"
