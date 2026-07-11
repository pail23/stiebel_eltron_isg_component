"""Switch platform for stiebel_eltron_isg."""

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pystiebeleltron import __dict__ as pystiebeleltron_symbols, wpm as wpm_module

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)
from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
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

PARALLEL_UPDATES = 1


class _RegisterRef:
    def __init__(self, owner: str, name: str) -> None:
        self._owner = owner
        self.name = name


class _RegisterShim:
    def __init__(self, owner: str) -> None:
        self._owner = owner

    def __getattr__(self, name: str) -> Any:
        return _RegisterRef(self._owner, name)


IsgRegisters = pystiebeleltron_symbols.get("IsgRegisters", Any)
EnergyManagementSettingsRegisters = pystiebeleltron_symbols.get(
    "EnergyManagementSettingsRegisters",
    _RegisterShim("EnergyManagementSettingsRegisters"),
)
WpmSystemStateRegisters = getattr(
    wpm_module,
    "WpmSystemStateRegisters",
    _RegisterShim("WpmSystemStateRegisters"),
)


class WpmCirculationPumpRegisters:
    """Registers related to the circulation pump in the WPM system."""

    DHW_CIRCULATION_PUMP = 47012


@dataclass(frozen=True, kw_only=True)
class StiebelEltronSwitchEntityDescription(SwitchEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: Any


SWITCH_TYPES = [
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_ACTIVE,
        translation_key=SG_READY_ACTIVE,
        device_class=SwitchDeviceClass.SWITCH,
        modbus_register=EnergyManagementSettingsRegisters.SWITCH_SG_READY_ON_AND_OFF,
    ),
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_INPUT_1,
        translation_key=SG_READY_INPUT_1,
        device_class=SwitchDeviceClass.SWITCH,
        modbus_register=EnergyManagementSettingsRegisters.SG_READY_INPUT_1,
    ),
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_INPUT_2,
        translation_key=SG_READY_INPUT_2,
        device_class=SwitchDeviceClass.SWITCH,
        modbus_register=EnergyManagementSettingsRegisters.SG_READY_INPUT_2,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
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
                    translation_key=CIRCULATION_PUMP,
                    device_class=SwitchDeviceClass.SWITCH,
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
        value = self.coordinator.get_component_value(
            _component_name(self.modbus_register),
            _to_field_name(self.modbus_register),
            self.modbus_register,
        )
        if value is not None:
            return value != 0
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.modbus_register == WpmSystemStateRegisters.DHW_CIRCULATION_PUMP:
            # For the circulation pump, we need to set the value to 1 to turn it on
            await self.coordinator.write_component_value(
                _component_name(WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP),
                _to_field_name(WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP),
                1,
                WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP,
            )
        else:
            await self.coordinator.write_component_value(
                _component_name(self.modbus_register),
                _to_field_name(self.modbus_register),
                1,
                self.modbus_register,
            )
        await self.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        if self.modbus_register == WpmSystemStateRegisters.DHW_CIRCULATION_PUMP:
            # For the circulation pump, we need to set the value to 1 to turn it on
            await self.coordinator.write_component_value(
                _component_name(WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP),
                _to_field_name(WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP),
                0,
                WpmCirculationPumpRegisters.DHW_CIRCULATION_PUMP,
            )
        else:
            await self.coordinator.write_component_value(
                _component_name(self.modbus_register),
                _to_field_name(self.modbus_register),
                0,
                self.modbus_register,
            )
        await self.async_update()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if self.modbus_register in (
            WpmSystemStateRegisters.DHW_CIRCULATION_PUMP,
            EnergyManagementSettingsRegisters.SG_READY_INPUT_1,
            EnergyManagementSettingsRegisters.SG_READY_INPUT_2,
        ):
            try:
                has_value = self.coordinator.has_register_value(self.modbus_register)
            except NotImplementedError:
                has_value = (
                    self.coordinator.get_component_value(
                        _component_name(self.modbus_register),
                        _to_field_name(self.modbus_register),
                        self.modbus_register,
                    )
                    is not None
                )

            if not has_value:
                _LOGGER.debug(
                    "Switch %s should not be available because register %s is not available",
                    self.entity_description.key,
                    self.modbus_register,
                )
            return True
        return super().available


def _to_field_name(register: Any) -> str:
    """Convert old enum-style register names to component field names."""
    register_name = getattr(register, "name", str(register))
    return register_name.lower()


def _component_name(register: Any) -> str:
    """Resolve component name from register type name."""
    register_type_name = getattr(register, "_owner", type(register).__name__)

    if "EnergyManagementSettings" in register_type_name:
        return "energy_management_settings"
    if "SystemState" in register_type_name:
        return "system_state"
    return "system_parameters"
