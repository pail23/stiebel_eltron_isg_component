"""Test the STIEBEL ELTRON config flow."""

from unittest.mock import MagicMock

from homeassistant.config_entries import SOURCE_DHCP, SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from modbus_connection import ModbusError
from modbus_connection.mock import MockModbusConnection
from pystiebeleltron import (
    ControllerModel,
    StiebelEltronModbusError,
    UnknownControllerModelError,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.const import DOMAIN

USER_INPUT = {CONF_HOST: "1.1.1.1", CONF_PORT: 502}
RECONFIGURE_INPUT = {CONF_HOST: "2.2.2.2", CONF_PORT: 502}
DHCP_DISCOVERY = DhcpServiceInfo(
    ip="1.1.1.2",
    hostname="servicewelt",
    macaddress="000000000001",
)


def assert_suggested_values(result, expected: dict[str, object]) -> None:
    """Assert the values Home Assistant will suggest in a config-flow form."""
    suggested_values = {
        key.schema: key.description["suggested_value"]
        for key in result["data_schema"].schema
        if key.description is not None and "suggested_value" in key.description
    }
    assert suggested_values == expected


async def test_full_flow(hass: HomeAssistant) -> None:
    """Test the full flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        USER_INPUT,
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Stiebel Eltron"
    assert result["data"] == USER_INPUT


@pytest.mark.parametrize(
    ("failing_fixture", "side_effect"),
    [
        pytest.param(
            "mock_get_controller_model", StiebelEltronModbusError, id="model_read"
        ),
        pytest.param("mock_connect_tcp", ModbusError, id="connect"),
    ],
)
async def test_form_cannot_connect(
    hass: HomeAssistant,
    request: pytest.FixtureRequest,
    failing_fixture: str,
    side_effect: type[Exception],
) -> None:
    """Test we handle a cannot connect error while opening or reading the device."""
    failing_mock = request.getfixturevalue(failing_fixture)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    failing_mock.side_effect = side_effect

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        USER_INPUT,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert_suggested_values(result, USER_INPUT)

    failing_mock.side_effect = None

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        USER_INPUT,
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_form_unknown_exception(
    hass: HomeAssistant,
    mock_get_controller_model: MagicMock,
) -> None:
    """Test we handle unknown exception."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    mock_get_controller_model.side_effect = Exception

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        USER_INPUT,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}
    assert_suggested_values(result, USER_INPUT)

    mock_get_controller_model.side_effect = None
    mock_get_controller_model.return_value = ControllerModel.LWZ  # Valid model (LWZ)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        USER_INPUT,
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_form_reports_unsupported_controller(
    hass: HomeAssistant,
    mock_get_controller_model: MagicMock,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """Test the user form reports an unsupported controller and its model ID."""
    mock_get_controller_model.side_effect = UnknownControllerModelError(165)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unsupported_controller"}
    assert result["description_placeholders"] == {"model_id": "165"}
    assert_suggested_values(result, USER_INPUT)
    assert hass.config_entries.async_entries(DOMAIN) == []
    assert mock_modbus_connection.connected is False

    mock_get_controller_model.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_reconfigure_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test reconfiguration flow."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": mock_config_entry.entry_id},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    assert_suggested_values(result, mock_config_entry.data)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        RECONFIGURE_INPUT,
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_HOST] == "2.2.2.2"

    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        pytest.param(StiebelEltronModbusError, "cannot_connect", id="cannot_connect"),
        pytest.param(Exception, "unknown", id="unknown"),
    ],
)
async def test_reconfigure_flow_errors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
    side_effect: type[Exception],
    expected_error: str,
) -> None:
    """Test error handling in reconfiguration flow."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": mock_config_entry.entry_id},
    )
    assert result["type"] is FlowResultType.FORM

    mock_get_controller_model.side_effect = side_effect
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        RECONFIGURE_INPUT,
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": expected_error}
    assert_suggested_values(result, RECONFIGURE_INPUT)

    mock_get_controller_model.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        RECONFIGURE_INPUT,
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"

    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()


async def test_reconfigure_reports_unsupported_controller(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
) -> None:
    """Test reconfiguration preserves data for an unsupported controller."""
    original_data = dict(mock_config_entry.data)
    mock_config_entry.add_to_hass(hass)
    mock_get_controller_model.side_effect = UnknownControllerModelError(165)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": mock_config_entry.entry_id},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], RECONFIGURE_INPUT
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unsupported_controller"}
    assert result["description_placeholders"] == {"model_id": "165"}
    assert_suggested_values(result, RECONFIGURE_INPUT)
    assert dict(mock_config_entry.data) == original_data

    mock_get_controller_model.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], RECONFIGURE_INPUT
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert dict(mock_config_entry.data) == RECONFIGURE_INPUT

    await hass.async_block_till_done()
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()


async def test_reconfigure_flow_already_configured(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test reconfigure aborts if another entry already uses the given host/port."""
    other_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data=RECONFIGURE_INPUT,
        entry_id="stiebel_eltron_002",
    )

    mock_config_entry.add_to_hass(hass)
    other_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": mock_config_entry.entry_id},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        RECONFIGURE_INPUT,
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test we handle already configured."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        USER_INPUT,
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_dhcp_discovery_flow(hass: HomeAssistant) -> None:
    """Test the full DHCP discovery flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_DHCP}, data=DHCP_DISCOVERY
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Stiebel Eltron"
    assert result["data"] == {CONF_HOST: "1.1.1.2", CONF_PORT: 502}
    assert result["result"].unique_id == "00:00:00:00:00:01"


async def test_dhcp_aborts_for_unsupported_controller(
    hass: HomeAssistant,
    mock_get_controller_model: MagicMock,
) -> None:
    """Test DHCP discovery reports an unsupported controller and its model ID."""
    mock_get_controller_model.side_effect = UnknownControllerModelError(165)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_DHCP}, data=DHCP_DISCOVERY
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unsupported_controller"
    assert result["description_placeholders"] == {"model_id": "165"}
    assert hass.config_entries.async_entries(DOMAIN) == []


async def test_dhcp_discovery_updates_host(hass: HomeAssistant) -> None:
    """Test DHCP discovery updates the host of an entry with a matching MAC."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502},
        unique_id="00:00:00:00:00:01",
    )
    config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_DHCP}, data=DHCP_DISCOVERY
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert config_entry.data[CONF_HOST] == "1.1.1.2"


async def test_dhcp_discovery_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test DHCP discovery aborts for an already configured host."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_DHCP},
        data=DhcpServiceInfo(
            ip="1.1.1.1",
            hostname="servicewelt",
            macaddress="000000000001",
        ),
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("side_effect", "expected_reason"),
    [
        pytest.param(StiebelEltronModbusError, "cannot_connect", id="cannot_connect"),
        pytest.param(Exception, "unknown", id="unknown"),
    ],
)
async def test_dhcp_discovery_errors(
    hass: HomeAssistant,
    mock_get_controller_model: MagicMock,
    side_effect: type[Exception],
    expected_reason: str,
) -> None:
    """Test DHCP discovery aborts when the device cannot be validated."""
    mock_get_controller_model.side_effect = side_effect

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_DHCP}, data=DHCP_DISCOVERY
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == expected_reason
