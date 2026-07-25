"""Modbus api for stiebel eltron heat pumps. This file is generated. Do not modify it manually."""
# ruff: noqa: D101, D102, D107

from __future__ import annotations

from modbus_connection import ModbusUnit
from modbus_connection.model import Component, ComponentGroup, gauge, integer
from pystiebeleltron import UNAVAILABLE, in_range, scaled_sum

WPM3I_HOLDING_RANGES = ((1500, 1520), (4000, 4002))
WPM3I_INPUT_RANGES = ((500, 540), (2500, 2506), (3500, 3521), (5000, 5001))


class Wpm3iSystemValues(Component):
    register_space = "input"
    register_ranges = WPM3I_INPUT_RANGES

    actual_temperature_fe7 = gauge(500, 0.1, nan=UNAVAILABLE, unit="°C")
    set_temperature_fe7 = gauge(501, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_temperature_fek = gauge(502, 0.1, nan=UNAVAILABLE, unit="°C")
    set_temperature_fek = gauge(503, 0.1, nan=UNAVAILABLE, unit="°C")
    relative_humidity = gauge(504, 0.1, nan=UNAVAILABLE, unit="%")
    dew_point_temperature = gauge(505, 0.1, nan=UNAVAILABLE, unit="°C")
    outside_temperature = gauge(506, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_temperature_hk_1 = gauge(507, 0.1, nan=UNAVAILABLE, unit="°C")
    set_temperature_hk_1_wpm3i = gauge(508, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_temperature_hk_2 = gauge(510, 0.1, nan=UNAVAILABLE, unit="°C")
    set_temperature_hk_2 = gauge(511, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_flow_temperature_wp = gauge(512, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_flow_temperature_nhz = gauge(513, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_flow_temperature = gauge(514, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_return_temperature = gauge(515, 0.1, nan=UNAVAILABLE, unit="°C")
    set_fixed_temperature = gauge(516, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_buffer_temperature = gauge(517, 0.1, nan=UNAVAILABLE, unit="°C")
    set_buffer_temperature = gauge(518, 0.1, nan=UNAVAILABLE, unit="°C")
    heating_pressure = gauge(519, 0.01, nan=UNAVAILABLE, unit="bar")
    flow_rate = gauge(520, 0.01, nan=UNAVAILABLE, unit="l/min")
    actual_temperature_dhw = gauge(521, 0.1, nan=UNAVAILABLE, unit="°C")
    set_temperature_dhw = gauge(522, 0.1, nan=UNAVAILABLE, unit="°C")
    actual_temperature_fan = gauge(523, 0.1, nan=UNAVAILABLE, unit="K")
    set_temperature_fan = gauge(524, 0.1, nan=UNAVAILABLE, unit="K")
    actual_temperature_area = gauge(525, 0.1, nan=UNAVAILABLE, unit="K")
    set_temperature_area = gauge(526, 0.1, nan=UNAVAILABLE, unit="K")
    application_limit_hzg = gauge(532, 0.1, nan=UNAVAILABLE, unit="°C")
    application_limit_ww = gauge(533, 0.1, nan=UNAVAILABLE, unit="°C")
    source_temperature = gauge(535, 0.1, nan=UNAVAILABLE, unit="°C")
    min_source_temperature = gauge(536, 0.1, nan=UNAVAILABLE, unit="°C")
    source_pressure = gauge(537, 0.01, nan=UNAVAILABLE, unit="bar")
    hot_gas_temperature = gauge(538, 0.1, nan=UNAVAILABLE, unit="°C")
    high_pressure = gauge(539, 0.1, nan=UNAVAILABLE, unit="bar")
    low_pressure = gauge(540, 0.1, nan=UNAVAILABLE, unit="bar")


class Wpm3iSystemParameters(Component):
    register_space = "holding"
    register_ranges = WPM3I_HOLDING_RANGES

    operating_mode = integer(
        1500, signed=False, nan=UNAVAILABLE, writable=in_range(0, 5)
    )
    comfort_temperature_hk_1 = gauge(
        1501, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(5, 30)
    )
    eco_temperature_hk_1 = gauge(
        1502, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(5, 30)
    )
    heating_curve_rise_hk_1 = gauge(
        1503, 0.01, nan=UNAVAILABLE, writable=in_range(0, 3)
    )
    comfort_temperature_hk_2 = gauge(
        1504, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(5, 30)
    )
    eco_temperature_hk_2 = gauge(
        1505, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(5, 30)
    )
    heating_curve_rise_hk_2 = gauge(
        1506, 0.01, nan=UNAVAILABLE, writable=in_range(0, 3)
    )
    fixed_value_operation = gauge(
        1507, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(20, 70)
    )
    dual_mode_temp_hzg = gauge(
        1508, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(-40, 40)
    )
    comfort_temperature = gauge(
        1509, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(10, 60)
    )
    eco_temperature = gauge(
        1510, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(10, 60)
    )
    dhw_stages = integer(1511, signed=False, nan=UNAVAILABLE, writable=in_range(0, 6))
    dual_mode_temp_ww = gauge(
        1512, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(-40, 40)
    )
    set_flow_temperature_area = gauge(
        1513, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(7, 25)
    )
    flow_temp_hysteresis_area = gauge(
        1514, 0.1, nan=UNAVAILABLE, unit="K", writable=in_range(1, 5)
    )
    set_room_temperature_area = gauge(
        1515, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(20, 30)
    )
    set_flow_temperature_fan = gauge(
        1516, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(7, 25)
    )
    flow_temp_hysteresis_fan = gauge(
        1517, 0.1, nan=UNAVAILABLE, unit="K", writable=in_range(1, 5)
    )
    set_room_temperature_fan = gauge(
        1518, 0.1, nan=UNAVAILABLE, unit="°C", writable=in_range(20, 30)
    )
    reset = integer(1519, signed=False, nan=UNAVAILABLE, writable=in_range(1, 3))
    restart_isg = integer(1520, signed=False, nan=UNAVAILABLE, writable=in_range(0, 2))


class Wpm3iSystemState(Component):
    register_space = "input"
    register_ranges = WPM3I_INPUT_RANGES

    operating_status = integer(2500, signed=False, nan=UNAVAILABLE)
    power_off = integer(2501, signed=False, nan=UNAVAILABLE)
    fault_status = integer(2503, signed=False, nan=UNAVAILABLE)
    bus_status = integer(2504, signed=False, nan=UNAVAILABLE)
    active_error = integer(2506, signed=False, nan=UNAVAILABLE)


class Wpm3iEnergyData(Component):
    register_space = "input"
    register_ranges = WPM3I_INPUT_RANGES

    vd_heating_day = integer(3500, signed=False, nan=UNAVAILABLE, unit="kWh")
    vd_heating_total = scaled_sum(3501, (1, 1000), unit="kWh")
    vd_dhw_day = integer(3503, signed=False, nan=UNAVAILABLE, unit="kWh")
    vd_dhw_total = scaled_sum(3504, (1, 1000), unit="kWh")
    nhz_heating_total = scaled_sum(3506, (1, 1000), unit="kWh")
    nhz_dhw_total = scaled_sum(3508, (1, 1000), unit="kWh")
    vd_heating_day_consumed = integer(3510, signed=False, nan=UNAVAILABLE, unit="kWh")
    vd_heating_total_consumed = scaled_sum(3511, (1, 1000), unit="kWh")
    vd_dhw_day_consumed = integer(3513, signed=False, nan=UNAVAILABLE, unit="kWh")
    vd_dhw_total_consumed = scaled_sum(3514, (1, 1000), unit="kWh")
    vd_heating = integer(3516, signed=False, nan=UNAVAILABLE, unit="h")
    vd_dhw = integer(3517, signed=False, nan=UNAVAILABLE, unit="h")
    vd_cooling = integer(3518, signed=False, nan=UNAVAILABLE, unit="h")
    nhz_1 = integer(3519, signed=False, nan=UNAVAILABLE, unit="h")
    nhz_2 = integer(3520, signed=False, nan=UNAVAILABLE, unit="h")
    nhz_1_2 = integer(3521, signed=False, nan=UNAVAILABLE, unit="h")

    _DAY_AND_TOTAL = (
        ("vd_heating_day", "vd_heating_total", "vd_heating_day_and_total"),
        ("vd_dhw_day", "vd_dhw_total", "vd_dhw_day_and_total"),
        (
            "vd_heating_day_consumed",
            "vd_heating_total_consumed",
            "vd_heating_day_and_total_consumed",
        ),
        (
            "vd_dhw_day_consumed",
            "vd_dhw_total_consumed",
            "vd_dhw_day_and_total_consumed",
        ),
    )

    def __init__(self, unit: ModbusUnit, index: int = 1) -> None:
        super().__init__(unit, index)
        self._running_totals: dict[str, int] = {}

    def notify(self) -> None:
        """Refresh the monotonic day-and-total counters, then notify listeners."""
        for day_attr, total_attr, key in self._DAY_AND_TOTAL:
            day = getattr(self, day_attr)
            total = getattr(self, total_attr)
            if day is not None and total is not None:
                combined = day + total
                previous = self._running_totals.get(key)
                self._running_totals[key] = (
                    combined if previous is None else max(combined, previous)
                )
        super().notify()

    @property
    def vd_heating_day_and_total(self) -> int | None:
        return self._running_totals.get("vd_heating_day_and_total")

    @property
    def vd_dhw_day_and_total(self) -> int | None:
        return self._running_totals.get("vd_dhw_day_and_total")

    @property
    def vd_heating_day_and_total_consumed(self) -> int | None:
        return self._running_totals.get("vd_heating_day_and_total_consumed")

    @property
    def vd_dhw_day_and_total_consumed(self) -> int | None:
        return self._running_totals.get("vd_dhw_day_and_total_consumed")


class Wpm3iEnergyManagementSettings(Component):
    register_space = "holding"
    register_ranges = WPM3I_HOLDING_RANGES

    switch_sg_ready_on_and_off = integer(
        4000, signed=False, nan=UNAVAILABLE, writable=in_range(0, 1)
    )
    sg_ready_input_1 = integer(
        4001, signed=False, nan=UNAVAILABLE, writable=in_range(0, 1)
    )
    sg_ready_input_2 = integer(
        4002, signed=False, nan=UNAVAILABLE, writable=in_range(0, 1)
    )


class Wpm3iEnergySystemInformation(Component):
    register_space = "input"
    register_ranges = WPM3I_INPUT_RANGES

    sg_ready_operating_state = integer(5000, signed=False, nan=UNAVAILABLE)
    controller_identification = integer(5001, signed=False, nan=UNAVAILABLE)


class Wpm3iStiebelEltronAPI:
    """Stiebel Eltron heat pump API over a modbus_connection ModbusUnit."""

    def __init__(self, unit: ModbusUnit) -> None:
        self.system_values = Wpm3iSystemValues(unit)
        self.system_parameters = Wpm3iSystemParameters(unit)
        self.system_state = Wpm3iSystemState(unit)
        self.energy_data = Wpm3iEnergyData(unit)
        self.energy_management_settings = Wpm3iEnergyManagementSettings(unit)
        self.energy_system_information = Wpm3iEnergySystemInformation(unit)
        self._group = ComponentGroup(
            unit,
            [
                self.system_values,
                self.system_parameters,
                self.system_state,
                self.energy_data,
                self.energy_management_settings,
                self.energy_system_information,
            ],
        )

    async def async_update(self) -> None:
        """Read every component in one pooled set of block reads."""
        await self._group.async_update()
