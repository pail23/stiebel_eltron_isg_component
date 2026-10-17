"""Climate platform for stiebel_eltron_isg."""

from dataclasses import dataclass
import logging
import math
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
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pystiebeleltron import ControllerModel

from .const import DOMAIN
from .coordinator import AnyStiebelEltronDataCoordinator, StiebelEltronConfigEntry
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

CLIMATE_HK_1 = "climate_hk_1"
CLIMATE_HK_2 = "climate_hk_2"
CLIMATE_HK_3 = "climate_hk_3"
CLIMATE_HK_4 = "climate_hk_4"
CLIMATE_HK_5 = "climate_hk_5"

ECO_MODE = 4
MANUAL_MODE = 14

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
    MANUAL_MODE: HVACMode.HEAT,
    1: HVACMode.AUTO,
    3: HVACMode.AUTO,
    4: HVACMode.AUTO,
    5: HVACMode.OFF,
    0: HVACMode.AUTO,
}

HA_TO_LWZ_HVAC = {
    HVACMode.AUTO: 11,
    HVACMode.OFF: 5,
    HVACMode.HEAT: MANUAL_MODE,
}

LWZ_TO_HA_PRESET = {
    1: PRESET_READY,
    3: PRESET_COMFORT,
    4: PRESET_ECO,
    5: PRESET_WATER_HEATING,
    11: PRESET_AUTO,
    MANUAL_MODE: PRESET_MANUAL,
    0: PRESET_EMERGENCY,
}

HA_TO_LWZ_PRESET = {
    PRESET_READY: 1,
    PRESET_COMFORT: 3,
    PRESET_ECO: 4,
    PRESET_WATER_HEATING: 5,
    PRESET_AUTO: 11,
    PRESET_MANUAL: MANUAL_MODE,
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
    min_temp: float
    max_temp: float
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


WPM_3I_CLIMATE_TYPES = [
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_1,
        translation_key=CLIMATE_HK_1,
        humidity_modbus_register=[
            lambda api: api.system_values.relative_humidity,
        ],
        actual_temperature_register=[
            lambda api: api.system_values.actual_temperature_fe7,
            lambda api: api.system_values.actual_temperature_fek,
        ],
        eco_target_temp_register=lambda api: api.system_parameters.eco_temperature_hk_1,
        comfort_target_temp_register=lambda api: (
            api.system_parameters.comfort_temperature_hk_1
        ),
        min_temp=5,
        max_temp=30,
        eco_target_temp_write_field="eco_temperature_hk_1",
        comfort_target_temp_write_field="comfort_temperature_hk_1",
    ),
    StiebelEltronClimateEntityDescription(
        key=CLIMATE_HK_2,
        translation_key=CLIMATE_HK_2,
        # The WPM 3i API exposes no room temperature or humidity assigned to HK2.
        humidity_modbus_register=[],
        actual_temperature_register=[],
        eco_target_temp_register=lambda api: api.system_parameters.eco_temperature_hk_2,
        comfort_target_temp_register=lambda api: (
            api.system_parameters.comfort_temperature_hk_2
        ),
        min_temp=5,
        max_temp=30,
        eco_target_temp_write_field="eco_temperature_hk_2",
        comfort_target_temp_write_field="comfort_temperature_hk_2",
    ),
]

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
        min_temp=5,
        max_temp=30,
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
        min_temp=5,
        max_temp=30,
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
        min_temp=5,
        max_temp=30,
        eco_target_temp_write_field="eco_temperature_hk_3",
        comfort_target_temp_write_field="comfort_temperature_hk_3",
    ),
]


def _extension_circuit_climate(
    circuit: int, key: str
) -> StiebelEltronClimateEntityDescription:
    """Describe heating circuit 4 or 5, which need the WPE extension module.

    Only WPMsystem supports the module, and the entity is registered disabled,
    like the circuit's sensors.
    """
    index = circuit - 1
    comfort_field = f"comfort_temperature_hk_{circuit}"
    eco_field = f"eco_temperature_hk_{circuit}"
    return StiebelEltronClimateEntityDescription(
        key=key,
        translation_key=key,
        entity_registry_enabled_default=False,
        humidity_modbus_register=[
            lambda api: api.system_values.room_temperatures[index].relative_humidity
        ],
        actual_temperature_register=[
            lambda api: api.system_values.room_temperatures[index].actual_temperature
        ],
        eco_target_temp_register=lambda api: getattr(api.system_parameters, eco_field),
        comfort_target_temp_register=lambda api: getattr(
            api.system_parameters, comfort_field
        ),
        min_temp=5,
        max_temp=30,
        eco_target_temp_write_field=eco_field,
        comfort_target_temp_write_field=comfort_field,
    )


