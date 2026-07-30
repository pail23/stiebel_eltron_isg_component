"""Sensor platform for stiebel_eltron_isg."""

from collections.abc import Callable
from dataclasses import dataclass
import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util
from pystiebeleltron import ControllerModel

from .const import (
    ACTIVE_ERROR,
    ACTUAL_HUMIDITY,
    ACTUAL_HUMIDITY_HK1,
    ACTUAL_HUMIDITY_HK2,
    ACTUAL_HUMIDITY_HK3,
    ACTUAL_ROOM_TEMPERATURE_HK1,
    ACTUAL_ROOM_TEMPERATURE_HK2,
    ACTUAL_ROOM_TEMPERATURE_HK3,
    ACTUAL_TEMPERATURE,
    ACTUAL_TEMPERATURE_BUFFER,
    ACTUAL_TEMPERATURE_COOLING_FANCOIL,
    ACTUAL_TEMPERATURE_COOLING_SURFACE,
    ACTUAL_TEMPERATURE_FEK,
    ACTUAL_TEMPERATURE_HK1,
    ACTUAL_TEMPERATURE_HK2,
    ACTUAL_TEMPERATURE_HK3,
    ACTUAL_TEMPERATURE_WATER,
    COMPRESSOR_HEATING,
    COMPRESSOR_HEATING_WATER,
    COMPRESSOR_SPEED,
    COMPRESSOR_STARTS,
    CONSUMED_COOLING_12M,
    CONSUMED_COOLING_LAST_24H,
    CONSUMED_COOLING_PREV_12M,
    CONSUMED_HEATING,
    CONSUMED_HEATING_12M,
    CONSUMED_HEATING_LAST_24H,
    CONSUMED_HEATING_PREV_12M,
    CONSUMED_HEATING_TODAY,
    CONSUMED_HEATING_TOTAL,
    CONSUMED_WATER_HEATING,
    CONSUMED_WATER_HEATING_12M,
    CONSUMED_WATER_HEATING_LAST_24H,
    CONSUMED_WATER_HEATING_PREV_12M,
    CONSUMED_WATER_HEATING_TODAY,
    CONSUMED_WATER_HEATING_TOTAL,
    COOLING_RUNTIME,
    CURRENT_POWER_CONSUMPTION,
    DEWPOINT_TEMPERATURE,
    DEWPOINT_TEMPERATURE_HK1,
    DEWPOINT_TEMPERATURE_HK2,
    DEWPOINT_TEMPERATURE_HK3,
    ELECTRICAL_BOOSTER_HEATING,
    ELECTRICAL_BOOSTER_HEATING_WATER,
    EXTRACT_AIR_ACTUAL_FAN_SPEED,
    EXTRACT_AIR_DEW_POINT,
    EXTRACT_AIR_HUMIDITY,
    EXTRACT_AIR_TARGET_FLOW_RATE,
    EXTRACT_AIR_TEMPERATURE,
    FLOW_TEMPERATURE,
    FLOW_TEMPERATURE_NHZ,
    FLOW_TEMPERATURE_WP,
    FLOW_TEMPERATURE_WP1,
    FLOW_TEMPERATURE_WP2,
    HEATER_PRESSURE,
    HIGH_PRESSURE,
    HIGH_PRESSURE_WP1,
    HIGH_PRESSURE_WP2,
    HOT_GAS_TEMPERATURE,
    HOT_GAS_TEMPERATURE_WP1,
    HOT_GAS_TEMPERATURE_WP2,
    LOW_PRESSURE,
    LOW_PRESSURE_WP1,
    LOW_PRESSURE_WP2,
    MIN_SOURCE_TEMPERATURE,
    OUTDOOR_TEMPERATURE,
    PRODUCED_ELECTRICAL_BOOSTER_HEATING_TOTAL,
    PRODUCED_ELECTRICAL_BOOSTER_WATER_HEATING_TOTAL,
    PRODUCED_HEATING,
    PRODUCED_HEATING_TODAY,
    PRODUCED_HEATING_TOTAL,
    PRODUCED_RECOVERY,
    PRODUCED_RECOVERY_TODAY,
    PRODUCED_RECOVERY_TOTAL,
    PRODUCED_SOLAR_HEATING,
    PRODUCED_SOLAR_HEATING_TODAY,
    PRODUCED_SOLAR_HEATING_TOTAL,
    PRODUCED_SOLAR_WATER_HEATING,
    PRODUCED_SOLAR_WATER_HEATING_TODAY,
    PRODUCED_SOLAR_WATER_HEATING_TOTAL,
    PRODUCED_WATER_HEATING,
    PRODUCED_WATER_HEATING_TODAY,
    PRODUCED_WATER_HEATING_TOTAL,
    RETURN_TEMPERATURE,
    RETURN_TEMPERATURE_WP1,
    RETURN_TEMPERATURE_WP2,
    SG_READY_STATE,
    SOLAR_COLLECTOR_TEMPERATURE,
    SOLAR_CYLINDER_TEMPERATURE,
    SOLAR_RUNTIME,
    SOURCE_PRESSURE,
    SOURCE_TEMPERATURE,
    TARGET_ROOM_TEMPERATURE_HK1,
    TARGET_ROOM_TEMPERATURE_HK2,
    TARGET_ROOM_TEMPERATURE_HK3,
    TARGET_TEMPERATURE,
    TARGET_TEMPERATURE_BUFFER,
    TARGET_TEMPERATURE_COOLING_FANCOIL,
    TARGET_TEMPERATURE_COOLING_SURFACE,
    TARGET_TEMPERATURE_FEK,
    TARGET_TEMPERATURE_HK1,
    TARGET_TEMPERATURE_HK2,
    TARGET_TEMPERATURE_HK3,
    TARGET_TEMPERATURE_WATER,
    VENTILATION_AIR_ACTUAL_FAN_SPEED,
    VENTILATION_AIR_TARGET_FLOW_RATE,
    VOLUME_STREAM,
    VOLUME_STREAM_WP1,
    VOLUME_STREAM_WP2,
)
from .coordinator import StiebelEltronConfigEntry, StiebelEltronDataCoordinator
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

