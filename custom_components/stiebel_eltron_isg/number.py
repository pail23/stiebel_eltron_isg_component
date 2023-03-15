"""Sensor number for stiebel_eltron_isg."""
import logging
from typing import Optional

from homeassistant.const import (
    UnitOfTemperature,
)

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from .const import DOMAIN, COMFORT_TEMPERATURE_TARGET, ECO_TEMPERATURE_TARGET
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


NUMBER_TYPES = [
    NumberEntityDescription(
        COMFORT_TEMPERATURE_TARGET,
        has_entity_name=True,
        name="Comfort Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="hass:thermometer",
        native_min_value=5,
        native_max_value=30,
        native_step=1,
    ),
    NumberEntityDescription(
        ECO_TEMPERATURE_TARGET,
        has_entity_name=True,
        name="Eco Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="hass:thermometer",
        native_min_value=5,
        native_max_value=30,
        native_step=1,
    ),
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in NUMBER_TYPES:
        select_entity = StiebelEltronISGNumberEntity(coordinator, entry, description)
        entities.append(select_entity)
    async_add_devices(entities)


class StiebelEltronISGNumberEntity(StiebelEltronISGEntity, NumberEntity):
    """stiebel_eltron_isg select class."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> Optional[str]:
        """Return the unique id of the select entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        self.coordinator.set_data(self.entity_description.key, value)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get(self.entity_description.key) is not None
