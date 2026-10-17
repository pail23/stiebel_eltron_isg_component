"""A real coordinator over a fake API for entity tests about writes.

The coordinator decides what an entity shows and whether a write would change
anything, so its real write and poll bookkeeping runs here. Only the Home
Assistant plumbing that needs ``hass`` is replaced.
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import CoordinatorEntity, UpdateFailed
from modbus_connection import ModbusError

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronDataCoordinator,
)


class FakeComponent:
    """A component whose fields are plain attributes and whose writes are kept.

    Like the library, a write does not change the field: the device answers
    with the next poll, which these tests emulate by assigning the attribute.
    """

    def __init__(self, name: str, writes: list[tuple], **fields: Any) -> None:
        """Keep the component name and record writes to the shared list."""
        self._name = name
        self._writes = writes
        for field, value in fields.items():
            setattr(self, field, value)

    async def write(self, field: str, value: Any) -> None:
        """Record the write instead of sending it to a device."""
        self._writes.append((self._name, field, value))


class FakeApi:
    """A fake API with named fake components and a mockable poll."""

    def __init__(self, writes: list[tuple], **components: dict[str, Any]) -> None:
        """Create one FakeComponent per keyword argument."""
        self.async_update = AsyncMock()
        for name, fields in components.items():
            setattr(self, name, FakeComponent(name, writes, **fields))


def make_coordinator(api: Any) -> StiebelEltronDataCoordinator:
    """Build the real coordinator without Home Assistant.

    ``writes`` receives every write of the fake API's components in order.
    """
    coordinator = StiebelEltronDataCoordinator.__new__(StiebelEltronDataCoordinator)
    coordinator._api = api
    coordinator._refresh_generation = 0
    coordinator._last_successful_refresh_generation = 0
    coordinator._pending_writes = {}
    coordinator._write_lock = asyncio.Lock()
    coordinator._listeners = {}
    coordinator.last_update_success = True
    return coordinator


def attach(
    coordinator: StiebelEltronDataCoordinator, entity: CoordinatorEntity
) -> None:
    """Register the entity like async_added_to_hass would, without hass."""
    entity.coordinator = coordinator
    entity.published_states = 0

    def _publish() -> None:
        entity.published_states += 1

    entity.async_write_ha_state = _publish
    coordinator._listeners[id(entity)] = (entity._handle_coordinator_update, None)


async def poll(
    coordinator: StiebelEltronDataCoordinator,
    *,
    success: bool = True,
    during: Callable[[], Awaitable[None]] | None = None,
) -> None:
    """Run one coordinator poll the way the update loop would.

    ``during`` runs while the poll is in flight, which is how a write that
    races a poll is emulated.
    """
    api = coordinator._api
    if during is not None:
        api.async_update.side_effect = during
    elif success:
        api.async_update.side_effect = None
    else:
        api.async_update.side_effect = ModbusError("offline")
    try:
        await coordinator._async_update_data()
    except UpdateFailed:
        coordinator.last_update_success = False
    else:
        coordinator.last_update_success = True
    coordinator.async_update_listeners()
