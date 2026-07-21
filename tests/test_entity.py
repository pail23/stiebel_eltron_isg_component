"""Tests for the shared entity base class."""

from custom_components.stiebel_eltron_isg.entity import StiebelEltronISGEntity


class _StubCoordinator:
    def __init__(self, last_update_success: bool, has_value: bool) -> None:
        self.last_update_success = last_update_success
        self._has_value = has_value

    def has_value(self, register) -> bool:
        return self._has_value


def _make_entity(last_update_success: bool, has_value: bool) -> StiebelEltronISGEntity:
    entity = StiebelEltronISGEntity.__new__(StiebelEltronISGEntity)
    entity.coordinator = _StubCoordinator(last_update_success, has_value)
    entity.modbus_register = lambda api: None
    return entity


def test_available_when_update_succeeded_and_value_present() -> None:
    """An entity is available when the last update succeeded and it has a value."""
    assert _make_entity(last_update_success=True, has_value=True).available is True


def test_unavailable_when_last_update_failed() -> None:
    """A failed update must mark the entity unavailable, not show a stale value."""
    assert _make_entity(last_update_success=False, has_value=True).available is False


def test_unavailable_when_value_missing() -> None:
    """A missing register value keeps the entity unavailable."""
    assert _make_entity(last_update_success=True, has_value=False).available is False
