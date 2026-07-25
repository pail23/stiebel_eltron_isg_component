"""Tests for the sensor platform."""

from types import SimpleNamespace

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfFrequency

from custom_components.stiebel_eltron_isg.const import (
    COMPRESSOR_HEATING,
    COMPRESSOR_HEATING_WATER,
    COMPRESSOR_SPEED,
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
    LWZ_SENSOR_TYPES,
    WPM_3I_SENSOR_TYPES,
    WPM_SENSOR_TYPES,
)


def _wpm(key: str):
    return next(d for d in WPM_SENSOR_TYPES if d.key == key)


def _lwz(key: str):
    return next(d for d in LWZ_SENSOR_TYPES if d.key == key)


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


def test_lwz_exposes_compressor_frequency() -> None:
    """LWZ compressor frequency reads system_values.compressor_speed (Hz)."""
    api = SimpleNamespace(system_values=SimpleNamespace(compressor_speed=31.0))

    speed = _lwz(COMPRESSOR_SPEED)
    assert speed.modbus_register(api) == 31.0
    assert speed.native_unit_of_measurement == UnitOfFrequency.HERTZ
    assert speed.device_class == SensorDeviceClass.FREQUENCY


def test_wpm_exposes_power_consumption_statistics() -> None:
    """WPM power-consumption windows read the 3707-3723 energy_data fields.

    Each window is a register pair that the library sums as
    ``low + high * 1000``, which yields the smaller of the two units the
    Servicewelt screen displays: the 24 h windows come out in Wh (Servicewelt
    shows kWh) and the 12-month windows in kWh (Servicewelt shows MWh). The
    values below are the readings bartveenstra measured against Servicewelt on
    a real WPMsystem while reverse engineering this block, see pull request
    #544.
    """
    api = SimpleNamespace(
        energy_data=SimpleNamespace(
            heating_24h=12,
            heating_12m=7244,  # Servicewelt: 7.244 MWh
            heating_13_24=3210,
            cooling_24h=1904,  # Servicewelt: 1.904 kWh
            cooling_12m=210,
            cooling_13_24=198,
            dhw_24h=19574,  # Servicewelt: 19.574 kWh
            dhw_12m=1500,
            dhw_13_24=1450,
        )
    )
    wh = UnitOfEnergy.WATT_HOUR
    kwh = UnitOfEnergy.KILO_WATT_HOUR
    expected = {
        CONSUMED_HEATING_LAST_24H: (12, wh),
        CONSUMED_HEATING_12M: (7244, kwh),
        CONSUMED_HEATING_PREV_12M: (3210, kwh),
        CONSUMED_COOLING_LAST_24H: (1904, wh),
        CONSUMED_COOLING_12M: (210, kwh),
        CONSUMED_COOLING_PREV_12M: (198, kwh),
        CONSUMED_WATER_HEATING_LAST_24H: (19574, wh),
        CONSUMED_WATER_HEATING_12M: (1500, kwh),
        CONSUMED_WATER_HEATING_PREV_12M: (1450, kwh),
    }

    for key, (value, unit) in expected.items():
        desc = _wpm(key)
        assert desc.modbus_register(api) == value
        assert desc.native_unit_of_measurement == unit
        assert desc.device_class == SensorDeviceClass.ENERGY
        # Rolling windows reset, so they must not be TOTAL_INCREASING.
        assert desc.state_class == SensorStateClass.TOTAL
