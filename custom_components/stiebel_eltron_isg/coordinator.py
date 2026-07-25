"""Data Coordinator base class for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any, Protocol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusConnection, ModbusUnit
from modbus_connection.cli_helper import field_rows
from pystiebeleltron import ControllerModel, ModbusError, StiebelEltronModbusError

from custom_components.stiebel_eltron_isg.const import (
    ATTR_MANUFACTURER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

type StiebelEltronConfigEntry = ConfigEntry[StiebelEltronDataCoordinator]


class StiebelEltronApi(Protocol):
    """Protocol for Stiebel Eltron API clients."""

    async def async_update(self) -> None:
        """Read every component in one pooled set of block reads."""
        ...


@dataclass
class StiebelEltronConnectionParams:
    """Connection parameters for Stiebel Eltron ISG."""

    host: str
    model: ControllerModel
    connection: ModbusConnection


class StiebelEltronDataCoordinator[T: StiebelEltronApi](DataUpdateCoordinator):
    """Data coordinator base class for stiebel eltron isg."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: StiebelEltronConfigEntry,
        api_client: T,
        params: StiebelEltronConnectionParams,
    ) -> None:
        """Initialize the Modbus hub."""
        self._model: ControllerModel = params.model
        self._host = params.host
        self._connection = params.connection
        self._api = api_client

        super().__init__(
            hass,
            _LOGGER,
            name=f"Stiebel Eltron {self._model.name}",
            config_entry=entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            # The coordinator holds no data of its own (the API client caches
            # the register values), so there is nothing to diff against.
            always_update=True,
        )

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            configuration_url=f"http://{self._host}",
            name=self.name,
            model=self._model.name,
            model_id=str(self._model.value),
            manufacturer=ATTR_MANUFACTURER,
        )

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
    def model(self) -> ControllerModel:
        """Return the controller model of the Stiebel Eltron ISG."""
        return self._model

    @property
    def model_name(self) -> str:
        """Return the name of the controller model of the Stiebel Eltron ISG."""
        if self._model == ControllerModel.LWZ:
            return "LWA/LWZ"
        if self._model == ControllerModel.LWZ_x04_SOL:
            return "LWZ"
        if self._model == ControllerModel.WPM_3:
            return "WPM 3"
        if self._model == ControllerModel.WPM_3i:
            return "WPM 3i"
        if self._model == ControllerModel.WPMsystem:
            return "WPMsystem"
        if self._model == ControllerModel.LWZ_R290:
            return "LWZ R290"
        # Fall back to the enum name for a clear, readable representation
        return f"other model ({self._model.name})"

    def get_raw_data(self) -> dict:
        """Return the raw data from the heat pump."""
        result: dict = {}
        for component in vars(self._api).values():
            component_result = dict(field_rows(component))
            result = {**result, **component_result}
        return result

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
        value_reference: Callable[[T], float | int | None],
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
        value_reference: Callable[[T], float | int | None],
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
        await self.write_component_value("system_parameters", "reset", 3)
