"""Custom integration to integrate stiebel_eltron_isg with Home Assistant.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.loader import async_get_loaded_integration
from modbus_connection import ModbusError
from modbus_connection.pymodbus import connect_tcp
from pystiebeleltron import StiebelEltronModbusError, get_controller_model

from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
    StiebEltronISGIntegrationData,
)
from custom_components.stiebel_eltron_isg.lwz_coordinator import (
    StiebelEltronModbusLWZDataCoordinator,
)
from custom_components.stiebel_eltron_isg.wpm_coordinator import (
    StiebelEltronModbusWPMDataCoordinator,
)

from .const import DEFAULT_PORT, PLATFORMS, UNIT_ID

_LOGGER: logging.Logger = logging.getLogger(__package__)

_PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.CLIMATE,
]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
) -> bool:
    """Set up this integration using UI."""

    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    try:
        connection = await connect_tcp(host, port=port)
    except ModbusError as exception:
        raise ConfigEntryNotReady("Could not connect to device") from exception
    entry.async_on_unload(connection.close)

    try:
        model = await get_controller_model(connection.for_unit(UNIT_ID))
    except StiebelEltronModbusError as exception:
        raise ConfigEntryNotReady("Could not read controller model") from exception

    coordinator = (
        StiebelEltronModbusWPMDataCoordinator(hass, entry, model, connection, host)
        if model.value >= 390
        else StiebelEltronModbusLWZDataCoordinator(
            hass,
            entry,
            model,
            connection,
            host,
        )
    )

    entry.runtime_data = StiebEltronISGIntegrationData(
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(
        connection.on_connection_lost(
            lambda: hass.config_entries.async_schedule_reload(entry.entry_id)
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
