"""Binary sensor platform for stiebel_eltron_isg."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pystiebeleltron import ControllerModel

from .const import (
    BUFFER_1_CHARGING_PUMP,
    BUFFER_2_CHARGING_PUMP,
    BUFFER_3_CHARGING_PUMP,
    BUFFER_4_CHARGING_PUMP,
    BUFFER_5_CHARGING_PUMP,
    BUFFER_6_CHARGING_PUMP,
    CIRCULATION_PUMP,
    COMPRESSOR_ON,
    COOLING_MODE,
    DHW_CHARGING_PUMP,
    DIFF_CONTROLLER_1_PUMP,
    DIFF_CONTROLLER_2_PUMP,
    ELECTRIC_REHEATING,
    EMERGENCY_HEATING_1,
    EMERGENCY_HEATING_1_2,
    EMERGENCY_HEATING_2,
    ERROR_STATUS,
    EVAPORATOR_DEFROST,
    FILTER,
    FILTER_EXTRACT_AIR,
    FILTER_VENTILATION_AIR,
    HEAT_PUMP_1_ON,
    HEAT_PUMP_2_ON,
    HEAT_PUMP_3_ON,
    HEAT_PUMP_4_ON,
    HEAT_PUMP_5_ON,
    HEAT_PUMP_6_ON,
    HEAT_UP_PROGRAM,
    HEATING_CIRCUIT_1_PUMP,
    HEATING_CIRCUIT_2_PUMP,
    HEATING_CIRCUIT_3_PUMP,
    HEATING_CIRCUIT_4_PUMP,
    HEATING_CIRCUIT_5_PUMP,
    IS_COOLING,
    IS_HEATING,
    IS_HEATING_WATER,
    IS_SUMMER_MODE,
    MIXER_CLOSE_HTG_CIRCUIT_2,
    MIXER_CLOSE_HTG_CIRCUIT_3,
    MIXER_CLOSE_HTG_CIRCUIT_4,
    MIXER_CLOSE_HTG_CIRCUIT_5,
    MIXER_OPEN_HTG_CIRCUIT_2,
    MIXER_OPEN_HTG_CIRCUIT_3,
    MIXER_OPEN_HTG_CIRCUIT_4,
    MIXER_OPEN_HTG_CIRCUIT_5,
    NHZ_STAGES_RUNNING,
    POOL_PRIMARY_PUMP,
    POOL_SECONDARY_PUMP,
    POWER_OFF,
    PUMP_ON_HK1,
    PUMP_ON_HK2,
    SECOND_GENERATOR_DHW,
    SECOND_GENERATOR_HEATING,
    SERVICE,
    SOURCE_PUMP,
    SWITCHING_PROGRAM_ENABLED,
    VENTILATION,
)
from .coordinator import (
    ControllerFamily,
    StiebelEltronConfigEntry,
    StiebelEltronDataCoordinator,
)
from .entity import StiebelEltronISGEntity, ValueAccessor

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class StiebelEltronBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: ValueAccessor
    bit_number: int = 0


def _state(
    key: str, field: str, bit_number: int = 0, **kwargs: Any
) -> StiebelEltronBinarySensorEntityDescription:
    """Describe one bit of a system state register."""
    return StiebelEltronBinarySensorEntityDescription(
        key=key,
        translation_key=key,
        modbus_register=lambda api: getattr(api.system_state, field),
        bit_number=bit_number,
        **kwargs,
    )


def _status_bits(*keys: str) -> list[StiebelEltronBinarySensorEntityDescription]:
    """Describe the operating status bits, in ascending order from bit 0."""
    return [
        _state(key, "operating_status", bit_number)
        for bit_number, key in enumerate(keys)
    ]


def _error_status() -> StiebelEltronBinarySensorEntityDescription:
    return _state(
        ERROR_STATUS,
        "fault_status",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    )


WPM_3I_BINARY_SENSOR_TYPES = [
    *_status_bits(
        PUMP_ON_HK1,
        PUMP_ON_HK2,
        HEAT_UP_PROGRAM,
        NHZ_STAGES_RUNNING,
        IS_HEATING,
        IS_HEATING_WATER,
        COMPRESSOR_ON,
        IS_SUMMER_MODE,
        IS_COOLING,
        EVAPORATOR_DEFROST,
    ),
    _state(POWER_OFF, "power_off"),
    _error_status(),
]


WPM_BINARY_SENSOR_TYPES = [
    *WPM_3I_BINARY_SENSOR_TYPES,
    *(
        _state(key, field)
        for key, field in (
            (COOLING_MODE, "cooling_mode"),
            (HEATING_CIRCUIT_1_PUMP, "heating_circuit_pump_1"),
            (HEATING_CIRCUIT_2_PUMP, "heating_circuit_pump_2"),
            (HEATING_CIRCUIT_3_PUMP, "heating_circuit_pump_3"),
            (HEATING_CIRCUIT_4_PUMP, "heating_circuit_pump_4"),
            (HEATING_CIRCUIT_5_PUMP, "heating_circuit_pump_5"),
            (BUFFER_1_CHARGING_PUMP, "buffer_charging_pump_1"),
            (BUFFER_2_CHARGING_PUMP, "buffer_charging_pump_2"),
            (BUFFER_3_CHARGING_PUMP, "buffer_charging_pump_3"),
            (BUFFER_4_CHARGING_PUMP, "buffer_charging_pump_4"),
            (BUFFER_5_CHARGING_PUMP, "buffer_charging_pump_5"),
            (BUFFER_6_CHARGING_PUMP, "buffer_charging_pump_6"),
            (DHW_CHARGING_PUMP, "dhw_charging_pump"),
            (SOURCE_PUMP, "source_pump"),
            (DIFF_CONTROLLER_1_PUMP, "diff_controller_pump_1"),
            (DIFF_CONTROLLER_2_PUMP, "diff_controller_pump_2"),
            (POOL_PRIMARY_PUMP, "pool_pump_primary"),
            (POOL_SECONDARY_PUMP, "pool_pump_secondary"),
            (HEAT_PUMP_1_ON, "compressor_1"),
            (HEAT_PUMP_2_ON, "compressor_2"),
            (HEAT_PUMP_3_ON, "compressor_3"),
            (HEAT_PUMP_4_ON, "compressor_4"),
            (HEAT_PUMP_5_ON, "compressor_5"),
            (HEAT_PUMP_6_ON, "compressor_6"),
            (SECOND_GENERATOR_DHW, "we_2_dhw"),
            (SECOND_GENERATOR_HEATING, "we_2_heating"),
            (MIXER_OPEN_HTG_CIRCUIT_2, "mixer_open_hc2"),
            (MIXER_OPEN_HTG_CIRCUIT_3, "mixer_open_hc3"),
            (MIXER_OPEN_HTG_CIRCUIT_4, "mixer_open_hc4"),
            (MIXER_OPEN_HTG_CIRCUIT_5, "mixer_open_hc5"),
            (MIXER_CLOSE_HTG_CIRCUIT_2, "mixer_close_hc2"),
            (MIXER_CLOSE_HTG_CIRCUIT_3, "mixer_close_hc3"),
            (MIXER_CLOSE_HTG_CIRCUIT_4, "mixer_close_hc4"),
            (MIXER_CLOSE_HTG_CIRCUIT_5, "mixer_close_hc5"),
            (EMERGENCY_HEATING_1, "nhz_1"),
            (EMERGENCY_HEATING_2, "nhz_2"),
            (EMERGENCY_HEATING_1_2, "nhz_1_2"),
        )
    ),
]

# Only WPMsystem and LWZ_R290 are confirmed to expose this system-state field,
# see #607. Do not widen the model gate without controller-specific evidence.
# pystiebeleltron exposes no matching writable WPM/LWZ parameter.
CIRCULATION_PUMP_BINARY_SENSOR_TYPES = [
    _state(
        CIRCULATION_PUMP,
        "dhw_circulation_pump",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
]


LWZ_BINARY_SENSOR_TYPES = [
    *_status_bits(
        SWITCHING_PROGRAM_ENABLED,
        COMPRESSOR_ON,
        IS_HEATING,
        IS_COOLING,
        IS_HEATING_WATER,
        ELECTRIC_REHEATING,
        SERVICE,
        POWER_OFF,
        FILTER,
        VENTILATION,
        PUMP_ON_HK1,
        EVAPORATOR_DEFROST,
        FILTER_EXTRACT_AIR,
        FILTER_VENTILATION_AIR,
        HEAT_UP_PROGRAM,
    ),
    _error_status(),
    _state(IS_SUMMER_MODE, "operating_status_2"),
]


_BINARY_SENSOR_TYPES = {
    ControllerFamily.WPM_3I: WPM_3I_BINARY_SENSOR_TYPES,
    ControllerFamily.WPM: WPM_BINARY_SENSOR_TYPES,
    ControllerFamily.LWZ: LWZ_BINARY_SENSOR_TYPES,
}


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = entry.runtime_data
    descriptions = list(_BINARY_SENSOR_TYPES[coordinator.family])
    if coordinator.model in (ControllerModel.LWZ_R290, ControllerModel.WPMsystem):
        descriptions.extend(CIRCULATION_PUMP_BINARY_SENSOR_TYPES)

    async_add_devices([
        StiebelEltronISGBinarySensor(coordinator, entry, description)
        for description in descriptions
    ])


class StiebelEltronISGBinarySensor(StiebelEltronISGEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register
        self.bit_number = description.bit_number

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        value = self.coordinator.get_value(self.modbus_register)
        if value is None:
            return False

        return int(value) & (1 << self.bit_number) != 0
