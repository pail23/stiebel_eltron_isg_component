"""Constants for stiebel_eltron_isg."""
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    SensorEntityDescription,
)
from homeassistant.components.switch import SwitchEntityDescription, SwitchDeviceClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE, UnitOfPressure

# Base component constants
DEFAULT_NAME = "Stiebel Eltron ISG"
NAME = DEFAULT_NAME
ATTR_MANUFACTURER = "Stiebel Eltron"
DOMAIN = "stiebel_eltron_isg"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.3.0"
ISSUE_URL = "https://github.com/pail23/stiebel_eltron_isg/issues"
DEFAULT_HOST_NAME = ""
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 502

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH]


ACTUAL_TEMPERATURE = "actual_temperature"
TARGET_TEMPERATURE = "target_temperature"
ACTUAL_TEMPERATURE_FEK = "actual_temperature_fek"
TARGET_TEMPERATURE_FEK = "target_temperature_fek"
ACTUAL_HUMIDITY = "actual_humidity"
DEWPOINT_TEMPERATURE = "dew_point_temperature"
OUTDOOR_TEMPERATURE = "outdoor_temperature"
ACTUAL_TEMPERATURE_HK1 = "actual_temperature_hk1"
TARGET_TEMPERATURE_HK1 = "target_temperature_hk1"
ACTUAL_TEMPERATURE_HK2 = "actual_temperature_hk2"
TARGET_TEMPERATURE_HK2 = "target_temperature_hk2"
ACTUAL_TEMPERATURE_BUFFER = "actual_temperature_buffer"
TARGET_TEMPERATURE_BUFFER = "target_temperature_buffer"
ACTUAL_TEMPERATURE_WATER = "actual_temperature_water"
TARGET_TEMPERATURE_WATER = "target_temperature_water"
SOURCE_TEMPERATURE = "source_temperature"
HEATER_PRESSURE = "heating_pressure"
VOLUME_STREAM = "volume_stream"
SG_READY_STATE = "sg_ready_state"
CONTROLLER_TYPE = "controller_type"
SG_READY_ACTIVE = "sg_ready_active"
SG_READY_INPUT_1 = "sg_ready_input_1"
SG_READY_INPUT_2 = "sg_ready_input_2"


def create_temperature_entity_description(name, key):
    """creates an entry description for a temperature sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="hass:thermometer",
        state_class=STATE_CLASS_MEASUREMENT,
    )


def create_humidity_entity_description(name, key):
    """creates an entry description for a humidity sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=PERCENTAGE,
        icon="hass:water-percent",
        state_class=STATE_CLASS_MEASUREMENT,
    )


def create_pressure_entity_description(name, key):
    """creates an entry description for a pressure sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        state_class=STATE_CLASS_MEASUREMENT,
    )


def create_volume_stream_entity_description(name, key):
    """creates an entry description for a volume stream sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement="l/min",
        icon="mdi:gauge",
        state_class=STATE_CLASS_MEASUREMENT,
    )


SYSTEM_VALUES_SENSOR_TYPES = [
    create_temperature_entity_description("Actual Temperature", ACTUAL_TEMPERATURE),
    create_temperature_entity_description("Target Temperature", TARGET_TEMPERATURE),
    create_temperature_entity_description(
        "Actual Temperature FEK", ACTUAL_TEMPERATURE_FEK
    ),
    create_temperature_entity_description(
        "Target Temperature FEK", TARGET_TEMPERATURE_FEK
    ),
    create_humidity_entity_description("Humidity", ACTUAL_HUMIDITY),
    create_temperature_entity_description(
        "Dew Point Temperature", DEWPOINT_TEMPERATURE
    ),
    create_temperature_entity_description("Outdoor Temperature", OUTDOOR_TEMPERATURE),
    create_temperature_entity_description(
        "Actual Temperature HK 1", ACTUAL_TEMPERATURE_HK1
    ),
    create_temperature_entity_description(
        "Target Temperature HK 1", TARGET_TEMPERATURE_HK1
    ),
    create_temperature_entity_description(
        "Actual Temperature HK 2", ACTUAL_TEMPERATURE_HK2
    ),
    create_temperature_entity_description(
        "Target Temperature HK 2", TARGET_TEMPERATURE_HK2
    ),
    create_temperature_entity_description(
        "Actual Temperature Buffer", ACTUAL_TEMPERATURE_BUFFER
    ),
    create_temperature_entity_description(
        "Target Temperature Buffer", TARGET_TEMPERATURE_BUFFER
    ),
    create_pressure_entity_description("Heater Pressure", HEATER_PRESSURE),
    create_volume_stream_entity_description("Volume Stream", VOLUME_STREAM),
    create_temperature_entity_description(
        "Actual Temperature Water", ACTUAL_TEMPERATURE_WATER
    ),
    create_temperature_entity_description(
        "Target Temperature Water", TARGET_TEMPERATURE_WATER
    ),
    create_temperature_entity_description("Source Temperature", SOURCE_TEMPERATURE),
]

