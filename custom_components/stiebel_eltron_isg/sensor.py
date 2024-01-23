"""Sensor platform for stiebel_eltron_isg."""
import logging


from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfEnergy,
)

from .const import (
    ACTUAL_HUMIDITY_HK1,
    ACTUAL_HUMIDITY_HK2,
    ACTUAL_HUMIDITY_HK3,
    DEWPOINT_TEMPERATURE_HK1,
    DEWPOINT_TEMPERATURE_HK2,
    DEWPOINT_TEMPERATURE_HK3,
    DOMAIN,
    ACTUAL_TEMPERATURE,
    TARGET_TEMPERATURE,
    ACTUAL_TEMPERATURE_FEK,
    TARGET_TEMPERATURE_FEK,
    ACTUAL_HUMIDITY,
    DEWPOINT_TEMPERATURE,
    OUTDOOR_TEMPERATURE,
    ACTUAL_TEMPERATURE_HK1,
    TARGET_TEMPERATURE_HK1,
    ACTUAL_TEMPERATURE_HK2,
    TARGET_TEMPERATURE_HK2,
    FLOW_TEMPERATURE,
    FLOW_TEMPERATURE_NHZ,
    RETURN_TEMPERATURE,
    ACTUAL_TEMPERATURE_BUFFER,
    TARGET_TEMPERATURE_BUFFER,
    ACTUAL_TEMPERATURE_WATER,
    ACTUAL_ROOM_TEMPERATURE_HK1,
    TARGET_ROOM_TEMPERATURE_HK1,
    ACTUAL_ROOM_TEMPERATURE_HK2,
    TARGET_ROOM_TEMPERATURE_HK2,
    ACTUAL_ROOM_TEMPERATURE_HK3,
    TARGET_ROOM_TEMPERATURE_HK3,
    TARGET_TEMPERATURE_WATER,
    SOURCE_TEMPERATURE,
    SOURCE_PRESSURE,
    HOT_GAS_TEMPERATURE,
    HIGH_PRESSURE,
    LOW_PRESSURE,
    HEATER_PRESSURE,
    VOLUME_STREAM,
    SG_READY_STATE,
    PRODUCED_HEATING_TODAY,
    PRODUCED_HEATING_TOTAL,
    PRODUCED_WATER_HEATING_TODAY,
    PRODUCED_WATER_HEATING_TOTAL,
    CONSUMED_HEATING_TODAY,
    CONSUMED_HEATING_TOTAL,
    CONSUMED_WATER_HEATING_TODAY,
    CONSUMED_WATER_HEATING_TOTAL,
    COMPRESSOR_STARTS,
    COMPRESSOR_HEATING,
    COMPRESSOR_HEATING_WATER,
    ELECTRICAL_BOOSTER_HEATING,
    ELECTRICAL_BOOSTER_HEATING_WATER,
    ACTIVE_ERROR,
    VENTILATION_AIR_ACTUAL_FAN_SPEED,
    VENTILATION_AIR_TARGET_FLOW_RATE,
    EXTRACT_AIR_ACTUAL_FAN_SPEED,
    EXTRACT_AIR_TARGET_FLOW_RATE,
    EXTRACT_AIR_HUMIDITY,
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


def create_temperature_entity_description(name, key):
    """Create an entry description for a temperature sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="hass:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
    )


def create_energy_entity_description(name, key, icon):
    """Create an entry description for a energy sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon=icon,
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
    )


def create_daily_energy_entity_description(name, key, icon):
    """Create an entry description for a energy sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon=icon,
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL,
        device_class=SensorDeviceClass.ENERGY,
    )


def create_humidity_entity_description(name, key):
    """Create an entry description for a humidity sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=PERCENTAGE,
        icon="hass:water-percent",
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
    )


def create_pressure_entity_description(name, key):
    """Create an entry description for a pressure sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
    )


def create_volume_stream_entity_description(name, key):
    """Create an entry description for a volume stream sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement="l/min",
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        has_entity_name=True,
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
    create_humidity_entity_description("Humidity HK 1", ACTUAL_HUMIDITY_HK1),
    create_humidity_entity_description("Humidity HK 2", ACTUAL_HUMIDITY_HK2),
    create_humidity_entity_description("Humidity HK 3", ACTUAL_HUMIDITY_HK3),
    create_temperature_entity_description(
        "Dew Point Temperature", DEWPOINT_TEMPERATURE
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 1", DEWPOINT_TEMPERATURE_HK1
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 2", DEWPOINT_TEMPERATURE_HK2
    ),
    create_temperature_entity_description(
        "Dew Point Temperature HK 3", DEWPOINT_TEMPERATURE_HK3
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
        "Actual Room Temperature HK 1", ACTUAL_ROOM_TEMPERATURE_HK1
    ),
    create_temperature_entity_description(
        "Target Room Temperature HK 1", TARGET_ROOM_TEMPERATURE_HK1
    ),
    create_temperature_entity_description(
        "Actual Room Temperature HK 2", ACTUAL_ROOM_TEMPERATURE_HK2
    ),
    create_temperature_entity_description(
        "Target Room Temperature HK 2", TARGET_ROOM_TEMPERATURE_HK2
    ),
    create_temperature_entity_description(
        "Actual Room Temperature HK 3", ACTUAL_ROOM_TEMPERATURE_HK3
    ),
    create_temperature_entity_description(
        "Target Room Temperature HK 3", TARGET_ROOM_TEMPERATURE_HK3
    ),
    create_temperature_entity_description("Flow Temperature", FLOW_TEMPERATURE),
    create_temperature_entity_description("Flow Temperature NHZ", FLOW_TEMPERATURE_NHZ),
    create_temperature_entity_description("Return Temperature", RETURN_TEMPERATURE),
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
    create_pressure_entity_description("Source Pressure", SOURCE_PRESSURE),
    create_temperature_entity_description("Hot Gas Temperature", HOT_GAS_TEMPERATURE),
    create_pressure_entity_description("High Pressure", HIGH_PRESSURE),
    create_pressure_entity_description("Low Pressure", LOW_PRESSURE),
    SensorEntityDescription(
        ACTIVE_ERROR,
        name="Active Error",
        has_entity_name=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert-circle",
    ),
]

