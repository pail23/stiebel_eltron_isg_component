"""Guards that every entity description resolves against its model's API.

All platforms declare their entities as descriptions holding lambda accessors
(``lambda api: api.<component>.<field>``) plus the ``write_field`` name that
``write_component_value`` writes to. A description used for a model whose API
does not have that field breaks only at runtime: the accessor raises
``AttributeError`` (the coordinator only catches ``StiebelEltronModbusError``)
and the write silently no-ops (``write_component_value`` guards with
``hasattr``). The tests below therefore resolve every accessor and every write
field of every model specific description list against the API class the
coordinator really builds for that model, and check that no description list
escapes that sweep.
"""

from functools import cache
from types import ModuleType
from typing import Any

from homeassistant.helpers.entity import EntityDescription
from modbus_connection.mock import MockModbusConnection
from pystiebeleltron.lwz import LwzStiebelEltronAPI
from pystiebeleltron.wpm import WpmStiebelEltronAPI
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI
import pytest

from custom_components.stiebel_eltron_isg import (
    binary_sensor,
    climate,
    number,
    select,
    sensor,
    switch,
)
from custom_components.stiebel_eltron_isg.const import UNIT_ID

WPM = "wpm"
WPM_3I = "wpm_3i"
LWZ = "lwz"

_API_CLASSES = {
    WPM: WpmStiebelEltronAPI,
    WPM_3I: Wpm3iStiebelEltronAPI,
    LWZ: LwzStiebelEltronAPI,
}

# button is left out on purpose: its descriptions carry a coordinator level
# press_action rather than an api accessor, and the same list serves every model.
_PLATFORM_MODULES = (binary_sensor, climate, number, select, sensor, switch)

# Description attributes holding an accessor lambda, or a list of them.
_ACCESSOR_ATTRIBUTES = (
    "modbus_register",
    "humidity_modbus_register",
    "actual_temperature_register",
    "eco_target_temp_register",
    "comfort_target_temp_register",
)

# Description attributes holding the name of a writable component field.
_WRITE_FIELD_ATTRIBUTES = (
    "write_field",
    "eco_target_temp_write_field",
    "comfort_target_temp_write_field",
)

# Every description list a platform hands to a model, with that model. Lists
# used by more than one model appear once per model. Lists that only exist to
# be spliced into one of these are covered through their parent;
# ``test_every_description_is_covered`` fails if one is missed entirely.
_DESCRIPTION_LISTS: list[tuple[str, str, list[Any]]] = [
    ("NUMBER_TYPES_WPM", WPM, number.NUMBER_TYPES_WPM),
    ("NUMBER_TYPES_WPM_3I", WPM_3I, number.NUMBER_TYPES_WPM_3I),
    ("NUMBER_TYPES_LWZ", LWZ, number.NUMBER_TYPES_LWZ),
    ("WPM_SENSOR_TYPES", WPM, sensor.WPM_SENSOR_TYPES),
    ("WPM_3I_SENSOR_TYPES", WPM_3I, sensor.WPM_3I_SENSOR_TYPES),
    ("LWZ_SENSOR_TYPES", LWZ, sensor.LWZ_SENSOR_TYPES),
    ("ENERGY_DAILY_SENSOR_TYPES", WPM, sensor.ENERGY_DAILY_SENSOR_TYPES),
    ("ENERGY_DAILY_SENSOR_TYPES", WPM_3I, sensor.ENERGY_DAILY_SENSOR_TYPES),
    ("LWZ_ENERGY_DAILY_SENSOR_TYPES", LWZ, sensor.LWZ_ENERGY_DAILY_SENSOR_TYPES),
    ("WPM_BINARY_SENSOR_TYPES", WPM, binary_sensor.WPM_BINARY_SENSOR_TYPES),
    ("WPM_3I_BINARY_SENSOR_TYPES", WPM_3I, binary_sensor.WPM_3I_BINARY_SENSOR_TYPES),
    ("LWZ_BINARY_SENSOR_TYPES", LWZ, binary_sensor.LWZ_BINARY_SENSOR_TYPES),
    ("SWITCH_TYPES", WPM, switch.SWITCH_TYPES),
    ("SWITCH_TYPES", WPM_3I, switch.SWITCH_TYPES),
    ("SWITCH_TYPES", LWZ, switch.SWITCH_TYPES),
    # WPMsystem and LWZ_R290, both of which are served by the WPM api.
    ("CIRCULATION_PUMP_SWITCH_TYPES", WPM, switch.CIRCULATION_PUMP_SWITCH_TYPES),
    ("WPM_SELECT_TYPES", WPM, select.WPM_SELECT_TYPES),
    ("WPM_SELECT_TYPES", WPM_3I, select.WPM_SELECT_TYPES),
    ("LWZ_SELECT_TYPES", LWZ, select.LWZ_SELECT_TYPES),
    ("WPM_CLIMATE_TYPES", WPM, climate.WPM_CLIMATE_TYPES),
    ("WPM_3I_CLIMATE_TYPES", WPM_3I, climate.WPM_3I_CLIMATE_TYPES),
    ("LWZ_CLIMATE_TYPES", LWZ, climate.LWZ_CLIMATE_TYPES),
]


