"""Custom integration to integrate stiebel_eltron_isg with Home Assistant.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.core_config import Config
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.loader import async_get_loaded_integration
from pymodbus.client import AsyncModbusTcpClient

from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronISGIntegrationConfigEntry,
    StiebEltronISGIntegrationData,
)
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
            CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
        ): cv.positive_int,
    },
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: STIEBEL_ELTRON_ISG_SCHEMA})},
    extra=vol.ALLOW_EXTRA,
)


class StiebelEltronModbusError(Exception):
    """Exception during modbus communication."""

    def __init(self) -> None:
        """Initialize the error."""
        super().__init__("Data error on the modbus")


async def get_controller_model(host, port) -> int:
    """Read the model of the controller.

    LWA and LWZ controllers have model ids 103 and 104.
    WPM controllers have 390, 391 or 449.
    """
    client = AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        inverter_data = await client.read_input_registers(
            address=5001,
            count=1,
            slave=1,
        )
        if not inverter_data.isError():
            value = client.convert_from_registers(
                inverter_data.registers, client.DATATYPE.UINT16, "big"
            )
            if isinstance(value, int):
                return value

        raise StiebelEltronModbusError
    finally:
        client.close()


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StiebelEltronISGIntegrationConfigEntry,
):
    """Set up this integration using UI."""

    name = str(entry.data.get(CONF_NAME))
    host = str(entry.data.get(CONF_HOST))
    port_data = entry.data.get(CONF_PORT)
    port = int(port_data) if port_data is not None else 502
    scan_interval = int(entry.data[CONF_SCAN_INTERVAL])

    try:
        model = await get_controller_model(host, port)
    except Exception as exception:
        raise ConfigEntryNotReady(exception) from exception

    coordinator = (
        StiebelEltronModbusWPMDataCoordinator(hass, name, host, port, scan_interval)
        if model >= 390
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
    entry: StiebelEltronISGIntegrationConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    coordinator = entry.runtime_data.coordinator
    await coordinator.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: StiebelEltronISGIntegrationConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
