"""Binary sensor platform for stiebel_eltron_isg."""


from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import StiebelEltronISGEntity
from .const import DOMAIN, IS_HEATING, IS_COOLING, IS_HEATING_WATER, IS_SUMMER_MODE, PUMP_ON_HK1, PUMP_ON_HK2, COMPRESSOR_ON, SWITCHING_PROGRAM_ENABLED, ELECTRIC_REHEATING, SERVICE, POWER_OFF, FILTER, VENTILATION, EVAPORATOR_DEFROST, FILTER_EXTRACT_AIR, FILTER_VENTILATION_AIR, HEAT_UP_PROGRAM, NHZ_STAGES_RUNNING, ERROR_STATUS

BINARY_SENSOR_TYPES = [
    BinarySensorEntityDescription(
        name="Is heating",
        key=IS_HEATING,
        icon="mdi:heat-wave",
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
    BinarySensorEntityDescription(
        name="Pump HK1",
        key=PUMP_ON_HK1,
        icon="mdi:pump",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Pump HK2",
        key=PUMP_ON_HK2,
        icon="mdi:pump",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Compressor",
        key=COMPRESSOR_ON,
        icon="mdi:heat-pump",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Switching Program Enabled",
        key=SWITCHING_PROGRAM_ENABLED,
        icon="mdi:clock-outline",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Electric Heating",
        key=ELECTRIC_REHEATING,
        icon="mdi:fence-electric",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Service",
        key=SERVICE,
        icon="mdi:account-wrench",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Power Off",
        key=POWER_OFF,
        icon="mdi:power-off",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Filter",
        key=FILTER,
        icon="mdi:air-filter",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Ventilation",
        key=VENTILATION,
        icon="mdi:fan",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Evaporator Defrost",
        key=EVAPORATOR_DEFROST,
        icon="mdi:snowflake-melt",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Filter Extract Air",
        key=FILTER_EXTRACT_AIR,
        icon="mdi:air-filter",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Filter Ventilation Air",
        key=FILTER_VENTILATION_AIR,
        icon="mdi:air-filter",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Heat-up Program",
        key=HEAT_UP_PROGRAM,
        icon="mdi:clock-outline",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="NHZ Stages Running",
        key=NHZ_STAGES_RUNNING,
        icon="mdi:fence-electric",
        has_entity_name=True,
    ),
    BinarySensorEntityDescription(
        name="Error Status",
        key=ERROR_STATUS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
        has_entity_name=True,
    ),
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in BINARY_SENSOR_TYPES:
        sensor = StiebelEltronISGBinarySensor(
            coordinator,
            entry,
            description,
        )
        entities.append(sensor)

    async_add_devices(entities)


class StiebelEltronISGBinarySensor(StiebelEltronISGEntity, BinarySensorEntity):
    """integration_blueprint binary_sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        description,
    ):
        """Initialize the binary sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the sensor."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.get(self.entity_description.key) is not None
