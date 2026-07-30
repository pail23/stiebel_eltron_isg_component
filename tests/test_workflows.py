"""Tests for GitHub Actions workflow safety."""

from pathlib import Path
import re

WORKFLOWS = Path(__file__).parent.parent / ".github" / "workflows"
REMOTE_ACTION = re.compile(
    r"""^\s*uses:\s*["']?(?P<action>[^@\s"']+)@(?P<ref>[^#\s"']+)""",
    re.MULTILINE,
)
COMMIT_SHA = re.compile(r"[0-9a-f]{40}")


def test_remote_actions_are_pinned_to_commit_shas() -> None:
    """A moved or compromised upstream tag must not change CI execution."""
    unpinned = []

    for workflow in sorted(WORKFLOWS.glob("*.y*ml")):
        unpinned.extend(
            f"{workflow.relative_to(WORKFLOWS.parent.parent)}: "
            f"{match['action']}@{match['ref']}"
            for match in REMOTE_ACTION.finditer(workflow.read_text(encoding="utf-8"))
            if not COMMIT_SHA.fullmatch(match["ref"])
        )

    assert not unpinned, "Unpinned remote actions:\n" + "\n".join(unpinned)
