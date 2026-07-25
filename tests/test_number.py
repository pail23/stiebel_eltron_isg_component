"""Tests for the number platform."""

from types import SimpleNamespace

from pystiebeleltron.lwz import LwzSystemParameters
import pytest

from custom_components.stiebel_eltron_isg.const import (
    AREA_COOLING_FLOW_TEMPERATURE_HYSTERESIS,
    FAN_COOLING_FLOW_TEMPERATURE_HYSTERESIS,
    FAN_LEVEL_MANUAL,
    FAN_LEVEL_PARTY,
)
from custom_components.stiebel_eltron_isg.number import (
    NUMBER_TYPES_LWZ,
    NUMBER_TYPES_WPM,
    StiebelEltronISGNumberEntity,
)


class _StubCoordinator:
    """Minimal coordinator stub exposing the value accessor API."""

    def __init__(self, current: float | None) -> None:
        self._current = current
        self.writes: list[tuple] = []
        self.refresh_generation = 0
        self.last_successful_refresh_generation = 0
        self.last_update_success = True

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
    # Written state is pushed to hass, which does not exist in these unit tests.
    entity.async_write_ha_state = lambda: None
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


async def test_number_shows_written_value_before_the_next_poll() -> None:
    """A written value must be reported at once, not only after the next poll."""
    entity = _make_number(current=10.0)

    await entity.async_set_native_value(12.0)

    assert entity.native_value == 12.0


async def test_number_can_return_to_device_value_before_the_next_poll() -> None:
    """A correction must be compared with the visible optimistic value."""
    entity = _make_number(current=10.0)

    await entity.async_set_native_value(12.0)
    await entity.async_set_native_value(10.0)

    assert entity.coordinator.writes == [
        ("system_parameters", "set_flow_temperature_area", 12.0),
        ("system_parameters", "set_flow_temperature_area", 10.0),
    ]
    assert entity.native_value == 10.0


async def test_number_returns_to_the_device_value_once_polled() -> None:
    """A poll made after the write must hand the value back to the device."""
    entity = _make_number(current=10.0)
    entity.coordinator.refresh_generation = 1
    await entity.async_set_native_value(12.0)

    # The controller clamped the value, which a later poll reports.
    entity.coordinator._current = 11.0

    entity.coordinator.last_successful_refresh_generation = 1
    entity._handle_coordinator_update()
    assert entity.native_value == 12.0

    entity.coordinator.refresh_generation = 2
    entity.coordinator.last_successful_refresh_generation = 2
    entity._handle_coordinator_update()

    assert entity.native_value == 11.0


async def test_number_uses_the_first_poll_started_after_the_write() -> None:
    """Without an in-flight poll, the next successful poll is authoritative."""
    entity = _make_number(current=10.0)
    await entity.async_set_native_value(12.0)
    entity.coordinator._current = 11.0
    entity.coordinator.refresh_generation = 1
    entity.coordinator.last_successful_refresh_generation = 1

    entity._handle_coordinator_update()

    assert entity.native_value == 11.0


async def test_number_does_not_assume_a_value_it_did_not_write() -> None:
    """A failed write must not change the reported value."""
    entity = _make_number(current=10.0)
    entity.coordinator.write_component_value = _failed_write

    with pytest.raises(RuntimeError, match="write failed"):
        await entity.async_set_native_value(12.0)

    assert entity.native_value == 10.0


async def _failed_write(component, field, value) -> None:
    """Stand in for a coordinator write that raises its translated error."""
    raise RuntimeError("write failed")


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


def test_lwz_fan_level_numbers_resolve_against_the_lwz_api() -> None:
    """Party and manual fan level must exist on the LWZ system parameters.

    The two entities were added because LWZ holding registers 1020 and 1021,
    documented addresses, carry the party and the manual ventilation stage, and
    only day and night were exposed before. Resolving the accessors against the
    real library class guards against a renamed or missing field.
    """
    by_key = {description.key: description for description in NUMBER_TYPES_LWZ}
    api = SimpleNamespace(system_parameters=LwzSystemParameters)

    for key, field in (
        (FAN_LEVEL_PARTY, "party_stage"),
        (FAN_LEVEL_MANUAL, "manual_stage"),
    ):
        description = by_key[key]
        assert description.modbus_register(api) is getattr(LwzSystemParameters, field)
        assert description.write_field == field
        assert (description.native_min_value, description.native_max_value) == (0, 3)
        assert description.native_step == 1
