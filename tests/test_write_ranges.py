"""Verify that entity write ranges are accepted by the library."""

from functools import cache
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from homeassistant.components.climate import ClimateEntityDescription
from homeassistant.components.number import NumberEntityDescription
from modbus_connection.mock import MockModbusConnection
from pystiebeleltron.lwz import LwzStiebelEltronAPI
from pystiebeleltron.wpm import WpmStiebelEltronAPI
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI
import pytest

from custom_components.stiebel_eltron_isg import (
    climate as climate_platform,
    number as number_platform,
)
from custom_components.stiebel_eltron_isg.climate import (
    LWZ_CLIMATE_TYPES,
    WPM_3I_CLIMATE_TYPES,
    WPM_CLIMATE_TYPES,
    StiebelEltronISGClimateEntity,
)
from custom_components.stiebel_eltron_isg.const import UNIT_ID
from custom_components.stiebel_eltron_isg.number import (
    NUMBER_TYPES_LWZ,
    NUMBER_TYPES_WPM,
    NUMBER_TYPES_WPM_3I,
)

_NUMBER_DESCRIPTION_LISTS = (
    ("NUMBER_TYPES_LWZ", LwzStiebelEltronAPI, NUMBER_TYPES_LWZ),
    ("NUMBER_TYPES_WPM", WpmStiebelEltronAPI, NUMBER_TYPES_WPM),
    (
        "NUMBER_TYPES_WPM_3I",
        Wpm3iStiebelEltronAPI,
        NUMBER_TYPES_WPM_3I,
    ),
)

_CLIMATE_DESCRIPTION_LISTS = (
    ("LWZ_CLIMATE_TYPES", LwzStiebelEltronAPI, LWZ_CLIMATE_TYPES),
    ("WPM_CLIMATE_TYPES", WpmStiebelEltronAPI, WPM_CLIMATE_TYPES),
    (
        "WPM_3I_CLIMATE_TYPES",
        Wpm3iStiebelEltronAPI,
        WPM_3I_CLIMATE_TYPES,
    ),
)

_CLIMATE_WRITE_FIELDS = (
    "eco_target_temp_write_field",
    "comfort_target_temp_write_field",
)

_EXPECTED_WRITE_RANGE_CASES = Path(__file__).with_name("capability_write_ranges.txt")
_BOUNDS_UNVERIFIED = frozenset({
    "NUMBER_TYPES_WPM-heating_curve_rise_hk3-heating_curve_rise_hk_3-0..3"
})


@cache
def _api(api_class: type[Any]) -> Any:
    """Return the API object used by one integration API family."""
    return api_class(MockModbusConnection().for_unit(UNIT_ID))


def _field_descriptor(
    api_class: type[Any],
    component: str,
    field: str,
) -> Any:
    """Return the descriptor from the component used by the real API."""
    component_object = getattr(_api(api_class), component, None)
    assert component_object is not None, (
        f"{api_class.__name__} has no component {component}"
    )
    descriptor = getattr(type(component_object), field, None)
    assert descriptor is not None, (
        f"{type(component_object).__name__} has no field {field}"
    )
    return descriptor


def _write_range_cases() -> list[Any]:
    """Return every advertised writable range and its library descriptor."""
    cases: list[Any] = []

    for list_name, api_class, descriptions in _NUMBER_DESCRIPTION_LISTS:
        for number_description in descriptions:
            if number_description.write_field is None:
                continue
            minimum = number_description.native_min_value
            maximum = number_description.native_max_value
            field = _field_descriptor(
                api_class,
                number_description.write_component,
                number_description.write_field,
            )
            case_id = (
                f"{list_name}-{number_description.key}-{number_description.write_field}"
                f"-{minimum}..{maximum}"
            )
            cases.append(
                pytest.param(
                    field,
                    minimum,
                    maximum,
                    id=case_id,
                )
            )

    for list_name, api_class, descriptions in _CLIMATE_DESCRIPTION_LISTS:
        for climate_description in descriptions:
            minimum = climate_description.min_temp
            maximum = climate_description.max_temp
            for write_field_attribute in _CLIMATE_WRITE_FIELDS:
                field = getattr(climate_description, write_field_attribute)
                if field is None:
                    continue
                descriptor = _field_descriptor(
                    api_class,
                    climate_description.write_component,
                    field,
                )
                case_id = (
                    f"{list_name}-{climate_description.key}-{field}"
                    f"-{minimum}..{maximum}"
                )
                cases.append(
                    pytest.param(
                        descriptor,
                        minimum,
                        maximum,
                        id=case_id,
                    )
                )

    return cases


