"""Guards that every entity description resolves against its model's API.

All platforms declare their entities as descriptions holding lambda accessors
(``lambda api: api.<component>.<field>``) plus the ``write_field`` name that
``write_component_value`` writes to. A description used for a model whose API
does not have that field breaks only at runtime: the accessor raises
``AttributeError`` (the coordinator only catches ``StiebelEltronModbusError``)
and the write raises a translated ``write_unsupported`` error. The tests below
therefore resolve every accessor and every write field of every model specific
description list against the API class the coordinator really builds for that
model, and check that no description list escapes that sweep.
"""

from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any

from homeassistant.const import EntityCategory
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

_EXPECTED_WRITE_FIELD_CASES = Path(__file__).with_name("capability_write_fields.txt")

# Every description list a platform hands to a model, with that model. Lists
# used by more than one model appear once per model. Lists that only exist to
# be spliced into one of these are covered through their parent;
# ``test_every_description_is_covered`` fails if one is missed entirely.
_DESCRIPTION_LISTS: list[tuple[str, str, list[Any]]] = [
    ("NUMBER_TYPES_WPM", WPM, number.NUMBER_TYPES_WPM),
    ("NUMBER_TYPES_WPM_3I", WPM_3I, number.NUMBER_TYPES_WPM_3I),
    ("NUMBER_TYPES_LWZ", LWZ, number.NUMBER_TYPES_LWZ),
    ("WPM_SENSOR_TYPES", WPM, sensor.WPM_SENSOR_TYPES),
    # WPMsystem only, see the comment on the list itself.
    ("WPM_INVERTER_POWER_SENSOR_TYPES", WPM, sensor.WPM_INVERTER_POWER_SENSOR_TYPES),
    ("WPM_3I_SENSOR_TYPES", WPM_3I, sensor.WPM_3I_SENSOR_TYPES),
    ("LWZ_SENSOR_TYPES", LWZ, sensor.LWZ_SENSOR_TYPES),
    ("ENERGY_DAILY_SENSOR_TYPES", WPM, sensor.ENERGY_DAILY_SENSOR_TYPES),
    ("ENERGY_DAILY_SENSOR_TYPES", WPM_3I, sensor.ENERGY_DAILY_SENSOR_TYPES),
    ("LWZ_ENERGY_DAILY_SENSOR_TYPES", LWZ, sensor.LWZ_ENERGY_DAILY_SENSOR_TYPES),
    ("WPM_BINARY_SENSOR_TYPES", WPM, binary_sensor.WPM_BINARY_SENSOR_TYPES),
    ("WPM_3I_BINARY_SENSOR_TYPES", WPM_3I, binary_sensor.WPM_3I_BINARY_SENSOR_TYPES),
    ("LWZ_BINARY_SENSOR_TYPES", LWZ, binary_sensor.LWZ_BINARY_SENSOR_TYPES),
    # WPMsystem and LWZ_R290, both of which are served by the WPM api.
    (
        "CIRCULATION_PUMP_BINARY_SENSOR_TYPES",
        WPM,
        binary_sensor.CIRCULATION_PUMP_BINARY_SENSOR_TYPES,
    ),
    ("SWITCH_TYPES", WPM, switch.SWITCH_TYPES),
    ("SWITCH_TYPES", WPM_3I, switch.SWITCH_TYPES),
    ("SWITCH_TYPES", LWZ, switch.SWITCH_TYPES),
    ("WPM_SELECT_TYPES", WPM, select.WPM_SELECT_TYPES),
    ("WPM_SELECT_TYPES", WPM_3I, select.WPM_SELECT_TYPES),
    ("LWZ_SELECT_TYPES", LWZ, select.LWZ_SELECT_TYPES),
    ("WPM_CLIMATE_TYPES", WPM, climate.WPM_CLIMATE_TYPES),
    ("WPM_3I_CLIMATE_TYPES", WPM_3I, climate.WPM_3I_CLIMATE_TYPES),
    ("LWZ_CLIMATE_TYPES", LWZ, climate.LWZ_CLIMATE_TYPES),
]


# The WPM list and the WPM 3i list a platform keeps for the same entities. The
# 3i profile is a subset of the WPM one, so every pair is a parity candidate.
_PARITY_CASES = [
    pytest.param(name, wpm, wpm_3i, id=name)
    for name, wpm, wpm_3i in (
        ("sensor", sensor.WPM_SENSOR_TYPES, sensor.WPM_3I_SENSOR_TYPES),
        (
            "binary_sensor",
            binary_sensor.WPM_BINARY_SENSOR_TYPES,
            binary_sensor.WPM_3I_BINARY_SENSOR_TYPES,
        ),
        ("number", number.NUMBER_TYPES_WPM, number.NUMBER_TYPES_WPM_3I),
        ("climate", climate.WPM_CLIMATE_TYPES, climate.WPM_3I_CLIMATE_TYPES),
    )
]


@cache
def _api(model: str) -> Any:
    """Return the API object a coordinator builds for ``model``."""
    return _API_CLASSES[model](MockModbusConnection().for_unit(UNIT_ID))


