"""Tests for the ventilation entities of controllers with the WPM register map."""

from types import SimpleNamespace

import pytest

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronDataCoordinator,
)
from custom_components.stiebel_eltron_isg.number import THZ_VENTILATION_NUMBER_TYPES
from custom_components.stiebel_eltron_isg.sensor import THZ_VENTILATION_SENSOR_TYPES


def _coordinator(api) -> StiebelEltronDataCoordinator:
    coordinator = StiebelEltronDataCoordinator.__new__(StiebelEltronDataCoordinator)
    coordinator._api = api
    return coordinator


def _sensor_registers():
    return [description.modbus_register for description in THZ_VENTILATION_SENSOR_TYPES]


def _values(**fields):
    names = (
        "extract_air_temperature",
        "extract_air_humidity",
        "extract_air_dew_point",
        "outside_air_temperature",
        "supply_air_temperature",
        "supply_air_flow",
        "exhaust_air_flow",
        "supply_fan_control",
        "exhaust_fan_control",
    )
    return SimpleNamespace(**{name: fields.get(name) for name in names})


def test_not_served_when_the_library_has_no_ventilation_component() -> None:
    """A library that predates the component must not create entities."""
    coordinator = _coordinator(SimpleNamespace())
    assert not coordinator.serves_component("ventilation_values", _sensor_registers())


def test_not_served_when_the_unit_reports_no_value() -> None:
    """A controller without ventilation reads every register as unavailable."""
    api = SimpleNamespace(ventilation_values=_values())
    coordinator = _coordinator(api)
    assert not coordinator.serves_component("ventilation_values", _sensor_registers())


def test_served_when_one_register_holds_a_value() -> None:
    """One answering register is enough to create the whole group."""
    api = SimpleNamespace(ventilation_values=_values(outside_air_temperature=12.5))
    coordinator = _coordinator(api)
    assert coordinator.serves_component("ventilation_values", _sensor_registers())


def test_sensor_keys_are_unique() -> None:
    keys = [description.key for description in THZ_VENTILATION_SENSOR_TYPES]
    assert len(keys) == len(set(keys))


@pytest.mark.parametrize("description", THZ_VENTILATION_NUMBER_TYPES)
def test_stage_numbers_write_the_stage_field(description) -> None:
    """Each stage number writes its own field and stays within 0..3."""
    assert description.write_component == "ventilation_parameters"
    assert description.write_field == description.key
    assert (description.native_min_value, description.native_max_value) == (0, 3)
    assert description.native_step == 1
    params = SimpleNamespace(**{description.key: 2})
    assert (
        description.modbus_register(SimpleNamespace(ventilation_parameters=params)) == 2
    )
