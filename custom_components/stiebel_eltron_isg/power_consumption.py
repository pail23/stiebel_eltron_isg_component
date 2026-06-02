"""WPM power consumption statistics (Modbus input registers 3700-3725).

These values match the Servicewelt POWER CONSUMPTION screen. They are not
documented in Stiebel Modbus software documentation 9535 (energy block ends
at register 3655), but are readable on WPM / WPM 3 / WPM 3i controllers.

Encoding:
- Single register: value = raw / 1000 (kWh or MWh depending on sensor)
- Register pair: value = whole + fraction / 1000
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription
from pystiebeleltron import IsgRegisters, ModbusRegister

POWER_CONSUMPTION_BASE_ADDRESS = 3699
POWER_CONSUMPTION_REGISTER_COUNT = 26
POWER_CONSUMPTION_SCALE = 1000.0


class WpmPowerConsumptionRegisters(IsgRegisters):
    """Undocumented WPM power consumption statistic registers."""

    HEATING_24H = 3708
    HEATING_12M_FRACTION = 3710
    HEATING_12M_WHOLE = 3711
    COOLING_24H_FRACTION = 3714
    COOLING_24H_WHOLE = 3715
    COOLING_12M = 3716
    DHW_24H_FRACTION = 3720
    DHW_24H_WHOLE = 3721
    DHW_12M_FRACTION = 3722
    DHW_12M_WHOLE = 3723


def _power_register(
    register: WpmPowerConsumptionRegisters, name: str
) -> ModbusRegister:
    return ModbusRegister(
        address=register.value,
        name=name,
        unit="kWh",
        min=0.0,
        max=65535.0,
        data_type=6,
        key=register,
    )


WPM_POWER_CONSUMPTION_REGISTERS: dict[IsgRegisters, ModbusRegister] = {
    WpmPowerConsumptionRegisters.HEATING_24H: _power_register(
        WpmPowerConsumptionRegisters.HEATING_24H, "VD HEATING POWER 24H"
    ),
    WpmPowerConsumptionRegisters.HEATING_12M_FRACTION: _power_register(
        WpmPowerConsumptionRegisters.HEATING_12M_FRACTION,
        "VD HEATING POWER 12M FRACTION",
    ),
    WpmPowerConsumptionRegisters.HEATING_12M_WHOLE: _power_register(
        WpmPowerConsumptionRegisters.HEATING_12M_WHOLE,
        "VD HEATING POWER 12M WHOLE",
    ),
    WpmPowerConsumptionRegisters.COOLING_24H_FRACTION: _power_register(
        WpmPowerConsumptionRegisters.COOLING_24H_FRACTION,
        "VD COOLING POWER 24H FRACTION",
    ),
    WpmPowerConsumptionRegisters.COOLING_24H_WHOLE: _power_register(
        WpmPowerConsumptionRegisters.COOLING_24H_WHOLE,
        "VD COOLING POWER 24H WHOLE",
    ),
    WpmPowerConsumptionRegisters.COOLING_12M: _power_register(
        WpmPowerConsumptionRegisters.COOLING_12M, "VD COOLING POWER 12M"
    ),
    WpmPowerConsumptionRegisters.DHW_24H_FRACTION: _power_register(
        WpmPowerConsumptionRegisters.DHW_24H_FRACTION, "VD DHW POWER 24H FRACTION"
    ),
    WpmPowerConsumptionRegisters.DHW_24H_WHOLE: _power_register(
        WpmPowerConsumptionRegisters.DHW_24H_WHOLE, "VD DHW POWER 24H WHOLE"
    ),
    WpmPowerConsumptionRegisters.DHW_12M_FRACTION: _power_register(
        WpmPowerConsumptionRegisters.DHW_12M_FRACTION, "VD DHW POWER 12M FRACTION"
    ),
    WpmPowerConsumptionRegisters.DHW_12M_WHOLE: _power_register(
        WpmPowerConsumptionRegisters.DHW_12M_WHOLE, "VD DHW POWER 12M WHOLE"
    ),
}


@dataclass(frozen=True, kw_only=True)
class PowerConsumptionSensorEntityDescription(SensorEntityDescription):
    """Entity description for a decoded power consumption statistic."""

    fraction_register: WpmPowerConsumptionRegisters
    whole_register: WpmPowerConsumptionRegisters | None = None


def decode_power_consumption_value(
    coordinator: object,
    description: PowerConsumptionSensorEntityDescription,
) -> float | None:
    """Decode a power consumption statistic from raw Modbus registers."""
    fraction = coordinator.get_register_value(description.fraction_register)
    if fraction is None:
        return None

    if description.whole_register is None:
        return float(fraction) / POWER_CONSUMPTION_SCALE

    whole = coordinator.get_register_value(description.whole_register)
    if whole is None:
        return None

    return float(whole) + float(fraction) / POWER_CONSUMPTION_SCALE
