"""StiebelEltronISGEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, VERSION, ATTR_MANUFACTURER


class StiebelEltronISGEntity(CoordinatorEntity):
    """stiebel_eltron_isg entity base class."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.name)},
            configuration_url=f"http://{self.coordinator.host}",
            name=self.coordinator.name,
            model=VERSION,
            manufacturer=ATTR_MANUFACTURER,
        )
