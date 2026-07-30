"""Tests for the release artifact builder."""

import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

COMPONENT = Path("custom_components/stiebel_eltron_isg")
REPOSITORY = Path(__file__).parent.parent
SCRIPT = REPOSITORY / "scripts" / "build_release.py"


def test_release_artifact_contains_only_tracked_component_files(tmp_path: Path) -> None:
    """The ZIP has the HACS root layout and the requested manifest version."""
    output = tmp_path / "stiebel_eltron_isg.zip"
    manifest_path = REPOSITORY / COMPONENT / "manifest.json"
    working_tree_manifest = manifest_path.read_bytes()

    result = subprocess.run(
        [sys.executable, SCRIPT, "2099.1-test", output],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert manifest_path.read_bytes() == working_tree_manifest

    tracked = subprocess.run(
        ["git", "ls-files", "--", COMPONENT],
        cwd=REPOSITORY,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.splitlines()
    expected_names = {str(Path(path).relative_to(COMPONENT)) for path in tracked}

    with ZipFile(output) as archive:
        assert set(archive.namelist()) == expected_names
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["version"] == "2099.1-test"
        for name in archive.namelist():
            if name.endswith(".json"):
                json.loads(archive.read(name))


def test_release_artifact_is_reproducible(tmp_path: Path) -> None:
    """Identical source and version inputs produce byte-identical ZIP files."""
    outputs = [tmp_path / "first.zip", tmp_path / "second.zip"]

    for output in outputs:
        subprocess.run(
            [sys.executable, SCRIPT, "2099.1-test", output],
            cwd=REPOSITORY,
            capture_output=True,
            text=True,
            check=True,
        )

    assert outputs[0].read_bytes() == outputs[1].read_bytes()


def test_release_artifact_rejects_an_invalid_version(tmp_path: Path) -> None:
    """A path-like or otherwise invalid tag can never reach manifest.json."""
    output = tmp_path / "stiebel_eltron_isg.zip"

    result = subprocess.run(
        [sys.executable, SCRIPT, "release/latest", output],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "invalid release version" in result.stderr
    assert not output.exists()
