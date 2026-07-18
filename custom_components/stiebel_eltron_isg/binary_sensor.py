"""Binary sensor platform for stiebel_eltron_isg."""

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronDataCoordinator,
)
from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)

from .const import (
    BUFFER_1_CHARGING_PUMP,
    BUFFER_2_CHARGING_PUMP,
    BUFFER_3_CHARGING_PUMP,
    BUFFER_4_CHARGING_PUMP,
    BUFFER_5_CHARGING_PUMP,
    BUFFER_6_CHARGING_PUMP,
    COMPRESSOR_ON,
    COOLING_MODE,
    DHW_CHARGING_PUMP,
    DIFF_CONTROLLER_1_PUMP,
    DIFF_CONTROLLER_2_PUMP,
    DOMAIN,
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
from .entity import StiebelEltronISGEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class StiebelEltronBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: Any
    bit_number: int = 0


WPM_BINARY_SENSOR_TYPES = [
    StiebelEltronBinarySensorEntityDescription(
        translation_key=PUMP_ON_HK1,
        key=PUMP_ON_HK1,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=PUMP_ON_HK2,
        key=PUMP_ON_HK2,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_UP_PROGRAM,
        key=HEAT_UP_PROGRAM,
        icon="mdi:clock-outline",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=NHZ_STAGES_RUNNING,
        key=NHZ_STAGES_RUNNING,
        icon="mdi:fence-electric",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_HEATING,
        key=IS_HEATING,
        icon="mdi:heat-wave",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_HEATING_WATER,
        key=IS_HEATING_WATER,
        icon="mdi:water-boiler",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=COMPRESSOR_ON,
        key=COMPRESSOR_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_SUMMER_MODE,
        key=IS_SUMMER_MODE,
        icon="mdi:weather-sunny",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=7,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_COOLING,
        key=IS_COOLING,
        icon="mdi:snowflake",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=8,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=EVAPORATOR_DEFROST,
        key=EVAPORATOR_DEFROST,
        icon="mdi:snowflake-melt",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=9,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=POWER_OFF,
        key=POWER_OFF,
        icon="mdi:power-off",
        modbus_register=lambda api: api.system_state.power_off,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=ERROR_STATUS,
        key=ERROR_STATUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
        modbus_register=lambda api: api.system_state.fault_status,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=COOLING_MODE,
        key=COOLING_MODE,
        icon="mdi:snowflake",
        modbus_register=lambda api: api.system_state.cooling_mode,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEATING_CIRCUIT_1_PUMP,
        key=HEATING_CIRCUIT_1_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.heating_circuit_pump_1,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEATING_CIRCUIT_2_PUMP,
        key=HEATING_CIRCUIT_2_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.heating_circuit_pump_2,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEATING_CIRCUIT_3_PUMP,
        key=HEATING_CIRCUIT_3_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.heating_circuit_pump_3,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEATING_CIRCUIT_4_PUMP,
        key=HEATING_CIRCUIT_4_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.heating_circuit_pump_4,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEATING_CIRCUIT_5_PUMP,
        key=HEATING_CIRCUIT_5_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.heating_circuit_pump_5,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=BUFFER_1_CHARGING_PUMP,
        key=BUFFER_1_CHARGING_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.buffer_charging_pump_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=BUFFER_2_CHARGING_PUMP,
        key=BUFFER_2_CHARGING_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.buffer_charging_pump_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=BUFFER_3_CHARGING_PUMP,
        key=BUFFER_3_CHARGING_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.buffer_charging_pump_3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=BUFFER_4_CHARGING_PUMP,
        key=BUFFER_4_CHARGING_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.buffer_charging_pump_4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=BUFFER_5_CHARGING_PUMP,
        key=BUFFER_5_CHARGING_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.buffer_charging_pump_5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=BUFFER_6_CHARGING_PUMP,
        key=BUFFER_6_CHARGING_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.buffer_charging_pump_6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=DHW_CHARGING_PUMP,
        key=DHW_CHARGING_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.dhw_charging_pump,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=SOURCE_PUMP,
        key=SOURCE_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.source_pump,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=DIFF_CONTROLLER_1_PUMP,
        key=DIFF_CONTROLLER_1_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.diff_controller_pump_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=DIFF_CONTROLLER_2_PUMP,
        key=DIFF_CONTROLLER_2_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.diff_controller_pump_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=POOL_PRIMARY_PUMP,
        key=POOL_PRIMARY_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.pool_pump_primary,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=POOL_SECONDARY_PUMP,
        key=POOL_SECONDARY_PUMP,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.pool_pump_secondary,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_PUMP_1_ON,
        key=HEAT_PUMP_1_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.compressor_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_PUMP_2_ON,
        key=HEAT_PUMP_2_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.compressor_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_PUMP_3_ON,
        key=HEAT_PUMP_3_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.compressor_3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_PUMP_4_ON,
        key=HEAT_PUMP_4_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.compressor_4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_PUMP_5_ON,
        key=HEAT_PUMP_5_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.compressor_5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_PUMP_6_ON,
        key=HEAT_PUMP_6_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.compressor_6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=SECOND_GENERATOR_DHW,
        key=SECOND_GENERATOR_DHW,
        icon="mdi:water-boiler",
        modbus_register=lambda api: api.system_state.we_2_dhw,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=SECOND_GENERATOR_HEATING,
        key=SECOND_GENERATOR_HEATING,
        icon="mdi:water-boiler",
        modbus_register=lambda api: api.system_state.we_2_heating,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_OPEN_HTG_CIRCUIT_2,
        key=MIXER_OPEN_HTG_CIRCUIT_2,
        icon="mdi:valve-open",
        modbus_register=lambda api: api.system_state.mixer_open_hc2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_OPEN_HTG_CIRCUIT_3,
        key=MIXER_OPEN_HTG_CIRCUIT_3,
        icon="mdi:valve-open",
        modbus_register=lambda api: api.system_state.mixer_open_hc3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_OPEN_HTG_CIRCUIT_4,
        key=MIXER_OPEN_HTG_CIRCUIT_4,
        icon="mdi:valve-open",
        modbus_register=lambda api: api.system_state.mixer_open_hc4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_OPEN_HTG_CIRCUIT_5,
        key=MIXER_OPEN_HTG_CIRCUIT_5,
        icon="mdi:valve-open",
        modbus_register=lambda api: api.system_state.mixer_open_hc5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_CLOSE_HTG_CIRCUIT_2,
        key=MIXER_CLOSE_HTG_CIRCUIT_2,
        icon="mdi:valve-closed",
        modbus_register=lambda api: api.system_state.mixer_close_hc2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_CLOSE_HTG_CIRCUIT_3,
        key=MIXER_CLOSE_HTG_CIRCUIT_3,
        icon="mdi:valve-closed",
        modbus_register=lambda api: api.system_state.mixer_close_hc3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_CLOSE_HTG_CIRCUIT_4,
        key=MIXER_CLOSE_HTG_CIRCUIT_4,
        icon="mdi:valve-closed",
        modbus_register=lambda api: api.system_state.mixer_close_hc4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=MIXER_CLOSE_HTG_CIRCUIT_5,
        key=MIXER_CLOSE_HTG_CIRCUIT_5,
        icon="mdi:valve-closed",
        modbus_register=lambda api: api.system_state.mixer_close_hc5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=EMERGENCY_HEATING_1,
        key=EMERGENCY_HEATING_1,
        icon="mdi:fence-electric",
        modbus_register=lambda api: api.system_state.nhz_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=EMERGENCY_HEATING_2,
        key=EMERGENCY_HEATING_2,
        icon="mdi:fence-electric",
        modbus_register=lambda api: api.system_state.nhz_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=EMERGENCY_HEATING_1_2,
        key=EMERGENCY_HEATING_1_2,
        icon="mdi:fence-electric",
        modbus_register=lambda api: api.system_state.nhz_1_2,
    ),
]

LWZ_BINARY_SENSOR_TYPES = [
    StiebelEltronBinarySensorEntityDescription(
        translation_key=SWITCHING_PROGRAM_ENABLED,
        key=SWITCHING_PROGRAM_ENABLED,
        icon="mdi:clock-outline",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=COMPRESSOR_ON,
        key=COMPRESSOR_ON,
        icon="mdi:heat-pump",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_HEATING,
        key=IS_HEATING,
        icon="mdi:heat-wave",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_COOLING,
        key=IS_COOLING,
        icon="mdi:snowflake",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_HEATING_WATER,
        key=IS_HEATING_WATER,
        icon="mdi:water-boiler",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=ELECTRIC_REHEATING,
        key=ELECTRIC_REHEATING,
        icon="mdi:fence-electric",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=SERVICE,
        key=SERVICE,
        icon="mdi:account-wrench",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=POWER_OFF,
        key=POWER_OFF,
        icon="mdi:power-off",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=7,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=FILTER,
        key=FILTER,
        icon="mdi:air-filter",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=8,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=VENTILATION,
        key=VENTILATION,
        icon="mdi:fan",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=9,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=PUMP_ON_HK1,
        key=PUMP_ON_HK1,
        icon="mdi:pump",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=10,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=EVAPORATOR_DEFROST,
        key=EVAPORATOR_DEFROST,
        icon="mdi:snowflake-melt",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=11,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=FILTER_EXTRACT_AIR,
        key=FILTER_EXTRACT_AIR,
        icon="mdi:air-filter",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=12,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=FILTER_VENTILATION_AIR,
        key=FILTER_VENTILATION_AIR,
        icon="mdi:air-filter",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=13,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=HEAT_UP_PROGRAM,
        key=HEAT_UP_PROGRAM,
        icon="mdi:clock-outline",
        modbus_register=lambda api: api.system_state.operating_status,
        bit_number=14,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=ERROR_STATUS,
        key=ERROR_STATUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
        modbus_register=lambda api: api.system_state.fault_status,
    ),
    StiebelEltronBinarySensorEntityDescription(
        translation_key=IS_SUMMER_MODE,
        key=IS_SUMMER_MODE,
        icon="mdi:weather-sunny",
        modbus_register=lambda api: api.system_state.operating_status_2,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = entry.runtime_data.coordinator

    if coordinator.is_wpm:
        entities = [
            StiebelEltronISGBinarySensor(
                coordinator,
                entry,
                description,
            )
            for description in WPM_BINARY_SENSOR_TYPES
        ]
    else:
        entities = [
            StiebelEltronISGBinarySensor(
                coordinator,
                entry,
                description,
            )
            for description in LWZ_BINARY_SENSOR_TYPES
        ]
    async_add_devices(entities)


class StiebelEltronISGBinarySensor(StiebelEltronISGEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
        description: StiebelEltronBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register
        self.bit_number = description.bit_number

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        value = self.coordinator.get_value(self.modbus_register)
        if value is None:
            return False

        return int(value) & (1 << self.bit_number) != 0
