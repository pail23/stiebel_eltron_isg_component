"""Tests for integration diagnostics."""

import importlib.metadata
import json
from types import SimpleNamespace

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.json import ExtendedJSONEncoder
from modbus_connection.mock import MockModbusConnection
from pystiebeleltron import ControllerModel
from pystiebeleltron.lwz import LwzStiebelEltronAPI
from pystiebeleltron.wpm import WpmStiebelEltronAPI
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronDataCoordinator,
)
from custom_components.stiebel_eltron_isg.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)


def test_raw_data_privacy_audit_matches_dependency_version() -> None:
    """A library update must trigger a new sensitive-field audit."""
    assert importlib.metadata.version("pystiebeleltron") == "0.7.1"


async def test_diagnostics_redact_host_and_preserve_useful_data(
    hass: HomeAssistant,
) -> None:
    """Both diagnostics entry points protect the host without losing context."""
    private_host = "private-isg.example.internal"
    mock_config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: private_host,
            CONF_PORT: 1502,
            "name": "Ground floor heat pump",
        },
        options={"scan_interval": 60},
    )
    mock_config_entry.runtime_data = SimpleNamespace(
        model=ControllerModel.WPM_3,
        get_raw_data=lambda: {
            "outside_temperature": 12.5,
            "produced_heating_total": 12345,
            "unsupported_value": None,
        },
    )

    config_diagnostics = await async_get_config_entry_diagnostics(
        hass, mock_config_entry
    )
    device_diagnostics = await async_get_device_diagnostics(
        hass,
        mock_config_entry,
        SimpleNamespace(),
    )

    assert config_diagnostics == device_diagnostics
    assert config_diagnostics["config_entry"] == {
        CONF_HOST: REDACTED,
        CONF_PORT: 1502,
        "name": "Ground floor heat pump",
    }
    assert config_diagnostics["options"] == {"scan_interval": 60}
    assert config_diagnostics["data"] == [
        {
            "outside_temperature": 12.5,
            "produced_heating_total": 12345,
        },
        {"model": "WPM_3", "model_id": 390},
    ]

    for diagnostics in (config_diagnostics, device_diagnostics):
        downloaded_json = json.dumps(diagnostics, cls=ExtendedJSONEncoder)
        assert private_host not in downloaded_json
        downloaded_diagnostics = json.loads(downloaded_json)
        assert downloaded_diagnostics["config_entry"][CONF_HOST] == REDACTED
        assert downloaded_diagnostics["config_entry"][CONF_PORT] == 1502
        assert downloaded_diagnostics["data"][1] == {
            "model": "WPM_3",
            "model_id": 390,
        }


@pytest.mark.parametrize(
    ("api_class", "model", "address"),
    [
        (WpmStiebelEltronAPI, ControllerModel.WPMsystem, 506),
        (Wpm3iStiebelEltronAPI, ControllerModel.WPM_3i, 506),
        (LwzStiebelEltronAPI, ControllerModel.LWZ, 6),
    ],
)
async def test_diagnostics_with_real_library_components(
    hass, api_class, model, address
):
    """Export actual register values without treating API helpers as components."""
    unit = MockModbusConnection().for_unit(1)
    unit.load_raw({"input": {address: 125}})
    api = api_class(unit)
    await api.system_values.async_update()
    coordinator = StiebelEltronDataCoordinator.__new__(StiebelEltronDataCoordinator)
    coordinator._api = api
    coordinator._model = model
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "private.example", CONF_PORT: 502}
    )
    entry.runtime_data = coordinator

    result = await async_get_config_entry_diagnostics(hass, entry)
    device_result = await async_get_device_diagnostics(hass, entry, SimpleNamespace())
    assert result == device_result
    assert result["data"][0]["outside_temperature"] == "12.5 °C"
    assert "sg_ready_operating_state" in result["data"][0]
    assert "operating_mode" in result["data"][0]
    assert result["data"][1] == {"model": model.name, "model_id": model.value}
    assert result["config_entry"][CONF_HOST] == REDACTED
    assert "private.example" not in json.dumps(result, cls=ExtendedJSONEncoder)
