"""Data Coordinator for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from homeassistant.core import HomeAssistant
from modbus_connection import ModbusConnection
from pystiebeleltron import ControllerModel
from pystiebeleltron.lwz import LwzStiebelEltronAPI

from .const import UNIT_ID
from .coordinator import (
    StiebelEltronConfigEntry,
    StiebelEltronConnectionParams,
    StiebelEltronDataCoordinator,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusLWZDataCoordinator(
    StiebelEltronDataCoordinator[LwzStiebelEltronAPI]
):
    """Thread safe wrapper class for pymodbus. Communicates with LWZ or LWA controller models."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: StiebelEltronConfigEntry,
        model: ControllerModel,
        connection: ModbusConnection,
        host: str,
    ) -> None:
        """Initialize the Modbus hub."""

        super().__init__(
            hass,
            entry,
            LwzStiebelEltronAPI(connection.for_unit(UNIT_ID)),
            StiebelEltronConnectionParams(
                host=host,
                model=model,
                connection=connection,
            ),
        )

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        await self._api.system_parameters.write(
            "reset",
            1,
        )
