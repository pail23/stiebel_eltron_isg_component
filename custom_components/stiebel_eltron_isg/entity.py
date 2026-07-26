"""StiebelEltronISGEntity class."""

from dataclasses import dataclass
from typing import Any

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import StiebelEltronConfigEntry, StiebelEltronDataCoordinator


def build_unique_id(entry: StiebelEltronConfigEntry, key: str) -> str:
    """Return the unique id of an entity of this config entry."""
    return f"{entry.entry_id}_{key}"


@dataclass(frozen=True, kw_only=True)
class StiebelEltronEntityDescription(EntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: Any


class StiebelEltronISGEntity(CoordinatorEntity[StiebelEltronDataCoordinator]):
    """stiebel_eltron_isg entity base class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
    ):
        """Initialize the entity base class."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_device_info = coordinator.device_info

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the entity.

        Derived from the config entry, never from a display name: a name is
        allowed to change, and when it did in 2026.7 it orphaned every entity.
        """
        return build_unique_id(self.config_entry, self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return True if entity is available.

        An entity is only available when the most recent coordinator update
        succeeded; otherwise a lost connection would keep reporting the last
        cached register value as if it were current.
        """
        return self.coordinator.last_update_success and self.coordinator.has_value(
            self.modbus_register
        )
