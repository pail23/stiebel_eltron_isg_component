"""Sensor platform for stiebel_eltron_isg."""

import logging


from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
import homeassistant.util.dt as dt_util
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfVolumeFlowRate,
)

from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronISGIntegrationConfigEntry,
)

from .const import (
    ACTUAL_HUMIDITY_HK1,
    ACTUAL_HUMIDITY_HK2,
    ACTUAL_HUMIDITY_HK3,
    CONSUMED_HEATING,
    CONSUMED_WATER_HEATING,
    DEWPOINT_TEMPERATURE_HK1,
    DEWPOINT_TEMPERATURE_HK2,
    DEWPOINT_TEMPERATURE_HK3,
    DOMAIN,
    ACTUAL_TEMPERATURE,
    PRODUCED_HEATING,
    PRODUCED_WATER_HEATING,
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
    ACTUAL_TEMPERATURE_HK3,
    TARGET_TEMPERATURE_HK3,
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
    RETURN_TEMPERATURE_WP1,
    FLOW_TEMPERATURE_WP1,
    HOT_GAS_TEMPERATURE_WP1,
    LOW_PRESSURE_WP1,
    HIGH_PRESSURE_WP1,
    VOLUME_STREAM_WP1,
    RETURN_TEMPERATURE_WP2,
    FLOW_TEMPERATURE_WP2,
    HOT_GAS_TEMPERATURE_WP2,
    LOW_PRESSURE_WP2,
    HIGH_PRESSURE_WP2,
    VOLUME_STREAM_WP2,
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
    ACTUAL_TEMPERATURE_COOLING_FANCOIL,
    TARGET_TEMPERATURE_COOLING_FANCOIL,
    ACTUAL_TEMPERATURE_COOLING_SURFACE,
    TARGET_TEMPERATURE_COOLING_SURFACE,
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


def create_temperature_entity_description(name, key):
    """Create an entry description for a temperature sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        has_entity_name=True,
    )


def create_energy_entity_description(name, key, visible_default=True):
    """Create an entry description for a energy sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:meter-electric",
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=visible_default,
    )