WPMSYSTEM_CLIMATE_TYPES = [
    *WPM_CLIMATE_TYPES,
    _extension_circuit_climate(4, CLIMATE_HK_4),
    _extension_circuit_climate(5, CLIMATE_HK_5),
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
        min_temp=10,
        max_temp=30,
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
        min_temp=10,
        max_temp=30,
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
    entities: list[StiebelEltronWPMClimateEntity | StiebelEltronLWZClimateEntity] = []
    if coordinator.model == ControllerModel.WPM_3i:
        entities = [
            StiebelEltronWPMClimateEntity(
                coordinator,
                entry,
                description,
            )
            for description in WPM_3I_CLIMATE_TYPES
        ]
    elif coordinator.model in (
        ControllerModel.WPM_3,
        ControllerModel.WPMsystem,
        ControllerModel.LWZ_R290,
    ):
        entities = [
            StiebelEltronWPMClimateEntity(
                coordinator,
                entry,
                description,
            )
            for description in (
                WPMSYSTEM_CLIMATE_TYPES
                if coordinator.model == ControllerModel.WPMsystem
                else WPM_CLIMATE_TYPES
            )
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
        coordinator: AnyStiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronClimateEntityDescription,
    ) -> None:
        """Initialize the climate entity."""
        self.entity_description = description

        self._attr_min_temp = description.min_temp
        self._attr_max_temp = description.max_temp
        self._attr_target_temperature_low = description.min_temp
        self._attr_target_temperature_high = description.max_temp
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
        """Return True if entity is available.

        While the operating mode is unknown the entity stays available as long
        as a setpoint register answers: Home Assistant passes no service call
        to an unavailable entity, and changing the mode is the way out of that
        state.
        """
        if not self.coordinator.last_update_success:
            return False
        if self.operation_mode is None:
            return any(
                self._read_accessor(register) is not None
                for register in (
                    self.comfort_target_temp_register,
                    self.eco_target_temp_register,
                )
            )
        return self.target_temperature is not None

    @property
    def operation_mode(self) -> int | None:
        """Return the raw operating mode, or None while the device reports none.

        The unavailable marker must not be replaced by a real mode: 0 is the
        emergency mode, so a fallback to 0 would show and write as if the heat
        pump were in emergency operation.

        A mode written moments ago counts before the device confirmed it, so a
        setpoint that follows a mode change goes to the field of the new mode.
        """
        value = self._read_written_or_device(
            "operating_mode", lambda api: api.system_parameters.operating_mode
        )
        return int(value) if value is not None else None

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
    def _target_temp_write_field(self) -> str | None:
        """Return the field the current operating mode takes its target from.

        None while the operating mode is unknown: without it there is no way to
        tell which of the two setpoints applies.
        """
        mode = self.operation_mode
        if mode is None:
            return None
        if mode == ECO_MODE:
            return self.eco_target_temp_write_field
        return self.comfort_target_temp_write_field

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach.

        A written target only holds for the field it was written to. Once the
        operating mode makes the other field the target, it no longer applies,
        whoever changed that mode.
        """
        mode = self.operation_mode
        if mode is None:
            return None
        if mode == ECO_MODE:
            return self._read_written_or_device(
                self.eco_target_temp_write_field, self.eco_target_temp_register
            )
        return self._read_written_or_device(
            self.comfort_target_temp_write_field, self.comfort_target_temp_register
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        value = kwargs["temperature"]
        async with self.coordinator.write_lock:
            # The field depends on the mode, which another entity may be
            # writing right now, so it is chosen under the same lock.
            field = self._target_temp_write_field
            if field is None:
                raise HomeAssistantError(
                    translation_domain=DOMAIN,
                    translation_key="operating_mode_unknown",
                )
            current = self.target_temperature
            if current is not None and math.isclose(current, value, abs_tol=1e-9):
                return

            await self._write_field(field, value)

    async def _async_write_operating_mode(self, new_mode: int | None) -> None:
        """Write a raw operating mode unless the controller already runs it.

        Several raw modes map to one Home Assistant mode, so the controller
        value is compared, not the mapped one.
        """
        if new_mode is None:
            return
        async with self.coordinator.write_lock:
            if self.operation_mode != new_mode:
                await self._write_field("operating_mode", new_mode)

    def _read_accessor(self, accessor: Any) -> float | int | None:
        """Read a value via accessor callable."""
        return self.coordinator.get_value(accessor)

    def _read_written_or_device(
        self, field: str | None, accessor: Any
    ) -> float | int | None:
        """Return the value written to ``field`` until the device confirmed it."""
        pending = self.coordinator.pending_value(self.write_component, field)
        if pending is not None:
            return pending
        return self.coordinator.get_value(accessor)

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
        coordinator: AnyStiebelEltronDataCoordinator,
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
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        mode = self.operation_mode
        return WPM_TO_HA_HVAC.get(mode) if mode is not None else None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        await self._async_write_operating_mode(HA_TO_WPM_HVAC.get(hvac_mode))

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        mode = self.operation_mode
        return WPM_TO_HA_PRESET.get(mode) if mode is not None else None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new target preset mode."""
        await self._async_write_operating_mode(HA_TO_WPM_PRESET.get(preset_mode))


class StiebelEltronLWZClimateEntity(StiebelEltronISGClimateEntity):
    """stiebel_eltron_isg climate class for lwz."""

    def __init__(
        self,
        coordinator: AnyStiebelEltronDataCoordinator,
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
        self._attr_supported_features |= ClimateEntityFeature.FAN_MODE

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. heat, cool, idle."""
        mode = self.operation_mode
        return LWZ_TO_HA_HVAC.get(mode) if mode is not None else None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        await self._async_write_operating_mode(HA_TO_LWZ_HVAC.get(hvac_mode))

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        mode = self.operation_mode
        return LWZ_TO_HA_PRESET.get(mode) if mode is not None else None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new target preset mode."""
        await self._async_write_operating_mode(HA_TO_LWZ_PRESET.get(preset_mode))

    @property
    def _fan_stage_field(self) -> str:
        """Select the fan stage used by the current operating mode."""
        if self.operation_mode == ECO_MODE:
            return "night_stage"
        if self.operation_mode == MANUAL_MODE:
            return "manual_stage"
        return "day_stage"

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting. Requires ClimateEntityFeature.FAN_MODE."""
        field = self._fan_stage_field
        value = self._read_written_or_device(
            field, lambda api: getattr(api.system_parameters, field)
        )
        if value is None:
            return None
        return LWZ_TO_HA_FAN.get(int(value))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        new_mode = HA_TO_LWZ_FAN.get(fan_mode)
        if new_mode is None:
            return
        async with self.coordinator.write_lock:
            if self.fan_mode != fan_mode:
                await self._write_field(self._fan_stage_field, new_mode)
