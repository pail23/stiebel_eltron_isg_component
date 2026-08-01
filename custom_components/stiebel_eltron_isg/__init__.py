"""Custom integration to integrate stiebel_eltron_isg with Home Assistant.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.typing import ConfigType
from modbus_connection import ModbusError
from modbus_connection.pymodbus import connect_tcp
from pystiebeleltron import (
    ControllerModel,
    StiebelEltronModbusError,
    UnknownControllerModelError,
    get_controller_model,
)

from .const import DEFAULT_PORT, DOMAIN, UNIT_ID
from .coordinator import StiebelEltronConfigEntry, StiebelEltronDataCoordinator
from .lwz_coordinator import StiebelEltronModbusLWZDataCoordinator
from .migration import (
    async_migrate_device_identifier,
    async_migrate_unique_ids,
    async_remove_legacy_circulation_pump_switch,
)
from .wpm3i_coordinator import StiebelEltronModbusWPM3iDataCoordinator
from .wpm_coordinator import StiebelEltronModbusWPMDataCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)

_PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.CLIMATE,
]

_ISSUE_TRACKER = "https://github.com/pail23/stiebel_eltron_isg_component/issues"


def _unsupported_controller_issue_id(entry: StiebelEltronConfigEntry) -> str:
    """Return the stable repair issue id for a config entry."""
    return f"unsupported_controller_{entry.entry_id}"


def _create_unsupported_controller_issue(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    model_id: object,
) -> None:
    """Tell the user how to handle a controller without integration support."""
    ir.async_create_issue(
        hass,
        DOMAIN,
        _unsupported_controller_issue_id(entry),
        is_fixable=False,
        learn_more_url=_ISSUE_TRACKER,
        severity=ir.IssueSeverity.ERROR,
        translation_key="unsupported_controller",
        translation_placeholders={"model_id": str(model_id)},
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
) -> bool:
    """Set up this integration using UI."""

    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    try:
        connection = await connect_tcp(host, port=port)
    except ModbusError as exception:
        raise ConfigEntryNotReady("Could not connect to device") from exception
    entry.async_on_unload(connection.close)
    try:
        model = await get_controller_model(connection.for_unit(UNIT_ID))
    except StiebelEltronModbusError as exception:
        raise ConfigEntryNotReady("Could not read controller model") from exception
    except UnknownControllerModelError as exception:
        # An unrecognised controller id is a permanent condition, not a
        # transient modbus glitch: fail cleanly instead of retrying forever.
        # Adding support requires a pystiebeleltron update, which reloads the
        # entry anyway.
        _create_unsupported_controller_issue(hass, entry, exception.model_id)
        raise ConfigEntryError(
            f"Unsupported controller model: {exception}"
        ) from exception

    coordinator: StiebelEltronDataCoordinator

    if model == ControllerModel.WPM_3i:
        coordinator = StiebelEltronModbusWPM3iDataCoordinator(
            hass, entry, model, connection, host
        )
    elif model in (
        ControllerModel.WPMsystem,
        ControllerModel.WPM_3,
        ControllerModel.LWZ_R290,
    ):
        coordinator = StiebelEltronModbusWPMDataCoordinator(
            hass, entry, model, connection, host
        )
    elif model in (
        ControllerModel.LWZ,
        ControllerModel.LWZ_x04_SOL,
    ):
        coordinator = StiebelEltronModbusLWZDataCoordinator(
            hass,
            entry,
            model,
            connection,
            host,
        )
    else:
        _create_unsupported_controller_issue(
            hass, entry, getattr(model, "value", model)
        )
        raise ConfigEntryError(f"Unsupported controller model: {model}")

    # A library and integration update can add the model while this repair still
    # exists from an earlier setup attempt.
    ir.async_delete_issue(hass, DOMAIN, _unsupported_controller_issue_id(entry))

    # Both have to run before the platforms are set up, so that the entities are
    # added to the registry entries and the device that already carry their new
    # identifiers.
    async_migrate_device_identifier(hass, entry)
    await async_migrate_unique_ids(hass, entry, model)
    async_remove_legacy_circulation_pump_switch(hass, entry, model)

    entry.runtime_data = coordinator

    await coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(
        connection.on_connection_lost(
            lambda: hass.config_entries.async_schedule_reload(entry.entry_id)
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def async_remove_entry(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
) -> None:
    """Remove repairs that belong to a deleted config entry."""
    ir.async_delete_issue(hass, DOMAIN, _unsupported_controller_issue_id(entry))
