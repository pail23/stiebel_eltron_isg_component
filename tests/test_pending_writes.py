"""Tests for the written values the coordinator holds until the device confirms them.

The library does not update its register cache on a write, and a write needs a
moment to reach the heat pump over CAN. Several entities read and write the
same field, so the value just written has to be shared: a follow-up command
from another entity must see it, both to show it and to decide whether a
write would change anything.
"""

import asyncio
from unittest.mock import AsyncMock

from homeassistant.components.climate.const import FAN_HIGH, FAN_LOW, HVACMode
from homeassistant.exceptions import HomeAssistantError
from modbus_connection import ModbusError
import pytest

from custom_components.stiebel_eltron_isg.climate import (
    ECO_MODE,
    StiebelEltronLWZClimateEntity,
    StiebelEltronWPMClimateEntity,
)
from custom_components.stiebel_eltron_isg.number import (
    NUMBER_TYPES_WPM,
    StiebelEltronISGNumberEntity,
)
from custom_components.stiebel_eltron_isg.select import (
    OPERATION_MODE_WPM_OPTIONS,
    StiebelEltronISGSelectEntity,
)
from tests.pending import FakeApi, attach, make_coordinator, poll

COMFORT_MODE = 3
PROGRAM_MODE = 2


def _wpm_setup(operating_mode: int = COMFORT_MODE):
    """Return a coordinator with the fields the WPM HK1 entities share."""
    writes: list[tuple] = []
    api = FakeApi(
        writes,
        system_parameters={
            "operating_mode": operating_mode,
            "comfort_temperature_hk_1": 21.0,
            "eco_temperature_hk_1": 18.0,
        },
    )
    coordinator = make_coordinator(api)
    coordinator.writes = writes
    return coordinator


def _wpm_climate(coordinator) -> StiebelEltronWPMClimateEntity:
    entity = StiebelEltronWPMClimateEntity.__new__(StiebelEltronWPMClimateEntity)
    entity.write_component = "system_parameters"
    entity.eco_target_temp_write_field = "eco_temperature_hk_1"
    entity.comfort_target_temp_write_field = "comfort_temperature_hk_1"
    entity.eco_target_temp_register = lambda api: (
        api.system_parameters.eco_temperature_hk_1
    )
    entity.comfort_target_temp_register = lambda api: (
        api.system_parameters.comfort_temperature_hk_1
    )
    attach(coordinator, entity)
    return entity


def _comfort_number(coordinator) -> StiebelEltronISGNumberEntity:
    entity = StiebelEltronISGNumberEntity.__new__(StiebelEltronISGNumberEntity)
    entity.entity_description = NUMBER_TYPES_WPM[0]
    entity.modbus_register = lambda api: api.system_parameters.comfort_temperature_hk_1
    entity.write_component = "system_parameters"
    entity.write_field = "comfort_temperature_hk_1"
    attach(coordinator, entity)
    return entity


def _mode_select(coordinator) -> StiebelEltronISGSelectEntity:
    entity = StiebelEltronISGSelectEntity.__new__(StiebelEltronISGSelectEntity)
    entity._options = OPERATION_MODE_WPM_OPTIONS
    entity.modbus_register = lambda api: api.system_parameters.operating_mode
    entity.write_component = "system_parameters"
    entity.write_field = "operating_mode"
    attach(coordinator, entity)
    return entity


def _lwz_climate(day_stage: int = 3) -> StiebelEltronLWZClimateEntity:
    writes: list[tuple] = []
    api = FakeApi(
        writes,
        system_parameters={
            "operating_mode": COMFORT_MODE,
            "day_stage": day_stage,
            "night_stage": 1,
            "manual_stage": 2,
            "room_temperature_day_hk1": 21.0,
            "room_temperature_night_hk1": 18.0,
        },
    )
    coordinator = make_coordinator(api)
    coordinator.writes = writes
    entity = StiebelEltronLWZClimateEntity.__new__(StiebelEltronLWZClimateEntity)
    entity.write_component = "system_parameters"
    entity.eco_target_temp_write_field = "room_temperature_night_hk1"
    entity.comfort_target_temp_write_field = "room_temperature_day_hk1"
    entity.eco_target_temp_register = lambda api: (
        api.system_parameters.room_temperature_night_hk1
    )
    entity.comfort_target_temp_register = lambda api: (
        api.system_parameters.room_temperature_day_hk1
    )
    attach(coordinator, entity)
    return entity


# --- coordinator bookkeeping ------------------------------------------------


async def test_a_successful_write_is_held_and_published() -> None:
    """The written value is visible at once and every listener is told."""
    coordinator = _wpm_setup()
    climate = _wpm_climate(coordinator)
    number = _comfort_number(coordinator)

    await coordinator.write_component_value(
        "system_parameters", "comfort_temperature_hk_1", 22.0
    )

    assert (
        coordinator.pending_value("system_parameters", "comfort_temperature_hk_1")
        == 22.0
    )
    assert climate.published_states == 1
    assert number.published_states == 1


async def test_a_failed_write_is_not_held() -> None:
    """A rejected write leaves the device's value in place."""
    coordinator = _wpm_setup()
    coordinator._api.system_parameters.write = AsyncMock(side_effect=ModbusError("x"))

    with pytest.raises(HomeAssistantError):
        await coordinator.write_component_value(
            "system_parameters", "comfort_temperature_hk_1", 22.0
        )

    assert (
        coordinator.pending_value("system_parameters", "comfort_temperature_hk_1")
        is None
    )


