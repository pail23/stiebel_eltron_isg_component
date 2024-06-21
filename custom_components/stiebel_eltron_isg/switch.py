"""Switch platform for stiebel_eltron_isg."""

import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)
from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronISGIntegrationConfigEntry,
)

from .const import (
    CIRCULATION_PUMP,
    DOMAIN,
    SG_READY_ACTIVE,
    SG_READY_INPUT_1,
    SG_READY_INPUT_2,
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = [
    SwitchEntityDescription(
        SG_READY_ACTIVE,
        SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Active",
    ),
    SwitchEntityDescription(
        SG_READY_INPUT_1,
        SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Input 1",
    ),
    SwitchEntityDescription(
        SG_READY_INPUT_2,
        SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Input 2",
    ),
    SwitchEntityDescription(
        CIRCULATION_PUMP,
        SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="Circulation Pump",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronISGIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = entry.runtime_data.coordinator

    entities = []

    for description in SWITCH_TYPES:
        switch = StiebelEltronISGSwitch(
            coordinator,
            entry,
            description,
        )
        entities.append(switch)

    async_add_devices(entities)


class StiebelEltronISGSwitch(StiebelEltronISGEntity, SwitchEntity):
    """stiebel_eltron_isg Sensor class."""

    def __init__(
        self, coordinator: StiebelEltronModbusDataCoordinator, config_entry, description
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the switch."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is not None:
            return self.coordinator.data.get(self.entity_description.key) != 0
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self.coordinator.set_data(self.entity_description.key, 1)
        await self.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        self.coordinator.set_data(self.entity_description.key, 0)
        await self.async_update()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get(self.entity_description.key) is not None
