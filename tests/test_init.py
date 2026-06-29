"""Test stiebel_eltron_isg setup process."""

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pystiebeleltron.wpm import WpmSystemParametersRegisters
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.wpm_coordinator import (
    StiebelEltronModbusWPMDataCoordinator,
)

from .const import MOCK_CONFIG

_COORDINATOR = "custom_components.stiebel_eltron_isg.coordinator.StiebelEltronModbusDataCoordinator"


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
@pytest.mark.asyncio
async def test_setup_unload_and_reload_entry(
    hass: HomeAssistant,
    bypass_get_data,
    get_model_wpm,
):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the StiebelEltronModbusDataCoordinator.async_get_data
    # call, no code from custom_components/stiebel_eltron_isg/api.py actually runs.
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED

    assert isinstance(
        config_entry.runtime_data.coordinator,
        StiebelEltronModbusWPMDataCoordinator,
    )

    # Unload the entry and verify that the data has been removed
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_data_coordinator_wpm(hass: HomeAssistant, mock_modbus_wpm) -> None:
    """Test creating a data coordinator for wpm models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("sensor.stiebel_eltron_isg_actual_temperature_fek")
    assert state is not None
    assert state.state == "0.2"
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_energy_data_wpm(hass: HomeAssistant, mock_modbus_wpm) -> None:
    """Test creating a data coordinator for lwz models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("sensor.stiebel_eltron_isg_produced_heating_today")
    assert state is not None
    assert state.state == "0"

    state = hass.states.get("sensor.stiebel_eltron_isg_produced_heating_total")
    assert state is not None
    assert state.state == "2001"

    state = hass.states.get("sensor.stiebel_eltron_isg_produced_heating")
    assert state is not None
    assert state.state == "2001"

    state = hass.states.get("sensor.stiebel_eltron_isg_consumed_heating_today")
    assert state is not None
    assert state.state == "10"

    state = hass.states.get("sensor.stiebel_eltron_isg_consumed_heating_total")
    assert state is not None
    assert state.state == "12011"

    state = hass.states.get("sensor.stiebel_eltron_isg_consumed_heating")
    assert state is not None
    assert state.state == "12021"

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_climate_wpm(hass: HomeAssistant, mock_modbus_wpm) -> None:
    """Test creating a data coordinator for lwz models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("climate.stiebel_eltron_isg_heat_circuit_1")
    assert state is not None
    assert state.state == "auto"
    assert state.attributes["current_temperature"] == 8.3
    assert state.attributes["temperature"] == 0.1
    assert state.attributes["current_humidity"] == 8.0

    state = hass.states.get("climate.stiebel_eltron_isg_heat_circuit_2")
    assert state is not None
    assert state.state == "auto"
    assert state.attributes["current_temperature"] == 8.7
    assert state.attributes["temperature"] == 0.4
    assert state.attributes["current_humidity"] == 8

    state = hass.states.get("climate.stiebel_eltron_isg_heat_circuit_3")
    assert state is not None
    assert state.state == "auto"
    assert state.attributes["current_temperature"] == 9.1
    assert state.attributes["temperature"] == 4.9
    assert state.attributes["current_humidity"] == 9

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_data_coordinator_lwz(hass: HomeAssistant, mock_modbus_lwz) -> None:
    """Test creating a data coordinator for lwz models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test_lwz")
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("sensor.stiebel_eltron_isg_actual_room_temperature_hk_2")
    assert state is not None
    assert state.state == "0.3"

    state = hass.states.get("sensor.stiebel_eltron_isg_compressor_starts")
    assert state is not None
    assert state.state == "30033"

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_energy_data_lwz(hass: HomeAssistant, mock_modbus_lwz) -> None:
    """Test creating a data coordinator for lwz models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test_lwz")
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("sensor.stiebel_eltron_isg_produced_heating_today")
    assert state is not None
    assert state.state == "0"

    state = hass.states.get("sensor.stiebel_eltron_isg_produced_heating_total")
    assert state is not None
    assert state.state == "2001"

    state = hass.states.get("sensor.stiebel_eltron_isg_produced_heating")
    assert state is not None
    assert state.state == "2001"

    state = hass.states.get("sensor.stiebel_eltron_isg_consumed_heating_today")
    assert state is not None
    assert state.state == "21"

    state = hass.states.get("sensor.stiebel_eltron_isg_consumed_heating_total")
    assert state is not None
    assert state.state == "23022"

    state = hass.states.get("sensor.stiebel_eltron_isg_consumed_heating")
    assert state is not None
    assert state.state == "23043"

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.asyncio
async def test_number_skips_write_when_value_unchanged(
    hass: HomeAssistant, mock_modbus_wpm
) -> None:
    """A number must not write to the register when the value is unchanged."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state == ConfigEntryState.LOADED

    entity_id = "number.stiebel_eltron_isg_area_cooling_flow_temperature_target"

    # The library decodes data_type 2 registers as float(raw) * 0.1, which is
    # not exactly equal to the decimal the user sets (e.g. 71 * 0.1 != 7.1).
    # The unchanged check must tolerate that float imprecision.
    current = 71 * 0.1  # the value the coordinator would report for 7.1
    assert current != 7.1
    with (
        patch(f"{_COORDINATOR}.get_register_value", return_value=current),
        patch(f"{_COORDINATOR}.write_register", new=AsyncMock()) as write_register,
    ):
        # Setting the same value (within float tolerance) must NOT write.
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": 7.1},
            blocking=True,
        )
        write_register.assert_not_awaited()

        # Setting a different value must write once.
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": 12.0},
            blocking=True,
        )
        write_register.assert_awaited_once_with(
            WpmSystemParametersRegisters.SET_FLOW_TEMPERATURE_AREA, 12.0
        )

    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
