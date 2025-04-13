"""Sensor platform for stiebel_eltron_isg."""

import datetime
import logging
from dataclasses import dataclass

import homeassistant.util.dt as dt_util
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
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
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
    IsgRegisters,
    EnergyManagementSettingsRegisters,
)
from custom_components.stiebel_eltron_isg.python_stiebel_eltron.lwz import (
    LwzEnergyDataRegisters,
    LwzSystemValuesRegisters,
)
from custom_components.stiebel_eltron_isg.python_stiebel_eltron.wpm import (
    WpmEnergyDataRegisters,
    WpmSystemStateRegisters,
    WpmSystemValuesRegisters,
)

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
    COMPRESSOR_STARTS,
    CONSUMED_HEATING,
    CONSUMED_HEATING_TODAY,
    CONSUMED_HEATING_TOTAL,
    CONSUMED_WATER_HEATING,
    CONSUMED_WATER_HEATING_TODAY,
    CONSUMED_WATER_HEATING_TOTAL,
    DEWPOINT_TEMPERATURE,
    DEWPOINT_TEMPERATURE_HK1,
    DEWPOINT_TEMPERATURE_HK2,
    DEWPOINT_TEMPERATURE_HK3,
    DOMAIN,
    ELECTRICAL_BOOSTER_HEATING,
    ELECTRICAL_BOOSTER_HEATING_WATER,
    EXTRACT_AIR_ACTUAL_FAN_SPEED,
    EXTRACT_AIR_DEW_POINT,
    EXTRACT_AIR_HUMIDITY,
    EXTRACT_AIR_TARGET_FLOW_RATE,
    EXTRACT_AIR_TEMPERATURE,
    FLOW_TEMPERATURE,
    FLOW_TEMPERATURE_NHZ,
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
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class StiebelEltronSensorEntityDescription(SensorEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: IsgRegisters


def create_temperature_entity_description(name, key, modbus_register: IsgRegisters):
    """Create an entry description for a temperature sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        name=name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        has_entity_name=True,
        modbus_register=modbus_register,
    )


def create_energy_entity_description(
    name,
    key,
    modbus_register: IsgRegisters,
    visible_default=True,
):
    """Create an entry description for a energy sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        name=name,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:meter-electric",
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=visible_default,
        modbus_register=modbus_register,
    )


def create_daily_energy_entity_description(
    name,
    key,
    modbus_register: IsgRegisters,
    visible_default=True,
):
    """Create an entry description for a energy sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        name=name,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:meter-electric",
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=visible_default,
        modbus_register=modbus_register,
    )


def create_humidity_entity_description(name, key, modbus_register: IsgRegisters):
    """Create an entry description for a humidity sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        name=name,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
        modbus_register=modbus_register,
    )


