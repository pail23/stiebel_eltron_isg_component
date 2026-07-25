"""Guard against the manifest drifting away from what the tests exercise.

``manifest.json`` declares what Home Assistant installs at runtime, while the
test environment installs whatever ``pyproject.toml`` asks for. When those two
diverge, the suite can pass against an API that a released installation does not
have, which is how the WPM power-consumption sensors shipped reading
``api.energy_data`` fields while the manifest still pinned a library that kept
them on ``api.power_consumption``.

Scope, deliberately narrow: this proves only that the one version present in CI
is admitted by the manifest requirement. It is a drift guard, not a compatibility
proof. With a range such as ``>=0.2.3`` every admitted version would have to be
API-compatible for that to hold, and nothing here checks the other admitted
versions. Guarding a range properly would mean testing its minimum, or asserting
that known-incompatible versions are excluded.
"""

import importlib.metadata
import json
from pathlib import Path

from packaging.requirements import Requirement
import pytest

_MANIFEST = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "stiebel_eltron_isg"
    / "manifest.json"
)


def test_installed_versions_satisfy_manifest_requirements() -> None:
    """Each active requirement is installed, at a version its specifier admits."""
    requirements = json.loads(_MANIFEST.read_text())["requirements"]

    assert requirements, "manifest declares no requirements"

    for entry in requirements:
        requirement = Requirement(entry)

        # A requirement whose environment marker does not apply here is not
        # expected to be installed, so it says nothing about this environment.
        if requirement.marker is not None and not requirement.marker.evaluate():
            continue

        try:
            installed = importlib.metadata.version(requirement.name)
        except importlib.metadata.PackageNotFoundError:
            pytest.fail(
                f"manifest.json requires {entry} but {requirement.name} is not "
                f"installed in the test environment, so nothing here exercises "
                f"the code that depends on it."
            )

        assert requirement.specifier.contains(installed, prereleases=True), (
            f"manifest.json requires {entry} but the tests run against "
            f"{requirement.name}=={installed}. Code relying on the installed "
            f"version would fail only on a real installation, never in CI."
        )
