"""Tests for the number platform."""

from types import SimpleNamespace

from custom_components.stiebel_eltron_isg.const import (
    AREA_COOLING_FLOW_TEMPERATURE_HYSTERESIS,
    FAN_COOLING_FLOW_TEMPERATURE_HYSTERESIS,
)
from custom_components.stiebel_eltron_isg.number import (
    NUMBER_TYPES_WPM,
    StiebelEltronISGNumberEntity,
)


class _StubCoordinator:
    """Minimal coordinator stub exposing the value accessor API."""

    def __init__(self, current: float | None) -> None:
        self._current = current
        self.writes: list[tuple] = []

    def get_value(self, accessor) -> float | None:
        return self._current

    async def write_component_value(self, component, field, value) -> None:
        self.writes.append((component, field, value))


def _make_number(current: float | None) -> StiebelEltronISGNumberEntity:
    entity = StiebelEltronISGNumberEntity.__new__(StiebelEltronISGNumberEntity)
    entity.coordinator = _StubCoordinator(current)
    entity.modbus_register = lambda api: None
    entity.write_component = "system_parameters"
    entity.write_field = "set_flow_temperature_area"
    return entity


async def test_number_skips_write_when_value_unchanged() -> None:
    """Setting the current value again must not issue a modbus write."""
    entity = _make_number(current=10.0)

    await entity.async_set_native_value(10.0)

    assert entity.coordinator.writes == []


async def test_number_writes_when_value_changed() -> None:
    """Setting a different value must issue exactly one write."""
    entity = _make_number(current=10.0)

    await entity.async_set_native_value(12.0)

    assert entity.coordinator.writes == [
        ("system_parameters", "set_flow_temperature_area", 12.0)
    ]


async def test_number_skips_write_within_float_tolerance() -> None:
    """A float-imprecise current value equal to the target must skip the write.

    The library decodes scaled registers as ``raw * 0.1``, so the reported
    value for 7.1 is ``71 * 0.1`` which is not exactly ``7.1``.
    """
    current = 71 * 0.1
    assert current != 7.1
    entity = _make_number(current=current)

    await entity.async_set_native_value(7.1)

    assert entity.coordinator.writes == []


async def test_number_writes_when_current_value_unknown() -> None:
    """An unknown (None) current value must still issue the write."""
    entity = _make_number(current=None)

    await entity.async_set_native_value(7.1)

    assert entity.coordinator.writes == [
        ("system_parameters", "set_flow_temperature_area", 7.1)
    ]


async def test_number_without_write_field_does_not_write() -> None:
    """A number without a write field must never write."""
    entity = _make_number(current=10.0)
    entity.write_field = None

    await entity.async_set_native_value(12.0)

    assert entity.coordinator.writes == []


def _description(key: str):
    return next(d for d in NUMBER_TYPES_WPM if d.key == key)


def test_area_cooling_hysteresis_number_is_wired() -> None:
    """The area cooling flow-temperature hysteresis number reads/writes 1514."""
    description = _description(AREA_COOLING_FLOW_TEMPERATURE_HYSTERESIS)

    api = SimpleNamespace(
        system_parameters=SimpleNamespace(flow_temp_hysteresis_area=3.0)
    )
    assert description.modbus_register(api) == 3.0
    assert description.write_field == "flow_temp_hysteresis_area"
    assert (description.native_min_value, description.native_max_value) == (1, 5)


def test_fan_cooling_hysteresis_number_is_wired() -> None:
    """The fan cooling flow-temperature hysteresis number reads/writes 1517."""
    description = _description(FAN_COOLING_FLOW_TEMPERATURE_HYSTERESIS)

    api = SimpleNamespace(
        system_parameters=SimpleNamespace(flow_temp_hysteresis_fan=2.5)
    )
    assert description.modbus_register(api) == 2.5
    assert description.write_field == "flow_temp_hysteresis_fan"
    assert (description.native_min_value, description.native_max_value) == (1, 5)
