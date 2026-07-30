"""Tests for the climate platform."""

from types import SimpleNamespace

from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.components.climate.const import FAN_HIGH, FAN_LOW
import pytest

from custom_components.stiebel_eltron_isg.climate import (
    ECO_MODE,
    LWZ_CLIMATE_TYPES,
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


def test_lwz_climate_preserves_supported_features() -> None:
    """LWZ fan support must not replace the features inherited from the base."""
    coordinator = SimpleNamespace(device_info={})
    config_entry = SimpleNamespace(entry_id="test")

    entity = StiebelEltronLWZClimateEntity(
        coordinator, config_entry, LWZ_CLIMATE_TYPES[0]
    )

    required_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.FAN_MODE
    )
    assert entity.supported_features & required_features == required_features


class _FakeSystemParameters:
    def __init__(self, operating_mode, day_stage, night_stage) -> None:
        self.operating_mode = operating_mode
        self.day_stage = day_stage
        self.night_stage = night_stage
        self.room_temperature_day_hk1 = 21.0
        self.room_temperature_night_hk1 = 18.0


class _FakeApi:
    def __init__(self, system_parameters) -> None:
        self.system_parameters = system_parameters


class _StubCoordinator:
    """Coordinator stub that resolves lambda accessors against a fake API."""

    def __init__(self, api) -> None:
        self._api = api
        self.writes: list[tuple] = []
        self.refresh_generation = 0
        self.last_successful_refresh_generation = 0
        self.last_update_success = True
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
    entity.eco_target_temp_write_field = "room_temperature_night_hk1"
    entity.comfort_target_temp_write_field = "room_temperature_day_hk1"
    entity.eco_target_temp_register = lambda api: (
        api.system_parameters.room_temperature_night_hk1
    )
    entity.comfort_target_temp_register = lambda api: (
        api.system_parameters.room_temperature_day_hk1
    )
    # Written state is pushed to hass, which does not exist in these unit tests.
    entity.published_states = 0

    def _publish() -> None:
        entity.published_states += 1

    entity.async_write_ha_state = _publish
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


async def test_climate_shows_written_target_before_the_next_poll() -> None:
    """A written target must be reported at once, not only after the next poll."""
    entity = _make_lwz_climate(operating_mode=3)

    await entity.async_set_temperature(temperature=22.5)

    assert entity.coordinator.writes == [
        ("system_parameters", "room_temperature_day_hk1", 22.5)
    ]
    assert entity.target_temperature == 22.5
    assert entity.published_states == 1


async def test_climate_does_not_assume_a_target_when_the_write_fails() -> None:
    """A failed write must leave the device's reported target in place."""
    entity = _make_lwz_climate(operating_mode=3)

    async def failed_write(component, field, value) -> None:
        raise RuntimeError("write failed")

    entity.coordinator.write_component_value = failed_write

    with pytest.raises(RuntimeError, match="write failed"):
        await entity.async_set_temperature(temperature=22.5)

    assert entity.target_temperature == 21.0


async def test_climate_returns_to_the_device_value_once_polled() -> None:
    """A poll made after the write must hand the target back to the device."""
    entity = _make_lwz_climate(operating_mode=3)
    entity.coordinator.refresh_generation = 1
    await entity.async_set_temperature(temperature=22.5)

    # This poll started before the write and may have read the old registers.
    entity.coordinator.last_successful_refresh_generation = 1
    entity._handle_coordinator_update()
    assert entity.target_temperature == 22.5

    entity.coordinator.refresh_generation = 2
    entity.coordinator.last_successful_refresh_generation = 2
    entity._handle_coordinator_update()

    assert entity.target_temperature == 21.0


async def test_climate_keeps_assumption_when_refresh_fails() -> None:
    """A failed refresh has no new device value and must not clear the write."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)
    entity.coordinator.refresh_generation = 1
    entity.coordinator.last_update_success = False

    entity._handle_coordinator_update()

    assert entity.target_temperature == 22.5


async def test_climate_drops_the_assumed_target_when_the_mode_makes_it_stale() -> None:
    """An assumed target only holds for the field it was written to."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)

    # Whoever changed it: in eco mode the target comes from the eco field, and
    # the assumed value belongs to the comfort field.
    entity.coordinator._api.system_parameters.operating_mode = ECO_MODE

    assert entity.target_temperature == 18.0


async def test_climate_keeps_the_assumed_target_when_the_fan_stage_changes() -> None:
    """A fan stage write leaves the target field untouched."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)

    await entity.async_set_fan_mode(FAN_LOW)

    assert entity.target_temperature == 22.5


async def test_climate_keeps_the_assumed_target_between_non_eco_modes() -> None:
    """Both modes read the target from the comfort field, so it still holds."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)

    entity.coordinator._api.system_parameters.operating_mode = 2

    assert entity.target_temperature == 22.5
