"""Binary sensor platform for stiebel_eltron_isg."""
from typing import Optional


from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)

from .entity import StiebelEltronISGEntity
from .const import (
    DOMAIN,
    BINARY_SENSOR_TYPES,
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in BINARY_SENSOR_TYPES:
        sensor = StiebelEltronISGBinarySensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    async_add_devices(entities)


class StiebelEltronISGBinarySensor(StiebelEltronISGEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        description,
    ):
        """Initialize the binary sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get(self.entity_description.key)