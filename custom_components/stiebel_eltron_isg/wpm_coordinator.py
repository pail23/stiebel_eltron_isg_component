"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from pystiebeleltron import wpm as wpm_module

from custom_components.stiebel_eltron_isg.client_bridge import StiebelEltronApiBridge
from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)


class _RegisterShim:
    def __getattr__(self, name: str) -> str:
        return name


WpmStiebelEltronAPI = wpm_module.WpmStiebelEltronAPI
WpmSystemParametersRegisters: Any = getattr(
    wpm_module,
    "WpmSystemParametersRegisters",
    _RegisterShim(),
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusWPMDataCoordinator(StiebelEltronModbusDataCoordinator):
    """Communicates with WPM Controllers."""

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
            StiebelEltronApiBridge(WpmStiebelEltronAPI, host=host, port=port),
            name,
            scan_interval,
        )

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        await self.write_component_value(
            "system_parameters",
            "reset",
            3,
            getattr(WpmSystemParametersRegisters, "RESET", None),
        )
