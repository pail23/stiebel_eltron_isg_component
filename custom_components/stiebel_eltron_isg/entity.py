"""StiebelEltronISGEntity class."""

from collections.abc import Callable, Sequence
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import StiebelEltronConfigEntry, StiebelEltronDataCoordinator


def build_unique_id(entry: StiebelEltronConfigEntry, key: str) -> str:
    """Return the unique id of an entity of this config entry."""
    return f"{entry.entry_id}_{key}"


# Reads one value from the model-specific API client. The client type is
# erased to Any at this boundary, see StiebelEltronDataCoordinator.get_value.
type ValueAccessor = Callable[[Any], float | int | None]


class StiebelEltronISGEntity(CoordinatorEntity[StiebelEltronDataCoordinator]):
    """stiebel_eltron_isg entity base class."""

    _attr_has_entity_name = True
    modbus_register: ValueAccessor

    def __init__(
        self,
        coordinator: StiebelEltronDataCoordinator,
        config_entry: StiebelEltronConfigEntry,
    ):
        """Initialize the entity base class."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_device_info = coordinator.device_info

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the entity.

        Derived from the config entry, never from a display name: a name is
        allowed to change, and when it did in 2026.7 it orphaned every entity.
        """
        return build_unique_id(self.config_entry, self.entity_description.key)

    @property
    def available(self) -> bool:
        """Return True if entity is available.

        An entity is only available when the most recent coordinator update
        succeeded; otherwise a lost connection would keep reporting the last
        cached register value as if it were current.
        """
        return self.coordinator.last_update_success and self.coordinator.has_value(
            self.modbus_register
        )


@callback
def async_add_when_served[D: EntityDescription](
    entry: StiebelEltronConfigEntry,
    component: str,
    descriptions: Sequence[D],
    create_entity: Callable[[D], Entity],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add entities of an optional library component once the unit serves it.

    The first refresh may not answer an optional block yet, for example while the
    controller is still starting, and the block can return valid values on a
    later poll. Deciding once during setup would then leave the entities out
    until the entry is reloaded, so the decision is repeated after every update
    until the entities were added. Nothing is listened for when the installed
    library does not have the component, because that cannot change.

    ``descriptions`` must carry a ``modbus_register`` accessor.
    """
    coordinator = entry.runtime_data
    if not coordinator.offers_component(component):
        return

    registers = [description.modbus_register for description in descriptions]  # type: ignore[attr-defined]
    remove_listener: Callable[[], None] | None = None

    @callback
    def _stop() -> None:
        nonlocal remove_listener
        if remove_listener is not None:
            remove_listener()
            remove_listener = None

    @callback
    def _add_if_served() -> None:
        if not coordinator.serves_component(component, registers):
            return
        _stop()
        async_add_entities([create_entity(description) for description in descriptions])

    if coordinator.serves_component(component, registers):
        async_add_entities([create_entity(description) for description in descriptions])
        return

    remove_listener = coordinator.async_add_listener(_add_if_served)
    entry.async_on_unload(_stop)