def _uncovered_descriptions(
    module: Any,
    description_type: type[Any],
    covered: set[int],
) -> set[str]:
    """Return module-level descriptions missing from the range sweep."""
    return {
        f"{name}: {description.key}"
        for name, value in vars(module).items()
        if isinstance(value, (list, tuple))
        and value
        and all(isinstance(item, description_type) for item in value)
        for description in value
        if id(description) not in covered
    }


def test_every_ranged_description_is_covered() -> None:
    """A new Number or Climate description must not escape range validation."""
    number_covered = {
        id(description)
        for _, _, descriptions in _NUMBER_DESCRIPTION_LISTS
        for description in descriptions
    }
    climate_covered = {
        id(description)
        for _, _, descriptions in _CLIMATE_DESCRIPTION_LISTS
        for description in descriptions
    }
    missing = _uncovered_descriptions(
        number_platform,
        NumberEntityDescription,
        number_covered,
    ) | _uncovered_descriptions(
        climate_platform,
        ClimateEntityDescription,
        climate_covered,
    )

    assert not missing, f"descriptions missing from write-range validation: {missing}"


def test_write_range_inventory_matches_reviewed_snapshot() -> None:
    """Range changes must name the exact reviewed entity and endpoints."""
    cases = _write_range_cases()
    expected = _EXPECTED_WRITE_RANGE_CASES.read_text(encoding="utf-8").splitlines()

    assert sorted(case.id for case in cases) == expected

    bounds_unverified = {case.id for case in cases if case.values[0].writable is True}
    assert bounds_unverified == _BOUNDS_UNVERIFIED, (
        "fields or advertised bounds without a library validator changed; "
        "verify both endpoints and update the reviewed inventory"
    )


@pytest.mark.parametrize(("field", "minimum", "maximum"), _write_range_cases())
def test_advertised_write_range_is_accepted(
    field: Any, minimum: float, maximum: float
) -> None:
    """Every callable library validator must accept both advertised bounds."""
    validator = field.writable

    # ``writable=False`` is not a missing validator but a read-only register:
    # an entity offering to write it can never succeed, which is the failure
    # this project already hit in issue #607.
    assert validator is not False, "entity writes a field the library marks read-only"

    # The exact ``True`` cases are pinned by ``_BOUNDS_UNVERIFIED`` above so an
    # unvalidated field cannot enter or leave the inventory silently. Callable
    # validators need to accept both advertised endpoints.
    if validator is not True:
        validator(minimum)
        validator(maximum)


@pytest.mark.parametrize(
    "description",
    [
        pytest.param(description, id=f"{list_name}-{description.key}")
        for list_name, _, descriptions in _CLIMATE_DESCRIPTION_LISTS
        for description in descriptions
    ],
)
def test_climate_entity_publishes_its_description_bounds(description: Any) -> None:
    """The bounds must reach the entity, not just sit on the description.

    Without this, dropping the assignment in ``__init__`` would silently
    restore Home Assistant's 7/35 defaults while the range test above still
    passed, because it only ever reads the description.
    """
    entity = StiebelEltronISGClimateEntity(
        SimpleNamespace(device_info=None, last_update_success=True),
        SimpleNamespace(entry_id="test"),
        description,
    )

    assert entity.min_temp == description.min_temp
    assert entity.max_temp == description.max_temp
