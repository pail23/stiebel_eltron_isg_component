"""Select platform for stiebel_eltron_isg."""

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import OPERATION_MODE
from .coordinator import (
    AnyStiebelEltronDataCoordinator,
    ControllerFamily,
    StiebelEltronConfigEntry,
)
from .entity import StiebelEltronISGEntity, ValueAccessor

PARALLEL_UPDATES = 1


OPERATION_MODE_WPM_OPTIONS = {
    0: "emergency",
    1: "ready",
    2: "program",
    3: "comfort",
    4: "eco",
    5: "water_heating",
}

OPERATION_MODE_LWZ_OPTIONS = {
    0: "emergency",
    1: "ready",
    3: "comfort",
    4: "eco",
    5: "water_heating",
    11: "automatic",
    14: "manual",
}


@dataclass(frozen=True, kw_only=True)
class StiebelEltronSelectEntityDescription(SelectEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: ValueAccessor
    write_component: str = "system_parameters"
    write_field: str | None = None
    operation_modes: dict[int, str]


WPM_SELECT_TYPES = [
    StiebelEltronSelectEntityDescription(
        key=OPERATION_MODE,
        translation_key="operation_mode",
        modbus_register=lambda api: api.system_parameters.operating_mode,
        write_field="operating_mode",
        operation_modes=OPERATION_MODE_WPM_OPTIONS,
    ),
]

LWZ_SELECT_TYPES = [
    StiebelEltronSelectEntityDescription(
        key=OPERATION_MODE,
        translation_key="operation_mode",
        modbus_register=lambda api: api.system_parameters.operating_mode,
        write_field="operating_mode",
        operation_modes=OPERATION_MODE_LWZ_OPTIONS,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator = entry.runtime_data
    descriptions = (
        LWZ_SELECT_TYPES
        if coordinator.family is ControllerFamily.LWZ
        else WPM_SELECT_TYPES
    )
    async_add_devices([
        StiebelEltronISGSelectEntity(coordinator, entry, description)
        for description in descriptions
    ])


def get_key_from_value(d: dict[int, str], val: str) -> int | None:
    """Return the value for a given key from a dictionary."""
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


class StiebelEltronISGSelectEntity(StiebelEltronISGEntity, SelectEntity):
    """stiebel_eltron_isg select class."""

    def __init__(
        self,
        coordinator: AnyStiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronSelectEntityDescription,
    ):
        """Initialize the select entity."""
        self.entity_description = description
        self._options = description.operation_modes
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register
        self.write_component = description.write_component
        self.write_field = description.write_field

    @property
    def options(self) -> list[str]:
        """Return the available options."""
        return list(self._options.values())

    @property
    def current_option(self) -> str | None:
        """Return the written option until the device confirmed it, else its own."""
        value = self.coordinator.pending_value(self.write_component, self.write_field)
        if value is None:
            value = self.coordinator.get_value(self.modbus_register)
        if value is None:
            return None
        return self._options.get(int(value))

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        key = get_key_from_value(self._options, option)
        if key is None or self.write_field is None:
            return

        async with self.coordinator.write_lock:
            if self.current_option == option:
                return

            await self.coordinator.write_component_value(
                self.write_component,
                self.write_field,
                key,
            )
