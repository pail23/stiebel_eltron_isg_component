"""Sensor number for stiebel_eltron_isg."""

from dataclasses import dataclass, replace
import math
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pystiebeleltron import ControllerModel

from .const import (
    AREA_COOLING_FLOW_TEMPERATURE_HYSTERESIS,
    AREA_COOLING_TARGET_FLOW_TEMPERATURE,
    AREA_COOLING_TARGET_ROOM_TEMPERATURE,
    COMFORT_COOLING_TEMPERATURE_TARGET_HK1,
    COMFORT_COOLING_TEMPERATURE_TARGET_HK2,
    COMFORT_TEMPERATURE_TARGET_HK1,
    COMFORT_TEMPERATURE_TARGET_HK2,
    COMFORT_TEMPERATURE_TARGET_HK3,
    COMFORT_TEMPERATURE_TARGET_HK4,
    COMFORT_TEMPERATURE_TARGET_HK5,
    COMFORT_WATER_TEMPERATURE_TARGET,
    DOMAIN,
    DUALMODE_TEMPERATURE_HZG,
    DUALMODE_TEMPERATURE_WW,
    ECO_COOLING_TEMPERATURE_TARGET_HK1,
    ECO_COOLING_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK1,
    ECO_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK3,
    ECO_TEMPERATURE_TARGET_HK4,
    ECO_TEMPERATURE_TARGET_HK5,
    ECO_WATER_TEMPERATURE_TARGET,
    FAN_COOLING_FLOW_TEMPERATURE_HYSTERESIS,
    FAN_COOLING_TARGET_FLOW_TEMPERATURE,
    FAN_COOLING_TARGET_ROOM_TEMPERATURE,
    FAN_LEVEL_DAY,
    FAN_LEVEL_MANUAL,
    FAN_LEVEL_NIGHT,
    FAN_LEVEL_PARTY,
    HEATING_CURVE_LOW_END_HK1,
    HEATING_CURVE_LOW_END_HK2,
    HEATING_CURVE_RISE_HK1,
    HEATING_CURVE_RISE_HK2,
    HEATING_CURVE_RISE_HK3,
    HEATING_CURVE_RISE_HK4,
    HEATING_CURVE_RISE_HK5,
    MANUAL_HC_SET_HK1,
    MANUAL_HC_SET_HK2,
    MANUAL_WATER_TEMPERATURE_TARGET,
    VENTILATION_STAGE_COMFORT,
    VENTILATION_STAGE_ECO,
    VENTILATION_STAGE_STANDBY,
)
from .coordinator import (
    ControllerFamily,
    StiebelEltronConfigEntry,
    StiebelEltronDataCoordinator,
)
from .entity import StiebelEltronISGEntity, ValueAccessor, async_add_when_served

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class StiebelEltronNumberEntityDescription(NumberEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    entity_category: EntityCategory | None = EntityCategory.CONFIG
    modbus_register: ValueAccessor
    write_component: str = "system_parameters"
    write_field: str | None = None
    enforce_step: bool = False


def number_mode(description: StiebelEltronNumberEntityDescription) -> NumberMode:
    """Return how the frontend should offer a number for input.

    Home Assistant picks a slider whenever a range has at most 256 steps, which
    covers nearly every temperature here at 0.1 degree steps and makes an exact
    setpoint hard to hit (#537). Temperatures therefore get an input box, while
    fan levels and the heating curve rise keep the automatic choice.
    """
    if description.mode is not None:
        return description.mode
    if description.native_unit_of_measurement in (
        UnitOfTemperature.CELSIUS,
        UnitOfTemperature.KELVIN,
    ):
        return NumberMode.BOX
    return NumberMode.AUTO


def number_device_class(
    description: StiebelEltronNumberEntityDescription,
) -> NumberDeviceClass | None:
    """Return the device class a number's unit stands for.

    Home Assistant converts a temperature to the unit system of the instance
    only when the device class says it is one. A hysteresis is a difference,
    which converts without the offset of the scale.
    """
    if description.device_class is not None:
        return description.device_class
    if description.native_unit_of_measurement == UnitOfTemperature.CELSIUS:
        return NumberDeviceClass.TEMPERATURE
    if description.native_unit_of_measurement == UnitOfTemperature.KELVIN:
        return NumberDeviceClass.TEMPERATURE_DELTA
    return None


def _number(
    key: str,
    field: str,
    minimum: float,
    maximum: float,
    step: float,
    **kwargs: Any,
) -> StiebelEltronNumberEntityDescription:
    """Describe a number that reads and writes one library field."""
    component = kwargs.setdefault("write_component", "system_parameters")
    return StiebelEltronNumberEntityDescription(
        key=key,
        translation_key=key,
        native_min_value=minimum,
        native_max_value=maximum,
        native_step=step,
        modbus_register=lambda api: getattr(getattr(api, component), field),
        write_field=field,
        **kwargs,
    )


def _temperature(
    key: str,
    field: str,
    minimum: float,
    maximum: float,
    step: float = 0.1,
    **kwargs: Any,
) -> StiebelEltronNumberEntityDescription:
    """Describe a temperature setpoint in degrees Celsius."""
    return _number(
        key,
        field,
        minimum,
        maximum,
        step,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        **kwargs,
    )


def _hysteresis(key: str, field: str) -> StiebelEltronNumberEntityDescription:
    """Describe a flow temperature hysteresis of 1 to 5 K."""
    return _number(
        key, field, 1, 5, 0.1, native_unit_of_measurement=UnitOfTemperature.KELVIN
    )


def _curve_rise(
    key: str, field: str, maximum: float = 3, **kwargs: Any
) -> StiebelEltronNumberEntityDescription:
    """Describe the unitless rise of a heating curve."""
    return _number(key, field, 0, maximum, 0.01, **kwargs)


def _stage(key: str, field: str, **kwargs: Any) -> StiebelEltronNumberEntityDescription:
    """Describe a fan or ventilation stage, a whole number from 0 to 3."""
    return _number(key, field, 0, 3, 1, enforce_step=True, **kwargs)


NUMBER_TYPES_WPM_3I = [
    _temperature(COMFORT_TEMPERATURE_TARGET_HK1, "comfort_temperature_hk_1", 5, 30),
    _temperature(ECO_TEMPERATURE_TARGET_HK1, "eco_temperature_hk_1", 5, 30),
    _temperature(COMFORT_TEMPERATURE_TARGET_HK2, "comfort_temperature_hk_2", 5, 30),
    _temperature(ECO_TEMPERATURE_TARGET_HK2, "eco_temperature_hk_2", 5, 30),
    _temperature(DUALMODE_TEMPERATURE_HZG, "dual_mode_temp_hzg", -20, 40),
    _temperature(COMFORT_WATER_TEMPERATURE_TARGET, "comfort_temperature_dhw", 10, 60),
    _temperature(ECO_WATER_TEMPERATURE_TARGET, "eco_temperature_dhw", 10, 60),
    _temperature(DUALMODE_TEMPERATURE_WW, "dual_mode_temp_ww", -20, 40),
    _temperature(
        AREA_COOLING_TARGET_ROOM_TEMPERATURE, "set_room_temperature_area", 20, 30
    ),
    _temperature(
        AREA_COOLING_TARGET_FLOW_TEMPERATURE, "set_flow_temperature_area", 7, 25
    ),
    _hysteresis(AREA_COOLING_FLOW_TEMPERATURE_HYSTERESIS, "flow_temp_hysteresis_area"),
    _temperature(
        FAN_COOLING_TARGET_ROOM_TEMPERATURE, "set_room_temperature_fan", 20, 30
    ),
    _temperature(
        FAN_COOLING_TARGET_FLOW_TEMPERATURE, "set_flow_temperature_fan", 7, 25
    ),
    _hysteresis(FAN_COOLING_FLOW_TEMPERATURE_HYSTERESIS, "flow_temp_hysteresis_fan"),
    _curve_rise(HEATING_CURVE_RISE_HK1, "heating_curve_rise_hk_1"),
    _curve_rise(HEATING_CURVE_RISE_HK2, "heating_curve_rise_hk_2"),
]

NUMBER_TYPES_WPM = [
    *NUMBER_TYPES_WPM_3I,
    _temperature(COMFORT_TEMPERATURE_TARGET_HK3, "comfort_temperature_hk_3", 5, 30),
    _temperature(ECO_TEMPERATURE_TARGET_HK3, "eco_temperature_hk_3", 5, 30),
    _curve_rise(HEATING_CURVE_RISE_HK3, "heating_curve_rise_hk_3"),
]


def _extension_circuit_numbers(
    circuit: int, comfort_key: str, eco_key: str, curve_key: str
) -> list[StiebelEltronNumberEntityDescription]:
    """Describe the setpoints and heating curve of heating circuit 4 or 5.

    These circuits need the WPE extension module of WPMsystem, so their entities
    are registered disabled, like the circuits' sensors. The manual gives no
    range for them; 5 to 30 °C is what the ISG's object database declares.
    """
    return [
        _temperature(
            comfort_key,
            f"comfort_temperature_hk_{circuit}",
            5,
            30,
            entity_registry_enabled_default=False,
        ),
        _temperature(
            eco_key,
            f"eco_temperature_hk_{circuit}",
            5,
            30,
            entity_registry_enabled_default=False,
        ),
        _curve_rise(
            curve_key,
            f"heating_curve_rise_hk_{circuit}",
            entity_registry_enabled_default=False,
        ),
    ]


NUMBER_TYPES_WPMSYSTEM = [
    *NUMBER_TYPES_WPM,
    *_extension_circuit_numbers(
        4,
        COMFORT_TEMPERATURE_TARGET_HK4,
        ECO_TEMPERATURE_TARGET_HK4,
        HEATING_CURVE_RISE_HK4,
    ),
    *_extension_circuit_numbers(
        5,
        COMFORT_TEMPERATURE_TARGET_HK5,
        ECO_TEMPERATURE_TARGET_HK5,
        HEATING_CURVE_RISE_HK5,
    ),
]


# The German wording of the THZ 5.1/7.1 (ISG Connect) differs from the one the
# other controllers use: its display and ISG call the operating modes "Komfort"
# and "Eco", not "Tag" and "Absenk". These descriptions only differ in their
# translation key, so keys, unique ids and registers stay those of
# NUMBER_TYPES_WPM and existing entities keep their ids.
_THZ_RELABELED_KEYS = frozenset({
    COMFORT_TEMPERATURE_TARGET_HK1,
    ECO_TEMPERATURE_TARGET_HK1,
    COMFORT_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK2,
    COMFORT_TEMPERATURE_TARGET_HK3,
    ECO_TEMPERATURE_TARGET_HK3,
    COMFORT_WATER_TEMPERATURE_TARGET,
    ECO_WATER_TEMPERATURE_TARGET,
})

NUMBER_TYPES_THZ = [
    replace(description, translation_key=f"{description.key}_thz")
    if description.key in _THZ_RELABELED_KEYS
    else description
    for description in NUMBER_TYPES_WPM
]

# Ventilation stages of the THZ 5.1/7.1 (ISG Connect). They belong to the
# optional ``ventilation_parameters`` component of the library, which releases
# before 0.9.3 do not have, so these are only used where it is present. The
# stage ECO was written 1 -> 2 -> 1 on a THZ 7.1 and the airflow followed
# (124 -> 168 m3/h). The comfort and standby stages are the same kind of
# register in the same block; standby was accepted and read back, but the unit
# had the ventilation off at the time, so no airflow change was seen.
THZ_VENTILATION_NUMBER_TYPES = [
    _stage(
        key,
        key,
        write_component="ventilation_parameters",
        mode=NumberMode.BOX,
    )
    for key in (
        VENTILATION_STAGE_COMFORT,
        VENTILATION_STAGE_ECO,
        VENTILATION_STAGE_STANDBY,
    )
]

NUMBER_TYPES_LWZ = [
    _temperature(COMFORT_TEMPERATURE_TARGET_HK1, "room_temperature_day_hk1", 10, 30),
    _temperature(ECO_TEMPERATURE_TARGET_HK1, "room_temperature_night_hk1", 10, 30),
    _temperature(COMFORT_TEMPERATURE_TARGET_HK2, "room_temperature_day_hk2", 10, 30),
    _temperature(ECO_TEMPERATURE_TARGET_HK2, "room_temperature_night_hk2", 10, 30),
    _temperature(COMFORT_WATER_TEMPERATURE_TARGET, "dhw_set_day", 10, 65),
    _temperature(ECO_WATER_TEMPERATURE_TARGET, "dhw_set_night", 10, 65),
    # The half-degree setpoints are checked on write: the input box does not
    # snap to their grid like a slider would.
    _temperature(
        MANUAL_WATER_TEMPERATURE_TARGET,
        "dhw_set_manual",
        10,
        65,
        0.5,
        enforce_step=True,
    ),
    _temperature(
        MANUAL_HC_SET_HK1, "manual_hc_set_hk1", 10, 65, 0.5, enforce_step=True
    ),
    _temperature(
        MANUAL_HC_SET_HK2, "manual_hc_set_hk2", 10, 65, 0.5, enforce_step=True
    ),
    _stage(FAN_LEVEL_DAY, "day_stage"),
    _stage(FAN_LEVEL_NIGHT, "night_stage"),
    _stage(FAN_LEVEL_PARTY, "party_stage"),
    _stage(FAN_LEVEL_MANUAL, "manual_stage"),
    _temperature(
        COMFORT_COOLING_TEMPERATURE_TARGET_HK1,
        "room_temperature_day_hk1_cooling",
        10,
        30,
    ),
    _temperature(
        ECO_COOLING_TEMPERATURE_TARGET_HK1,
        "room_temperature_night_hk1_cooling",
        10,
        30,
    ),
    _temperature(
        COMFORT_COOLING_TEMPERATURE_TARGET_HK2,
        "room_temperature_day_hk2_cooling",
        10,
        30,
    ),
    _temperature(
        ECO_COOLING_TEMPERATURE_TARGET_HK2,
        "room_temperature_night_hk2_cooling",
        10,
        30,
    ),
    _curve_rise(HEATING_CURVE_RISE_HK1, "gradient_hk1", 5),
    _curve_rise(HEATING_CURVE_RISE_HK2, "gradient_hk2", 5),
    _temperature(
        HEATING_CURVE_LOW_END_HK1, "low_end_hk1", 0, 20, 0.5, enforce_step=True
    ),
    _temperature(
        HEATING_CURVE_LOW_END_HK2, "low_end_hk2", 0, 20, 0.5, enforce_step=True
    ),
]


_NUMBER_TYPES = {
    ControllerFamily.WPM_3I: NUMBER_TYPES_WPM_3I,
    ControllerFamily.WPM: NUMBER_TYPES_WPM,
    ControllerFamily.LWZ: NUMBER_TYPES_LWZ,
}


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = entry.runtime_data
    if coordinator.model is ControllerModel.WPMsystem:
        descriptions = NUMBER_TYPES_WPMSYSTEM
    elif coordinator.model is ControllerModel.LWZ_R290:
        descriptions = NUMBER_TYPES_THZ
    else:
        descriptions = _NUMBER_TYPES[coordinator.family]
    async_add_devices([
        StiebelEltronISGNumberEntity(coordinator, entry, description)
        for description in descriptions
    ])
    if coordinator.model is ControllerModel.LWZ_R290:
        # Only the THZ 7.1 (LWZ_R290) is confirmed on hardware.
        async_add_when_served(
            entry,
            "ventilation_parameters",
            THZ_VENTILATION_NUMBER_TYPES,
            lambda description: StiebelEltronISGNumberEntity(
                coordinator, entry, description
            ),
            async_add_devices,
        )


class StiebelEltronISGNumberEntity(StiebelEltronISGEntity, NumberEntity):
    """stiebel_eltron_isg select class."""

    entity_description: StiebelEltronNumberEntityDescription

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
        description: StiebelEltronNumberEntityDescription,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self._attr_mode = number_mode(description)
        self._attr_device_class = number_device_class(description)
        self.modbus_register = description.modbus_register
        self.write_component = description.write_component
        self.write_field = description.write_field

    async def async_set_native_value(self, value: float) -> None:
        """Set new value.

        Skip the modbus write when the value is unchanged. These registers are
        stored in the controller's EEPROM, so avoiding redundant writes (e.g.
        an automation repeatedly setting the same value) protects its limited
        write endurance.

        The comparison tolerates float imprecision: the library decodes scaled
        registers as ``raw * 0.1``, which is not exactly equal to the decimal
        value the user sets (e.g. ``71 * 0.1 != 7.1``).
        """
        if self.write_field is None:
            return

        if self.entity_description.enforce_step:
            # Home Assistant validates bounds but does not enforce native_step.
            step = self.native_step
            assert step is not None
            steps = (value - self.native_min_value) / step
            # Home Assistant converts the value of an instance that shows
            # another unit, but offers the native step unchanged, so a value
            # picked there rarely lands on the grid. It is moved to the nearest
            # step instead of being refused.
            native_unit = self.native_unit_of_measurement
            converted = (
                native_unit is not None and self.unit_of_measurement != native_unit
            )
            if not math.isfinite(steps) or not (
                converted or math.isclose(steps, round(steps), rel_tol=0, abs_tol=1e-9)
            ):
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="invalid_write_step",
                    translation_placeholders={
                        "value": str(value),
                        "field": self.write_field,
                        "step": str(step),
                    },
                )
            # Remove floating-point noise, or the remainder of a conversion.
            value = self.native_min_value + round(steps) * step

        async with self.coordinator.write_lock:
            current = self.native_value
            if current is not None and math.isclose(current, value, abs_tol=1e-9):
                return

            await self.coordinator.write_component_value(
                self.write_component,
                self.write_field,
                value,
            )

    @property
    def native_value(self) -> float | None:
        """Return the written value until the device confirmed it, else its own."""
        pending = self.coordinator.pending_value(self.write_component, self.write_field)
        if pending is not None:
            return pending
        return self.coordinator.get_value(self.modbus_register)
