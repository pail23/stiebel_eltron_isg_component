"""Diagnostics support for Stiebel Eltron ISG."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics.util import async_redact_data
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from pystiebeleltron import IsgRegisters

from custom_components.stiebel_eltron_isg.data import (
    StiebelEltronIsgIntegrationConfigEntry,
)

CONFIG_FIELDS_TO_REDACT: list[str] = []
DATA_FIELDS_TO_REDACT: list[str] = []


def _get_register_key(register: IsgRegisters) -> str:
    """Extract string key from a register object.

    Handles both enum-like registers with a .value attribute
    and plain values.
    """
    return str(register.value) if hasattr(register, "value") else str(register)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: StiebelEltronIsgIntegrationConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator

    data = {
        _get_register_key(k): v
        for k, v in coordinator.raw_data.items()
        if v is not None
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
        _get_register_key(k): v
        for k, v in coordinator.raw_data.items()
        if v is not None
    }

    return {
        "config_entry": async_redact_data(config_entry.data, CONFIG_FIELDS_TO_REDACT),
        "options": async_redact_data(config_entry.options, []),
        "data": [
            async_redact_data(data, DATA_FIELDS_TO_REDACT),
            {"model": coordinator.model},
        ],
    }
