"""Test stiebel_eltron_isg setup process."""

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.wpm_coordinator import (
    StiebelEltronModbusWPMDataCoordinator,
)

from .const import MOCK_CONFIG


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
@pytest.mark.asyncio()
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


@pytest.mark.asyncio()
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


@pytest.mark.asyncio()
async def test_data_coordinator_lwz(hass: HomeAssistant, mock_modbus_lwz) -> None:
    """Test creating a data coordinator for lwz models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test_lwz")
    config_entry.add_to_hass(hass)

    # assert await async_setup_entry(hass, config_entry)
    # assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("sensor.stiebel_eltron_isg_actual_temperature_fek")
    assert state is not None
    assert state.state == "0.3"
    await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
