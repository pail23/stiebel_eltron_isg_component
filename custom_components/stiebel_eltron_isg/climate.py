"""Climate platform for stiebel_eltron_isg."""

from dataclasses import dataclass
import logging
from typing import Any

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

from .const import DOMAIN
from .coordinator import StiebelEltronConfigEntry, StiebelEltronDataCoordinator
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

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


def _as_accessor(register_or_accessor: Any) -> Any:
    """Return an API value accessor callable for descriptor inputs."""
    if callable(register_or_accessor):
        return register_or_accessor

    raise TypeError("climate field reference must be a lambda expression")


@dataclass(frozen=True, kw_only=True)
class StiebelEltronClimateEntityDescription(ClimateEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    humidity_modbus_register: list[Any]
    actual_temperature_register: list[Any]
    eco_target_temp_register: Any
    comfort_target_temp_register: Any
    write_component: str = "system_parameters"
    eco_target_temp_write_field: str | None = None
    comfort_target_temp_write_field: str | None = None

    def __post_init__(self) -> None:
        """Convert legacy register tokens into API value accessor lambdas."""
        object.__setattr__(
            self,
            "humidity_modbus_register",
            [_as_accessor(ref) for ref in self.humidity_modbus_register],
        )
        object.__setattr__(
            self,
            "actual_temperature_register",
            [_as_accessor(ref) for ref in self.actual_temperature_register],
        )

        if not callable(self.eco_target_temp_register):
            raise TypeError("eco_target_temp_register must be a lambda expression")

        if not callable(self.comfort_target_temp_register):
            raise TypeError("comfort_target_temp_register must be a lambda expression")


WPM_CLIMATE_TYPES = [
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_1,
        translation_key=CLIMATE_HK_1,
        humidity_modbus_register=[
            lambda api: api.system_values.room_temperatures[0].relative_humidity,
            lambda api: api.system_values.relative_humidity,
        ],
        actual_temperature_register=[
            lambda api: api.system_values.room_temperatures[0].actual_temperature,
            lambda api: api.system_values.actual_temperature_fe7,
            lambda api: api.system_values.actual_temperature_fek,
        ],
        eco_target_temp_register=lambda api: api.system_parameters.eco_temperature_hk_1,
        comfort_target_temp_register=lambda api: (
            api.system_parameters.comfort_temperature_hk_1
        ),
        eco_target_temp_write_field="eco_temperature_hk_1",
        comfort_target_temp_write_field="comfort_temperature_hk_1",
    ),
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_2,
        translation_key=CLIMATE_HK_2,
        humidity_modbus_register=[
            lambda api: api.system_values.room_temperatures[1].relative_humidity
        ],
        actual_temperature_register=[
            lambda api: api.system_values.room_temperatures[1].actual_temperature
        ],
        eco_target_temp_register=lambda api: api.system_parameters.eco_temperature_hk_2,
        comfort_target_temp_register=lambda api: (
            api.system_parameters.comfort_temperature_hk_2
        ),
        eco_target_temp_write_field="eco_temperature_hk_2",
        comfort_target_temp_write_field="comfort_temperature_hk_2",
    ),
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_3,
        translation_key=CLIMATE_HK_3,
        humidity_modbus_register=[
            lambda api: api.system_values.room_temperatures[2].relative_humidity
        ],
        actual_temperature_register=[
            lambda api: api.system_values.room_temperatures[2].actual_temperature
        ],
        eco_target_temp_register=lambda api: api.system_parameters.eco_temperature_hk_3,
        comfort_target_temp_register=lambda api: (
            api.system_parameters.comfort_temperature_hk_3
        ),
        eco_target_temp_write_field="eco_temperature_hk_3",
        comfort_target_temp_write_field="comfort_temperature_hk_3",
    ),
]