def _resolves_on_wpm_3i(description: Any) -> bool:
    """Return whether every accessor of ``description`` resolves on the 3i api."""
    accessors = [
        accessor
        for attribute in _ACCESSOR_ATTRIBUTES
        for value in [getattr(description, attribute, None)]
        if value is not None
        for accessor in (value if isinstance(value, list) else [value])
    ]

    try:
        for accessor in accessors:
            accessor(_api(WPM_3I))
    except AttributeError:
        return False
    return bool(accessors)


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
    cases: list[Any] = []
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
    cases: list[Any] = []
    for list_name, model, descriptions in _DESCRIPTION_LISTS:
        for description in descriptions:
            component = getattr(description, "write_component", None)
            write_fields = [
                (attribute, field)
                for attribute in _WRITE_FIELD_ATTRIBUTES
                for field in [getattr(description, attribute, None)]
                if field is not None
            ]
            if component is None:
                assert not write_fields, (
                    f"{list_name}-{model}-{description.key} carries a write field "
                    "without a write component"
                )
                continue
            cases.extend(
                pytest.param(
                    model,
                    component,
                    field,
                    id=(f"{list_name}-{model}-{description.key}-{attribute}-{field}"),
                )
                for attribute, field in write_fields
            )
    return cases


def test_write_field_inventory_matches_reviewed_snapshot() -> None:
    """Write-field drift must identify every added or removed case."""
    expected = _EXPECTED_WRITE_FIELD_CASES.read_text(encoding="utf-8").splitlines()

    assert sorted(case.id for case in _write_field_cases()) == expected, (
        "write fields changed; verify the targets and update "
        "tests/capability_write_fields.txt"
    )


def test_number_type_sets_are_non_empty() -> None:
    """Ensure configuration-category tests always run against non-empty entity sets."""
    assert number.NUMBER_TYPES_WPM
    assert number.NUMBER_TYPES_WPM_3I
    assert number.NUMBER_TYPES_LWZ


@pytest.mark.parametrize(
    "description",
    [
        *number.NUMBER_TYPES_WPM,
        *number.NUMBER_TYPES_WPM_3I,
        *number.NUMBER_TYPES_LWZ,
    ],
    ids=lambda description: description.key,
)
def test_number_settings_are_configuration_entities(description: Any) -> None:
    """Persistent controller parameters belong in the device configuration."""
    assert description.entity_category is EntityCategory.CONFIG


def test_every_controller_family_has_number_settings() -> None:
    """The category contract must exercise settings for every model family."""
    assert number.NUMBER_TYPES_WPM
    assert number.NUMBER_TYPES_WPM_3I
    assert number.NUMBER_TYPES_LWZ


def test_number_description_defaults_to_configuration_category() -> None:
    """New Number descriptions inherit the reviewed configuration category."""
    assert (
        number.StiebelEltronNumberEntityDescription.__dataclass_fields__[
            "entity_category"
        ].default
        is EntityCategory.CONFIG
    )


@pytest.mark.parametrize(("model", "accessor"), _accessor_cases())
def test_description_accessor_resolves(model: str, accessor: Any) -> None:
    """Every accessor must resolve against the API of the model using it."""
    accessor(_api(model))


@pytest.mark.parametrize(("model", "component", "field"), _write_field_cases())
def test_description_write_field_resolves(
    model: str, component: str, field: str
) -> None:
    """Every write field must exist and be writable for the model using it."""
    component_object = getattr(_api(model), component, None)

    assert component_object is not None, f"{model} api has no component {component}"
    assert hasattr(component_object, field), (
        f"{type(component_object).__name__} has no field {field}"
    )
    field_descriptor = getattr(type(component_object), field, None)
    assert field_descriptor is not None, (
        f"{type(component_object).__name__}.{field} is not a field descriptor"
    )
    write_contract = getattr(field_descriptor, "writable", None)
    assert write_contract is True or callable(write_contract), (
        f"{type(component_object).__name__}.{field} has no supported write contract"
    )


@pytest.mark.parametrize(("list_name", "wpm", "wpm_3i"), _PARITY_CASES)
def test_wpm_3i_offers_what_its_api_supports(
    list_name: str, wpm: list[Any], wpm_3i: list[Any]
) -> None:
    """A WPM entity the WPM 3i api can serve has to be offered to the 3i too.

    The 3i lists are curated rather than derived, so an entity added to the WPM
    list stays invisible on a 3i until someone remembers the second list. That
    is silent: nothing raises, the entity simply never appears. Whether the 3i
    api resolves the accessor is the same test the coordinator would fail on,
    so it decides here which entities the 3i is entitled to.
    """
    offered = {description.key for description in wpm_3i}

    missing = sorted(
        description.key
        for description in wpm
        if description.key not in offered and _resolves_on_wpm_3i(description)
    )

    assert not missing, (
        f"{list_name} entities the WPM 3i api supports but the 3i list omits: {missing}"
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
