"""Sensor platform for stiebel_eltron_isg."""
import logging
from typing import Optional, Dict, Any
from .const import (
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    SENSOR,
    ATTR_MANUFACTURER,
    ENERGY_SENSOR_TYPES,
)
from .entity import StiebelEltronISGEntity

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
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

    device_info = {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": entry.entry_id,
        "manufacturer": ATTR_MANUFACTURER,
    }
    entities = []
    for meter_sensor_info in ENERGY_SENSOR_TYPES.values():
        sensor = StiebelEltronISGSensor(
            DOMAIN,
            coordinator,
            device_info,
            meter_sensor_info[0],
            meter_sensor_info[1],
            meter_sensor_info[2],
            meter_sensor_info[3],
        )
        entities.append(sensor)

    async_add_devices(entities)


class StiebelEltronISGSensor(SensorEntity):
    """stiebel_eltron_isg Sensor class."""

    def __init__(self, platform_name, hub, device_info, name, key, unit, icon):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._hub = hub
        self._key = key
        self._name = name
        self._unit_of_measurement = unit
        self._icon = icon
        self._device_info = device_info
        self._attr_state_class = STATE_CLASS_MEASUREMENT
        if self._unit_of_measurement == ENERGY_KILO_WATT_HOUR:
            self._attr_state_class = STATE_CLASS_TOTAL_INCREASING
            self._attr_device_class = DEVICE_CLASS_ENERGY

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_isg_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_isg_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @callback
    def _update_state(self):
        if self._key in self._hub.data:
            self._state = self._hub.data[self._key]

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} ({self._name})"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self._key}"

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
        if self._key in self._hub.data:
            return self._hub.data[self._key]

    @property
    def extra_state_attributes(self):
        return None

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._device_info
