"""Tests for the climate platform."""

from types import SimpleNamespace

from homeassistant.components.climate.const import FAN_HIGH, FAN_LOW

from custom_components.stiebel_eltron_isg.climate import (
    ECO_MODE,
    StiebelEltronLWZClimateEntity,
    StiebelEltronWPMClimateEntity,
)


def test_climate_unavailable_when_last_update_failed() -> None:
    """A failed coordinator update must mark the climate entity unavailable."""
    entity = StiebelEltronWPMClimateEntity.__new__(StiebelEltronWPMClimateEntity)
    entity.coordinator = SimpleNamespace(last_update_success=False)

    # last_update_success is False, so availability must short-circuit to False
    # without evaluating the (stale) target temperature.
    assert entity.available is False


class _FakeSystemParameters:
    def __init__(self, operating_mode, day_stage, night_stage) -> None:
        self.operating_mode = operating_mode
        self.day_stage = day_stage
        self.night_stage = night_stage


class _FakeApi:
    def __init__(self, system_parameters) -> None:
        self.system_parameters = system_parameters


class _StubCoordinator:
    """Coordinator stub that resolves lambda accessors against a fake API."""

    def __init__(self, api) -> None:
        self._api = api
        self.writes: list[tuple] = []
        # The real DataUpdateCoordinator caches nothing of its own; ``data`` is
        # an empty dict. The old code queried it with a string key and always
        # missed, which is exactly the bug under test.
        self.data: dict = {}

    def get_value(self, accessor):
        return accessor(self._api)

    async def write_component_value(self, component, field, value) -> None:
        self.writes.append((component, field, value))


def _make_lwz_climate(
    operating_mode: int, day_stage: int = 3, night_stage: int = 1
) -> StiebelEltronLWZClimateEntity:
    entity = StiebelEltronLWZClimateEntity.__new__(StiebelEltronLWZClimateEntity)
    api = _FakeApi(_FakeSystemParameters(operating_mode, day_stage, night_stage))
    entity.coordinator = _StubCoordinator(api)
    entity.write_component = "system_parameters"
    return entity


def test_lwz_fan_mode_uses_night_stage_when_eco() -> None:
    """In eco mode the fan mode must reflect the night stage, not the day stage."""
    entity = _make_lwz_climate(operating_mode=ECO_MODE, day_stage=3, night_stage=1)

    assert entity.fan_mode == FAN_LOW


def test_lwz_fan_mode_uses_day_stage_when_not_eco() -> None:
    """Outside eco mode the fan mode must reflect the day stage."""
    entity = _make_lwz_climate(operating_mode=3, day_stage=3, night_stage=1)

    assert entity.fan_mode == FAN_HIGH


async def test_lwz_set_fan_mode_writes_night_stage_when_eco() -> None:
    """Setting the fan mode in eco mode must write the night stage field."""
    entity = _make_lwz_climate(operating_mode=ECO_MODE)

    await entity.async_set_fan_mode(FAN_LOW)

    assert entity.coordinator.writes == [("system_parameters", "night_stage", 1)]


async def test_lwz_set_fan_mode_writes_day_stage_when_not_eco() -> None:
    """Setting the fan mode outside eco mode must write the day stage field."""
    entity = _make_lwz_climate(operating_mode=3)

    await entity.async_set_fan_mode(FAN_HIGH)

    assert entity.coordinator.writes == [("system_parameters", "day_stage", 3)]