ENERGYMANAGEMENT_SENSOR_TYPES = [
    SensorEntityDescription(
        SG_READY_STATE,
        name="SG Ready State",
        icon="mdi:solar-power",
    )
]

PRODUCED_HEATING_TODAY = "produced_heating_today"
PRODUCED_HEATING_TOTAL = "produced_heating_total"
PRODUCED_WATER_HEATING_TODAY = "produced_water_heating_today"
PRODUCED_WATER_HEATING_TOTAL = "produced_water_heating_total"

CONSUMED_HEATING_TODAY = "consumed_heating_today"
CONSUMED_HEATING_TOTAL = "consumed_heating_total"
CONSUMED_WATER_HEATING_TODAY = "consumed_water_heating_today"
CONSUMED_WATER_HEATING_TOTAL = "consumed_water_heating_total"
CONSUMED_POWER = "consumed_power"
HEATPUMPT_AVERAGE_POWER = 4.5

ENERGY_SENSOR_TYPES = [
    [
        "Produced Heating Today",
        PRODUCED_HEATING_TODAY,
        "kWh",
        "mdi:radiator",
    ],
    [
        "Produced Heating Total",
        PRODUCED_HEATING_TOTAL,
        "kWh",
        "mdi:radiator",
    ],
    [
        "Produced Water Heating Today",
        PRODUCED_WATER_HEATING_TODAY,
        "kWh",
        "mdi:water-boiler",
    ],
    [
        "Produced Water Heating Total",
        PRODUCED_WATER_HEATING_TOTAL,
        "kWh",
        "mdi:water-boiler",
    ],
    [
        "Consumed Heating Today",
        CONSUMED_HEATING_TODAY,
        "kWh",
        "mdi:lightning-bolt",
    ],
    [
        "Consumed Heating Total",
        CONSUMED_HEATING_TOTAL,
        "kWh",
        "mdi:lightning-bolt",
    ],
    [
        "Consumed Water Heating Today",
        CONSUMED_WATER_HEATING_TODAY,
        "kWh",
        "mdi:lightning-bolt",
    ],
    [
        "Consumed Water Heating Total",
        CONSUMED_WATER_HEATING_TOTAL,
        "kWh",
        "mdi:lightning-bolt",
    ],
    [
        "Consumed Power",
        CONSUMED_POWER,
        "kW",
        "mdi:lightning-bolt",
    ],
]

IS_HEATING = "is_heating"
IS_HEATING_WATER = "is_heating_water"
IS_SUMMER_MODE = "is_summer_mode"
IS_COOLING = "is_cooling"

BINARY_SENSOR_TYPES = [
    BinarySensorEntityDescription(
        name="Is heating",
        key=IS_HEATING,
        icon="mdi:radiator",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Is heating boiler",
        key=IS_HEATING_WATER,
        icon="mdi:water-boiler",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Is in summer mode",
        key=IS_SUMMER_MODE,
        icon="mdi:weather-sunny",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Is cooling",
        key=IS_COOLING,
        icon="mdi:snowflake",
        has_entity_name=True,
    ),
]

SWITCH_TYPES = [
    SwitchEntityDescription(
        SG_READY_ACTIVE,
        SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Active",
    ),
    SwitchEntityDescription(
        SG_READY_INPUT_1,
        SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Input 1",
    ),
    SwitchEntityDescription(
        SG_READY_INPUT_2,
        SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        name="SG Ready Input 2",
    ),
]


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
