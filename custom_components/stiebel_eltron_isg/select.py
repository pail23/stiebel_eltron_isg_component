"""Select platform for stiebel_eltron_isg."""

import logging
from dataclasses import dataclass

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pystiebeleltron import IsgRegisters
from pystiebeleltron.lwz import (
    LwzSystemParametersRegisters,
)
from pystiebeleltron.wpm import (
    WpmSystemParametersRegisters,
)

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)
from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)

from .const import DOMAIN, OPERATION_MODE
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


OPERATION_MODE_WPM_OPTIONS = {
    0: "Emergency",
    1: "Ready",
    2: "Program",
    3: "Comfort",
    4: "Eco",
    5: "Water heating",
}

OPERATION_MODE_LWZ_OPTIONS = {
    0: "Emergency",
    1: "Ready",
    3: "Comfort",
    4: "Eco",
    5: "Water heating",
    11: "Automatic",
    14: "Manual",
}


@dataclass(frozen=True, kw_only=True)
class StiebelEltronSelectEntityDescription(SelectEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: IsgRegisters
    operation_modes: dict


WPM_SELECT_TYPES = [
    StiebelEltronSelectEntityDescription(
        key=OPERATION_MODE,
        has_entity_name=True,
        name="Operation Mode",
        modbus_register=WpmSystemParametersRegisters.OPERATING_MODE,
        operation_modes=OPERATION_MODE_WPM_OPTIONS,
    ),
]

LWZ_SELECT_TYPES = [
    StiebelEltronSelectEntityDescription(
        key=OPERATION_MODE,
        has_entity_name=True,
        name="Operation Mode",
        modbus_register=LwzSystemParametersRegisters.OPERATING_MODE,
        operation_modes=OPERATION_MODE_LWZ_OPTIONS,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator = entry.runtime_data.coordinator

    entities = []
    if coordinator.is_wpm:
        entities = [
            StiebelEltronISGSelectEntity(
                coordinator,
                entry,
                description,
            )
            for description in WPM_SELECT_TYPES
        ]
    else:
        entities = [
            StiebelEltronISGSelectEntity(
                coordinator,
                entry,
                description,
            )
            for description in LWZ_SELECT_TYPES
        ]

    async_add_devices(entities)


def get_key_from_value(d, val) -> int | None:
    """Return the value for a given key from a dictionary."""
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


class StiebelEltronISGSelectEntity(StiebelEltronISGEntity, SelectEntity):
    """stiebel_eltron_isg select class."""

    def __init__(
        self,
        coordinator: StiebelEltronModbusDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
        description: StiebelEltronSelectEntityDescription,
    ):
        """Initialize the select entity."""
        self.entity_description = description
        self._options = description.operation_modes
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the select entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def options(self):
        """Return the available options."""
        return list(self._options.values())

    @property
    def current_option(self):
        """Return current option."""
        key = int(self.coordinator.get_register_value(self.modbus_register))
        return self._options.get(key)

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        key = get_key_from_value(self._options, option)
        if key is not None:
            await self.coordinator.write_register(self.modbus_register, key)
