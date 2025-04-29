"""Switch platform for stiebel_eltron_isg."""

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)
from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)
from custom_components.stiebel_eltron_isg.python_stiebel_eltron import (
    EnergyManagementSettingsRegisters,
    IsgRegisters,
)
from custom_components.stiebel_eltron_isg.python_stiebel_eltron.wpm import (
    WpmSystemStateRegisters,
)

from .const import (
    CIRCULATION_PUMP,
    DOMAIN,
    SG_READY_ACTIVE,
    SG_READY_INPUT_1,
    SG_READY_INPUT_2,
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


class WpmCirculationPumpRegisters(IsgRegisters):
    """Registers related to the circulation pump in the WPM system."""

    DHW_CIRCULATION_PUMP = 47012


@dataclass(frozen=True, kw_only=True)
class StiebelEltronSwitchEntityDescription(SwitchEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: IsgRegisters


SWITCH_TYPES = [
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_ACTIVE,
        device_class=SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Active",
        modbus_register=EnergyManagementSettingsRegisters.SWITCH_SG_READY_ON_AND_OFF,
    ),
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_INPUT_1,
        device_class=SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Input 1",
        modbus_register=EnergyManagementSettingsRegisters.SG_READY_INPUT_1,
    ),
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_INPUT_2,
        device_class=SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Input 2",
        modbus_register=EnergyManagementSettingsRegisters.SG_READY_INPUT_2,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = entry.runtime_data.coordinator

    entities = [
        StiebelEltronISGSwitch(
            coordinator,
            entry,
            description,
        )
        for description in SWITCH_TYPES
    ]

    if coordinator.is_wpm:
        # Add the circulation pump switch for WPM systems
        entities.append(
            StiebelEltronISGSwitch(
                coordinator,
                entry,
                StiebelEltronSwitchEntityDescription(
                    key=CIRCULATION_PUMP,
                    device_class=SwitchDeviceClass.SWITCH,
                    has_entity_name=True,
                    name="Circulation Pump",
                    modbus_register=WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP,
                ),
            )
        )

    async_add_devices(entities)


class StiebelEltronISGSwitch(StiebelEltronISGEntity, SwitchEntity):
    """stiebel_eltron_isg Sensor class."""

    def __init__(
        self,
        coordinator: StiebelEltronModbusDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
        description: StiebelEltronSwitchEntityDescription,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the switch."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        value = self.coordinator.get_register_value(self.modbus_register)
        if value is not None:
            return value != 0
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.modbus_register == WpmSystemStateRegisters.DHW_CIRCULATION_PUMP:
            # For the circulation pump, we need to set the value to 1 to turn it on
            await self.coordinator.write_register(
                WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP, 1
            )
        else:
            await self.coordinator.write_register(self.modbus_register, 1)
        await self.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        if self.modbus_register == WpmSystemStateRegisters.DHW_CIRCULATION_PUMP:
            # For the circulation pump, we need to set the value to 1 to turn it on
            await self.coordinator.write_register(
                WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP, 0
            )
        else:
            await self.coordinator.write_register(self.modbus_register, 0)
        await self.async_update()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if self.modbus_register in (
            WpmSystemStateRegisters.DHW_CIRCULATION_PUMP,
            EnergyManagementSettingsRegisters.SG_READY_INPUT_1,
            EnergyManagementSettingsRegisters.SG_READY_INPUT_2,
        ):
            if not self.coordinator.has_register_value(self.modbus_register):
                _LOGGER.debug(
                    "Switch %s should not be available because register %s is not available",
                    self.entity_description.key,
                    self.modbus_register,
                )
                return False
            return True
        return super().available
