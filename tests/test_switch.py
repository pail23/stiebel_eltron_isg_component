"""Tests for the switch platform."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.stiebel_eltron_isg.const import (
    SG_READY_ACTIVE,
    SG_READY_INPUT_1,
    SG_READY_INPUT_2,
)
from custom_components.stiebel_eltron_isg.switch import (
    StiebelEltronISGSwitch,
    StiebelEltronSwitchEntityDescription,
)
from tests.pending import FakeApi, attach, make_coordinator, poll


def _make_writable_switch(value: int | None) -> StiebelEltronISGSwitch:
    """Build a switch over the real coordinator with a fake settings component."""
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    writes: list[tuple] = []
    coordinator = make_coordinator(FakeApi(writes, settings={"enabled": value}))
    coordinator.writes = writes
    entity.write_component = "settings"
    entity.write_field = "enabled"
    entity.modbus_register = lambda api: api.settings.enabled
    attach(coordinator, entity)
    return entity


def _make_switch(key: str, last_update_success: bool) -> StiebelEltronISGSwitch:
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.entity_description = SimpleNamespace(key=key)
    entity.coordinator = SimpleNamespace(last_update_success=last_update_success)
    return entity


@pytest.mark.parametrize("key", [SG_READY_INPUT_1, SG_READY_INPUT_2])
def test_write_only_switch_unavailable_when_last_update_failed(key: str) -> None:
    """A write-only switch must still go unavailable on a failed update."""
    entity = _make_switch(key, last_update_success=False)

    assert entity.available is False


@pytest.mark.parametrize("key", [SG_READY_INPUT_1, SG_READY_INPUT_2])
def test_write_only_switch_available_when_update_succeeded(key: str) -> None:
    """With a successful update a write-only switch stays available."""
    entity = _make_switch(key, last_update_success=True)

    assert entity.available is True


def test_switch_description_rejects_non_callable_register() -> None:
    """Register references must use the API accessor contract."""
    with pytest.raises(TypeError, match="must be a lambda expression"):
        StiebelEltronSwitchEntityDescription(
            key="invalid",
            modbus_register="legacy register token",
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, None), (0, False), (1, True)],
)
def test_switch_state_uses_the_register_value(value, expected: bool | None) -> None:
    """Zero is off, any non-zero value is on, and a missing value is unknown."""
    entity = _make_writable_switch(value)

    assert entity.is_on is expected


@pytest.mark.parametrize(
    ("method", "value"), [("async_turn_on", 1), ("async_turn_off", 0)]
)
async def test_switch_action_writes_and_shows_the_new_state(
    method: str, value: int
) -> None:
    """A changed state is written once and reported before the next poll."""
    entity = _make_writable_switch(1 - value)

    await getattr(entity, method)()

    assert entity.coordinator.writes == [("settings", "enabled", value)]
    assert entity.is_on is bool(value)
    assert entity.published_states == 1


@pytest.mark.parametrize(
    ("method", "value"), [("async_turn_on", 1), ("async_turn_off", 0)]
)
async def test_switch_skips_write_when_state_is_unchanged(
    method: str, value: int
) -> None:
    """Setting a known switch state again must not issue a Modbus write."""
    entity = _make_writable_switch(value)

    await getattr(entity, method)()

    assert entity.coordinator.writes == []


async def test_switch_writes_when_read_back_is_unknown() -> None:
    """An unknown read-back must not be mistaken for the off state."""
    entity = _make_writable_switch(None)

    await entity.async_turn_off()

    assert entity.coordinator.writes == [("settings", "enabled", 0)]


async def test_switch_reverses_a_write_before_the_read_back_caught_up() -> None:
    """Turning off right after turning on must write, not compare the old read-back."""
    entity = _make_writable_switch(0)

    await entity.async_turn_on()
    await entity.async_turn_off()

    assert entity.coordinator.writes == [
        ("settings", "enabled", 1),
        ("settings", "enabled", 0),
    ]
    assert entity.is_on is False


async def test_switch_returns_to_the_device_state_once_polled() -> None:
    """A poll started after the write reports what the device made of it."""
    entity = _make_writable_switch(0)
    await entity.async_turn_on()
    assert entity.is_on is True

    # The device did not take the command, which the next poll shows.
    await poll(entity.coordinator)

    assert entity.is_on is False


@pytest.mark.parametrize("method", ["async_turn_on", "async_turn_off"])
async def test_switch_without_write_target_does_nothing(method: str) -> None:
    """A read-only description must never attempt a write."""
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.write_component = None
    entity.write_field = None
    entity.coordinator = SimpleNamespace(write_component_value=AsyncMock())

    await getattr(entity, method)()

    entity.coordinator.write_component_value.assert_not_awaited()


@pytest.mark.parametrize(("has_value", "expected"), [(False, False), (True, True)])
def test_regular_switch_availability_follows_read_back_value(
    has_value: bool,
    expected: bool,
) -> None:
    """Read-back switches use the shared coordinator availability rules."""
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.entity_description = SimpleNamespace(key=SG_READY_ACTIVE)
    entity.modbus_register = lambda api: None
    entity.coordinator = SimpleNamespace(
        last_update_success=True,
        has_value=lambda _register: has_value,
    )

    assert entity.available is expected
