"""Tests for integration diagnostics."""

import importlib.metadata
import json
from types import SimpleNamespace

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.json import ExtendedJSONEncoder
from pystiebeleltron import ControllerModel
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
)


def test_raw_data_privacy_audit_matches_dependency_version() -> None:
    """A library update must trigger a new sensitive-field audit."""
    assert importlib.metadata.version("pystiebeleltron") == "0.7.0"


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
