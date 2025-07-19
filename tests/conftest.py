"""Global fixtures for stiebel_eltron_isg integration."""

# Fixtures allow you to replace functions with a Mock object. You can perform
# many options via the Mock to reflect a particular behavior from the original
# function that you want to see without going through the function's actual logic.
# Fixtures can either be passed into tests as parameters, or if autouse=True, they
# will automatically be used across all tests.
#
# Fixtures that are defined in conftest.py are available across all tests. You can also
# define fixtures within a particular test file to scope them locally.
#
# pytest_homeassistant_custom_component provides some fixtures that are provided by
# Home Assistant core. You can find those fixture definitions here:
# https://github.com/MatthewFlamm/pytest-homeassistant-custom-component/blob/master/pytest_homeassistant_custom_component/common.py
#
# See here for more info: https://docs.pytest.org/en/latest/fixture.html (note that
# pytest includes fixtures OOB which you can use as defined on this page)
from unittest.mock import patch

import pytest
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
    ReadInputRegistersResponse,
)
from pystiebeleltron import ControllerModel

pytest_plugins = "pytest_homeassistant_custom_component"


# This fixture enables loading custom integrations in all tests.
# Remove to enable selective use of this fixture
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom integrations in all tests."""
    return


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="skip_connect")
def skip_connect_fixture():
    """Skip calls to get data from API."""
    with patch(
        "pymodbus.client.AsyncModbusTcpClient.read_input_registers",
        return_value={},
    ):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="bypass_get_data")
def bypass_get_data_fixture():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.stiebel_eltron_isg.coordinator.StiebelEltronModbusDataCoordinator._async_update_data",
        return_value={},
    ):
        yield


def read_input_register(
    address: int, register, start, count
) -> ReadInputRegistersResponse:
    """Read a slice from the input register."""
    return ReadInputRegistersResponse(
        address=address, count=count, registers=register[start : start + count]
    )


async def read_input_registers_wpm(
    address: int, *, count: int = 1, slave: int = 0, no_response_expected: bool = False
):
    """Simulate reads on the input registers on wpm models."""
    system_info = [2, 390]
    if address >= 5000:
        return read_input_register(address, system_info, address - 5000, count)
    return ReadInputRegistersResponse(
        address=address, count=count, registers=list(range(count))
    )


async def read_input_registers_lwz(
    address: int, *, count: int = 1, slave: int = 0, no_response_expected: bool = False
):
    """Simulate reads on the input registers on lwz models ."""
    system_info = [2, 103]
    if address >= 5000:
        return read_input_register(address, system_info, address - 5000, count)
    return ReadInputRegistersResponse(
        address=address, count=count, registers=list(range(count))
    )


async def read_holding_registers(
    address: int, *, count: int = 1, slave: int = 0, no_response_expected: bool = False
):
    """Simulate reads on the holding registers on lwz models ."""
    return ReadHoldingRegistersResponse(
        address=address, count=count, registers=list(range(count))
    )


# This fixture, when used, will result in calls to read_input_registers to return mock data. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="mock_modbus_wpm")
def modbus_wpm_fixture():
    """Skip calls to get data from API."""
    with (
        patch(
            "pymodbus.client.AsyncModbusTcpClient.read_input_registers",
            side_effect=read_input_registers_wpm,
        ),
        patch(
            "pymodbus.client.AsyncModbusTcpClient.read_holding_registers",
            side_effect=read_holding_registers,
        ),
        patch("pymodbus.client.AsyncModbusTcpClient.connect"),
    ):
        yield


# This fixture, when used, will result in calls to read_holding_registers to return mock data. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="mock_modbus_lwz")
def modbus_lwz_fixture():
    """Skip calls to get data from API."""
    with (
        patch(
            "pymodbus.client.AsyncModbusTcpClient.read_input_registers",
            side_effect=read_input_registers_lwz,
        ),
        patch(
            "pymodbus.client.AsyncModbusTcpClient.read_holding_registers",
            side_effect=read_holding_registers,
        ),
        patch("pymodbus.client.AsyncModbusTcpClient.connect"),
    ):
        yield


# In this fixture, we are forcing calls to async_get_data to raise an Exception. This is useful
# for exception handling.
@pytest.fixture(name="error_on_get_data")
def error_get_data_fixture():
    """Simulate error when retrieving data from API."""
    with patch(
        "custom_components.stiebel_eltron_isg.wpm_coordinator.StiebelEltronModbusWPMDataCoordinator._async_update_data",
        side_effect=Exception,
    ):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="get_model_wpm")
def get_model_wpm_fixture():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.stiebel_eltron_isg.get_controller_model",
        return_value=ControllerModel.WPM_3i,
    ):
        yield


# This fixture, when used, will result in calls to async_get_data to return None. To have the call
# return a value, we would add the `return_value=<VALUE_TO_RETURN>` parameter to the patch call.
@pytest.fixture(name="get_model_lwz")
def get_model_lwz_fixture():
    """Skip calls to get data from API."""
    with patch(
        "custom_components.stiebel_eltron_isg.get_controller_model",
        return_value=ControllerModel.LWZ,
    ):
        yield
