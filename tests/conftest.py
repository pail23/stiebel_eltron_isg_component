"""Common fixtures for the STIEBEL ELTRON tests."""

from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager
from unittest.mock import MagicMock, PropertyMock, patch

from homeassistant.const import CONF_HOST, CONF_PORT
from modbus_connection.mock import MockModbusConnection
from pystiebeleltron import ControllerModel
from pystiebeleltron.lwz import OperatingMode
from pystiebeleltron.wpm import (
    WpmEnergyData,
    WpmEnergyManagementSettings,
    WpmEnergySystemInformation,
    WpmExtendedEnergyData,
    WpmSystemParameters,
    WpmSystemState,
    WpmSystemValues,
)
from pystiebeleltron.wpm3i import (
    Wpm3iEnergyData,
    Wpm3iEnergyManagementSettings,
    Wpm3iEnergySystemInformation,
    Wpm3iSystemParameters,
    Wpm3iSystemState,
    Wpm3iSystemValues,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations in all tests."""
    return


@pytest.fixture
async def mock_modbus_connection() -> AsyncGenerator[MockModbusConnection]:
    """Provide a connected in-memory Modbus connection for each test."""
    connection = MockModbusConnection()
    await connection.connect()
    yield connection
    if connection.connected:
        await connection.close()


@pytest.fixture(autouse=True)
def mock_get_controller_model() -> Generator[MagicMock]:
    """Mock the Stiebel Eltron get_controller_model function."""
    with (
        patch(
            "custom_components.stiebel_eltron_isg.get_controller_model",
            autospec=True,
        ) as mock_get_model,
        patch(
            "custom_components.stiebel_eltron_isg.config_flow.get_controller_model",
            new=mock_get_model,
        ),
    ):
        mock_get_model.return_value = ControllerModel.WPM_3
        yield mock_get_model


@pytest.fixture(autouse=True)
def mock_get_unit(
    mock_modbus_connection: MockModbusConnection,
) -> Generator[MagicMock]:
    """Patch Home Assistant unit acquisition for config entry setup."""

    def get_unit(hass, entry, params, unit_id):
        entry.async_on_unload(mock_modbus_connection.close)
        return mock_modbus_connection.for_unit(unit_id)

    getter = MagicMock(side_effect=get_unit)
    with patch("custom_components.stiebel_eltron_isg.async_get_unit", new=getter):
        yield getter


@pytest.fixture(autouse=True)
def mock_get_temporary_unit(
    mock_modbus_connection: MockModbusConnection,
) -> Generator[MagicMock]:
    """Patch temporary unit acquisition for config-flow probes."""

    @asynccontextmanager
    async def get_temporary_unit(hass, params, unit_id):
        yield mock_modbus_connection.for_unit(unit_id)

    getter = MagicMock(side_effect=get_temporary_unit)
    with patch(
        "custom_components.stiebel_eltron_isg.config_flow.async_get_temporary_unit",
        new=getter,
    ):
        yield getter


@pytest.fixture(autouse=True)
def mock_lwz_api() -> Generator[MagicMock]:
    """Patch the LWZ API and return the mocked client."""

    with patch(
        "custom_components.stiebel_eltron_isg.lwz_coordinator.LwzStiebelEltronAPI",
        autospec=True,
    ) as mock_api_cls:
        api_client = mock_api_cls.return_value

        api_client.get_target_temp.return_value = 22.5
        api_client.get_current_temp.return_value = 21.0
        api_client.get_current_humidity.return_value = 45.0
        api_client.get_operation.return_value = OperatingMode.AUTOMATIC
        api_client.get_heating_status.return_value = True
        api_client.get_cooling_status.return_value = False
        api_client.get_filter_alarm_status.return_value = False

        yield api_client


@pytest.fixture(autouse=True)
def mock_wpm_3i_api() -> Generator[MagicMock]:
    """Patch the WPM API and return the mocked client."""

    with patch(
        "custom_components.stiebel_eltron_isg.wpm3i_coordinator.Wpm3iStiebelEltronAPI",
        autospec=True,
    ) as mock_api_cls:
        api_client = mock_api_cls.return_value
        type(api_client).energy_system_information = PropertyMock(
            return_value=MagicMock(spec=Wpm3iEnergySystemInformation)
        )
        type(api_client).energy_management_settings = PropertyMock(
            return_value=MagicMock(spec=Wpm3iEnergyManagementSettings)
        )
        type(api_client).system_parameters = PropertyMock(
            return_value=MagicMock(spec=Wpm3iSystemParameters)
        )
        type(api_client).energy_data = PropertyMock(
            return_value=MagicMock(spec=Wpm3iEnergyData)
        )
        type(api_client).system_state = PropertyMock(
            return_value=MagicMock(spec=Wpm3iSystemState)
        )
        type(api_client).system_values = PropertyMock(
            return_value=MagicMock(spec=Wpm3iSystemValues)
        )
        yield api_client


@pytest.fixture(autouse=True)
def mock_wpm_api() -> Generator[MagicMock]:
    """Patch the WPM API and return the mocked client."""

    with patch(
        "custom_components.stiebel_eltron_isg.wpm_coordinator.WpmStiebelEltronAPI",
        autospec=True,
    ) as mock_api_cls:
        api_client = mock_api_cls.return_value
        type(api_client).energy_system_information = PropertyMock(
            return_value=MagicMock(spec=WpmEnergySystemInformation)
        )
        type(api_client).system_parameters = PropertyMock(
            return_value=MagicMock(spec=WpmSystemParameters)
        )
        type(api_client).energy_management_settings = PropertyMock(
            return_value=MagicMock(spec=WpmEnergyManagementSettings)
        )
        type(api_client).energy_data = PropertyMock(
            return_value=MagicMock(spec=WpmEnergyData)
        )
        # The optional components are built in the API constructor, so autospec
        # does not know them and every accessor on them would raise
        # AttributeError, which silently drops those entities.
        type(api_client).extended_energy_data = PropertyMock(
            return_value=MagicMock(spec=WpmExtendedEnergyData)
        )
        type(api_client).system_state = PropertyMock(
            return_value=MagicMock(spec=WpmSystemState)
        )
        type(api_client).system_values = PropertyMock(
            return_value=MagicMock(spec=WpmSystemValues)
        )
        yield api_client


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Mock a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502},
        entry_id="stiebel_eltron_001",
    )
