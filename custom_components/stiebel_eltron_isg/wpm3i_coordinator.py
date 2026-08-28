"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from homeassistant.core import HomeAssistant
from modbus_connection import ModbusUnit
from pystiebeleltron import ControllerModel
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI

from .coordinator import (
    StiebelEltronConfigEntry,
    StiebelEltronConnectionParams,
    StiebelEltronDataCoordinator,
)

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
        unit: ModbusUnit,
        host: str,
    ) -> None:
        """Initialize the Modbus hub."""
        super().__init__(
            hass,
            entry,
            Wpm3iStiebelEltronAPI(unit),
            StiebelEltronConnectionParams(
                host=host,
                model=model,
            ),
        )
