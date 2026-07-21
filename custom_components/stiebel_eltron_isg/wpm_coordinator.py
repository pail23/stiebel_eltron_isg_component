"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from modbus_connection import ModbusConnection
from modbus_connection.cli_helper import field_rows
from pystiebeleltron import ControllerModel, ModbusError, StiebelEltronModbusError
from pystiebeleltron.wpm import WpmStiebelEltronAPI

from custom_components.stiebel_eltron_isg.const import UNIT_ID

from .coordinator import StiebelEltronConfigEntry, StiebelEltronDataCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronModbusWPMDataCoordinator(StiebelEltronDataCoordinator):
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
        self._api = WpmStiebelEltronAPI(connection.for_unit(UNIT_ID))

        super().__init__(hass, entry, model, connection, host)

    async def _async_update_data(self) -> dict[Any, float | int | None]:
        """Time to update."""
        try:
            await self._api.async_update()
        except ModbusError as exception:
            raise UpdateFailed(exception) from exception
        else:
            return {}

    def get_value(
        self,
        value_reference: Callable[[WpmStiebelEltronAPI], float | int | None],
    ) -> float | int | None:
        """Return a value from a callable accessor."""
        try:
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
        component_obj = getattr(self._api, component, None)
        if component_obj is not None and hasattr(component_obj, field):
            await component_obj.write(field, value)

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        await self._api.system_parameters.write(
            "reset",
            3,
        )

    def get_raw_data(self) -> dict:
        """Return the raw data from the heat pump."""
        result: dict = {}
        for component in vars(self._api).values():
            component_result = dict(field_rows(component))
            result = {**result, **component_result}
        return result
