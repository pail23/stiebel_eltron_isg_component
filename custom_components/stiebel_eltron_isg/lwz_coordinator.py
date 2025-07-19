"""Data Coordinator for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)
from pystiebeleltron.lwz import (
    LwzStiebelEltronAPI,
    LwzSystemParametersRegisters,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusLWZDataCoordinator(StiebelEltronModbusDataCoordinator):
    """Thread safe wrapper class for pymodbus. Communicates with LWZ or LWA controller models."""

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
            hass, LwzStiebelEltronAPI(host=host, port=port), name, scan_interval
        )

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump is not implemented of LWZ/LWA")
        await self.write_register(LwzSystemParametersRegisters.RESET, value=1)
