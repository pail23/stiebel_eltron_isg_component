"""Tests for the STIEBEL ELTRON integration."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.components.modbus import async_get_temporary_unit, async_get_unit
from homeassistant.config_entries import ConfigEntry, ConfigEntryState, ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, issue_registry as ir
from modbus_connection import ModbusError, ModbusTcpParams
from modbus_connection.mock import MockModbusConnection
from modbus_connection.tmodbus import ModbusConnection as TmodbusConnection
from pystiebeleltron import (
    ControllerModel,
    StiebelEltronModbusError,
    UnknownControllerModelError,
)
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    mock_config_flow,
    mock_integration,
    mock_platform,
)

from custom_components.stiebel_eltron_isg.const import (
    COMPRESSOR_HEATING,
    CURRENT_POWER_CONSUMPTION,
    DOMAIN,
    UNIT_ID,
)
from custom_components.stiebel_eltron_isg.entity import build_unique_id
from custom_components.stiebel_eltron_isg.migration import duplicate_entity_issue_id
from custom_components.stiebel_eltron_isg.sensor import WPM_SENSOR_TYPES
from custom_components.stiebel_eltron_isg.wpm3i_coordinator import (
    StiebelEltronModbusWPM3iDataCoordinator,
)


async def test_async_setup_entry_success(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test successful setup of the integration."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert result is True
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert "modbus" in hass.config.components


async def test_async_setup_entry_selects_wpm_3i_coordinator(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
) -> None:
    """WPM 3i controllers must use their model-specific API coordinator."""
    mock_get_controller_model.return_value = ControllerModel.WPM_3i
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert isinstance(
        mock_config_entry.runtime_data,
        StiebelEltronModbusWPM3iDataCoordinator,
    )


async def test_setup_registers_every_wpm_sensor(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Every WPM sensor description has to end up with a state.

    An accessor that raises AttributeError, which is what an API mock missing
    one of the optional components does, still reaches the entity registry but
    fails while being added, so it never gets a state. Nothing else in the
    suite notices that, which is why the power-consumption windows silently
    vanished when they moved to the optional extended_energy_data component.
    This guards the fixture as much as the code.
    """
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_ids = {
        entry.unique_id: entry.entity_id
        for entry in er.async_entries_for_config_entry(
            er.async_get(hass), mock_config_entry.entry_id
        )
    }
    stateless = []
    for description in WPM_SENSOR_TYPES:
        entity_id = entity_ids.get(build_unique_id(mock_config_entry, description.key))
        if entity_id is None or hass.states.get(entity_id) is None:
            stateless.append(description.key)

    assert not stateless, f"These sensors never got a state: {sorted(stateless)}"


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (ControllerModel.WPMsystem, True),
        (ControllerModel.WPM_3, False),
        (ControllerModel.LWZ_R290, False),
    ],
)
async def test_inverter_power_is_created_for_wpmsystem_only(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
    model: ControllerModel,
    expected: bool,
) -> None:
    """Wire 3679 is only confirmed answered on WPMsystem.

    WPM_3, WPMsystem and LWZ_R290 share one sensor list, so without a model
    check the other two would be handed an entity that can never hold a value.
    All three are covered here so that a change to ``async_setup_entry`` cannot
    quietly widen the set again.
    """
    mock_get_controller_model.return_value = model
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    unique_ids = {
        entry.unique_id
        for entry in er.async_entries_for_config_entry(
            er.async_get(hass), mock_config_entry.entry_id
        )
    }
    created = (
        build_unique_id(mock_config_entry, CURRENT_POWER_CONSUMPTION) in unique_ids
    )
    assert created is expected


