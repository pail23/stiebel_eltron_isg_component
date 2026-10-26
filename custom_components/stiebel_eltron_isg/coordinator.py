"""Data update coordinator for Stiebel Eltron ISG controllers.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import asyncio
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
import logging
from typing import Any, Protocol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError, ModbusUnit
from modbus_connection.cli_helper import field_rows
from modbus_connection.model import Component, ManualComponent
from pystiebeleltron import ControllerModel
from pystiebeleltron.lwz import LwzStiebelEltronAPI
from pystiebeleltron.wpm import WpmStiebelEltronAPI
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI

from custom_components.stiebel_eltron_isg.const import (
    ATTR_MANUFACTURER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

type StiebelEltronConfigEntry = ConfigEntry[StiebelEltronDataCoordinator]


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


class ControllerFamily(Enum):
    """The register layout a controller model is served with.

    The platforms pick their entity descriptions by family, not by model, so
    a model that shares a layout is added in one place: ``CONTROLLER_FAMILIES``.
    """

    WPM_3I = "wpm_3i"
    WPM = "wpm"
    LWZ = "lwz"


CONTROLLER_FAMILIES: dict[ControllerModel, ControllerFamily] = {
    ControllerModel.WPM_3i: ControllerFamily.WPM_3I,
    ControllerModel.WPM_3: ControllerFamily.WPM,
    ControllerModel.WPMsystem: ControllerFamily.WPM,
    ControllerModel.LWZ_R290: ControllerFamily.WPM,
    ControllerModel.LWZ: ControllerFamily.LWZ,
    ControllerModel.LWZ_x04_SOL: ControllerFamily.LWZ,
}

# The value ``system_parameters.reset`` takes to restart the heat pump.
RESET_VALUES: dict[ControllerFamily, int] = {
    ControllerFamily.WPM_3I: 3,
    ControllerFamily.WPM: 3,
    ControllerFamily.LWZ: 1,
}


class StiebelEltronApi(Protocol):
    """Protocol for Stiebel Eltron API clients."""

    async def async_update(self) -> None:
        """Read every component in one pooled set of block reads."""
        ...


def create_api(family: ControllerFamily, unit: ModbusUnit) -> StiebelEltronApi:
    """Return the library client that reads a family's register layout."""
    if family is ControllerFamily.WPM_3I:
        return Wpm3iStiebelEltronAPI(unit)
    if family is ControllerFamily.WPM:
        return WpmStiebelEltronAPI(unit)
    return LwzStiebelEltronAPI(unit)


@dataclass(frozen=True)
class PendingWrite:
    """A value written to the device that no later poll has confirmed yet."""

    value: float | int
    # The newest poll that had started when the value was written. A poll with
    # a higher generation started after the write and is the first one that can
    # report what the device made of it.
    refresh_generation: int


class StiebelEltronDataCoordinator(DataUpdateCoordinator[None]):
    """Poll one controller and route writes to it.

    The coordinator holds no data of its own: the API client caches the
    register values, and entities read them through accessors.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: StiebelEltronConfigEntry,
        api_client: StiebelEltronApi,
        model: ControllerModel,
        host: str,
    ) -> None:
        """Initialize the Modbus hub."""
        self._model = model
        self._host = host
        self._api = api_client
        self._refresh_generation = 0
        self._last_successful_refresh_generation = 0
        self._pending_writes: dict[tuple[str, str], PendingWrite] = {}
        self._write_lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=coordinator_display_name(self._model),
            config_entry=entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            # There is no coordinator data to diff against, so every successful
            # poll has to notify the entities.
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
    def family(self) -> ControllerFamily:
        """Return the register layout family of the controller model."""
        return CONTROLLER_FAMILIES[self._model]

    def get_raw_data(self) -> dict[str, Any]:
        """Return the raw data from the heat pump."""
        result: dict[str, Any] = {}
        for component in vars(self._api).values():
            # APIs also contain polling helpers, which have no register fields.
            if not isinstance(component, (Component, ManualComponent)):
                continue
            result.update(field_rows(component))
        return result

    async def _async_update_data(self) -> None:
        """Time to update."""
        self._refresh_generation += 1
        generation = self._refresh_generation
        try:
            await self._api.async_update()
        except ModbusError as exception:
            raise UpdateFailed(exception) from exception
        self._last_successful_refresh_generation = generation
        # Only a poll that started after a write can have read the device's
        # answer to it. A poll that was already in flight may have read the
        # registers before the write, so its pending values stay.
        self._pending_writes = {
            key: pending
            for key, pending in self._pending_writes.items()
            if pending.refresh_generation >= generation
        }

    @property
    def refresh_generation(self) -> int:
        """Return the generation of the newest started refresh."""
        return self._refresh_generation

    @property
    def last_successful_refresh_generation(self) -> int:
        """Return the generation of the newest successful refresh."""
        return self._last_successful_refresh_generation

    @property
    def write_lock(self) -> asyncio.Lock:
        """Serialise an entity's comparison and write across all entities.

        A written value is only held once its write has completed. Two entities
        writing the same field at the same time would otherwise both compare
        against the value from before either write, and the second command
        would be dropped as unchanged or written twice. Holding this lock from
        the comparison to the end of the write makes the second one see the
        first. Home Assistant serialises calls within a platform only.
        """
        return self._write_lock

    def pending_value(
        self, component: str | None, field: str | None
    ) -> float | int | None:
        """Return the value last written to a field until the device confirmed it.

        A write travels ISG to CAN to heat pump and needs a moment to be
        reflected in the registers; the library does not update its cache on a
        write either. Until a poll started after the write has succeeded, the
        written value is therefore the best knowledge of the field. It is held
        here rather than in the entity that wrote it because several entities
        read and write the same field: the number and the climate entity share a
        setpoint, the select and every climate entity share the operating mode.
        A follow-up command from any of them has to see the value just written,
        both to display it and to decide whether a write would change anything.

        If the controller clamps or rounds the value, that correction appears
        with the first poll started after the write.
        """
        if component is None or field is None:
            return None
        pending = self._pending_writes.get((component, field))
        return pending.value if pending is not None else None

    def get_value(
        self,
        value_reference: Callable[[Any], float | int | None],
    ) -> float | int | None:
        """Return a value from a callable accessor.

        Accessors read the library's cache and raise nothing on their own; a
        non-numeric result, such as the unavailable marker decoded to None, is
        reported as no value. The client is passed untyped because accessors
        reach model-specific attributes the shared protocol cannot express.
        """
        value = value_reference(self._api)
        return value if isinstance(value, (int, float)) else None

    def has_value(
        self,
        value_reference: Callable[[Any], float | int | None],
    ) -> bool:
        """Check if a callable accessor has a value."""
        return self.get_value(value_reference) is not None

    def serves_component(
        self,
        component: str,
        registers: Iterable[Callable[[Any], float | int | None]],
    ) -> bool:
        """Return True if the library offers ``component`` and the unit answers it.

        Home Assistant Core pins a library release that may predate a component,
        and a controller that does not have an optional block reads it as
        unavailable for good. Entities that depend on such a component are only
        created when the library offers it and at least one of ``registers``
        holds a value after the first refresh.
        """
        if getattr(self._api, component, None) is None:
            return False
        return any(self.has_value(register) for register in registers)

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
        except ModbusError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="write_failed",
                translation_placeholders={"field": field},
            ) from err

        self._pending_writes[(component, field)] = PendingWrite(
            value, self._refresh_generation
        )
        # Every entity reading this field shows the written value right away.
        self.async_update_listeners()

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        await self.write_component_value(
            "system_parameters", "reset", RESET_VALUES[self.family]
        )
