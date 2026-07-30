"""StiebelEltronISGEntity class."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.core import callback
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AnyStiebelEltronDataCoordinator, StiebelEltronConfigEntry

# At runtime this must remain ``object``: concrete entities place the mixin
# before StiebelEltronISGEntity so ``super()`` reaches CoordinatorEntity.
if TYPE_CHECKING:
    _OptimisticValueMixinBase = CoordinatorEntity[AnyStiebelEltronDataCoordinator]
else:
    _OptimisticValueMixinBase = object


def build_unique_id(entry: StiebelEltronConfigEntry, key: str) -> str:
    """Return the unique id of an entity of this config entry."""
    return f"{entry.entry_id}_{key}"


@dataclass(frozen=True, kw_only=True)
class StiebelEltronEntityDescription(EntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: Any


class OptimisticValueMixin(_OptimisticValueMixinBase):
    """Report a written value right away, until the device reports its own.

    A write travels ISG to CAN to heat pump and needs a moment to be reflected
    in the registers, so an immediate read back would still return the old
    value. The written value is therefore assumed until the coordinator has
    polled again, at which point the device's own value takes over. If the
    controller clamps or rounds the value, that correction appears with that
    poll.

    The mixin must precede ``CoordinatorEntity`` in the entity's MRO. It keeps
    the assumption until a successful poll that started after the write, so a
    poll already in flight cannot restore a value it read before the write.
    """

    _optimistic_value: float | int | None = None
    _optimistic_after_generation: int | None = None

    def _set_optimistic_value(self, value: float | int) -> None:
        """Assume ``value`` until the device has been polled after the write."""
        self._optimistic_value = value
        self._optimistic_after_generation = self.coordinator.refresh_generation
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Hand the value back to the device once it has been polled."""
        if (
            self._optimistic_after_generation is not None
            and self.coordinator.last_update_success
            and self.coordinator.last_successful_refresh_generation
            > self._optimistic_after_generation
        ):
            self._optimistic_value = None
            self._optimistic_after_generation = None
        super()._handle_coordinator_update()


class StiebelEltronISGEntity(CoordinatorEntity[AnyStiebelEltronDataCoordinator]):
    """stiebel_eltron_isg entity base class."""

    _attr_has_entity_name = True
    modbus_register: Callable[[Any], float | int | None]

    def __init__(
        self,
        coordinator: AnyStiebelEltronDataCoordinator,
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
