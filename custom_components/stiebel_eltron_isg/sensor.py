"""Sensor platform for stiebel_eltron_isg."""
import logging
from typing import Optional


from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    ENERGY_KILO_WATT_HOUR,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfPressure,
)

from .const import (
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
    RETURN_TEMPERATURE,
    ACTUAL_TEMPERATURE_BUFFER,
    TARGET_TEMPERATURE_BUFFER,
    ACTUAL_TEMPERATURE_WATER,
    TARGET_TEMPERATURE_WATER,
    SOURCE_TEMPERATURE,
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
        state_class=STATE_CLASS_MEASUREMENT,
        has_entity_name=True,
    )


def create_humidity_entity_description(name, key):
    """Create an entry description for a humidity sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=PERCENTAGE,
        icon="hass:water-percent",
        state_class=STATE_CLASS_MEASUREMENT,
        has_entity_name=True,
    )


def create_pressure_entity_description(name, key):
    """Create an entry description for a pressure sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfPressure.BAR,
        icon="mdi:gauge",
        state_class=STATE_CLASS_MEASUREMENT,
        has_entity_name=True,
    )


def create_volume_stream_entity_description(name, key):
    """Create an entry description for a volume stream sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement="l/min",
        icon="mdi:gauge",
        state_class=STATE_CLASS_MEASUREMENT,
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
    create_temperature_entity_description("Flow Temperature", FLOW_TEMPERATURE),
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
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        COMPRESSOR_HEATING_WATER,
        name="Compressor heating water",
        icon="mdi:heat-pump",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        ELECTRICAL_BOOSTER_HEATING,
        name="Electrical booster heating",
        icon="mdi:heating-coil",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    SensorEntityDescription(
        ELECTRICAL_BOOSTER_HEATING_WATER,
        name="Electrical booster heating water",
        icon="mdi:heating-coil",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=STATE_CLASS_MEASUREMENT,
    ),
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

    for meter_sensor_info in ENERGY_SENSOR_TYPES:
        description = SensorEntityDescription(
            name=f"{meter_sensor_info[0]}",
            key=meter_sensor_info[1],
            native_unit_of_measurement=meter_sensor_info[2],
            icon=meter_sensor_info[3],
            state_class=STATE_CLASS_MEASUREMENT,
            has_entity_name=True,
        )
        if description.native_unit_of_measurement == ENERGY_KILO_WATT_HOUR:
            description.state_class = STATE_CLASS_TOTAL_INCREASING
            description.device_class = DEVICE_CLASS_ENERGY

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
    def unique_id(self) -> Optional[str]:
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
