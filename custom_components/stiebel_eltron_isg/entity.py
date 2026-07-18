"""StiebelEltronISGEntity class."""

from dataclasses import dataclass
from typing import Any

from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

try:
    from pystiebeleltron import IsgRegisters, IsgRegistersNone
except ImportError:
    IsgRegisters = Any

    class _IsgRegistersNone:
        NONE = "NONE"

    IsgRegistersNone = _IsgRegistersNone

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronDataCoordinator,
)
from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)


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
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
    ):
        """Initialize the entity base class."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.has_value(self.modbus_register)
