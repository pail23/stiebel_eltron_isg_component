"""Guards on the integration manifest.

``manifest.json`` declares what Home Assistant installs at runtime. The test
environment installs whatever ``pyproject.toml`` asks for. When the version the
tests run against does not satisfy the manifest requirement, the whole suite can
pass while the released integration is broken, which is how the WPM
power-consumption sensors shipped against an API the pinned library did not have.

The invariant asserted here is deliberately the weaker "what CI runs must be
installable per the manifest" rather than "the two files agree exactly", so that
a legitimate loosening of the manifest, for example to ``>=``, does not fail.
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
    """Every manifest requirement must be met by the environment CI tests on."""
    requirements = json.loads(_MANIFEST.read_text())["requirements"]

    assert requirements, "manifest declares no requirements"

    for entry in requirements:
        requirement = Requirement(entry)

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
