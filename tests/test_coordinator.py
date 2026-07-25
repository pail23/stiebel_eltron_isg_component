"""Tests for coordinator write actions."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.update_coordinator import UpdateFailed
from modbus_connection import ModbusError
from pystiebeleltron import ControllerModel, StiebelEltronModbusError
import pytest

from custom_components.stiebel_eltron_isg import coordinator as coordinator_module
from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronDataCoordinator,
)
from custom_components.stiebel_eltron_isg.lwz_coordinator import (
    StiebelEltronModbusLWZDataCoordinator,
)


def _coordinator(api) -> StiebelEltronDataCoordinator:
    """Build a coordinator without invoking Home Assistant setup."""
    coordinator = StiebelEltronDataCoordinator.__new__(StiebelEltronDataCoordinator)
    coordinator._api = api
    return coordinator


def test_for_unit_uses_the_active_connection() -> None:
    """Unit access must be delegated to the shared connection."""
    coordinator = _coordinator(SimpleNamespace())
    connection = MagicMock()
    coordinator._connection = connection

    assert coordinator._for_unit(1) is connection.for_unit.return_value
    connection.for_unit.assert_called_once_with(1)


def test_for_unit_rejects_a_missing_connection() -> None:
    """Access without a connection must fail explicitly."""
    coordinator = _coordinator(SimpleNamespace())
    coordinator._connection = None

    with pytest.raises(RuntimeError, match="Connection not established"):
        coordinator._for_unit(1)


@pytest.mark.parametrize(
    ("connection", "expected"),
    [
        (None, False),
        (SimpleNamespace(connected=False), False),
        (SimpleNamespace(connected=True), True),
    ],
)
def test_is_connected_reflects_the_connection(connection, expected: bool) -> None:
    """Connection state must include the not-yet-connected case."""
    coordinator = _coordinator(SimpleNamespace())
    coordinator._connection = connection

    assert coordinator.is_connected is expected


def test_host_returns_the_configured_address() -> None:
    """The coordinator exposes the address used for its device."""
    coordinator = _coordinator(SimpleNamespace())
    coordinator._host = "isg.local"

    assert coordinator.host == "isg.local"


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (ControllerModel.LWZ, "LWA/LWZ"),
        (ControllerModel.LWZ_x04_SOL, "LWZ"),
        (ControllerModel.WPM_3, "WPM 3"),
        (ControllerModel.WPM_3i, "WPM 3i"),
        (ControllerModel.WPMsystem, "WPMsystem"),
        (ControllerModel.LWZ_R290, "LWZ R290"),
        (SimpleNamespace(name="FUTURE"), "other model (FUTURE)"),
    ],
)
def test_model_name_is_readable(model, expected: str) -> None:
    """Every known model and the forward-compatible fallback have a name."""
    coordinator = _coordinator(SimpleNamespace())
    coordinator._model = model

    assert coordinator.model_name == expected


def test_get_raw_data_combines_all_api_components() -> None:
    """Diagnostics receive the rows of every API component."""
    first = object()
    second = object()
    coordinator = _coordinator(SimpleNamespace(first=first, second=second))

    with patch.object(
        coordinator_module,
        "field_rows",
        side_effect=(
            [("first", 1), ("shared", 1)],
            [("second", 2), ("shared", 2)],
        ),
    ) as rows:
        assert coordinator.get_raw_data() == {
            "first": 1,
            "second": 2,
            "shared": 2,
        }

    assert rows.call_args_list[0].args == (first,)
    assert rows.call_args_list[1].args == (second,)


def test_get_value_returns_none_for_library_read_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A register read error makes one entity unavailable without crashing."""
    coordinator = _coordinator(SimpleNamespace())

    def failed_accessor(api):
        raise StiebelEltronModbusError

    assert coordinator.get_value(failed_accessor) is None
    assert "Failed to get value from accessor" in caplog.text


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1, 1), (1.5, 1.5), (True, True), ("not numeric", None), (None, None)],
)
def test_get_value_only_accepts_numeric_states(value, expected) -> None:
    """Entity state accessors may only return numeric Modbus values."""
    coordinator = _coordinator(SimpleNamespace(value=value))

    assert coordinator.get_value(lambda api: api.value) == expected


async def test_refresh_generations_only_advance_success_after_read() -> None:
    """Entities can distinguish an old or failed poll from fresh device data."""
    api = SimpleNamespace(async_update=AsyncMock())
    coordinator = _coordinator(api)
    coordinator._refresh_generation = 0
    coordinator._last_successful_refresh_generation = 0

    await coordinator._async_update_data()

    assert coordinator.refresh_generation == 1
    assert coordinator.last_successful_refresh_generation == 1

    api.async_update.side_effect = ModbusError("read failed")
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.refresh_generation == 2
    assert coordinator.last_successful_refresh_generation == 1


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
