"""Tests for GitHub Actions workflow safety."""

from pathlib import Path
import re

WORKFLOWS = Path(__file__).parent.parent / ".github" / "workflows"
REMOTE_ACTION = re.compile(
    r"""^\s*uses:\s*["']?(?P<action>[^@\s"']+)@(?P<ref>[^#\s"']+)["']?"""
    r"""(?:\s+#\s*(?P<label>\S.*))?\s*$""",
    re.MULTILINE,
)
COMMIT_SHA = re.compile(r"[0-9a-f]{40}")


def test_remote_actions_are_pinned_to_commit_shas() -> None:
    """A moved or compromised upstream tag must not change CI execution."""
    unpinned = []
    unlabeled = []

    for workflow in sorted(WORKFLOWS.glob("*.y*ml")):
        for match in REMOTE_ACTION.finditer(workflow.read_text(encoding="utf-8")):
            action = (
                f"{workflow.relative_to(WORKFLOWS.parent.parent)}: "
                f"{match['action']}@{match['ref']}"
            )
            if not COMMIT_SHA.fullmatch(match["ref"]):
                unpinned.append(action)
            if match["label"] is None:
                unlabeled.append(action)

    assert not unpinned, "Unpinned remote actions:\n" + "\n".join(unpinned)
    assert not unlabeled, "Unlabeled remote actions:\n" + "\n".join(unlabeled)
