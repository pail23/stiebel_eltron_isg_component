"""StiebelEltronISGEntity class."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, ATTR_MANUFACTURER


class StiebelEltronISGEntity(CoordinatorEntity):
    """stiebel_eltron_isg entity base class."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, config_entry):
        """Initialize the entity base class."""
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def device_info(self):
        """Return the device info of the entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.name)},
            configuration_url=f"http://{self.coordinator.host}",
            name=self.coordinator.name,
            model=self.coordinator.model,
            manufacturer=ATTR_MANUFACTURER,
        )

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added.

        This only applies when fist added to the entity registry.
        """
        return self.coordinator.data.get(self.entity_description.key) is not None