async def test_only_a_poll_started_after_the_write_releases_it() -> None:
    """A poll in flight during the write may have read the old registers."""
    coordinator = _wpm_setup()

    async def write_while_polling() -> None:
        await coordinator.write_component_value(
            "system_parameters", "comfort_temperature_hk_1", 22.0
        )

    await poll(coordinator, during=write_while_polling)
    assert (
        coordinator.pending_value("system_parameters", "comfort_temperature_hk_1")
        == 22.0
    )

    await poll(coordinator, success=False)
    assert (
        coordinator.pending_value("system_parameters", "comfort_temperature_hk_1")
        == 22.0
    )

    await poll(coordinator)
    assert (
        coordinator.pending_value("system_parameters", "comfort_temperature_hk_1")
        is None
    )


def test_pending_value_without_a_write_target() -> None:
    """Read-only descriptions have no field to look up."""
    coordinator = _wpm_setup()

    assert coordinator.pending_value(None, "comfort_temperature_hk_1") is None
    assert coordinator.pending_value("system_parameters", None) is None


# --- command sequences across entities ---------------------------------------


async def test_a_setpoint_after_a_mode_change_goes_to_the_new_mode() -> None:
    """Set eco, then 19 degrees: the eco field is written, not the comfort one."""
    climate = _wpm_climate(_wpm_setup())

    await climate.async_set_preset_mode("eco")
    assert climate.preset_mode == "eco"
    assert climate.target_temperature == 18.0

    await climate.async_set_temperature(temperature=19.0)

    assert climate.coordinator.writes == [
        ("system_parameters", "operating_mode", ECO_MODE),
        ("system_parameters", "eco_temperature_hk_1", 19.0),
    ]
    assert climate.target_temperature == 19.0


async def test_a_mode_can_be_changed_back_before_the_next_poll() -> None:
    """Switching back to the mode the device still reports must still write."""
    climate = _wpm_climate(_wpm_setup())

    await climate.async_set_preset_mode("eco")
    await climate.async_set_preset_mode("comfort")
    await climate.async_set_hvac_mode(HVACMode.OFF)
    await climate.async_set_hvac_mode(HVACMode.AUTO)

    assert [value for _, field, value in climate.coordinator.writes] == [
        ECO_MODE,
        COMFORT_MODE,
        5,
        PROGRAM_MODE,
    ]


async def test_the_number_and_the_climate_entity_share_a_setpoint() -> None:
    """A correction through the other entity must not be dropped as unchanged."""
    coordinator = _wpm_setup()
    climate = _wpm_climate(coordinator)
    number = _comfort_number(coordinator)

    await number.async_set_native_value(22.0)
    assert climate.target_temperature == 22.0

    await climate.async_set_temperature(temperature=21.0)

    assert coordinator.writes == [
        ("system_parameters", "comfort_temperature_hk_1", 22.0),
        ("system_parameters", "comfort_temperature_hk_1", 21.0),
    ]
    assert number.native_value == 21.0


async def test_the_select_and_the_climate_entity_share_the_mode() -> None:
    """A mode set through the select is the mode the climate entity acts on."""
    coordinator = _wpm_setup()
    climate = _wpm_climate(coordinator)
    select = _mode_select(coordinator)

    await select.async_select_option("eco")
    assert climate.preset_mode == "eco"

    await climate.async_set_preset_mode("comfort")

    assert coordinator.writes == [
        ("system_parameters", "operating_mode", ECO_MODE),
        ("system_parameters", "operating_mode", COMFORT_MODE),
    ]
    assert select.current_option == "comfort"


async def test_a_fan_stage_can_be_changed_back_before_the_next_poll() -> None:
    """High, low, high: the second change must not be dropped as unchanged."""
    climate = _lwz_climate(day_stage=3)

    await climate.async_set_fan_mode(FAN_LOW)
    assert climate.fan_mode == FAN_LOW

    await climate.async_set_fan_mode(FAN_HIGH)

    assert climate.coordinator.writes == [
        ("system_parameters", "day_stage", 1),
        ("system_parameters", "day_stage", 3),
    ]


async def test_the_device_answer_replaces_the_written_mode() -> None:
    """The controller refused the mode; the next poll shows what it kept."""
    coordinator = _wpm_setup()
    climate = _wpm_climate(coordinator)
    select = _mode_select(coordinator)

    await select.async_select_option("eco")
    await poll(coordinator)

    assert climate.preset_mode == "comfort"
    assert select.current_option == "comfort"


async def test_overlapping_writes_to_one_field_see_each_other() -> None:
    """A command arriving while another entity's write is in flight is not dropped.

    Home Assistant serialises service calls within a platform only, so the
    number and the climate entity can write the same field at the same time.
    """
    coordinator = _wpm_setup()
    climate = _wpm_climate(coordinator)
    number = _comfort_number(coordinator)
    device = coordinator._api.system_parameters
    device_write = device.write
    release = asyncio.Event()

    async def slow_write(field: str, value: float) -> None:
        await release.wait()
        await device_write(field, value)

    device.write = slow_write

    first = asyncio.create_task(number.async_set_native_value(22.0))
    await asyncio.sleep(0)
    second = asyncio.create_task(climate.async_set_temperature(temperature=21.0))
    await asyncio.sleep(0)
    release.set()
    await asyncio.gather(first, second)

    assert coordinator.writes == [
        ("system_parameters", "comfort_temperature_hk_1", 22.0),
        ("system_parameters", "comfort_temperature_hk_1", 21.0),
    ]
