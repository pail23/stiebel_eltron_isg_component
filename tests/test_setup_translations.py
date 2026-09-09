"""Setup errors keep their causes and provide HA translation metadata."""

import json
from pathlib import Path
from string import Formatter
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import (
    ConfigEntryError,
    ConfigEntryNotReady,
    HomeAssistantError,
)
from homeassistant.helpers.translation import async_get_translations
from modbus_connection import ModbusError
from pystiebeleltron import StiebelEltronModbusError, UnknownControllerModelError
import pytest

from custom_components import stiebel_eltron_isg as integration
from custom_components.stiebel_eltron_isg.const import DOMAIN


@pytest.mark.parametrize(
    "case",
    [
        (
            "async_get_unit",
            HomeAssistantError("link conflict"),
            "modbus_setup_failed",
            {"error": "link conflict"},
            ConfigEntryState.SETUP_ERROR,
        ),
        (
            "get_controller_model",
            StiebelEltronModbusError(),
            "controller_read_failed",
            {"error": "Data error on the modbus"},
            ConfigEntryState.SETUP_RETRY,
        ),
        (
            "get_controller_model",
            UnknownControllerModelError(165),
            "unsupported_controller",
            {"model_id": "165"},
            ConfigEntryState.SETUP_ERROR,
        ),
        (
            "update",
            ModbusError("read timeout"),
            "initial_read_failed",
            {"error": "read timeout"},
            ConfigEntryState.SETUP_RETRY,
        ),
    ],
)
async def test_setup_error_metadata_and_cause(
    hass, mock_config_entry, mock_wpm_api, case
):
    target, failure, key, placeholders, state = case
    mock_config_entry.add_to_hass(hass)
    setup = integration.async_setup_entry
    caught = []

    async def capture(*args):
        try:
            return await setup(*args)
        except (ConfigEntryError, ConfigEntryNotReady) as err:
            caught.append(err)
            raise

    if target == "update":
        mock_wpm_api.async_update.side_effect = failure
        target = "get_controller_model"
        replacement = integration.get_controller_model
    else:
        replacement = (
            AsyncMock(side_effect=failure) if target == "get_controller_model" else None
        )

    with patch.object(integration, "async_setup_entry", side_effect=capture):
        if replacement is not None:
            with patch.object(integration, target, new=replacement):
                assert not await hass.config_entries.async_setup(
                    mock_config_entry.entry_id
                )
        else:
            with patch.object(integration, target, side_effect=failure):
                assert not await hass.config_entries.async_setup(
                    mock_config_entry.entry_id
                )

    assert mock_config_entry.state is state
    assert mock_config_entry.error_reason_translation_key == key
    assert mock_config_entry.error_reason_translation_placeholders == placeholders
    assert caught[0].translation_domain == DOMAIN
    cause = caught[0].__cause__
    while cause is not failure and cause is not None:
        cause = cause.__cause__
    assert cause is failure


@pytest.mark.parametrize("language", ["en", "de"])
async def test_setup_messages_resolve_through_home_assistant(hass, language):
    translations = await async_get_translations(hass, language, "exceptions", {DOMAIN})
    for key, values in {
        "modbus_setup_failed": {"error": "link conflict"},
        "controller_read_failed": {"error": "timeout"},
        "unsupported_controller": {"model_id": "165"},
        "initial_read_failed": {"error": "read timeout"},
    }.items():
        message = translations[f"component.{DOMAIN}.exceptions.{key}.message"]
        rendered = message.format(**values)
        assert all(value in rendered for value in values.values())
        assert "{" not in rendered
    assert ("Reglermodell" if language == "de" else "controller model") in translations[
        f"component.{DOMAIN}.exceptions.unsupported_controller.message"
    ]


def test_all_setup_translation_resources_have_matching_placeholders():
    root = Path(integration.__file__).parent
    for path in [root / "strings.json", *(root / "translations").glob("*.json")]:
        messages = json.loads(path.read_text())["exceptions"]
        for key in (
            "modbus_setup_failed",
            "controller_read_failed",
            "unsupported_controller",
            "initial_read_failed",
        ):
            fields = {
                field
                for _, field, _, _ in Formatter().parse(messages[key]["message"])
                if field
            }
            assert fields == (
                {"model_id"} if key == "unsupported_controller" else {"error"}
            ), path
