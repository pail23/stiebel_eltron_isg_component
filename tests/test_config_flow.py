"""Test stiebel_eltron_isg config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.data_entry_flow import FlowResultType

from custom_components.stiebel_eltron_isg.const import (
    DOMAIN,
)

from .const import MOCK_CONFIG, MOCK_INVALID_IP_CONFIG


# This fixture bypasses the actual setup of the integration
# since we only want to test the config flow. We test the
# actual functionality of the integration in other test modules.
@pytest.fixture(autouse=True)
def bypass_setup_fixture():
    """Prevent setup."""
    with (
        patch(
            "custom_components.stiebel_eltron_isg.async_setup",
            return_value=True,
        ),
        patch(
            "custom_components.stiebel_eltron_isg.async_setup_entry",
            return_value=True,
        ),
        patch(
            "custom_components.stiebel_eltron_isg.async_unload_entry",
            return_value=True,
        ),
    ):
        yield


# Here we simiulate a successful config flow from the backend.
# Note that we use the `bypass_get_data` fixture here because
# we want the config flow validation to succeed during the test.
@pytest.mark.asyncio()
async def test_successful_config_flow(hass, bypass_get_data):
    """Test a successful config flow."""
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to enter `test_username` for username and `test_password`
    # for password, it would result in this function call
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_CONFIG,
    )

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Stiebel Eltron ISG"
    assert result["data"] == MOCK_CONFIG
    assert result["result"]


# In this case, we want to simulate a failure during the config flow.
# We use the `error_on_get_data` mock instead of `bypass_get_data`
# (note the function parameters) to raise an Exception during
# validation of the input config.
@pytest.mark.asyncio()
async def test_failed_config_flow(hass, error_on_get_data):
    """Test a failed config flow due to credential validation failure."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_INVALID_IP_CONFIG,
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_HOST: "invalid_host_IP"}


@pytest.mark.asyncio()
async def test_successful_reconfigure_flow(hass, bypass_get_data):
    """Test a successful reconfigure flow."""
    # First, create a config entry
    config_entry = hass.config_entries.async_entries(DOMAIN)
    if not config_entry:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG,
        )
        config_entry = hass.config_entries.async_entries(DOMAIN)[0]
    else:
        config_entry = config_entry[0]

    # Initialize a reconfigure flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": config_entry.entry_id,
        },
    )

    # Check that the reconfigure flow shows the reconfigure form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Configure with new host and port
    new_host_config = {
        CONF_HOST: "192.168.1.100",
        CONF_PORT: 502,
    }
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=new_host_config,
    )

    # Check that the reconfigure flow is complete
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"


@pytest.mark.asyncio()
async def test_reconfigure_invalid_host(hass, bypass_get_data):
    """Test reconfigure flow with invalid host IP."""
    # Create a config entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_CONFIG,
    )
    config_entry = hass.config_entries.async_entries(DOMAIN)[0]

    # Initialize a reconfigure flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": config_entry.entry_id,
        },
    )

    # Configure with invalid host
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_INVALID_IP_CONFIG,
    )

    # Check that the reconfigure flow shows an error
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_HOST: "invalid_host_IP"}


@pytest.mark.asyncio()
async def test_reconfigure_cannot_connect(hass, bypass_get_data):
    """Test reconfigure flow with connection failure."""
    # Create a config entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_CONFIG,
    )
    config_entry = hass.config_entries.async_entries(DOMAIN)[0]

    # Initialize a reconfigure flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": config_entry.entry_id,
        },
    )

    # Mock a connection failure
    with patch(
        "custom_components.stiebel_eltron_isg.config_flow.get_controller_model",
        side_effect=Exception("Connection failed"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_HOST: "192.168.1.50",
                CONF_PORT: 502,
            },
        )

    # Check that the reconfigure flow shows an error
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_HOST: "cannot_connect"}


@pytest.mark.asyncio()
async def test_reconfigure_already_configured_host(hass, bypass_get_data):
    """Test reconfigure flow when trying to use an already configured host."""
    # Create first config entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=MOCK_CONFIG,
    )

    # Create second config entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    new_config = {
        CONF_NAME: "Another ISG",
        CONF_HOST: "192.168.1.200",
        CONF_PORT: 502,
    }
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=new_config,
    )
    config_entry_2 = hass.config_entries.async_entries(DOMAIN)[1]

    # Initialize a reconfigure flow for the second entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": config_entry_2.entry_id,
        },
    )

    # Try to configure with the first entry's host
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: MOCK_CONFIG[CONF_HOST],
            CONF_PORT: MOCK_CONFIG[CONF_PORT],
        },
    )

    # Check that the reconfigure flow shows an already_configured error
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_HOST: "already_configured"}
