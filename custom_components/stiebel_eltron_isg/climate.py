"""Climate platform for stiebel_eltron_isg."""

import logging
from dataclasses import dataclass

from homeassistant.components.climate import ClimateEntity, ClimateEntityDescription
from homeassistant.components.climate.const import (
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
    PRESET_COMFORT,
    PRESET_ECO,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pystiebeleltron import IsgRegisters
from pystiebeleltron.lwz import (
    LwzSystemParametersRegisters,
    LwzSystemValuesRegisters,
)
from pystiebeleltron.wpm import (
    WpmSystemParametersRegisters,
    WpmSystemValuesRegisters,
)

from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)

from .const import (
    DOMAIN,
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


@dataclass(frozen=True, kw_only=True)
class StiebelEltronClimateEntityDescription(ClimateEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    humidity_modbus_register: list[IsgRegisters]
    actual_temperature_register: list[IsgRegisters]
    eco_target_temp_register: IsgRegisters
    comfort_target_temp_register: IsgRegisters


WPM_CLIMATE_TYPES = [
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_1,
        has_entity_name=True,
        name="Heat Circuit 1",
        humidity_modbus_register=[
            WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC1,
            WpmSystemValuesRegisters.RELATIVE_HUMIDITY,
        ],
        actual_temperature_register=[
            WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC1,
            WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FE7,
            WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FEK,
        ],
        eco_target_temp_register=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_1,
        comfort_target_temp_register=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_1,
    ),
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_2,
        has_entity_name=True,
        name="Heat Circuit 2",
        humidity_modbus_register=[
            WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC2
        ],
        actual_temperature_register=[
            WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC2
        ],
        eco_target_temp_register=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_2,
        comfort_target_temp_register=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_2,
    ),
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_3,
        has_entity_name=True,
        name="Heat Circuit 3",
        humidity_modbus_register=[
            WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC3
        ],
        actual_temperature_register=[
            WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC3
        ],
        eco_target_temp_register=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_3,
        comfort_target_temp_register=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_3,
    ),
]

LWZ_CLIMATE_TYPES = [
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_1,
        has_entity_name=True,
        name="Heat Circuit 1",
        humidity_modbus_register=[LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC1],
        actual_temperature_register=[LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC1],
        eco_target_temp_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK1,
        comfort_target_temp_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1,
    ),
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_2,
        has_entity_name=True,
        name="Heat Circuit 2",
        humidity_modbus_register=[LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC2],
        actual_temperature_register=[LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC2],
        eco_target_temp_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK2,
        comfort_target_temp_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK2,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
    """Set up the select platform."""
    coordinator = entry.runtime_data.coordinator

    if coordinator.is_wpm:
        entities = [
            StiebelEltronWPMClimateEntity(
                coordinator,
                entry,
                description,
            )
            for description in WPM_CLIMATE_TYPES
        ]
    else:
        entities = [
            StiebelEltronLWZClimateEntity(
                coordinator,
                entry,
                description,
            )
            for description in LWZ_CLIMATE_TYPES
        ]

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

    def __init__(
        self,
        coordinator,
        config_entry,
        description: StiebelEltronClimateEntityDescription,
    ):
        """Initialize the climate entity."""
        self.entity_description = description

        self._attr_target_temperature_low = 5
        self._attr_target_temperature_high = 30
        self._attr_target_temperature_step = 0.1
        self._attr_translation_key = "climate"

        super().__init__(coordinator, config_entry)

        self.humidity_modbus_register = description.humidity_modbus_register
        self.actual_temperature_register = description.actual_temperature_register
        self.eco_target_temp_register = description.eco_target_temp_register
        self.comfort_target_temp_register = description.comfort_target_temp_register

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.target_temperature is not None

    @property
    def operation_mode(self) -> int:
        """Operating mode of the heat pump."""
        raise NotImplementedError()

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the climate entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def current_humidity(self) -> int | None:
        """Return the current humidity."""
        for register in self.humidity_modbus_register:
            if self.coordinator.get_register_value(register) is not None:
                return int(self.coordinator.get_register_value(register))
        return None

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        for register in self.actual_temperature_register:
            if self.coordinator.get_register_value(register) is not None:
                return self.coordinator.get_register_value(register)
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if self.operation_mode == ECO_MODE:
            return self.coordinator.get_register_value(self.eco_target_temp_register)
        return self.coordinator.get_register_value(self.comfort_target_temp_register)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        value = kwargs["temperature"]
        if self.operation_mode == ECO_MODE:
            await self.coordinator.write_register(
                self.eco_target_temp_register,
                value,
            )
        else:
            await self.coordinator.write_register(
                self.comfort_target_temp_register,
                value,
            )


