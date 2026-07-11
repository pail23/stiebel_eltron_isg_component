"""Data Coordinator for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from pystiebeleltron import lwz as lwz_module
from custom_components.stiebel_eltron_isg.client_bridge import StiebelEltronApiBridge
from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)


class _RegisterShim:
    def __getattr__(self, name: str) -> str:
        return name


LwzStiebelEltronAPI = lwz_module.LwzStiebelEltronAPI
LwzSystemParametersRegisters: Any = getattr(
    lwz_module,
    "LwzSystemParametersRegisters",
    _RegisterShim(),
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusLWZDataCoordinator(StiebelEltronModbusDataCoordinator):
    """Thread safe wrapper class for pymodbus. Communicates with LWZ or LWA controller models."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        port: int,
        scan_interval: int,
    ) -> None:
        """Initialize the Modbus hub."""

        super().__init__(
            hass,
            StiebelEltronApiBridge(LwzStiebelEltronAPI, host=host, port=port),
            name,
            scan_interval,
        )

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump is not implemented of LWZ/LWA")
        await self.write_component_value(
            "system_parameters",
            "reset",
            1,
            getattr(LwzSystemParametersRegisters, "RESET", None),
        )
