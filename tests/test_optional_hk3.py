"""WPMsystem setup with and without the optional heating circuit 3 block."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers import entity_registry as er
from modbus_connection import IllegalDataAddressError
from pystiebeleltron import ControllerModel
from pystiebeleltron.wpm import (
    WPM_HOLDING_RANGES,
    WPM_INPUT_RANGES,
    WpmStiebelEltronAPI,
)
import pytest

from custom_components.stiebel_eltron_isg.const import (
    ACTUAL_TEMPERATURE_HK3,
    DOMAIN,
    OUTDOOR_TEMPERATURE,
    TARGET_TEMPERATURE_HK3,
    UNIT_ID,
)
from custom_components.stiebel_eltron_isg.entity import build_unique_id

# Wire addresses of the HK3 actual and set temperature, issue #693.
HK3_ACTUAL = 609
HK3_TARGET = 610


@pytest.mark.parametrize("serves_hk3", [True, False])
async def test_wpmsystem_setup_tolerates_missing_hk3_block(
    hass,
    mock_config_entry,
    mock_get_controller_model,
    mock_modbus_connection,
    serves_hk3,
) -> None:
    """A controller that rejects the HK3 block still sets up, issue #693."""
    unit = mock_modbus_connection.for_unit(UNIT_ID)
    raw = {
        "input": {
            address: 0
            for start, end in WPM_INPUT_RANGES
            for address in range(start, end + 1)
        },
        "holding": {
            address: 0
            for start, end in WPM_HOLDING_RANGES
            for address in range(start, end + 1)
        },
    }
    raw["input"][HK3_ACTUAL] = 215
    raw["input"][HK3_TARGET] = 230
    unit.load_raw(raw)
    if not serves_hk3:
        unit.fail_read(HK3_ACTUAL, IllegalDataAddressError(2), register_type="input")

    api = WpmStiebelEltronAPI(unit)
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_config_entry.add_to_hass(hass)
    with patch(
        "custom_components.stiebel_eltron_isg.wpm_coordinator.WpmStiebelEltronAPI",
        return_value=api,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)

    def state_of(key: str) -> str:
        entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, build_unique_id(mock_config_entry, key)
        )
        assert entity_id is not None
        return hass.states.get(entity_id).state

    assert state_of(OUTDOOR_TEMPERATURE) != STATE_UNAVAILABLE
    if serves_hk3:
        assert state_of(ACTUAL_TEMPERATURE_HK3) == "21.5"
        assert state_of(TARGET_TEMPERATURE_HK3) == "23.0"
    else:
        assert state_of(ACTUAL_TEMPERATURE_HK3) == STATE_UNAVAILABLE
        assert state_of(TARGET_TEMPERATURE_HK3) == STATE_UNAVAILABLE
