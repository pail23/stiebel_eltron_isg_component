"""Climate platform for stiebel_eltron_isg."""
import logging
from typing import Optional


from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import UnitOfTemperature


from .const import (
    DOMAIN,
    ACTUAL_HUMIDITY,
    ACTUAL_TEMPERATURE,
    ACTUAL_TEMPERATURE_FEK,
    COMFORT_TEMPERATURE_TARGET_HK1,
    OPERATION_MODE
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

CLIMATE_HK_1 = "climate_hk_1"

WPM_TO_HA_HVAC = {
    1: HVACMode.AUTO,
    2: HVACMode.AUTO,
    3: HVACMode.AUTO,
    4: HVACMode.AUTO,
    5: HVACMode.OFF,
    0: HVACMode.AUTO,
}

HA_TO_WPM_HVAC = {
    HVACMode.AUTO: 2,
    HVACMode.OFF: 5,
}

LWZ_TO_HA_HVAC = {
    11: HVACMode.AUTO,
    14: HVACMode.HEAT,
    1: HVACMode.AUTO,
    3: HVACMode.AUTO,
    4: HVACMode.AUTO,
    5: HVACMode.OFF,
    0: HVACMode.AUTO,
}

HA_TO_LWZ_HVAC = {
    HVACMode.AUTO: 11,
    HVACMode.OFF: 5,
    HVACMode.HEAT: 14,
}

CLIMATE_TYPES = [
    ClimateEntityDescription(CLIMATE_HK_1, has_entity_name=True, name="Heat Circuit 1")
]


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in CLIMATE_TYPES:
        if coordinator.is_wpm:
            climate_entity = StiebelEltronWPMClimateEntity(
                coordinator, entry, description
            ) if coordinator.is_wpm else StiebelEltronLWZClimateEntity(
                coordinator, entry, description
            )
        entities.append(climate_entity)
    async_add_devices(entities)


class StiebelEltronISGClimateEntity(StiebelEltronISGEntity, ClimateEntity):
    """stiebel_eltron_isg climate class."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the climate entity."""
        self.entity_description = description
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_target_temperature_low = 5
        self._attr_target_temperature_high = 30
        self._attr_target_temperature_step = 0.1

        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> Optional[str]:
        """Return the unique id of the climate entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def current_humidity(self) -> int | None:
        """Return the current humidity."""
        return self.coordinator.data.get(ACTUAL_HUMIDITY)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        temperature = self.coordinator.data.get(ACTUAL_TEMPERATURE)
        return temperature if temperature is not None else self.coordinator.data.get(ACTUAL_TEMPERATURE_FEK)

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get(COMFORT_TEMPERATURE_TARGET_HK1)

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        value = kwargs["temperature"]
        self.coordinator.set_data(COMFORT_TEMPERATURE_TARGET_HK1, value)


class StiebelEltronWPMClimateEntity(StiebelEltronISGClimateEntity):

    def __init__(self, coordinator, config_entry, description):
        """Initialize the climate entity."""
        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
        super().__init__(coordinator, config_entry, description)


    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return WPM_TO_HA_HVAC.get(self.coordinator.data.get(OPERATION_MODE))

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_WPM_HVAC.get(hvac_mode)
        self.coordinator.set_data(OPERATION_MODE, new_mode)


class StiebelEltronLWZClimateEntity(StiebelEltronISGClimateEntity):

    def __init__(self, coordinator, config_entry, description):
        """Initialize the climate entity."""
        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF, HVACMode.MANUAL]
        super().__init__(coordinator, config_entry, description)


    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return LWZ_TO_HA_HVAC.get(self.coordinator.data.get(OPERATION_MODE))

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_LWZ_HVAC.get(hvac_mode)
        self.coordinator.set_data(OPERATION_MODE, new_mode)