def create_pressure_entity_description(name, key, modbus_register: IsgRegisters):
    """Create an entry description for a pressure sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        name=name,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
        modbus_register=modbus_register,
    )


def create_volume_stream_entity_description(name, key, modbus_register: IsgRegisters):
    """Create an entry description for a volume stream sensor."""
    return StiebelEltronSensorEntityDescription(
        key=key,
        name=name,
        native_unit_of_measurement="l/min",
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
        modbus_register=modbus_register,
    )


SYSTEM_VALUES_SENSOR_TYPES = [
    create_temperature_entity_description(
        "Actual Temperature",
        ACTUAL_TEMPERATURE,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FE7,
    ),
    create_temperature_entity_description(
        "Target Temperature",
        TARGET_TEMPERATURE,
        WpmSystemValuesRegisters.SET_TEMPERATURE_FE7,
    ),
    create_temperature_entity_description(
        "Actual Temperature FEK",
        ACTUAL_TEMPERATURE_FEK,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FEK,
    ),
    create_temperature_entity_description(
        "Target Temperature FEK",
        TARGET_TEMPERATURE_FEK,
        WpmSystemValuesRegisters.SET_TEMPERATURE_FEK,
    ),
    create_humidity_entity_description(
        "Humidity", ACTUAL_HUMIDITY, WpmSystemValuesRegisters.RELATIVE_HUMIDITY
    ),
    create_humidity_entity_description(
        "Humidity HK 1",
        ACTUAL_HUMIDITY_HK1,
        WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC1,
    ),
    create_humidity_entity_description(
        "Humidity HK 2",
        ACTUAL_HUMIDITY_HK2,
        WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC1,
    ),
    create_humidity_entity_description(
        "Humidity HK 3",
        ACTUAL_HUMIDITY_HK3,
        WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC1,
    ),
    create_temperature_entity_description(
        "Dew Point Temperature",
        DEWPOINT_TEMPERATURE,
        WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 1",
        DEWPOINT_TEMPERATURE_HK1,
        WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC1,
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 2",
        DEWPOINT_TEMPERATURE_HK2,
        WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC2,
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 3",
        DEWPOINT_TEMPERATURE_HK3,
        WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC3,
    ),
    create_temperature_entity_description(
        "Outdoor Temperature",
        OUTDOOR_TEMPERATURE,
        WpmSystemValuesRegisters.OUTSIDE_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Actual Temperature HK 1",
        ACTUAL_TEMPERATURE_HK1,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_1,
    ),
    create_temperature_entity_description(
        "Target Temperature HK 1",
        TARGET_TEMPERATURE_HK1,
        WpmSystemValuesRegisters.SET_TEMPERATURE_HK_1,
    ),
    create_temperature_entity_description(
        "Actual Temperature HK 2",
        ACTUAL_TEMPERATURE_HK2,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_2,
    ),
    create_temperature_entity_description(
        "Target Temperature HK 2",
        TARGET_TEMPERATURE_HK2,
        WpmSystemValuesRegisters.SET_TEMPERATURE_HK_2,
    ),
    create_temperature_entity_description(
        "Actual Temperature HK 3",
        ACTUAL_TEMPERATURE_HK3,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_3,
    ),
    create_temperature_entity_description(
        "Target Temperature HK 3",
        TARGET_TEMPERATURE_HK3,
        WpmSystemValuesRegisters.SET_TEMPERATURE_HK_3,
    ),
    create_temperature_entity_description(
        "Actual Temperature Cooling Fancoil",
        ACTUAL_TEMPERATURE_COOLING_FANCOIL,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FAN,
    ),
    create_temperature_entity_description(
        "Target Temperature Cooling Fancoil",
        TARGET_TEMPERATURE_COOLING_FANCOIL,
        WpmSystemValuesRegisters.SET_TEMPERATURE_FAN,
    ),
    create_temperature_entity_description(
        "Actual Temperature Cooling Surface",
        ACTUAL_TEMPERATURE_COOLING_SURFACE,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_AREA,
    ),
    create_temperature_entity_description(
        "Target Temperature Cooling Surface",
        TARGET_TEMPERATURE_COOLING_SURFACE,
        WpmSystemValuesRegisters.SET_TEMPERATURE_AREA,
    ),
    create_temperature_entity_description(
        "Solar Cylinder Temperature",
        SOLAR_CYLINDER_TEMPERATURE,
        WpmSystemValuesRegisters.CYLINDER_TEMPERATURE,
    ),
    StiebelEltronSensorEntityDescription(
        key=SOLAR_RUNTIME,
        name="Solar Runtime",
        has_entity_name=True,
        icon="mdi:hours-24",
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=WpmSystemValuesRegisters.RUNTIME,
    ),
    create_temperature_entity_description(
        "Actual Room Temperature HK 1",
        ACTUAL_ROOM_TEMPERATURE_HK1,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE__ROOM_TEMP_HC1,
    ),
    create_temperature_entity_description(
        "Target Room Temperature HK 1",
        TARGET_ROOM_TEMPERATURE_HK1,
        WpmSystemValuesRegisters.SET_TEMPERATURE__ROOM_TEMP_HC1,
    ),
    create_temperature_entity_description(
        "Actual Room Temperature HK 2",
        ACTUAL_ROOM_TEMPERATURE_HK2,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE__ROOM_TEMP_HC2,
    ),
    create_temperature_entity_description(
        "Target Room Temperature HK 2",
        TARGET_ROOM_TEMPERATURE_HK2,
        WpmSystemValuesRegisters.SET_TEMPERATURE__ROOM_TEMP_HC2,
    ),
    create_temperature_entity_description(
        "Actual Room Temperature HK 3",
        ACTUAL_ROOM_TEMPERATURE_HK3,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE__ROOM_TEMP_HC3,
    ),
    create_temperature_entity_description(
        "Target Room Temperature HK 3",
        TARGET_ROOM_TEMPERATURE_HK3,
        WpmSystemValuesRegisters.SET_TEMPERATURE__ROOM_TEMP_HC3,
    ),
    create_temperature_entity_description(
        "Flow Temperature",
        FLOW_TEMPERATURE,
        WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE_WP,
    ),
    create_temperature_entity_description(
        "Flow Temperature NHZ",
        FLOW_TEMPERATURE_NHZ,
        WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE_NHZ,
    ),
    create_temperature_entity_description(
        "Return Temperature",
        RETURN_TEMPERATURE,
        WpmSystemValuesRegisters.ACTUAL_RETURN_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Actual Temperature Buffer",
        ACTUAL_TEMPERATURE_BUFFER,
        WpmSystemValuesRegisters.ACTUAL_BUFFER_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Target Temperature Buffer",
        TARGET_TEMPERATURE_BUFFER,
        WpmSystemValuesRegisters.SET_BUFFER_TEMPERATURE,
    ),
    create_pressure_entity_description(
        "Heater Pressure", HEATER_PRESSURE, WpmSystemValuesRegisters.HEATING_PRESSURE
    ),
    create_volume_stream_entity_description(
        "Volume Stream", VOLUME_STREAM, WpmSystemValuesRegisters.FLOW_RATE
    ),
    create_temperature_entity_description(
        "Actual Temperature Water",
        ACTUAL_TEMPERATURE_WATER,
        WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_DHW,
    ),
    create_temperature_entity_description(
        "Target Temperature Water",
        TARGET_TEMPERATURE_WATER,
        WpmSystemValuesRegisters.SET_TEMPERATURE_DHW,
    ),
    create_temperature_entity_description(
        "Solar Collector Temperature",
        SOLAR_COLLECTOR_TEMPERATURE,
        WpmSystemValuesRegisters.COLLECTOR_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Source Temperature",
        SOURCE_TEMPERATURE,
        WpmSystemValuesRegisters.SOURCE_TEMPERATURE,
    ),
    create_pressure_entity_description(
        "Source Pressure", SOURCE_PRESSURE, WpmSystemValuesRegisters.SOURCE_PRESSURE
    ),
    create_temperature_entity_description(
        "Hot Gas Temperature",
        HOT_GAS_TEMPERATURE,
        WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE,
    ),
    create_pressure_entity_description(
        "High Pressure", HIGH_PRESSURE, WpmSystemValuesRegisters.HIGH_PRESSURE
    ),
    create_pressure_entity_description(
        "Low Pressure", LOW_PRESSURE, WpmSystemValuesRegisters.LOW_PRESSURE
    ),
    create_temperature_entity_description(
        "Return Temperature WP1",
        RETURN_TEMPERATURE_WP1,
        WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP1,
    ),
    create_temperature_entity_description(
        "Flow Temperature WP1",
        FLOW_TEMPERATURE_WP1,
        WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP1,
    ),
    create_temperature_entity_description(
        "Hot Gas Temperature WP1",
        HOT_GAS_TEMPERATURE_WP1,
        WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP1,
    ),
    create_pressure_entity_description(
        "Low Pressure WP1", LOW_PRESSURE_WP1, WpmSystemValuesRegisters.LOW_PRESSURE_HP1
    ),
    create_pressure_entity_description(
        "High Pressure WP1",
        HIGH_PRESSURE_WP1,
        WpmSystemValuesRegisters.HIGH_PRESSURE_HP1,
    ),
    create_volume_stream_entity_description(
        "Volume Stream WP1",
        VOLUME_STREAM_WP1,
        WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP1,
    ),
    create_temperature_entity_description(
        "Return Temperature WP2",
        RETURN_TEMPERATURE_WP2,
        WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP2,
    ),
    create_temperature_entity_description(
        "Flow Temperature WP2",
        FLOW_TEMPERATURE_WP2,
        WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP2,
    ),
    create_temperature_entity_description(
        "Hot Gas Temperature WP2",
        HOT_GAS_TEMPERATURE_WP2,
        WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP2,
    ),
    create_pressure_entity_description(
        "Low Pressure WP2", LOW_PRESSURE_WP2, WpmSystemValuesRegisters.LOW_PRESSURE_HP2
    ),
    create_pressure_entity_description(
        "High Pressure WP2",
        HIGH_PRESSURE_WP2,
        WpmSystemValuesRegisters.HIGH_PRESSURE_HP2,
    ),
    create_volume_stream_entity_description(
        "Volume Stream WP2",
        VOLUME_STREAM_WP2,
        WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP2,
    ),
    StiebelEltronSensorEntityDescription(
        key=ACTIVE_ERROR,
        name="Active Error",
        has_entity_name=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert-circle",
        modbus_register=WpmSystemStateRegisters.ACTIVE_ERROR,
    ),
]

LWZ_SYSTEM_VALUES_SENSOR_TYPES = [
    create_temperature_entity_description(
        "Actual Temperature",
        ACTUAL_TEMPERATURE,
        LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC1,
    ),
    create_temperature_entity_description(
        "Target Temperature",
        TARGET_TEMPERATURE,
        LwzSystemValuesRegisters.SET_ROOM_TEMPERATURE_HC1,
    ),
    create_temperature_entity_description(
        "Actual Temperature FEK",
        ACTUAL_TEMPERATURE_FEK,
        LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC2,
    ),
    create_temperature_entity_description(
        "Target Temperature FEK",
        TARGET_TEMPERATURE_FEK,
        LwzSystemValuesRegisters.SET_ROOM_TEMPERATURE_HC2,
    ),
    create_humidity_entity_description(
        "Humidity", ACTUAL_HUMIDITY, LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC1
    ),
    create_humidity_entity_description(
        "Humidity HK 2",
        ACTUAL_HUMIDITY_HK2,
        LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC2,
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 1",
        DEWPOINT_TEMPERATURE_HK1,
        LwzSystemValuesRegisters.DEW_POINT_TEMP_HC1,
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 2",
        DEWPOINT_TEMPERATURE_HK2,
        LwzSystemValuesRegisters.DEW_POINT_TEMP_HC2,
    ),
    create_temperature_entity_description(
        "Outdoor Temperature",
        OUTDOOR_TEMPERATURE,
        LwzSystemValuesRegisters.OUTSIDE_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Actual Temperature HK 1",
        ACTUAL_TEMPERATURE_HK1,
        LwzSystemValuesRegisters.ACTUAL_VALUE_HC1,
    ),
    create_temperature_entity_description(
        "Target Temperature HK 1",
        TARGET_TEMPERATURE_HK1,
        LwzSystemValuesRegisters.SET_VALUE_HC1,
    ),
    create_temperature_entity_description(
        "Actual Temperature HK 2",
        ACTUAL_TEMPERATURE_HK2,
        LwzSystemValuesRegisters.ACTUAL_VALUE_HC2,
    ),
    create_temperature_entity_description(
        "Target Temperature HK 2",
        TARGET_TEMPERATURE_HK2,
        LwzSystemValuesRegisters.SET_VALUE_HC2,
    ),
    create_temperature_entity_description(
        "Flow Temperature",
        FLOW_TEMPERATURE,
        LwzSystemValuesRegisters.FLOW_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Return Temperature",
        RETURN_TEMPERATURE,
        LwzSystemValuesRegisters.RETURN_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Actual Temperature Water",
        ACTUAL_TEMPERATURE_WATER,
        LwzSystemValuesRegisters.ACTUAL_DHW_T,
    ),
    create_temperature_entity_description(
        "Target Temperature Water",
        TARGET_TEMPERATURE_WATER,
        LwzSystemValuesRegisters.DHW_SET_TEMPERATURE,
    ),
    create_temperature_entity_description(
        "Hot Gas Temperature",
        HOT_GAS_TEMPERATURE,
        LwzSystemValuesRegisters.HOT_GAS_TEMPERATURE,
    ),
    create_pressure_entity_description(
        "High Pressure", HIGH_PRESSURE, LwzSystemValuesRegisters.HIGH_PRESSURE
    ),
    create_pressure_entity_description(
        "Low Pressure", LOW_PRESSURE, LwzSystemValuesRegisters.LOW_PRESSURE
    ),
]


ENERGYMANAGEMENT_SENSOR_TYPES = [
    StiebelEltronSensorEntityDescription(
        key=SG_READY_STATE,
        name="SG Ready State",
        icon="mdi:solar-power",
        has_entity_name=True,
        modbus_register=EnergyManagementSettingsRegisters.SWITCH_SG_READY_ON_AND_OFF,
    ),
]

ENERGY_SENSOR_TYPES = [
    create_energy_entity_description(
        "Produced Heating Total",
        PRODUCED_HEATING_TOTAL,
        WpmEnergyDataRegisters.VD_HEATING_TOTAL,
    ),
    create_energy_entity_description(
        "Produced Heating", PRODUCED_HEATING, WpmEnergyDataRegisters.VD_HEATING_TOTAL
    ),
    create_energy_entity_description(
        "Produced Water Heating Total",
        PRODUCED_WATER_HEATING_TOTAL,
        WpmEnergyDataRegisters.VD_DHW_TOTAL,
    ),
    create_energy_entity_description(
        "Produced Water Heating",
        PRODUCED_WATER_HEATING,
        WpmEnergyDataRegisters.VD_DHW_TOTAL,
    ),
    create_energy_entity_description(
        "Consumed Heating Total",
        CONSUMED_HEATING_TOTAL,
        WpmEnergyDataRegisters.VD_HEATING_TOTAL_CONSUMED,
    ),
    create_energy_entity_description(
        "Consumed Heating",
        CONSUMED_HEATING,
        WpmEnergyDataRegisters.VD_HEATING_TOTAL_CONSUMED,
    ),
    create_energy_entity_description(
        "Consumed Water Heating Total",
        CONSUMED_WATER_HEATING_TOTAL,
        WpmEnergyDataRegisters.VD_DHW_TOTAL_CONSUMED,
    ),
    create_energy_entity_description(
        "Consumed Water Heating",
        CONSUMED_WATER_HEATING,
        WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED,
    ),
]

LWZ_ENERGY_SENSOR_TYPES = [
    create_energy_entity_description(
        "Produced Electrical Booster Heating Total",
        PRODUCED_ELECTRICAL_BOOSTER_HEATING_TOTAL,
        LwzEnergyDataRegisters.HEAT_M_BOOST_HTG_TTL,
    ),
    create_energy_entity_description(
        "Produced Electrical Booster Water Heating Total",
        PRODUCED_ELECTRICAL_BOOSTER_WATER_HEATING_TOTAL,
        LwzEnergyDataRegisters.HEAT_M_BOOST_DHW_TTL,
    ),
    create_energy_entity_description(
        "Produced Recovery",
        PRODUCED_RECOVERY,
        LwzEnergyDataRegisters.HEAT_M_RECOVERY_DAY,
    ),
    create_energy_entity_description(
        "Produced Recovery Total",
        PRODUCED_RECOVERY_TOTAL,
        LwzEnergyDataRegisters.HEAT_M_RECOVERY_TTL,
    ),
    create_energy_entity_description(
        "Produced Solar Heating",
        PRODUCED_SOLAR_HEATING,
        LwzEnergyDataRegisters.HM_SOLAR_HTG_TOTAL,
    ),
    create_energy_entity_description(
        "Produced Solar Heating Total",
        PRODUCED_SOLAR_HEATING_TOTAL,
        LwzEnergyDataRegisters.HM_SOLAR_HTG_TOTAL,
    ),
    create_energy_entity_description(
        "Produced Solar Water Heating Total",
        PRODUCED_SOLAR_WATER_HEATING_TOTAL,
        LwzEnergyDataRegisters.HM_SOLAR_DWH_TOTAL,
    ),
    create_energy_entity_description(
        "Produced Solar Water Heating",
        PRODUCED_SOLAR_WATER_HEATING,
        LwzEnergyDataRegisters.HM_SOLAR_DWH_TOTAL,
    ),
]

ENERGY_DAILY_SENSOR_TYPES = [
    create_daily_energy_entity_description(
        "Produced Heating Today",
        PRODUCED_HEATING_TODAY,
        WpmEnergyDataRegisters.VD_HEATING_DAY,
    ),
    create_daily_energy_entity_description(
        "Produced Water Heating Today",
        PRODUCED_WATER_HEATING_TODAY,
        WpmEnergyDataRegisters.VD_DHW_DAY,
    ),
    create_daily_energy_entity_description(
        "Consumed Heating Today",
        CONSUMED_HEATING_TODAY,
        WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED,
    ),
    create_daily_energy_entity_description(
        "Consumed Water Heating Today",
        CONSUMED_WATER_HEATING_TODAY,
        WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED,
    ),
]

LWZ_ENERGY_DAILY_SENSOR_TYPES = [
    create_daily_energy_entity_description(
        "Produced Recovery Today",
        PRODUCED_RECOVERY_TODAY,
        LwzEnergyDataRegisters.HEAT_M_RECOVERY_DAY,
    ),
    create_daily_energy_entity_description(
        "Produced Solar Heating Today",
        PRODUCED_SOLAR_HEATING_TODAY,
        LwzEnergyDataRegisters.HM_SOLAR_HTG_DAY,
    ),
    create_daily_energy_entity_description(
        "Produced Solar Water Heating Today",
        PRODUCED_SOLAR_WATER_HEATING_TODAY,
        LwzEnergyDataRegisters.HM_SOLAR_DHW_DAY,
    ),
]


LWZ_COMPRESSOR_SENSOR_TYPES = [
    StiebelEltronSensorEntityDescription(
        key=COMPRESSOR_STARTS,
        name="Compressor starts",
        icon="mdi:restart",
        has_entity_name=True,
        modbus_register=LwzSystemValuesRegisters.COMPRESSOR_STARTS,
    ),
    StiebelEltronSensorEntityDescription(
        key=COMPRESSOR_HEATING,
        name="Compressor heating",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzEnergyDataRegisters.COMPRESSOR_HEATING,
    ),
    StiebelEltronSensorEntityDescription(
        key=COMPRESSOR_HEATING_WATER,
        name="Compressor heating water",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzEnergyDataRegisters.COMPRESSOR_DHW,
    ),
    StiebelEltronSensorEntityDescription(
        key=ELECTRICAL_BOOSTER_HEATING,
        name="Electrical booster heating",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzEnergyDataRegisters.ELEC_BOOSTER_HEATING,
    ),
    StiebelEltronSensorEntityDescription(
        key=ELECTRICAL_BOOSTER_HEATING_WATER,
        name="Electrical booster heating water",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzEnergyDataRegisters.ELEC_BOOSTER_DHW,
    ),
]

LWZ_VENTILATION_SENSOR_TYPES = [
    StiebelEltronSensorEntityDescription(
        key=VENTILATION_AIR_ACTUAL_FAN_SPEED,
        name="Ventilation air actual fan speed",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzSystemValuesRegisters.VENTILATION_AIR_ACTUAL_FAN_SPEED,
    ),
    StiebelEltronSensorEntityDescription(
        key=VENTILATION_AIR_TARGET_FLOW_RATE,
        name="Ventilation air target flow rate",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzSystemValuesRegisters.VENTILATION_AIR_SET_FLOW_RATE,
    ),
    StiebelEltronSensorEntityDescription(
        key=EXTRACT_AIR_ACTUAL_FAN_SPEED,
        name="Extract air actual fan speed",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzSystemValuesRegisters.EXTRACT_AIR_ACTUAL_FAN_SPEED,
    ),
    StiebelEltronSensorEntityDescription(
        key=EXTRACT_AIR_TARGET_FLOW_RATE,
        name="Extract air target flow rate",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        modbus_register=LwzSystemValuesRegisters.EXTRACT_AIR_SET_FLOW_RATE,
    ),
    create_temperature_entity_description(
        "Extract air dew point",
        EXTRACT_AIR_DEW_POINT,
        LwzSystemValuesRegisters.EXTRACT_AIR_DEW_POINT,
    ),
    create_humidity_entity_description(
        "Extract air humidity",
        EXTRACT_AIR_HUMIDITY,
        LwzSystemValuesRegisters.EXTRACT_AIR_HUMIDITY,
    ),
    create_temperature_entity_description(
        "Extract air temperature",
        EXTRACT_AIR_TEMPERATURE,
        LwzSystemValuesRegisters.EXTRACT_AIR_TEMP,
    ),
]


WPM_SENSOR_TYPES = (
    SYSTEM_VALUES_SENSOR_TYPES + ENERGYMANAGEMENT_SENSOR_TYPES + ENERGY_SENSOR_TYPES
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
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

    if coordinator.is_wpm:
        entities = [
            StiebelEltronISGSensor(
                coordinator,
                entry,
                description,
            )
            for description in WPM_SENSOR_TYPES
        ]
        daily_energy_entities = [
            StiebelEltronISGSensor(
                coordinator,
                entry,
                description,
            )
            for description in ENERGY_DAILY_SENSOR_TYPES
        ]
        entities.extend(daily_energy_entities)
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
            StiebelEltronISGSensor(
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
        coordinator: StiebelEltronModbusDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
        description: StiebelEltronSensorEntityDescription,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.modbus_register == WpmSystemStateRegisters.ACTIVE_ERROR:
            error = int(self.coordinator.get_register_value(self.modbus_register))
            if error in (32768, 0):
                return "no error"
            return f"error {error}"
        return self.coordinator.get_register_value(self.modbus_register)


class StiebelEltronISGEnergySensor(StiebelEltronISGEntity, SensorEntity):
    """stiebel_eltron_isg Energy Sensor class."""

    def __init__(
        self,
        coordinator: StiebelEltronModbusDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
        description: StiebelEltronSensorEntityDescription,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.get_register_value(self.modbus_register)

    @property
    def last_reset(self) -> datetime.datetime | None:
        """Set Last Reset to now, if value is 0."""
        if (
            self.coordinator.has_register_value(self.modbus_register)
            and self.coordinator.get_register_value(self.modbus_register) == 0
        ):
            return dt_util.utcnow()
        return None