class StiebelEltronWPMClimateEntity(StiebelEltronISGClimateEntity):
    """stiebel_eltron_isg climate class for wpm."""

    def __init__(
        self,
        coordinator,
        config_entry,
        description: StiebelEltronClimateEntityDescription,
    ):
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
    def operation_mode(self) -> int:
        """Operating mode of the heat pump."""
        return int(
            self.coordinator.get_register_value(
                WpmSystemParametersRegisters.OPERATING_MODE
            )
        )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return WPM_TO_HA_HVAC.get(self.operation_mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_WPM_HVAC.get(hvac_mode)
        if new_mode is not None:
            await self.coordinator.write_register(
                WpmSystemParametersRegisters.OPERATING_MODE, new_mode
            )

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        return WPM_TO_HA_PRESET.get(self.operation_mode)

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        new_mode = HA_TO_WPM_PRESET.get(preset_mode)
        if new_mode is not None:
            await self.coordinator.write_register(
                WpmSystemParametersRegisters.OPERATING_MODE, new_mode
            )


class StiebelEltronLWZClimateEntity(StiebelEltronISGClimateEntity):
    """stiebel_eltron_isg climate class for lwz."""

    def __init__(
        self,
        coordinator,
        config_entry,
        description: StiebelEltronClimateEntityDescription,
    ):
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
    def operation_mode(self) -> int:
        """Operating mode of the heat pump."""
        return int(
            self.coordinator.get_register_value(
                LwzSystemParametersRegisters.OPERATING_MODE
            )
        )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return LWZ_TO_HA_HVAC.get(self.operation_mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_LWZ_HVAC.get(hvac_mode)
        if new_mode is not None:
            await self.coordinator.write_register(
                LwzSystemParametersRegisters.OPERATING_MODE, new_mode
            )

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        return LWZ_TO_HA_PRESET.get(self.operation_mode)

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        new_mode = HA_TO_LWZ_PRESET.get(preset_mode)
        if new_mode is not None:
            await self.coordinator.write_register(
                LwzSystemParametersRegisters.OPERATING_MODE, new_mode
            )

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting. Requires ClimateEntityFeature.FAN_MODE."""
        if self.coordinator.data.get(OPERATION_MODE) == ECO_MODE:
            return LWZ_TO_HA_FAN.get(
                int(
                    self.coordinator.get_register_value(
                        LwzSystemParametersRegisters.NIGHT_STAGE
                    )
                )
            )
        return LWZ_TO_HA_FAN.get(
            int(
                self.coordinator.get_register_value(
                    LwzSystemParametersRegisters.DAY_STAGE
                )
            )
        )

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        new_mode = HA_TO_LWZ_FAN.get(fan_mode)
        if new_mode is not None:
            if self.coordinator.data.get(OPERATION_MODE) == ECO_MODE:
                await self.coordinator.write_register(
                    LwzSystemParametersRegisters.NIGHT_STAGE, new_mode
                )
            else:
                await self.coordinator.write_register(
                    LwzSystemParametersRegisters.DAY_STAGE, new_mode
                )
