"""Select platform for stiebel_eltron_isg."""
import logging
from typing import Optional


from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
)
from .const import DOMAIN, OPERATION_MODE
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


OPERATION_MODE_WPM_OPTIONS = {
    0: "Emergency",
    1: "Ready",
    2: "Program",
    3: "Comfort",
    4: "Eco",
    5: "Water heating",
}

OPERATION_MODE_LWZ_OPTIONS = {
    0: "Emergency",
    1: "Ready",
    3: "Comfort",
    4: "Eco",
    5: "Water heating",
    11: "Automatic",
    14: "Manual",
}


SELECT_TYPES = [
    SelectEntityDescription(
        OPERATION_MODE,
        has_entity_name=True,
        name="Operation Mode",
    )
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in SELECT_TYPES:
        select_entity = StiebelEltronISGSelectEntity(
            coordinator,
            entry,
            description,
            OPERATION_MODE_WPM_OPTIONS
            if coordinator.is_wpm
            else OPERATION_MODE_LWZ_OPTIONS,
        )
        entities.append(select_entity)
    async_add_devices(entities)


def get_key_from_value(d, val):
    """Return the value for a given key from a dictionary."""
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None


class StiebelEltronISGSelectEntity(StiebelEltronISGEntity, SelectEntity):
    """stiebel_eltron_isg select class."""

    def __init__(self, coordinator, config_entry, description, options):
        """Initialize the select entity."""
        self.entity_description = description
        self._options = options
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> Optional[str]:
        """Return the unique id of the select entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def options(self):
        """Return the available options."""
        return list(self._options.values())

    @property
    def current_option(self):
        """Return current option."""
        key = self.coordinator.data.get(self.entity_description.key)
        return self._options.get(key)

    async def async_select_option(self, option: str) -> None:
        """Update the current selected option."""
        key = get_key_from_value(self._options, option)
        self.coordinator.set_data(self.entity_description.key, key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get(self.entity_description.key) is not None
