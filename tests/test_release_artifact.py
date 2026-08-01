"""Tests for the release artifact builder."""

import json
from pathlib import Path
import subprocess
import sys
import warnings
from zipfile import ZipFile, ZipInfo

import pytest

from scripts import build_release as release_builder

COMPONENT = Path("custom_components/stiebel_eltron_isg")
REPOSITORY = Path(__file__).parent.parent
SCRIPT = REPOSITORY / "scripts" / "build_release.py"


def _minimal_repository(path: Path) -> Path:
    """Create a Git repository carrying the minimum releasable component."""
    repository = path / "repository"
    component = repository / COMPONENT
    component.mkdir(parents=True)
    (component / "__init__.py").write_text("", encoding="utf-8")
    (component / "manifest.json").write_text(
        '{"domain": "stiebel_eltron_isg", "version": "source"}\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(["git", "add", str(COMPONENT)], cwd=repository, check=True)
    return repository


def _write_archive(path: Path, entries: list[tuple[str, bytes]]) -> None:
    """Write the supplied entries, retaining duplicates for negative tests."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Duplicate name:")
        with ZipFile(path, mode="w") as archive:
            for name, data in entries:
                archive.writestr(ZipInfo(name), data)


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


@pytest.mark.parametrize(
    "version",
    [
        "2026.7",
        "2026.7.3",
        "2026.7-beta4",
        "V0.12.0",
        "2026.8.0b1",
        "v2026.8.0-rc1",
    ],
)
def test_release_artifact_accepts_historical_and_prerelease_tags(
    tmp_path: Path, version: str
) -> None:
    """Historical and expected prerelease tag formats remain releasable."""
    repository = _minimal_repository(tmp_path)
    output = tmp_path / f"{version}.zip"

    release_builder.build_release(repository, version, output)

    with ZipFile(output) as archive:
        assert json.loads(archive.read("manifest.json"))["version"] == version


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


def test_untracked_component_files_are_excluded(tmp_path: Path) -> None:
    """Only Git's index decides which component files enter the artifact."""
    repository = _minimal_repository(tmp_path)
    component = repository / COMPONENT
    (component / "untracked.txt").write_text("do not ship", encoding="utf-8")
    output = tmp_path / "release.zip"

    release_builder.build_release(repository, "2099.1-test", output)

    with ZipFile(output) as archive:
        assert set(archive.namelist()) == {"__init__.py", "manifest.json"}


def test_tracked_symlinks_are_rejected(tmp_path: Path) -> None:
    """A tracked link cannot copy bytes from outside the component into a ZIP."""
    repository = _minimal_repository(tmp_path)
    target = repository / "secret.txt"
    target.write_text("outside component", encoding="utf-8")
    link = repository / COMPONENT / "linked.txt"
    link.symlink_to(target)
    subprocess.run(["git", "add", str(link)], cwd=repository, check=True)

    with pytest.raises(release_builder.ArtifactError, match="is a symlink"):
        release_builder.build_release(
            repository, "2099.1-test", tmp_path / "release.zip"
        )


def test_generated_tracked_file_is_rejected_end_to_end(tmp_path: Path) -> None:
    """The public builder rejects generated files even when they are tracked."""
    repository = _minimal_repository(tmp_path)
    generated = repository / COMPONENT / "__pycache__" / "module.pyc"
    generated.parent.mkdir()
    generated.write_bytes(b"generated")
    subprocess.run(["git", "add", "-f", str(generated)], cwd=repository, check=True)

    with pytest.raises(release_builder.ArtifactError, match="generated file"):
        release_builder.build_release(
            repository, "2099.1-test", tmp_path / "release.zip"
        )


def test_non_object_manifest_is_rejected(tmp_path: Path) -> None:
    """The builder reports an invalid manifest shape without a traceback."""
    repository = _minimal_repository(tmp_path)
    manifest = repository / COMPONENT / "manifest.json"
    manifest.write_text("[]\n", encoding="utf-8")

    with pytest.raises(release_builder.ArtifactError, match="JSON object"):
        release_builder.build_release(
            repository, "2099.1-test", tmp_path / "release.zip"
        )


@pytest.mark.parametrize(
    ("entries", "expected_contents", "error"),
    [
        (
            [("__init__.py", b""), ("__init__.py", b"duplicate")],
            {"__init__.py": b""},
            "duplicate paths",
        ),
        (
            [("../escape.py", b"")],
            {"../escape.py": b""},
            "unsafe path",
        ),
        (
            [("__pycache__/module.pyc", b"")],
            {"__pycache__/module.pyc": b""},
            "generated file",
        ),
        (
            [("manifest.json", b"not json")],
            {"manifest.json": b"not json"},
            "invalid JSON",
        ),
        (
            [("__init__.py", b"archive")],
            {"__init__.py": b"source"},
            "content differs from source",
        ),
        (
            [("__init__.py", b"")],
            {"__init__.py": b"", "manifest.json": b"{}"},
            "contents differ from tracked files",
        ),
    ],
    ids=[
        "duplicate",
        "unsafe-path",
        "generated-file",
        "invalid-json",
        "changed-content",
        "missing-file",
    ],
)
def test_archive_verification_rejects_invalid_artifacts(
    tmp_path: Path,
    entries: list[tuple[str, bytes]],
    expected_contents: dict[str, bytes],
    error: str,
) -> None:
    """Every validation branch rejects the malformed archive."""
    archive = tmp_path / "invalid.zip"
    _write_archive(archive, entries)

    with pytest.raises(release_builder.ArtifactError, match=error):
        release_builder._verify_archive(archive, expected_contents, "2099.1-test")


def test_archive_verification_rejects_a_wrong_manifest_version(
    tmp_path: Path,
) -> None:
    """Matching bytes are not enough when the embedded version is wrong."""
    archive = tmp_path / "wrong-version.zip"
    manifest = b'{"version": "2099.2"}'
    _write_archive(archive, [("manifest.json", manifest)])

    with pytest.raises(release_builder.ArtifactError, match="version does not match"):
        release_builder._verify_archive(
            archive, {"manifest.json": manifest}, "2099.1-test"
        )
