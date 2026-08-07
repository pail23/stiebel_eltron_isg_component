"""Config flow for the STIEBEL ELTRON integration."""

from collections.abc import Mapping
from dataclasses import dataclass, field
import logging
from types import MappingProxyType
from typing import Any, override

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from modbus_connection import ModbusError
from modbus_connection.pymodbus import connect_tcp
from pystiebeleltron import (
    StiebelEltronModbusError,
    UnknownControllerModelError,
    get_controller_model,
)
import voluptuous as vol

from .const import DEFAULT_PORT, DOMAIN, UNIT_ID

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): TextSelector(),
    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
        NumberSelector(
            NumberSelectorConfig(min=1, max=65535, mode=NumberSelectorMode.BOX)
        ),
        vol.Coerce(int),
    ),
})


@dataclass(frozen=True)
class ControllerCheckResult:
    """Result of validating a controller during a config flow."""

    error: str | None = None
    description_placeholders: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({})
    )


async def check_controller_model(host: str, port: int) -> ControllerCheckResult:
    """Check if the controller model is valid."""
    try:
        connection = await connect_tcp(host, port=port)
        try:
            await get_controller_model(connection.for_unit(UNIT_ID))
        finally:
            await connection.close()
    except UnknownControllerModelError as exception:
        _LOGGER.debug("Unsupported controller model %s", exception.model_id)
        return ControllerCheckResult(
            "unsupported_controller",
            MappingProxyType({"model_id": str(exception.model_id)}),
        )
    except StiebelEltronModbusError, ModbusError:
        _LOGGER.debug("Cannot connect to Stiebel Eltron device", exc_info=True)
        return ControllerCheckResult("cannot_connect")
    except Exception:
        _LOGGER.exception("Unexpected exception")
        return ControllerCheckResult("unknown")
    return ControllerCheckResult()


class StiebelEltronConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STIEBEL ELTRON."""

    VERSION = 1

    _discovered_host: str

    @override
    async def async_step_dhcp(
        self, discovery_info: DhcpServiceInfo
    ) -> ConfigFlowResult:
        """Handle DHCP discovery."""
        await self.async_set_unique_id(format_mac(discovery_info.macaddress))
        self._abort_if_unique_id_configured(updates={CONF_HOST: discovery_info.ip})
        self._async_abort_entries_match({CONF_HOST: discovery_info.ip})

        check_result = await check_controller_model(discovery_info.ip, DEFAULT_PORT)
        if check_result.error is not None:
            return self.async_abort(
                reason=check_result.error,
                description_placeholders=dict(check_result.description_placeholders),
            )

        self._discovered_host = discovery_info.ip
        self.context["title_placeholders"] = {CONF_HOST: discovery_info.ip}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow the user to confirm adding the discovered device."""
        if user_input is not None:
            return self.async_create_entry(
                title="Stiebel Eltron",
                data={CONF_HOST: self._discovered_host, CONF_PORT: DEFAULT_PORT},
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={CONF_HOST: self._discovered_host},
        )

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match({
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
            })
            check_result = await check_controller_model(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if check_result.error is not None:
                errors["base"] = check_result.error
                description_placeholders = dict(check_result.description_placeholders)
            else:
                return self.async_create_entry(title="Stiebel Eltron", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders=description_placeholders,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a reconfiguration flow."""
        config_entry = self._get_reconfigure_entry()

        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] = {}
        if user_input is not None:
            self._async_abort_entries_match({
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
            })
            check_result = await check_controller_model(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if check_result.error is not None:
                errors["base"] = check_result.error
                description_placeholders = dict(check_result.description_placeholders)
            else:
                return self.async_update_reload_and_abort(
                    config_entry,
                    data_updates={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                    },
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, config_entry.data
            ),
            errors=errors,
            description_placeholders=description_placeholders,
        )
