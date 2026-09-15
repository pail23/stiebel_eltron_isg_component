"""WPMsystem cooling-circuit setpoint sensor regressions."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers import entity_registry as er
from pystiebeleltron import ControllerModel
from pystiebeleltron.wpm import (
    WPM_HOLDING_RANGES,
    WPM_INPUT_RANGES,
    WpmStiebelEltronAPI,
)
import pytest

from custom_components.stiebel_eltron_isg import sensor as sensor_module
from custom_components.stiebel_eltron_isg.const import (
    DOMAIN,
    TARGET_TEMPERATURE_COOLING_CIRCUIT_1_HK1,
    UNIT_ID,
)
from custom_components.stiebel_eltron_isg.entity import build_unique_id


@pytest.mark.parametrize(
    "case",
    [(251, "25.1"), (32768, STATE_UNAVAILABLE)],
)
async def test_wpmsystem_cooling_setpoint_reads_register_1603(
    hass,
    mock_config_entry,
    mock_get_controller_model,
    mock_modbus_connection,
    case,
) -> None:
    """The read-only entity uses cooling-circuit register 1603, not area 1515."""
    raw_cooling_setpoint, expected_state = case
    unit = mock_modbus_connection.for_unit(UNIT_ID)
    raw = {
        "input": {
            address: 0
            for start, end in WPM_INPUT_RANGES
            for address in range(start, end + 1)
        },
        "holding": {
            address: 0
            for start, end in WPM_HOLDING_RANGES
            for address in range(start, end + 1)
        },
    }
    raw["holding"][1515] = 299
    raw["holding"][1603] = raw_cooling_setpoint
    unit.load_raw(raw)

    api = WpmStiebelEltronAPI(unit)
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_config_entry.add_to_hass(hass)
    with patch(
        "custom_components.stiebel_eltron_isg.wpm_coordinator.WpmStiebelEltronAPI",
        return_value=api,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor",
        DOMAIN,
        build_unique_id(mock_config_entry, TARGET_TEMPERATURE_COOLING_CIRCUIT_1_HK1),
    )
    assert entity_id is not None
    assert hass.states.get(entity_id).state == expected_state
    assert api.system_parameters.set_room_temperature_area == 29.9


@pytest.mark.parametrize(
    "model",
    [
        ControllerModel.WPM_3,
        ControllerModel.WPM_3i,
        ControllerModel.LWZ_R290,
        ControllerModel.LWZ,
    ],
)
async def test_cooling_setpoint_sensor_is_limited_to_wpmsystem(model) -> None:
    """No other controller family receives the WPMsystem-only register."""
    entry = SimpleNamespace(runtime_data=SimpleNamespace(model=model))
    add_entities = MagicMock()
    with patch.object(
        sensor_module,
        "StiebelEltronISGSensor",
        side_effect=lambda coordinator, config_entry, description: description.key,
    ):
        await sensor_module.async_setup_entry(None, entry, add_entities)

    assert (
        TARGET_TEMPERATURE_COOLING_CIRCUIT_1_HK1 not in add_entities.call_args.args[0]
    )
