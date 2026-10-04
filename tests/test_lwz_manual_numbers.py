"""LWZ manual setpoint service tests against the released library and mock Modbus."""

from unittest.mock import patch

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from pystiebeleltron import ControllerModel
from pystiebeleltron.lwz import LwzStiebelEltronAPI
import pytest

from custom_components.stiebel_eltron_isg.const import DOMAIN, UNIT_ID
from custom_components.stiebel_eltron_isg.entity import build_unique_id

MANUAL_TARGETS = [
    ("manual_hc_set_hk1", 1003),
    ("manual_hc_set_hk2", 1006),
    ("manual_water_temperature_target", 1013),
]
ORIGINAL_HOLDING = {1000: 14, 1003: 410, 1006: 420, 1011: 500, 1012: 450, 1013: 430}


@pytest.fixture
def lwz_number_setup(
    hass,
    mock_config_entry,
    mock_get_controller_model,
    mock_modbus_connection,
):
    async def setup(key, original=None):
        mock_get_controller_model.return_value = ControllerModel.LWZ
        unit = mock_modbus_connection.for_unit(UNIT_ID)
        unit.load_raw({"holding": original or ORIGINAL_HOLDING})
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
            "number", DOMAIN, build_unique_id(mock_config_entry, key)
        )
        assert entity_id is not None
        return unit, writes, entity_id

    return setup


async def _set_number(hass, entity_id, value):
    await hass.services.async_call(
        "number", "set_value", {"entity_id": entity_id, "value": value}, blocking=True
    )


@pytest.mark.parametrize(("key", "address"), MANUAL_TARGETS)
async def test_manual_target_accepts_half_step_and_rejects_tenth_step(
    hass,
    lwz_number_setup,
    mock_config_entry,
    key,
    address,
):
    unit, writes, entity_id = await lwz_number_setup(key)
    assert float(hass.states.get(entity_id).state) == ORIGINAL_HOLDING[address] / 10

    await _set_number(hass, entity_id, 45.5)
    assert [(e.register_type, e.address, e.values) for e in writes] == [
        ("holding", address, [455])
    ]
    assert all(
        unit.holding[a] == v for a, v in ORIGINAL_HOLDING.items() if a != address
    )
    assert float(hass.states.get(entity_id).state) == 45.5

    await _set_number(hass, entity_id, 45.5)
    assert len(writes) == 1
    with pytest.raises(ServiceValidationError):
        await _set_number(hass, entity_id, 45.3)
    assert len(writes) == 1
    assert float(hass.states.get(entity_id).state) == 45.5

    coordinator = mock_config_entry.runtime_data
    unit.holding[address] = 0x8000
    await coordinator.async_refresh()
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE
    unit.holding[address] = ORIGINAL_HOLDING[address]
    await coordinator.async_refresh()
    assert float(hass.states.get(entity_id).state) == ORIGINAL_HOLDING[address] / 10


async def test_invalid_current_value_does_not_bypass_step_validation(
    hass,
    lwz_number_setup,
):
    original = {**ORIGINAL_HOLDING, 1003: 453}
    _, writes, entity_id = await lwz_number_setup("manual_hc_set_hk1", original)
    assert float(hass.states.get(entity_id).state) == 45.3
    with pytest.raises(ServiceValidationError):
        await _set_number(hass, entity_id, 45.3)
    assert writes == []
    assert float(hass.states.get(entity_id).state) == 45.3


@pytest.mark.parametrize(
    "value", [float("nan"), float("inf"), float("-inf"), 9.5, 65.5]
)
async def test_manual_target_rejects_nonfinite_and_out_of_range_values(
    hass,
    lwz_number_setup,
    value,
):
    _, writes, entity_id = await lwz_number_setup("manual_hc_set_hk1")
    with pytest.raises(ServiceValidationError):
        await _set_number(hass, entity_id, value)
    assert writes == []
    assert float(hass.states.get(entity_id).state) == 41.0


async def test_manual_target_accepts_both_range_boundaries(
    hass,
    lwz_number_setup,
):
    _, writes, entity_id = await lwz_number_setup("manual_hc_set_hk1")
    await _set_number(hass, entity_id, 10.0)
    await _set_number(hass, entity_id, 65.0)
    assert [(e.address, e.values) for e in writes] == [(1003, [100]), (1003, [650])]
    assert float(hass.states.get(entity_id).state) == 65.0


async def test_manual_target_accepts_float_noise_at_a_valid_step(
    hass,
    lwz_number_setup,
):
    _, writes, entity_id = await lwz_number_setup("manual_hc_set_hk1")
    await _set_number(hass, entity_id, 45.5 + 1e-12)
    assert [(e.address, e.values) for e in writes] == [(1003, [455])]
    assert float(hass.states.get(entity_id).state) == 45.5


async def test_existing_lwz_comfort_target_still_accepts_tenth_degree(
    hass,
    lwz_number_setup,
):
    _, writes, entity_id = await lwz_number_setup("comfort_water_temperature_target")
    await _set_number(hass, entity_id, 20.3)
    assert [(e.register_type, e.address, e.values) for e in writes] == [
        ("holding", 1011, [203])
    ]
    assert float(hass.states.get(entity_id).state) == 20.3
