"""Climate platform for stiebel_eltron_isg."""
import logging
from typing import Optional


from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature


from .const import (
    DOMAIN,
    ACTUAL_HUMIDITY,
    ACTUAL_TEMPERATURE_FEK,
    COMFORT_TEMPERATURE_TARGET_HK1,
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

CLIMATE_HK_1 = "climate_hk_1"

CLIMATE_HK_1_MAPPING = {
    "humidity": ACTUAL_HUMIDITY,
    "actual_temperature": ACTUAL_TEMPERATURE_FEK,
    "target_temperature": COMFORT_TEMPERATURE_TARGET_HK1,
}


CLIMATE_TYPES = [
    ClimateEntityDescription(CLIMATE_HK_1, has_entity_name=True, name="Heat Circuit 1")
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in CLIMATE_TYPES:
        climate_entity = StiebelEltronISGClimateEntity(
            coordinator, entry, description, CLIMATE_HK_1_MAPPING
        )
        entities.append(climate_entity)
    async_add_devices(entities)


class StiebelEltronISGClimateEntity(StiebelEltronISGEntity, ClimateEntity):
    """stiebel_eltron_isg select class."""

    def __init__(self, coordinator, config_entry, description, mapping):
        """Initialize the select entity."""
        self.entity_description = description
        self.mapping = mapping
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_target_temperature_low = 5
        self._attr_target_temperature_high = 30
        self._attr_target_temperature_step = 0.1

        # todo: implement this
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
        self._attr_hvac_mode = HVACMode.HEAT

        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> Optional[str]:
        """Return the unique id of the climate entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def current_humidity(self) -> int | None:
        """Return the current humidity."""
        return self.coordinator.data.get(self.mapping["humidity"])

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.get(self.mapping["actual_temperature"])

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get(self.mapping["target_temperature"])

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        value = kwargs["temperature"]
        self.coordinator.set_data(self.mapping["target_temperature"], value)
