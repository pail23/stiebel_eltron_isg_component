"""Tests for the button platform."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from modbus_connection import ModbusError
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.button import StiebelEltronISGButtonEntity
from custom_components.stiebel_eltron_isg.const import DOMAIN, RESET_HEATPUMP
from custom_components.stiebel_eltron_isg.entity import build_unique_id


@pytest.mark.parametrize("last_update_success", [True, False])
def test_reset_button_availability_follows_coordinator(
    last_update_success: bool,
) -> None:
    """The reset action must not be offered while the device is unavailable."""
    entity = StiebelEltronISGButtonEntity.__new__(StiebelEltronISGButtonEntity)
    entity.coordinator = SimpleNamespace(last_update_success=last_update_success)

    assert entity.available is last_update_success


async def test_reset_button_becomes_unavailable_after_failed_refresh(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_wpm_api: MagicMock,
) -> None:
    """A failed coordinator refresh is reflected in the HA entity state."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_id = er.async_get(hass).async_get_entity_id(
        "button",
        DOMAIN,
        build_unique_id(mock_config_entry, RESET_HEATPUMP),
    )
    assert entity_id is not None
    assert hass.states.get(entity_id).state != STATE_UNAVAILABLE

    mock_wpm_api.async_update.side_effect = ModbusError("update failed")
    await mock_config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE
