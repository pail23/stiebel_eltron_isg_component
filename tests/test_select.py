"""Tests for the select platform."""

import pytest

from custom_components.stiebel_eltron_isg.select import StiebelEltronISGSelectEntity

_OPTIONS = {0: "off", 1: "eco", 2: "comfort"}


class _StubCoordinator:
    """Minimal coordinator stub exposing the value accessor API."""

    def __init__(self, current: int | None) -> None:
        self._current = current
        self.writes: list[tuple] = []
        self.refresh_generation = 0
        self.last_successful_refresh_generation = 0
        self.last_update_success = True

    def get_value(self, accessor) -> int | None:
        return self._current

    async def write_component_value(self, component, field, value) -> None:
        self.writes.append((component, field, value))


def _make_select(current: int | None) -> StiebelEltronISGSelectEntity:
    entity = StiebelEltronISGSelectEntity.__new__(StiebelEltronISGSelectEntity)
    entity.coordinator = _StubCoordinator(current)
    entity._options = _OPTIONS
    entity.modbus_register = lambda api: None
    entity.write_component = "system_parameters"
    entity.write_field = "operating_mode"
    # Written state is pushed to hass, which does not exist in these unit tests.
    entity.async_write_ha_state = lambda: None
    return entity


async def test_select_writes_the_key_of_the_option() -> None:
    """Selecting an option must write the key that option maps to."""
    entity = _make_select(current=0)

    await entity.async_select_option("comfort")

    assert entity.coordinator.writes == [("system_parameters", "operating_mode", 2)]


async def test_select_shows_written_option_before_the_next_poll() -> None:
    """A selected option must be reported at once, not only after the next poll."""
    entity = _make_select(current=0)

    await entity.async_select_option("comfort")

    assert entity.current_option == "comfort"


async def test_select_returns_to_the_device_value_once_polled() -> None:
    """A poll made after the write must hand the option back to the device."""
    entity = _make_select(current=0)
    entity.coordinator.refresh_generation = 1
    await entity.async_select_option("comfort")

    entity.coordinator.last_successful_refresh_generation = 1
    entity._handle_coordinator_update()
    assert entity.current_option == "comfort"

    # The controller rejected the mode and stayed where it was.
    entity.coordinator.refresh_generation = 2
    entity.coordinator.last_successful_refresh_generation = 2
    entity._handle_coordinator_update()

    assert entity.current_option == "off"


async def test_select_does_not_assume_an_option_it_did_not_write() -> None:
    """A failed write must not change the reported option."""
    entity = _make_select(current=0)

    async def failed_write(component, field, value) -> None:
        raise RuntimeError("write failed")

    entity.coordinator.write_component_value = failed_write

    with pytest.raises(RuntimeError, match="write failed"):
        await entity.async_select_option("comfort")

    assert entity.current_option == "off"


async def test_select_ignores_an_unknown_option() -> None:
    """An option outside the mapping must not write anything."""
    entity = _make_select(current=0)

    await entity.async_select_option("does not exist")

    assert entity.coordinator.writes == []
    assert entity.current_option == "off"
