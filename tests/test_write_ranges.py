"""Verify that entity write ranges are accepted by the library."""

from types import SimpleNamespace
from typing import Any

from homeassistant.components.climate.const import DEFAULT_MAX_TEMP, DEFAULT_MIN_TEMP
from pystiebeleltron.lwz import LwzSystemParameters
from pystiebeleltron.wpm import WpmSystemParameters
from pystiebeleltron.wpm3i import Wpm3iSystemParameters
import pytest

from custom_components.stiebel_eltron_isg.climate import (
    LWZ_CLIMATE_TYPES,
    WPM_3I_CLIMATE_TYPES,
    WPM_CLIMATE_TYPES,
    StiebelEltronISGClimateEntity,
)
from custom_components.stiebel_eltron_isg.number import (
    NUMBER_TYPES_LWZ,
    NUMBER_TYPES_WPM,
    NUMBER_TYPES_WPM_3I,
)

_NUMBER_DESCRIPTION_LISTS = (
    ("NUMBER_TYPES_LWZ", (LwzSystemParameters,), NUMBER_TYPES_LWZ),
    ("NUMBER_TYPES_WPM", (WpmSystemParameters,), NUMBER_TYPES_WPM),
    (
        "NUMBER_TYPES_WPM_3I",
        (Wpm3iSystemParameters, WpmSystemParameters),
        NUMBER_TYPES_WPM_3I,
    ),
)

_CLIMATE_DESCRIPTION_LISTS = (
    ("LWZ_CLIMATE_TYPES", (LwzSystemParameters,), LWZ_CLIMATE_TYPES),
    ("WPM_CLIMATE_TYPES", (WpmSystemParameters,), WPM_CLIMATE_TYPES),
    (
        "WPM_3I_CLIMATE_TYPES",
        (Wpm3iSystemParameters, WpmSystemParameters),
        WPM_3I_CLIMATE_TYPES,
    ),
)

_CLIMATE_WRITE_FIELDS = (
    "eco_target_temp_write_field",
    "comfort_target_temp_write_field",
)


def _field_descriptor(component_classes: tuple[type, ...], field: str) -> Any:
    """Return a field declared by the model, falling back for WPM 3i fields."""
    for component_class in component_classes:
        if field in component_class.__dict__:
            return component_class.__dict__[field]
    raise AssertionError(f"{field} is not declared by any expected component class")


def _write_range_cases() -> list[Any]:
    """Return every advertised writable range and its library descriptor."""
    cases = []

    for list_name, component_classes, descriptions in _NUMBER_DESCRIPTION_LISTS:
        for description in descriptions:
            if description.write_field is None:
                continue
            minimum = description.native_min_value
            maximum = description.native_max_value
            cases.append(
                pytest.param(
                    _field_descriptor(component_classes, description.write_field),
                    minimum,
                    maximum,
                    id=(
                        f"{list_name}-{description.key}-{description.write_field}"
                        f"-{minimum}..{maximum}"
                    ),
                )
            )

    for list_name, component_classes, descriptions in _CLIMATE_DESCRIPTION_LISTS:
        for description in descriptions:
            minimum = getattr(description, "min_temp", DEFAULT_MIN_TEMP)
            maximum = getattr(description, "max_temp", DEFAULT_MAX_TEMP)
            for write_field_attribute in _CLIMATE_WRITE_FIELDS:
                field = getattr(description, write_field_attribute)
                if field is None:
                    continue
                cases.append(
                    pytest.param(
                        _field_descriptor(component_classes, field),
                        minimum,
                        maximum,
                        id=(
                            f"{list_name}-{description.key}-{field}"
                            f"-{minimum}..{maximum}"
                        ),
                    )
                )

    return cases


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

    if validator is True:
        pytest.skip("library field has no range validator")

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
    entity = StiebelEltronISGClimateEntity.__new__(StiebelEltronISGClimateEntity)
    StiebelEltronISGClimateEntity.__init__(
        entity,
        SimpleNamespace(device_info=None, last_update_success=True),
        SimpleNamespace(entry_id="test"),
        description,
    )

    assert entity.min_temp == description.min_temp
    assert entity.max_temp == description.max_temp