async def test_async_setup_entry_with_custom_port(
    hass: HomeAssistant,
    mock_modbus_connection_class: MagicMock,
) -> None:
    """Test setup with custom port."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "192.168.1.100", CONF_PORT: 5020},
    )
    config_entry.add_to_hass(hass)

    result = await hass.config_entries.async_setup(config_entry.entry_id)

    assert result is True
    mock_modbus_connection_class.assert_called_once_with(
        ModbusTcpParams(host="192.168.1.100", port=5020)
    )


async def test_async_setup_entry_without_port(
    hass: HomeAssistant,
    mock_modbus_connection_class: MagicMock,
) -> None:
    """Test setup without port (should use default)."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "192.168.1.100"},
    )
    config_entry.add_to_hass(hass)

    result = await hass.config_entries.async_setup(config_entry.entry_id)

    assert result is True
    mock_modbus_connection_class.assert_called_once_with(
        ModbusTcpParams(host="192.168.1.100", port=502)
    )


async def test_async_setup_entry_conflicting_link_settings(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test setup fails permanently for incompatible shared link settings."""
    async with async_get_temporary_unit(
        hass,
        ModbusTcpParams(host="1.1.1.1", port=502, framer="rtu"),
        UNIT_ID,
    ):
        mock_config_entry.add_to_hass(hass)

        result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert result is False
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    assert (
        ir.async_get(hass).async_get_issue(
            DOMAIN, f"unsupported_controller_{mock_config_entry.entry_id}"
        )
        is None
    )


async def test_async_setup_entry_modbus_error(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """Test setup retries when reading the controller model fails."""
    mock_config_entry.add_to_hass(hass)
    mock_get_controller_model.side_effect = StiebelEltronModbusError()

    result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert result is False
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
    assert (
        ir.async_get(hass).async_get_issue(
            DOMAIN, f"unsupported_controller_{mock_config_entry.entry_id}"
        )
        is None
    )
    assert mock_modbus_connection.connected is False


async def test_async_setup_entry_unknown_model(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """Setup fails cleanly (no retry) when the controller model is unknown."""
    assert mock_modbus_connection.connected is True
    mock_config_entry.add_to_hass(hass)
    mock_get_controller_model.side_effect = UnknownControllerModelError(165)

    result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert result is False
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    assert not hasattr(mock_config_entry, "runtime_data")
    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, f"unsupported_controller_{mock_config_entry.entry_id}"
    )
    assert issue is not None
    assert issue.is_fixable is False
    assert issue.severity is ir.IssueSeverity.ERROR
    assert issue.translation_key == "unsupported_controller"
    assert issue.translation_placeholders == {"model_id": "165"}
    assert (
        issue.learn_more_url
        == "https://github.com/pail23/stiebel_eltron_isg_component/issues"
    )
    assert mock_modbus_connection.connected is False


async def test_supported_model_clears_a_previous_controller_repair(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """A library update that recognizes the model resolves the repair."""
    issue_id = f"unsupported_controller_{mock_config_entry.entry_id}"
    ir.async_create_issue(
        hass,
        DOMAIN,
        issue_id,
        is_fixable=False,
        issue_domain=DOMAIN,
        severity=ir.IssueSeverity.ERROR,
        translation_key="unsupported_controller",
        translation_placeholders={"model_id": "165"},
    )
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert ir.async_get(hass).async_get_issue(DOMAIN, issue_id) is None


async def test_async_setup_entry_rejects_unhandled_model(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """A detected model without a coordinator must fail with a repair."""
    assert mock_modbus_connection.connected is True
    mock_get_controller_model.return_value = SimpleNamespace(name="FUTURE", value=166)
    mock_config_entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.stiebel_eltron_isg.async_migrate_device_identifier"
        ) as migrate_device,
        patch(
            "custom_components.stiebel_eltron_isg.async_migrate_unique_ids",
            new_callable=AsyncMock,
        ) as migrate_entities,
        patch(
            "custom_components.stiebel_eltron_isg."
            "async_remove_legacy_circulation_pump_switch"
        ) as remove_legacy,
    ):
        result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert result is False
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    assert not hasattr(mock_config_entry, "runtime_data")
    migrate_device.assert_not_called()
    migrate_entities.assert_not_awaited()
    remove_legacy.assert_not_called()
    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, f"unsupported_controller_{mock_config_entry.entry_id}"
    )
    assert issue is not None
    assert issue.translation_placeholders == {"model_id": "166"}
    assert mock_modbus_connection.connected is False


async def test_removing_entry_clears_its_repairs(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
) -> None:
    """Deleting an entry must not leave either Repair orphaned."""
    controller_issue_id = f"unsupported_controller_{mock_config_entry.entry_id}"
    duplicate_issue_id = duplicate_entity_issue_id(mock_config_entry)
    mock_get_controller_model.side_effect = UnknownControllerModelError(165)
    mock_config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    assert ir.async_get(hass).async_get_issue(DOMAIN, controller_issue_id) is not None
    ir.async_create_issue(
        hass,
        DOMAIN,
        duplicate_issue_id,
        data={
            "entry_id": mock_config_entry.entry_id,
            "model_id": ControllerModel.WPM_3.value,
        },
        is_fixable=True,
        is_persistent=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key="duplicate_entities",
        translation_placeholders={"count": "1", "entities": "sensor.duplicate"},
    )

    await hass.config_entries.async_remove(mock_config_entry.entry_id)

    issue_registry = ir.async_get(hass)
    assert issue_registry.async_get_issue(DOMAIN, controller_issue_id) is None
    assert issue_registry.async_get_issue(DOMAIN, duplicate_issue_id) is None


async def test_async_setup_entry_coordinator_update_fails(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_wpm_api: MagicMock,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """Test setup retries and closes the connection when the first update fails."""
    mock_wpm_api.async_update.side_effect = ModbusError("update failed")
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.async_setup(mock_config_entry.entry_id)

    assert result is False
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
    assert mock_modbus_connection.connected is False


async def test_connection_lost_reconnects_without_entry_reload(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
    mock_wpm_api: MagicMock,
) -> None:
    """Reconnect on the next update without reloading the config entry."""
    unit = mock_modbus_connection.for_unit(UNIT_ID)
    unit.load_raw({"input": {0: 42}})

    async def update_through_shared_unit() -> None:
        assert await unit.read_input_registers(0, 1) == [42]

    mock_wpm_api.async_update.side_effect = update_through_shared_unit
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with patch.object(
        hass.config_entries, "async_schedule_reload"
    ) as mock_schedule_reload:
        mock_modbus_connection.simulate_connection_lost()
        assert mock_modbus_connection.connected is False

        await mock_config_entry.runtime_data.async_refresh()

    mock_schedule_reload.assert_not_called()
    assert mock_config_entry.runtime_data.last_update_success is True
    assert mock_modbus_connection.connected is True
    assert len(unit.read_events) == 2


async def test_tmodbus_unit_reconnects_after_connection_loss() -> None:
    """Keep the backend reconnect contract the integration relies on."""
    connection = TmodbusConnection(ModbusTcpParams(host="1.1.1.1", port=502))
    first_unit_client = MagicMock()
    first_unit_client.read_input_registers = AsyncMock(return_value=[41])
    first_client = MagicMock()
    first_client.for_unit_id.return_value = first_unit_client
    first_client.disconnect = AsyncMock()

    second_unit_client = MagicMock()
    second_unit_client.read_input_registers = AsyncMock(return_value=[42])
    second_client = MagicMock()
    second_client.for_unit_id.return_value = second_unit_client
    second_client.disconnect = AsyncMock()

    with patch.object(
        connection,
        "_connect_client",
        AsyncMock(side_effect=[first_client, second_client]),
    ) as connect_client:
        unit = connection.for_unit(UNIT_ID)
        assert await unit.read_input_registers(0, 1) == [41]

        connection._on_connection_lost(ConnectionError())
        assert connection.connected is False

        assert await unit.read_input_registers(0, 1) == [42]
        assert connect_client.await_count == 2

        await connection.close()

    second_client.disconnect.assert_awaited_once()
    first_client.disconnect.assert_not_awaited()


async def test_unload_entry_closes_connection(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """Test unloading the config entry closes the Modbus connection."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert result is True
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_modbus_connection.connected is False


async def test_unload_keeps_connection_held_by_temporary_consumer(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
    mock_modbus_connection_class: MagicMock,
) -> None:
    """Keep a shared connection open until its temporary hold exits."""
    params = ModbusTcpParams(host="1.1.1.1", port=502)
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    mock_modbus_connection_class.assert_called_once_with(params)

    async with async_get_temporary_unit(hass, params, UNIT_ID):
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()
        assert mock_modbus_connection.connected is True

    assert mock_modbus_connection.connected is False


async def test_shares_connection_with_another_config_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
    mock_modbus_connection_class: MagicMock,
) -> None:
    """Share one connection with another integration using the same device."""
    params = ModbusTcpParams(host="1.1.1.1", port=502)
    other_domain = "other_modbus_consumer"

    class OtherConfigFlow(ConfigFlow):
        """Stand in for another integration's config flow."""

    async def async_setup_other_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        async_get_unit(hass, entry, params, UNIT_ID)
        return True

    async def async_unload_other_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
        return True

    mock_integration(
        hass,
        MockModule(
            other_domain,
            async_setup_entry=async_setup_other_entry,
            async_unload_entry=async_unload_other_entry,
        ),
    )
    mock_platform(hass, f"{other_domain}.config_flow")
    other_entry = MockConfigEntry(domain=other_domain)
    with mock_config_flow(other_domain, OtherConfigFlow):
        other_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(other_entry.entry_id)

        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        mock_modbus_connection_class.assert_called_once_with(params)

        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()
        assert mock_modbus_connection.connected is True

        assert await hass.config_entries.async_unload(other_entry.entry_id)
        await hass.async_block_till_done()
    assert mock_modbus_connection.connected is False


