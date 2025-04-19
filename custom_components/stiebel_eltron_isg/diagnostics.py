"""Diagnostics support for Stiebel Eltron ISG."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics.util import async_redact_data
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)

CONFIG_FIELDS_TO_REDACT: list = []
DATA_FIELDS_TO_REDACT: list = []


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator

    data = {
        k.value: v for k, v in coordinator._api_client._data.items() if v is not None
    }

    return {
        "config_entry": async_redact_data(entry.data, CONFIG_FIELDS_TO_REDACT),
        "options": async_redact_data(entry.options, []),
        "data": [
            async_redact_data(data, DATA_FIELDS_TO_REDACT),
            {"model": coordinator.model},
        ],
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    config_entry: StiebelEltronIsgIntegrationConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    coordinator = config_entry.runtime_data.coordinator

    data = {
        k.value: v for k, v in coordinator._api_client._data.items() if v is not None
    }

    return {
        "config_entry": async_redact_data(config_entry.data, CONFIG_FIELDS_TO_REDACT),
        "options": async_redact_data(config_entry.options, []),
        "data": [
            async_redact_data(data, DATA_FIELDS_TO_REDACT),
            {"model": coordinator.model},
        ],
    }
