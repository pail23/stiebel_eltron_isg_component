"""Sensor platform for stiebel_eltron_isg."""
import logging
from typing import Optional, Dict, Any
from .const import (
    NAME,
    DOMAIN,
    ENERGY_SENSOR_TYPES,
)
from .entity import StiebelEltronISGEntity

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
)
from homeassistant.const import CONF_NAME, DEVICE_CLASS_ENERGY, ENERGY_KILO_WATT_HOUR
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT as STATE_CLASS_TOTAL_INCREASING,
)
from homeassistant.core import callback
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for meter_sensor_info in ENERGY_SENSOR_TYPES:
        sensor = StiebelEltronISGSensor(
            coordinator,
            entry,
            meter_sensor_info[0],
            meter_sensor_info[1],
            meter_sensor_info[2],
            meter_sensor_info[3],
        )
        entities.append(sensor)

    async_add_devices(entities)


class StiebelEltronISGSensor(StiebelEltronISGEntity, SensorEntity):
    """stiebel_eltron_isg Sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        name,
        key,
        unit,
        icon,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry, key)
        self._key = key
        self.sensor_name = name
        self._unit_of_measurement = unit
        self._icon = icon
        self._attr_state_class = STATE_CLASS_MEASUREMENT
        if self._unit_of_measurement == ENERGY_KILO_WATT_HOUR:
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
            self._attr_device_class = DEVICE_CLASS_ENERGY

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{NAME} {self.sensor_name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self.coordinator.name}_{self._key}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the sensor icon."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._key)
