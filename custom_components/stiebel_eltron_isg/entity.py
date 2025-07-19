"""StiebelEltronISGEntity class."""

from dataclasses import dataclass

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pystiebeleltron import (
    IsgRegisters,
    IsgRegistersNone,
)

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)
from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)

from .const import ATTR_MANUFACTURER, DOMAIN


@dataclass(frozen=True, kw_only=True)
class StiebelEltronEntityDescription(EntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: IsgRegisters


class StiebelEltronISGEntity(CoordinatorEntity[StiebelEltronModbusDataCoordinator]):
    """stiebel_eltron_isg entity base class."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: StiebelEltronModbusDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
    ):
        """Initialize the entity base class."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.modbus_register: IsgRegisters = IsgRegistersNone.NONE

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
        return self.available

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.has_register_value(self.modbus_register)
