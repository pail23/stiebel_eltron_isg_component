"""Binary sensor platform for stiebel_eltron_isg."""

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pystiebeleltron import IsgRegisters
from pystiebeleltron.lwz import (
    LwzSystemStateRegisters,
)
from pystiebeleltron.wpm import (
    WpmSystemStateRegisters,
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
from .data import StiebelEltronIsgIntegrationConfigEntry
from .entity import StiebelEltronISGEntity


@dataclass(frozen=True, kw_only=True)
class StiebelEltronBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: IsgRegisters
    bit_number: int = 0


WPM_BINARY_SENSOR_TYPES = [
    StiebelEltronBinarySensorEntityDescription(
        name="Pump HK1",
        key=PUMP_ON_HK1,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Pump HK2",
        key=PUMP_ON_HK2,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat-up Program",
        key=HEAT_UP_PROGRAM,
        icon="mdi:clock-outline",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="NHZ Stages Running",
        key=NHZ_STAGES_RUNNING,
        icon="mdi:fence-electric",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is heating",
        key=IS_HEATING,
        icon="mdi:heat-wave",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is heating boiler",
        key=IS_HEATING_WATER,
        icon="mdi:water-boiler",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Compressor",
        key=COMPRESSOR_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is in summer mode",
        key=IS_SUMMER_MODE,
        icon="mdi:weather-sunny",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=7,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is cooling",
        key=IS_COOLING,
        icon="mdi:snowflake",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=8,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Evaporator Defrost",
        key=EVAPORATOR_DEFROST,
        icon="mdi:snowflake-melt",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.OPERATING_STATUS,
        bit_number=9,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Power Off (EVU)",
        key=POWER_OFF,
        icon="mdi:power-off",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.POWER_OFF,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Error Status",
        key=ERROR_STATUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.FAULT_STATUS,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Cooling active",
        key=COOLING_MODE,
        icon="mdi:snowflake",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.COOLING_MODE,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heating circuit 1 pump",
        key=HEATING_CIRCUIT_1_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_1,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heating circuit 2 pump",
        key=HEATING_CIRCUIT_2_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_2,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heating circuit 3 pump",
        key=HEATING_CIRCUIT_3_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_3,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heating circuit 4 pump",
        key=HEATING_CIRCUIT_4_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_4,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heating circuit 5 pump",
        key=HEATING_CIRCUIT_5_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_5,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Buffer 1 charging pump",
        key=BUFFER_1_CHARGING_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Buffer 2 charging pump",
        key=BUFFER_2_CHARGING_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Buffer 3 charging pump",
        key=BUFFER_3_CHARGING_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Buffer 4 charging pump",
        key=BUFFER_4_CHARGING_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Buffer 5 charging pump",
        key=BUFFER_5_CHARGING_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Buffer 6 charging pump",
        key=BUFFER_6_CHARGING_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="DHW charging pump",
        key=DHW_CHARGING_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.DHW_CHARGING_PUMP,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Source pump",
        key=SOURCE_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.SOURCE_PUMP,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Diff. controller 1 pump",
        key=DIFF_CONTROLLER_1_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.DIFF_CONTROLLER_PUMP_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Diff. controller 2 pump",
        key=DIFF_CONTROLLER_2_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.DIFF_CONTROLLER_PUMP_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Pool primary pump",
        key=POOL_PRIMARY_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.POOL_PUMP_PRIMARY,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Pool secondary pump",
        key=POOL_SECONDARY_PUMP,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.POOL_PUMP_SECONDARY,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat pump 1 ON",
        key=HEAT_PUMP_1_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.COMPRESSOR_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat pump 2 ON",
        key=HEAT_PUMP_2_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.COMPRESSOR_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat pump 3 ON",
        key=HEAT_PUMP_3_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.COMPRESSOR_3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat pump 4 ON",
        key=HEAT_PUMP_4_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.COMPRESSOR_4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat pump 5 ON",
        key=HEAT_PUMP_5_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.COMPRESSOR_5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat pump 6 ON",
        key=HEAT_PUMP_6_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.COMPRESSOR_6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Second generator for DHW",
        key=SECOND_GENERATOR_DHW,
        icon="mdi:water-boiler",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.WE_2_DHW,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Second generator for heating",
        key=SECOND_GENERATOR_HEATING,
        icon="mdi:water-boiler",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.WE_2_HEATING,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer opening heating circuit 2",
        key=MIXER_OPEN_HTG_CIRCUIT_2,
        icon="mdi:valve-open",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_OPEN_HC2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer opening heating circuit 3",
        key=MIXER_OPEN_HTG_CIRCUIT_3,
        icon="mdi:valve-open",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_OPEN_HC3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer opening heating circuit 4",
        key=MIXER_OPEN_HTG_CIRCUIT_4,
        icon="mdi:valve-open",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_OPEN_HC4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer opening heating circuit 5",
        key=MIXER_OPEN_HTG_CIRCUIT_5,
        icon="mdi:valve-open",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_OPEN_HC5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer closing heating circuit 2",
        key=MIXER_CLOSE_HTG_CIRCUIT_2,
        icon="mdi:valve-closed",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_CLOSE_HC2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer closing heating circuit 3",
        key=MIXER_CLOSE_HTG_CIRCUIT_3,
        icon="mdi:valve-closed",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_CLOSE_HC3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer closing heating circuit 4",
        key=MIXER_CLOSE_HTG_CIRCUIT_4,
        icon="mdi:valve-closed",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_CLOSE_HC4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Mixer closing heating circuit 5",
        key=MIXER_CLOSE_HTG_CIRCUIT_5,
        icon="mdi:valve-closed",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.MIXER_CLOSE_HC5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Emergency heating 1",
        key=EMERGENCY_HEATING_1,
        icon="mdi:fence-electric",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.NHZ_1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Emergency heating 2",
        key=EMERGENCY_HEATING_2,
        icon="mdi:fence-electric",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.NHZ_2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Emergency heating 1 & 2",
        key=EMERGENCY_HEATING_1_2,
        icon="mdi:fence-electric",
        has_entity_name=True,
        modbus_register=WpmSystemStateRegisters.NHZ_1_2,
    ),
]

LWZ_BINARY_SENSOR_TYPES = [
    StiebelEltronBinarySensorEntityDescription(
        name="Switching Program Enabled",
        key=SWITCHING_PROGRAM_ENABLED,
        icon="mdi:clock-outline",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=0,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Compressor",
        key=COMPRESSOR_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=1,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is heating",
        key=IS_HEATING,
        icon="mdi:heat-wave",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=2,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is cooling",
        key=IS_COOLING,
        icon="mdi:snowflake",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=3,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is heating boiler",
        key=IS_HEATING_WATER,
        icon="mdi:water-boiler",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=4,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Electric Heating",
        key=ELECTRIC_REHEATING,
        icon="mdi:fence-electric",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=5,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Service",
        key=SERVICE,
        icon="mdi:account-wrench",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=6,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Power Off (EVU)",
        key=POWER_OFF,
        icon="mdi:power-off",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=7,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Filter",
        key=FILTER,
        icon="mdi:air-filter",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=8,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Ventilation",
        key=VENTILATION,
        icon="mdi:fan",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=9,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Pump HK1",
        key=PUMP_ON_HK1,
        icon="mdi:pump",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=10,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Evaporator Defrost",
        key=EVAPORATOR_DEFROST,
        icon="mdi:snowflake-melt",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=11,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Filter Extract Air",
        key=FILTER_EXTRACT_AIR,
        icon="mdi:air-filter",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=12,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Filter Ventilation Air",
        key=FILTER_VENTILATION_AIR,
        icon="mdi:air-filter",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=13,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Heat-up Program",
        key=HEAT_UP_PROGRAM,
        icon="mdi:clock-outline",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS,
        bit_number=14,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Error Status",
        key=ERROR_STATUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.FAULT_STATUS,
    ),
    StiebelEltronBinarySensorEntityDescription(
        name="Is in summer mode",
        key=IS_SUMMER_MODE,
        icon="mdi:weather-sunny",
        has_entity_name=True,
        modbus_register=LwzSystemStateRegisters.OPERATING_STATUS_2,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
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
        coordinator,
        config_entry,
        description: StiebelEltronBinarySensorEntityDescription,
    ):
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
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return (
            int(self.coordinator.get_register_value(self.modbus_register))
            & (1 << self.bit_number)
            != 0
        )
