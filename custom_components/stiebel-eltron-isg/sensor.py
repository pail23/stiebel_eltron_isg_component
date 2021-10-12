"""Sensor platform for stiebel_eltron_isg."""
from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import StiebelEltronISGEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([StiebelEltronISGSensor(coordinator, entry)])


class StiebelEltronISGSensor(StiebelEltronISGEntity):
    """stiebel_eltron_isg Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return 1.23

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON
