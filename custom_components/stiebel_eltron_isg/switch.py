"""Switch platform for stiebel_eltron_isg."""
import logging
from typing import Optional, Any


from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
    SwitchDeviceClass,
)

from .const import DOMAIN, SWITCH_TYPES
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

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

    def __init__(self, coordinator, config_entry, description):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> Optional[str]:
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.coordinator.data.get(self.entity_description.key) != 0

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        self.coordinator.set_data(self.entity_description.key, 1)
        await self.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        self.coordinator.set_data(self.entity_description.key, 0)
        await self.async_update()