LWZ_CLIMATE_TYPES = [
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_1,
        translation_key=CLIMATE_HK_1,
        humidity_modbus_register=[lambda api: api.system_values.relative_humidity_hc1],
        actual_temperature_register=[lambda api: api.system_values.actual_room_t_hc1],
        eco_target_temp_register=lambda api: (
            api.system_parameters.room_temperature_night_hk1
        ),
        comfort_target_temp_register=lambda api: (
            api.system_parameters.room_temperature_day_hk1
        ),
        eco_target_temp_write_field="room_temperature_night_hk1",
        comfort_target_temp_write_field="room_temperature_day_hk1",
    ),
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_2,
        translation_key=CLIMATE_HK_2,
        humidity_modbus_register=[lambda api: api.system_values.relative_humidity_hc2],
        actual_temperature_register=[lambda api: api.system_values.actual_room_t_hc2],
        eco_target_temp_register=lambda api: (
            api.system_parameters.room_temperature_night_hk2
        ),
        comfort_target_temp_register=lambda api: (
            api.system_parameters.room_temperature_day_hk2
        ),
        eco_target_temp_write_field="room_temperature_night_hk2",
        comfort_target_temp_write_field="room_temperature_day_hk2",
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator = entry.runtime_data

    if coordinator.is_wpm:
        entities: list[
            StiebelEltronWPMClimateEntity | StiebelEltronLWZClimateEntity
        ] = [
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

        super().__init__(coordinator, config_entry)

        self.humidity_modbus_register = description.humidity_modbus_register
        self.actual_temperature_register = description.actual_temperature_register
        self.eco_target_temp_register = description.eco_target_temp_register
        self.comfort_target_temp_register = description.comfort_target_temp_register
        self.write_component = description.write_component
        self.eco_target_temp_write_field = description.eco_target_temp_write_field
        self.comfort_target_temp_write_field = (
            description.comfort_target_temp_write_field
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success and self.target_temperature is not None
        )

    @property
    def operation_mode(self) -> int:
        """Operating mode of the heat pump."""
        raise NotImplementedError

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the climate entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    @property
    def current_humidity(self) -> int | None:
        """Return the current humidity."""
        for accessor in self.humidity_modbus_register:
            value = self._read_accessor(accessor)
            if value == 0:
                continue
            if value is not None:
                return int(value)
        return None

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        for accessor in self.actual_temperature_register:
            value = self._read_accessor(accessor)
            if value == 0:
                continue
            if value is not None:
                return value
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if self.operation_mode == ECO_MODE:
            return self._read_accessor(self.eco_target_temp_register)
        return self._read_accessor(self.comfort_target_temp_register)

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        value = kwargs["temperature"]
        field = (
            self.eco_target_temp_write_field
            if self.operation_mode == ECO_MODE
            else self.comfort_target_temp_write_field
        )
        if field is not None:
            await self._write_field(field, value)

    def _read_accessor(self, accessor: Any) -> float | int | None:
        """Read a value via accessor callable."""
        return self.coordinator.get_value(accessor)

    def _read_register(self, register: Any) -> float | int | None:
        """Read a register reference."""
        return self.coordinator.get_value(register)

    async def _write_field(self, field: str, value: float | int) -> None:
        """Write a component field reference."""
        await self.coordinator.write_component_value(
            self.write_component,
            field,
            value,
        )


class StiebelEltronWPMClimateEntity(StiebelEltronISGClimateEntity):
    """stiebel_eltron_isg climate class for wpm."""

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronClimateEntityDescription,
    ) -> None:
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
        value = self._read_register(lambda api: api.system_parameters.operating_mode)
        return int(value) if value is not None else 0

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return WPM_TO_HA_HVAC.get(self.operation_mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_WPM_HVAC.get(hvac_mode)
        if new_mode is not None:
            await self._write_field("operating_mode", new_mode)

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        return WPM_TO_HA_PRESET.get(self.operation_mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new target preset mode."""
        new_mode = HA_TO_WPM_PRESET.get(preset_mode)
        if new_mode is not None:
            await self._write_field("operating_mode", new_mode)


class StiebelEltronLWZClimateEntity(StiebelEltronISGClimateEntity):
    """stiebel_eltron_isg climate class for lwz."""

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronClimateEntityDescription,
    ) -> None:
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
        value = self._read_register(lambda api: api.system_parameters.operating_mode)
        return int(value) if value is not None else 0

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        return LWZ_TO_HA_HVAC.get(self.operation_mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        new_mode = HA_TO_LWZ_HVAC.get(hvac_mode)
        if new_mode is not None:
            await self._write_field("operating_mode", new_mode)

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        return LWZ_TO_HA_PRESET.get(self.operation_mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new target preset mode."""
        new_mode = HA_TO_LWZ_PRESET.get(preset_mode)
        if new_mode is not None:
            await self._write_field("operating_mode", new_mode)

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting. Requires ClimateEntityFeature.FAN_MODE."""
        if self.operation_mode == ECO_MODE:
            value = self._read_register(lambda api: api.system_parameters.night_stage)
            if value is None:
                return None
            return LWZ_TO_HA_FAN.get(int(value))
        value = self._read_register(lambda api: api.system_parameters.day_stage)
        if value is None:
            return None
        return LWZ_TO_HA_FAN.get(int(value))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        new_mode = HA_TO_LWZ_FAN.get(fan_mode)
        if new_mode is not None:
            if self.operation_mode == ECO_MODE:
                await self._write_field("night_stage", new_mode)
            else:
                await self._write_field("day_stage", new_mode)
