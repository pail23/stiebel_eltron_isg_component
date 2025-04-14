"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)

from .python_stiebel_eltron.wpm import (
    WpmStiebelEltronAPI,
    WpmSystemParametersRegisters,
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

    async def read_modbus_data(self) -> dict:
        """Read the ISG data through modbus."""
        return {}

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        await self.write_register(WpmSystemParametersRegisters.RESET, value=3)

    def assign_if_increased(self, value: float | int, key: str) -> float:
        """Assign the value as new value or keep the old value from the internal cache in case the old value is larger than value."""
        if value == 0:
            return 0
        if self.data:
            data = self.data.get(key)
            if data is not None:
                old_value = float(data)
                _LOGGER.debug(
                    f"old value for {key} is {old_value} new value is {value}"
                )
                if old_value > value:
                    _LOGGER.info(
                        f"Value for {key} is not strictly increasing existing value is {old_value} and new value is {value}",
                    )
                    return old_value
        return value