type StiebelEltronModbusRegister = Callable[[Any], int | float | None]


@dataclass(frozen=True, kw_only=True)
class StiebelEltronSensorEntityDescription(SensorEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: StiebelEltronModbusRegister

    def __post_init__(self) -> None:
        """Ensure value references are lambda-based."""
        if callable(self.modbus_register):
            return

        raise TypeError("modbus_register must be a lambda expression")


def create_temperature_entity_description(
    key: str, modbus_register: StiebelEltronModbusRegister
) -> StiebelEltronSensorEntityDescription:
    """Create an entry description for a temperature sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        modbus_register=modbus_register,
    )


def create_energy_entity_description(
    key: str,
    modbus_register: StiebelEltronModbusRegister,
    visible_default: bool = True,
) -> StiebelEltronSensorEntityDescription:
    """Create an entry description for a energy sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=visible_default,
        modbus_register=modbus_register,
    )


def create_power_consumption_entity_description(
    key: str,
    modbus_register: StiebelEltronModbusRegister,
    native_unit: UnitOfEnergy = UnitOfEnergy.KILO_WATT_HOUR,
) -> StiebelEltronSensorEntityDescription:
    """Create a sensor for one Servicewelt "POWER CONSUMPTION" window.

    The state class is a placeholder. Whether a window rolls continuously or
    resets to zero is not established, and the two cases want different classes:
    a reset-to-zero counter is what ``TOTAL_INCREASING`` is for, while a rolling
    sum suits neither, since its long-term sum statistic would just drift. Until
    someone samples a real machine over a day, ``TOTAL`` stays as the least bad
    option. The presence of a "previous 12 months" register suggests these are
    bucketed rolling sums rather than daily counters.

    The unit is selected per window: the library sums each register pair as
    ``low + high * 1000``, so the result carries the smaller of the two units
    Servicewelt displays. The 24 h windows therefore come out in Wh and pass
    ``native_unit`` explicitly, while the 12-month windows are kWh and use the
    default.
    """
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=native_unit,
        state_class=SensorStateClass.TOTAL,
        device_class=SensorDeviceClass.ENERGY,
        modbus_register=modbus_register,
    )


def create_daily_energy_entity_description(
    key: str,
    modbus_register: StiebelEltronModbusRegister,
    visible_default: bool = True,
) -> StiebelEltronSensorEntityDescription:
    """Create an entry description for a energy sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=visible_default,
        modbus_register=modbus_register,
    )


def create_humidity_entity_description(
    key: str, modbus_register: StiebelEltronModbusRegister
) -> StiebelEltronSensorEntityDescription:
    """Create an entry description for a humidity sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.HUMIDITY,
        modbus_register=modbus_register,
    )


def create_pressure_entity_description(
    key: str, modbus_register: StiebelEltronModbusRegister
) -> StiebelEltronSensorEntityDescription:
    """Create an entry description for a pressure sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
        modbus_register=modbus_register,
    )


def create_volume_stream_entity_description(
    key: str, modbus_register: StiebelEltronModbusRegister
) -> StiebelEltronSensorEntityDescription:
    """Create an entry description for a volume stream sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        modbus_register=modbus_register,
    )


