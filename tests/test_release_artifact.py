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


DEFAULT_DEPENDENCIES = ["modbus-connection (>=4,<5)"]


def _library_checkout(path: Path, *dependencies: str) -> Path:
    """Create a Git checkout shaped like the pystiebeleltron repository."""
    checkout = path / "library"
    package = checkout / "pystiebeleltron"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        '__version__ = "9.9.9"\nMODEL = "bundled"\n', encoding="utf-8"
    )
    (package / "wpm.py").write_text("from . import MODEL\n", encoding="utf-8")
    (package / "py.typed").write_text("", encoding="utf-8")
    (checkout / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    (checkout / "pyproject.toml").write_text(
        f'[project]\nname = "pystiebeleltron"\ndynamic = ["version"]\n'
        f"dependencies = {json.dumps(list(dependencies or DEFAULT_DEPENDENCIES))}\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
    subprocess.run(["git", "add", "."], cwd=checkout, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-q",
            "-m",
            "library",
        ],
        cwd=checkout,
        check=True,
    )
    return checkout


def _bundling_repository(path: Path, module: str) -> Path:
    """Create a releasable component that imports the library."""
    repository = _minimal_repository(path)
    component = repository / COMPONENT
    (component / "manifest.json").write_text(
        json.dumps({
            "domain": "stiebel_eltron_isg",
            "requirements": ["pystiebeleltron>=0.8.0,<0.9.0"],
            "version": "source",
        }),
        encoding="utf-8",
    )
    (component / "coordinator.py").write_text(module, encoding="utf-8")
    subprocess.run(["git", "add", str(COMPONENT)], cwd=repository, check=True)
    return repository


def _bundle(checkout: Path) -> release_builder.LibraryBundle:
    return release_builder.LibraryBundle(checkout, "owner/library", "feature")


def test_bundled_release_vendors_the_library(tmp_path: Path) -> None:
    """A beta ZIP runs on its own library copy, not on the PyPI release."""
    repository = _bundling_repository(
        tmp_path,
        "from pystiebeleltron import MODEL\nfrom pystiebeleltron.wpm import MODEL as WPM\n",
    )
    checkout = _library_checkout(tmp_path)
    output = tmp_path / "beta.zip"

    release_builder.build_release(repository, "2099.1-beta1", output, _bundle(checkout))

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=checkout,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()
    with ZipFile(output) as archive:
        assert set(archive.namelist()) == {
            "__init__.py",
            "coordinator.py",
            "manifest.json",
            "_vendor/__init__.py",
            "_vendor/pystiebeleltron/__init__.py",
            "_vendor/pystiebeleltron/wpm.py",
            "_vendor/pystiebeleltron/py.typed",
            "_vendor/pystiebeleltron/LICENSE",
        }
        assert archive.read("coordinator.py").decode() == (
            "from ._vendor.pystiebeleltron import MODEL\n"
            "from ._vendor.pystiebeleltron.wpm import MODEL as WPM\n"
        )
        manifest = json.loads(archive.read("manifest.json"))
        archive.extractall(tmp_path / "extracted" / "beta_component")

    assert manifest["requirements"] == []
    assert manifest["bundled_library"] == {
        "name": "pystiebeleltron",
        "version": "9.9.9",
        "repository": "owner/library",
        "ref": "feature",
        "commit": commit,
        "modbus_connection": ">=4,<5",
    }

    sys.path.insert(0, str(tmp_path / "extracted"))
    try:
        from beta_component import coordinator  # noqa: PLC0415

        assert (coordinator.MODEL, coordinator.WPM) == ("bundled", "bundled")
    finally:
        sys.path.remove(str(tmp_path / "extracted"))
        for name in [name for name in sys.modules if name.startswith("beta_component")]:
            del sys.modules[name]


def test_bundled_library_refuses_an_incompatible_modbus_backend(
    tmp_path: Path,
) -> None:
    """A beta on an older Home Assistant fails with an explanation."""
    repository = _bundling_repository(tmp_path, "from pystiebeleltron import MODEL\n")
    checkout = _library_checkout(tmp_path, "modbus-connection (>=999)")
    output = tmp_path / "beta.zip"
    release_builder.build_release(repository, "2099.1-beta1", output, _bundle(checkout))
    with ZipFile(output) as archive:
        archive.extractall(tmp_path / "extracted" / "old_ha_component")

    sys.path.insert(0, str(tmp_path / "extracted"))
    try:
        with pytest.raises(ImportError, match=r"needs modbus-connection>=999"):
            __import__("old_ha_component.coordinator")
    finally:
        sys.path.remove(str(tmp_path / "extracted"))
        for name in [
            name for name in sys.modules if name.startswith("old_ha_component")
        ]:
            del sys.modules[name]


@pytest.mark.parametrize(
    ("module", "dependency", "error"),
    [
        ("import pystiebeleltron\n", None, "cannot redirect"),
        (
            "from pystiebeleltron import (\n    MODEL,\n)\nimport pystiebeleltron.wpm\n",
            None,
            "cannot redirect",
        ),
        ("", ("modbus-connection (>=4,<5)", "requests"), "does not provide"),
        (
            "",
            ("modbus-connection>=4; python_version < '4'",),
            "unsupported library dependency",
        ),
    ],
    ids=["plain-import", "submodule-import", "extra-dependency", "marker"],
)
def test_bundling_rejects_what_it_cannot_ship_safely(
    tmp_path: Path, module: str, dependency: tuple[str, ...] | None, error: str
) -> None:
    """Unrewritable imports and new dependencies stop the beta build."""
    repository = _bundling_repository(tmp_path, module)
    checkout = (
        _library_checkout(tmp_path)
        if dependency is None
        else _library_checkout(tmp_path, *dependency)
    )

    with pytest.raises(release_builder.ArtifactError, match=error):
        release_builder.build_release(
            repository, "2099.1-beta1", tmp_path / "beta.zip", _bundle(checkout)
        )


def test_bundling_requires_the_library_license(tmp_path: Path) -> None:
    """The MIT license travels with every bundled copy."""
    repository = _bundling_repository(tmp_path, "")
    checkout = _library_checkout(tmp_path)
    (checkout / "LICENSE").unlink()

    with pytest.raises(release_builder.ArtifactError, match="LICENSE is missing"):
        release_builder.build_release(
            repository, "2099.1-beta1", tmp_path / "beta.zip", _bundle(checkout)
        )


def test_bundling_requires_one_library_requirement(tmp_path: Path) -> None:
    """The beta manifest must drop exactly the requirement it replaces."""
    repository = _minimal_repository(tmp_path)

    with pytest.raises(release_builder.ArtifactError, match="exactly once"):
        release_builder.build_release(
            repository,
            "2099.1-beta1",
            tmp_path / "beta.zip",
            _bundle(_library_checkout(tmp_path)),
        )


def test_release_cli_bundles_the_library(tmp_path: Path) -> None:
    """The workflow's command line reaches the bundling path."""
    output = tmp_path / "beta.zip"
    checkout = _library_checkout(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "2099.1-beta1",
            output,
            "--bundle-library",
            checkout,
            "--library-repository",
            "owner/library",
            "--library-ref",
            "feature",
        ],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    with ZipFile(output) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        coordinator = archive.read("coordinator.py").decode()
    assert "pystiebeleltron" not in {
        requirement.split(">")[0] for requirement in manifest["requirements"]
    }
    assert manifest["bundled_library"]["ref"] == "feature"
    assert "from ._vendor.pystiebeleltron import" in coordinator
    assert "\nfrom pystiebeleltron" not in coordinator


def test_bundling_rejects_a_symlinked_license(tmp_path: Path) -> None:
    """A license link cannot copy files from outside the checkout into a ZIP."""
    repository = _bundling_repository(tmp_path, "")
    checkout = _library_checkout(tmp_path)
    secret = tmp_path / "git-config"
    secret.write_text("token", encoding="utf-8")
    (checkout / "LICENSE").unlink()
    (checkout / "LICENSE").symlink_to(secret)

    with pytest.raises(release_builder.ArtifactError, match="LICENSE is a symlink"):
        release_builder.build_release(
            repository, "2099.1-beta1", tmp_path / "beta.zip", _bundle(checkout)
        )


def test_bundling_rejects_absolute_self_imports_in_the_library(
    tmp_path: Path,
) -> None:
    """A library module must not reach the installed copy by its top-level name."""
    repository = _bundling_repository(tmp_path, "")
    checkout = _library_checkout(tmp_path)
    (checkout / "pystiebeleltron" / "wpm.py").write_text(
        "from pystiebeleltron import MODEL\n", encoding="utf-8"
    )

    with pytest.raises(release_builder.ArtifactError, match="wpm.py:1"):
        release_builder.build_release(
            repository, "2099.1-beta1", tmp_path / "beta.zip", _bundle(checkout)
        )


def test_bundling_rejects_dynamic_dependencies(tmp_path: Path) -> None:
    """Dependencies the build cannot read cannot be checked against HA."""
    repository = _bundling_repository(tmp_path, "")
    checkout = _library_checkout(tmp_path)
    (checkout / "pyproject.toml").write_text(
        '[project]\nname = "pystiebeleltron"\ndynamic = ["version", "dependencies"]\n',
        encoding="utf-8",
    )

    with pytest.raises(release_builder.ArtifactError, match="dynamically"):
        release_builder.build_release(
            repository, "2099.1-beta1", tmp_path / "beta.zip", _bundle(checkout)
        )
