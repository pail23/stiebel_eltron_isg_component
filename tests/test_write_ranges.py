"""Verify that entity write ranges are accepted by the library."""

from dataclasses import dataclass
from functools import cache
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

_UNVALIDATED_WRITE_FIELDS = frozenset({
    (WpmStiebelEltronAPI, "system_parameters", "heating_curve_rise_hk_3")
})


@dataclass(frozen=True)
class WriteRangeCase:
    """One Home Assistant range and the library field that accepts it."""

    list_name: str
    api_class: type[Any]
    component: str
    entity_key: str
    field: str
    minimum: float
    maximum: float

    @property
    def id(self) -> str:
        """Return a stable, readable pytest identifier."""
        return (
            f"{self.list_name}-{self.entity_key}-{self.field}"
            f"-{self.minimum}..{self.maximum}"
        )

    @property
    def target(self) -> tuple[type[Any], str, str]:
        """Return the library target independently of advertised bounds."""
        return (self.api_class, self.component, self.field)


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


def _write_range_cases() -> list[WriteRangeCase]:
    """Return every advertised writable range and its library target."""
    cases: list[WriteRangeCase] = []

    for list_name, api_class, descriptions in _NUMBER_DESCRIPTION_LISTS:
        for number_description in descriptions:
            if number_description.write_field is None:
                continue
            cases.append(
                WriteRangeCase(
                    list_name=list_name,
                    api_class=api_class,
                    component=number_description.write_component,
                    entity_key=number_description.key,
                    field=number_description.write_field,
                    minimum=number_description.native_min_value,
                    maximum=number_description.native_max_value,
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
                cases.append(
                    WriteRangeCase(
                        list_name=list_name,
                        api_class=api_class,
                        component=climate_description.write_component,
                        entity_key=climate_description.key,
                        field=field,
                        minimum=minimum,
                        maximum=maximum,
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


def test_unvalidated_write_fields_are_explicit() -> None:
    """Library fields without a bounds validator must be reviewed explicitly."""
    actual = {
        case.target
        for case in _write_range_cases()
        if _field_descriptor(case.api_class, case.component, case.field).writable
        is True
    }

    assert actual == _UNVALIDATED_WRITE_FIELDS, (
        "library fields without bounds validators changed; verify their Home Assistant "
        "ranges and update the explicit target set"
    )


@pytest.mark.parametrize(
    "case",
    [pytest.param(case, id=case.id) for case in _write_range_cases()],
)
def test_advertised_write_range_is_accepted(case: WriteRangeCase) -> None:
    """Every callable library validator must accept both advertised bounds."""
    field = _field_descriptor(case.api_class, case.component, case.field)
    validator = field.writable

    # ``writable=False`` is not a missing validator but a read-only register:
    # an entity offering to write it can never succeed, which is the failure
    # this project already hit in issue #607.
    assert validator is not False, "entity writes a field the library marks read-only"
    assert validator is True or callable(validator), (
        "entity writes a field without a supported library write contract"
    )

    # The exact ``True`` targets are pinned by ``_UNVALIDATED_WRITE_FIELDS``.
    # Callable validators need to accept both advertised endpoints.
    if validator is not True:
        validator(case.minimum)
        validator(case.maximum)


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
