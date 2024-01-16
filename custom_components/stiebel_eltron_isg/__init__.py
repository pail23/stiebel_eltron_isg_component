"""Custom integration to integrate stiebel_eltron_isg with Home Assistant.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""
from datetime import timedelta
import logging


import voluptuous as vol

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.exceptions import ConfigEntryNotReady
from custom_components.stiebel_eltron_isg.lwz_coordinator import (
    StiebelEltronModbusLWZDataCoordinator,
)

from custom_components.stiebel_eltron_isg.wpm_coordinator import (
    StiebelEltronModbusWPMDataCoordinator,
)

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


STIEBEL_ELTRON_ISG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: STIEBEL_ELTRON_ISG_SCHEMA})}, extra=vol.ALLOW_EXTRA
)


def get_controller_model(host, port) -> int:
    """Read the model of the controller.

    LWA and LWZ controllers have model ids 103 and 104.
    WPM controllers have 390, 391 or 449.
    """
    client = ModbusTcpClient(host=host, port=port)
    try:
        client.connect()
        inverter_data = client.read_input_registers(address=5001, count=1, slave=1)
        client.close()
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            model = decoder.decode_16bit_uint()
            return model
    except Exception as ex:
        client.close()
        raise ex


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    name = entry.data.get(CONF_NAME)
    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT)
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    try:
        model = get_controller_model(host, port)
    except Exception as exception:
        raise ConfigEntryNotReady(exception) from exception

    coordinator = (
        StiebelEltronModbusWPMDataCoordinator(hass, name, host, port, scan_interval)
        if model >= 390
        else StiebelEltronModbusLWZDataCoordinator(
            hass, name, host, port, scan_interval
        )
    )
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.shutdown()
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