ENERGYMANAGEMENT_SENSOR_TYPES = [
    SensorEntityDescription(
        SG_READY_STATE,
        name="SG Ready State",
        icon="mdi:solar-power",
        has_entity_name=True,
    )
]


ENERGY_SENSOR_TYPES = [
    create_daily_energy_entity_description(
        "Produced Heating Today",
        PRODUCED_HEATING_TODAY,
        "mdi:radiator",
    ),
    create_energy_entity_description(
        "Produced Heating Total",
        PRODUCED_HEATING_TOTAL,
        "mdi:radiator",
    ),
    create_daily_energy_entity_description(
        "Produced Water Heating Today",
        PRODUCED_WATER_HEATING_TODAY,
        "mdi:water-boiler",
    ),
    create_energy_entity_description(
        "Produced Water Heating Total",
        PRODUCED_WATER_HEATING_TOTAL,
        "mdi:water-boiler",
    ),
    create_daily_energy_entity_description(
        "Consumed Heating Today",
        CONSUMED_HEATING_TODAY,
        "mdi:lightning-bolt",
    ),
    create_energy_entity_description(
        "Consumed Heating Total",
        CONSUMED_HEATING_TOTAL,
        "mdi:lightning-bolt",
    ),
    create_daily_energy_entity_description(
        "Consumed Water Heating Today",
        CONSUMED_WATER_HEATING_TODAY,
        "mdi:lightning-bolt",
    ),
    create_energy_entity_description(
        "Consumed Water Heating Total",
        CONSUMED_WATER_HEATING_TOTAL,
        "mdi:lightning-bolt",
    ),
]


COMPRESSOR_SENSOR_TYPES = [
    SensorEntityDescription(
        COMPRESSOR_STARTS,
        name="Compressor starts",
        icon="mdi:heat-pump",
        has_entity_name=True,
    ),
    SensorEntityDescription(
        COMPRESSOR_HEATING,
        name="Compressor heating",
        icon="mdi:heat-pump",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        COMPRESSOR_HEATING_WATER,
        name="Compressor heating water",
        icon="mdi:heat-pump",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        ELECTRICAL_BOOSTER_HEATING,
        name="Electrical booster heating",
        icon="mdi:heating-coil",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        ELECTRICAL_BOOSTER_HEATING_WATER,
        name="Electrical booster heating water",
        icon="mdi:heating-coil",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
]

VENTILATION_SENSOR_TYPES = [
    SensorEntityDescription(
        VENTILATION_AIR_ACTUAL_FAN_SPEED,
        name="Ventilaction air actual fan speed",
        icon="mdi:fan",
        has_entity_name=True,
    ),
    SensorEntityDescription(
        VENTILATION_AIR_TARGET_FLOW_RATE,
        name="Ventilaction air target fan speed",
        icon="mdi:fan",
        has_entity_name=True,
    ),
    SensorEntityDescription(
        EXTRACT_AIR_ACTUAL_FAN_SPEED,
        name="Extract air actual fan speed",
        icon="mdi:fan",
        has_entity_name=True,
    ),
    SensorEntityDescription(
        EXTRACT_AIR_TARGET_FLOW_RATE,
        name="Extract air target fan speed",
        icon="mdi:fan",
        has_entity_name=True,
    ),
    create_humidity_entity_description("Extract air humidity", EXTRACT_AIR_HUMIDITY),
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in SYSTEM_VALUES_SENSOR_TYPES:
        sensor = StiebelEltronISGSensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    for description in ENERGYMANAGEMENT_SENSOR_TYPES:
        sensor = StiebelEltronISGSensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    for description in ENERGY_SENSOR_TYPES:
        sensor = StiebelEltronISGSensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    if not coordinator.is_wpm:
        for description in COMPRESSOR_SENSOR_TYPES:
            sensor = StiebelEltronISGSensor(
                coordinator,
                entry,
                description,
            )
            entities.append(sensor)
        for description in VENTILATION_SENSOR_TYPES:
            sensor = StiebelEltronISGSensor(
                coordinator,
                entry,
                description,
            )
            entities.append(sensor)

    async_add_devices(entities)


class StiebelEltronISGSensor(StiebelEltronISGEntity, SensorEntity):
    """stiebel_eltron_isg Sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        description,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get(self.entity_description.key) is not None
