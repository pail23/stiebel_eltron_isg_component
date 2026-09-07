"""Tests for the integration's asynchronous dependency boundary."""

from collections.abc import Callable
from inspect import iscoroutinefunction
from pathlib import Path
from typing import Any

from modbus_connection.model import Component
from pystiebeleltron import get_controller_model
from pystiebeleltron.lwz import LwzStiebelEltronAPI
from pystiebeleltron.wpm import WpmStiebelEltronAPI
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI
import pytest

ROOT = Path(__file__).parent.parent
INTEGRATION_DIR = ROOT / "custom_components" / "stiebel_eltron_isg"

# Connection ownership belongs to Home Assistant's shared Modbus integration.
# tests/test_init.py covers sharing, temporary consumers, reconnect and unload.
# These are the library I/O operations called directly by this integration.
ASYNC_DEPENDENCY_OPERATIONS = (
    pytest.param(get_controller_model, id="get_controller_model"),
    pytest.param(
        WpmStiebelEltronAPI.async_update,
        id="WpmStiebelEltronAPI.async_update",
    ),
    pytest.param(
        Wpm3iStiebelEltronAPI.async_update,
        id="Wpm3iStiebelEltronAPI.async_update",
    ),
    pytest.param(
        LwzStiebelEltronAPI.async_update,
        id="LwzStiebelEltronAPI.async_update",
    ),
    pytest.param(Component.write, id="Component.write"),
)


@pytest.mark.parametrize("operation", ASYNC_DEPENDENCY_OPERATIONS)
def test_dependency_io_entry_point_is_async(
    operation: Callable[..., Any],
) -> None:
    """Keep every dependency I/O entry point natively asynchronous."""
    assert iscoroutinefunction(operation)


def test_integration_does_not_wrap_dependency_io_in_executor() -> None:
    """Reject HA executor wrappers without claiming all sync calls are harmless."""
    occurrences = [
        f"{path.relative_to(ROOT)}:{line_number}"
        for path in sorted(INTEGRATION_DIR.rglob("*.py"))
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(),
            start=1,
        )
        if "async_add_executor_job" in line
    ]

    assert not occurrences, "Found Home Assistant executor wrappers at " + ", ".join(
        occurrences
    )
