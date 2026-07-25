"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from homeassistant.core import HomeAssistant
from modbus_connection import ModbusConnection
from pystiebeleltron import ControllerModel
from pystiebeleltron.wpm import WpmStiebelEltronAPI

from custom_components.stiebel_eltron_isg.const import UNIT_ID

from .coordinator import (
    StiebelEltronConfigEntry,
    StiebelEltronConnectionParams,
    StiebelEltronDataCoordinator,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusWPMDataCoordinator(
    StiebelEltronDataCoordinator[WpmStiebelEltronAPI]
):
    """Communicates with WPM Controllers."""

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
            WpmStiebelEltronAPI(connection.for_unit(UNIT_ID)),
            StiebelEltronConnectionParams(
                host=host,
                model=model,
                connection=connection,
            ),
        )
