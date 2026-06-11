"""Decode WPM power consumption statistics exposed by pystiebeleltron.

Registers 3708-3723 match the Servicewelt POWER CONSUMPTION screen. They are
read by ``WpmStiebelEltronAPI`` via ``WpmPowerConsumptionRegisters`` in
pystiebeleltron (Modbus block base 3707).

Encoding:
- Single register: value = raw / 1000 (kWh or MWh depending on sensor)
- Register pair: value = whole + fraction / 1000
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntityDescription
from pystiebeleltron.wpm import WpmPowerConsumptionRegisters

POWER_CONSUMPTION_SCALE = 1000.0


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
