"""Regression cases for the optional water/inverter snapshot estimate."""

from types import SimpleNamespace
from unittest.mock import patch

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers import entity_registry as er
from pystiebeleltron import ControllerModel
from pystiebeleltron.wpm import WpmStiebelEltronAPI
import pytest

from custom_components.stiebel_eltron_isg.const import DOMAIN, UNIT_ID
from custom_components.stiebel_eltron_isg.entity import build_unique_id
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


@pytest.mark.parametrize(("mode", "flag"), [("heating", 4), ("dhw", 5)])
@pytest.mark.parametrize(
    ("supply", "return_temp", "expected"),
    [
        pytest.param(35.2, 35.0, None, id="threshold-rounded-up-in-binary"),
        pytest.param(34.9, 34.7, None, id="threshold-rounded-down-in-binary"),
        pytest.param(35.1, 35.0, None, id="below-threshold"),
        pytest.param(35.0, 35.0, None, id="zero-difference"),
        pytest.param(35.0, 35.2, None, id="reverse-flow"),
        pytest.param(35.3, 35.0, 0.42, id="first-valid-step-rounded-down-in-binary"),
        pytest.param(35.2, 34.9, 0.42, id="first-valid-step-rounded-up-in-binary"),
    ],
)
def test_temperature_guard_uses_register_resolution(
    mode, flag, supply, return_temp, expected
):
    api = sample(
        (1 << 6) | (1 << flag),
        flow_temperature=supply,
        return_temperature=return_temp,
    )
    assert estimated_water_inverter_cop(api, mode) == expected


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


async def test_new_estimates_stay_disabled_in_home_assistant(
    hass, mock_config_entry, mock_get_controller_model
):
    """Fresh installations register both estimates without recording states."""
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    for description in WPMSYSTEM_ESTIMATED_COP_SENSOR_TYPES:
        entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, build_unique_id(mock_config_entry, description.key)
        )
        assert entity_id is not None
        entry = registry.async_get(entity_id)
        assert entry is not None
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
        assert hass.states.get(entity_id) is None


async def test_enabled_estimates_follow_decoded_registers_in_home_assistant(
    hass, mock_config_entry, mock_modbus_connection, mock_get_controller_model
):
    """Exercise the current library, coordinator and HA states across a run."""
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_config_entry.add_to_hass(hass)
    registry = er.async_get(hass)
    entities = [
        registry.async_get_or_create(
            "sensor",
            DOMAIN,
            build_unique_id(mock_config_entry, description.key),
            config_entry=mock_config_entry,
            suggested_object_id=description.key,
        )
        for description in WPMSYSTEM_ESTIMATED_COP_SENSOR_TYPES
    ]
    unit = mock_modbus_connection.for_unit(UNIT_ID)
    api = WpmStiebelEltronAPI(unit)
    # Wire registers: return 541, supply 542, flow 547, status 2500,
    # inverter input 3679. Their scales are decoded by the installed library.
    unit.load_raw({"input": {541: 350, 542: 352, 547: 300, 2500: 80, 3679: 15}})
    with patch(
        "custom_components.stiebel_eltron_isg.coordinator.WpmStiebelEltronAPI",
        return_value=api,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    cases = [
        (352, 80, 15, (STATE_UNAVAILABLE, STATE_UNAVAILABLE)),  # 0.2 K boundary.
        (400, 80, 15, ("6.98", STATE_UNAVAILABLE)),  # Heating.
        (400, 96, 15, (STATE_UNAVAILABLE, "6.98")),  # Hot water.
        (400, 16, 15, (STATE_UNAVAILABLE, STATE_UNAVAILABLE)),  # Residual heat.
        (400, 80 | (1 << 9), 15, (STATE_UNAVAILABLE, STATE_UNAVAILABLE)),  # Defrost.
        (400, 80, 32768, (STATE_UNAVAILABLE, STATE_UNAVAILABLE)),  # Missing power.
        (353, 80, 15, ("0.42", STATE_UNAVAILABLE)),  # Recover at the next 0.1 K step.
    ]
    for supply_raw, status_raw, power_raw, expected in cases:
        unit.load_raw({"input": {542: supply_raw, 2500: status_raw, 3679: power_raw}})
        await mock_config_entry.runtime_data.async_refresh()
        await hass.async_block_till_done()
        states = [hass.states.get(entry.entity_id) for entry in entities]
        assert all(state is not None for state in states)
        assert tuple(state.state for state in states) == expected
        assert all("state_class" not in state.attributes for state in states)
        assert all("unit_of_measurement" not in state.attributes for state in states)
