"""Tests for the switch platform."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.stiebel_eltron_isg.const import SG_READY_ACTIVE, SG_READY_INPUT_1
from custom_components.stiebel_eltron_isg.switch import (
    StiebelEltronISGSwitch,
    StiebelEltronSwitchEntityDescription,
)


def _make_switch(key: str, last_update_success: bool) -> StiebelEltronISGSwitch:
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.entity_description = SimpleNamespace(key=key)
    entity.coordinator = SimpleNamespace(last_update_success=last_update_success)
    return entity


def test_write_only_switch_unavailable_when_last_update_failed() -> None:
    """A write-only switch must still go unavailable on a failed update."""
    entity = _make_switch(SG_READY_INPUT_1, last_update_success=False)

    assert entity.available is False


def test_write_only_switch_available_when_update_succeeded() -> None:
    """With a successful update a write-only switch stays available."""
    entity = _make_switch(SG_READY_INPUT_1, last_update_success=True)

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
    [(None, False), (0, False), (1, True)],
)
def test_switch_state_uses_the_register_value(value, expected: bool) -> None:
    """Missing and zero values are off; any non-zero value is on."""
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    api = SimpleNamespace(value=value)
    entity.modbus_register = lambda api: api.value
    entity.coordinator = SimpleNamespace(get_value=lambda accessor: accessor(api))

    assert entity.is_on is expected


@pytest.mark.parametrize(
    ("method", "value"), [("async_turn_on", 1), ("async_turn_off", 0)]
)
async def test_switch_action_writes_and_updates(method: str, value: int) -> None:
    """Switch actions use the central write path and then refresh their state."""
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.write_component = "settings"
    entity.write_field = "enabled"
    entity.coordinator = SimpleNamespace(write_component_value=AsyncMock())
    entity.async_update = AsyncMock()

    await getattr(entity, method)()

    entity.coordinator.write_component_value.assert_awaited_once_with(
        "settings", "enabled", value
    )
    entity.async_update.assert_awaited_once()


@pytest.mark.parametrize("method", ["async_turn_on", "async_turn_off"])
async def test_switch_without_write_target_does_nothing(method: str) -> None:
    """A read-only description must never attempt a write."""
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.write_component = None
    entity.write_field = None
    entity.coordinator = SimpleNamespace(write_component_value=AsyncMock())

    await getattr(entity, method)()

    entity.coordinator.write_component_value.assert_not_awaited()


def test_regular_switch_availability_requires_a_value() -> None:
    """Read-back switches use the shared coordinator availability rules."""
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.entity_description = SimpleNamespace(key=SG_READY_ACTIVE)
    entity.modbus_register = lambda api: None
    entity.coordinator = SimpleNamespace(
        last_update_success=True,
        has_value=lambda register: False,
    )

    assert entity.available is False
