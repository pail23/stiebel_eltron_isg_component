"""Sensor number for stiebel_eltron_isg."""

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)

from .const import (
    AREA_COOLING_TARGET_FLOW_TEMPERATURE,
    AREA_COOLING_TARGET_ROOM_TEMPERATURE,
    COMFORT_COOLING_TEMPERATURE_TARGET_HK1,
    COMFORT_COOLING_TEMPERATURE_TARGET_HK2,
    COMFORT_TEMPERATURE_TARGET_HK1,
    COMFORT_TEMPERATURE_TARGET_HK2,
    COMFORT_TEMPERATURE_TARGET_HK3,
    COMFORT_WATER_TEMPERATURE_TARGET,
    DOMAIN,
    DUALMODE_TEMPERATURE_HZG,
    DUALMODE_TEMPERATURE_WW,
    ECO_COOLING_TEMPERATURE_TARGET_HK1,
    ECO_COOLING_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK1,
    ECO_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK3,
    ECO_WATER_TEMPERATURE_TARGET,
    FAN_COOLING_TARGET_FLOW_TEMPERATURE,
    FAN_COOLING_TARGET_ROOM_TEMPERATURE,
    FAN_LEVEL_DAY,
    FAN_LEVEL_NIGHT,
    HEATING_CURVE_LOW_END_HK1,
    HEATING_CURVE_LOW_END_HK2,
    HEATING_CURVE_RISE_HK1,
    HEATING_CURVE_RISE_HK2,
    HEATING_CURVE_RISE_HK3,
)
from .data import StiebelEltronIsgIntegrationConfigEntry
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class StiebelEltronNumberEntityDescription(NumberEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: Any
    write_component: str = "system_parameters"
    write_field: str | None = None

    def __post_init__(self) -> None:
        """Ensure value references are lambda-based."""
        if callable(self.modbus_register):
            return

        raise TypeError("modbus_register must be a lambda expression")


NUMBER_TYPES_WPM = [
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK1,
        translation_key=COMFORT_TEMPERATURE_TARGET_HK1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.comfort_temperature_hk_1,
        write_field="comfort_temperature_hk_1",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK1,
        translation_key=ECO_TEMPERATURE_TARGET_HK1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.eco_temperature_hk_1,
        write_field="eco_temperature_hk_1",
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK2,
        translation_key=COMFORT_TEMPERATURE_TARGET_HK2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.comfort_temperature_hk_2,
        write_field="comfort_temperature_hk_2",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK2,
        translation_key=ECO_TEMPERATURE_TARGET_HK2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.eco_temperature_hk_2,
        write_field="eco_temperature_hk_2",
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK3,
        translation_key=COMFORT_TEMPERATURE_TARGET_HK3,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.comfort_temperature_hk_3,
        write_field="comfort_temperature_hk_3",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK3,
        translation_key=ECO_TEMPERATURE_TARGET_HK3,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.eco_temperature_hk_3,
        write_field="eco_temperature_hk_3",
    ),
    StiebelEltronNumberEntityDescription(
        key=DUALMODE_TEMPERATURE_HZG,
        translation_key=DUALMODE_TEMPERATURE_HZG,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-off",
        native_min_value=-20,
        native_max_value=40,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.dual_mode_temp_hzg,
        write_field="dual_mode_temp_hzg",
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_WATER_TEMPERATURE_TARGET,
        translation_key=COMFORT_WATER_TEMPERATURE_TARGET,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.comfort_temperature,
        write_field="comfort_temperature",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_WATER_TEMPERATURE_TARGET,
        translation_key=ECO_WATER_TEMPERATURE_TARGET,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.eco_temperature,
        write_field="eco_temperature",
    ),
    StiebelEltronNumberEntityDescription(
        key=DUALMODE_TEMPERATURE_WW,
        translation_key=DUALMODE_TEMPERATURE_WW,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-off",
        native_min_value=-20,
        native_max_value=40,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.dual_mode_temp_ww,
        write_field="dual_mode_temp_ww",
    ),
    StiebelEltronNumberEntityDescription(
        key=AREA_COOLING_TARGET_ROOM_TEMPERATURE,
        translation_key=AREA_COOLING_TARGET_ROOM_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=20,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.set_room_temperature_area,
        write_field="set_room_temperature_area",
    ),
    StiebelEltronNumberEntityDescription(
        key=AREA_COOLING_TARGET_FLOW_TEMPERATURE,
        translation_key=AREA_COOLING_TARGET_FLOW_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=7,
        native_max_value=25,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.set_flow_temperature_area,
        write_field="set_flow_temperature_area",
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_COOLING_TARGET_ROOM_TEMPERATURE,
        translation_key=FAN_COOLING_TARGET_ROOM_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=20,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.set_room_temperature_fan,
        write_field="set_room_temperature_fan",
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_COOLING_TARGET_FLOW_TEMPERATURE,
        translation_key=FAN_COOLING_TARGET_FLOW_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=7,
        native_max_value=25,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.set_flow_temperature_fan,
        write_field="set_flow_temperature_fan",
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK1,
        translation_key=HEATING_CURVE_RISE_HK1,
        icon="mdi:thermometer-chevron-up",
        native_min_value=0,
        native_max_value=3,
        native_step=0.01,
        modbus_register=lambda api: api.system_parameters.heating_curve_rise_hk_1,
        write_field="heating_curve_rise_hk_1",
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK2,
        translation_key=HEATING_CURVE_RISE_HK2,
        icon="mdi:thermometer-chevron-up",
        native_min_value=0,
        native_max_value=3,
        native_step=0.01,
        modbus_register=lambda api: api.system_parameters.heating_curve_rise_hk_2,
        write_field="heating_curve_rise_hk_2",
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK3,
        translation_key=HEATING_CURVE_RISE_HK3,
        icon="mdi:thermometer-chevron-up",
        native_min_value=0,
        native_max_value=3,
        native_step=0.01,
        modbus_register=lambda api: api.system_parameters.heating_curve_rise_hk_3,
        write_field="heating_curve_rise_hk_3",
    ),
]

