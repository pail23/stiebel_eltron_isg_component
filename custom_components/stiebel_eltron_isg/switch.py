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


@dataclass(frozen=True, kw_only=True)
class StiebelEltronSwitchEntityDescription(SwitchEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: Any
    write_component: str | None = None
    write_field: str | None = None

    def __post_init__(self) -> None:
        """Ensure value references are lambda-based."""
        if callable(self.modbus_register):
            return

        raise TypeError("modbus_register must be a lambda expression")


SWITCH_TYPES = [
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_ACTIVE,
        translation_key=SG_READY_ACTIVE,
        device_class=SwitchDeviceClass.SWITCH,
        modbus_register=lambda api: (
            api.energy_management_settings.switch_sg_ready_on_and_off
        ),
        write_component="energy_management_settings",
        write_field="switch_sg_ready_on_and_off",
    ),
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_INPUT_1,
        translation_key=SG_READY_INPUT_1,
        device_class=SwitchDeviceClass.SWITCH,
        modbus_register=lambda api: api.energy_management_settings.sg_ready_input_1,
        write_component="energy_management_settings",
        write_field="sg_ready_input_1",
    ),
    StiebelEltronSwitchEntityDescription(
        key=SG_READY_INPUT_2,
        translation_key=SG_READY_INPUT_2,
        device_class=SwitchDeviceClass.SWITCH,
        modbus_register=lambda api: api.energy_management_settings.sg_ready_input_2,
        write_component="energy_management_settings",
        write_field="sg_ready_input_2",
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
                    modbus_register=lambda api: api.system_state.dhw_circulation_pump,
                    write_component="system_state",
                    write_field="dhw_circulation_pump",
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
        self.write_component = description.write_component
        self.write_field = description.write_field

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the switch."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        value = self.coordinator.get_value(self.modbus_register)
        if value is not None:
            return value != 0
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.write_component is None or self.write_field is None:
            return

        await self.coordinator.write_component_value(
            self.write_component,
            self.write_field,
            1,
        )
        await self.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        if self.write_component is None or self.write_field is None:
            return

        await self.coordinator.write_component_value(
            self.write_component,
            self.write_field,
            0,
        )
        await self.async_update()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if self.entity_description.key in (
            CIRCULATION_PUMP,
            SG_READY_INPUT_1,
            SG_READY_INPUT_2,
        ):
            has_value = self.coordinator.has_value(self.modbus_register)

            if not has_value:
                _LOGGER.debug(
                    "Switch %s should not be available because register %s is not available",
                    self.entity_description.key,
                    self.entity_description.key,
                )
            return True
        return super().available
