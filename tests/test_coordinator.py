"""Tests for coordinator write actions."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from modbus_connection import ModbusError
from pystiebeleltron import ControllerModel, StiebelEltronModbusError
import pytest

from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronDataCoordinator,
)
from custom_components.stiebel_eltron_isg.lwz_coordinator import (
    StiebelEltronModbusLWZDataCoordinator,
)
from custom_components.stiebel_eltron_isg.wpm3i_coordinator import (
    StiebelEltronModbusWPM3iDataCoordinator,
)


def _coordinator(api) -> StiebelEltronDataCoordinator:
    """Build a coordinator without invoking Home Assistant setup."""
    coordinator = StiebelEltronDataCoordinator.__new__(StiebelEltronDataCoordinator)
    coordinator._api = api
    return coordinator


async def test_write_component_value_writes_supported_field() -> None:
    """A supported field is passed to the library unchanged."""
    component = SimpleNamespace(target=21.0, write=AsyncMock())
    coordinator = _coordinator(SimpleNamespace(parameters=component))

    await coordinator.write_component_value("parameters", "target", 22.0)

    component.write.assert_awaited_once_with("target", 22.0)


@pytest.mark.parametrize(
    ("api", "component", "field"),
    [
        pytest.param(SimpleNamespace(), "missing", "target", id="missing-component"),
        pytest.param(
            SimpleNamespace(parameters=SimpleNamespace(write=AsyncMock())),
            "parameters",
            "missing",
            id="missing-field",
        ),
    ],
)
async def test_write_component_value_rejects_unsupported_target(
    api,
    component: str,
    field: str,
) -> None:
    """Missing components and fields must not silently swallow an action."""
    coordinator = _coordinator(api)

    with pytest.raises(HomeAssistantError) as error:
        await coordinator.write_component_value(component, field, 22.0)

    assert type(error.value) is HomeAssistantError
    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == "write_unsupported"
    assert error.value.translation_placeholders == {"field": field}


@pytest.mark.parametrize(
    "read_only_error",
    [
        pytest.param(
            AttributeError("target is read-only"),
            id="read-only-field",
        ),
        pytest.param(
            AttributeError("target is in the input register space, which is read-only"),
            id="read-only-space",
        ),
    ],
)
async def test_write_component_value_reports_read_only_field(
    read_only_error: AttributeError,
) -> None:
    """The library's read-only error is exposed as a translated HA error."""
    component = SimpleNamespace(
        target=21.0,
        write=AsyncMock(side_effect=read_only_error),
    )
    coordinator = _coordinator(SimpleNamespace(parameters=component))

    with pytest.raises(HomeAssistantError) as error:
        await coordinator.write_component_value("parameters", "target", 22.0)

    assert type(error.value) is HomeAssistantError
    assert error.value.translation_key == "write_unsupported"
    assert error.value.__cause__ is read_only_error


async def test_write_component_value_reports_invalid_value() -> None:
    """Library validation failures are service validation errors."""
    component = SimpleNamespace(
        target=21.0,
        write=AsyncMock(side_effect=ValueError("outside allowed range")),
    )
    coordinator = _coordinator(SimpleNamespace(parameters=component))

    with pytest.raises(ServiceValidationError) as error:
        await coordinator.write_component_value("parameters", "target", 99.0)

    assert type(error.value) is ServiceValidationError
    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == "invalid_write_value"
    assert error.value.translation_placeholders == {
        "field": "target",
        "value": "99.0",
    }
    assert isinstance(error.value.__cause__, ValueError)


@pytest.mark.parametrize(
    "write_error",
    [
        pytest.param(ModbusError("write failed"), id="modbus"),
        pytest.param(StiebelEltronModbusError(), id="library"),
    ],
)
async def test_write_component_value_reports_communication_error(
    write_error: Exception,
) -> None:
    """Communication failures are exposed as translated HA errors."""
    component = SimpleNamespace(
        target=21.0,
        write=AsyncMock(side_effect=write_error),
    )
    coordinator = _coordinator(SimpleNamespace(parameters=component))

    with pytest.raises(HomeAssistantError) as error:
        await coordinator.write_component_value("parameters", "target", 22.0)

    assert type(error.value) is HomeAssistantError
    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == "write_failed"
    assert error.value.translation_placeholders == {"field": "target"}
    assert error.value.__cause__ is write_error


@pytest.mark.parametrize(
    "write_error",
    [
        pytest.param(RuntimeError("boom"), id="runtime-error"),
        pytest.param(
            AttributeError("'NoneType' object has no attribute 'address'"),
            id="unrelated-attribute-error",
        ),
    ],
)
async def test_write_component_value_propagates_unexpected_error(
    write_error: Exception,
) -> None:
    """Unexpected library defects must not be disguised as device limitations."""
    component = SimpleNamespace(
        target=21.0,
        write=AsyncMock(side_effect=write_error),
    )
    coordinator = _coordinator(SimpleNamespace(parameters=component))

    with pytest.raises(type(write_error)) as error:
        await coordinator.write_component_value("parameters", "target", 22.0)

    assert error.value is write_error


async def test_reset_heatpump_uses_wpm_reset_value() -> None:
    """The base WPM coordinator resets with the WPM-specific value."""
    coordinator = _coordinator(SimpleNamespace())
    coordinator.write_component_value = AsyncMock()

    await coordinator.async_reset_heatpump()

    coordinator.write_component_value.assert_awaited_once_with(
        "system_parameters", "reset", 3
    )


async def test_lwz_reset_heatpump_uses_central_write_path() -> None:
    """LWZ keeps its value 1 while using the shared error handling."""
    coordinator = StiebelEltronModbusLWZDataCoordinator.__new__(
        StiebelEltronModbusLWZDataCoordinator
    )
    coordinator.write_component_value = AsyncMock()

    await coordinator.async_reset_heatpump()

    coordinator.write_component_value.assert_awaited_once_with(
        "system_parameters", "reset", 1
    )


def test_wpm_3i_coordinator_initializes_model_specific_api(
    hass,
    mock_config_entry,
    mock_modbus_connection,
    mock_wpm_3i_api,
) -> None:
    """The WPM 3i coordinator keeps its model-specific API, model and host."""
    coordinator = StiebelEltronModbusWPM3iDataCoordinator(
        hass,
        mock_config_entry,
        ControllerModel.WPM_3i,
        mock_modbus_connection,
        "isg.local",
    )

    assert coordinator.model is ControllerModel.WPM_3i
    assert coordinator.host == "isg.local"
    assert coordinator._api is mock_wpm_3i_api
