"""Tests for Home Assistant Repairs exposed by the integration."""

from typing import Any

from homeassistant.components.repairs import ConfirmRepairFlow
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er, issue_registry as ir
from pystiebeleltron import ControllerModel
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg import repairs
from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.migration import duplicate_entity_issue_id

MODEL = ControllerModel.WPM_3
MODEL_NAME = "Stiebel Eltron WPM_3"
KEY = "outdoor_temperature"


@pytest.fixture
def legacy_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Register an entry that was created before the 2026.7 transition."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502, CONF_NAME: "My Heatpump"},
        entry_id="stiebel_eltron_repair",
    )
    entry.add_to_hass(hass)
    return entry


def _register_duplicate_pair(
    hass: HomeAssistant,
    entry: MockConfigEntry,
) -> tuple[er.RegistryEntry, er.RegistryEntry]:
    """Register an already-migrated winner and its model-name duplicate."""
    registry = er.async_get(hass)
    winner = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{entry.entry_id}_{KEY}",
        config_entry=entry,
        suggested_object_id="stiebel_eltron_isg_outdoor_temperature",
    )
    loser = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        f"{DOMAIN}_{MODEL_NAME}_{KEY}",
        config_entry=entry,
        suggested_object_id="stiebel_eltron_wpm_3_aussentemperatur",
    )
    return winner, loser


def _create_duplicate_issue(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    """Create the Repair that launches the cleanup flow."""
    ir.async_create_issue(
        hass,
        DOMAIN,
        duplicate_entity_issue_id(entry),
        data={"entry_id": entry.entry_id, "model_id": MODEL.value},
        is_fixable=True,
        is_persistent=True,
        issue_domain=DOMAIN,
        severity=ir.IssueSeverity.WARNING,
        translation_key="duplicate_entities",
        translation_placeholders={"count": "1", "entities": "sensor.duplicate"},
    )


async def _create_flow(
    hass: HomeAssistant,
    entry: MockConfigEntry,
) -> repairs.DuplicateEntityRepairFlow:
    """Create a live duplicate cleanup flow through its public factory."""
    flow = await repairs.async_create_fix_flow(
        hass,
        duplicate_entity_issue_id(entry),
        {"entry_id": entry.entry_id, "model_id": MODEL.value},
    )
    assert isinstance(flow, repairs.DuplicateEntityRepairFlow)
    flow.hass = hass
    return flow


async def test_confirmed_repair_removes_only_current_duplicate_losers(
    hass: HomeAssistant,
    legacy_config_entry: MockConfigEntry,
) -> None:
    """Confirmation removes the orphan while preserving the working winner."""
    winner, loser = _register_duplicate_pair(hass, legacy_config_entry)
    _create_duplicate_issue(hass, legacy_config_entry)
    flow = await _create_flow(hass, legacy_config_entry)

    form = await flow.async_step_init()

    assert form["type"] is FlowResultType.FORM
    assert form["step_id"] == "confirm"
    assert form["description_placeholders"] == {
        "count": "1",
        "entities": f"- `{loser.entity_id}`",
    }

    result = await flow.async_step_confirm({})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    registry = er.async_get(hass)
    assert registry.async_get(winner.entity_id) is not None
    assert registry.async_get(loser.entity_id) is None
    assert (
        ir.async_get(hass).async_get_issue(
            DOMAIN, duplicate_entity_issue_id(legacy_config_entry)
        )
        is None
    )


async def test_repair_revalidates_losers_before_removing_anything(
    hass: HomeAssistant,
    legacy_config_entry: MockConfigEntry,
) -> None:
    """A former loser survives if its winner disappears before confirmation."""
    winner, former_loser = _register_duplicate_pair(hass, legacy_config_entry)
    _create_duplicate_issue(hass, legacy_config_entry)
    flow = await _create_flow(hass, legacy_config_entry)
    assert (await flow.async_step_init())["type"] is FlowResultType.FORM

    er.async_get(hass).async_remove(winner.entity_id)
    result = await flow.async_step_confirm({})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert er.async_get(hass).async_get(former_loser.entity_id) is not None


async def test_repair_aborts_after_duplicates_were_removed_manually(
    hass: HomeAssistant,
    legacy_config_entry: MockConfigEntry,
) -> None:
    """Opening a stale Repair performs no registry mutation."""
    _create_duplicate_issue(hass, legacy_config_entry)
    flow = await _create_flow(hass, legacy_config_entry)

    result = await flow.async_step_init()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_duplicates"
    assert (
        ir.async_get(hass).async_get_issue(
            DOMAIN, duplicate_entity_issue_id(legacy_config_entry)
        )
        is None
    )


@pytest.mark.parametrize(
    ("issue_id", "data"),
    [
        ("duplicate_entities_missing", None),
        (
            "duplicate_entities_missing",
            {"entry_id": "missing", "model_id": MODEL.value},
        ),
        (
            "duplicate_entities_stiebel_eltron_repair",
            {"entry_id": "stiebel_eltron_repair", "model_id": "invalid"},
        ),
        (
            "duplicate_entities_stiebel_eltron_repair",
            {"entry_id": "stiebel_eltron_repair", "model_id": 999},
        ),
        (
            "unrelated_stiebel_eltron_repair",
            {"entry_id": "stiebel_eltron_repair", "model_id": MODEL.value},
        ),
    ],
)
async def test_malformed_repair_data_never_removes_registry_entries(
    hass: HomeAssistant,
    legacy_config_entry: MockConfigEntry,
    issue_id: str,
    data: dict[str, Any] | None,
) -> None:
    """Untrusted Repair identifiers cannot reach the deletion flow."""
    winner, loser = _register_duplicate_pair(hass, legacy_config_entry)

    flow = await repairs.async_create_fix_flow(hass, issue_id, data)

    assert isinstance(flow, ConfirmRepairFlow)
    registry = er.async_get(hass)
    assert registry.async_get(winner.entity_id) is not None
    assert registry.async_get(loser.entity_id) is not None
