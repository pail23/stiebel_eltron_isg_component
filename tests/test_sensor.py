"""Tests for the sensor platform."""

from types import SimpleNamespace

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy

from custom_components.stiebel_eltron_isg.const import (
    COMPRESSOR_HEATING,
    COMPRESSOR_HEATING_WATER,
    CONSUMED_COOLING_12M,
    CONSUMED_COOLING_LAST_24H,
    CONSUMED_COOLING_PREV_12M,
    CONSUMED_HEATING_12M,
    CONSUMED_HEATING_LAST_24H,
    CONSUMED_HEATING_PREV_12M,
    CONSUMED_WATER_HEATING_12M,
    CONSUMED_WATER_HEATING_LAST_24H,
    CONSUMED_WATER_HEATING_PREV_12M,
    COOLING_RUNTIME,
)
from custom_components.stiebel_eltron_isg.sensor import (
    WPM_3I_SENSOR_TYPES,
    WPM_SENSOR_TYPES,
)


def _wpm(key: str):
    return next(d for d in WPM_SENSOR_TYPES if d.key == key)


def test_wpm_exposes_compressor_runtime_hours() -> None:
    """WPM compressor runtime-hour sensors read vd_heating/vd_dhw/vd_cooling."""
    api = SimpleNamespace(
        energy_data=SimpleNamespace(vd_heating=2789, vd_dhw=1305, vd_cooling=9794)
    )

    heating = _wpm(COMPRESSOR_HEATING)
    assert heating.modbus_register(api) == 2789
    assert heating.native_unit_of_measurement == "h"

    water = _wpm(COMPRESSOR_HEATING_WATER)
    assert water.modbus_register(api) == 1305
    assert water.native_unit_of_measurement == "h"

    cooling = _wpm(COOLING_RUNTIME)
    assert cooling.modbus_register(api) == 9794
    assert cooling.native_unit_of_measurement == "h"


def test_wpm_3i_exposes_compressor_runtime_hours() -> None:
    """WPM_3i shares the vd_heating/vd_dhw/vd_cooling registers (3516-3518)."""
    keys = {d.key for d in WPM_3I_SENSOR_TYPES}
    assert {COMPRESSOR_HEATING, COMPRESSOR_HEATING_WATER, COOLING_RUNTIME} <= keys


def test_wpm_exposes_power_consumption_statistics() -> None:
    """WPM power-consumption windows read the 3707-3723 energy_data fields (kWh)."""
    api = SimpleNamespace(
        energy_data=SimpleNamespace(
            heating_24h=12,
            heating_12m=3456,
            heating_13_24=3210,
            cooling_24h=1,
            cooling_12m=210,
            cooling_13_24=198,
            dhw_24h=5,
            dhw_12m=1500,
            dhw_13_24=1450,
        )
    )
    expected = {
        CONSUMED_HEATING_LAST_24H: ("heating_24h", 12),
        CONSUMED_HEATING_12M: ("heating_12m", 3456),
        CONSUMED_HEATING_PREV_12M: ("heating_13_24", 3210),
        CONSUMED_COOLING_LAST_24H: ("cooling_24h", 1),
        CONSUMED_COOLING_12M: ("cooling_12m", 210),
        CONSUMED_COOLING_PREV_12M: ("cooling_13_24", 198),
        CONSUMED_WATER_HEATING_LAST_24H: ("dhw_24h", 5),
        CONSUMED_WATER_HEATING_12M: ("dhw_12m", 1500),
        CONSUMED_WATER_HEATING_PREV_12M: ("dhw_13_24", 1450),
    }

    for key, (_field, value) in expected.items():
        desc = _wpm(key)
        assert desc.modbus_register(api) == value
        assert desc.native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
        assert desc.device_class == SensorDeviceClass.ENERGY
        # Rolling windows reset, so they must not be TOTAL_INCREASING.
        assert desc.state_class == SensorStateClass.TOTAL
