"""Tests for WPM power consumption register decoding."""

from unittest.mock import Mock

from custom_components.stiebel_eltron_isg.power_consumption import (
    PowerConsumptionSensorEntityDescription,
    decode_power_consumption_value,
)
from pystiebeleltron.wpm import WpmPowerConsumptionRegisters


def _coordinator(values: dict) -> Mock:
    coordinator = Mock()
    coordinator.get_register_value = lambda register: values.get(register)
    return coordinator


def test_decode_single_register_heating_24h() -> None:
    """Single-register values are scaled by 1/1000."""
    description = PowerConsumptionSensorEntityDescription(
        key="consumed_heating_last_24h",
        fraction_register=WpmPowerConsumptionRegisters.HEATING_24H,
    )
    coordinator = _coordinator({WpmPowerConsumptionRegisters.HEATING_24H: 8})

    assert decode_power_consumption_value(coordinator, description) == 0.008


def test_decode_pair_heating_12m() -> None:
    """Paired registers encode whole units plus a milli fraction."""
    description = PowerConsumptionSensorEntityDescription(
        key="consumed_heating_total_12m",
        fraction_register=WpmPowerConsumptionRegisters.HEATING_12M_FRACTION,
        whole_register=WpmPowerConsumptionRegisters.HEATING_12M_WHOLE,
    )
    coordinator = _coordinator(
        {
            WpmPowerConsumptionRegisters.HEATING_12M_FRACTION: 244,
            WpmPowerConsumptionRegisters.HEATING_12M_WHOLE: 7,
        }
    )

    assert decode_power_consumption_value(coordinator, description) == 7.244


def test_decode_pair_cooling_24h() -> None:
    """Cooling last-24h matches Servicewelt pair encoding."""
    description = PowerConsumptionSensorEntityDescription(
        key="consumed_cooling_last_24h",
        fraction_register=WpmPowerConsumptionRegisters.COOLING_24H_FRACTION,
        whole_register=WpmPowerConsumptionRegisters.COOLING_24H_WHOLE,
    )
    coordinator = _coordinator(
        {
            WpmPowerConsumptionRegisters.COOLING_24H_FRACTION: 904,
            WpmPowerConsumptionRegisters.COOLING_24H_WHOLE: 1,
        }
    )

    assert decode_power_consumption_value(coordinator, description) == 1.904


def test_decode_single_register_cooling_12m() -> None:
    """12-month cooling total uses a single scaled register."""
    description = PowerConsumptionSensorEntityDescription(
        key="consumed_cooling_total_12m",
        fraction_register=WpmPowerConsumptionRegisters.COOLING_12M,
    )
    coordinator = _coordinator({WpmPowerConsumptionRegisters.COOLING_12M: 7})

    assert decode_power_consumption_value(coordinator, description) == 0.007
