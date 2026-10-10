"""WPM setup with and without the optional heating circuit 3 block."""

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
    COMPRESSOR_HEATING_HP_1,
    DOMAIN,
    OUTDOOR_TEMPERATURE,
    TARGET_TEMPERATURE_HK3,
    UNIT_ID,
)
from custom_components.stiebel_eltron_isg.entity import build_unique_id

# Wire addresses of the HK3 actual and set temperature, issue #693.
HK3_ACTUAL = 609
HK3_TARGET = 610
# First register of the optional energy block, heat pump 1 VD HEIZEN hours.
HP1_HEATING_RUNTIME = 3643


def _load_wpm_registers(unit) -> None:
    """Serve every WPM register, with 21.5 and 23.0 °C for HK3 and 2268 h for HP 1."""
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
    raw["input"][HP1_HEATING_RUNTIME] = 2268
    unit.load_raw(raw)


@pytest.mark.parametrize(
    "hk3_case",
    [
        pytest.param((ControllerModel.WPMsystem, True), id="WPMsystem-with-HK3"),
        pytest.param((ControllerModel.WPMsystem, False), id="WPMsystem-without-HK3"),
        pytest.param((ControllerModel.WPM_3, True), id="WPM3-with-HK3"),
        pytest.param((ControllerModel.WPM_3, False), id="WPM3-without-HK3"),
    ],
)
async def test_wpm_setup_tolerates_missing_hk3_block(
    hass,
    mock_config_entry,
    mock_get_controller_model,
    mock_modbus_connection,
    hk3_case,
) -> None:
    """Missing HK3 blocks do not prevent setup, issues #693 and #722."""
    model, serves_hk3 = hk3_case
    unit = mock_modbus_connection.for_unit(UNIT_ID)
    _load_wpm_registers(unit)
    if not serves_hk3:
        unit.fail_read(HK3_ACTUAL, IllegalDataAddressError(2), register_type="input")

    api = WpmStiebelEltronAPI(unit)
    mock_get_controller_model.return_value = model
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


@pytest.mark.parametrize(
    "block_case",
    [
        pytest.param(
            (HK3_ACTUAL, ACTUAL_TEMPERATURE_HK3, "21.5", 220, "22.0"), id="HK3-block"
        ),
        pytest.param(
            (HP1_HEATING_RUNTIME, COMPRESSOR_HEATING_HP_1, "2268", 2269, "2269"),
            id="energy-block",
        ),
    ],
)
async def test_optional_block_refused_after_a_successful_read_until_answered_again(
    hass,
    mock_config_entry,
    mock_get_controller_model,
    mock_modbus_connection,
    block_case,
) -> None:
    """A later refusal makes the entities unavailable until the block is answered again."""
    refused_address, key, served, raw_later, served_later = block_case
    unit = mock_modbus_connection.for_unit(UNIT_ID)
    _load_wpm_registers(unit)

    api = WpmStiebelEltronAPI(unit)
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_config_entry.add_to_hass(hass)
    with patch(
        "custom_components.stiebel_eltron_isg.wpm_coordinator.WpmStiebelEltronAPI",
        return_value=api,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    registry = er.async_get(hass)

    def state_of(entity_key: str) -> str:
        entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, build_unique_id(mock_config_entry, entity_key)
        )
        assert entity_id is not None
        return hass.states.get(entity_id).state

    async def poll() -> None:
        await mock_config_entry.runtime_data.async_refresh()
        await hass.async_block_till_done()

    assert state_of(key) == served
    assert state_of(OUTDOOR_TEMPERATURE) != STATE_UNAVAILABLE

    unit.fail_read(refused_address, IllegalDataAddressError(2), register_type="input")
    await poll()

    assert state_of(key) == STATE_UNAVAILABLE
    assert state_of(OUTDOOR_TEMPERATURE) == STATE_UNAVAILABLE

    # The block must be read again, not skipped: a skipped block would let the
    # next poll succeed and bring back the cached value from before the refusal.
    unit.load_raw({"input": {refused_address: raw_later}})
    await poll()

    assert state_of(key) == STATE_UNAVAILABLE
    assert state_of(OUTDOOR_TEMPERATURE) == STATE_UNAVAILABLE

    unit.fail_read(refused_address, None, register_type="input")
    await poll()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert state_of(key) == served_later
    assert state_of(OUTDOOR_TEMPERATURE) != STATE_UNAVAILABLE
