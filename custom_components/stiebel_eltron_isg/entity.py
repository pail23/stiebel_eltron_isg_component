"""StiebelEltronISGEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, NAME, VERSION, ATTR_MANUFACTURER


class StiebelEltronISGEntity(CoordinatorEntity):
    """stiebel_eltron_isg entity base class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.name)},
            name=NAME,
            model=VERSION,
            manufacturer=ATTR_MANUFACTURER,
        )


'''
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            #            "attribution": ATTRIBUTION,
            "id": str(self.entity_description.key),
            "integration": DOMAIN,
        }
'''