NUMBER_TYPES_LWZ = [
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK1,
        translation_key=COMFORT_TEMPERATURE_TARGET_HK1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.room_temperature_day_hk1,
        write_field="room_temperature_day_hk1",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK1,
        translation_key=ECO_TEMPERATURE_TARGET_HK1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.room_temperature_night_hk1,
        write_field="room_temperature_night_hk1",
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK2,
        translation_key=COMFORT_TEMPERATURE_TARGET_HK2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.room_temperature_day_hk2,
        write_field="room_temperature_day_hk2",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK2,
        translation_key=ECO_TEMPERATURE_TARGET_HK2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.room_temperature_night_hk2,
        write_field="room_temperature_night_hk2",
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_WATER_TEMPERATURE_TARGET,
        translation_key=COMFORT_WATER_TEMPERATURE_TARGET,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.dhw_set_day,
        write_field="dhw_set_day",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_WATER_TEMPERATURE_TARGET,
        translation_key=ECO_WATER_TEMPERATURE_TARGET,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=lambda api: api.system_parameters.dhw_set_night,
        write_field="dhw_set_night",
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_LEVEL_DAY,
        translation_key=FAN_LEVEL_DAY,
        icon="mdi:fan",
        native_min_value=0,
        native_max_value=3,
        native_step=1,
        modbus_register=lambda api: api.system_parameters.day_stage,
        write_field="day_stage",
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_LEVEL_NIGHT,
        translation_key=FAN_LEVEL_NIGHT,
        icon="mdi:fan",
        native_min_value=0,
        native_max_value=3,
        native_step=1,
        modbus_register=lambda api: api.system_parameters.night_stage,
        write_field="night_stage",
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_COOLING_TEMPERATURE_TARGET_HK1,
        translation_key=COMFORT_COOLING_TEMPERATURE_TARGET_HK1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: (
            api.system_parameters.room_temperature_day_hk1_cooling
        ),
        write_field="room_temperature_day_hk1_cooling",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_COOLING_TEMPERATURE_TARGET_HK1,
        translation_key=ECO_COOLING_TEMPERATURE_TARGET_HK1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: (
            api.system_parameters.room_temperature_night_hk1_cooling
        ),
        write_field="room_temperature_night_hk1_cooling",
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_COOLING_TEMPERATURE_TARGET_HK2,
        translation_key=COMFORT_COOLING_TEMPERATURE_TARGET_HK2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: (
            api.system_parameters.room_temperature_day_hk2_cooling
        ),
        write_field="room_temperature_day_hk2_cooling",
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_COOLING_TEMPERATURE_TARGET_HK2,
        translation_key=ECO_COOLING_TEMPERATURE_TARGET_HK2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=lambda api: (
            api.system_parameters.room_temperature_night_hk2_cooling
        ),
        write_field="room_temperature_night_hk2_cooling",
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK1,
        translation_key=HEATING_CURVE_RISE_HK1,
        icon="mdi:chart-bell-curve-cumulative",
        native_min_value=0,
        native_max_value=5,
        native_step=0.01,
        modbus_register=lambda api: api.system_parameters.gradient_hk1,
        write_field="gradient_hk1",
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK2,
        translation_key=HEATING_CURVE_RISE_HK2,
        icon="mdi:chart-bell-curve-cumulative",
        native_min_value=0,
        native_max_value=5,
        native_step=0.01,
        modbus_register=lambda api: api.system_parameters.gradient_hk2,
        write_field="gradient_hk2",
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_LOW_END_HK1,
        translation_key=HEATING_CURVE_LOW_END_HK1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:chart-sankey",
        native_min_value=0,
        native_max_value=20,
        native_step=0.5,
        modbus_register=lambda api: api.system_parameters.low_end_hk1,
        write_field="low_end_hk1",
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_LOW_END_HK2,
        translation_key=HEATING_CURVE_LOW_END_HK2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:chart-sankey",
        native_min_value=0,
        native_max_value=20,
        native_step=0.5,
        modbus_register=lambda api: api.system_parameters.low_end_hk2,
        write_field="low_end_hk2",
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator = entry.runtime_data.coordinator

    entities = []
    if coordinator.is_wpm:
        entities = [
            StiebelEltronISGNumberEntity(
                coordinator,
                entry,
                description,
            )
            for description in NUMBER_TYPES_WPM
        ]
    else:
        entities = [
            StiebelEltronISGNumberEntity(
                coordinator,
                entry,
                description,
            )
            for description in NUMBER_TYPES_LWZ
        ]
    async_add_devices(entities)


class StiebelEltronISGNumberEntity(StiebelEltronISGEntity, NumberEntity):
    """stiebel_eltron_isg select class."""

    def __init__(
        self,
        coordinator: StiebelEltronModbusDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
        description: StiebelEltronNumberEntityDescription,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register
        self.write_component = description.write_component
        self.write_field = description.write_field

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the select entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if self.write_field is None:
            return

        await self.coordinator.write_component_value(
            self.write_component,
            self.write_field,
            value,
        )

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.get_value(self.modbus_register)
