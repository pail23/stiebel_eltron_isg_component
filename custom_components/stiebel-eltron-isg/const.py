"""Constants for stiebel_eltron_isg."""
# Base component constants
NAME = "Stiebel Eltron ISG"
ATTR_MANUFACTURER = "Stiebel Eltron"
DOMAIN = "stiebel_eltron_isg"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/pail23/stiebel_eltron_isg/issues"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PORT = 502

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [SENSOR]  # [BINARY_SENSOR, SENSOR, SWITCH]


ENERGY_SENSOR_TYPES = {
    "Produced_Heating_Today": [
        "Produced Heating Today",
        "producedheatingtoday",
        "kWh",
        "mdi:lightning-bolt",
    ],
    "Produced_Heating_Total": [
        "Produced Heating Total",
        "producedheatingtotal",
        "kWh",
        "mdi:lightning-bolt",
    ],
    "Produced_Water_Heating_Today": [
        "Produced Water Heating Today",
        "producedwaterheatingtoday",
        "kWh",
        "mdi:lightning-bolt",
    ],
    "Produced_Water_Heating_Total": [
        "Produced Water Heating Total",
        "producedwaterheatingtotal",
        "kWh",
        "mdi:lightning-bolt",
    ],
    "Consumed_Heating_Today": [
        "Consumed Heating Today",
        "consumedheatingtoday",
        "kWh",
        "mdi:lightning-bolt",
    ],
    "Consumed_Heating_Total": [
        "Consumed Heating Total",
        "consumedheatingtotal",
        "kWh",
        "mdi:lightning-bolt",
    ],
    "Consumed_Water_Heating_Today": [
        "Consumed Water Heating Today",
        "consumedwaterheatingtoday",
        "kWh",
        "mdi:lightning-bolt",
    ],
    "Consumed_Water_Heating_Total": [
        "Consumed Water Heating Total",
        "consumedwaterheatingtotal",
        "kWh",
        "mdi:lightning-bolt",
    ],
}


# Configuration and options
CONF_ENABLED = "enabled"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
