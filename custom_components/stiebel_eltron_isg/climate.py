"""Climate platform for stiebel_eltron_isg."""

import logging

from homeassistant.components.climate import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
    PRESET_COMFORT,
    PRESET_ECO,
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronISGIntegrationConfigEntry,
)

from .const import (
    ACTUAL_HUMIDITY,
    ACTUAL_TEMPERATURE,
    ACTUAL_TEMPERATURE_FEK,
    COMFORT_TEMPERATURE_TARGET_HK1,
    COMFORT_TEMPERATURE_TARGET_HK2,
    COMFORT_TEMPERATURE_TARGET_HK3,
    DOMAIN,
    ECO_TEMPERATURE_TARGET_HK1,
    ECO_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK3,
    FAN_LEVEL_DAY,
    FAN_LEVEL_NIGHT,
    OPERATION_MODE,
)
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

CLIMATE_HK_1 = "climate_hk_1"
CLIMATE_HK_2 = "climate_hk_2"
CLIMATE_HK_3 = "climate_hk_3"

ECO_MODE = 4

WPM_TO_HA_HVAC = {
    1: HVACMode.AUTO,
    2: HVACMode.AUTO,
    3: HVACMode.AUTO,
    4: HVACMode.AUTO,
    5: HVACMode.OFF,
    0: HVACMode.AUTO,
}

PRESET_PROGRAM = "program"
PRESET_WATER_HEATING = "water_heating"
PRESET_EMERGENCY = "emergency"
PRESET_READY = "ready"
PRESET_MANUAL = "manual"
PRESET_AUTO = "auto"


WPM_TO_HA_PRESET = {
    1: PRESET_READY,
    2: PRESET_PROGRAM,
    3: PRESET_COMFORT,
    4: PRESET_ECO,
    5: PRESET_WATER_HEATING,
    0: PRESET_EMERGENCY,
}

