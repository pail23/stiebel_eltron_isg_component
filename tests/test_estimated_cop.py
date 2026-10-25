"""Regression cases for the optional water/inverter snapshot estimate."""

from types import SimpleNamespace

import pytest

from custom_components.stiebel_eltron_isg.estimated_cop import (
    estimated_water_inverter_cop,
)
from custom_components.stiebel_eltron_isg.sensor import (
    LWZ_SENSOR_TYPES,
    WPM_3I_SENSOR_TYPES,
    WPM_SENSOR_TYPES,
    WPMSYSTEM_ESTIMATED_COP_SENSOR_TYPES,
)


def sample(status=(1 << 6) | (1 << 4), **overrides):
    values = {
        "wp_water_flow_rate": 30.0,
        "flow_temperature": 35.0,
        "return_temperature": 30.0,
    }
    values.update({k: v for k, v in overrides.items() if k in values})
    return SimpleNamespace(
        system_state=SimpleNamespace(operating_status=status),
        system_values=SimpleNamespace(heat_pumps=[SimpleNamespace(**values)]),
        extended_energy_data=SimpleNamespace(
            inverter_power_iws_1=overrides.get("power", 1.5)
        ),
    )


@pytest.mark.parametrize(("mode", "flag"), [("heating", 4), ("dhw", 5)])
def test_matching_mode_uses_water_power_and_inverter_power(mode, flag):
    assert estimated_water_inverter_cop(sample((1 << 6) | (1 << flag)), mode) == 6.98


@pytest.mark.parametrize(
    "status",
    [
        None,
        True,
        80.0,
        -1,
        65536,
        0,
        1 << 4,  # Residual heat circulation without the compressor.
        (1 << 6) | (1 << 5),  # DHW cannot be attributed to heating.
        (1 << 6) | (1 << 4) | (1 << 5),  # Ambiguous mode.
        *((1 << 6) | (1 << 4) | (1 << bit) for bit in (3, 8, 9)),
    ],
)
def test_rejects_missing_ambiguous_or_excluded_operating_states(status):
    assert estimated_water_inverter_cop(sample(status), "heating") is None


@pytest.mark.parametrize(
    "field", ["wp_water_flow_rate", "flow_temperature", "return_temperature", "power"]
)
@pytest.mark.parametrize("value", [None, True, "1.5", float("nan"), float("inf")])
def test_missing_or_invalid_inputs_are_not_replaced_with_zero(field, value):
    assert estimated_water_inverter_cop(sample(**{field: value}), "heating") is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"power": 0},
        {"power": -1},
        {"power": 0.1},
        {"wp_water_flow_rate": 0},
        {"wp_water_flow_rate": -1},
        {"flow_temperature": 29},
        {"flow_temperature": 30},
        {"flow_temperature": 30.1},
    ],
)
def test_near_zero_and_reverse_heat_flow_are_unavailable(overrides):
    assert estimated_water_inverter_cop(sample(**overrides), "heating") is None


def test_extreme_result_is_not_silently_clipped():
    assert estimated_water_inverter_cop(sample(power=0.2), "heating") == 52.33


def test_nonfinite_derived_result_is_unavailable():
    api = sample(wp_water_flow_rate=1e308, flow_temperature=1e308)
    assert estimated_water_inverter_cop(api, "heating") is None


def test_estimates_are_opt_in_without_statistics_or_a_unit():
    assert len(WPMSYSTEM_ESTIMATED_COP_SENSOR_TYPES) == 2
    for description in WPMSYSTEM_ESTIMATED_COP_SENSOR_TYPES:
        assert description.entity_registry_enabled_default is False
        assert description.state_class is None
        assert description.native_unit_of_measurement is None


def test_estimate_descriptions_map_modes_without_reusing_existing_keys():
    heating, dhw = WPMSYSTEM_ESTIMATED_COP_SENSOR_TYPES
    assert heating.modbus_register(sample()) == 6.98
    assert dhw.modbus_register(sample()) is None
    assert dhw.modbus_register(sample((1 << 6) | (1 << 5))) == 6.98
    keys = {description.key for description in WPMSYSTEM_ESTIMATED_COP_SENSOR_TYPES}
    for shared in (WPM_SENSOR_TYPES, WPM_3I_SENSOR_TYPES, LWZ_SENSOR_TYPES):
        assert not keys.intersection(description.key for description in shared)
