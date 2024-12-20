"""Adds config flow for Stiebel Eltron ISG."""

from __future__ import annotations

import ipaddress
import re

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, CONN_CLASS_LOCAL_POLL
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback

from .const import (
    DEFAULT_HOST_NAME,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    },
)


def host_valid(host):
    """Return True if hostname or IP address is valid."""
    try:
        if ipaddress.ip_address(host).version in (4, 6):
            return True
    except ValueError:
        disallowed = re.compile(r"[^a-zA-Z\d\-]")
        return all(x and not disallowed.search(x) for x in host.split("."))


@callback
def stiebeleltron_modbus_entries(hass: HomeAssistant):
    """Return the hosts already configured."""
    return {
        entry.data[CONF_HOST] for entry in hass.config_entries.async_entries(DOMAIN)
    }


@callback
def stiebeleltron_entries(hass: HomeAssistant):
    """Return the hosts already configured."""
    return {
        entry.data[CONF_NAME] for entry in hass.config_entries.async_entries(DOMAIN)
    }


class StiebelEltronISGFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Stiebel Eltron ISG."""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    def _host_in_configuration_exists(self, host) -> bool:
        """Return True if host exists in configuration."""
        return host in stiebeleltron_modbus_entries(self.hass)

    def _name_in_configuration_exists(self, name) -> bool:
        """Return True if host exists in configuration."""
        return name in stiebeleltron_entries(self.hass)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            host = user_input[CONF_HOST]
            name = user_input[CONF_NAME]

            if self._host_in_configuration_exists(host):
                self._errors[CONF_HOST] = "already_configured"
            elif self._name_in_configuration_exists(name):
                self._errors[CONF_NAME] = "already_configured"
            elif not host_valid(user_input[CONF_HOST]):
                self._errors[CONF_HOST] = "invalid_host_IP"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )
            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_NAME] = DEFAULT_NAME
        user_input[CONF_HOST] = DEFAULT_HOST_NAME
        user_input[CONF_PORT] = DEFAULT_PORT
        user_input[CONF_SCAN_INTERVAL] = DEFAULT_SCAN_INTERVAL
        return await self._show_config_form(user_input)

    #        return self.async_show_form(
    #            step_id="user", data_schema=DATA_SCHEMA, errors=self._errors
    #        )

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                    vol.Required(CONF_HOST, default=user_input[CONF_HOST]): str,
                    vol.Required(CONF_PORT, default=user_input[CONF_PORT]): int,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=user_input[CONF_SCAN_INTERVAL],
                    ): int,
                },
            ),
            errors=self._errors,
        )