HA_TO_WPM_PRESET = {
    PRESET_READY: 1,
    PRESET_PROGRAM: 2,
    PRESET_COMFORT: 3,
    PRESET_ECO: 4,
    PRESET_WATER_HEATING: 5,
    PRESET_EMERGENCY: 0,
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

LWZ_TO_HA_PRESET = {
    1: PRESET_READY,
    3: PRESET_COMFORT,
    4: PRESET_ECO,
    5: PRESET_WATER_HEATING,
    11: PRESET_AUTO,
    14: PRESET_MANUAL,
    0: PRESET_EMERGENCY,
}

HA_TO_LWZ_PRESET = {
    PRESET_READY: 1,
    PRESET_COMFORT: 3,
    PRESET_ECO: 4,
    PRESET_WATER_HEATING: 5,
    PRESET_AUTO: 11,
    PRESET_MANUAL: 14,
    PRESET_EMERGENCY: 0,
}

LWZ_TO_HA_FAN = {0: FAN_OFF, 1: FAN_LOW, 2: FAN_MEDIUM, 3: FAN_HIGH}
HA_TO_LWZ_FAN = {k: i for i, k in LWZ_TO_HA_FAN.items()}


CLIMATE_TYPES = [
    ClimateEntityDescription(CLIMATE_HK_1, has_entity_name=True, name="Heat Circuit 1"),
    ClimateEntityDescription(CLIMATE_HK_2, has_entity_name=True, name="Heat Circuit 2"),
    ClimateEntityDescription(CLIMATE_HK_3, has_entity_name=True, name="Heat Circuit 3"),
]

TEMPERATURE_KEY_MAP = {
    CLIMATE_HK_1: [ECO_TEMPERATURE_TARGET_HK1, COMFORT_TEMPERATURE_TARGET_HK1],
    CLIMATE_HK_2: [ECO_TEMPERATURE_TARGET_HK2, COMFORT_TEMPERATURE_TARGET_HK2],
    CLIMATE_HK_3: [ECO_TEMPERATURE_TARGET_HK3, COMFORT_TEMPERATURE_TARGET_HK3],
}


async def async_setup_entry(
    hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronISGIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
    """Set up the select platform."""
    coordinator = entry.runtime_data.coordinator

    entities = []
    for description in CLIMATE_TYPES:
        climate_entity = (
            StiebelEltronWPMClimateEntity(coordinator, entry, description)
            if coordinator.is_wpm
            else StiebelEltronLWZClimateEntity(coordinator, entry, description)
        )
        entities.append(climate_entity)
    async_add_devices(entities)


class StiebelEltronISGClimateEntity(StiebelEltronISGEntity, ClimateEntity):
    """stiebel_eltron_isg climate class."""

    _enable_turn_on_off_backwards_compatibility = False
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    def __init__(self, coordinator, config_entry, description):
        """Initialize the climate entity."""
        self.entity_description = description

        self._attr_target_temperature_low = 5
        self._attr_target_temperature_high = 30
        self._attr_target_temperature_step = 0.1
        self._attr_translation_key = "climate"

        super().__init__(coordinator, config_entry)

    @property
    def unique_id(self) -> str | None:
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
        return (
            temperature
            if temperature is not None
            else self.coordinator.data.get(ACTUAL_TEMPERATURE_FEK)
        )

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if self.coordinator.data.get(OPERATION_MODE) == ECO_MODE:
            return self.coordinator.data.get(
                TEMPERATURE_KEY_MAP[self.entity_description.key][0],
            )
        return self.coordinator.data.get(
            TEMPERATURE_KEY_MAP[self.entity_description.key][1],
        )

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        value = kwargs["temperature"]
        if self.coordinator.data.get(OPERATION_MODE) == ECO_MODE:
            await self.coordinator.set_data(
                TEMPERATURE_KEY_MAP[self.entity_description.key][0],
                value,
            )
        else:
            await self.coordinator.set_data(
                TEMPERATURE_KEY_MAP[self.entity_description.key][1],
                value,
            )

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added.

        This only applies when fist added to the entity registry.
        """
        return (
            self.coordinator.data.get(
                TEMPERATURE_KEY_MAP[self.entity_description.key][0],
            )
            is not None
        )


class StiebelEltronWPMClimateEntity(StiebelEltronISGClimateEntity):
    """stiebel_eltron_isg climate class for wpm."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the climate entity."""
        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF]
        self._attr_preset_modes = [
            PRESET_READY,
            PRESET_PROGRAM,
            PRESET_ECO,
            PRESET_COMFORT,
            PRESET_WATER_HEATING,
            PRESET_EMERGENCY,
        ]
        super().__init__(coordinator, config_entry, description)

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return WPM_TO_HA_HVAC.get(self.coordinator.data.get(OPERATION_MODE))

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_WPM_HVAC.get(hvac_mode)
        await self.coordinator.set_data(OPERATION_MODE, new_mode)

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        return WPM_TO_HA_PRESET.get(self.coordinator.data.get(OPERATION_MODE))

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        new_mode = HA_TO_WPM_PRESET.get(preset_mode)
        await self.coordinator.set_data(OPERATION_MODE, new_mode)


class StiebelEltronLWZClimateEntity(StiebelEltronISGClimateEntity):
    """stiebel_eltron_isg climate class for lwz."""

    def __init__(self, coordinator, config_entry, description):
        """Initialize the climate entity."""
        self._attr_hvac_modes = [HVACMode.AUTO, HVACMode.OFF, HVACMode.HEAT]
        self._attr_preset_modes = [
            PRESET_READY,
            PRESET_AUTO,
            PRESET_MANUAL,
            PRESET_ECO,
            PRESET_COMFORT,
            PRESET_WATER_HEATING,
            PRESET_EMERGENCY,
        ]
        self._attr_fan_modes = [FAN_OFF, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
        super().__init__(coordinator, config_entry, description)
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
        )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return LWZ_TO_HA_HVAC.get(self.coordinator.data.get(OPERATION_MODE))

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_LWZ_HVAC.get(hvac_mode)
        await self.coordinator.set_data(OPERATION_MODE, new_mode)

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        return LWZ_TO_HA_PRESET.get(self.coordinator.data.get(OPERATION_MODE))

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        new_mode = HA_TO_LWZ_PRESET.get(preset_mode)
        await self.coordinator.set_data(OPERATION_MODE, new_mode)

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting. Requires ClimateEntityFeature.FAN_MODE."""
        if self.coordinator.data.get(OPERATION_MODE) == ECO_MODE:
            return LWZ_TO_HA_FAN.get(self.coordinator.data.get(FAN_LEVEL_NIGHT))
        return LWZ_TO_HA_FAN.get(self.coordinator.data.get(FAN_LEVEL_DAY))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        new_mode = HA_TO_LWZ_FAN.get(fan_mode)
        if self.coordinator.data.get(OPERATION_MODE) == ECO_MODE:
            await self.coordinator.set_data(FAN_LEVEL_NIGHT, new_mode)
        else:
            await self.coordinator.set_data(FAN_LEVEL_DAY, new_mode)
