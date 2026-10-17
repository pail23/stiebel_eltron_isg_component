"""Tests for coordinator write actions."""

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.update_coordinator import UpdateFailed
from modbus_connection import ModbusError
from modbus_connection.model import Component, ManualComponent
import pystiebeleltron
from pystiebeleltron import ControllerModel
import pytest

from custom_components.stiebel_eltron_isg import coordinator as coordinator_module
from custom_components.stiebel_eltron_isg.const import DOMAIN
from custom_components.stiebel_eltron_isg.coordinator import (
    CONTROLLER_FAMILIES,
    RESET_VALUES,
    ControllerFamily,
    StiebelEltronDataCoordinator,
    coordinator_display_name,
    create_api,
)
from custom_components.stiebel_eltron_isg.sensor import (
    StiebelEltronISGSensor,
    StiebelEltronSensorEntityDescription,
)


def test_library_modbus_error_is_the_transport_error() -> None:
    """The direct transport import must catch the library's re-exported error."""
    assert pystiebeleltron.ModbusError is ModbusError


def _coordinator(api) -> StiebelEltronDataCoordinator:
    """Build a coordinator without invoking Home Assistant setup."""
    coordinator = StiebelEltronDataCoordinator.__new__(StiebelEltronDataCoordinator)
    coordinator._api = api
    coordinator._model = ControllerModel.WPM_3
    coordinator._refresh_generation = 0
    coordinator._pending_writes = {}
    coordinator._listeners = {}
    return coordinator


