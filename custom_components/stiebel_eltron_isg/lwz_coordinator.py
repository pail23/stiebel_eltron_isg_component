"""Data Coordinator for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pystiebeleltron import StiebelEltronModbusError
from pystiebeleltron.lwz import LwzStiebelEltronAPI

from .coordinator import StiebelEltronModbusDataCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusLWZDataCoordinator(StiebelEltronModbusDataCoordinator):
    """Thread safe wrapper class for pymodbus. Communicates with LWZ or LWA controller models."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        host: str,
        port: int,
        scan_interval: int,
    ) -> None:
        """Initialize the Modbus hub."""
        self._api: LwzStiebelEltronAPI | None = None
        super().__init__(
            hass, name=name, host=host, port=port, scan_interval=scan_interval
        )

    async def connect(self) -> None:
        """Connect client."""
        await super().connect()
        self._api = LwzStiebelEltronAPI(self._for_unit(1))

    async def close(self) -> None:
        """Disconnect client."""
        await super().close()
        self._api = None

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
        value_reference: Callable[[LwzStiebelEltronAPI], float | int | None],
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
        value_reference: Callable[[LwzStiebelEltronAPI], float | int | None],
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
                1,
            )
