"""StiebelEltronISGEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, VERSION, ATTR_MANUFACTURER


class StiebelEltronISGEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._key = key

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.name)},
            "name": NAME,
            "model": VERSION,
            "manufacturer": ATTR_MANUFACTURER,
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            #            "attribution": ATTRIBUTION,
            "id": str(self._key),
            "integration": DOMAIN,
        }
