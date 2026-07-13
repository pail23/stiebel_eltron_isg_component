"""Data Coordinator base class for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from modbus_connection import ModbusUnit
from modbus_connection.pymodbus import PymodbusConnection, connect_tcp

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusDataCoordinator(DataUpdateCoordinator):
    """Data coordinator base class for stiebel eltron isg."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        port: int,
        scan_interval: int,
    ) -> None:
        """Initialize the Modbus hub."""
        self._model_id: int = 0
        self._host = host
        self._port = port
        self._connection: PymodbusConnection | None = None
        self._scan_interval = timedelta(seconds=scan_interval)
        self.platforms: list[str] = []

        super().__init__(hass, _LOGGER, name=name, update_interval=self._scan_interval)

    async def close(self) -> None:
        """Disconnect client."""
        _LOGGER.debug("Closing connection to %s", self.host)
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def connect(self) -> None:
        """Connect client."""
        _LOGGER.debug("Connecting to %s", self.host)
        self._connection = await connect_tcp(self._host, port=self._port)

    def _for_unit(self, unit: int) -> ModbusUnit:
        """Return a connection for a specific unit."""
        if self._connection is None:
            raise RuntimeError("Connection not established")
        return self._connection.for_unit(unit)

    @property
    def is_connected(self) -> bool:
        """Check modbus client connection status."""
        if self._connection is None:
            return False
        return self._connection.connected

    @property
    def host(self) -> str:
        """Return the host address of the Stiebel Eltron ISG."""
        return self._host

    @property
    def model(self) -> str:
        """Return the controller model of the Stiebel Eltron ISG."""
        if self._model_id == 103:
            return "LWA/LWZ"
        if self._model_id == 104:
            return "LWZ"
        if self._model_id == 390:
            return "WPM 3"
        if self._model_id == 391:
            return "WPM 3i"
        if self._model_id == 449:
            return "WPMsystem"
        return f"other model ({self._model_id})"

    @property
    def is_wpm(self) -> bool:
        """Check if heat pump controller is a wpm model."""
        return self._model_id >= 390

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
