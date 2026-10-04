"""LWZ fan services against the released library and mock Modbus."""

from unittest.mock import patch

from homeassistant.helpers import entity_registry as er
from pystiebeleltron import ControllerModel
from pystiebeleltron.lwz import LwzStiebelEltronAPI
import pytest

from custom_components.stiebel_eltron_isg.const import DOMAIN, UNIT_ID
from custom_components.stiebel_eltron_isg.entity import build_unique_id


@pytest.fixture
def lwz_fan_setup(
    hass, mock_config_entry, mock_get_controller_model, mock_modbus_connection
):
    async def setup(model, mode, stage=2):
        mock_get_controller_model.return_value = model
        unit = mock_modbus_connection.for_unit(UNIT_ID)
        unit.load_raw({
            "holding": {
                1000: mode,
                1001: 210,
                1002: 180,
                1017: stage if mode == 3 else 1,
                1018: stage if mode == 4 else 0,
                1019: 1,
                1020: stage if mode == 14 else 0,
            }
        })
        writes = []
        unit.on_write(writes.append)
        mock_config_entry.add_to_hass(hass)
        with patch(
            "custom_components.stiebel_eltron_isg.lwz_coordinator.LwzStiebelEltronAPI",
            LwzStiebelEltronAPI,
        ):
            assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()
        entity_id = er.async_get(hass).async_get_entity_id(
            "climate", DOMAIN, build_unique_id(mock_config_entry, "climate_hk_1")
        )
        assert entity_id is not None
        return unit, writes, entity_id

    return setup


@pytest.mark.parametrize("model", [ControllerModel.LWZ, ControllerModel.LWZ_x04_SOL])
@pytest.mark.parametrize(
    "mode_and_address",
    [(3, 1017), (4, 1018), (14, 1020)],
    ids=["comfort", "eco", "manual"],
)
async def test_fan_service_uses_active_stage_only(
    hass, mock_config_entry, lwz_fan_setup, model, mode_and_address
):
    mode, address = mode_and_address
    unit, writes, entity_id = await lwz_fan_setup(model, mode)
    original = {a: unit.holding[a] for a in (1017, 1018, 1019, 1020)}
    assert hass.states.get(entity_id).attributes["fan_mode"] == "medium"

    async def set_fan(value):
        await hass.services.async_call(
            "climate",
            "set_fan_mode",
            {"entity_id": entity_id, "fan_mode": value},
            blocking=True,
        )

    await set_fan("medium")
    assert writes == []
    await set_fan("high")
    assert [(w.register_type, w.address, w.values) for w in writes] == [
        ("holding", address, [3])
    ]
    assert all(unit.holding[a] == v for a, v in original.items() if a != address)
    await mock_config_entry.runtime_data.async_refresh()
    assert hass.states.get(entity_id).attributes["fan_mode"] == "high"
    await set_fan("high")
    assert len(writes) == 1


async def test_manual_stage_unavailable_and_mode_change(
    hass, mock_config_entry, lwz_fan_setup
):
    unit, writes, entity_id = await lwz_fan_setup(ControllerModel.LWZ, 14, 0x8000)
    assert hass.states.get(entity_id).attributes.get("fan_mode") is None
    await hass.services.async_call(
        "climate",
        "set_fan_mode",
        {"entity_id": entity_id, "fan_mode": "medium"},
        blocking=True,
    )
    assert [(w.address, w.values) for w in writes] == [(1020, [2])]
    coordinator = mock_config_entry.runtime_data
    await coordinator.async_refresh()
    assert hass.states.get(entity_id).attributes["fan_mode"] == "medium"
    unit.holding[1000] = 3
    await coordinator.async_refresh()
    assert hass.states.get(entity_id).attributes["fan_mode"] == "low"
    assert unit.holding[1020] == 2
