"""Common fixtures for the STIEBEL ELTRON tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from homeassistant.const import CONF_HOST, CONF_PORT
from modbus_connection.mock import MockModbusConnection
from pystiebeleltron import ControllerModel, EnergySystemInformation
from pystiebeleltron.lwz import OperatingMode
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
def mock_connect_tcp(
    mock_modbus_connection: MockModbusConnection,
) -> Generator[AsyncMock]:
    """Patch connect_tcp to return the in-memory mock connection."""
    connect = AsyncMock(return_value=mock_modbus_connection)
    with (
        patch("custom_components.stiebel_eltron_isg.connect_tcp", new=connect),
        patch(
            "custom_components.stiebel_eltron_isg.config_flow.connect_tcp",
            new=connect,
        ),
    ):
        yield connect


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
def mock_wpm_api() -> Generator[MagicMock]:
    """Patch the WPM API and return the mocked client."""

    with patch(
        "custom_components.stiebel_eltron_isg.wpm_coordinator.WpmStiebelEltronAPI",
        autospec=True,
    ) as mock_api_cls:
        api_client = mock_api_cls.return_value
        type(api_client).energy_system_information = PropertyMock(
            return_value=MagicMock(spec=EnergySystemInformation)
        )
        # api_client.energy_system_information.controller_identification = 390

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
