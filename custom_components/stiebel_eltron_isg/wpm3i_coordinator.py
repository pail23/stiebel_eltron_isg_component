"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from homeassistant.core import HomeAssistant
from modbus_connection import ModbusConnection
from pystiebeleltron import ControllerModel

from custom_components.stiebel_eltron_isg.const import UNIT_ID

from .coordinator import (
    StiebelEltronConfigEntry,
    StiebelEltronConnectionParams,
    StiebelEltronDataCoordinator,
)
from .wpm3i import Wpm3iStiebelEltronAPI

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusWPM3iDataCoordinator(
    StiebelEltronDataCoordinator[Wpm3iStiebelEltronAPI]
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
            Wpm3iStiebelEltronAPI(connection.for_unit(UNIT_ID)),
            StiebelEltronConnectionParams(
                host=host,
                model=model,
                connection=connection,
            ),
        )
