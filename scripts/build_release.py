#!/usr/bin/env python3
"""Build and verify the HACS release ZIP from tracked integration files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

COMPONENT_PATH = Path("custom_components/stiebel_eltron_isg")
REQUIRED_FILES = {"__init__.py", "manifest.json"}
VERSION_PATTERN = re.compile(r"^\d{4}\.\d+(?:\.\d+)?(?:-[A-Za-z0-9][A-Za-z0-9.-]*)?$")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


class ArtifactError(ValueError):
    """The release artifact contract was not met."""


def _tracked_component_files(repository: Path) -> list[Path]:
    """Return tracked component files relative to the component directory."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", COMPONENT_PATH],
            cwd=repository,
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as err:
        message = os.fsdecode(err.stderr).strip()
        raise ArtifactError(
            f"could not list tracked component files: {message}"
        ) from err

    prefix = f"{COMPONENT_PATH.as_posix()}/"
    files = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = os.fsdecode(raw_path)
        if not path.startswith(prefix):
            raise ArtifactError(f"tracked path is outside the component: {path}")
        relative = Path(path.removeprefix(prefix))
        if relative.is_absolute() or ".." in relative.parts:
            raise ArtifactError(f"unsafe component path: {relative}")
        source = repository / COMPONENT_PATH / relative
        if source.is_symlink():
            raise ArtifactError(f"tracked component file is a symlink: {relative}")
        if not source.is_file():
            raise ArtifactError(f"tracked component file is missing: {relative}")
        files.append(relative)

    names = {path.as_posix() for path in files}
    if missing := REQUIRED_FILES - names:
        raise ArtifactError(f"required component files are missing: {sorted(missing)}")
    return sorted(files, key=lambda path: path.as_posix())


def _manifest_with_version(path: Path, version: str) -> bytes:
    """Return manifest JSON carrying the release version."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ArtifactError(f"invalid JSON in manifest.json: {err}") from err
    manifest["version"] = version
    return f"{json.dumps(manifest, indent=2)}\n".encode()


def _zip_info(name: str) -> ZipInfo:
    """Return reproducible metadata for one regular archive file."""
    info = ZipInfo(name, date_time=ZIP_TIMESTAMP)
    info.create_system = 3
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    return info


def _expected_contents(
    component: Path, relative_files: list[Path], version: str
) -> dict[str, bytes]:
    """Return the exact bytes each tracked source must have in the archive."""
    return {
        relative.as_posix(): (
            _manifest_with_version(component / relative, version)
            if relative.as_posix() == "manifest.json"
            else (component / relative).read_bytes()
        )
        for relative in relative_files
    }


def _verify_archive(
    path: Path, expected_contents: dict[str, bytes], version: str
) -> None:
    """Verify archive layout, contents, JSON files and manifest version."""
    expected_names = set(expected_contents)
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ArtifactError("archive contains duplicate paths")
        if set(names) != expected_names:
            missing = sorted(expected_names - set(names))
            extra = sorted(set(names) - expected_names)
            raise ArtifactError(
                f"archive contents differ from tracked files: missing={missing}, extra={extra}"
            )

        for name in names:
            pure_path = PurePosixPath(name)
            if pure_path.is_absolute() or ".." in pure_path.parts:
                raise ArtifactError(f"archive contains unsafe path: {name}")
            if "__pycache__" in pure_path.parts or pure_path.suffix in {
                ".pyc",
                ".zip",
            }:
                raise ArtifactError(f"archive contains generated file: {name}")
            data = archive.read(name)
            if data != expected_contents[name]:
                raise ArtifactError(f"archive content differs from source: {name}")
            if pure_path.suffix == ".json":
                try:
                    json.loads(data)
                except json.JSONDecodeError as err:
                    raise ArtifactError(
                        f"archive contains invalid JSON: {name}"
                    ) from err

        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("version") != version:
            raise ArtifactError(
                "manifest version does not match the requested release version"
            )


def build_release(repository: Path, version: str, output: Path) -> None:
    """Build and atomically publish one verified release artifact."""
    if not VERSION_PATTERN.fullmatch(version):
        raise ArtifactError(f"invalid release version: {version!r}")

    repository = repository.resolve()
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    component = repository / COMPONENT_PATH
    relative_files = _tracked_component_files(repository)
    expected_contents = _expected_contents(component, relative_files, version)

    with tempfile.NamedTemporaryFile(
        dir=output.parent,
        prefix=f".{output.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)

    try:
        with ZipFile(temporary_path, mode="w") as archive:
            for name, data in expected_contents.items():
                archive.writestr(_zip_info(name), data)

        _verify_archive(temporary_path, expected_contents, version)
        os.replace(temporary_path, output)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> None:
    """Parse CLI arguments and build the artifact."""
    parser = argparse.ArgumentParser()
    parser.add_argument("version", help="GitHub release tag/version")
    parser.add_argument("output", type=Path, help="output ZIP path")
    args = parser.parse_args()

    try:
        build_release(Path.cwd(), args.version, args.output)
    except (ArtifactError, OSError, subprocess.SubprocessError) as err:
        parser.error(str(err))

    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    sys.stdout.write(f"Built {args.output} (sha256: {digest})\n")


if __name__ == "__main__":
    main()
