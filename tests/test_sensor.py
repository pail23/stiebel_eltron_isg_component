"""Tests for the sensor platform."""

from types import SimpleNamespace

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfFrequency

from custom_components.stiebel_eltron_isg.const import (
    COMPRESSOR_HEATING,
    COMPRESSOR_HEATING_WATER,
    COMPRESSOR_SPEED,
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