@cache
def _api(model: str) -> Any:
    """Return the API object a coordinator builds for ``model``."""
    return _API_CLASSES[model](MockModbusConnection().for_unit(UNIT_ID))


def _module_description_lists(module: ModuleType) -> list[tuple[str, list[Any]]]:
    """Return every module level list of entity descriptions of ``module``."""
    lists = []
    for name, value in vars(module).items():
        if not isinstance(value, (list, tuple)) or not value:
            continue
        if all(isinstance(item, EntityDescription) for item in value):
            lists.append((name, list(value)))
    return lists


def _accessor_cases() -> list[Any]:
    """Return a param per accessor of every description, carrying its test id."""
    cases = []
    for list_name, model, descriptions in _DESCRIPTION_LISTS:
        for description in descriptions:
            for attribute in _ACCESSOR_ATTRIBUTES:
                value = getattr(description, attribute, None)
                if value is None:
                    continue
                # Climate descriptions hold a list of accessors per attribute.
                accessors = value if isinstance(value, list) else [value]
                name = f"{list_name}-{model}-{description.key}-{attribute}"
                cases.extend(
                    pytest.param(
                        model,
                        accessor,
                        id=f"{name}[{index}]" if len(accessors) > 1 else name,
                    )
                    for index, accessor in enumerate(accessors)
                )
    return cases


def _write_field_cases() -> list[Any]:
    """Return a param per write field of every description, with its test id."""
    cases = []
    for list_name, model, descriptions in _DESCRIPTION_LISTS:
        for description in descriptions:
            component = getattr(description, "write_component", None)
            if component is None:
                continue
            cases.extend(
                pytest.param(
                    model,
                    component,
                    getattr(description, attribute),
                    id=f"{list_name}-{model}-{description.key}-{attribute}",
                )
                for attribute in _WRITE_FIELD_ATTRIBUTES
                if getattr(description, attribute, None) is not None
            )
    return cases


@pytest.mark.parametrize(("model", "accessor"), _accessor_cases())
def test_description_accessor_resolves(model: str, accessor: Any) -> None:
    """Every accessor must resolve against the API of the model using it."""
    accessor(_api(model))


@pytest.mark.parametrize(("model", "component", "field"), _write_field_cases())
def test_description_write_field_resolves(
    model: str, component: str, field: str
) -> None:
    """Every write field must exist on the component of the model using it."""
    component_object = getattr(_api(model), component, None)

    assert component_object is not None, f"{model} api has no component {component}"
    assert hasattr(component_object, field), (
        f"{type(component_object).__name__} has no field {field}"
    )


@pytest.mark.parametrize(
    "module", _PLATFORM_MODULES, ids=lambda module: module.__name__.rsplit(".", 1)[-1]
)
def test_every_description_is_covered(module: ModuleType) -> None:
    """No description list may escape the sweep above.

    Keeps ``_DESCRIPTION_LISTS`` from going stale: a new list, or a list that
    stops being spliced into a covered one, has to be registered with the model
    that uses it before it can be shipped.
    """
    covered = {
        id(description)
        for _, _, descriptions in _DESCRIPTION_LISTS
        for description in descriptions
    }

    missing = {
        f"{name}: {description.key}"
        for name, descriptions in _module_description_lists(module)
        for description in descriptions
        if id(description) not in covered
    }

    assert not missing, (
        f"descriptions of {module.__name__} not covered by _DESCRIPTION_LISTS: "
        f"{sorted(missing)}"
    )
