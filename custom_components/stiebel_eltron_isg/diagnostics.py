"""Diagnostics support for Stiebel Eltron ISG."""

from __future__ import annotations

from typing import Any, Final

from homeassistant.components.diagnostics.util import async_redact_data
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .coordinator import StiebelEltronConfigEntry

CONFIG_FIELDS_TO_REDACT: Final[set[str]] = {CONF_HOST}
# async_redact_data also converts ConfigEntry.options from MappingProxyType to
# a plain JSON-safe dict, even while there are no sensitive option fields.
OPTIONS_FIELDS_TO_REDACT: Final[set[str]] = set()
# Audited against pinned pystiebeleltron 0.6.2: its Modbus fields contain no
# serial, MAC, host or IP identifiers. Re-audit this set on dependency updates;
# other ISG interfaces can expose a MAC-based serial number.
DATA_FIELDS_TO_REDACT: Final[set[str]] = set()


def _diagnostics_for_entry(
    entry: StiebelEltronConfigEntry,
) -> dict[str, Any]:
    """Build diagnostics shared by the config entry and device endpoints."""
    coordinator = entry.runtime_data
    data = {str(k): v for k, v in coordinator.get_raw_data().items() if v is not None}

    return {
        "config_entry": async_redact_data(entry.data, CONFIG_FIELDS_TO_REDACT),
        "options": async_redact_data(entry.options, OPTIONS_FIELDS_TO_REDACT),
        "data": [
            async_redact_data(data, DATA_FIELDS_TO_REDACT),
            {
                "model": coordinator.model.name,
                "model_id": coordinator.model.value,
            },
        ],
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return _diagnostics_for_entry(entry)


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    config_entry: StiebelEltronConfigEntry,
    device: DeviceEntry,
) -> dict[str, Any]:
    """Return entry-scoped diagnostics for its single controller device."""
    return _diagnostics_for_entry(config_entry)
