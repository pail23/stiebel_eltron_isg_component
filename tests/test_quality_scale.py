"""Tests for the custom integration quality-scale evidence."""

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from yaml.nodes import MappingNode, ScalarNode

ROOT = Path(__file__).parent.parent
INTEGRATION_DIR = ROOT / "custom_components" / "stiebel_eltron_isg"
QUALITY_SCALE_FILE = INTEGRATION_DIR / "quality_scale.yaml"
MANIFEST_FILE = INTEGRATION_DIR / "manifest.json"

PINNED_RULES = frozenset({
    "action-exceptions",
    "action-setup",
    "appropriate-polling",
    "async-dependency",
    "brands",
    "common-modules",
    "config-entry-unloading",
    "config-flow",
    "config-flow-test-coverage",
    "dependency-transparency",
    "devices",
    "diagnostics",
    "discovery",
    "discovery-update-info",
    "docs-actions",
    "docs-conditions",
    "docs-configuration-parameters",
    "docs-data-update",
    "docs-examples",
    "docs-high-level-description",
    "docs-installation-instructions",
    "docs-installation-parameters",
    "docs-known-limitations",
    "docs-removal-instructions",
    "docs-supported-devices",
    "docs-supported-functions",
    "docs-triggers",
    "docs-troubleshooting",
    "docs-use-cases",
    "dynamic-devices",
    "entity-category",
    "entity-device-class",
    "entity-disabled-by-default",
    "entity-event-setup",
    "entity-translations",
    "entity-unique-id",
    "entity-unavailable",
    "exception-translations",
    "has-entity-name",
    "icon-translations",
    "inject-websession",
    "integration-owner",
    "log-when-unavailable",
    "parallel-updates",
    "reauthentication-flow",
    "reconfiguration-flow",
    "repair-issues",
    "runtime-data",
    "stale-devices",
    "strict-typing",
    "test-before-configure",
    "test-before-setup",
    "test-coverage",
    "unique-config-entry",
})
VALID_STATUSES = frozenset({"done", "todo", "exempt"})


@pytest.fixture
def raw_quality_scale() -> str:
    """Return the raw custom quality evidence."""
    if not QUALITY_SCALE_FILE.is_file():
        pytest.skip("quality_scale.yaml has not been implemented yet")
    return QUALITY_SCALE_FILE.read_text(encoding="utf-8")


@pytest.fixture
def quality_rules(raw_quality_scale: str) -> dict[str, Any]:
    """Return the parsed rule mapping."""
    document = yaml.safe_load(raw_quality_scale)
    assert set(document) == {"rules"}
    assert isinstance(document["rules"], dict)
    return document["rules"]


def _status(value: Any) -> Any:
    """Return the normalized status for one rule value."""
    return value if isinstance(value, str) else value.get("status")


def _mapping_keys(node: MappingNode) -> list[str]:
    """Return scalar keys from a YAML mapping node."""
    keys: list[str] = []
    for key_node, _ in node.value:
        assert isinstance(key_node, ScalarNode)
        keys.append(key_node.value)
    return keys


def test_quality_scale_file_exists() -> None:
    """Require the repository to publish its custom quality evidence."""
    assert QUALITY_SCALE_FILE.is_file()


def test_quality_scale_tracks_pinned_rule_inventory(
    quality_rules: dict[str, Any],
) -> None:
    """Track every pinned Home Assistant 2026.7.4 rule."""
    assert set(quality_rules) == PINNED_RULES


def test_quality_scale_defines_each_rule_once(raw_quality_scale: str) -> None:
    """Reject duplicate YAML keys that a normal loader would hide."""
    document_node = yaml.compose(raw_quality_scale)
    assert isinstance(document_node, MappingNode)
    assert _mapping_keys(document_node) == ["rules"]

    rules_node = document_node.value[0][1]
    assert isinstance(rules_node, MappingNode)
    rule_keys = _mapping_keys(rules_node)
    assert len(rule_keys) == len(set(rule_keys))


def test_quality_scale_entries_match_custom_schema(
    quality_rules: dict[str, Any],
) -> None:
    """Keep statuses and their supporting rationale fail closed."""
    for rule, value in quality_rules.items():
        if isinstance(value, str):
            assert value == "done", rule
            continue

        assert isinstance(value, dict), rule
        assert set(value) == {"status", "comment"}, rule
        assert value["status"] in VALID_STATUSES, rule
        assert isinstance(value["comment"], str), rule
        assert value["comment"].strip(), rule


def test_completed_documentation_rules_cite_local_evidence(
    quality_rules: dict[str, Any],
) -> None:
    """Point completed documentation rules at a concrete local heading."""
    for rule, value in quality_rules.items():
        if not rule.startswith("docs-") or _status(value) != "done":
            continue

        assert isinstance(value, dict), rule
        comment = value["comment"]
        assert "README.md#" in comment or "info.md#" in comment, rule


def test_quality_scale_is_explicitly_a_custom_self_assessment(
    raw_quality_scale: str,
) -> None:
    """Avoid presenting the checklist as an official Home Assistant tier."""
    assert "custom integration" in raw_quality_scale.lower()
    assert "self-assessment" in raw_quality_scale.lower()
    assert "Home Assistant Core 2026.7.4" in raw_quality_scale


def test_manifest_does_not_claim_an_official_quality_tier() -> None:
    """Keep the custom checklist out of the Home Assistant manifest schema."""
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    assert "quality_scale" not in manifest
