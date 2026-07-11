"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from collections.abc import Callable
from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection.pymodbus import PymodbusConnection, connect_tcp
from pystiebeleltron import StiebelEltronModbusError
from pystiebeleltron.wpm import WpmStiebelEltronAPI

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusWPMDataCoordinator(DataUpdateCoordinator):
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
        self._model_id: int = 0
        self._host = host
        self._port = port
        self._scan_interval = timedelta(seconds=scan_interval)
        self._connection: PymodbusConnection | None = None
        self._api: WpmStiebelEltronAPI | None = None

        super().__init__(hass, _LOGGER, name=name, update_interval=self._scan_interval)

    async def connect(self) -> None:
        """Connect client."""
        _LOGGER.debug("Connecting to %s", self._host)
        self._connection = await connect_tcp(self._host, port=self._port)
        self._api = WpmStiebelEltronAPI(self._connection.for_unit(1))

    async def close(self) -> None:
        """Disconnect client."""
        _LOGGER.debug("Closing connection to %s", self._host)
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
            self._api = None

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

    async def _async_update_data(self) -> dict[Any, float | int | None]:
        """Time to update."""
        try:
            if not self.is_connected:
                await self.connect()
            if self._api is not None:
                await self._api.async_update()
                self._model_id = (
                    self._api.energy_system_information.controller_identification
                ) or 0

        except Exception as exception:
            raise UpdateFailed(exception) from exception
        else:
            return {}

    def get_value(
        self,
        value_reference: Callable[[WpmStiebelEltronAPI], float | int | None],
    ) -> float | int | None:
        """Return a value from a callable accessor."""
        try:
            if self._api is not None:
                value = value_reference(self._api)
        except StiebelEltronModbusError as err:
            _LOGGER.warning(
                "Failed to get value from accessor %r: %s",
                value_reference,
                err,
            )
            return None
        return value if isinstance(value, (int, float)) else None

    def has_value(
        self,
        value_reference: Callable[[WpmStiebelEltronAPI], float | int | None],
    ) -> bool:
        """Check if a callable accessor has a value."""
        return self.get_value(value_reference) is not None

    async def write_component_value(
        self,
        component: str,
        field: str,
        value: int | float,
    ) -> None:
        """Write a value to a component field."""
        if self._api is not None:
            component_obj = getattr(self._api, component, None)
            if component_obj is not None and hasattr(component_obj, field):
                await component_obj.write(field, value)

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        if self._api is not None:
            await self._api.system_parameters.write(
                "reset",
                3,
            )