async def test_unload_entry_does_not_close_connection_if_platform_unload_fails(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """Test the connection is not closed if platform unload fails."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_unload_platforms",
        return_value=False,
    ):
        result = await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert result is False
    assert mock_modbus_connection.connected is True

    # Home Assistant puts the entry into FAILED_UNLOAD, which cannot be
    # unloaded a second time. Stop the coordinator and connection explicitly
    # so the deliberately failed unload does not leak resources from the test.
    await mock_config_entry.runtime_data.async_shutdown()
    await mock_modbus_connection.close()


async def test_setup_removes_unsupported_wpmsystem_runtime_sensor(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
) -> None:
    """Setting up a WPMsystem clears a runtime sensor left by an earlier release."""
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_config_entry.add_to_hass(hass)
    stale = er.async_get(hass).async_get_or_create(
        "sensor",
        DOMAIN,
        build_unique_id(mock_config_entry, COMPRESSOR_HEATING),
        config_entry=mock_config_entry,
        suggested_object_id=COMPRESSOR_HEATING,
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id) is True
    await hass.async_block_till_done()

    assert er.async_get(hass).async_get(stale.entity_id) is None


async def test_removed_runtime_sensor_raises_no_duplicate_repair(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
) -> None:
    """A sensor about to be deleted must not be reported as a duplicate first."""
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_config_entry.add_to_hass(hass)
    registry = er.async_get(hass)
    for unique_id, object_id in (
        (build_unique_id(mock_config_entry, COMPRESSOR_HEATING), COMPRESSOR_HEATING),
        (f"{DOMAIN}_Stiebel Eltron_{COMPRESSOR_HEATING}", "legacy_compressor_heating"),
    ):
        registry.async_get_or_create(
            "sensor",
            DOMAIN,
            unique_id,
            config_entry=mock_config_entry,
            suggested_object_id=object_id,
        )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id) is True
    await hass.async_block_till_done()

    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, duplicate_entity_issue_id(mock_config_entry)
    )
    assert issue is None
