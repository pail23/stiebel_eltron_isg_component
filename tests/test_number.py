"""Tests for the number platform."""

from custom_components.stiebel_eltron_isg.number import StiebelEltronISGNumberEntity


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
