"""Test stiebel_eltron_isg setup process."""
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.config_entries import ConfigEntryState
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg import (
    StiebelEltronModbusWPMDataCoordinator,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.stiebel_eltron_isg.const import DOMAIN

from .const import MOCK_CONFIG


# We can pass fixtures as defined in conftest.py to tell pytest to use the fixture
# for a given test. We can also leverage fixtures and mocks that are available in
# Home Assistant using the pytest_homeassistant_custom_component plugin.
# Assertions allow you to verify that the return value of whatever is on the left
# side of the assertion matches with the right side.
@pytest.mark.asyncio
async def test_setup_unload_and_reload_entry(hass, bypass_get_data, get_model_wpm):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because we have patched the StiebelEltronModbusDataCoordinator.async_get_data
    # call, no code from custom_components/stiebel_eltron_isg/api.py actually runs.
    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == StiebelEltronModbusWPMDataCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    assert await async_reload_entry(hass, config_entry) is None
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id])
        == StiebelEltronModbusWPMDataCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_setup_entry_exception(hass, error_on_get_data):
    """Test ConfigEntryNotReady when API raises an exception during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_get_data` fixture which simulates
    # an error.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


@pytest.mark.asyncio
async def test_data_coordinator_wpm(hass, mock_modbus_wpm):
    """Test creating a data coordinator for wpm models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test_wpm")

    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("sensor.stiebel_eltron_isg_actual_temperature_fek")
    assert state is not None
    assert state.state == '0.2'
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]

@pytest.mark.asyncio
async def test_data_coordinator_lwz(hass, mock_modbus_lwz):
    """Test creating a data coordinator for lwz models."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test_lwz")

    assert await async_setup_entry(hass, config_entry)
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]

    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED

    state = hass.states.get("sensor.stiebel_eltron_isg_actual_temperature_fek")
    assert state is not None
    assert state.state == '0.3'
    assert await async_unload_entry(hass, config_entry)
    assert config_entry.entry_id not in hass.data[DOMAIN]
