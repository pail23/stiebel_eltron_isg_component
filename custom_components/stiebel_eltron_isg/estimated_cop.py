"""Optional water-side inverter COP estimates for a single WPMsystem unit."""

from math import isfinite
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from pystiebeleltron.wpm import WpmStiebelEltronAPI

_HEATING = 1 << 4
_DHW = 1 << 5
_COMPRESSOR = 1 << 6
_EXCLUDED = (1 << 3) | (1 << 8) | (1 << 9)  # Booster, cooling, defrost.

# Approximate rho * cp / 60 for liquid water, in kW per (L/min * K).
_WATER_KW_PER_L_MIN_K = 0.06977


def estimated_water_inverter_cop(
    api: WpmStiebelEltronAPI, mode: Literal["heating", "dhw"]
) -> float | None:
    """Estimate COP from one coordinator update, with explicit mode attribution.

    This assumes water and HP1/IWS1 on a single-unit WPMsystem. It is not a
    calibrated heat meter, a whole-system COP, or an energy-window ratio.
    The inverter reading has 0.1 kW resolution; the low-power and delta-T
    guards only avoid division near zero and do not establish accuracy.
    Firmware may report different registers with different internal delays.
    """
    status = api.system_state.operating_status
    if (
        isinstance(status, bool)
        or not isinstance(status, int)
        or not 0 <= status <= 0xFFFF
        or not status & _COMPRESSOR
        or status & _EXCLUDED
    ):
        return None
    expected_mode = _HEATING if mode == "heating" else _DHW
    if status & (_HEATING | _DHW) != expected_mode:
        return None

    pump = api.system_values.heat_pumps[0]
    flow = pump.wp_water_flow_rate
    supply = pump.flow_temperature
    return_temp = pump.return_temperature
    electricity = api.extended_energy_data.inverter_power_iws_1
    values = (flow, supply, return_temp, electricity)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
        for value in values
    ):
        return None

    delta_t = supply - return_temp
    if flow <= 0 or electricity < 0.2 or delta_t <= 0.2:
        return None
    ratio = _WATER_KW_PER_L_MIN_K * flow * delta_t / electricity
    # Do not clip to an arbitrary COP range: it would hide unusual readings.
    return round(ratio, 2) if isfinite(ratio) else None
