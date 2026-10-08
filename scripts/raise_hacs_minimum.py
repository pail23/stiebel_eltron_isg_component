#!/usr/bin/env python3
"""Raise the minimum Home Assistant version in hacs.json, never lower it.

HACS reads hacs.json at the release tag, so a bundled beta can require a
newer Home Assistant than the stable releases.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def raise_minimum(path: Path, minimum: str) -> bool:
    """Raise the minimum in place and return whether the file changed."""
    hacs = json.loads(path.read_text(encoding="utf-8"))
    if _key(hacs.get("homeassistant", "0")) >= _key(minimum):
        return False
    hacs["homeassistant"] = minimum
    path.write_text(json.dumps(hacs, indent=4) + "\n", encoding="utf-8")
    return True


def main() -> None:
    """Parse CLI arguments and update hacs.json."""
    parser = argparse.ArgumentParser()
    parser.add_argument("minimum", help="Home Assistant version, e.g. 2026.10.0")
    parser.add_argument("--path", type=Path, default=Path("hacs.json"))
    args = parser.parse_args()
    raise_minimum(args.path, args.minimum)


if __name__ == "__main__":
    main()
