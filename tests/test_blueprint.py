"""Run the shipped blueprint through Home Assistant's actual automation engine."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

from homeassistant.components.automation.config import AUTOMATION_BLUEPRINT_SCHEMA
from homeassistant.components.blueprint.models import Blueprint, BlueprintInputs
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.util.yaml import load_yaml
from modbus_connection.mock import MockModbusConnection
from pystiebeleltron import ControllerModel
from pystiebeleltron.lwz import LwzStiebelEltronAPI
from pystiebeleltron.wpm import WpmStiebelEltronAPI
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI
import pytest

from custom_components.stiebel_eltron_isg.const import DOMAIN, ERROR_STATUS
from custom_components.stiebel_eltron_isg.entity import build_unique_id

BLUEPRINT_PATH = (
    Path(__file__).parent.parent / "blueprints/automation/heat_pump_fault.yaml"
)


@pytest.mark.parametrize("custom_action", [False, True])
async def test_fault_blueprint_only_notifies_for_active_fault(hass, custom_action):
    blueprint = Blueprint(
        load_yaml(str(BLUEPRINT_PATH)),
        expected_domain="automation",
        schema=AUTOMATION_BLUEPRINT_SCHEMA,
    )
    inputs = {"fault_sensor": "binary_sensor.heat_pump_fault"}
    calls = []

    async def capture(call):
        calls.append(call.data)

    hass.services.async_register("test", "notify", capture)
    if custom_action:
        inputs["notification_action"] = [
            {"action": "test.notify", "data": {"message": "fault"}}
        ]
    else:
        hass.services.async_register("persistent_notification", "create", capture)
    configured = BlueprintInputs(blueprint, {"use_blueprint": {"input": inputs}})
    configured.validate()
    config = configured.async_substitute()
    config["id"] = "test_fault_blueprint"
    hass.states.async_set("binary_sensor.heat_pump_fault", "off")
    assert await async_setup_component(hass, "automation", {"automation": config})
    await hass.async_block_till_done()
    for state in ("unknown", "unavailable", "off"):
        hass.states.async_set("binary_sensor.heat_pump_fault", state)
        await hass.async_block_till_done()
    assert calls == []
    hass.states.async_set("binary_sensor.heat_pump_fault", "on")
    await hass.async_block_till_done()
    assert len(calls) == 1
    assert "fault" in calls[0]["message"].lower()
    hass.states.async_set(
        "binary_sensor.heat_pump_fault", "on", {"friendly_name": "Updated name"}
    )
    await hass.async_block_till_done()
    assert len(calls) == 1
    hass.states.async_set("binary_sensor.heat_pump_fault", "off")
    await hass.async_block_till_done()
    assert len(calls) == 1


@pytest.mark.parametrize("model", list(ControllerModel))
async def test_blueprint_selector_matches_only_fault_entity(
    hass, mock_config_entry, mock_get_controller_model, model
):
    """Pump and compressor entities must not be offered as fault sensors."""
    mock_get_controller_model.return_value = model
    mock_config_entry.add_to_hass(hass)
    if model in (ControllerModel.LWZ, ControllerModel.LWZ_x04_SOL):
        module, api_class = "lwz_coordinator", LwzStiebelEltronAPI
    elif model == ControllerModel.WPM_3i:
        module, api_class = "wpm3i_coordinator", Wpm3iStiebelEltronAPI
    else:
        module, api_class = "wpm_coordinator", WpmStiebelEltronAPI
    api = api_class(MockModbusConnection().for_unit(1))
    api.async_update = AsyncMock()
    with patch(
        f"custom_components.stiebel_eltron_isg.{module}.{api_class.__name__}",
        return_value=api,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()
    data = load_yaml(str(BLUEPRINT_PATH))
    filters = data["blueprint"]["input"]["fault_sensor"]["selector"]["entity"]["filter"]
    assert filters == [
        {"integration": DOMAIN, "domain": "binary_sensor", "device_class": "problem"}
    ]
    entries = er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )
    selectable = [
        entry
        for entry in entries
        if entry.domain == "binary_sensor"
        and hass.states.get(entry.entity_id).attributes.get("device_class") == "problem"
    ]
    assert [entry.unique_id for entry in selectable] == [
        build_unique_id(mock_config_entry, ERROR_STATUS)
    ]
