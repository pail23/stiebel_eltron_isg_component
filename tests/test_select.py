"""Tests for the select platform."""

from unittest.mock import AsyncMock

import pytest

from custom_components.stiebel_eltron_isg.select import StiebelEltronISGSelectEntity
from tests.pending import FakeApi, FakeComponent, attach, make_coordinator, poll

_OPTIONS = {0: "off", 1: "eco", 2: "comfort"}


def _make_select(current: int | None) -> StiebelEltronISGSelectEntity:
    entity = StiebelEltronISGSelectEntity.__new__(StiebelEltronISGSelectEntity)
    writes: list[tuple] = []
    coordinator = make_coordinator(
        FakeApi(writes, system_parameters={"operating_mode": current})
    )
    coordinator.writes = writes
    entity._options = _OPTIONS
    entity.modbus_register = lambda api: api.system_parameters.operating_mode
    entity.write_component = "system_parameters"
    entity.write_field = "operating_mode"
    attach(coordinator, entity)
    return entity


def _device(entity: StiebelEltronISGSelectEntity) -> FakeComponent:
    return entity.coordinator._api.system_parameters


async def test_select_writes_the_key_of_the_option() -> None:
    """Selecting an option must write the key that option maps to."""
    entity = _make_select(current=0)

    await entity.async_select_option("comfort")

    assert entity.coordinator.writes == [("system_parameters", "operating_mode", 2)]


async def test_select_skips_write_when_option_is_unchanged() -> None:
    """Selecting the reported option again must not issue a Modbus write."""
    entity = _make_select(current=2)

    await entity.async_select_option("comfort")

    assert entity.coordinator.writes == []


async def test_select_writes_when_current_option_is_unknown() -> None:
    """An unknown read-back must not suppress a valid option write."""
    entity = _make_select(current=None)

    await entity.async_select_option("comfort")

    assert entity.coordinator.writes == [("system_parameters", "operating_mode", 2)]
    assert entity.current_option == "comfort"


async def test_select_shows_written_option_before_the_next_poll() -> None:
    """A selected option must be reported at once, not only after the next poll."""
    entity = _make_select(current=0)

    await entity.async_select_option("comfort")

    assert entity.current_option == "comfort"


async def test_select_returns_to_the_device_value_once_polled() -> None:
    """Only a poll started after the write hands the option back to the device."""
    entity = _make_select(current=0)

    async def write_while_polling() -> None:
        await entity.async_select_option("comfort")

    # This poll was in flight during the write and may have read the old mode.
    await poll(entity.coordinator, during=write_while_polling)
    assert entity.current_option == "comfort"

    # The controller rejected the mode and stayed where it was.
    await poll(entity.coordinator)

    assert entity.current_option == "off"


async def test_select_keeps_written_option_when_refresh_fails() -> None:
    """A failed poll has no fresh device option to replace the selected one."""
    entity = _make_select(current=0)
    await entity.async_select_option("comfort")

    await poll(entity.coordinator, success=False)

    assert entity.current_option == "comfort"

    await poll(entity.coordinator)

    assert entity.current_option == "off"


async def test_select_does_not_assume_an_option_it_did_not_write() -> None:
    """A failed write must not change the reported option."""
    entity = _make_select(current=0)
    _device(entity).write = AsyncMock(side_effect=RuntimeError("write failed"))

    with pytest.raises(RuntimeError, match="write failed"):
        await entity.async_select_option("comfort")

    assert entity.current_option == "off"


async def test_select_ignores_an_unknown_option() -> None:
    """An option outside the mapping must not write anything."""
    entity = _make_select(current=0)

    await entity.async_select_option("does not exist")

    assert entity.coordinator.writes == []
    assert entity.current_option == "off"