def create_runtime_entity_description(
    key: str, modbus_register: StiebelEltronModbusRegister
) -> StiebelEltronSensorEntityDescription:
    """Create an entry description for an operating-duration sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        translation_key=key,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
        modbus_register=modbus_register,
    )


WPM_3I_SYSTEM_VALUES_SENSOR_TYPES = [
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE,
        lambda api: api.system_values.actual_temperature_fe7,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE,
        lambda api: api.system_values.set_temperature_fe7,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_FEK,
        lambda api: api.system_values.actual_temperature_fek,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_FEK,
        lambda api: api.system_values.set_temperature_fek,
    ),
    create_humidity_entity_description(
        ACTUAL_HUMIDITY, lambda api: api.system_values.relative_humidity
    ),
    create_temperature_entity_description(
        DEWPOINT_TEMPERATURE,
        lambda api: api.system_values.dew_point_temperature,
    ),
    create_temperature_entity_description(
        OUTDOOR_TEMPERATURE,
        lambda api: api.system_values.outside_temperature,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_HK1,
        lambda api: api.system_values.actual_temperature_hk_1,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_HK1,
        lambda api: api.system_values.set_temperature_hk_1,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_HK2,
        lambda api: api.system_values.actual_temperature_hk_2,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_HK2,
        lambda api: api.system_values.set_temperature_hk_2,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE_WP,
        lambda api: api.system_values.actual_flow_temperature_wp,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE_NHZ,
        lambda api: api.system_values.actual_flow_temperature_nhz,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE,
        lambda api: api.system_values.actual_flow_temperature,
    ),
    create_temperature_entity_description(
        RETURN_TEMPERATURE,
        lambda api: api.system_values.actual_return_temperature,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_BUFFER,
        lambda api: api.system_values.actual_buffer_temperature,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_BUFFER,
        lambda api: api.system_values.set_buffer_temperature,
    ),
    create_pressure_entity_description(
        HEATER_PRESSURE,
        lambda api: api.system_values.heating_pressure,
    ),
    create_volume_stream_entity_description(
        VOLUME_STREAM, lambda api: api.system_values.flow_rate
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_WATER,
        lambda api: api.system_values.actual_temperature_dhw,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_WATER,
        lambda api: api.system_values.set_temperature_dhw,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_COOLING_FANCOIL,
        lambda api: api.system_values.actual_temperature_fan,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_COOLING_FANCOIL,
        lambda api: api.system_values.set_temperature_fan,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_COOLING_SURFACE,
        lambda api: api.system_values.actual_temperature_area,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_COOLING_SURFACE,
        lambda api: api.system_values.set_temperature_area,
    ),
    create_temperature_entity_description(
        SOURCE_TEMPERATURE,
        lambda api: api.system_values.source_temperature,
    ),
    create_temperature_entity_description(
        MIN_SOURCE_TEMPERATURE,
        lambda api: api.system_values.min_source_temperature,
    ),
    create_pressure_entity_description(
        SOURCE_PRESSURE,
        lambda api: api.system_values.source_pressure,
    ),
    create_temperature_entity_description(
        HOT_GAS_TEMPERATURE,
        lambda api: api.system_values.hot_gas_temperature,
    ),
    create_pressure_entity_description(
        HIGH_PRESSURE, lambda api: api.system_values.high_pressure
    ),
    create_pressure_entity_description(
        LOW_PRESSURE, lambda api: api.system_values.low_pressure
    ),
    StiebelEltronSensorEntityDescription(
        key=ACTIVE_ERROR,
        translation_key=ACTIVE_ERROR,
        entity_category=EntityCategory.DIAGNOSTIC,
        modbus_register=lambda api: api.system_state.active_error,
    ),
]

SYSTEM_VALUES_SENSOR_TYPES = [
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE,
        lambda api: api.system_values.actual_temperature_fe7,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE,
        lambda api: api.system_values.set_temperature_fe7,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_FEK,
        lambda api: api.system_values.actual_temperature_fek,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_FEK,
        lambda api: api.system_values.set_temperature_fek,
    ),
    create_humidity_entity_description(
        ACTUAL_HUMIDITY, lambda api: api.system_values.relative_humidity
    ),
    create_humidity_entity_description(
        ACTUAL_HUMIDITY_HK1,
        lambda api: api.system_values.room_temperatures[0].relative_humidity,
    ),
    create_humidity_entity_description(
        ACTUAL_HUMIDITY_HK2,
        lambda api: api.system_values.room_temperatures[1].relative_humidity,
    ),
    create_humidity_entity_description(
        ACTUAL_HUMIDITY_HK3,
        lambda api: api.system_values.room_temperatures[2].relative_humidity,
    ),
    create_temperature_entity_description(
        DEWPOINT_TEMPERATURE,
        lambda api: api.system_values.dew_point_temperature,
    ),
    create_temperature_entity_description(
        DEWPOINT_TEMPERATURE_HK1,
        lambda api: api.system_values.room_temperatures[0].dew_point_temperature,
    ),
    create_temperature_entity_description(
        DEWPOINT_TEMPERATURE_HK2,
        lambda api: api.system_values.room_temperatures[1].dew_point_temperature,
    ),
    create_temperature_entity_description(
        DEWPOINT_TEMPERATURE_HK3,
        lambda api: api.system_values.room_temperatures[2].dew_point_temperature,
    ),
    create_temperature_entity_description(
        OUTDOOR_TEMPERATURE,
        lambda api: api.system_values.outside_temperature,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_HK1,
        lambda api: api.system_values.actual_temperature_hk_1,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_HK1,
        lambda api: api.system_values.set_temperature_hk_1,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_HK2,
        lambda api: api.system_values.actual_temperature_hk_2,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_HK2,
        lambda api: api.system_values.set_temperature_hk_2,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_HK3,
        lambda api: api.system_values.actual_temperature_hk_3,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_HK3,
        lambda api: api.system_values.set_temperature_hk_3,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_COOLING_FANCOIL,
        lambda api: api.system_values.actual_temperature_fan,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_COOLING_FANCOIL,
        lambda api: api.system_values.set_temperature_fan,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_COOLING_SURFACE,
        lambda api: api.system_values.actual_temperature_area,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_COOLING_SURFACE,
        lambda api: api.system_values.set_temperature_area,
    ),
    create_temperature_entity_description(
        SOLAR_CYLINDER_TEMPERATURE,
        lambda api: api.system_values.cylinder_temperature,
    ),
    create_runtime_entity_description(
        SOLAR_RUNTIME,
        lambda api: api.system_values.runtime,
    ),
    create_temperature_entity_description(
        ACTUAL_ROOM_TEMPERATURE_HK1,
        lambda api: api.system_values.room_temperatures[0].actual_temperature,
    ),
    create_temperature_entity_description(
        TARGET_ROOM_TEMPERATURE_HK1,
        lambda api: api.system_values.room_temperatures[0].set_temperature,
    ),
    create_temperature_entity_description(
        ACTUAL_ROOM_TEMPERATURE_HK2,
        lambda api: api.system_values.room_temperatures[1].actual_temperature,
    ),
    create_temperature_entity_description(
        TARGET_ROOM_TEMPERATURE_HK2,
        lambda api: api.system_values.room_temperatures[1].set_temperature,
    ),
    create_temperature_entity_description(
        ACTUAL_ROOM_TEMPERATURE_HK3,
        lambda api: api.system_values.room_temperatures[2].actual_temperature,
    ),
    create_temperature_entity_description(
        TARGET_ROOM_TEMPERATURE_HK3,
        lambda api: api.system_values.room_temperatures[2].set_temperature,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE_WP,
        lambda api: api.system_values.actual_flow_temperature_wp,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE_NHZ,
        lambda api: api.system_values.actual_flow_temperature_nhz,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE,
        lambda api: api.system_values.actual_flow_temperature,
    ),
    create_temperature_entity_description(
        RETURN_TEMPERATURE,
        lambda api: api.system_values.actual_return_temperature,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_BUFFER,
        lambda api: api.system_values.actual_buffer_temperature,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_BUFFER,
        lambda api: api.system_values.set_buffer_temperature,
    ),
    create_pressure_entity_description(
        HEATER_PRESSURE,
        lambda api: api.system_values.heating_pressure,
    ),
    create_volume_stream_entity_description(
        VOLUME_STREAM, lambda api: api.system_values.flow_rate
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_WATER,
        lambda api: api.system_values.actual_temperature_dhw,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_WATER,
        lambda api: api.system_values.set_temperature_dhw,
    ),
    create_temperature_entity_description(
        SOLAR_COLLECTOR_TEMPERATURE,
        lambda api: api.system_values.collector_temperature,
    ),
    create_temperature_entity_description(
        SOURCE_TEMPERATURE,
        lambda api: api.system_values.source_temperature,
    ),
    create_temperature_entity_description(
        MIN_SOURCE_TEMPERATURE,
        lambda api: api.system_values.min_source_temperature,
    ),
    create_pressure_entity_description(
        SOURCE_PRESSURE,
        lambda api: api.system_values.source_pressure,
    ),
    create_temperature_entity_description(
        HOT_GAS_TEMPERATURE,
        lambda api: api.system_values.hot_gas_temperature,
    ),
    create_pressure_entity_description(
        HIGH_PRESSURE, lambda api: api.system_values.high_pressure
    ),
    create_pressure_entity_description(
        LOW_PRESSURE, lambda api: api.system_values.low_pressure
    ),
    create_temperature_entity_description(
        RETURN_TEMPERATURE_WP1,
        lambda api: api.system_values.heat_pumps[0].return_temperature,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE_WP1,
        lambda api: api.system_values.heat_pumps[0].flow_temperature,
    ),
    create_temperature_entity_description(
        HOT_GAS_TEMPERATURE_WP1,
        lambda api: api.system_values.heat_pumps[0].hot_gas_temperature,
    ),
    create_pressure_entity_description(
        LOW_PRESSURE_WP1,
        lambda api: api.system_values.heat_pumps[0].low_pressure,
    ),
    create_pressure_entity_description(
        HIGH_PRESSURE_WP1,
        lambda api: api.system_values.heat_pumps[0].high_pressure,
    ),
    create_volume_stream_entity_description(
        VOLUME_STREAM_WP1,
        lambda api: api.system_values.heat_pumps[0].wp_water_flow_rate,
    ),
    create_temperature_entity_description(
        RETURN_TEMPERATURE_WP2,
        lambda api: api.system_values.heat_pumps[1].return_temperature,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE_WP2,
        lambda api: api.system_values.heat_pumps[1].flow_temperature,
    ),
    create_temperature_entity_description(
        HOT_GAS_TEMPERATURE_WP2,
        lambda api: api.system_values.heat_pumps[1].hot_gas_temperature,
    ),
    create_pressure_entity_description(
        LOW_PRESSURE_WP2,
        lambda api: api.system_values.heat_pumps[1].low_pressure,
    ),
    create_pressure_entity_description(
        HIGH_PRESSURE_WP2,
        lambda api: api.system_values.heat_pumps[1].high_pressure,
    ),
    create_volume_stream_entity_description(
        VOLUME_STREAM_WP2,
        lambda api: api.system_values.heat_pumps[1].wp_water_flow_rate,
    ),
    StiebelEltronSensorEntityDescription(
        key=ACTIVE_ERROR,
        translation_key=ACTIVE_ERROR,
        entity_category=EntityCategory.DIAGNOSTIC,
        modbus_register=lambda api: api.system_state.active_error,
    ),
]

LWZ_SYSTEM_VALUES_SENSOR_TYPES = [
    create_temperature_entity_description(
        ACTUAL_ROOM_TEMPERATURE_HK1,
        lambda api: api.system_values.actual_room_t_hc1,
    ),
    create_temperature_entity_description(
        TARGET_ROOM_TEMPERATURE_HK1,
        lambda api: api.system_values.set_room_temperature_hc1,
    ),
    create_temperature_entity_description(
        ACTUAL_ROOM_TEMPERATURE_HK2,
        lambda api: api.system_values.actual_room_t_hc2,
    ),
    create_temperature_entity_description(
        TARGET_ROOM_TEMPERATURE_HK2,
        lambda api: api.system_values.set_room_temperature_hc2,
    ),
    create_humidity_entity_description(
        ACTUAL_HUMIDITY,
        lambda api: api.system_values.relative_humidity_hc1,
    ),
    create_humidity_entity_description(
        ACTUAL_HUMIDITY_HK2,
        lambda api: api.system_values.relative_humidity_hc2,
    ),
    create_temperature_entity_description(
        DEWPOINT_TEMPERATURE_HK1,
        lambda api: api.system_values.dew_point_temp_hc1,
    ),
    create_temperature_entity_description(
        DEWPOINT_TEMPERATURE_HK2,
        lambda api: api.system_values.dew_point_temp_hc2,
    ),
    create_temperature_entity_description(
        OUTDOOR_TEMPERATURE,
        lambda api: api.system_values.outside_temperature,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_HK1,
        lambda api: api.system_values.actual_value_hc1,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_HK1,
        lambda api: api.system_values.set_value_hc1,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_HK2,
        lambda api: api.system_values.actual_value_hc2,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_HK2,
        lambda api: api.system_values.set_value_hc2,
    ),
    create_temperature_entity_description(
        FLOW_TEMPERATURE,
        lambda api: api.system_values.flow_temperature,
    ),
    create_temperature_entity_description(
        RETURN_TEMPERATURE,
        lambda api: api.system_values.return_temperature,
    ),
    create_volume_stream_entity_description(
        VOLUME_STREAM, lambda api: api.system_values.flow_rate
    ),
    create_pressure_entity_description(
        HEATER_PRESSURE,
        lambda api: api.system_values.pressure_htg_circ,
    ),
    create_temperature_entity_description(
        ACTUAL_TEMPERATURE_WATER,
        lambda api: api.system_values.actual_dhw_t,
    ),
    create_temperature_entity_description(
        TARGET_TEMPERATURE_WATER,
        lambda api: api.system_values.dhw_set_temperature,
    ),
    create_temperature_entity_description(
        SOLAR_COLLECTOR_TEMPERATURE,
        lambda api: api.system_values.collector_temperature,
    ),
    create_temperature_entity_description(
        HOT_GAS_TEMPERATURE,
        lambda api: api.system_values.hot_gas_temperature,
    ),
    create_pressure_entity_description(
        HIGH_PRESSURE, lambda api: api.system_values.high_pressure
    ),
    create_pressure_entity_description(
        LOW_PRESSURE, lambda api: api.system_values.low_pressure
    ),
]


ENERGYMANAGEMENT_SENSOR_TYPES = [
    StiebelEltronSensorEntityDescription(
        key=SG_READY_STATE,
        translation_key=SG_READY_STATE,
        modbus_register=lambda api: (
            api.energy_system_information.sg_ready_operating_state
        ),
    ),
]

ENERGY_SENSOR_TYPES = [
    create_energy_entity_description(
        PRODUCED_HEATING_TOTAL,
        lambda api: api.energy_data.vd_heating_total,
    ),
    create_energy_entity_description(
        PRODUCED_HEATING,
        lambda api: api.energy_data.vd_heating_day_and_total,
    ),
    create_energy_entity_description(
        PRODUCED_WATER_HEATING_TOTAL,
        lambda api: api.energy_data.vd_dhw_total,
    ),
    create_energy_entity_description(
        PRODUCED_WATER_HEATING,
        lambda api: api.energy_data.vd_dhw_day_and_total,
    ),
    create_energy_entity_description(
        CONSUMED_HEATING_TOTAL,
        lambda api: api.energy_data.vd_heating_total_consumed,
    ),
    create_energy_entity_description(
        CONSUMED_HEATING,
        lambda api: api.energy_data.vd_heating_day_and_total_consumed,
    ),
    create_energy_entity_description(
        CONSUMED_WATER_HEATING_TOTAL,
        lambda api: api.energy_data.vd_dhw_total_consumed,
    ),
    create_energy_entity_description(
        CONSUMED_WATER_HEATING,
        lambda api: api.energy_data.vd_dhw_day_and_total_consumed,
    ),
    create_energy_entity_description(
        PRODUCED_ELECTRICAL_BOOSTER_HEATING_TOTAL,
        lambda api: api.energy_data.nhz_heating_total,
    ),
    create_energy_entity_description(
        PRODUCED_ELECTRICAL_BOOSTER_WATER_HEATING_TOTAL,
        lambda api: api.energy_data.nhz_dhw_total,
    ),
]

LWZ_ENERGY_SENSOR_TYPES = [
    create_energy_entity_description(
        PRODUCED_HEATING_TOTAL,
        lambda api: api.energy_data.heat_meter_htg_ttl,
    ),
    create_energy_entity_description(
        PRODUCED_HEATING,
        lambda api: api.energy_data.heat_meter_htg_day_and_total,
    ),
    create_energy_entity_description(
        PRODUCED_WATER_HEATING_TOTAL,
        lambda api: api.energy_data.heat_meter_dhw_ttl,
    ),
    create_energy_entity_description(
        PRODUCED_WATER_HEATING,
        lambda api: api.energy_data.heat_meter_dhw_day_and_total,
    ),
    create_energy_entity_description(
        CONSUMED_HEATING_TOTAL,
        lambda api: api.energy_data.pwr_con_htg_ttl,
    ),
    create_energy_entity_description(
        CONSUMED_HEATING,
        lambda api: api.energy_data.pwr_con_htg_day_and_total,
    ),
    create_energy_entity_description(
        CONSUMED_WATER_HEATING_TOTAL,
        lambda api: api.energy_data.pwr_con_dhw_ttl,
    ),
    create_energy_entity_description(
        CONSUMED_WATER_HEATING,
        lambda api: api.energy_data.pwr_con_dhw_day_and_total,
    ),
    create_energy_entity_description(
        PRODUCED_ELECTRICAL_BOOSTER_HEATING_TOTAL,
        lambda api: api.energy_data.heat_m_boost_htg_ttl,
    ),
    create_energy_entity_description(
        PRODUCED_ELECTRICAL_BOOSTER_WATER_HEATING_TOTAL,
        lambda api: api.energy_data.heat_m_boost_dhw_ttl,
    ),
    create_energy_entity_description(
        PRODUCED_RECOVERY,
        lambda api: api.energy_data.heat_m_recovery_day_and_total,
    ),
    create_energy_entity_description(
        PRODUCED_RECOVERY_TOTAL,
        lambda api: api.energy_data.heat_m_recovery_ttl,
    ),
    create_energy_entity_description(
        PRODUCED_SOLAR_HEATING,
        lambda api: api.energy_data.hm_solar_htg_day_and_total,
    ),
    create_energy_entity_description(
        PRODUCED_SOLAR_HEATING_TOTAL,
        lambda api: api.energy_data.hm_solar_htg_total,
    ),
    create_energy_entity_description(
        PRODUCED_SOLAR_WATER_HEATING_TOTAL,
        lambda api: api.energy_data.hm_solar_dwh_total,
    ),
    create_energy_entity_description(
        PRODUCED_SOLAR_WATER_HEATING,
        lambda api: api.energy_data.hm_solar_dhw_day_and_total,
    ),
]

ENERGY_DAILY_SENSOR_TYPES = [
    create_daily_energy_entity_description(
        PRODUCED_HEATING_TODAY,
        lambda api: api.energy_data.vd_heating_day,
    ),
    create_daily_energy_entity_description(
        PRODUCED_WATER_HEATING_TODAY,
        lambda api: api.energy_data.vd_dhw_day,
    ),
    create_daily_energy_entity_description(
        CONSUMED_HEATING_TODAY,
        lambda api: api.energy_data.vd_heating_day_consumed,
    ),
    create_daily_energy_entity_description(
        CONSUMED_WATER_HEATING_TODAY,
        lambda api: api.energy_data.vd_dhw_day_consumed,
    ),
]

LWZ_ENERGY_DAILY_SENSOR_TYPES = [
    create_daily_energy_entity_description(
        PRODUCED_HEATING_TODAY,
        lambda api: api.energy_data.heat_meter_htg_day,
    ),
    create_daily_energy_entity_description(
        PRODUCED_WATER_HEATING_TODAY,
        lambda api: api.energy_data.heat_meter_dhw_day,
    ),
    create_daily_energy_entity_description(
        CONSUMED_HEATING_TODAY,
        lambda api: api.energy_data.pwr_con_htg_day,
    ),
    create_daily_energy_entity_description(
        CONSUMED_WATER_HEATING_TODAY,
        lambda api: api.energy_data.pwr_con_dhw_day,
    ),
    create_daily_energy_entity_description(
        PRODUCED_RECOVERY_TODAY,
        lambda api: api.energy_data.heat_m_recovery_day,
    ),
    create_daily_energy_entity_description(
        PRODUCED_SOLAR_HEATING_TODAY,
        lambda api: api.energy_data.hm_solar_htg_day,
    ),
    create_daily_energy_entity_description(
        PRODUCED_SOLAR_WATER_HEATING_TODAY,
        lambda api: api.energy_data.hm_solar_dhw_day,
    ),
]


LWZ_COMPRESSOR_SENSOR_TYPES = [
    StiebelEltronSensorEntityDescription(
        key=COMPRESSOR_STARTS,
        translation_key=COMPRESSOR_STARTS,
        modbus_register=lambda api: api.system_values.compressor_starts,
    ),
    StiebelEltronSensorEntityDescription(
        key=COMPRESSOR_SPEED,
        translation_key=COMPRESSOR_SPEED,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=lambda api: api.system_values.compressor_speed,
    ),
    create_runtime_entity_description(
        COMPRESSOR_HEATING,
        lambda api: api.energy_data.compressor_heating,
    ),
    create_runtime_entity_description(
        COMPRESSOR_HEATING_WATER,
        lambda api: api.energy_data.compressor_dhw,
    ),
    create_runtime_entity_description(
        ELECTRICAL_BOOSTER_HEATING,
        lambda api: api.energy_data.elec_booster_heating,
    ),
    create_runtime_entity_description(
        ELECTRICAL_BOOSTER_HEATING_WATER,
        lambda api: api.energy_data.elec_booster_dhw,
    ),
]

LWZ_VENTILATION_SENSOR_TYPES = [
    StiebelEltronSensorEntityDescription(
        key=VENTILATION_AIR_ACTUAL_FAN_SPEED,
        translation_key=VENTILATION_AIR_ACTUAL_FAN_SPEED,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=lambda api: api.system_values.ventilation_air_actual_fan_speed,
    ),
    StiebelEltronSensorEntityDescription(
        key=VENTILATION_AIR_TARGET_FLOW_RATE,
        translation_key=VENTILATION_AIR_TARGET_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=lambda api: api.system_values.ventilation_air_set_flow_rate,
    ),
    StiebelEltronSensorEntityDescription(
        key=EXTRACT_AIR_ACTUAL_FAN_SPEED,
        translation_key=EXTRACT_AIR_ACTUAL_FAN_SPEED,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=lambda api: api.system_values.extract_air_actual_fan_speed,
    ),
    StiebelEltronSensorEntityDescription(
        key=EXTRACT_AIR_TARGET_FLOW_RATE,
        translation_key=EXTRACT_AIR_TARGET_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=lambda api: api.system_values.extract_air_set_flow_rate,
    ),
    create_temperature_entity_description(
        EXTRACT_AIR_DEW_POINT,
        lambda api: api.system_values.extract_air_dew_point,
    ),
    create_humidity_entity_description(
        EXTRACT_AIR_HUMIDITY,
        lambda api: api.system_values.extract_air_humidity,
    ),
    create_temperature_entity_description(
        EXTRACT_AIR_TEMPERATURE,
        lambda api: api.system_values.extract_air_temp,
    ),
]


WPM_COMPRESSOR_SENSOR_TYPES = [
    create_runtime_entity_description(
        COMPRESSOR_HEATING,
        lambda api: api.energy_data.vd_heating,
    ),
    create_runtime_entity_description(
        COMPRESSOR_HEATING_WATER,
        lambda api: api.energy_data.vd_dhw,
    ),
    # Firmware register "VD KÜHLEN". On brine/ground-source systems cooling is
    # passive (no compressor runs), so this counts cooling operation hours
    # rather than compressor hours - hence the neutral name.
    create_runtime_entity_description(
        COOLING_RUNTIME,
        lambda api: api.energy_data.vd_cooling,
    ),
]

# Servicewelt "POWER CONSUMPTION" screen: nine register pairs spanning 3707-3724,
# followed immediately by the efficiency block at 3725, which confirms the
# nine-times-two layout leaves no gap. The
# pystiebeleltron library decodes each register pair as ``low + high * 1000``,
# which lands in Wh for the 24 h windows and in kWh for the 12-month ones. The
# library's own field metadata claims kWh throughout, which is wrong for the
# 24 h windows; the neighbouring amount-of-heat block declares Wh for its 24 h
# entry with the same arithmetic.
WPM_POWER_CONSUMPTION_SENSOR_TYPES = [
    create_power_consumption_entity_description(
        CONSUMED_HEATING_LAST_24H,
        lambda api: api.extended_energy_data.heating_24h,
        UnitOfEnergy.WATT_HOUR,
    ),
    create_power_consumption_entity_description(
        CONSUMED_HEATING_12M,
        lambda api: api.extended_energy_data.heating_12m,
    ),
    create_power_consumption_entity_description(
        CONSUMED_HEATING_PREV_12M,
        lambda api: api.extended_energy_data.heating_13_24,
    ),
    create_power_consumption_entity_description(
        CONSUMED_COOLING_LAST_24H,
        lambda api: api.extended_energy_data.cooling_24h,
        UnitOfEnergy.WATT_HOUR,
    ),
    create_power_consumption_entity_description(
        CONSUMED_COOLING_12M,
        lambda api: api.extended_energy_data.cooling_12m,
    ),
    create_power_consumption_entity_description(
        CONSUMED_COOLING_PREV_12M,
        lambda api: api.extended_energy_data.cooling_13_24,
    ),
    create_power_consumption_entity_description(
        CONSUMED_WATER_HEATING_LAST_24H,
        lambda api: api.extended_energy_data.dhw_24h,
        UnitOfEnergy.WATT_HOUR,
    ),
    create_power_consumption_entity_description(
        CONSUMED_WATER_HEATING_12M,
        lambda api: api.extended_energy_data.dhw_12m,
    ),
    create_power_consumption_entity_description(
        CONSUMED_WATER_HEATING_PREV_12M,
        lambda api: api.extended_energy_data.dhw_13_24,
    ),
]

# Servicewelt "PROZESSDATEN" -> INVERTER AUFNAHMELEISTUNG, wire register 3679.
# Verified against a WPMsystem while its compressor modulated: raw 6, 10 and 11
# read 0.6, 1.0 and 1.1 kW on the ISG display in the same sample, which fixes
# the library's 0.1 scale. The LWZ side declares 0.01 on the same wire address
# and is deliberately left out until someone measures it.
#
# Only IWS 1 is exposed. The library carries inverter_power_iws_2 through _6 for
# cascades; on a single-compressor machine those read the unavailable marker, so
# exposing all six would give most installations five dead entities.
WPM_INVERTER_POWER_SENSOR_TYPES = [
    StiebelEltronSensorEntityDescription(
        key=CURRENT_POWER_CONSUMPTION,
        translation_key=CURRENT_POWER_CONSUMPTION,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        modbus_register=lambda api: api.extended_energy_data.inverter_power_iws_1,
    ),
]


WPM_3I_SENSOR_TYPES = (
    WPM_3I_SYSTEM_VALUES_SENSOR_TYPES
    + ENERGYMANAGEMENT_SENSOR_TYPES
    + ENERGY_SENSOR_TYPES
    + WPM_COMPRESSOR_SENSOR_TYPES
)

WPM_SENSOR_TYPES = (
    SYSTEM_VALUES_SENSOR_TYPES
    + ENERGYMANAGEMENT_SENSOR_TYPES
    + ENERGY_SENSOR_TYPES
    + WPM_COMPRESSOR_SENSOR_TYPES
    + WPM_POWER_CONSUMPTION_SENSOR_TYPES
)

LWZ_SENSOR_TYPES = (
    LWZ_SYSTEM_VALUES_SENSOR_TYPES
    + ENERGYMANAGEMENT_SENSOR_TYPES
    + LWZ_ENERGY_SENSOR_TYPES
    + LWZ_COMPRESSOR_SENSOR_TYPES
    + LWZ_VENTILATION_SENSOR_TYPES
)


async def async_setup_entry(
    _hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data

    if coordinator.model == ControllerModel.WPM_3i:
        entities = [
            StiebelEltronISGSensor(
                coordinator,
                entry,
                description,
            )
            for description in WPM_3I_SENSOR_TYPES
        ]
        daily_energy_entities = [
            StiebelEltronISGEnergySensor(
                coordinator,
                entry,
                description,
            )
            for description in ENERGY_DAILY_SENSOR_TYPES
        ]
        entities.extend(daily_energy_entities)
    elif coordinator.model in (
        ControllerModel.WPM_3,
        ControllerModel.WPMsystem,
        ControllerModel.LWZ_R290,
    ):
        entities = [
            StiebelEltronISGSensor(
                coordinator,
                entry,
                description,
            )
            for description in WPM_SENSOR_TYPES
        ]
        daily_energy_entities = [
            StiebelEltronISGEnergySensor(
                coordinator,
                entry,
                description,
            )
            for description in ENERGY_DAILY_SENSOR_TYPES
        ]
        entities.extend(daily_energy_entities)
        if coordinator.model == ControllerModel.WPMsystem:
            # Only WPMsystem is measured to answer wire 3679. A WPM 3i refuses
            # it outright, and nothing is known about WPM_3 or LWZ_R290, so the
            # sensor stays off the shared list rather than risk an entity that
            # can never hold a value.
            entities.extend(
                StiebelEltronISGSensor(coordinator, entry, description)
                for description in WPM_INVERTER_POWER_SENSOR_TYPES
            )
    else:
        entities = [
            StiebelEltronISGSensor(
                coordinator,
                entry,
                description,
            )
            for description in LWZ_SENSOR_TYPES
        ]
        daily_energy_entities = [
            StiebelEltronISGEnergySensor(
                coordinator,
                entry,
                description,
            )
            for description in LWZ_ENERGY_DAILY_SENSOR_TYPES
        ]
        entities.extend(daily_energy_entities)
    async_add_devices(entities)


class StiebelEltronISGSensor(StiebelEltronISGEntity, SensorEntity):
    """stiebel_eltron_isg Sensor class."""

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronSensorEntityDescription,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register

    @property
    def native_value(self) -> str | float | None:
        """Return the state of the sensor."""
        if self.entity_description.key == ACTIVE_ERROR:
            error_raw = self.coordinator.get_value(self.modbus_register)
            if error_raw is None:
                return None
            error = int(error_raw)
            if error in (32768, 0):
                return "no error"
            return f"error {error}"
        return self.coordinator.get_value(self.modbus_register)


class StiebelEltronISGEnergySensor(StiebelEltronISGSensor):
    """stiebel_eltron_isg Energy Sensor class."""

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronSensorEntityDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry, description)

    @property
    def last_reset(self) -> datetime.datetime | None:
        """Set Last Reset to now, if value is 0."""
        if (
            self.coordinator.has_value(self.modbus_register)
            and self.coordinator.get_value(self.modbus_register) == 0
        ):
            return dt_util.utcnow()
        return None
