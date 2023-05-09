"""Diagnostics support for Stiebel Eltron ISG."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics.util import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry


from .const import DOMAIN

CONFIG_FIELDS_TO_REDACT = []
DATA_FIELDS_TO_REDACT = []

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    diagnostics_data = {
        "config_entry": async_redact_data(config_entry.data, CONFIG_FIELDS_TO_REDACT),
        "options": async_redact_data(config_entry.options, []),
        "data": [
            async_redact_data(coordinator.data, DATA_FIELDS_TO_REDACT), {"model": coordinator.model}
        ],
    }

    return diagnostics_data


async def async_get_device_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]


    return {
        "config_entry": async_redact_data(
            config_entry.data, CONFIG_FIELDS_TO_REDACT
        ),
        "options": async_redact_data(config_entry.options, []),
        "data": [async_redact_data(coordinator.data, DATA_FIELDS_TO_REDACT), {"model": coordinator.model}],
    }