def create_daily_energy_entity_description(name, key, visible_default=True):
    """Create an entry description for a energy sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:meter-electric",
        has_entity_name=True,
        state_class=SensorStateClass.TOTAL,
        device_class=SensorDeviceClass.ENERGY,
        entity_registry_visible_default=visible_default,
    )


def create_humidity_entity_description(name, key):
    """Create an entry description for a humidity sensor."""
    return SensorEntityDescription(
        key,
        name=name,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
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
        "Actual Temperature HK 3", ACTUAL_TEMPERATURE_HK3
    ),
    create_temperature_entity_description(
        "Target Temperature HK 3", TARGET_TEMPERATURE_HK3
    ),
    create_temperature_entity_description(
        "Actual Temperature Cooling Fancoil", ACTUAL_TEMPERATURE_COOLING_FANCOIL
    ),
    create_temperature_entity_description(
        "Target Temperature Cooling Fancoil", TARGET_TEMPERATURE_COOLING_FANCOIL
    ),
    create_temperature_entity_description(
        "Actual Temperature Cooling Surface", ACTUAL_TEMPERATURE_COOLING_SURFACE
    ),
    create_temperature_entity_description(
        "Target Temperature Cooling Surface", TARGET_TEMPERATURE_COOLING_SURFACE
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
    create_temperature_entity_description(
        "Return Temperature WP1", RETURN_TEMPERATURE_WP1
    ),
    create_temperature_entity_description("Flow Temperature WP1", FLOW_TEMPERATURE_WP1),
    create_temperature_entity_description(
        "Hot Gas Temperature WP1", HOT_GAS_TEMPERATURE_WP1
    ),
    create_pressure_entity_description("Low Pressure WP1", LOW_PRESSURE_WP1),
    create_pressure_entity_description("High Pressure WP1", HIGH_PRESSURE_WP1),
    create_volume_stream_entity_description("Volume Stream WP1", VOLUME_STREAM_WP1),
    create_temperature_entity_description(
        "Return Temperature WP2", RETURN_TEMPERATURE_WP2
    ),
    create_temperature_entity_description("Flow Temperature WP2", FLOW_TEMPERATURE_WP2),
    create_temperature_entity_description(
        "Hot Gas Temperature WP2", HOT_GAS_TEMPERATURE_WP2
    ),
    create_pressure_entity_description("Low Pressure WP2", LOW_PRESSURE_WP2),
    create_pressure_entity_description("High Pressure WP2", HIGH_PRESSURE_WP2),
    create_volume_stream_entity_description("Volume Stream WP2", VOLUME_STREAM_WP2),
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
    create_energy_entity_description(
        "Produced Heating Total",
        PRODUCED_HEATING_TOTAL,
    ),
    create_energy_entity_description(
        "Produced Heating",
        PRODUCED_HEATING,
    ),
    create_energy_entity_description(
        "Produced Water Heating Total",
        PRODUCED_WATER_HEATING_TOTAL,
    ),
    create_energy_entity_description("Produced Water Heating", PRODUCED_WATER_HEATING),
    create_energy_entity_description(
        "Consumed Heating Total",
        CONSUMED_HEATING_TOTAL,
    ),
    create_energy_entity_description(
        "Consumed Heating",
        CONSUMED_HEATING,
    ),
    create_energy_entity_description(
        "Consumed Water Heating Total",
        CONSUMED_WATER_HEATING_TOTAL,
    ),
    create_energy_entity_description(
        "Consumed Water Heating",
        CONSUMED_WATER_HEATING,
    ),
]

ENERGY_DAILY_SENSOR_TYPES = [
    create_daily_energy_entity_description(
        "Produced Heating Today",
        PRODUCED_HEATING_TODAY,
    ),
    create_daily_energy_entity_description(
        "Produced Water Heating Today",
        PRODUCED_WATER_HEATING_TODAY,
    ),
    create_daily_energy_entity_description(
        "Consumed Heating Today",
        CONSUMED_HEATING_TODAY,
    ),
    create_daily_energy_entity_description(
        "Consumed Water Heating Today",
        CONSUMED_WATER_HEATING_TODAY,
    ),
]


COMPRESSOR_SENSOR_TYPES = [
    SensorEntityDescription(
        COMPRESSOR_STARTS,
        name="Compressor starts",
        icon="mdi:restart",
        has_entity_name=True,
    ),
    SensorEntityDescription(
        COMPRESSOR_HEATING,
        name="Compressor heating",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        COMPRESSOR_HEATING_WATER,
        name="Compressor heating water",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        ELECTRICAL_BOOSTER_HEATING,
        name="Electrical booster heating",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        ELECTRICAL_BOOSTER_HEATING_WATER,
        name="Electrical booster heating water",
        icon="mdi:hours-24",
        has_entity_name=True,
        native_unit_of_measurement="h",
        state_class=SensorStateClass.MEASUREMENT,
    ),
]

VENTILATION_SENSOR_TYPES = [
    SensorEntityDescription(
        VENTILATION_AIR_ACTUAL_FAN_SPEED,
        name="Ventilation air actual fan speed",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        VENTILATION_AIR_TARGET_FLOW_RATE,
        name="Ventilation air target fan speed",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        EXTRACT_AIR_ACTUAL_FAN_SPEED,
        name="Extract air actual fan speed",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        EXTRACT_AIR_TARGET_FLOW_RATE,
        name="Extract air target fan speed",
        icon="mdi:fan",
        has_entity_name=True,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    create_humidity_entity_description("Extract air humidity", EXTRACT_AIR_HUMIDITY),
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: StiebelEltronISGIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

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

    for description in ENERGY_DAILY_SENSOR_TYPES:
        sensor = StiebelEltronISGEnergySensor(
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


class StiebelEltronISGEnergySensor(StiebelEltronISGEntity, SensorEntity):
    """stiebel_eltron_isg Energy Sensor class."""

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

    @property
    def last_reset(self):
        """Set Last Reset to now, if value is 0."""
        value = self.coordinator.data.get(self.entity_description.key)
        if value is not None and value == 0:
            return dt_util.utcnow()
        else:
            return None