async def test_coordinator_and_entity_recover_after_repeated_offline_updates(
    hass,
    mock_config_entry,
    mock_modbus_connection,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """One outage log and one recovery log accompany entity availability."""

    class SequencedApi:
        value = 21.5

        def __init__(self) -> None:
            self._updates = [
                None,
                ModbusError("offline"),
                ModbusError("still offline"),
                None,
            ]

        async def async_update(self) -> None:
            outcome = self._updates.pop(0)
            if outcome is not None:
                raise outcome
            if not self._updates:
                self.value = 22.0

    api = SequencedApi()
    display_name = coordinator_display_name(ControllerModel.WPM_3)
    coordinator = StiebelEltronDataCoordinator(
        hass, mock_config_entry, api, ControllerModel.WPM_3, "isg.local"
    )
    entity = StiebelEltronISGSensor(
        coordinator,
        mock_config_entry,
        StiebelEltronSensorEntityDescription(
            key="outdoor_temperature",
            modbus_register=lambda client: client.value,
        ),
    )
    caplog.set_level(logging.INFO, logger="custom_components.stiebel_eltron_isg")

    await coordinator.async_refresh()
    assert entity.available is True

    await coordinator.async_refresh()
    assert entity.available is False

    await coordinator.async_refresh()
    assert entity.available is False

    await coordinator.async_refresh()
    assert entity.available is True
    assert entity.native_value == 22.0

    # These messages come from DataUpdateCoordinator. Keeping them here pins the
    # ModbusError -> UpdateFailed translation: returning stale data quietly
    # would leave the entity available and suppress both transition messages.
    outage_logs = [
        record
        for record in caplog.records
        if f"Error fetching {display_name} data" in record.getMessage()
    ]
    recovery_logs = [
        record
        for record in caplog.records
        if record.getMessage() == f"Fetching {display_name} data recovered"
    ]
    assert len(outage_logs) == 1
    assert len(recovery_logs) == 1


async def test_equal_data_refreshes_still_notify_entities(
    hass,
    mock_config_entry,
    mock_modbus_connection,
) -> None:
    """Every successful device poll must notify entities.

    Register values are cached on the API client while the coordinator holds
    no data. Disabling ``always_update`` would therefore suppress every
    listener update after the first successful poll.
    """
    api = SimpleNamespace(async_update=AsyncMock())
    coordinator = StiebelEltronDataCoordinator(
        hass, mock_config_entry, api, ControllerModel.WPM_3, "isg.local"
    )
    listener = MagicMock()
    remove_listener = coordinator.async_add_listener(listener)

    try:
        await coordinator.async_refresh()
        await coordinator.async_refresh()

        assert coordinator.data is None
        assert api.async_update.await_count == 2
        assert listener.call_count == 2
    finally:
        remove_listener()


def test_host_returns_the_configured_address() -> None:
    """The coordinator exposes the address used for its device."""
    coordinator = _coordinator(SimpleNamespace())
    coordinator._host = "isg.local"

    assert coordinator.host == "isg.local"


def test_get_raw_data_combines_all_api_components() -> None:
    """Diagnostics receive the rows of every API component."""
    first = Component.__new__(Component)
    second = ManualComponent.__new__(ManualComponent)
    coordinator = _coordinator(
        SimpleNamespace(first=first, second=second, _group=object())
    )

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

    assert rows.call_count == 2
    assert rows.call_args_list[0].args == (first,)
    assert rows.call_args_list[1].args == (second,)


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


async def test_write_component_value_reports_communication_error() -> None:
    """Communication failures are exposed as translated HA errors."""
    component = SimpleNamespace(
        target=21.0,
        write=AsyncMock(side_effect=ModbusError("write failed")),
    )
    coordinator = _coordinator(SimpleNamespace(parameters=component))

    with pytest.raises(HomeAssistantError) as error:
        await coordinator.write_component_value("parameters", "target", 22.0)

    assert type(error.value) is HomeAssistantError
    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == "write_failed"
    assert error.value.translation_placeholders == {"field": "target"}
    assert isinstance(error.value.__cause__, ModbusError)


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


@pytest.mark.parametrize(
    ("model", "reset_value"),
    [
        (ControllerModel.WPM_3, 3),
        (ControllerModel.WPM_3i, 3),
        (ControllerModel.WPMsystem, 3),
        (ControllerModel.LWZ_R290, 3),
        (ControllerModel.LWZ, 1),
        (ControllerModel.LWZ_x04_SOL, 1),
    ],
)
async def test_reset_heatpump_writes_the_value_of_the_family(
    model: ControllerModel, reset_value: int
) -> None:
    """Every model resets through the shared write path with its family's value."""
    coordinator = _coordinator(SimpleNamespace())
    coordinator._model = model
    coordinator.write_component_value = AsyncMock()

    await coordinator.async_reset_heatpump()

    coordinator.write_component_value.assert_awaited_once_with(
        "system_parameters", "reset", reset_value
    )


def test_every_family_has_a_reset_value() -> None:
    """A family added to the layout table cannot be left without one."""
    assert set(RESET_VALUES) == set(ControllerFamily)
    assert set(CONTROLLER_FAMILIES) == set(ControllerModel)


@pytest.mark.parametrize(
    ("family", "api_fixture"),
    [
        (ControllerFamily.WPM_3I, "mock_wpm_3i_api"),
        (ControllerFamily.WPM, "mock_wpm_api"),
        (ControllerFamily.LWZ, "mock_lwz_api"),
    ],
)
def test_create_api_picks_the_client_of_the_family(
    request: pytest.FixtureRequest,
    mock_modbus_connection,
    family: ControllerFamily,
    api_fixture: str,
) -> None:
    """Each register layout is read by its own library client."""
    api = create_api(family, mock_modbus_connection.for_unit(1))

    assert api is request.getfixturevalue(api_fixture)


def test_coordinator_keeps_api_model_and_host(
    hass,
    mock_config_entry,
    mock_modbus_connection,
    mock_wpm_3i_api,
) -> None:
    """The coordinator exposes the client, model and host it was set up with."""
    coordinator = StiebelEltronDataCoordinator(
        hass,
        mock_config_entry,
        create_api(ControllerFamily.WPM_3I, mock_modbus_connection.for_unit(1)),
        ControllerModel.WPM_3i,
        "isg.local",
    )

    assert coordinator.model is ControllerModel.WPM_3i
    assert coordinator.family is ControllerFamily.WPM_3I
    assert coordinator.host == "isg.local"
    assert coordinator._api is mock_wpm_3i_api
