"""Binary sensor platform for stiebel_eltron_isg."""
from typing import Optional


from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import StiebelEltronISGEntity
from .const import DOMAIN, IS_HEATING, IS_COOLING, IS_HEATING_WATER, IS_SUMMER_MODE

BINARY_SENSOR_TYPES = [
    BinarySensorEntityDescription(
        name="Is heating",
        key=IS_HEATING,
        icon="mdi:radiator",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Is heating boiler",
        key=IS_HEATING_WATER,
        icon="mdi:water-boiler",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Is in summer mode",
        key=IS_SUMMER_MODE,
        icon="mdi:weather-sunny",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Is cooling",
        key=IS_COOLING,
        icon="mdi:snowflake",
        has_entity_name=True,
    ),
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
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
        """Return the unique id of the sensor."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get(self.entity_description.key) is not None
