"""Constants for stiebel_eltron_isg."""
from homeassistant.const import Platform

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
PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.CLIMATE,
]

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
FLOW_TEMPERATURE = "flow_temperature"
RETURN_TEMPERATURE = "return_temperature"
HEATER_PRESSURE = "heating_pressure"
VOLUME_STREAM = "volume_stream"
SG_READY_STATE = "sg_ready_state"
CONTROLLER_TYPE = "controller_type"
SG_READY_ACTIVE = "sg_ready_active"
SG_READY_INPUT_1 = "sg_ready_input_1"
SG_READY_INPUT_2 = "sg_ready_input_2"

OPERATION_MODE = "operation_mode"


PRODUCED_HEATING_TODAY = "produced_heating_today"
PRODUCED_HEATING_TOTAL = "produced_heating_total"
PRODUCED_WATER_HEATING_TODAY = "produced_water_heating_today"
PRODUCED_WATER_HEATING_TOTAL = "produced_water_heating_total"

CONSUMED_HEATING_TODAY = "consumed_heating_today"
CONSUMED_HEATING_TOTAL = "consumed_heating_total"
CONSUMED_WATER_HEATING_TODAY = "consumed_water_heating_today"
CONSUMED_WATER_HEATING_TOTAL = "consumed_water_heating_total"

COMPRESSOR_STARTS = "compressor_starts"
COMPRESSOR_HEATING = "compressor_heating"
COMPRESSOR_HEATING_WATER = "compressor_heating_water"
ELECTRICAL_BOOSTER_HEATING = "electrical_booster_heating"
ELECTRICAL_BOOSTER_HEATING_WATER = "electrical_booster_heating_water"


IS_HEATING = "is_heating"
IS_HEATING_WATER = "is_heating_water"
IS_SUMMER_MODE = "is_summer_mode"
IS_COOLING = "is_cooling"
PUMP_ON_HK1 = "pump_on_hk1"
PUMP_ON_HK2 = "pump_on_hk2"
COMPRESSOR_ON = "compressor_on"
CIRCULATION_PUMP = "circulation_pump"

SWITCHING_PROGRAM_ENABLED = "switching_program_enabled"
ELECTRIC_REHEATING = "electric_reheating"
SERVICE = "service"
POWER_OFF = "power_off"
FILTER = "filter"
VENTILATION = "ventilation"
EVAPORATOR_DEFROST = "evaporator_defrost"
FILTER_EXTRACT_AIR = "filter_extract_air"
FILTER_VENTILATION_AIR = "filter_ventilation_air"
HEAT_UP_PROGRAM = "heat_up_program"

COMFORT_TEMPERATURE_TARGET_HK1 = "comfort_temperature_target_hk1"
ECO_TEMPERATURE_TARGET_HK1 = "eco_temperature_target_hk1"
HEATING_CURVE_RISE_HK1 = "heating_curve_rise_hk1"
COMFORT_TEMPERATURE_TARGET_HK2 = "comfort_temperature_target_hk2"
ECO_TEMPERATURE_TARGET_HK2 = "eco_temperature_target_hk2"
HEATING_CURVE_RISE_HK2 = "heating_curve_rise_hk2"

COMFORT_WATER_TEMPERATURE_TARGET = "comfort_water_temperature_target"
ECO_WATER_TEMPERATURE_TARGET = "eco_water_temperature_target"


FAN_LEVEL_DAY = "fan_level_comfort"
FAN_LEVEL_NIGHT = "fan_level_eco"
VENTILATION_AIR_ACTUAL_FAN_SPEED = "ventilation_air_actual_fan_speed"
VENTILATION_AIR_TARGET_FLOW_RATE = "ventilation_air_target_flow_rate"
EXTRACT_AIR_ACTUAL_FAN_SPEED = "extract_air_actual"
EXTRACT_AIR_TARGET_FLOW_RATE = "extract_air_target_flowrate"


RESET_HEATPUMP = "reset_heatpump"
ACTIVE_ERROR = "active_error"
ERROR_STATUS = "error_status"

MODEL_ID = "model_id"
