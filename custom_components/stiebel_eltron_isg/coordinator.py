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
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError
from modbus_connection.cli_helper import field_rows
from pystiebeleltron import ControllerModel, StiebelEltronModbusError

from custom_components.stiebel_eltron_isg.const import (
    ATTR_MANUFACTURER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

# Entity accessors reach model-specific API attributes that the shared protocol
# cannot express. Keep that erasure at the shared coordinator/config-entry
# boundary while the coordinator's own interface and data remain typed.
type AnyStiebelEltronDataCoordinator = StiebelEltronDataCoordinator[Any]
type StiebelEltronConfigEntry = ConfigEntry[AnyStiebelEltronDataCoordinator]


def _is_read_only_write_error(err: AttributeError, field: str) -> bool:
    """Return whether modbus_connection rejected a read-only field or space."""
    message = str(err)
    return message == f"{field} is read-only" or (
        message.startswith(f"{field} is in the ")
        and message.endswith(" register space, which is read-only")
    )


def coordinator_display_name(model: ControllerModel) -> str:
    """Return the display name used for a controller model.

    The unique id migration has to rebuild this exact string for entities that
    were created by an earlier release, so both places derive it from here.
    """
    return f"Stiebel Eltron {model.name}"


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


class StiebelEltronDataCoordinator[T: StiebelEltronApi](
    DataUpdateCoordinator[dict[str, float | int | None]]
):
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
        self._api = api_client
        self._refresh_generation = 0
        self._last_successful_refresh_generation = 0

        super().__init__(
            hass,
            _LOGGER,
            name=coordinator_display_name(self._model),
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

    def get_raw_data(self) -> dict[str, Any]:
        """Return the raw data from the heat pump."""
        result: dict[str, Any] = {}
        for component in vars(self._api).values():
            component_result = dict(field_rows(component))
            result = {**result, **component_result}
        return result

    async def _async_update_data(self) -> dict[str, float | int | None]:
        """Time to update."""
        self._refresh_generation += 1
        generation = self._refresh_generation
        try:
            await self._api.async_update()
        except ModbusError as exception:
            raise UpdateFailed(exception) from exception
        else:
            self._last_successful_refresh_generation = generation
            return {}

    @property
    def refresh_generation(self) -> int:
        """Return the generation of the newest started refresh."""
        return self._refresh_generation

    @property
    def last_successful_refresh_generation(self) -> int:
        """Return the generation of the newest successful refresh."""
        return self._last_successful_refresh_generation

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
        if component_obj is None or not hasattr(component_obj, field):
            _LOGGER.debug("Write target %s.%s is unsupported", component, field)
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_unsupported",
                translation_placeholders={"field": field},
            )

        try:
            await component_obj.write(field, value)
        except ValueError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_write_value",
                translation_placeholders={
                    "field": field,
                    "value": str(value),
                },
            ) from err
        except AttributeError as err:
            # Only translate the two documented read-only errors. An unrelated
            # AttributeError from inside the library is a programming error and
            # must remain visible.
            if not _is_read_only_write_error(err, field):
                raise
            _LOGGER.debug(
                "Write target %s.%s is read-only",
                component,
                field,
                exc_info=True,
            )
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_unsupported",
                translation_placeholders={"field": field},
            ) from err
        except (ModbusError, StiebelEltronModbusError) as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={"field": field},
            ) from err

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        await self.write_component_value("system_parameters", "reset", 3)
