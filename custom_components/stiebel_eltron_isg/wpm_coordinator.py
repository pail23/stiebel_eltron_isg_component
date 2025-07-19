"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from pystiebeleltron.wpm import (
    WpmStiebelEltronAPI,
    WpmSystemParametersRegisters,
)

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusWPMDataCoordinator(StiebelEltronModbusDataCoordinator):
    """Communicates with WPM Controllers."""

    def __init__(
        self,
        hass,
        name: str,
        host: str,
        port: int,
        scan_interval,
    ):
        """Initialize the Modbus hub."""

        super().__init__(
            hass, WpmStiebelEltronAPI(host=host, port=port), name, scan_interval
        )

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        await self.write_register(WpmSystemParametersRegisters.RESET, value=3)
