"""Custom integration to integrate stiebel_eltron_isg with Home Assistant.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.loader import async_get_loaded_integration
from pystiebeleltron import get_controller_model

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

from .const import DEFAULT_SCAN_INTERVAL, PLATFORMS

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
):
    """Set up this integration using UI."""

    name = str(entry.data.get(CONF_NAME, entry.title))
    host = str(entry.data.get(CONF_HOST))
    port_data = entry.data.get(CONF_PORT)
    port = int(port_data) if port_data is not None else 502
    scan_interval = int(
        entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
    )

    try:
        model = await get_controller_model(host, port)
    except Exception as exception:
        raise ConfigEntryNotReady(exception) from exception

    coordinator = (
        StiebelEltronModbusWPMDataCoordinator(hass, name, host, port, scan_interval)
        if model.value >= 390
        else StiebelEltronModbusLWZDataCoordinator(
            hass,
            name,
            host,
            port,
            scan_interval,
        )
    )

    entry.runtime_data = StiebEltronISGIntegrationData(
        coordinator=coordinator,
        integration=async_get_loaded_integration(hass, entry.domain),
    )
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    coordinator = entry.runtime_data.coordinator
    await coordinator.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
