"""Sensor platform for stiebel_eltron_isg."""
import logging
from typing import Optional


from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import DEVICE_CLASS_ENERGY, ENERGY_KILO_WATT_HOUR

from .const import (
    DOMAIN,
    ENERGY_SENSOR_TYPES,
    SYSTEM_VALUES_SENSOR_TYPES,
    ENERGYMANAGEMENT_SENSOR_TYPES,
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in SYSTEM_VALUES_SENSOR_TYPES:
        sensor = StiebelEltronISGSensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    for description in ENERGYMANAGEMENT_SENSOR_TYPES:
        sensor = StiebelEltronISGSensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    for meter_sensor_info in ENERGY_SENSOR_TYPES:
        description = SensorEntityDescription(
            name=f"{meter_sensor_info[0]}",
            key=meter_sensor_info[1],
            native_unit_of_measurement=meter_sensor_info[2],
            icon=meter_sensor_info[3],
            state_class=STATE_CLASS_MEASUREMENT,
            has_entity_name=True,
        )
        if description.native_unit_of_measurement == ENERGY_KILO_WATT_HOUR:
            description.state_class = STATE_CLASS_TOTAL_INCREASING
            description.device_class = DEVICE_CLASS_ENERGY

        sensor = StiebelEltronISGSensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    async_add_devices(entities)


class StiebelEltronISGSensor(StiebelEltronISGEntity, SensorEntity):
    """stiebel_eltron_isg Sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        description,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> Optional[str]:
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
